//! FAISS-Inspired Ultra Optimized Flat Index
//! Matches FAISS memory layout and performance characteristics

use core::{Vector, DistanceMetric};
use super::{AnnIndex, IndexConfig, IndexStats, BulkAnnIndex, SnapshotIndex, IndexWithSnapshot};
use std::collections::HashMap;
use rayon::prelude::*;
use ordered_float::OrderedFloat;

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// FAISS-style ultra optimized flat index
/// Memory layout: Single contiguous block like FAISS IndexFlatL2
pub struct FaissInspiredFlatIndex {
    /// Core configuration
    config: IndexConfig,
    
    /// FAISS-style contiguous vector storage
    /// Layout: [vec0[0], vec0[1], ..., vec0[d-1], vec1[0], vec1[1], ..., vec1[d-1], ...]
    /// This matches FAISS's exact memory layout for cache efficiency
    vectors: Vec<f32>,
    
    /// ID mapping (minimal overhead)
    ids: Vec<usize>,
    
    /// Vector count and dimension
    count: usize,
    dimension: usize,
    
    /// Pre-allocated search buffers (avoid allocations during search)
    distances_buffer: Vec<f32>,
    indices_buffer: Vec<usize>,
}

impl FaissInspiredFlatIndex {
    /// Create new FAISS-inspired index
    pub fn new(config: IndexConfig) -> Self {
        let dimension = config.dim;
        
        Self {
            config,
            vectors: Vec::new(),
            ids: Vec::new(),
            count: 0,
            dimension,
            distances_buffer: Vec::new(),
            indices_buffer: Vec::new(),
        }
    }
    
    /// FAISS-style single allocation bulk insert
    /// This is the key to FAISS's performance - single memory allocation and copy
    pub fn faiss_bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) -> usize {
        if vectors.is_empty() {
            return 0;
        }
        
        let new_count = vectors.len();
        let total_count = self.count + new_count;
        
        // FAISS approach: Pre-allocate exact memory needed
        let total_elements = total_count * self.dimension;
        
        // Reserve exact capacity (avoid over-allocation)
        if self.vectors.len() < total_elements {
            self.vectors.resize(total_elements, 0.0);
        }
        
        // Reserve ID storage
        if self.ids.len() < total_count {
            self.ids.resize(total_count, 0);
        }
        
        // FAISS-style bulk memory copy - optimized for cache efficiency
        let start_offset = self.count * self.dimension;
        
        // Use SIMD-friendly copying when possible
        if self.dimension % 8 == 0 {
            // Optimized copy for aligned dimensions
            unsafe {
                for (i, vector) in vectors.iter().enumerate() {
                    let dst_offset = start_offset + i * self.dimension;
                    let src_ptr = vector.as_slice().as_ptr();
                    let dst_ptr = self.vectors.as_mut_ptr().add(dst_offset);
                    
                    // Copy in 32-byte (8 float) chunks for better cache utilization
                    for chunk in 0..(self.dimension / 8) {
                        let chunk_offset = chunk * 8;
                        std::ptr::copy_nonoverlapping(
                            src_ptr.add(chunk_offset),
                            dst_ptr.add(chunk_offset),
                            8
                        );
                    }
                }
            }
        } else {
            // Standard copy for non-aligned dimensions
            for (i, vector) in vectors.iter().enumerate() {
                let dst_offset = start_offset + i * self.dimension;
                let vec_slice = vector.as_slice();
                self.vectors[dst_offset..dst_offset + self.dimension]
                    .copy_from_slice(vec_slice);
            }
        }
        
        // Update IDs efficiently
        for (i, &id) in ids.iter().enumerate() {
            self.ids[self.count + i] = id;
        }
        
        self.count = total_count;
        
        // Update search buffers only if they need resizing
        if self.distances_buffer.len() < self.count {
            self.distances_buffer.resize(self.count, 0.0);
            self.indices_buffer.resize(self.count, 0);
        }
        
        new_count
    }
    
    /// FAISS-style optimized search with SIMD and cache optimization
    pub fn faiss_search(&mut self, query: &[f32], k: usize) -> Vec<(usize, f32)> {
        if self.count == 0 || k == 0 {
            return Vec::new();
        }
        
        let k = k.min(self.count);
        
        // Compute all distances using FAISS-style SIMD
        self.compute_distances_faiss_style(query);
        
        // FAISS-style partial sort (faster than full sort)
        self.partial_sort_faiss_style(k);
        
        // Return results
        self.indices_buffer[..k]
            .iter()
            .map(|&idx| (self.ids[idx], self.distances_buffer[idx]))
            .collect()
    }
    
    /// FAISS-inspired SIMD distance computation
    /// Optimized for modern CPUs with aggressive prefetching and vectorization
    fn compute_distances_faiss_style(&mut self, query: &[f32]) {
        #[cfg(target_arch = "x86_64")]
        {
            if is_x86_feature_detected!("avx2") && is_x86_feature_detected!("fma") {
                unsafe { self.compute_distances_avx2_fma(query); }
                return;
            }
        }
        
        // Fallback: Optimized scalar with manual vectorization
        self.compute_distances_optimized_scalar(query);
    }
    
    #[cfg(target_arch = "x86_64")]
    unsafe fn compute_distances_avx2_fma(&mut self, query: &[f32]) {
        let dim = self.dimension;
        let simd_width = 8; // AVX2 processes 8 floats
        let simd_chunks = dim / simd_width;
        let remainder = dim % simd_width;
        
        // Process multiple vectors simultaneously for better cache utilization
        const VECTOR_BATCH_SIZE: usize = 16; // Process 16 vectors at once
        
        for batch_start in (0..self.count).step_by(VECTOR_BATCH_SIZE) {
            let batch_end = (batch_start + VECTOR_BATCH_SIZE).min(self.count);
            
            // Prefetch next batch
            if batch_end < self.count {
                let prefetch_addr = self.vectors.as_ptr().add(batch_end * dim);
                _mm_prefetch(prefetch_addr as *const i8, _MM_HINT_T0);
            }
            
            // Process current batch
            for vec_idx in batch_start..batch_end {
                let vec_start = vec_idx * dim;
                let vec_data = &self.vectors[vec_start..vec_start + dim];
                
                let mut sum_vec = _mm256_setzero_ps();
                
                // Main SIMD loop with FMA
                for chunk_idx in 0..simd_chunks {
                    let offset = chunk_idx * simd_width;
                    
                    let q_vec = _mm256_loadu_ps(query.as_ptr().add(offset));
                    let v_vec = _mm256_loadu_ps(vec_data.as_ptr().add(offset));
                    let diff_vec = _mm256_sub_ps(q_vec, v_vec);
                    
                    // Use FMA for better performance: sum += diff * diff
                    sum_vec = _mm256_fmadd_ps(diff_vec, diff_vec, sum_vec);
                }
                
                // Horizontal sum with optimized reduction
                let sum_high = _mm256_extractf128_ps(sum_vec, 1);
                let sum_low = _mm256_castps256_ps128(sum_vec);
                let sum_combined = _mm_add_ps(sum_high, sum_low);
                let sum_shuf = _mm_movehl_ps(sum_combined, sum_combined);
                let sum_final = _mm_add_ps(sum_combined, sum_shuf);
                let sum_single = _mm_add_ss(sum_final, _mm_shuffle_ps(sum_final, sum_final, 0x55));
                
                let mut distance = _mm_cvtss_f32(sum_single);
                
                // Handle remainder dimensions
                for i in (simd_chunks * simd_width)..dim {
                    let diff = query[i] - vec_data[i];
                    distance += diff * diff;
                }
                
                self.distances_buffer[vec_idx] = distance;
            }
        }
    }
    
    /// Optimized scalar fallback with manual loop unrolling
    fn compute_distances_optimized_scalar(&mut self, query: &[f32]) {
        // Use parallel processing for large datasets
        if self.count > 10000 {
            let dimension = self.dimension;
            let query_vec = query.to_vec(); // Clone query for parallel processing
            
            // Create chunks for parallel processing
            let chunk_size = 1024;
            let mut results: Vec<f32> = vec![0.0; self.count];
            
            results.par_chunks_mut(chunk_size).enumerate().for_each(|(chunk_idx, chunk)| {
                let start_vec = chunk_idx * chunk_size;
                
                for (i, distance) in chunk.iter_mut().enumerate() {
                    let vec_idx = start_vec + i;
                    if vec_idx < self.count {
                        let vec_start = vec_idx * dimension;
                        let vec_end = vec_start + dimension;
                        
                        // Access vector data safely
                        if vec_end <= self.vectors.len() {
                            let vec_data = &self.vectors[vec_start..vec_end];
                            *distance = Self::compute_l2_distance_unrolled_static(&query_vec, vec_data);
                        }
                    }
                }
            });
            
            // Copy results back to distances_buffer
            self.distances_buffer[..self.count].copy_from_slice(&results[..self.count]);
        } else {
            // Sequential for small datasets
            for vec_idx in 0..self.count {
                self.distances_buffer[vec_idx] = self.compute_l2_distance_unrolled(query, vec_idx);
            }
        }
    }
    
    /// Unrolled L2 distance computation
    #[inline(always)]
    fn compute_l2_distance_unrolled(&self, query: &[f32], vec_idx: usize) -> f32 {
        let vec_start = vec_idx * self.dimension;
        let vec_data = &self.vectors[vec_start..vec_start + self.dimension];
        
        let mut sum = 0.0f32;
        let chunks = self.dimension / 4;
        let remainder = self.dimension % 4;
        
        // Unrolled loop for better performance
        for i in 0..chunks {
            let base = i * 4;
            let d0 = query[base] - vec_data[base];
            let d1 = query[base + 1] - vec_data[base + 1];
            let d2 = query[base + 2] - vec_data[base + 2];
            let d3 = query[base + 3] - vec_data[base + 3];
            sum += d0*d0 + d1*d1 + d2*d2 + d3*d3;
        }
        
        // Handle remainder
        let base = chunks * 4;
        for i in 0..remainder {
            let diff = query[base + i] - vec_data[base + i];
            sum += diff * diff;
        }
        
        sum // Return squared distance for speed (avoid sqrt during sorting)
    }
    
    /// Static version of unrolled L2 distance computation for parallel processing
    #[inline(always)]
    fn compute_l2_distance_unrolled_static(query: &[f32], vec_data: &[f32]) -> f32 {
        let mut sum = 0.0f32;
        let dimension = query.len();
        let chunks = dimension / 4;
        let remainder = dimension % 4;
        
        // Unrolled loop for better performance
        for i in 0..chunks {
            let base = i * 4;
            let d0 = query[base] - vec_data[base];
            let d1 = query[base + 1] - vec_data[base + 1];
            let d2 = query[base + 2] - vec_data[base + 2];
            let d3 = query[base + 3] - vec_data[base + 3];
            sum += d0*d0 + d1*d1 + d2*d2 + d3*d3;
        }
        
        // Handle remainder
        let base = chunks * 4;
        for i in 0..remainder {
            let diff = query[base + i] - vec_data[base + i];
            sum += diff * diff;
        }
        
        sum // Return squared distance for speed (avoid sqrt during sorting)
    }
    
    /// FAISS-style partial sort using nth_element equivalent
    fn partial_sort_faiss_style(&mut self, k: usize) {
        // Initialize indices
        for i in 0..self.count {
            self.indices_buffer[i] = i;
        }
        
        // Use partial sort which is O(n + k log k) instead of O(n log n)
        // This is what FAISS does internally
        let (_, _, right) = self.indices_buffer[..self.count]
            .select_nth_unstable_by(k, |&a, &b| {
                self.distances_buffer[a].partial_cmp(&self.distances_buffer[b])
                    .unwrap_or(std::cmp::Ordering::Equal)
            });
        
        // Sort only the k smallest elements
        right.sort_unstable_by(|&a, &b| {
            self.distances_buffer[a].partial_cmp(&self.distances_buffer[b])
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        
        // Convert squared distances to actual distances only for results
        for i in 0..k {
            let idx = self.indices_buffer[i];
            self.distances_buffer[idx] = self.distances_buffer[idx].sqrt();
        }
    }
}

/// Implement required traits
impl AnnIndex for FaissInspiredFlatIndex {
    fn with_config(config: IndexConfig) -> Self {
        Self::new(config)
    }
    
    fn insert(&mut self, id: usize, vector: Vector) {
        // For single insertion, use bulk insert with single vector
        self.faiss_bulk_insert(&[id], &[vector]);
    }
    
    fn search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        if self.count == 0 || k == 0 {
            return Vec::new();
        }
        
        let k = k.min(self.count);
        let query_slice = query.as_slice();
        
        // Allocate temporary buffers for this search
        let mut distances_buffer = vec![0.0f32; self.count];
        let mut indices_buffer: Vec<usize> = (0..self.count).collect();
        
        // Compute distances directly without mutation
        self.compute_distances_const(query_slice, &mut distances_buffer);
        
        // Partial sort for top-k
        let (_, _, right) = indices_buffer[..self.count]
            .select_nth_unstable_by(k, |&a, &b| {
                distances_buffer[a].partial_cmp(&distances_buffer[b])
                    .unwrap_or(std::cmp::Ordering::Equal)
            });
        
        // Sort only the k smallest elements
        right.sort_unstable_by(|&a, &b| {
            distances_buffer[a].partial_cmp(&distances_buffer[b])
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        
        // Convert squared distances to actual distances and return results
        indices_buffer[..k]
            .iter()
            .map(|&idx| (self.ids[idx], distances_buffer[idx].sqrt()))
            .collect()
    }
    
    fn config(&self) -> &IndexConfig {
        &self.config
    }
    
    fn stats(&self) -> IndexStats {
        IndexStats {
            vector_count: self.count,
            dimension: self.dimension,
            index_type: "FaissInspiredFlat".to_string(),
            distance_metric: self.config.distance_metric.clone(),
            memory_usage: self.vectors.len() * 4 + self.ids.len() * 8,
            build_time_ms: None,
            last_search_time_ms: None,
            total_searches: 0,
            total_inserts: self.count as u64,
            additional_stats: std::collections::HashMap::new(),
        }
    }
    
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
    
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
}

impl BulkAnnIndex for FaissInspiredFlatIndex {
    fn bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) {
        self.faiss_bulk_insert(ids, vectors);
    }
    
    fn reserve(&mut self, capacity: usize) {
        if capacity > self.count {
            let new_capacity = capacity.max(self.count * 2);
            self.vectors.reserve(new_capacity * self.dimension - self.vectors.len());
            self.ids.reserve(new_capacity - self.ids.len());
            
            if self.distances_buffer.len() < new_capacity {
                self.distances_buffer.resize(new_capacity, 0.0);
                self.indices_buffer.resize(new_capacity, 0);
            }
        }
    }
}

impl SnapshotIndex for FaissInspiredFlatIndex {
    fn dump(&self) -> Vec<u8> {
        // For now, return empty snapshot (TODO: implement proper serialization)
        Vec::new()
    }
    
    fn restore(config: IndexConfig, _data: &[u8]) -> Self {
        // For now, just create a new index (TODO: implement proper deserialization)
        Self::new(config)
    }
}

impl IndexWithSnapshot for FaissInspiredFlatIndex {}

impl FaissInspiredFlatIndex {
    /// Const version of distance computation for non-mutable search
    fn compute_distances_const(&self, query: &[f32], distances_buffer: &mut [f32]) {
        #[cfg(target_arch = "x86_64")]
        {
            if is_x86_feature_detected!("avx2") && is_x86_feature_detected!("fma") {
                unsafe { self.compute_distances_avx2_fma_const(query, distances_buffer); }
                return;
            }
        }
        
        // Fallback: Sequential computation without mutation
        for vec_idx in 0..self.count {
            distances_buffer[vec_idx] = self.compute_l2_distance_unrolled(query, vec_idx);
        }
    }
    
    #[cfg(target_arch = "x86_64")]
    unsafe fn compute_distances_avx2_fma_const(&self, query: &[f32], distances_buffer: &mut [f32]) {
        let dim = self.dimension;
        let simd_width = 8;
        let simd_chunks = dim / simd_width;
        let remainder = dim % simd_width;
        
        for vec_idx in 0..self.count {
            let vec_start = vec_idx * dim;
            let vec_data = &self.vectors[vec_start..vec_start + dim];
            
            let mut sum_vec = _mm256_setzero_ps();
            
            // Main SIMD loop with FMA
            for chunk_idx in 0..simd_chunks {
                let offset = chunk_idx * simd_width;
                
                let q_vec = _mm256_loadu_ps(query.as_ptr().add(offset));
                let v_vec = _mm256_loadu_ps(vec_data.as_ptr().add(offset));
                let diff_vec = _mm256_sub_ps(q_vec, v_vec);
                
                sum_vec = _mm256_fmadd_ps(diff_vec, diff_vec, sum_vec);
            }
            
            // Horizontal sum
            let sum_high = _mm256_extractf128_ps(sum_vec, 1);
            let sum_low = _mm256_castps256_ps128(sum_vec);
            let sum_combined = _mm_add_ps(sum_high, sum_low);
            let sum_shuf = _mm_movehl_ps(sum_combined, sum_combined);
            let sum_final = _mm_add_ps(sum_combined, sum_shuf);
            let sum_single = _mm_add_ss(sum_final, _mm_shuffle_ps(sum_final, sum_final, 0x55));
            
            let mut distance = _mm_cvtss_f32(sum_single);
            
            // Handle remainder dimensions
            for i in (simd_chunks * simd_width)..dim {
                let diff = query[i] - vec_data[i];
                distance += diff * diff;
            }
            
            distances_buffer[vec_idx] = distance;
        }
    }
}
