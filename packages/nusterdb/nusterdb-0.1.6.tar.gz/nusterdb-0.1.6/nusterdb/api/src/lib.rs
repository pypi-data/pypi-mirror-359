//! api: simple service layer integrating storage + index

pub mod server;
pub use server::serve;

use anyhow::{Context, Result};
use core as core_crate;
use core_crate::Vector;
use index::{
    AnnIndex, BulkAnnIndex, SnapshotIndex, 
    FlatIndex, HnswIndex, OptimizedFlatIndex, UltraFastFlatIndex, SuperOptimizedFlatIndex,
    IndexConfig, IndexType, HnswConfig, create_index, IndexWithSnapshot
};
use storage::{Storage, Meta, StorageConfig};
use std::collections::HashMap;

// Helper functions for bulk operations
fn try_bulk_insert(index: &mut Box<dyn IndexWithSnapshot>, ids: &[usize], vectors: &[Vector]) -> bool {
    // Try to downcast to different bulk-capable index types
    if let Some(super_index) = index.as_any_mut().downcast_mut::<SuperOptimizedFlatIndex>() {
        super_index.bulk_insert(ids, vectors);
        true
    } else {
        false
    }
}

/// Configuration for the service
#[derive(Debug, Clone)]
pub struct ServiceConfig {
    pub dim: usize,
    pub use_hnsw: bool,
    pub hnsw_m: usize,            // HNSW max connections
    pub hnsw_ef_construction: usize, // HNSW build quality
    pub auto_snapshot: bool,       // Enable auto-snapshots
    pub snapshot_interval_secs: u64, // Auto-snapshot interval
}

impl Default for ServiceConfig {
    fn default() -> Self {
        Self {
            dim: 3,
            use_hnsw: false,
            hnsw_m: 16,
            hnsw_ef_construction: 200,
            auto_snapshot: false,
            snapshot_interval_secs: 3600, // 1 hour
        }
    }
}

/// Service holds both persistence and in-memory index.
pub struct Service {
    pub storage: Storage,
    pub index: Box<dyn IndexWithSnapshot>,
    /// Keep metadata for each id in memory
    pub metadata: HashMap<usize, Meta>,
    /// Service configuration
    pub config: ServiceConfig,
    /// Index type for metrics
    pub index_type: String,
}

impl Service {
    /// Create a new service with default configuration
    pub fn new(path: &str, dim: usize, use_hnsw: bool) -> Result<Self> {
        let mut config = ServiceConfig::default();
        config.dim = dim;
        config.use_hnsw = use_hnsw;
        Self::with_config(path, config)
    }

    /// Create a new service with enhanced configuration
    pub fn new_with_configs(path: &str, index_config: IndexConfig, storage_config: StorageConfig) -> Result<Self> {
        let storage = Storage::with_config(path, storage_config)
            .context("opening RocksDB storage")?;

        let index_type = match index_config.index_type {
            IndexType::Hnsw => "HNSW".to_string(),
            IndexType::Flat => "Flat".to_string(),
            IndexType::OptimizedFlat => "OptimizedFlat".to_string(),
            IndexType::UltraFastFlat => "UltraFastFlat".to_string(),
            IndexType::SuperOptimizedFlat => "SuperOptimizedFlat".to_string(),
            _ => "Other".to_string(),
        };

        // Try loading an existing snapshot first
        let index: Box<dyn IndexWithSnapshot> = 
            if let Ok(bytes) = storage.load_snapshot("default") {
                println!("Loading index from snapshot...");
                // restore from snapshot
                match index_config.index_type {
                    IndexType::Hnsw => Box::new(HnswIndex::restore(index_config.clone(), &bytes)),
                    IndexType::Flat => Box::new(FlatIndex::restore(index_config.clone(), &bytes)),
                    IndexType::OptimizedFlat => Box::new(OptimizedFlatIndex::restore(index_config.clone(), &bytes)),
                    IndexType::UltraFastFlat => Box::new(UltraFastFlatIndex::restore(index_config.clone(), &bytes)),
                    IndexType::SuperOptimizedFlat => Box::new(SuperOptimizedFlatIndex::restore(index_config.clone(), &bytes)),
                    _ => {
                        println!("Unsupported index type, falling back to SuperOptimizedFlat");
                        Box::new(SuperOptimizedFlatIndex::restore(index_config.clone(), &bytes))
                    }
                }
            } else {
                println!("No snapshot found, building index from scratch...");
                // no snapshot: build from scratch
                let mut idx: Box<dyn IndexWithSnapshot> = match index_config.index_type {
                    IndexType::Hnsw => Box::new(HnswIndex::with_config(index_config.clone())),
                    IndexType::Flat => Box::new(FlatIndex::with_config(index_config.clone())),
                    IndexType::OptimizedFlat => Box::new(OptimizedFlatIndex::with_config(index_config.clone())),
                    IndexType::UltraFastFlat => Box::new(UltraFastFlatIndex::with_config(index_config.clone())),
                    IndexType::SuperOptimizedFlat => Box::new(SuperOptimizedFlatIndex::with_config(index_config.clone())),
                    _ => {
                        println!("Unsupported index type, falling back to SuperOptimizedFlat");
                        Box::new(SuperOptimizedFlatIndex::with_config(index_config.clone()))
                    }
                };
                
                // warm-up loop
                for id in storage.list_ids().context("listing vector IDs")? {
                    let vec = storage.load_vector(id)
                        .with_context(|| format!("loading vector {}", id))?;
                    idx.insert(id, vec);
                }
                idx
            };

        let mut metadata = HashMap::new();

        // Always load metadata (not included in index snapshot)
        for id in storage.list_ids().context("listing vector IDs")? {
            let meta = storage.load_metadata(id)
                .with_context(|| format!("loading metadata {}", id))?;
            metadata.insert(id, meta);
        }

        let config = ServiceConfig {
            dim: index_config.dim,
            use_hnsw: matches!(index_config.index_type, IndexType::Hnsw),
            hnsw_m: index_config.hnsw_config.as_ref()
                .map(|c| c.max_nb_connection)
                .unwrap_or(16),
            hnsw_ef_construction: index_config.hnsw_config.as_ref()
                .map(|c| c.ef_construction)
                .unwrap_or(200),
            auto_snapshot: false,
            snapshot_interval_secs: 3600,
        };

        Ok(Service { storage, index, metadata, config, index_type })
    }

    /// Create a new service with custom configuration
    pub fn with_config(path: &str, config: ServiceConfig) -> Result<Self> {
        let storage = Storage::open(path)
            .context("opening RocksDB storage")?;

        let index_type = if config.use_hnsw { "HNSW".to_string() } else { "Flat".to_string() };

        // Create index configuration
        let index_config = IndexConfig {
            dim: config.dim,
            distance_metric: core_crate::DistanceMetric::Euclidean,
            index_type: if config.use_hnsw { IndexType::Hnsw } else { IndexType::Flat },
            hnsw_config: if config.use_hnsw {
                Some(HnswConfig {
                    max_nb_connection: config.hnsw_m,
                    ef_construction: config.hnsw_ef_construction,
                    max_nb_elements: 10000,
                    max_layer: 16,
                    ef_search: None,
                    use_heuristic: true,
                })
            } else {
                None
            },
            flat_config: None,
        };

        // Try loading an existing snapshot first
        let index: Box<dyn IndexWithSnapshot> = 
            if let Ok(bytes) = storage.load_snapshot("default") {
                println!("Loading index from snapshot...");
                // restore from snapshot
                if config.use_hnsw {
                    Box::new(HnswIndex::restore(index_config, &bytes))
                } else {
                    Box::new(FlatIndex::restore(index_config, &bytes))
                }
            } else {
                println!("No snapshot found, building index from scratch...");
                // no snapshot: build from scratch
                let mut idx: Box<dyn IndexWithSnapshot> = if config.use_hnsw {
                    Box::new(HnswIndex::with_config(index_config))
                } else {
                    Box::new(FlatIndex::with_config(index_config))
                };
                
                // warm-up loop
                for id in storage.list_ids().context("listing vector IDs")? {
                    let vec = storage.load_vector(id)
                        .with_context(|| format!("loading vector {}", id))?;
                    idx.insert(id, vec);
                }
                idx
            };

        let mut metadata = HashMap::new();

        // Always load metadata (not included in index snapshot)
        for id in storage.list_ids().context("listing vector IDs")? {
            let meta = storage.load_metadata(id)
                .with_context(|| format!("loading metadata {}", id))?;
            metadata.insert(id, meta);
        }

        Ok(Service { storage, index, metadata, config, index_type })
    }

    /// Get the expected vector dimension
    pub fn dimension(&self) -> usize {
        self.config.dim
    }

    /// Get the index type
    pub fn index_type(&self) -> &str {
        &self.index_type
    }

    /// Persist & index a new vector (plus metadata).
    pub fn add(&mut self, id: usize, vector: Vector, meta: Meta) -> Result<()> {
        // Validate dimension
        if vector.dim() != self.config.dim {
            return Err(anyhow::anyhow!(
                "Vector dimension mismatch: expected {}, got {}", 
                self.config.dim, vector.dim()
            ));
        }

        self.storage
            .save_vector(id, &vector)
            .with_context(|| format!("saving vector {}", id))?;
        self.index.insert(id, vector);
        
        self.storage
            .save_metadata(id, &meta)
            .with_context(|| format!("saving metadata {}", id))?;
        self.metadata.insert(id, meta);
        Ok(())
    }

    /// Bulk insert vectors - FAISS-style all-at-once insertion for maximum performance
    pub fn bulk_add(&mut self, ids: &[usize], vectors: &[Vector], metas: &[Meta]) -> Result<usize> {
        if ids.len() != vectors.len() || vectors.len() != metas.len() {
            return Err(anyhow::anyhow!("IDs, vectors, and metadata arrays must have the same length"));
        }

        let mut successful = 0;
        let mut errors = Vec::new();

        // Validate all vectors first
        for (idx, vector) in vectors.iter().enumerate() {
            if vector.dim() != self.config.dim {
                errors.push(format!(
                    "Index {}: Vector dimension mismatch: expected {}, got {}", 
                    idx, self.config.dim, vector.dim()
                ));
            }
        }

        if !errors.is_empty() {
            return Err(anyhow::anyhow!("Validation errors: {}", errors.join("; ")));
        }

        // Try bulk insertion if the index supports it
        if try_bulk_insert(&mut self.index, ids, vectors) {
            successful = vectors.len();
            println!("Bulk inserted {} vectors using optimized bulk method", successful);
        } else {
            // Fallback to individual insertions for other index types
            for ((&id, vector), meta) in ids.iter().zip(vectors.iter()).zip(metas.iter()) {
                match self.add(id, vector.clone(), meta.clone()) {
                    Ok(_) => successful += 1,
                    Err(e) => errors.push(format!("ID {}: {}", id, e)),
                }
            }
            println!("Inserted {} vectors using individual insertion method", successful);
        }

        // Bulk save to storage
        if successful > 0 {
            for ((&id, vector), meta) in ids.iter().zip(vectors.iter()).zip(metas.iter()).take(successful) {
                if let Err(e) = self.storage.save_vector(id, vector) {
                    eprintln!("Warning: Failed to save vector {}: {}", id, e);
                }
                if let Err(e) = self.storage.save_metadata(id, meta) {
                    eprintln!("Warning: Failed to save metadata {}: {}", id, e);
                }
                self.metadata.insert(id, meta.clone());
            }
        }

        if !errors.is_empty() {
            eprintln!("Bulk insertion warnings: {}", errors.join("; "));
        }

        Ok(successful)
    }

    /// Query top-k nearest neighbors, only among IDs whose metadata satisfy ALL `filter`.
    pub fn search(&self, query: &Vector, k: usize, filter: &HashMap<String, String>) -> Vec<(usize, f32)> {
        // Validate dimension
        if query.dim() != self.config.dim {
            eprintln!("Warning: Query dimension {} doesn't match expected {}", 
                     query.dim(), self.config.dim);
            return Vec::new();
        }

        if filter.is_empty() {
            // No filtering - use normal index search
            return self.index.search(query, k);
        }

        // 1. Pre-filter IDs by metadata
        let candidates: Vec<usize> = self.metadata.iter()
            .filter(|(_, meta)| {
                // Use the new Meta structure with proper field access
                filter.iter().all(|(k, v)| {
                    meta.get(k).map(|mv| mv == v).unwrap_or(false)
                })
            })
            .map(|(&id, _)| id)
            .collect();

        // 2. For each candidate, load vector and compute score
        let mut scores: Vec<(usize, f32)> = candidates.into_iter()
            .filter_map(|id| {
                // Load vector from storage
                self.storage.load_vector(id).ok().map(|v| (id, v))
            })
            .map(|(id, v)| (id, v.dot(query)))
            .collect();

        // 3. Sort & take top-k
        scores.sort_unstable_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        scores.into_iter().take(k).collect()
    }

    /// Write a snapshot named `default` to disk.
    pub fn snapshot(&self) -> Result<()> {
        let data = self.index.dump();
        self.storage.save_snapshot("default", &data)
            .context("saving snapshot to storage")?;
        println!("Snapshot created successfully");
        Ok(())
    }

    /// Write a named snapshot to disk.
    pub fn snapshot_named(&self, name: &str) -> Result<()> {
        let data = self.index.dump();
        self.storage.save_snapshot(name, &data)
            .context("saving named snapshot to storage")?;
        println!("Snapshot '{}' created successfully", name);
        Ok(())
    }

    /// Write a named snapshot to disk with metadata.
    pub fn snapshot_with_metadata(&self, name: &str, metadata: HashMap<String, String>) -> Result<()> {
        let data = self.index.dump();
        
        // Create snapshot info with metadata
        let info = storage::SnapshotInfo {
            name: name.to_string(),
            created_at: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
            size_bytes: data.len() as u64,
            vector_count: self.metadata.len(),
            index_type: self.index_type.clone(),
            compression: storage::CompressionType::LZ4,
            checksum: 0, // Will be calculated by storage
            metadata,
        };
        
        self.storage.save_snapshot_with_info(name, &data, info)
            .context("saving named snapshot with metadata to storage")?;
        println!("Snapshot '{}' created successfully with metadata", name);
        Ok(())
    }

    /// Clear the on-disk snapshot.
    pub fn clear_snapshot(&self) -> Result<()> {
        self.storage.delete_snapshot("default")
            .context("deleting snapshot from storage")?;
        Ok(())
    }

    /// Remove a vector by ID from both storage and index.
    pub fn remove(&mut self, id: usize) -> Result<()> {
        self.storage
            .delete_complete(id)
            .with_context(|| format!("deleting vector and metadata {}", id))?;
        self.metadata.remove(&id);
        // Note: Index remove might not be supported by all index types
        // let _ = self.index.remove(id); // Remove not supported in our current interface
        Ok(())
    }

    /// Get vector by ID from storage.
    pub fn get(&self, id: usize) -> Result<Vector> {
        self.storage
            .load_vector(id)
            .with_context(|| format!("loading vector {}", id))
    }

    /// Get metadata by ID.
    pub fn get_metadata(&self, id: usize) -> Option<&Meta> {
        self.metadata.get(&id)
    }

    /// List all vector IDs.
    pub fn list_ids(&self) -> Result<Vec<usize>> {
        self.storage
            .list_ids()
            .context("listing vector IDs")
    }

    /// Get service statistics
    pub fn stats(&self) -> Result<ServiceStats> {
        let ids = self.list_ids()?;
        Ok(ServiceStats {
            vector_count: ids.len(),
            dimension: self.config.dim,
            index_type: self.index_type.clone(),
            metadata_keys: self.get_metadata_keys(),
        })
    }

    /// Get all unique metadata keys
    fn get_metadata_keys(&self) -> Vec<String> {
        let mut keys = std::collections::HashSet::new();
        for meta in self.metadata.values() {
            // Use the new Meta structure properly
            for key in meta.keys() {
                keys.insert(key.clone());
            }
        }
        keys.into_iter().collect()
    }
}

#[derive(Debug, serde::Serialize)]
pub struct ServiceStats {
    pub vector_count: usize,
    pub dimension: usize,
    pub index_type: String,
    pub metadata_keys: Vec<String>,
}

// Convenience function for the server module
pub async fn serve_with_configs(path: String, index_config: IndexConfig, storage_config: StorageConfig, addr: std::net::SocketAddr) -> Result<()> {
    let service = Service::new_with_configs(&path, index_config, storage_config)
        .context("creating service")?;
    server::serve_with_service(service, addr).await
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core_crate::Vector;
    use std::fs;

    #[test]
    fn service_flat_flow() {
        let path = "_test_api_flat";
        let _ = fs::remove_dir_all(path);
        let mut svc = Service::new(path, 3, false).unwrap();

        let v = Vector::new(vec![1.0, 0.0, 0.0]);
        let meta = Meta::new();
        svc.add(5, v.clone(), meta).unwrap();
        let top = svc.search(&Vector::new(vec![1.0, 0.0, 0.0]), 1, &HashMap::new());
        assert_eq!(top[0].0, 5);

        let loaded = svc.storage.load_vector(5).unwrap();
        assert_eq!(loaded, v);
        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn service_dimension_validation() {
        let path = "_test_api_dim";
        let _ = fs::remove_dir_all(path);
        let mut svc = Service::new(path, 3, false).unwrap();

        // Try to add vector with wrong dimension
        let v = Vector::new(vec![1.0, 0.0]); // 2D instead of 3D
        let meta = Meta::new();
        let result = svc.add(1, v, meta);
        assert!(result.is_err());

        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn service_config() {
        let path = "_test_api_config";
        let _ = fs::remove_dir_all(path);
        
        let config = ServiceConfig {
            dim: 5,
            use_hnsw: true,
            hnsw_m: 32,
            hnsw_ef_construction: 400,
            auto_snapshot: true,
            snapshot_interval_secs: 1800,
        };
        
        let svc = Service::with_config(path, config.clone()).unwrap();
        assert_eq!(svc.dimension(), 5);
        assert_eq!(svc.index_type(), "HNSW");

        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn service_hnsw_flow() {
        let path = "_test_api_hnsw";
        let _ = fs::remove_dir_all(path);
        let mut svc = Service::new(path, 3, true).unwrap();

        let v = Vector::new(vec![0.0, 1.0, 0.0]);
        let meta = Meta::new();
        svc.add(9, v.clone(), meta).unwrap();
        let top = svc.search(&Vector::new(vec![0.0, 1.0, 0.0]), 1, &HashMap::new());
        assert_eq!(top[0].0, 9);

        let loaded = svc.storage.load_vector(9).unwrap();
        assert_eq!(loaded, v);
        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn service_snapshot_flow() {
        let path = "_test_api_snapshot";
        let _ = fs::remove_dir_all(path);
        
        // Create service and add data
        {
            let mut svc = Service::new(path, 3, false).unwrap();
            let v = Vector::new(vec![1.0, 2.0, 3.0]);
            let meta = Meta::new();
            svc.add(42, v, meta).unwrap();
            
            // Create snapshot
            svc.snapshot().unwrap();
        }
        
        // Reload service from snapshot
        {
            let svc = Service::new(path, 3, false).unwrap();
            let results = svc.search(&Vector::new(vec![1.0, 2.0, 3.0]), 1, &HashMap::new());
            assert_eq!(results[0].0, 42);
        }

        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn service_metadata_filtering() {
        let path = "_test_api_filter";
        let _ = fs::remove_dir_all(path);
        let mut svc = Service::new(path, 3, false).unwrap();

        // Add vectors with different metadata
        let v1 = Vector::new(vec![1.0, 0.0, 0.0]);
        let mut meta1 = Meta::new();
        meta1.set("lang".to_string(), "en".to_string());
        svc.add(1, v1, meta1).unwrap();

        let v2 = Vector::new(vec![1.0, 0.0, 0.0]);
        let mut meta2 = Meta::new();
        meta2.set("lang".to_string(), "es".to_string());
        svc.add(2, v2, meta2).unwrap();

        // Search with filter
        let mut filter = HashMap::new();
        filter.insert("lang".to_string(), "en".to_string());
        let results = svc.search(&Vector::new(vec![1.0, 0.0, 0.0]), 2, &filter);
        
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].0, 1);

        // Search without filter
        let results_all = svc.search(&Vector::new(vec![1.0, 0.0, 0.0]), 2, &HashMap::new());
        assert_eq!(results_all.len(), 2);

        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn service_basic_flow() {
        let path = "_test_api";
        let _ = fs::remove_dir_all(path);

        // Test with FlatIndex (use_hnsw = false)
        let mut svc = Service::new(path, 3, false).unwrap();

        let v = Vector::new(vec![2.0, 0.0, 0.0]);
        let meta = Meta::new();
        svc.add(7, v.clone(), meta).unwrap();
        let top = svc.search(&Vector::new(vec![2.0, 0.0, 0.0]), 1, &HashMap::new());
        assert_eq!(top[0].0, 7);

        let loaded = svc.storage.load_vector(7).unwrap();
        assert_eq!(loaded, v);

        let _ = fs::remove_dir_all(path);
    }
}