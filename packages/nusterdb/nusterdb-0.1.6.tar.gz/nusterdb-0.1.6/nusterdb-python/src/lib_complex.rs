use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::exceptions::{PyValueError, PyRuntimeError};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};
use core as nuster_core;
use nuster_core::{Vector as CoreVector, DistanceMetric as CoreDistanceMetric};
use index::{IndexConfig, IndexType as CoreIndexType, HnswConfig, FlatConfig, SortAlgorithm};
use storage::{StorageConfig, CompressionType, CompactionStyle, Meta};
use api::Service as CoreService;
use std::sync::{Arc, Mutex};

/// Python wrapper for Vector
#[pyclass]
#[derive(Clone)]
pub struct Vector {
    inner: CoreVector,
}

#[pymethods]
impl Vector {
    #[new]
    fn new(data: Vec<f32>) -> PyResult<Self> {
        if data.is_empty() {
            return Err(PyValueError::new_err("Vector must have at least one dimension"));
        }
        Ok(Vector {
            inner: CoreVector::new(data),
        })
    }

    #[staticmethod]
    fn zeros(dim: usize) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        Ok(Vector {
            inner: CoreVector::zeros(dim),
        })
    }

    #[staticmethod]
    fn ones(dim: usize) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        Ok(Vector {
            inner: CoreVector::ones(dim),
        })
    }

    #[staticmethod]
    fn random(dim: usize, min: f32, max: f32) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        if min > max {
            return Err(PyValueError::new_err("min must be <= max"));
        }
        Ok(Vector {
            inner: CoreVector::random(dim, min, max),
        })
    }

    #[staticmethod]
    fn unit_random(dim: usize) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        Ok(Vector {
            inner: CoreVector::unit_random(dim),
        })
    }

    /// Get the raw data as Python list
    fn to_list(&self) -> Vec<f32> {
        self.inner.raw()
    }

    /// Get vector dimension
    fn dim(&self) -> usize {
        self.inner.dim()
    }

    /// Get element at index
    fn get(&self, index: usize) -> PyResult<f32> {
        self.inner.get(index).ok_or_else(|| 
            PyValueError::new_err(format!("Index {} out of bounds", index))
        )
    }

    /// Set element at index
    fn set(&mut self, index: usize, value: f32) -> PyResult<()> {
        self.inner.set(index, value).map_err(|e| PyValueError::new_err(e))
    }

    /// Check if vector contains only finite values
    fn is_finite(&self) -> bool {
        self.inner.is_finite()
    }

    /// Check if vector is normalized (unit length)
    fn is_normalized(&self, tolerance: Option<f32>) -> bool {
        self.inner.is_normalized(tolerance.unwrap_or(1e-6))
    }

    /// Dot product with another vector
    fn dot(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Dimension mismatch"));
        }
        Ok(self.inner.dot(&other.inner))
    }

    /// Euclidean norm (L2 norm)
    fn norm(&self) -> f32 {
        self.inner.norm()
    }

    /// L1 norm (Manhattan norm)
    fn l1_norm(&self) -> f32 {
        self.inner.l1_norm()
    }

    /// L∞ norm (max norm)
    fn linf_norm(&self) -> f32 {
        self.inner.linf_norm()
    }

    /// Squared L2 norm
    fn norm_squared(&self) -> f32 {
        self.inner.norm_squared()
    }

    /// Normalize to unit length (returns new vector)
    fn normalize(&self) -> Self {
        Vector {
            inner: self.inner.normalize(),
        }
    }

    /// Normalize to unit length (modifies in place)
    fn normalize_mut(&mut self) {
        self.inner.normalize_mut();
    }

    /// Add two vectors
    fn __add__(&self, other: &Vector) -> PyResult<Vector> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Dimension mismatch"));
        }
        Ok(Vector {
            inner: self.inner.clone() + other.inner.clone(),
        })
    }

    /// Subtract vector
    fn __sub__(&self, other: &Vector) -> PyResult<Vector> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Dimension mismatch"));
        }
        Ok(Vector {
            inner: self.inner.clone() - other.inner.clone(),
        })
    }

    /// Multiply by scalar
    fn __mul__(&self, scalar: f32) -> Vector {
        Vector {
            inner: self.inner.clone() * scalar,
        }
    }

    /// Divide by scalar
    fn __truediv__(&self, scalar: f32) -> PyResult<Vector> {
        if scalar == 0.0 {
            return Err(PyValueError::new_err("Division by zero"));
        }
        Ok(Vector {
            inner: self.inner.clone() / scalar,
        })
    }

    /// String representation
    fn __repr__(&self) -> String {
        format!("Vector({})", 
            self.inner.as_slice().iter()
                .map(|x| format!("{:.3}", x))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }

    /// Sum of all elements
    fn sum(&self) -> f32 {
        self.inner.sum()
    }

    /// Mean of all elements
    fn mean(&self) -> f32 {
        self.inner.mean()
    }

    /// Variance of elements
    fn variance(&self) -> f32 {
        self.inner.variance()
    }

    /// Standard deviation of elements
    fn std_dev(&self) -> f32 {
        self.inner.std_dev()
    }
}

/// Distance metrics available
#[pyclass]
#[derive(Clone, Copy)]
pub enum DistanceMetric {
    Euclidean,
    Manhattan,
    Chebyshev,
    Cosine,
    Angular,
    Jaccard,
    Hamming,
}

impl From<DistanceMetric> for CoreDistanceMetric {
    fn from(metric: DistanceMetric) -> Self {
        match metric {
            DistanceMetric::Euclidean => CoreDistanceMetric::Euclidean,
            DistanceMetric::Manhattan => CoreDistanceMetric::Manhattan,
            DistanceMetric::Chebyshev => CoreDistanceMetric::Chebyshev,
            DistanceMetric::Cosine => CoreDistanceMetric::Cosine,
            DistanceMetric::Angular => CoreDistanceMetric::Angular,
            DistanceMetric::Jaccard => CoreDistanceMetric::Jaccard,
            DistanceMetric::Hamming => CoreDistanceMetric::Hamming,
        }
    }
}

/// Index types available
#[pyclass]
#[derive(Clone, Copy, Debug)]
pub enum PyIndexType {
    Flat,
    Hnsw,
    IVF,
    LSH,
    Annoy,
}

impl From<PyIndexType> for CoreIndexType {
    fn from(idx_type: PyIndexType) -> Self {
        match idx_type {
            PyIndexType::Flat => CoreIndexType::Flat,
            PyIndexType::Hnsw => CoreIndexType::Hnsw,
            PyIndexType::IVF => CoreIndexType::IVF,
            PyIndexType::LSH => CoreIndexType::LSH,
            PyIndexType::Annoy => CoreIndexType::Annoy,
        }
    }
}

/// Compression types for storage
#[pyclass]
#[derive(Clone, Copy)]
pub enum Compression {
    None,
    Snappy,
    LZ4,
    ZSTD,
}

impl From<Compression> for CompressionType {
    fn from(comp: Compression) -> Self {
        match comp {
            Compression::None => CompressionType::None,
            Compression::Snappy => CompressionType::Snappy,
            Compression::LZ4 => CompressionType::LZ4,
            Compression::ZSTD => CompressionType::ZSTD,
        }
    }
}

/// Main NusterDB class
#[pyclass]
pub struct NusterDB {
    service: Arc<Mutex<CoreService>>,
    config: DatabaseConfig,
}

/// Configuration for the database
#[pyclass]
#[derive(Clone)]
pub struct DatabaseConfig {
    pub dim: usize,
    pub index_type: PyIndexType,
    pub distance_metric: DistanceMetric,
    pub compression: Compression,
    pub cache_size_mb: u64,
    pub write_buffer_size_mb: u64,
    pub enable_bloom_filter: bool,
    pub enable_statistics: bool,
    pub max_background_jobs: i32,
    // HNSW specific
    pub hnsw_max_connections: usize,
    pub hnsw_ef_construction: usize,
    pub hnsw_ef_search: Option<usize>,
    pub hnsw_max_elements: usize,
    pub hnsw_max_layers: usize,
    // Flat specific
    pub flat_batch_size: usize,
    pub flat_use_simd: bool,
}

#[pymethods]
impl DatabaseConfig {
    #[new]
    #[pyo3(signature = (
        dim,
        index_type = PyIndexType::Flat,
        distance_metric = DistanceMetric::Euclidean,
        compression = Compression::LZ4,
        cache_size_mb = 256,
        write_buffer_size_mb = 64,
        enable_bloom_filter = true,
        enable_statistics = true,
        max_background_jobs = 4,
        hnsw_max_connections = 16,
        hnsw_ef_construction = 200,
        hnsw_ef_search = None,
        hnsw_max_elements = 10000,
        hnsw_max_layers = 16,
        flat_batch_size = 1000,
        flat_use_simd = true
    ))]
    fn new(
        dim: usize,
        index_type: PyIndexType,
        distance_metric: DistanceMetric,
        compression: Compression,
        cache_size_mb: u64,
        write_buffer_size_mb: u64,
        enable_bloom_filter: bool,
        enable_statistics: bool,
        max_background_jobs: i32,
        hnsw_max_connections: usize,
        hnsw_ef_construction: usize,
        hnsw_ef_search: Option<usize>,
        hnsw_max_elements: usize,
        hnsw_max_layers: usize,
        flat_batch_size: usize,
        flat_use_simd: bool,
    ) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        
        Ok(DatabaseConfig {
            dim,
            index_type,
            distance_metric,
            compression,
            cache_size_mb,
            write_buffer_size_mb,
            enable_bloom_filter,
            enable_statistics,
            max_background_jobs,
            hnsw_max_connections,
            hnsw_ef_construction,
            hnsw_ef_search,
            hnsw_max_elements,
            hnsw_max_layers,
            flat_batch_size,
            flat_use_simd,
        })
    }
}

#[pymethods]
impl NusterDB {
    #[new]
    fn new(path: String, config: DatabaseConfig) -> PyResult<Self> {
        // Convert config to internal types
        let index_config = IndexConfig {
            dim: config.dim,
            distance_metric: config.distance_metric.into(),
            index_type: config.index_type.into(),
            hnsw_config: Some(HnswConfig {
                max_nb_connection: config.hnsw_max_connections,
                max_nb_elements: config.hnsw_max_elements,
                max_layer: config.hnsw_max_layers,
                ef_construction: config.hnsw_ef_construction,
                ef_search: config.hnsw_ef_search,
                use_heuristic: true,
            }),
            flat_config: Some(FlatConfig {
                use_simd: config.flat_use_simd,
                batch_size: config.flat_batch_size,
                sort_algorithm: SortAlgorithm::Unstable,
            }),
        };

        let storage_config = StorageConfig {
            compression: config.compression.into(),
            cache_size_mb: config.cache_size_mb,
            write_buffer_size_mb: config.write_buffer_size_mb,
            max_write_buffer_number: 3,
            enable_statistics: config.enable_statistics,
            enable_bloom_filter: config.enable_bloom_filter,
            bloom_filter_bits_per_key: 10,
            compaction_style: CompactionStyle::Level,
            max_background_jobs: config.max_background_jobs,
        };

        let service = CoreService::new_with_configs(&path, index_config, storage_config)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create service: {}", e)))?;

        Ok(NusterDB {
            service: Arc::new(Mutex::new(service)),
            config,
        })
    }

    /// Insert a vector with optional metadata
    fn insert(&self, vector: &Vector, metadata: Option<&PyDict>) -> PyResult<usize> {
        let mut service = self.service.lock().unwrap();
        
        let meta = if let Some(meta_dict) = metadata {
            let mut meta_map = HashMap::new();
            for (key, value) in meta_dict {
                let key_str = key.extract::<String>()?;
                let value_str = value.extract::<String>()?;
                meta_map.insert(key_str, value_str);
            }
            let now = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            storage::Meta { 
                data: meta_map,
                created_at: now,
                updated_at: now,
                version: 1,
                tags: Vec::new(),
            }
        } else {
            let now = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            storage::Meta { 
                data: HashMap::new(),
                created_at: now,
                updated_at: now,
                version: 1,
                tags: Vec::new(),
            }
        };

        // We need an ID for insertion - let's generate one or use the current count
        let next_id = service.list_ids()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to get next ID: {}", e)))?
            .len();
        
        service.add(next_id, vector.inner.clone(), meta)
            .map_err(|e| PyRuntimeError::new_err(format!("Insert failed: {}", e)))?;
        
        Ok(next_id)
    }

    /// Search for k nearest neighbors
    fn search(&self, query: &Vector, k: usize, _ef_search: Option<usize>) -> PyResult<Vec<(usize, f32)>> {
        let service = self.service.lock().unwrap();
        
        // Service.search expects a filter HashMap, use empty filter for now
        let filter = HashMap::new();
        let results = service.search(&query.inner, k, &filter);
        Ok(results)
    }

    /// Get vector by ID
    fn get(&self, id: usize) -> PyResult<Option<Vector>> {
        let service = self.service.lock().unwrap();
        
        match service.get(id) {
            Ok(vector) => Ok(Some(Vector { inner: vector })),
            Err(_) => Ok(None), // Return None if not found
        }
    }

    /// Get metadata by ID
    fn get_metadata(&self, id: usize) -> PyResult<Option<PyObject>> {
        let service = self.service.lock().unwrap();
        
        match service.get_metadata(id) {
            Some(meta) => {
                Python::with_gil(|py| {
                    let dict = PyDict::new(py);
                    for (key, value) in &meta.data {
                        dict.set_item(key, value)?;
                    }
                    Ok(Some(dict.into()))
                })
            }
            None => Ok(None),
        }
    }

    /// Delete vector by ID
    fn delete(&self, id: usize) -> PyResult<bool> {
        let mut service = self.service.lock().unwrap();
        
        service.remove(id)
            .map_err(|e| PyRuntimeError::new_err(format!("Delete failed: {}", e)))?;
        Ok(true)
    }

    /// Update metadata (remove the old vector and add it back with new metadata)
    fn update_metadata(&self, id: usize, metadata: &PyDict) -> PyResult<bool> {
        let mut service = self.service.lock().unwrap();
        
        // Get the existing vector first
        let vector = service.get(id)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to get vector for update: {}", e)))?;
        
        // Remove the old entry
        service.remove(id)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to remove old vector: {}", e)))?;
        
        // Create new metadata
        let mut meta_map = HashMap::new();
        for (key, value) in metadata {
            let key_str = key.extract::<String>()?;
            let value_str = value.extract::<String>()?;
            meta_map.insert(key_str, value_str);
        }
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        let meta = storage::Meta { 
            data: meta_map,
            created_at: now,
            updated_at: now,
            version: 1,
            tags: Vec::new(),
        };

        // Add back with new metadata
        service.add(id, vector, meta)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to add vector with new metadata: {}", e)))?;
        Ok(true)
    }

    /// Get total count of vectors
    fn count(&self) -> PyResult<usize> {
        let service = self.service.lock().unwrap();
        
        let ids = service.list_ids()
            .map_err(|e| PyRuntimeError::new_err(format!("Count failed: {}", e)))?;
        Ok(ids.len())
    }

    /// Create a snapshot
    fn snapshot(&self, name: Option<String>, metadata: Option<&PyDict>) -> PyResult<()> {
        let service = self.service.lock().unwrap();
        
        if let Some(meta_dict) = metadata {
            let mut meta_map = HashMap::new();
            for (key, value) in meta_dict {
                let key_str = key.extract::<String>()?;
                let value_str = value.extract::<String>()?;
                meta_map.insert(key_str, value_str);
            }
            
            if let Some(snapshot_name) = name {
                service.snapshot_with_metadata(&snapshot_name, meta_map)
                    .map_err(|e| PyRuntimeError::new_err(format!("Snapshot failed: {}", e)))?;
            } else {
                service.snapshot()
                    .map_err(|e| PyRuntimeError::new_err(format!("Snapshot failed: {}", e)))?;
            }
        } else {
            if let Some(snapshot_name) = name {
                service.snapshot_named(&snapshot_name)
                    .map_err(|e| PyRuntimeError::new_err(format!("Snapshot failed: {}", e)))?;
            } else {
                service.snapshot()
                    .map_err(|e| PyRuntimeError::new_err(format!("Snapshot failed: {}", e)))?;
            }
        }

        Ok(())
    }

    /// List all snapshots
    fn list_snapshots(&self) -> PyResult<Vec<String>> {
        let service = self.service.lock().unwrap();
        
        service.storage.list_snapshots()
            .map_err(|e| PyRuntimeError::new_err(format!("List snapshots failed: {}", e)))
    }

    /// Delete a snapshot
    fn delete_snapshot(&self, name: String) -> PyResult<()> {
        let service = self.service.lock().unwrap();
        
        service.storage.delete_snapshot(&name)
            .map_err(|e| PyRuntimeError::new_err(format!("Delete snapshot failed: {}", e)))
    }

    /// Get database statistics
    fn stats(&self) -> PyResult<PyObject> {
        let mut service = self.service.lock().unwrap();
        
        service.storage.refresh_stats()
            .map_err(|e| PyRuntimeError::new_err(format!("Refresh stats failed: {}", e)))?;
        
        let stats = service.storage.stats();
        
        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("total_vectors", stats.total_vectors)?;
            dict.set_item("total_metadata", stats.total_metadata)?;
            dict.set_item("total_snapshots", stats.total_snapshots)?;
            dict.set_item("database_size_bytes", stats.database_size_bytes)?;
            dict.set_item("memory_usage_bytes", stats.memory_usage_bytes)?;
            dict.set_item("total_reads", stats.total_reads)?;
            dict.set_item("total_writes", stats.total_writes)?;
            dict.set_item("average_read_time_ms", stats.average_read_time_ms)?;
            dict.set_item("average_write_time_ms", stats.average_write_time_ms)?;
            dict.set_item("cache_hit_rate", stats.cache_hit_rate)?;
            Ok(dict.into())
        })
    }

    /// Compact the database
    fn compact(&self) -> PyResult<()> {
        let service = self.service.lock().unwrap();
        
        service.storage.compact()
            .map_err(|e| PyRuntimeError::new_err(format!("Compact failed: {}", e)))
    }

    /// Batch insert multiple vectors
    fn batch_insert(&self, vectors: &PyList, metadata_list: Option<&PyList>) -> PyResult<Vec<usize>> {
        let mut service = self.service.lock().unwrap();
        let mut results = Vec::new();

        for (i, vector_obj) in vectors.iter().enumerate() {
            let vector: Vector = vector_obj.extract()?;
            
            let meta = if let Some(meta_list) = metadata_list {
                if let Ok(meta_dict) = meta_list.get_item(i)?.extract::<&PyDict>() {
                    let mut meta_map = HashMap::new();
                    for (key, value) in meta_dict {
                        let key_str = key.extract::<String>()?;
                        let value_str = value.extract::<String>()?;
                        meta_map.insert(key_str, value_str);
                    }
                    let now = SystemTime::now()
                        .duration_since(UNIX_EPOCH)
                        .unwrap()
                        .as_secs();
                    storage::Meta { 
                        data: meta_map,
                        created_at: now,
                        updated_at: now,
                        version: 1,
                        tags: Vec::new(),
                    }
                } else {
                    let now = SystemTime::now()
                        .duration_since(UNIX_EPOCH)
                        .unwrap()
                        .as_secs();
                    storage::Meta { 
                        data: HashMap::new(),
                        created_at: now,
                        updated_at: now,
                        version: 1,
                        tags: Vec::new(),
                    }
                }
            } else {
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs();
                storage::Meta { 
                    data: HashMap::new(),
                    created_at: now,
                    updated_at: now,
                    version: 1,
                    tags: Vec::new(),
                }
            };

            // Get next ID
            let next_id = service.list_ids()
                .map_err(|e| PyRuntimeError::new_err(format!("Failed to get next ID: {}", e)))?
                .len() + i;
            
            service.add(next_id, vector.inner.clone(), meta)
                .map_err(|e| PyRuntimeError::new_err(format!("Batch insert failed at index {}: {}", i, e)))?;
            
            results.push(next_id);
        }

        Ok(results)
    }

    /// Range search - find all vectors within a distance threshold
    fn range_search(&self, query: &Vector, radius: f32) -> PyResult<Vec<(usize, f32)>> {
        let service = self.service.lock().unwrap();
        
        // For now, we'll implement this as a k-NN search with a large k and filter by distance
        // This is not optimal but works with the current API
        let filter = HashMap::new();
        let results = service.search(&query.inner, 1000, &filter);
        
        Ok(results.into_iter().filter(|(_, dist)| *dist <= radius).collect())
    }

    fn __repr__(&self) -> String {
        format!("NusterDB(dim={}, index_type={:?}, vectors={})", 
            self.config.dim, 
            self.config.index_type,
            self.count().unwrap_or(0)
        )
    }
}

/// Python module definition
#[pymodule]
fn nusterdb(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Vector>()?;
    m.add_class::<DistanceMetric>()?;
    m.add_class::<PyIndexType>()?;
    m.add_class::<Compression>()?;
    m.add_class::<DatabaseConfig>()?;
    m.add_class::<NusterDB>()?;
    
    // Add version
    m.add("__version__", "0.1.0")?;
    
    Ok(())
}
