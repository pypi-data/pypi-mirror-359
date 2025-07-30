//! Super-optimized flat index with bulk operations and advanced vectorization

use core::{Vector, DistanceMetric};
use super::{AnnIndex, IndexConfig, IndexStats, SnapshotIndex, IndexWithSnapshot, BulkAnnIndex};
use std::collections::HashMap;
use rayon::prelude::*;
use ordered_float::OrderedFloat;

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// Ultra-high-performance flat index optimized for bulk operations and FAISS-like performance
pub struct SuperOptimizedFlatIndex {
    config: IndexConfig,
    // Pre-allocated flat memory layout for maximum cache efficiency
    vectors_data: Vec<f32>,  // All vectors in one contiguous block
    ids: Vec<usize>,
    id_to_idx: HashMap<usize, usize>,
    vector_count: usize,
    dimension: usize,
    capacity: usize,
    
    // Pre-allocated working buffers to avoid allocations during operations
    distance_buffer: Vec<f32>,
    sorted_indices: Vec<usize>,
    temp_buffer: Vec<f32>,
}

impl SuperOptimizedFlatIndex {
    /// Bulk insert multiple vectors at once - FAISS-style
    pub fn bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) {
        if ids.len() != vectors.len() {
            panic!("IDs and vectors length mismatch");
        }
        
        let new_count = vectors.len();
        let required_capacity = self.vector_count + new_count;
        
        // Ensure capacity with minimal reallocations
        if required_capacity > self.capacity {
            let new_capacity = (required_capacity * 2).max(self.capacity * 2);
            self.reserve_capacity(new_capacity);
        }
        
        // Bulk copy all vector data in one operation
        let start_offset = self.vector_count * self.dimension;
        for (i, vector) in vectors.iter().enumerate() {
            let offset = start_offset + i * self.dimension;
            self.vectors_data[offset..offset + self.dimension]
                .copy_from_slice(vector.as_slice());
        }
        
        // Bulk update IDs and index mapping
        for (i, &id) in ids.iter().enumerate() {
            let idx = self.vector_count + i;
            self.ids.push(id);
            self.id_to_idx.insert(id, idx);
        }
        
        self.vector_count += new_count;
    }
    
    /// Reserve capacity for vectors to minimize reallocations
    fn reserve_capacity(&mut self, new_capacity: usize) {
        if new_capacity > self.capacity {
            // Resize vectors_data
            self.vectors_data.resize(new_capacity * self.dimension, 0.0);
            self.ids.reserve(new_capacity - self.capacity);
            self.id_to_idx.reserve(new_capacity - self.capacity);
            
            // Resize working buffers
            self.distance_buffer.resize(new_capacity, 0.0);
            self.sorted_indices.resize(new_capacity, 0);
            
            self.capacity = new_capacity;
        }
    }
    
    /// Get vector data slice for a specific vector index
    fn get_vector_data(&self, idx: usize) -> &[f32] {
        let start = idx * self.dimension;
        &self.vectors_data[start..start + self.dimension]
    }
    
    /// Ultra-fast bulk distance calculation using aggressive SIMD and loop unrolling
    #[cfg(target_arch = "x86_64")]
    fn bulk_distances_avx2(&self, query: &[f32]) -> &[f32] {
        if !is_x86_feature_detected!("avx2") {
            return self.bulk_distances_fallback(query);
        }
        
        unsafe {
            self.bulk_distances_avx2_unsafe(query)
        }
    }
    
    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "avx2")]
    unsafe fn bulk_distances_avx2_unsafe(&self, query: &[f32]) -> &[f32] {
        let dim = self.dimension;
        let dim_chunks = dim / 8;
        let dim_remainder = dim % 8;
        
        // Process vectors in chunks for better cache utilization
        const CHUNK_SIZE: usize = 64; // Process 64 vectors at once
        
        for chunk_start in (0..self.vector_count).step_by(CHUNK_SIZE) {
            let chunk_end = (chunk_start + CHUNK_SIZE).min(self.vector_count);
            
            // Prefetch next chunk
            if chunk_end < self.vector_count {
                let prefetch_offset = chunk_end * dim;
                _mm_prefetch(
                    self.vectors_data.as_ptr().add(prefetch_offset) as *const i8,
                    _MM_HINT_T0
                );
            }
            
            // Process current chunk
            for vector_idx in chunk_start..chunk_end {
                let vector_data = self.get_vector_data(vector_idx);
                let mut sum_vec = _mm256_setzero_ps();
                
                // Vectorized main loop
                for i in 0..dim_chunks {
                    let offset = i * 8;
                    let q_vec = _mm256_loadu_ps(query.as_ptr().add(offset));
                    let v_vec = _mm256_loadu_ps(vector_data.as_ptr().add(offset));
                    let diff_vec = _mm256_sub_ps(q_vec, v_vec);
                    let sq_vec = _mm256_fmadd_ps(diff_vec, diff_vec, sum_vec);
                    sum_vec = sq_vec;
                }
                
                // Horizontal sum using optimized reduction
                let sum_high = _mm256_extractf128_ps(sum_vec, 1);
                let sum_low = _mm256_castps256_ps128(sum_vec);
                let sum_sse = _mm_add_ps(sum_high, sum_low);
                let sum_final = _mm_add_ps(sum_sse, _mm_movehl_ps(sum_sse, sum_sse));
                let sum_scalar = _mm_add_ss(sum_final, _mm_shuffle_ps(sum_final, sum_final, 0x55));
                let mut distance = _mm_cvtss_f32(sum_scalar);
                
                // Handle remainder elements
                for i in (dim_chunks * 8)..dim {
                    let diff = query[i] - vector_data[i];
                    distance += diff * diff;
                }
                
                self.distance_buffer[vector_idx] = distance.sqrt();
            }
        }
        
        &self.distance_buffer[..self.vector_count]
    }
    
    #[cfg(not(target_arch = "x86_64"))]
    fn bulk_distances_avx2(&mut self, query: &[f32]) -> &[f32] {
        self.bulk_distances_fallback(query)
    }
    
    fn bulk_distances_fallback(&mut self, query: &[f32]) -> &[f32] {
        // Parallel fallback using Rayon with aggressive chunking
        const PARALLEL_THRESHOLD: usize = 1000;
        
        if self.vector_count > PARALLEL_THRESHOLD {
            self.distance_buffer[..self.vector_count]
                .par_chunks_mut(256)
                .enumerate()
                .for_each(|(chunk_idx, chunk)| {
                    let start_idx = chunk_idx * 256;
                    for (i, distance) in chunk.iter_mut().enumerate() {
                        let vector_idx = start_idx + i;
                        if vector_idx < self.vector_count {
                            let vector_data = self.get_vector_data(vector_idx);
                            *distance = self.euclidean_distance_optimized(query, vector_data);
                        }
                    }
                });
        } else {
            for i in 0..self.vector_count {
                let vector_data = self.get_vector_data(i);
                self.distance_buffer[i] = self.euclidean_distance_optimized(query, vector_data);
            }
        }
        
        &self.distance_buffer[..self.vector_count]
    }
    
    /// Optimized euclidean distance calculation
    fn euclidean_distance_optimized(&self, a: &[f32], b: &[f32]) -> f32 {
        let mut sum = 0.0f32;
        
        // Loop unrolling for better performance
        let chunks = a.len() / 4;
        let remainder = a.len() % 4;
        
        for i in 0..chunks {
            let base = i * 4;
            let d0 = a[base] - b[base];
            let d1 = a[base + 1] - b[base + 1];
            let d2 = a[base + 2] - b[base + 2];
            let d3 = a[base + 3] - b[base + 3];
            sum += d0 * d0 + d1 * d1 + d2 * d2 + d3 * d3;
        }
        
        // Handle remainder
        for i in (chunks * 4)..(chunks * 4 + remainder) {
            let diff = a[i] - b[i];
            sum += diff * diff;
        }
        
        sum.sqrt()
    }
    
    /// Ultra-fast k-NN search using optimized sorting
    fn fast_knn_search(&mut self, query: &[f32], k: usize) -> Vec<(usize, f32)> {
        if self.vector_count == 0 {
            return Vec::new();
        }
        
        // Compute all distances in bulk
        let distances = self.bulk_distances_avx2(query);
        
        // Use optimized partial sorting for k << n cases
        if k * 10 < self.vector_count {
            self.partial_sort_knn(distances, k)
        } else {
            self.full_sort_knn(distances, k)
        }
    }
    
    /// Optimized partial sort for small k
    fn partial_sort_knn(&self, distances: &[f32], k: usize) -> Vec<(usize, f32)> {
        // Use nth_element-style algorithm for O(n) average case
        for i in 0..self.vector_count {
            self.sorted_indices[i] = i;
        }
        
        // Introspective quickselect with heap for small k
        let mut results = Vec::with_capacity(k);
        let mut heap = std::collections::BinaryHeap::with_capacity(k + 1);
        
        for i in 0..self.vector_count {
            let distance = OrderedFloat(distances[i]);
            let id = self.ids[i];
            
            if heap.len() < k {
                heap.push((distance, id));
            } else if distance < heap.peek().unwrap().0 {
                heap.pop();
                heap.push((distance, id));
            }
        }
        
        // Extract results
        while let Some((dist, id)) = heap.pop() {
            results.push((id, dist.0));
        }
        
        results.reverse();
        results
    }
    
    /// Full sort for larger k
    fn full_sort_knn(&self, distances: &[f32], k: usize) -> Vec<(usize, f32)> {
        let mut indexed_distances: Vec<(usize, f32)> = distances
            .iter()
            .enumerate()
            .map(|(i, &dist)| (self.ids[i], dist))
            .collect();
        
        // Use unstable sort for better performance
        indexed_distances.par_sort_unstable_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        
        indexed_distances.truncate(k);
        indexed_distances
    }
}

impl AnnIndex for SuperOptimizedFlatIndex {
    fn with_config(config: IndexConfig) -> Self {
        let initial_capacity = config.flat_config.as_ref()
            .map(|c| c.batch_size.max(10000))
            .unwrap_or(50000); // Start with larger capacity
            
        let dimension = config.dim;
        
        Self {
            config,
            vectors_data: vec![0.0; initial_capacity * dimension],
            ids: Vec::with_capacity(initial_capacity),
            id_to_idx: HashMap::with_capacity(initial_capacity),
            vector_count: 0,
            dimension,
            capacity: initial_capacity,
            distance_buffer: vec![0.0; initial_capacity],
            sorted_indices: vec![0; initial_capacity],
            temp_buffer: vec![0.0; dimension],
        }
    }

    fn insert(&mut self, id: usize, vector: Vector) {
        // Single insert - less efficient, prefer bulk_insert
        if let Some(&existing_idx) = self.id_to_idx.get(&id) {
            // Update existing vector
            let start = existing_idx * self.dimension;
            self.vectors_data[start..start + self.dimension]
                .copy_from_slice(vector.as_slice());
        } else {
            // Ensure capacity
            if self.vector_count >= self.capacity {
                self.reserve_capacity(self.capacity * 2);
            }
            
            // Insert new vector
            let start = self.vector_count * self.dimension;
            self.vectors_data[start..start + self.dimension]
                .copy_from_slice(vector.as_slice());
            
            self.ids.push(id);
            self.id_to_idx.insert(id, self.vector_count);
            self.vector_count += 1;
        }
    }

    fn search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        if self.vector_count == 0 {
            return Vec::new();
        }

        // Use stack-allocated temporary buffers for search
        let mut distance_buffer = vec![0.0f32; self.vector_count];
        
        // Compute all distances
        self.compute_all_distances(query.as_slice(), &mut distance_buffer);
        
        // Use optimized partial sorting for k << n cases
        if k * 10 < self.vector_count {
            self.partial_sort_knn_static(&distance_buffer, k)
        } else {
            self.full_sort_knn_static(&distance_buffer, k)
        }
    }

    fn config(&self) -> &IndexConfig {
        &self.config
    }

    fn stats(&self) -> IndexStats {
        IndexStats {
            vector_count: self.vector_count,
            dimension: self.dimension,
            index_type: "SuperOptimizedFlat".to_string(),
            distance_metric: self.config.distance_metric,
            memory_usage: self.memory_usage(),
            build_time_ms: None,
            last_search_time_ms: None,
            total_searches: 0,
            total_inserts: self.vector_count as u64,
            additional_stats: {
                let mut stats = std::collections::HashMap::new();
                stats.insert("bulk_insertion".to_string(), "true".to_string());
                stats.insert("simd_support".to_string(), if cfg!(target_arch = "x86_64") { "true" } else { "false" }.to_string());
                stats.insert("memory_layout".to_string(), "flat_contiguous".to_string());
                stats
            },
        }
    }
    
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
    
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
}

impl SuperOptimizedFlatIndex {
    fn memory_usage(&self) -> usize {
        self.vectors_data.len() * std::mem::size_of::<f32>() +
        self.ids.len() * std::mem::size_of::<usize>() +
        self.id_to_idx.len() * (std::mem::size_of::<usize>() * 2) +
        self.distance_buffer.len() * std::mem::size_of::<f32>() +
        self.sorted_indices.len() * std::mem::size_of::<usize>()
    }
}

impl SnapshotIndex for SuperOptimizedFlatIndex {
    fn dump(&self) -> Vec<u8> {
        use serde::{Serialize, Deserialize};
        
        #[derive(Serialize, Deserialize)]
        struct Snapshot {
            config: IndexConfig,
            vectors_data: Vec<f32>,
            ids: Vec<usize>,
            vector_count: usize,
            dimension: usize,
        }
        
        let snapshot = Snapshot {
            config: self.config.clone(),
            vectors_data: self.vectors_data[..self.vector_count * self.dimension].to_vec(),
            ids: self.ids.clone(),
            vector_count: self.vector_count,
            dimension: self.dimension,
        };
        
        bincode::serialize(&snapshot).unwrap_or_default()
    }
    
    fn restore(config: IndexConfig, data: &[u8]) -> Self {
        use serde::{Serialize, Deserialize};
        
        #[derive(Serialize, Deserialize)]
        struct Snapshot {
            config: IndexConfig,
            vectors_data: Vec<f32>,
            ids: Vec<usize>,
            vector_count: usize,
            dimension: usize,
        }
        
        if let Ok(snapshot) = bincode::deserialize::<Snapshot>(data) {
            let capacity = snapshot.vector_count.max(10000);
            let mut vectors_data = vec![0.0; capacity * snapshot.dimension];
            vectors_data[..snapshot.vectors_data.len()].copy_from_slice(&snapshot.vectors_data);
            
            let mut id_to_idx = HashMap::with_capacity(capacity);
            for (idx, &id) in snapshot.ids.iter().enumerate() {
                id_to_idx.insert(id, idx);
            }
            
            Self {
                config: snapshot.config,
                vectors_data,
                ids: snapshot.ids,
                id_to_idx,
                vector_count: snapshot.vector_count,
                dimension: snapshot.dimension,
                capacity,
                distance_buffer: vec![0.0; capacity],
                sorted_indices: vec![0; capacity],
                temp_buffer: vec![0.0; snapshot.dimension],
            }
        } else {
            Self::with_config(config)
        }
    }
}

impl IndexWithSnapshot for SuperOptimizedFlatIndex {}

impl BulkAnnIndex for SuperOptimizedFlatIndex {
    fn bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) {
        SuperOptimizedFlatIndex::bulk_insert(self, ids, vectors);
    }
    
    fn reserve(&mut self, capacity: usize) {
        self.reserve_capacity(capacity);
    }
}

impl SuperOptimizedFlatIndex {
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
    
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
    
    /// Compute distances to all vectors and store in provided buffer
    fn compute_all_distances(&self, query: &[f32], distance_buffer: &mut [f32]) {
        // Use the same SIMD-optimized approach but with provided buffer
        #[cfg(target_arch = "x86_64")]
        {
            self.compute_distances_avx2(query, distance_buffer);
        }
        
        #[cfg(not(target_arch = "x86_64"))]
        {
            self.compute_distances_fallback(query, distance_buffer);
        }
    }
    
    #[cfg(target_arch = "x86_64")]
    fn compute_distances_avx2(&self, query: &[f32], distance_buffer: &mut [f32]) {
        use std::arch::x86_64::*;

        let dim = self.dimension;
        let dim_chunks = dim / 8;
        
        // Process vectors in chunks for better cache utilization
        const CHUNK_SIZE: usize = 64;
        
        for chunk_start in (0..self.vector_count).step_by(CHUNK_SIZE) {
            let chunk_end = (chunk_start + CHUNK_SIZE).min(self.vector_count);
            
            // Process current chunk
            for vector_idx in chunk_start..chunk_end {
                let vector_data = self.get_vector_data(vector_idx);
                let mut sum_vec = unsafe { _mm256_setzero_ps() };
                
                // Vectorized main loop
                for i in 0..dim_chunks {
                    let offset = i * 8;
                    unsafe {
                        let q_vec = _mm256_loadu_ps(query.as_ptr().add(offset));
                        let v_vec = _mm256_loadu_ps(vector_data.as_ptr().add(offset));
                        let diff_vec = _mm256_sub_ps(q_vec, v_vec);
                        let sq_vec = _mm256_fmadd_ps(diff_vec, diff_vec, sum_vec);
                        sum_vec = sq_vec;
                    }
                }
                
                // Horizontal sum using optimized reduction
                unsafe {
                    let sum_high = _mm256_extractf128_ps(sum_vec, 1);
                    let sum_low = _mm256_castps256_ps128(sum_vec);
                    let sum_sse = _mm_add_ps(sum_high, sum_low);
                    let sum_final = _mm_add_ps(sum_sse, _mm_movehl_ps(sum_sse, sum_sse));
                    let sum_scalar = _mm_add_ss(sum_final, _mm_shuffle_ps(sum_final, sum_final, 0x55));
                    let mut distance = _mm_cvtss_f32(sum_scalar);
                    
                    // Handle remainder elements
                    for i in (dim_chunks * 8)..dim {
                        let diff = query[i] - vector_data[i];
                        distance += diff * diff;
                    }
                    
                    distance_buffer[vector_idx] = distance.sqrt();
                }
            }
        }
    }
    
    #[cfg(not(target_arch = "x86_64"))]
    fn compute_distances_fallback(&self, query: &[f32], distance_buffer: &mut [f32]) {
        // Parallel fallback using Rayon with aggressive chunking
        const PARALLEL_THRESHOLD: usize = 1000;
        
        if self.vector_count > PARALLEL_THRESHOLD {
            distance_buffer[..self.vector_count]
                .par_chunks_mut(256)
                .enumerate()
                .for_each(|(chunk_idx, chunk)| {
                    let start_idx = chunk_idx * 256;
                    for (i, distance) in chunk.iter_mut().enumerate() {
                        let vector_idx = start_idx + i;
                        if vector_idx < self.vector_count {
                            let vector_data = self.get_vector_data(vector_idx);
                            *distance = self.euclidean_distance_optimized(query, vector_data);
                        }
                    }
                });
        } else {
            for i in 0..self.vector_count {
                let vector_data = self.get_vector_data(i);
                distance_buffer[i] = self.euclidean_distance_optimized(query, vector_data);
            }
        }
    }
    
    /// Optimized partial sort for small k using static buffers
    fn partial_sort_knn_static(&self, distances: &[f32], k: usize) -> Vec<(usize, f32)> {
        // Use introspective quickselect with heap for small k
        let mut results = Vec::with_capacity(k);
        let mut heap = std::collections::BinaryHeap::with_capacity(k + 1);
        
        for i in 0..self.vector_count {
            let distance = ordered_float::OrderedFloat(distances[i]);
            let id = self.ids[i];
            
            if heap.len() < k {
                heap.push((distance, id));
            } else if distance < heap.peek().unwrap().0 {
                heap.pop();
                heap.push((distance, id));
            }
        }
        
        // Extract results
        while let Some((dist, id)) = heap.pop() {
            results.push((id, dist.0));
        }
        
        results.reverse();
        results
    }
    
    /// Full sort for larger k using static buffers
    fn full_sort_knn_static(&self, distances: &[f32], k: usize) -> Vec<(usize, f32)> {
        let mut indexed_distances: Vec<(usize, f32)> = distances[..self.vector_count]
            .iter()
            .enumerate()
            .map(|(i, &dist)| (self.ids[i], dist))
            .collect();
        
        // Use unstable sort for better performance
        indexed_distances.par_sort_unstable_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        
        indexed_distances.truncate(k);
        indexed_distances
    }
