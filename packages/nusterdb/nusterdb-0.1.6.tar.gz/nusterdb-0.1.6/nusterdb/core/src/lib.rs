//! core: basic vector types & math ops with SIMD optimizations

use std::ops::{Add, Sub, Mul, Div};
use serde::{Serialize, Deserialize};

// Add SIMD support
#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// A simple n-dimensional vector of f32s with SIMD optimizations.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Vector {
    data: Vec<f32>,
}

impl Vector {
    /// Create a new vector. Panics if `data` is empty.
    pub fn new(data: Vec<f32>) -> Self {
        assert!(!data.is_empty(), "Vector must have at least one dimension");
        Self { data }
    }

    /// Create a zero vector of given dimension
    pub fn zeros(dim: usize) -> Self {
        assert!(dim > 0, "Dimension must be positive");
        Self { data: vec![0.0; dim] }
    }

    /// Create a vector of ones with given dimension
    pub fn ones(dim: usize) -> Self {
        assert!(dim > 0, "Dimension must be positive");
        Self { data: vec![1.0; dim] }
    }

    /// Create a random vector with values in range [min, max]
    pub fn random(dim: usize, min: f32, max: f32) -> Self {
        assert!(dim > 0, "Dimension must be positive");
        assert!(min <= max, "min must be <= max");
        
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut data = Vec::with_capacity(dim);
        let mut hasher = DefaultHasher::new();
        
        for i in 0..dim {
            i.hash(&mut hasher);
            let hash = hasher.finish();
            let normalized = (hash as f32) / (u64::MAX as f32);
            data.push(min + normalized * (max - min));
        }
        
        Self { data }
    }

    /// Create a unit vector (normalized to length 1)
    pub fn unit_random(dim: usize) -> Self {
        let mut v = Self::random(dim, -1.0, 1.0);
        v.normalize_mut();
        v
    }

    /// Get raw data as slice
    pub fn as_slice(&self) -> &[f32] {
        &self.data
    }

    /// Get raw data as mutable slice
    pub fn as_mut_slice(&mut self) -> &mut [f32] {
        &mut self.data
    }

    /// Get raw data as owned vector
    pub fn raw(&self) -> Vec<f32> {
        self.data.clone()
    }

    /// Get raw data as owned vector (consuming self)
    pub fn into_raw(self) -> Vec<f32> {
        self.data
    }

    /// Return dimension (length) of this vector.
    pub fn dim(&self) -> usize {
        self.data.len()
    }

    /// Get element at index
    pub fn get(&self, index: usize) -> Option<f32> {
        self.data.get(index).copied()
    }

    /// Set element at index
    pub fn set(&mut self, index: usize, value: f32) -> Result<(), String> {
        if index >= self.data.len() {
            return Err(format!("Index {} out of bounds for vector of dimension {}", index, self.data.len()));
        }
        self.data[index] = value;
        Ok(())
    }

    /// Check if vector contains only finite values
    pub fn is_finite(&self) -> bool {
        self.data.iter().all(|&x| x.is_finite())
    }

    /// Check if vector is normalized (unit length)
    pub fn is_normalized(&self, tolerance: f32) -> bool {
        (self.norm() - 1.0).abs() < tolerance
    }

    /// SIMD-optimized dot product: ⟨self, other⟩.
    #[cfg(target_arch = "x86_64")]
    pub fn dot(&self, other: &Self) -> f32 {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        
        if is_x86_feature_detected!("avx2") {
            unsafe { self.dot_avx2(other) }
        } else if is_x86_feature_detected!("sse") {
            unsafe { self.dot_sse(other) }
        } else {
            self.dot_fallback(other)
        }
    }

    #[cfg(not(target_arch = "x86_64"))]
    pub fn dot(&self, other: &Self) -> f32 {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        self.dot_fallback(other)
    }

    /// Fallback dot product implementation
    fn dot_fallback(&self, other: &Self) -> f32 {
        self.data.iter()
            .zip(&other.data)
            .map(|(a, b)| a * b)
            .sum()
    }

    /// AVX2-optimized dot product
    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "avx2")]
    unsafe fn dot_avx2(&self, other: &Self) -> f32 {
        let mut result = 0.0f32;
        let len = self.data.len();
        let chunks = len / 8;
        let _remainder = len % 8;

        let mut sum_vec = unsafe { _mm256_setzero_ps() };
        
        for i in 0..chunks {
            let offset = i * 8;
            let a_vec = unsafe { _mm256_loadu_ps(self.data.as_ptr().add(offset)) };
            let b_vec = unsafe { _mm256_loadu_ps(other.data.as_ptr().add(offset)) };
            let mul_vec = unsafe { _mm256_mul_ps(a_vec, b_vec) };
            sum_vec = unsafe { _mm256_add_ps(sum_vec, mul_vec) };
        }

        // Horizontal sum of AVX2 register
        let sum_high = unsafe { _mm256_extractf128_ps(sum_vec, 1) };
        let sum_low = unsafe { _mm256_castps256_ps128(sum_vec) };
        let sum_sse = unsafe { _mm_add_ps(sum_high, sum_low) };
        let sum_64 = unsafe { _mm_add_ps(sum_sse, _mm_movehl_ps(sum_sse, sum_sse)) };
        let sum_32 = unsafe { _mm_add_ss(sum_64, _mm_shuffle_ps(sum_64, sum_64, 0x55)) };
        result = unsafe { _mm_cvtss_f32(sum_32) };

        // Handle remainder
        for i in (chunks * 8)..len {
            result += self.data[i] * other.data[i];
        }

        result
    }

    /// SSE-optimized dot product
    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "sse")]
    unsafe fn dot_sse(&self, other: &Self) -> f32 {
        let mut result = 0.0f32;
        let len = self.data.len();
        let chunks = len / 4;
        let _remainder = len % 4;

        let mut sum_vec = unsafe { _mm_setzero_ps() };
        
        for i in 0..chunks {
            let offset = i * 4;
            let a_vec = unsafe { _mm_loadu_ps(self.data.as_ptr().add(offset)) };
            let b_vec = unsafe { _mm_loadu_ps(other.data.as_ptr().add(offset)) };
            let mul_vec = unsafe { _mm_mul_ps(a_vec, b_vec) };
            sum_vec = unsafe { _mm_add_ps(sum_vec, mul_vec) };
        }

        // Horizontal sum of SSE register
        let sum_64 = unsafe { _mm_add_ps(sum_vec, _mm_movehl_ps(sum_vec, sum_vec)) };
        let sum_32 = unsafe { _mm_add_ss(sum_64, _mm_shuffle_ps(sum_64, sum_64, 0x55)) };
        result = unsafe { _mm_cvtss_f32(sum_32) };

        // Handle remainder
        for i in (chunks * 4)..len {
            result += self.data[i] * other.data[i];
        }

        result
    }

    /// SIMD-optimized euclidean distance squared
    #[cfg(target_arch = "x86_64")]
    pub fn euclidean_distance_squared(&self, other: &Self) -> f32 {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        
        if is_x86_feature_detected!("avx2") {
            unsafe { self.euclidean_distance_squared_avx2(other) }
        } else if is_x86_feature_detected!("sse") {
            unsafe { self.euclidean_distance_squared_sse(other) }
        } else {
            self.euclidean_distance_squared_fallback(other)
        }
    }

    #[cfg(not(target_arch = "x86_64"))]
    pub fn euclidean_distance_squared(&self, other: &Self) -> f32 {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        self.euclidean_distance_squared_fallback(other)
    }

    fn euclidean_distance_squared_fallback(&self, other: &Self) -> f32 {
        self.data.iter()
            .zip(&other.data)
            .map(|(a, b)| (a - b).powi(2))
            .sum()
    }

    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "avx2")]
    unsafe fn euclidean_distance_squared_avx2(&self, other: &Self) -> f32 {
        let mut result = 0.0f32;
        let len = self.data.len();
        let chunks = len / 8;
        let remainder = len % 8;

        let mut sum_vec = _mm256_setzero_ps();
        
        for i in 0..chunks {
            let offset = i * 8;
            let a_vec = _mm256_loadu_ps(self.data.as_ptr().add(offset));
            let b_vec = _mm256_loadu_ps(other.data.as_ptr().add(offset));
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
        result = _mm_cvtss_f32(sum_32);

        // Handle remainder
        for i in (chunks * 8)..len {
            let diff = self.data[i] - other.data[i];
            result += diff * diff;
        }

        result
    }

    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "sse")]
    unsafe fn euclidean_distance_squared_sse(&self, other: &Self) -> f32 {
        let mut result = 0.0f32;
        let len = self.data.len();
        let chunks = len / 4;
        let remainder = len % 4;

        let mut sum_vec = _mm_setzero_ps();
        
        for i in 0..chunks {
            let offset = i * 4;
            let a_vec = _mm_loadu_ps(self.data.as_ptr().add(offset));
            let b_vec = _mm_loadu_ps(other.data.as_ptr().add(offset));
            let diff_vec = _mm_sub_ps(a_vec, b_vec);
            let sq_vec = _mm_mul_ps(diff_vec, diff_vec);
            sum_vec = _mm_add_ps(sum_vec, sq_vec);
        }

        // Horizontal sum
        let sum_64 = _mm_add_ps(sum_vec, _mm_movehl_ps(sum_vec, sum_vec));
        let sum_32 = _mm_add_ss(sum_64, _mm_shuffle_ps(sum_64, sum_64, 0x55));
        result = _mm_cvtss_f32(sum_32);

        // Handle remainder
        for i in (chunks * 4)..len {
            let diff = self.data[i] - other.data[i];
            result += diff * diff;
        }

        result
    }

    /// Euclidean norm (L2 norm): ‖self‖ = sqrt(⟨self, self⟩)
    pub fn norm(&self) -> f32 {
        self.dot(self).sqrt()
    }

    /// L1 norm (Manhattan norm): sum of absolute values
    pub fn l1_norm(&self) -> f32 {
        self.data.iter().map(|x| x.abs()).sum()
    }

    /// L∞ norm (max norm): maximum absolute value
    pub fn linf_norm(&self) -> f32 {
        self.data.iter().map(|x| x.abs()).fold(0.0, f32::max)
    }

    /// Squared L2 norm (avoids sqrt for efficiency)
    pub fn norm_squared(&self) -> f32 {
        self.dot(self)
    }

    /// Normalize to unit length (returns new vector)
    pub fn normalize(&self) -> Self {
        let norm = self.norm();
        if norm == 0.0 {
            return self.clone();
        }
        self.clone() / norm
    }

    /// Normalize to unit length (modifies in place)
    pub fn normalize_mut(&mut self) {
        let norm = self.norm();
        if norm != 0.0 {
            for x in &mut self.data {
                *x /= norm;
            }
        }
    }

    /// Euclidean distance: ‖self - other‖
    pub fn euclidean_distance(&self, other: &Self) -> f32 {
        self.euclidean_distance_squared(other).sqrt()
    }

    /// Manhattan distance (L1 distance)
    pub fn manhattan_distance(&self, other: &Self) -> f32 {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        self.data.iter()
            .zip(&other.data)
            .map(|(a, b)| (a - b).abs())
            .sum()
    }

    /// Chebyshev distance (L∞ distance)
    pub fn chebyshev_distance(&self, other: &Self) -> f32 {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        self.data.iter()
            .zip(&other.data)
            .map(|(a, b)| (a - b).abs())
            .fold(0.0, f32::max)
    }

    /// Cosine similarity: ⟨self, other⟩ / (‖self‖ · ‖other‖)
    pub fn cosine_similarity(&self, other: &Self) -> f32 {
        let denom = self.norm() * other.norm();
        if denom == 0.0 {
            0.0
        } else {
            self.dot(other) / denom
        }
    }

    /// Cosine distance: 1 - cosine_similarity
    pub fn cosine_distance(&self, other: &Self) -> f32 {
        1.0 - self.cosine_similarity(other)
    }

    /// Angular distance: arccos(cosine_similarity) / π
    pub fn angular_distance(&self, other: &Self) -> f32 {
        let cos_sim = self.cosine_similarity(other).clamp(-1.0, 1.0);
        cos_sim.acos() / std::f32::consts::PI
    }

    /// Jaccard similarity (for binary vectors)
    pub fn jaccard_similarity(&self, other: &Self) -> f32 {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        
        let mut intersection = 0.0;
        let mut union = 0.0;
        
        for (a, b) in self.data.iter().zip(&other.data) {
            let a_binary = if *a > 0.0 { 1.0 } else { 0.0 };
            let b_binary = if *b > 0.0 { 1.0 } else { 0.0 };
            
            intersection += a_binary * b_binary;
            union += if a_binary > 0.0 || b_binary > 0.0 { 1.0 } else { 0.0 };
        }
        
        if union == 0.0 { 0.0 } else { intersection / union }
    }

    /// Hamming distance (for binary vectors)
    pub fn hamming_distance(&self, other: &Self) -> f32 {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        
        self.data.iter()
            .zip(&other.data)
            .map(|(a, b)| {
                let a_binary = if *a > 0.0 { 1.0 } else { 0.0 };
                let b_binary = if *b > 0.0 { 1.0 } else { 0.0 };
                if a_binary != b_binary { 1.0 } else { 0.0 }
            })
            .sum()
    }

    /// Element-wise absolute value
    pub fn abs(&self) -> Self {
        Self {
            data: self.data.iter().map(|x| x.abs()).collect()
        }
    }

    /// Element-wise minimum with another vector
    pub fn min(&self, other: &Self) -> Self {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        Self {
            data: self.data.iter().zip(&other.data).map(|(a, b)| a.min(*b)).collect()
        }
    }

    /// Element-wise maximum with another vector
    pub fn max(&self, other: &Self) -> Self {
        assert_eq!(self.dim(), other.dim(), "Dimension mismatch: {} vs {}", self.dim(), other.dim());
        Self {
            data: self.data.iter().zip(&other.data).map(|(a, b)| a.max(*b)).collect()
        }
    }

    /// Sum of all elements
    pub fn sum(&self) -> f32 {
        self.data.iter().sum()
    }

    /// Mean of all elements
    pub fn mean(&self) -> f32 {
        self.sum() / self.dim() as f32
    }

    /// Variance of elements
    pub fn variance(&self) -> f32 {
        let mean = self.mean();
        let sum_sq_diff: f32 = self.data.iter().map(|x| (x - mean).powi(2)).sum();
        sum_sq_diff / self.dim() as f32
    }

    /// Standard deviation of elements
    pub fn std_dev(&self) -> f32 {
        self.variance().sqrt()
    }

    /// Apply function to each element
    pub fn map<F>(&self, f: F) -> Self 
    where
        F: Fn(f32) -> f32,
    {
        Self {
            data: self.data.iter().map(|&x| f(x)).collect()
        }
    }

    /// Apply function to each element (in place)
    pub fn map_mut<F>(&mut self, f: F)
    where
        F: Fn(f32) -> f32,
    {
        for x in &mut self.data {
            *x = f(*x);
        }
    }

    /// Check if two vectors are approximately equal
    pub fn approx_eq(&self, other: &Self, tolerance: f32) -> bool {
        if self.dim() != other.dim() {
            return false;
        }
        
        self.data.iter()
            .zip(&other.data)
            .all(|(a, b)| (a - b).abs() < tolerance)
    }
}

// Operator overloads
impl Add for Vector {
    type Output = Self;
    fn add(self, rhs: Self) -> Self::Output {
        assert_eq!(self.dim(), rhs.dim(), "Dimension mismatch: {} vs {}", self.dim(), rhs.dim());
        Vector::new(
            self.data.iter().zip(rhs.data.iter())
                .map(|(a, b)| a + b)
                .collect()
        )
    }
}

impl Sub for Vector {
    type Output = Self;
    fn sub(self, rhs: Self) -> Self::Output {
        assert_eq!(self.dim(), rhs.dim(), "Dimension mismatch: {} vs {}", self.dim(), rhs.dim());
        Vector::new(
            self.data.iter().zip(rhs.data.iter())
                .map(|(a, b)| a - b)
                .collect()
        )
    }
}

impl Mul<f32> for Vector {
    type Output = Self;
    fn mul(self, scalar: f32) -> Self::Output {
        Vector::new(
            self.data.iter().map(|x| x * scalar).collect()
        )
    }
}

impl Div<f32> for Vector {
    type Output = Self;
    fn div(self, scalar: f32) -> Self::Output {
        assert_ne!(scalar, 0.0, "Division by zero");
        Vector::new(
            self.data.iter().map(|x| x / scalar).collect()
        )
    }
}

// Support for scalar on left side
impl Mul<Vector> for f32 {
    type Output = Vector;
    fn mul(self, vector: Vector) -> Self::Output {
        vector * self
    }
}

/// Distance metric enumeration for flexible distance calculations
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum DistanceMetric {
    Euclidean,
    Manhattan,
    Chebyshev,
    Cosine,
    Angular,
    Jaccard,
    Hamming,
}

impl DistanceMetric {
    /// Calculate distance between two vectors using this metric
    pub fn distance(&self, a: &Vector, b: &Vector) -> f32 {
        match self {
            DistanceMetric::Euclidean => a.euclidean_distance(b),
            DistanceMetric::Manhattan => a.manhattan_distance(b),
            DistanceMetric::Chebyshev => a.chebyshev_distance(b),
            DistanceMetric::Cosine => a.cosine_distance(b),
            DistanceMetric::Angular => a.angular_distance(b),
            DistanceMetric::Jaccard => 1.0 - a.jaccard_similarity(b),
            DistanceMetric::Hamming => a.hamming_distance(b),
        }
    }

    /// Calculate similarity between two vectors using this metric
    pub fn similarity(&self, a: &Vector, b: &Vector) -> f32 {
        match self {
            DistanceMetric::Euclidean => 1.0 / (1.0 + a.euclidean_distance(b)),
            DistanceMetric::Manhattan => 1.0 / (1.0 + a.manhattan_distance(b)),
            DistanceMetric::Chebyshev => 1.0 / (1.0 + a.chebyshev_distance(b)),
            DistanceMetric::Cosine => a.cosine_similarity(b),
            DistanceMetric::Angular => 1.0 - a.angular_distance(b),
            DistanceMetric::Jaccard => a.jaccard_similarity(b),
            DistanceMetric::Hamming => 1.0 - (a.hamming_distance(b) / a.dim() as f32),
        }
    }
}

/// Utility functions for vector operations
pub mod utils {
    use super::Vector;

    /// Calculate centroid of a collection of vectors
    pub fn centroid(vectors: &[Vector]) -> Option<Vector> {
        if vectors.is_empty() {
            return None;
        }
        
        let dim = vectors[0].dim();
        let mut sum = Vector::zeros(dim);
        
        for v in vectors {
            assert_eq!(v.dim(), dim, "All vectors must have the same dimension");
            sum = sum + v.clone();
        }
        
        Some(sum / vectors.len() as f32)
    }

    /// Calculate pairwise distances between all vectors
    pub fn pairwise_distances(vectors: &[Vector], metric: super::DistanceMetric) -> Vec<Vec<f32>> {
        let n = vectors.len();
        let mut distances = vec![vec![0.0; n]; n];
        
        for i in 0..n {
            for j in i+1..n {
                let dist = metric.distance(&vectors[i], &vectors[j]);
                distances[i][j] = dist;
                distances[j][i] = dist;
            }
        }
        
        distances
    }

    /// Find k nearest neighbors to a query vector
    pub fn k_nearest_neighbors(
        query: &Vector, 
        vectors: &[Vector], 
        k: usize,
        metric: super::DistanceMetric,
    ) -> Vec<(usize, f32)> {
        let mut distances: Vec<(usize, f32)> = vectors.iter()
            .enumerate()
            .map(|(i, v)| (i, metric.distance(query, v)))
            .collect();
        
        distances.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        distances.into_iter().take(k).collect()
    }

    /// Linear interpolation between two vectors
    pub fn lerp(a: &Vector, b: &Vector, t: f32) -> Vector {
        assert_eq!(a.dim(), b.dim(), "Dimension mismatch");
        let t = t.clamp(0.0, 1.0);
        a.clone() * (1.0 - t) + b.clone() * t
    }

    /// Spherical linear interpolation (for unit vectors)
    pub fn slerp(a: &Vector, b: &Vector, t: f32) -> Vector {
        assert_eq!(a.dim(), b.dim(), "Dimension mismatch");
        let t = t.clamp(0.0, 1.0);
        
        let dot = a.dot(b);
        let theta = dot.acos();
        
        if theta.abs() < 1e-6 {
            // Vectors are nearly parallel, use linear interpolation
            return lerp(a, b, t);
        }
        
        let sin_theta = theta.sin();
        let factor_a = ((1.0 - t) * theta).sin() / sin_theta;
        let factor_b = (t * theta).sin() / sin_theta;
        
        a.clone() * factor_a + b.clone() * factor_b
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::utils::*;

    #[test]
    fn test_basic_operations() {
        let v1 = Vector::new(vec![1.0, 2.0, 3.0]);
        let v2 = Vector::new(vec![4.0, 5.0, 6.0]);
        
        assert_eq!(v1.dot(&v2), 32.0);
        assert!((v1.norm() - (14.0_f32).sqrt()).abs() < 1e-6);
        assert_eq!(v1.dim(), 3);
    }

    #[test]
    fn test_distance_metrics() {
        let v1 = Vector::new(vec![0.0, 0.0]);
        let v2 = Vector::new(vec![3.0, 4.0]);
        
        assert!((v1.euclidean_distance(&v2) - 5.0).abs() < 1e-6);
        assert_eq!(v1.manhattan_distance(&v2), 7.0);
        assert_eq!(v1.chebyshev_distance(&v2), 4.0);
    }

    #[test]
    fn test_normalization() {
        let mut v = Vector::new(vec![3.0, 4.0]);
        assert!(!v.is_normalized(1e-6));
        
        v.normalize_mut();
        assert!(v.is_normalized(1e-6));
        assert!((v.norm() - 1.0).abs() < 1e-6);
    }

    #[test]
    fn test_construction() {
        let zeros = Vector::zeros(5);
        assert_eq!(zeros.dim(), 5);
        assert_eq!(zeros.sum(), 0.0);
        
        let ones = Vector::ones(3);
        assert_eq!(ones.dim(), 3);
        assert_eq!(ones.sum(), 3.0);
    }

    #[test]
    fn test_statistics() {
        let v = Vector::new(vec![1.0, 2.0, 3.0, 4.0, 5.0]);
        assert_eq!(v.sum(), 15.0);
        assert_eq!(v.mean(), 3.0);
        assert!((v.variance() - 2.0).abs() < 1e-6);
    }

    #[test]
    fn test_operators() {
        let v1 = Vector::new(vec![1.0, 2.0]);
        let v2 = Vector::new(vec![3.0, 4.0]);
        
        let sum = v1.clone() + v2.clone();
        assert_eq!(sum.raw(), vec![4.0, 6.0]);
        
        let diff = v2.clone() - v1.clone();
        assert_eq!(diff.raw(), vec![2.0, 2.0]);
        
        let scaled = v1.clone() * 2.0;
        assert_eq!(scaled.raw(), vec![2.0, 4.0]);
        
        let scaled2 = 3.0 * v1.clone();
        assert_eq!(scaled2.raw(), vec![3.0, 6.0]);
    }

    #[test]
    fn test_cosine_similarity() {
        let v1 = Vector::new(vec![1.0, 0.0]);
        let v2 = Vector::new(vec![0.0, 1.0]);
        assert!((v1.cosine_similarity(&v2)).abs() < 1e-6);

        let v3 = Vector::new(vec![1.0, 1.0]);
        let sim = v3.cosine_similarity(&v3);
        assert!((sim - 1.0).abs() < 1e-6);
    }

    #[test]
    fn test_distance_metric_enum() {
        let v1 = Vector::new(vec![1.0, 0.0]);
        let v2 = Vector::new(vec![0.0, 1.0]);
        
        let euclidean_dist = DistanceMetric::Euclidean.distance(&v1, &v2);
        assert!((euclidean_dist - 2.0_f32.sqrt()).abs() < 1e-6);
        
        let cosine_sim = DistanceMetric::Cosine.similarity(&v1, &v2);
        assert!(cosine_sim.abs() < 1e-6);
    }

    #[test]
    fn test_utils() {
        let vectors = vec![
            Vector::new(vec![1.0, 1.0]),
            Vector::new(vec![2.0, 2.0]),
            Vector::new(vec![3.0, 3.0]),
        ];
        
        let center = centroid(&vectors).unwrap();
        assert_eq!(center.raw(), vec![2.0, 2.0]);
        
        let query = Vector::new(vec![1.5, 1.5]);
        let neighbors = k_nearest_neighbors(&query, &vectors, 2, DistanceMetric::Euclidean);
        assert_eq!(neighbors.len(), 2);
        assert_eq!(neighbors[0].0, 0); // Closest should be first vector
    }

    #[test]
    fn test_finite_check() {
        let v1 = Vector::new(vec![1.0, 2.0, 3.0]);
        assert!(v1.is_finite());
        
        let v2 = Vector::new(vec![1.0, f32::INFINITY, 3.0]);
        assert!(!v2.is_finite());
        
        let v3 = Vector::new(vec![1.0, f32::NAN, 3.0]);
        assert!(!v3.is_finite());
    }

    #[test]
    fn test_approximate_equality() {
        let v1 = Vector::new(vec![1.0, 2.0, 3.0]);
        let v2 = Vector::new(vec![1.001, 2.001, 3.001]);
        
        assert!(!v1.approx_eq(&v2, 1e-6));
        assert!(v1.approx_eq(&v2, 1e-2));
    }
}