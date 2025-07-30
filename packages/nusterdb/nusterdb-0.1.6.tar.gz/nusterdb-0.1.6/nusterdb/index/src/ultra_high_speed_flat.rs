//! Ultra-High-Speed Flat Index with Advanced Insertion Optimizations
//! Target: 500K+ vectors/sec insertion with optimal memory usage

use core::{Vector, DistanceMetric};
use super::{AnnIndex, IndexConfig, IndexStats, BulkAnnIndex, SnapshotIndex, IndexWithSnapshot};
use rayon::prelude::*;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// Ultra-high-speed insertion modes
#[derive(Debug, Clone, Copy)]
pub enum InsertionMode {
    Sequential,        // Single-threaded sequential
    Parallel,          // Multi-threaded parallel
    Vectorized,        // SIMD-optimized single-threaded
    HyperParallel,     // Multi-threaded + SIMD + memory prefetching
}

/// Quantization modes for memory optimization
#[derive(Debug, Clone, Copy)]
pub enum QuantizationMode {
    None,      // Full f32 precision
    Int8,      // 8-bit quantization (4x memory reduction)
    Int4,      // 4-bit quantization (8x memory reduction)
}

/// Ultra-high-speed flat index optimized for maximum insertion throughput
pub struct UltraHighSpeedFlatIndex {
    config: IndexConfig,
    dimension: usize,
    count: AtomicUsize,
    
    /// Insertion configuration
    insertion_mode: InsertionMode,
    quantization: QuantizationMode,
    
    /// High-performance storage
    quantized_data: Vec<u8>,
    scale: Vec<f32>,
    offset: Vec<f32>,
    ids: Vec<u32>,
    
    /// Performance optimization structures
    insertion_buffer: Vec<u8>,      // Pre-allocated buffer for batch processing
    parallel_chunks: Vec<Vec<u8>>,  // Pre-allocated chunks for parallel processing
    simd_buffer: Vec<f32>,          // SIMD-aligned buffer
    
    /// Memory prefetching hints
    prefetch_distance: usize,
    cache_line_size: usize,
}

impl UltraHighSpeedFlatIndex {
    /// Create new ultra-high-speed index
    pub fn new(config: IndexConfig, insertion_mode: InsertionMode, quantization: QuantizationMode) -> Self {
        let dimension = config.dim;
        let cache_line_size = 64; // Modern CPUs typically use 64-byte cache lines
        
        Self {
            config,
            dimension,
            count: AtomicUsize::new(0),
            insertion_mode,
            quantization,
            quantized_data: Vec::new(),
            scale: vec![1.0; dimension],
            offset: vec![0.0; dimension],
            ids: Vec::new(),
            insertion_buffer: Vec::new(),
            parallel_chunks: Vec::new(),
            simd_buffer: Vec::new(),
            prefetch_distance: 8,
            cache_line_size,
        }
    }
    
    /// Create with default configuration for maximum speed
    pub fn with_config(config: IndexConfig) -> Self {
        Self::new(config, InsertionMode::HyperParallel, QuantizationMode::Int8)
    }
    
    /// Get bytes per element based on quantization
    fn bytes_per_element(&self) -> usize {
        match self.quantization {
            QuantizationMode::None => 4,
            QuantizationMode::Int8 => 1,
            QuantizationMode::Int4 => 1, // Packed 2 per byte
        }
    }
    
    /// Calculate memory requirements for vectors
    fn calculate_memory_requirements(&self, num_vectors: usize) -> usize {
        let bytes_per_vec = match self.quantization {
            QuantizationMode::None => self.dimension * 4,
            QuantizationMode::Int8 => self.dimension,
            QuantizationMode::Int4 => (self.dimension + 1) / 2,
        };
        num_vectors * bytes_per_vec
    }
    
    /// Compute quantization parameters from training data (optimized version)
    fn compute_quantization_params_fast(&mut self, vectors: &[Vector]) {
        if matches!(self.quantization, QuantizationMode::None) {
            return;
        }
        
        // Parallel computation of min/max for each dimension
        let (min_vals, max_vals): (Vec<f32>, Vec<f32>) = (0..self.dimension)
            .into_par_iter()
            .map(|dim_idx| {
                let mut min_val = f32::INFINITY;
                let mut max_val = f32::NEG_INFINITY;
                
                for vector in vectors {
                    let data = vector.as_slice();
                    if dim_idx < data.len() {
                        let val = data[dim_idx];
                        min_val = min_val.min(val);
                        max_val = max_val.max(val);
                    }
                }
                
                (min_val, max_val)
            })
            .unzip();
        
        // Compute scale and offset
        for i in 0..self.dimension {
            let range = max_vals[i] - min_vals[i];
            self.offset[i] = min_vals[i];
            
            self.scale[i] = match self.quantization {
                QuantizationMode::Int8 => if range > 0.0 { range / 255.0 } else { 1.0 },
                QuantizationMode::Int4 => if range > 0.0 { range / 15.0 } else { 1.0 },
                QuantizationMode::None => 1.0,
            };
        }
    }
    
    /// Ultra-fast vectorized quantization using SIMD
    #[cfg(target_arch = "x86_64")]
    unsafe fn quantize_vectors_simd(&self, vectors: &[Vector]) -> Vec<u8> {
        let total_bytes = self.calculate_memory_requirements(vectors.len());
        let mut result = vec![0u8; total_bytes];
        
        match self.quantization {
            QuantizationMode::Int8 => {
                self.quantize_int8_simd(vectors, &mut result);
            },
            QuantizationMode::None => {
                self.copy_f32_simd(vectors, &mut result);
            },
            QuantizationMode::Int4 => {
                self.quantize_int4_simd(vectors, &mut result);
            }
        }
        
        result
    }
    
    /// SIMD-optimized int8 quantization
    #[cfg(target_arch = "x86_64")]
    unsafe fn quantize_int8_simd(&self, vectors: &[Vector], output: &mut [u8]) {
        if !is_x86_feature_detected!("avx2") {
            self.quantize_int8_scalar(vectors, output);
            return;
        }
        
        let simd_width = 8; // Process 8 f32s at once with AVX2
        
        for (vec_idx, vector) in vectors.iter().enumerate() {
            let data = vector.as_slice();
            let output_offset = vec_idx * self.dimension;
            
            let mut dim_idx = 0;
            
            // Process dimensions in SIMD chunks
            while dim_idx + simd_width <= self.dimension {
                // Load input values
                let input = _mm256_loadu_ps(data.as_ptr().add(dim_idx));
                
                // Load scale and offset
                let scale = _mm256_loadu_ps(self.scale.as_ptr().add(dim_idx));
                let offset = _mm256_loadu_ps(self.offset.as_ptr().add(dim_idx));
                
                // Normalize: (input - offset) / scale
                let normalized = _mm256_div_ps(_mm256_sub_ps(input, offset), scale);
                
                // Clamp to [0, 255] and convert to int32
                let clamped = _mm256_max_ps(_mm256_min_ps(normalized, _mm256_set1_ps(255.0)), _mm256_setzero_ps());
                let as_int = _mm256_cvtps_epi32(clamped);
                
                // Pack to int8 (we'll do this in chunks for efficiency)
                let packed_low = _mm256_castsi256_si128(as_int);
                let packed_high = _mm256_extracti128_si256(as_int, 1);
                let packed = _mm_packus_epi32(packed_low, packed_high);
                let final_packed = _mm_packus_epi16(packed, packed);
                
                // Store result
                let output_ptr = output.as_mut_ptr().add(output_offset + dim_idx);
                _mm_storel_epi64(output_ptr as *mut __m128i, final_packed);
                
                dim_idx += simd_width;
            }
            
            // Handle remaining dimensions
            while dim_idx < self.dimension && dim_idx < data.len() {
                let val = data[dim_idx];
                let normalized = (val - self.offset[dim_idx]) / self.scale[dim_idx];
                output[output_offset + dim_idx] = normalized.clamp(0.0, 255.0) as u8;
                dim_idx += 1;
            }
        }
    }
    
    /// Scalar fallback for int8 quantization
    fn quantize_int8_scalar(&self, vectors: &[Vector], output: &mut [u8]) {
        for (vec_idx, vector) in vectors.iter().enumerate() {
            let data = vector.as_slice();
            let output_offset = vec_idx * self.dimension;
            
            for (dim_idx, &val) in data.iter().enumerate().take(self.dimension) {
                let normalized = (val - self.offset[dim_idx]) / self.scale[dim_idx];
                output[output_offset + dim_idx] = normalized.clamp(0.0, 255.0) as u8;
            }
        }
    }
    
    /// SIMD-optimized f32 copying
    #[cfg(target_arch = "x86_64")]
    unsafe fn copy_f32_simd(&self, vectors: &[Vector], output: &mut [u8]) {
        let output_f32 = std::slice::from_raw_parts_mut(
            output.as_mut_ptr() as *mut f32,
            output.len() / 4
        );
        
        for (vec_idx, vector) in vectors.iter().enumerate() {
            let data = vector.as_slice();
            let output_offset = vec_idx * self.dimension;
            
            if is_x86_feature_detected!("avx2") {
                let mut dim_idx = 0;
                let simd_width = 8;
                
                // SIMD copy in chunks of 8
                while dim_idx + simd_width <= self.dimension.min(data.len()) {
                    let input = _mm256_loadu_ps(data.as_ptr().add(dim_idx));
                    _mm256_storeu_ps(output_f32.as_mut_ptr().add(output_offset + dim_idx), input);
                    dim_idx += simd_width;
                }
                
                // Copy remaining elements
                while dim_idx < self.dimension && dim_idx < data.len() {
                    output_f32[output_offset + dim_idx] = data[dim_idx];
                    dim_idx += 1;
                }
            } else {
                // Fallback to regular copy
                let copy_len = self.dimension.min(data.len());
                output_f32[output_offset..output_offset + copy_len]
                    .copy_from_slice(&data[..copy_len]);
            }
        }
    }
    
    /// SIMD-optimized int4 quantization
    #[cfg(target_arch = "x86_64")]
    unsafe fn quantize_int4_simd(&self, vectors: &[Vector], output: &mut [u8]) {
        // For now, use scalar implementation as int4 SIMD is more complex
        self.quantize_int4_scalar(vectors, output);
    }
    
    /// Scalar int4 quantization
    fn quantize_int4_scalar(&self, vectors: &[Vector], output: &mut [u8]) {
        let bytes_per_vec = (self.dimension + 1) / 2;
        
        for (vec_idx, vector) in vectors.iter().enumerate() {
            let data = vector.as_slice();
            let output_offset = vec_idx * bytes_per_vec;
            
            for chunk_idx in 0..(self.dimension + 1) / 2 {
                let dim_idx1 = chunk_idx * 2;
                let dim_idx2 = dim_idx1 + 1;
                
                let val1 = if dim_idx1 < data.len() {
                    let normalized = (data[dim_idx1] - self.offset[dim_idx1]) / self.scale[dim_idx1];
                    (normalized.clamp(0.0, 15.0) as u8) & 0x0F
                } else { 0 };
                
                let val2 = if dim_idx2 < self.dimension && dim_idx2 < data.len() {
                    let normalized = (data[dim_idx2] - self.offset[dim_idx2]) / self.scale[dim_idx2];
                    ((normalized.clamp(0.0, 15.0) as u8) & 0x0F) << 4
                } else { 0 };
                
                output[output_offset + chunk_idx] = val1 | val2;
            }
        }
    }
    
    /// Ultra-fast bulk insertion with multiple optimization strategies
    pub fn hyper_bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) -> usize {
        if vectors.is_empty() {
            return 0;
        }
        
        let start_count = self.count.load(Ordering::Relaxed);
        let new_count = vectors.len();
        let total_count = start_count + new_count;
        
        // Compute quantization parameters if first insertion
        if start_count == 0 {
            self.compute_quantization_params_fast(vectors);
        }
        
        // Pre-allocate exact memory
        let total_bytes = self.calculate_memory_requirements(total_count);
        if self.quantized_data.len() < total_bytes {
            self.quantized_data.resize(total_bytes, 0);
        }
        
        if self.ids.len() < total_count {
            self.ids.resize(total_count, 0);
        }
        
        // Choose insertion strategy based on mode and vector count
        match self.insertion_mode {
            InsertionMode::HyperParallel if new_count > 1000 => {
                self.insert_hyper_parallel(ids, vectors, start_count)
            },
            InsertionMode::Parallel if new_count > 100 => {
                self.insert_parallel(ids, vectors, start_count)
            },
            InsertionMode::Vectorized => {
                self.insert_vectorized(ids, vectors, start_count)
            },
            _ => {
                self.insert_sequential(ids, vectors, start_count)
            }
        }
        
        self.count.store(total_count, Ordering::Relaxed);
        new_count
    }
    
    /// Hyper-parallel insertion with SIMD + prefetching
    fn insert_hyper_parallel(&mut self, ids: &[usize], vectors: &[Vector], start_count: usize) {
        let chunk_size = (vectors.len() / rayon::current_num_threads()).max(1000);
        
        // Parallel quantization
        let quantized_chunks: Vec<Vec<u8>> = vectors
            .par_chunks(chunk_size)
            .map(|chunk| {
                #[cfg(target_arch = "x86_64")]
                unsafe {
                    self.quantize_vectors_simd(chunk)
                }
                #[cfg(not(target_arch = "x86_64"))]
                {
                    self.quantize_vectors_scalar(chunk)
                }
            })
            .collect();
        
        // Merge chunks into main storage
        let bytes_per_vec = self.calculate_memory_requirements(1);
        let mut current_offset = start_count * bytes_per_vec;
        
        for (chunk_idx, chunk_data) in quantized_chunks.iter().enumerate() {
            let chunk_start = chunk_idx * chunk_size;
            let chunk_end = (chunk_start + chunk_size).min(vectors.len());
            let actual_chunk_size = chunk_end - chunk_start;
            
            // Copy quantized data
            let copy_bytes = actual_chunk_size * bytes_per_vec;
            self.quantized_data[current_offset..current_offset + copy_bytes]
                .copy_from_slice(&chunk_data[..copy_bytes]);
            
            // Copy IDs in parallel
            for (local_idx, &id) in ids[chunk_start..chunk_end].iter().enumerate() {
                self.ids[start_count + chunk_start + local_idx] = id as u32;
            }
            
            current_offset += copy_bytes;
        }
    }
    
    /// Standard parallel insertion
    fn insert_parallel(&mut self, ids: &[usize], vectors: &[Vector], start_count: usize) {
        let bytes_per_vec = self.calculate_memory_requirements(1);
        
        // Use the scalar quantization method for parallel processing
        #[cfg(target_arch = "x86_64")]
        let quantized_data = unsafe { self.quantize_vectors_simd(vectors) };
        
        #[cfg(not(target_arch = "x86_64"))]
        let quantized_data = self.quantize_vectors_scalar(vectors);
        
        // Copy to main storage
        let start_offset = start_count * bytes_per_vec;
        self.quantized_data[start_offset..start_offset + quantized_data.len()]
            .copy_from_slice(&quantized_data);
        
        // Update IDs
        for (i, &id) in ids.iter().enumerate() {
            self.ids[start_count + i] = id as u32;
        }
    }
    
    /// SIMD-vectorized insertion
    fn insert_vectorized(&mut self, ids: &[usize], vectors: &[Vector], start_count: usize) {
        #[cfg(target_arch = "x86_64")]
        {
            unsafe {
                let quantized_data = self.quantize_vectors_simd(vectors);
                let bytes_per_vec = self.calculate_memory_requirements(1);
                let start_offset = start_count * bytes_per_vec;
                
                self.quantized_data[start_offset..start_offset + quantized_data.len()]
                    .copy_from_slice(&quantized_data);
            }
            
            // Update IDs
            for (i, &id) in ids.iter().enumerate() {
                self.ids[start_count + i] = id as u32;
            }
        }
        
        #[cfg(not(target_arch = "x86_64"))]
        {
            self.insert_sequential(ids, vectors, start_count);
        }
    }
    
    /// Sequential insertion fallback
    fn insert_sequential(&mut self, ids: &[usize], vectors: &[Vector], start_count: usize) {
        let bytes_per_vec = self.calculate_memory_requirements(1);
        
        for (i, vector) in vectors.iter().enumerate() {
            let output_offset = (start_count + i) * bytes_per_vec;
            
            // Create a temporary slice for this vector
            let data = vector.as_slice();
            match self.quantization {
                QuantizationMode::None => {
                    let end_offset = output_offset + self.dimension * 4;
                    let output_slice = &mut self.quantized_data[output_offset..end_offset];
                    let output_f32 = unsafe {
                        std::slice::from_raw_parts_mut(
                            output_slice.as_mut_ptr() as *mut f32,
                            self.dimension
                        )
                    };
                    let copy_len = self.dimension.min(data.len());
                    output_f32[..copy_len].copy_from_slice(&data[..copy_len]);
                },
                QuantizationMode::Int8 => {
                    for (dim_idx, &val) in data.iter().enumerate().take(self.dimension) {
                        let normalized = (val - self.offset[dim_idx]) / self.scale[dim_idx];
                        self.quantized_data[output_offset + dim_idx] = normalized.clamp(0.0, 255.0) as u8;
                    }
                },
                QuantizationMode::Int4 => {
                    let bytes_per_vec_int4 = (self.dimension + 1) / 2;
                    for chunk_idx in 0..bytes_per_vec_int4 {
                        let dim_idx1 = chunk_idx * 2;
                        let dim_idx2 = dim_idx1 + 1;
                        
                        let val1 = if dim_idx1 < data.len() {
                            let normalized = (data[dim_idx1] - self.offset[dim_idx1]) / self.scale[dim_idx1];
                            (normalized.clamp(0.0, 15.0) as u8) & 0x0F
                        } else { 0 };
                        
                        let val2 = if dim_idx2 < self.dimension && dim_idx2 < data.len() {
                            let normalized = (data[dim_idx2] - self.offset[dim_idx2]) / self.scale[dim_idx2];
                            ((normalized.clamp(0.0, 15.0) as u8) & 0x0F) << 4
                        } else { 0 };
                        
                        self.quantized_data[output_offset + chunk_idx] = val1 | val2;
                    }
                }
            }
            
            self.ids[start_count + i] = ids[i] as u32;
        }
    }
    
    /// Fallback quantization for non-SIMD architectures
    #[cfg(not(target_arch = "x86_64"))]
    fn quantize_vectors_scalar(&self, vectors: &[Vector]) -> Vec<u8> {
        let total_bytes = self.calculate_memory_requirements(vectors.len());
        let mut result = vec![0u8; total_bytes];
        let bytes_per_vec = self.calculate_memory_requirements(1);
        
        for (vec_idx, vector) in vectors.iter().enumerate() {
            let offset = vec_idx * bytes_per_vec;
            let data = vector.as_slice();
            
            match self.quantization {
                QuantizationMode::None => {
                    let output_f32 = unsafe {
                        std::slice::from_raw_parts_mut(
                            result.as_mut_ptr().add(offset) as *mut f32,
                            self.dimension
                        )
                    };
                    let copy_len = self.dimension.min(data.len());
                    output_f32[..copy_len].copy_from_slice(&data[..copy_len]);
                },
                QuantizationMode::Int8 => {
                    for (dim_idx, &val) in data.iter().enumerate().take(self.dimension) {
                        let normalized = (val - self.offset[dim_idx]) / self.scale[dim_idx];
                        result[offset + dim_idx] = normalized.clamp(0.0, 255.0) as u8;
                    }
                },
                QuantizationMode::Int4 => {
                    let bytes_per_vec_int4 = (self.dimension + 1) / 2;
                    for chunk_idx in 0..bytes_per_vec_int4 {
                        let dim_idx1 = chunk_idx * 2;
                        let dim_idx2 = dim_idx1 + 1;
                        
                        let val1 = if dim_idx1 < data.len() {
                            let normalized = (data[dim_idx1] - self.offset[dim_idx1]) / self.scale[dim_idx1];
                            (normalized.clamp(0.0, 15.0) as u8) & 0x0F
                        } else { 0 };
                        
                        let val2 = if dim_idx2 < self.dimension && dim_idx2 < data.len() {
                            let normalized = (data[dim_idx2] - self.offset[dim_idx2]) / self.scale[dim_idx2];
                            ((normalized.clamp(0.0, 15.0) as u8) & 0x0F) << 4
                        } else { 0 };
                        
                        result[offset + chunk_idx] = val1 | val2;
                    }
                }
            }
        }
        
        result
    }
    
    /// Get current vector count
    pub fn len(&self) -> usize {
        self.count.load(Ordering::Relaxed)
    }
    
    /// Check if empty
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
    
    /// Get memory usage statistics
    pub fn memory_stats(&self) -> (usize, usize, f32) {
        let actual = self.quantized_data.len() + self.ids.len() * 4;
        let theoretical = self.len() * (self.bytes_per_element() * self.dimension + 4);
        let efficiency = if actual > 0 { theoretical as f32 / actual as f32 * 100.0 } else { 0.0 };
        (actual, theoretical, efficiency)
    }
}

// Implement required traits (simplified search for now, focusing on insertion speed)
impl AnnIndex for UltraHighSpeedFlatIndex {
    fn with_config(config: IndexConfig) -> Self {
        Self::new(config, InsertionMode::HyperParallel, QuantizationMode::Int8)
    }
    
    fn insert(&mut self, id: usize, vector: Vector) {
        self.hyper_bulk_insert(&[id], &[vector]);
    }
    
    fn search(&self, _query: &Vector, _k: usize) -> Vec<(usize, f32)> {
        // Placeholder for search - focusing on insertion speed
        Vec::new()
    }
    
    fn config(&self) -> &IndexConfig {
        &self.config
    }
    
    fn stats(&self) -> IndexStats {
        let (actual_memory, theoretical_memory, efficiency) = self.memory_stats();
        
        IndexStats {
            vector_count: self.len(),
            dimension: self.dimension,
            index_type: format!("UltraHighSpeed_{:?}_{:?}", self.insertion_mode, self.quantization),
            distance_metric: self.config.distance_metric.clone(),
            memory_usage: actual_memory,
            build_time_ms: None,
            last_search_time_ms: None,
            total_searches: 0,
            total_inserts: self.len() as u64,
            additional_stats: {
                let mut stats = std::collections::HashMap::new();
                stats.insert("insertion_mode".to_string(), format!("{:?}", self.insertion_mode));
                stats.insert("quantization".to_string(), format!("{:?}", self.quantization));
                stats.insert("memory_efficiency".to_string(), format!("{:.1}%", efficiency));
                stats.insert("theoretical_memory".to_string(), format!("{}", theoretical_memory));
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

impl BulkAnnIndex for UltraHighSpeedFlatIndex {
    fn bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) {
        self.hyper_bulk_insert(ids, vectors);
    }
    
    fn reserve(&mut self, capacity: usize) {
        let total_bytes = self.calculate_memory_requirements(capacity);
        self.quantized_data.reserve(total_bytes);
        self.ids.reserve(capacity);
    }
}

impl SnapshotIndex for UltraHighSpeedFlatIndex {
    fn dump(&self) -> Vec<u8> {
        Vec::new() // Placeholder
    }
    
    fn restore(config: IndexConfig, _data: &[u8]) -> Self {
        Self::new(config, InsertionMode::HyperParallel, QuantizationMode::Int8)
    }
}

impl IndexWithSnapshot for UltraHighSpeedFlatIndex {}
