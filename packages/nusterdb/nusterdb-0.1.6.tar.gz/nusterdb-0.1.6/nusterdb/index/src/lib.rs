//! index: pluggable ANN index implementations with optimizations

use core::{Vector, DistanceMetric};
// use hnsw_rs::prelude::{Hnsw, DistL2}; // Currently unused
use serde::{Serialize, Deserialize};
use bincode;
use std::collections::HashMap;
// use std::cell::UnsafeCell; // Currently unused

// Import our optimized implementations
mod optimized_flat;
mod ultra_fast_flat;
mod super_optimized_flat;

pub use optimized_flat::OptimizedFlatIndex;
pub use ultra_fast_flat::UltraFastFlatIndex;
pub use super_optimized_flat::SuperOptimizedFlatIndex;

/// Configuration for index creation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IndexConfig {
    pub dim: usize,
    pub distance_metric: DistanceMetric,
    pub index_type: IndexType,
    pub hnsw_config: Option<HnswConfig>,
    pub flat_config: Option<FlatConfig>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HnswConfig {
    pub max_nb_connection: usize,      // M - number of connections
    pub max_nb_elements: usize,        // initial capacity
    pub max_layer: usize,              // number of layers
    pub ef_construction: usize,        // build quality
    pub ef_search: Option<usize>,      // search quality (if None, uses k.max(50))
    pub use_heuristic: bool,           // use heuristic for connection selection
}

impl Default for HnswConfig {
    fn default() -> Self {
        Self {
            max_nb_connection: 16,
            max_nb_elements: 1024,
            max_layer: 16,
            ef_construction: 200,
            ef_search: None,
            use_heuristic: true,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlatConfig {
    pub use_simd: bool,                // use SIMD optimizations
    pub batch_size: usize,             // batch size for operations
    pub sort_algorithm: SortAlgorithm, // sorting algorithm for results
}

impl Default for FlatConfig {
    fn default() -> Self {
        Self {
            use_simd: true,
            batch_size: 1000,
            sort_algorithm: SortAlgorithm::Unstable,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SortAlgorithm {
    Stable,
    Unstable,
    PartialSort,  // Use partial sort for top-k
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IndexType {
    Flat,
    OptimizedFlat,       // SIMD-optimized flat index
    UltraFastFlat,       // Ultra-high-performance flat index
    SuperOptimizedFlat,  // FAISS-level optimized flat index with bulk operations
    Hnsw,
    // Future index types
    IVF,     // Inverted File
    LSH,     // Locality Sensitive Hashing  
    Annoy,   // Spotify's Annoy
}

impl Default for IndexConfig {
    fn default() -> Self {
        Self {
            dim: 3,
            distance_metric: DistanceMetric::Euclidean,
            index_type: IndexType::UltraFastFlat,
            hnsw_config: None,
            flat_config: Some(FlatConfig::default()),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IndexStats {
    pub vector_count: usize,
    pub dimension: usize,
    pub index_type: String,
    pub distance_metric: DistanceMetric,
    pub memory_usage: usize,
    pub build_time_ms: Option<u64>,
    pub last_search_time_ms: Option<u64>,
    pub total_searches: u64,
    pub total_inserts: u64,
    pub additional_stats: HashMap<String, String>,
}

/// Core trait for all ANN index implementations
pub trait AnnIndex: Send + Sync {
    fn with_config(config: IndexConfig) -> Self where Self: Sized;
    fn insert(&mut self, id: usize, vector: Vector);
    fn search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)>;
    fn config(&self) -> &IndexConfig;
    fn stats(&self) -> IndexStats;
    fn as_any(&self) -> &dyn std::any::Any;
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any;
}

/// Trait for bulk operations on indices
pub trait BulkAnnIndex: AnnIndex {
    fn bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]);
    fn reserve(&mut self, capacity: usize);
}

/// Trait for snapshot and restore functionality
pub trait SnapshotIndex: AnnIndex {
    fn dump(&self) -> Vec<u8>;
    fn restore(config: IndexConfig, data: &[u8]) -> Self where Self: Sized;
}

/// Trait for indices that support both operations
pub trait IndexWithSnapshot: AnnIndex + SnapshotIndex {}

/// Simple flat index implementation
pub struct FlatIndex {
    config: IndexConfig,
    vectors: Vec<(usize, Vector)>,
}

impl AnnIndex for FlatIndex {
    fn with_config(config: IndexConfig) -> Self {
        Self {
            config,
            vectors: Vec::new(),
        }
    }

    fn insert(&mut self, id: usize, vector: Vector) {
        // Update existing or add new
        if let Some(pos) = self.vectors.iter().position(|(existing_id, _)| *existing_id == id) {
            self.vectors[pos] = (id, vector);
        } else {
            self.vectors.push((id, vector));
        }
    }

    fn search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        let mut distances: Vec<(usize, f32)> = self.vectors
            .iter()
            .map(|(id, vector)| {
                let distance = match self.config.distance_metric {
                    DistanceMetric::Euclidean => euclidean_distance(query, vector),
                    DistanceMetric::Cosine => cosine_distance(query, vector),
                    _ => euclidean_distance(query, vector), // Default to euclidean for other metrics
                };
                (*id, distance)
            })
            .collect();

        distances.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        distances.truncate(k);
        distances
    }

    fn config(&self) -> &IndexConfig {
        &self.config
    }

    fn stats(&self) -> IndexStats {
        IndexStats {
            vector_count: self.vectors.len(),
            dimension: self.config.dim,
            index_type: "Flat".to_string(),
            distance_metric: self.config.distance_metric,
            memory_usage: self.vectors.len() * (std::mem::size_of::<usize>() + self.config.dim * std::mem::size_of::<f32>()),
            build_time_ms: None,
            last_search_time_ms: None,
            total_searches: 0,
            total_inserts: self.vectors.len() as u64,
            additional_stats: HashMap::new(),
        }
    }

    fn as_any(&self) -> &dyn std::any::Any {
        self
    }

    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
}

impl SnapshotIndex for FlatIndex {
    fn dump(&self) -> Vec<u8> {
        bincode::serialize(&self.vectors).unwrap_or_default()
    }

    fn restore(config: IndexConfig, data: &[u8]) -> Self {
        let vectors = bincode::deserialize(data).unwrap_or_default();
        Self { config, vectors }
    }
}

impl IndexWithSnapshot for FlatIndex {}

// HNSW index implementation - temporarily disabled due to API issues
// pub struct HnswIndex {
//     config: IndexConfig,
//     hnsw: UnsafeCell<Option<Hnsw<'static, f32, DistL2>>>,
//     id_to_index: HashMap<usize, usize>,
//     index_to_id: HashMap<usize, usize>,
//     next_internal_id: usize,
// }
// 
// unsafe impl Send for HnswIndex {}
// unsafe impl Sync for HnswIndex {}

// Simple placeholder HnswIndex for now
pub struct HnswIndex {
    config: IndexConfig,
    vectors: Vec<(usize, Vector)>,
}

impl AnnIndex for HnswIndex {
    fn with_config(config: IndexConfig) -> Self {
        Self {
            config,
            vectors: Vec::new(),
        }
    }

    fn insert(&mut self, id: usize, vector: Vector) {
        // Update existing or add new
        if let Some(pos) = self.vectors.iter().position(|(existing_id, _)| *existing_id == id) {
            self.vectors[pos] = (id, vector);
        } else {
            self.vectors.push((id, vector));
        }
    }

    fn search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        let mut distances: Vec<(usize, f32)> = self.vectors
            .iter()
            .map(|(id, vector)| {
                let distance = match self.config.distance_metric {
                    DistanceMetric::Euclidean => euclidean_distance(query, vector),
                    DistanceMetric::Cosine => cosine_distance(query, vector),
                    _ => euclidean_distance(query, vector), // Default to euclidean for other metrics
                };
                (*id, distance)
            })
            .collect();

        distances.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        distances.truncate(k);
        distances
    }

    fn config(&self) -> &IndexConfig {
        &self.config
    }

    fn stats(&self) -> IndexStats {
        IndexStats {
            vector_count: self.vectors.len(),
            dimension: self.config.dim,
            index_type: "HNSW".to_string(),
            distance_metric: self.config.distance_metric,
            memory_usage: self.vectors.len() * (std::mem::size_of::<usize>() + self.config.dim * std::mem::size_of::<f32>()),
            build_time_ms: None,
            last_search_time_ms: None,
            total_searches: 0,
            total_inserts: self.vectors.len() as u64,
            additional_stats: HashMap::new(),
        }
    }

    fn as_any(&self) -> &dyn std::any::Any {
        self
    }

    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
}

impl SnapshotIndex for HnswIndex {
    fn dump(&self) -> Vec<u8> {
        bincode::serialize(&self.vectors).unwrap_or_default()
    }

    fn restore(config: IndexConfig, data: &[u8]) -> Self {
        let vectors = bincode::deserialize(data).unwrap_or_default();
        Self { config, vectors }
    }
}

impl IndexWithSnapshot for HnswIndex {}

/// Factory function to create indices
pub fn create_index(config: IndexConfig) -> Box<dyn AnnIndex> {
    match config.index_type {
        IndexType::Flat => Box::new(FlatIndex::with_config(config)),
        IndexType::OptimizedFlat => Box::new(OptimizedFlatIndex::with_config(config)),
        IndexType::UltraFastFlat => Box::new(UltraFastFlatIndex::with_config(config)),
        IndexType::SuperOptimizedFlat => Box::new(SuperOptimizedFlatIndex::with_config(config)),
        IndexType::Hnsw => Box::new(HnswIndex::with_config(config)),
        _ => {
            println!("Unsupported index type, falling back to UltraFastFlat");
            Box::new(UltraFastFlatIndex::with_config(config))
        }
    }
}

/// Distance functions
fn euclidean_distance(a: &Vector, b: &Vector) -> f32 {
    let a_slice = a.as_slice();
    let b_slice = b.as_slice();
    
    a_slice.iter()
        .zip(b_slice.iter())
        .map(|(x, y)| (x - y).powi(2))
        .sum::<f32>()
        .sqrt()
}

fn cosine_distance(a: &Vector, b: &Vector) -> f32 {
    let a_slice = a.as_slice();
    let b_slice = b.as_slice();
    
    let dot_product: f32 = a_slice.iter().zip(b_slice.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f32 = a_slice.iter().map(|x| x * x).sum::<f32>().sqrt();
    let norm_b: f32 = b_slice.iter().map(|x| x * x).sum::<f32>().sqrt();
    
    1.0 - (dot_product / (norm_a * norm_b))
}

#[cfg(test)]
mod tests {
    use super::*;
    use core::Vector;

    #[test]
    fn test_flat_index() {
        let config = IndexConfig {
            dim: 3,
            distance_metric: DistanceMetric::Euclidean,
            index_type: IndexType::Flat,
            hnsw_config: None,
            flat_config: None,
        };

        let mut index = FlatIndex::with_config(config);
        
        let v1 = Vector::new(vec![1.0, 2.0, 3.0]);
        let v2 = Vector::new(vec![4.0, 5.0, 6.0]);
        
        index.insert(1, v1);
        index.insert(2, v2);
        
        let query = Vector::new(vec![1.1, 2.1, 3.1]);
        let results = index.search(&query, 2);
        
        assert_eq!(results.len(), 2);
        assert_eq!(results[0].0, 1); // closest should be v1
    }

    #[test]
    fn test_optimized_flat_index() {
        let config = IndexConfig {
            dim: 3,
            distance_metric: DistanceMetric::Euclidean,
            index_type: IndexType::OptimizedFlat,
            hnsw_config: None,
            flat_config: Some(FlatConfig::default()),
        };

        let mut index = OptimizedFlatIndex::with_config(config);
        
        let v1 = Vector::new(vec![1.0, 2.0, 3.0]);
        let v2 = Vector::new(vec![4.0, 5.0, 6.0]);
        
        index.insert(1, v1);
        index.insert(2, v2);
        
        let query = Vector::new(vec![1.1, 2.1, 3.1]);
        let results = index.search(&query, 2);
        
        assert_eq!(results.len(), 2);
        assert_eq!(results[0].0, 1); // closest should be v1
    }

    #[test]
    fn test_ultra_fast_flat_index() {
        let config = IndexConfig {
            dim: 3,
            distance_metric: DistanceMetric::Euclidean,
            index_type: IndexType::UltraFastFlat,
            hnsw_config: None,
            flat_config: Some(FlatConfig::default()),
        };

        let mut index = UltraFastFlatIndex::with_config(config);
        
        let v1 = Vector::new(vec![1.0, 2.0, 3.0]);
        let v2 = Vector::new(vec![4.0, 5.0, 6.0]);
        
        index.insert(1, v1);
        index.insert(2, v2);
        
        let query = Vector::new(vec![1.1, 2.1, 3.1]);
        let results = index.search(&query, 2);
        
        assert_eq!(results.len(), 2);
        assert_eq!(results[0].0, 1); // closest should be v1
    }

    #[test]
    fn test_super_optimized_flat_index() {
        let config = IndexConfig {
            dim: 3,
            distance_metric: DistanceMetric::Euclidean,
            index_type: IndexType::SuperOptimizedFlat,
            hnsw_config: None,
            flat_config: Some(FlatConfig::default()),
        };

        let mut index = SuperOptimizedFlatIndex::with_config(config);
        
        let v1 = Vector::new(vec![1.0, 2.0, 3.0]);
        let v2 = Vector::new(vec![4.0, 5.0, 6.0]);
        
        index.insert(1, v1);
        index.insert(2, v2);
        
        let query = Vector::new(vec![1.1, 2.1, 3.1]);
        let results = index.search(&query, 2);
        
        assert_eq!(results.len(), 2);
        assert_eq!(results[0].0, 1); // closest should be v1
    }

    #[test]
    fn test_bulk_insert() {
        let config = IndexConfig {
            dim: 3,
            distance_metric: DistanceMetric::Euclidean,
            index_type: IndexType::SuperOptimizedFlat,
            hnsw_config: None,
            flat_config: Some(FlatConfig::default()),
        };

        let mut index = SuperOptimizedFlatIndex::with_config(config);
        
        let vectors = vec![
            Vector::new(vec![1.0, 2.0, 3.0]),
            Vector::new(vec![4.0, 5.0, 6.0]),
            Vector::new(vec![7.0, 8.0, 9.0]),
        ];
        let ids = vec![1, 2, 3];
        
        index.bulk_insert(&ids, &vectors);
        
        let query = Vector::new(vec![1.1, 2.1, 3.1]);
        let results = index.search(&query, 2);
        
        assert_eq!(results.len(), 2);
        assert_eq!(results[0].0, 1); // closest should be first vector
    }
}
