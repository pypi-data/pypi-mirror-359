//! Ultra Memory-Optimized Quantized Flat Index
//! Implements FAISS-style quantization and memory optimization

use core::{Vector, DistanceMetric};
use super::{AnnIndex, IndexConfig, IndexStats, BulkAnnIndex, SnapshotIndex, IndexWithSnapshot};
use rayon::prelude::*;

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// Quantization modes for memory optimization
#[derive(Debug, Clone, Copy)]
pub enum QuantizationMode {
    None,      // Full f32 precision (4 bytes per element)
    Int8,      // 8-bit quantization (1 byte per element) - 4x memory reduction
    Int4,      // 4-bit quantization (0.5 bytes per element) - 8x memory reduction
}

/// Ultra memory-optimized index with quantization
pub struct UltraOptimizedFlatIndex {
    config: IndexConfig,
    dimension: usize,
    count: usize,
    
    /// Quantization configuration
    quantization: QuantizationMode,
    
    /// Quantized vector storage (packed for maximum efficiency)
    quantized_data: Vec<u8>,
    
    /// Quantization parameters
    scale: Vec<f32>,        // Per-dimension scaling factor
    offset: Vec<f32>,       // Per-dimension offset
    
    /// Vector IDs (minimal storage)
    ids: Vec<u32>,          // Use u32 instead of usize to save memory
    
    /// Pre-allocated search buffers (reused)
    search_buffer: Vec<f32>,
    indices_buffer: Vec<u32>,
}

impl UltraOptimizedFlatIndex {
    /// Create new ultra-optimized index with quantization
    pub fn new(config: IndexConfig, quantization: QuantizationMode) -> Self {
        let dimension = config.dim;
        
        Self {
            config,
            dimension,
            count: 0,
            quantization,
            quantized_data: Vec::new(),
            scale: vec![1.0; dimension],
            offset: vec![0.0; dimension],
            ids: Vec::new(),
            search_buffer: Vec::new(),
            indices_buffer: Vec::new(),
        }
    }
    
    /// Get bytes per element based on quantization mode
    fn bytes_per_element(&self) -> usize {
        match self.quantization {
            QuantizationMode::None => 4,   // f32
            QuantizationMode::Int8 => 1,   // u8
            QuantizationMode::Int4 => 1,   // u8 (packed 2 per byte)
        }
    }
    
    /// Calculate quantization parameters from training data
    fn compute_quantization_params(&mut self, vectors: &[Vector]) {
        if matches!(self.quantization, QuantizationMode::None) {
            return;
        }
        
        // Compute per-dimension min/max for optimal quantization
        let mut min_vals = vec![f32::INFINITY; self.dimension];
        let mut max_vals = vec![f32::NEG_INFINITY; self.dimension];
        
        for vector in vectors {
            let data = vector.as_slice();
            for (i, &val) in data.iter().enumerate() {
                min_vals[i] = min_vals[i].min(val);
                max_vals[i] = max_vals[i].max(val);
            }
        }
        
        // Compute scale and offset for quantization
        for i in 0..self.dimension {
            let range = max_vals[i] - min_vals[i];
            self.offset[i] = min_vals[i];
            
            self.scale[i] = match self.quantization {
                QuantizationMode::Int8 => range / 255.0,
                QuantizationMode::Int4 => range / 15.0,
                QuantizationMode::None => 1.0,
            };
            
            // Avoid division by zero
            if self.scale[i] == 0.0 {
                self.scale[i] = 1.0;
            }
        }
    }
    
    /// Quantize a single vector
    fn quantize_vector(&self, vector: &[f32]) -> Vec<u8> {
        match self.quantization {
            QuantizationMode::None => {
                // Store as raw f32 bytes
                let mut result = Vec::with_capacity(self.dimension * 4);
                for &val in vector {
                    result.extend_from_slice(&val.to_le_bytes());
                }
                result
            },
            QuantizationMode::Int8 => {
                vector.iter().enumerate().map(|(i, &val)| {
                    let normalized = (val - self.offset[i]) / self.scale[i];
                    normalized.clamp(0.0, 255.0) as u8
                }).collect()
            },
            QuantizationMode::Int4 => {
                let mut result = Vec::with_capacity((self.dimension + 1) / 2);
                for chunk in vector.chunks(2) {
                    let val1 = {
                        let normalized = (chunk[0] - self.offset[0]) / self.scale[0];
                        (normalized.clamp(0.0, 15.0) as u8) & 0x0F
                    };
                    let val2 = if chunk.len() > 1 {
                        let idx = if chunk.len() > 1 { 1 } else { 0 };
                        let normalized = (chunk[idx] - self.offset[idx]) / self.scale[idx];
                        ((normalized.clamp(0.0, 15.0) as u8) & 0x0F) << 4
                    } else {
                        0
                    };
                    result.push(val1 | val2);
                }
                result
            }
        }
    }
    
    /// Dequantize vector for distance computation
    fn dequantize_vector(&self, vec_idx: usize, output: &mut [f32]) {
        let bytes_per_vec = self.bytes_per_element() * match self.quantization {
            QuantizationMode::None => self.dimension,
            QuantizationMode::Int8 => self.dimension,
            QuantizationMode::Int4 => (self.dimension + 1) / 2,
        };
        
        let start_byte = vec_idx * bytes_per_vec;
        let data = &self.quantized_data[start_byte..start_byte + bytes_per_vec];
        
        match self.quantization {
            QuantizationMode::None => {
                for (i, chunk) in data.chunks(4).enumerate() {
                    if i < self.dimension {
                        output[i] = f32::from_le_bytes([chunk[0], chunk[1], chunk[2], chunk[3]]);
                    }
                }
            },
            QuantizationMode::Int8 => {
                for (i, &byte_val) in data.iter().enumerate() {
                    if i < self.dimension {
                        output[i] = self.offset[i] + (byte_val as f32) * self.scale[i];
                    }
                }
            },
            QuantizationMode::Int4 => {
                for (byte_idx, &packed_byte) in data.iter().enumerate() {
                    let dim_idx1 = byte_idx * 2;
                    let dim_idx2 = dim_idx1 + 1;
                    
                    if dim_idx1 < self.dimension {
                        let val1 = packed_byte & 0x0F;
                        output[dim_idx1] = self.offset[dim_idx1] + (val1 as f32) * self.scale[dim_idx1];
                    }
                    
                    if dim_idx2 < self.dimension {
                        let val2 = (packed_byte >> 4) & 0x0F;
                        output[dim_idx2] = self.offset[dim_idx2] + (val2 as f32) * self.scale[dim_idx2];
                    }
                }
            }
        }
    }
    
    /// FAISS-style optimized bulk insertion with quantization
    pub fn ultra_bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) -> usize {
        if vectors.is_empty() {
            return 0;
        }
        
        let new_count = vectors.len();
        let total_count = self.count + new_count;
        
        // Compute quantization parameters if this is the first insertion
        if self.count == 0 {
            self.compute_quantization_params(vectors);
        }
        
        // Calculate exact memory requirements
        let bytes_per_vec = self.bytes_per_element() * match self.quantization {
            QuantizationMode::None => self.dimension,
            QuantizationMode::Int8 => self.dimension,
            QuantizationMode::Int4 => (self.dimension + 1) / 2,
        };
        
        let total_bytes = total_count * bytes_per_vec;
        
        // Pre-allocate exact memory (no over-allocation like FAISS)
        if self.quantized_data.len() < total_bytes {
            self.quantized_data.resize(total_bytes, 0);
        }
        
        if self.ids.len() < total_count {
            self.ids.resize(total_count, 0);
        }
        
        // Quantize and store vectors efficiently
        let start_offset = self.count * bytes_per_vec;
        
        // Parallel quantization for speed
        let quantized_vectors: Vec<Vec<u8>> = vectors.par_iter()
            .map(|v| self.quantize_vector(v.as_slice()))
            .collect();
        
        // Bulk copy quantized data
        for (i, quantized) in quantized_vectors.iter().enumerate() {
            let dst_offset = start_offset + i * bytes_per_vec;
            self.quantized_data[dst_offset..dst_offset + quantized.len()]
                .copy_from_slice(quantized);
        }
        
        // Update IDs (use u32 to save memory)
        for (i, &id) in ids.iter().enumerate() {
            self.ids[self.count + i] = id as u32;
        }
        
        self.count = total_count;
        
        // Update search buffers only if needed
        if self.search_buffer.len() < self.count {
            self.search_buffer.resize(self.count, 0.0);
            self.indices_buffer.resize(self.count, 0);
        }
        
        new_count
    }
    
    /// Optimized distance computation with quantization awareness
    fn compute_distances_quantized(&self, query: &[f32], distances: &mut [f32]) {
        match self.quantization {
            QuantizationMode::None => {
                // Use SIMD for full precision
                self.compute_distances_f32_simd(query, distances);
            },
            QuantizationMode::Int8 => {
                // Optimized int8 distance computation
                self.compute_distances_int8_simd(query, distances);
            },
            QuantizationMode::Int4 => {
                // Fallback for int4 (more complex SIMD)
                self.compute_distances_int4(query, distances);
            }
        }
    }
    
    /// SIMD-optimized f32 distance computation
    fn compute_distances_f32_simd(&self, query: &[f32], distances: &mut [f32]) {
        let mut temp_vector = vec![0.0f32; self.dimension];
        
        for vec_idx in 0..self.count {
            self.dequantize_vector(vec_idx, &mut temp_vector);
            
            let mut sum = 0.0f32;
            
            #[cfg(target_arch = "x86_64")]
            {
                if is_x86_feature_detected!("avx2") {
                    sum = unsafe { self.compute_l2_avx2(query, &temp_vector) };
                } else {
                    sum = self.compute_l2_scalar(query, &temp_vector);
                }
            }
            
            #[cfg(not(target_arch = "x86_64"))]
            {
                sum = self.compute_l2_scalar(query, &temp_vector);
            }
            
            distances[vec_idx] = sum;
        }
    }
    
    /// Optimized int8 distance computation (avoids dequantization)
    fn compute_distances_int8_simd(&self, query: &[f32], distances: &mut [f32]) {
        // Quantize query once
        let quantized_query: Vec<u8> = query.iter().enumerate().map(|(i, &val)| {
            let normalized = (val - self.offset[i]) / self.scale[i];
            normalized.clamp(0.0, 255.0) as u8
        }).collect();
        
        let bytes_per_vec = self.dimension;
        
        for vec_idx in 0..self.count {
            let start_byte = vec_idx * bytes_per_vec;
            let vec_data = &self.quantized_data[start_byte..start_byte + bytes_per_vec];
            
            // Compute distance directly on quantized data
            let mut sum = 0.0f32;
            
            for i in 0..self.dimension {
                let diff = (quantized_query[i] as f32) - (vec_data[i] as f32);
                sum += diff * diff * self.scale[i] * self.scale[i];
            }
            
            distances[vec_idx] = sum;
        }
    }
    
    /// Int4 distance computation
    fn compute_distances_int4(&self, query: &[f32], distances: &mut [f32]) {
        let mut temp_vector = vec![0.0f32; self.dimension];
        
        for vec_idx in 0..self.count {
            self.dequantize_vector(vec_idx, &mut temp_vector);
            distances[vec_idx] = self.compute_l2_scalar(query, &temp_vector);
        }
    }
    
    /// Scalar L2 distance computation
    #[inline(always)]
    fn compute_l2_scalar(&self, a: &[f32], b: &[f32]) -> f32 {
        let mut sum = 0.0f32;
        for i in 0..self.dimension {
            let diff = a[i] - b[i];
            sum += diff * diff;
        }
        sum
    }
    
    /// AVX2 optimized L2 distance
    #[cfg(target_arch = "x86_64")]
    #[inline(always)]
    unsafe fn compute_l2_avx2(&self, a: &[f32], b: &[f32]) -> f32 {
        let mut sum_vec = _mm256_setzero_ps();
        let simd_width = 8;
        let simd_chunks = self.dimension / simd_width;
        
        for i in 0..simd_chunks {
            let offset = i * simd_width;
            let a_vec = _mm256_loadu_ps(a.as_ptr().add(offset));
            let b_vec = _mm256_loadu_ps(b.as_ptr().add(offset));
            let diff = _mm256_sub_ps(a_vec, b_vec);
            sum_vec = _mm256_fmadd_ps(diff, diff, sum_vec);
        }
        
        // Horizontal sum
        let sum_high = _mm256_extractf128_ps(sum_vec, 1);
        let sum_low = _mm256_castps256_ps128(sum_vec);
        let sum_combined = _mm_add_ps(sum_high, sum_low);
        let sum_shuf = _mm_movehl_ps(sum_combined, sum_combined);
        let sum_final = _mm_add_ps(sum_combined, sum_shuf);
        let sum_single = _mm_add_ss(sum_final, _mm_shuffle_ps(sum_final, sum_final, 0x55));
        
        let mut result = _mm_cvtss_f32(sum_single);
        
        // Handle remainder
        for i in (simd_chunks * simd_width)..self.dimension {
            let diff = a[i] - b[i];
            result += diff * diff;
        }
        
        result
    }
    
    /// Memory usage report
    pub fn memory_usage_bytes(&self) -> usize {
        let vector_storage = self.quantized_data.len();
        let ids_storage = self.ids.len() * 4; // u32
        let metadata = self.scale.len() * 4 + self.offset.len() * 4;
        let buffers = self.search_buffer.len() * 4 + self.indices_buffer.len() * 4;
        
        vector_storage + ids_storage + metadata + buffers
    }
    
    /// Get theoretical minimum memory usage
    pub fn theoretical_minimum_bytes(&self) -> usize {
        self.count * self.dimension * self.bytes_per_element() + self.count * 4
    }
    
    /// Memory efficiency as percentage
    pub fn memory_efficiency(&self) -> f32 {
        let theoretical = self.theoretical_minimum_bytes() as f32;
        let actual = self.memory_usage_bytes() as f32;
        (theoretical / actual) * 100.0
    }
}

// Implement required traits
impl AnnIndex for UltraOptimizedFlatIndex {
    fn with_config(config: IndexConfig) -> Self {
        // Default to Int8 quantization for good balance of speed and accuracy
        Self::new(config, QuantizationMode::Int8)
    }
    
    fn insert(&mut self, id: usize, vector: Vector) {
        self.ultra_bulk_insert(&[id], &[vector]);
    }
    
    fn search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        if self.count == 0 || k == 0 {
            return Vec::new();
        }
        
        let k = k.min(self.count);
        let mut distances = vec![0.0f32; self.count];
        let mut indices: Vec<usize> = (0..self.count).collect();
        
        // Compute distances with quantization awareness
        self.compute_distances_quantized(query.as_slice(), &mut distances);
        
        // Partial sort for efficiency
        indices.select_nth_unstable_by(k, |&a, &b| {
            distances[a].partial_cmp(&distances[b]).unwrap_or(std::cmp::Ordering::Equal)
        });
        
        // Sort top-k results
        indices[..k].sort_unstable_by(|&a, &b| {
            distances[a].partial_cmp(&distances[b]).unwrap_or(std::cmp::Ordering::Equal)
        });
        
        // Return results with sqrt for actual L2 distance
        indices[..k].iter()
            .map(|&idx| (self.ids[idx] as usize, distances[idx].sqrt()))
            .collect()
    }
    
    fn config(&self) -> &IndexConfig {
        &self.config
    }
    
    fn stats(&self) -> IndexStats {
        IndexStats {
            vector_count: self.count,
            dimension: self.dimension,
            index_type: format!("UltraOptimizedFlat_{:?}", self.quantization),
            distance_metric: self.config.distance_metric.clone(),
            memory_usage: self.memory_usage_bytes(),
            build_time_ms: None,
            last_search_time_ms: None,
            total_searches: 0,
            total_inserts: self.count as u64,
            additional_stats: {
                let mut stats = std::collections::HashMap::new();
                stats.insert("quantization".to_string(), format!("{:?}", self.quantization));
                stats.insert("memory_efficiency".to_string(), format!("{:.1}%", self.memory_efficiency()));
                stats.insert("theoretical_min_mb".to_string(), 
                    format!("{:.1}", self.theoretical_minimum_bytes() as f32 / 1024.0 / 1024.0));
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

impl BulkAnnIndex for UltraOptimizedFlatIndex {
    fn bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) {
        self.ultra_bulk_insert(ids, vectors);
    }
    
    fn reserve(&mut self, capacity: usize) {
        let bytes_per_vec = self.bytes_per_element() * match self.quantization {
            QuantizationMode::None => self.dimension,
            QuantizationMode::Int8 => self.dimension,
            QuantizationMode::Int4 => (self.dimension + 1) / 2,
        };
        
        self.quantized_data.reserve(capacity * bytes_per_vec);
        self.ids.reserve(capacity);
    }
}

impl SnapshotIndex for UltraOptimizedFlatIndex {
    fn dump(&self) -> Vec<u8> {
        // Simple binary serialization
        Vec::new() // Placeholder - implement actual serialization
    }
    
    fn restore(config: IndexConfig, _data: &[u8]) -> Self {
        Self::new(config, QuantizationMode::Int8) // Placeholder
    }
}

impl IndexWithSnapshot for UltraOptimizedFlatIndex {}
