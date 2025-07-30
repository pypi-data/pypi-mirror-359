//! Optimized flat index with SIMD support and advanced algorithms

use core::{Vector, DistanceMetric};
use super::{AnnIndex, IndexConfig, IndexStats, SortAlgorithm, SnapshotIndex, IndexWithSnapshot};
use std::collections::{HashMap, BinaryHeap};
use std::cmp::Reverse;
use rayon::prelude::*;
use ordered_float::OrderedFloat;

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// High-performance flat index with SIMD optimizations
pub struct OptimizedFlatIndex {
    config: IndexConfig,
    vectors: Vec<Vector>,
    ids: Vec<usize>,
    id_to_idx: HashMap<usize, usize>,
    // Memory pool for efficient batch operations
    distance_buffer: Vec<f32>,
    temp_results: Vec<(usize, f32)>,
}

impl OptimizedFlatIndex {
    /// Batch distance calculation with SIMD
    #[cfg(target_arch = "x86_64")]
    fn batch_distances_simd(&self, query: &Vector, batch_size: usize) -> Vec<f32> {
        let mut distances = vec![0.0f32; self.vectors.len()];
        
        if is_x86_feature_detected!("avx2") {
            unsafe { self.batch_distances_avx2(query, &mut distances, batch_size) };
        } else if is_x86_feature_detected!("sse") {
            unsafe { self.batch_distances_sse(query, &mut distances, batch_size) };
        } else {
            self.batch_distances_fallback(query, &mut distances);
        }
        
        distances
    }

    #[cfg(not(target_arch = "x86_64"))]
    fn batch_distances_simd(&self, query: &Vector, _batch_size: usize) -> Vec<f32> {
        let mut distances = vec![0.0f32; self.vectors.len()];
        self.batch_distances_fallback(query, &mut distances);
        distances
    }

    fn batch_distances_fallback(&self, query: &Vector, distances: &mut [f32]) {
        for (i, vector) in self.vectors.iter().enumerate() {
            distances[i] = self.config.distance_metric.distance(query, vector);
        }
    }

    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "avx2")]
    unsafe fn batch_distances_avx2(&self, query: &Vector, distances: &mut [f32], _batch_size: usize) {
        let query_data = query.as_slice();
        let dim = query.dim();
        
        for (i, vector) in self.vectors.iter().enumerate() {
            let vector_data = vector.as_slice();
            
            match self.config.distance_metric {
                DistanceMetric::Euclidean => {
                    distances[i] = self.euclidean_distance_avx2(query_data, vector_data, dim);
                }
                _ => {
                    distances[i] = self.config.distance_metric.distance(query, vector);
                }
            }
        }
    }

    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "sse")]
    unsafe fn batch_distances_sse(&self, query: &Vector, distances: &mut [f32], _batch_size: usize) {
        let query_data = query.as_slice();
        let dim = query.dim();
        
        for (i, vector) in self.vectors.iter().enumerate() {
            let vector_data = vector.as_slice();
            
            match self.config.distance_metric {
                DistanceMetric::Euclidean => {
                    distances[i] = self.euclidean_distance_sse(query_data, vector_data, dim);
                }
                _ => {
                    distances[i] = self.config.distance_metric.distance(query, vector);
                }
            }
        }
    }

    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "avx2")]
    unsafe fn euclidean_distance_avx2(&self, a: &[f32], b: &[f32], dim: usize) -> f32 {
        let chunks = dim / 8;
        let remainder = dim % 8;
        let mut sum_vec = _mm256_setzero_ps();
        
        for i in 0..chunks {
            let offset = i * 8;
            let a_vec = _mm256_loadu_ps(a.as_ptr().add(offset));
            let b_vec = _mm256_loadu_ps(b.as_ptr().add(offset));
            let diff_vec = _mm256_sub_ps(a_vec, b_vec);
            let sq_vec = _mm256_mul_ps(diff_vec, diff_vec);
            sum_vec = _mm256_add_ps(sum_vec, sq_vec);
        }

        // Horizontal sum
        let sum_high = _mm256_extractf128_ps(sum_vec, 1);
        let sum_low = _mm256_castps256_ps128(sum_vec);
        let sum_sse = _mm_add_ps(sum_high, sum_low);
        let sum_64 = _mm_add_ps(sum_sse, _mm_movehl_ps(sum_sse, sum_sse));
        let sum_32 = _mm_add_ss(sum_64, _mm_shuffle_ps(sum_64, sum_64, 0x55));
        let mut result = _mm_cvtss_f32(sum_32);

        // Handle remainder
        for i in (chunks * 8)..dim {
            let diff = a[i] - b[i];
            result += diff * diff;
        }

        result.sqrt()
    }

    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "sse")]
    unsafe fn euclidean_distance_sse(&self, a: &[f32], b: &[f32], dim: usize) -> f32 {
        let chunks = dim / 4;
        let remainder = dim % 4;
        let mut sum_vec = _mm_setzero_ps();
        
        for i in 0..chunks {
            let offset = i * 4;
            let a_vec = _mm_loadu_ps(a.as_ptr().add(offset));
            let b_vec = _mm_loadu_ps(b.as_ptr().add(offset));
            let diff_vec = _mm_sub_ps(a_vec, b_vec);
            let sq_vec = _mm_mul_ps(diff_vec, diff_vec);
            sum_vec = _mm_add_ps(sum_vec, sq_vec);
        }

        // Horizontal sum
        let sum_64 = _mm_add_ps(sum_vec, _mm_movehl_ps(sum_vec, sum_vec));
        let sum_32 = _mm_add_ss(sum_64, _mm_shuffle_ps(sum_64, sum_64, 0x55));
        let mut result = _mm_cvtss_f32(sum_32);

        // Handle remainder
        for i in (chunks * 4)..dim {
            let diff = a[i] - b[i];
            result += diff * diff;
        }

        result.sqrt()
    }

    /// Optimized partial sort for top-k selection
    fn partial_sort_top_k(&self, distances: &mut [(usize, f32)], k: usize) {
        if distances.len() <= k {
            distances.sort_unstable_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
            return;
        }

        // Use pdqselect for optimal performance
        let (_, _, greater) = distances.select_nth_unstable_by(k, |a, b| a.1.partial_cmp(&b.1).unwrap());
        greater.sort_unstable_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
    }

    /// Parallel batch processing for large datasets
    fn parallel_search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        const PARALLEL_THRESHOLD: usize = 10000;
        
        if self.vectors.len() < PARALLEL_THRESHOLD {
            return self.sequential_search(query, k);
        }

        // Use rayon for parallel processing
        let chunk_size = (self.vectors.len() / rayon::current_num_threads()).max(1000);
        
        let results: Vec<Vec<(usize, f32)>> = self.vectors
            .par_chunks(chunk_size)
            .enumerate()
            .map(|(chunk_idx, chunk)| {
                let mut chunk_results = Vec::with_capacity(chunk.len());
                let offset = chunk_idx * chunk_size;
                
                for (local_idx, vector) in chunk.iter().enumerate() {
                    let global_idx = offset + local_idx;
                    let distance = self.config.distance_metric.distance(query, vector);
                    chunk_results.push((self.ids[global_idx], distance));
                }
                
                // Sort chunk locally
                chunk_results.sort_unstable_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
                chunk_results.truncate(k);
                chunk_results
            })
            .collect();

        // Merge sorted chunks
        self.merge_sorted_results(results, k)
    }

    fn sequential_search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        let batch_size = self.config.flat_config.as_ref()
            .map(|c| c.batch_size)
            .unwrap_or(1000);

        // Use SIMD batch processing
        let distances = self.batch_distances_simd(query, batch_size);
        
        let mut results: Vec<(usize, f32)> = self.ids.iter()
            .zip(distances.iter())
            .map(|(&id, &dist)| (id, dist))
            .collect();

        // Use optimized sorting based on configuration
        match self.config.flat_config.as_ref().map(|c| &c.sort_algorithm) {
            Some(SortAlgorithm::PartialSort) => self.partial_sort_top_k(&mut results, k),
            Some(SortAlgorithm::Stable) => results.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap()),
            _ => results.sort_unstable_by(|a, b| a.1.partial_cmp(&b.1).unwrap()),
        }

        results.truncate(k);
        results
    }

    fn merge_sorted_results(&self, results: Vec<Vec<(usize, f32)>>, k: usize) -> Vec<(usize, f32)> {
        use std::collections::BinaryHeap;
        use std::cmp::Reverse;

        let mut heap = BinaryHeap::new();
        let mut iterators: Vec<_> = results.into_iter()
            .map(|v| v.into_iter())
            .collect();

        // Initialize heap with first element from each iterator
        for (i, iter) in iterators.iter_mut().enumerate() {
            if let Some(item) = iter.next() {
                heap.push(Reverse((OrderedFloat(item.1), item.0, i)));
            }
        }

        let mut final_results = Vec::with_capacity(k);
        
        while final_results.len() < k && !heap.is_empty() {
            if let Some(Reverse((dist, id, iter_idx))) = heap.pop() {
                final_results.push((id, dist.into_inner()));
                
                // Add next element from the same iterator
                if let Some(next_item) = iterators[iter_idx].next() {
                    heap.push(Reverse((OrderedFloat(next_item.1), next_item.0, iter_idx)));
                }
            }
        }

        final_results
    }
}

impl AnnIndex for OptimizedFlatIndex {
    fn with_config(config: IndexConfig) -> Self {
        let initial_capacity = config.flat_config.as_ref()
            .map(|c| c.batch_size)
            .unwrap_or(10000);
            
        Self {
            config,
            vectors: Vec::with_capacity(initial_capacity),
            ids: Vec::with_capacity(initial_capacity),
            id_to_idx: HashMap::with_capacity(initial_capacity),
            distance_buffer: Vec::with_capacity(initial_capacity),
            temp_results: Vec::with_capacity(initial_capacity),
        }
    }

    fn insert(&mut self, id: usize, vector: Vector) {
        if let Some(&existing_idx) = self.id_to_idx.get(&id) {
            // Update existing vector
            self.vectors[existing_idx] = vector;
        } else {
            // Insert new vector
            let idx = self.vectors.len();
            self.vectors.push(vector);
            self.ids.push(id);
            self.id_to_idx.insert(id, idx);
        }
    }

    fn search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        if self.vectors.is_empty() {
            return Vec::new();
        }

        let use_parallel = self.config.flat_config.as_ref()
            .map(|c| self.vectors.len() > c.batch_size * 10)
            .unwrap_or(false);

        if use_parallel {
            self.parallel_search(query, k)
        } else {
            self.sequential_search(query, k)
        }
    }

    fn config(&self) -> &IndexConfig {
        &self.config
    }

    fn stats(&self) -> IndexStats {
        IndexStats {
            vector_count: self.vectors.len(),
            dimension: self.config.dim,
            index_type: "OptimizedFlat".to_string(),
            distance_metric: self.config.distance_metric,
            memory_usage: self.memory_usage(),
            build_time_ms: None,
            last_search_time_ms: None,
            total_searches: 0,
            total_inserts: self.vectors.len() as u64,
            additional_stats: {
                let mut stats = std::collections::HashMap::new();
                stats.insert("simd_support".to_string(), format!("{}", cfg!(target_arch = "x86_64")));
                stats.insert("parallel_threshold".to_string(), format!("{}", 10000));
                stats
            }
        }
    }
    
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
    
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
}

impl OptimizedFlatIndex {
    // Extra methods not part of AnnIndex trait
    pub fn len(&self) -> usize {
        self.vectors.len()
    }

    pub fn clear(&mut self) {
        self.vectors.clear();
        self.ids.clear();
        self.id_to_idx.clear();
        self.distance_buffer.clear();
        self.temp_results.clear();
    }

    pub fn memory_usage(&self) -> usize {
        let vector_size = self.vectors.len() * self.config.dim * std::mem::size_of::<f32>();
        let ids_size = self.ids.len() * std::mem::size_of::<usize>();
        let map_size = self.id_to_idx.len() * (std::mem::size_of::<usize>() * 2);
        let buffer_size = self.distance_buffer.capacity() * std::mem::size_of::<f32>();
        let temp_size = self.temp_results.capacity() * std::mem::size_of::<(usize, f32)>();
        
        vector_size + ids_size + map_size + buffer_size + temp_size
    }
}

/// Serializable representation of the optimized index
#[derive(serde::Serialize, serde::Deserialize)]
struct OptimizedFlatSnapshot {
    config: IndexConfig,
    vectors: Vec<Vector>,
    ids: Vec<usize>,
    id_to_idx: HashMap<usize, usize>,
}

impl SnapshotIndex for OptimizedFlatIndex {
    fn dump(&self) -> Vec<u8> {
        let snapshot = OptimizedFlatSnapshot {
            config: self.config.clone(),
            vectors: self.vectors.clone(),
            ids: self.ids.clone(),
            id_to_idx: self.id_to_idx.clone(),
        };
        
        bincode::serialize(&snapshot).expect("Failed to serialize OptimizedFlatIndex")
    }
    
    fn restore(config: IndexConfig, data: &[u8]) -> Self {
        let snapshot: OptimizedFlatSnapshot = bincode::deserialize(data)
            .expect("Failed to deserialize OptimizedFlatIndex");
        
        let capacity = snapshot.vectors.len().max(1000);
        
        Self {
            config,
            vectors: snapshot.vectors,
            ids: snapshot.ids,
            id_to_idx: snapshot.id_to_idx,
            distance_buffer: Vec::with_capacity(capacity),
            temp_results: Vec::with_capacity(capacity),
        }
    }
}

impl IndexWithSnapshot for OptimizedFlatIndex {}

impl OptimizedFlatIndex {
    // Extra methods not part of AnnIndex trait
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
    
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
}
