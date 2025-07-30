use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyRuntimeError};
use std::collections::HashMap;

// Import the Rust modules with proper aliasing
use nuster_core::{Vector as CoreVector, DistanceMetric as CoreDistanceMetric};
use api::{Service, ServiceConfig};
use index::{IndexConfig, IndexType, HnswConfig, FlatConfig};
use storage::{StorageConfig, Meta as StorageMeta};

/// Python wrapper for Vector with all advanced features
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
            inner: CoreVector::new(data) 
        })
    }
    
    /// Create a zero vector of given dimension
    #[staticmethod]
    fn zeros(dim: usize) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        Ok(Vector { 
            inner: CoreVector::zeros(dim) 
        })
    }
    
    /// Create a vector of ones with given dimension
    #[staticmethod]
    fn ones(dim: usize) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        Ok(Vector { 
            inner: CoreVector::ones(dim) 
        })
    }
    
    /// Create a random vector with values in range [min, max]
    #[staticmethod]
    fn random(dim: usize, min: f32, max: f32) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        if min > max {
            return Err(PyValueError::new_err("min must be <= max"));
        }
        Ok(Vector { 
            inner: CoreVector::random(dim, min, max) 
        })
    }
    
    /// Create a unit vector (normalized to length 1)
    #[staticmethod]
    fn unit_random(dim: usize) -> PyResult<Self> {
        if dim == 0 {
            return Err(PyValueError::new_err("Dimension must be positive"));
        }
        Ok(Vector { 
            inner: CoreVector::unit_random(dim) 
        })
    }

    // Property getters
    #[getter]
    fn dimension(&self) -> usize {
        self.inner.dim()
    }

    #[getter]
    fn data(&self) -> Vec<f32> {
        self.inner.as_slice().to_vec()
    }
    
    fn __repr__(&self) -> String {
        format!("Vector({})", 
            self.inner.as_slice().iter()
                .map(|x| format!("{:.3}", x))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }
    
    fn len(&self) -> usize {
        self.inner.dim()
    }
    
    fn dim(&self) -> usize {
        self.inner.dim()
    }
    
    /// L1 norm (Manhattan norm)
    fn l1_norm(&self) -> f32 {
        self.inner.l1_norm()
    }

    /// L∞ norm (max norm)
    fn linf_norm(&self) -> f32 {
        self.inner.linf_norm()
    }

    /// Check if vector is normalized (unit length)
    fn is_normalized(&self, tolerance: Option<f32>) -> bool {
        self.inner.is_normalized(tolerance.unwrap_or(1e-6))
    }

    /// Normalize to unit length (returns new vector)
    fn normalize(&self) -> Vector {
        Vector { inner: self.inner.normalize() }
    }

    /// Squared L2 norm (avoids sqrt for efficiency)
    fn norm_squared(&self) -> f32 {
        self.inner.norm_squared()
    }

    /// Check if vector contains only finite values
    fn is_finite(&self) -> bool {
        self.inner.is_finite()
    }
    
    /// Dot product with another vector
    fn dot(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.dot(&other.inner))
    }
    
    /// Euclidean norm (L2 norm)
    fn norm(&self) -> f32 {
        self.inner.norm()
    }
    
    /// Normalize to unit length (modifies in place)
    fn normalize_mut(&mut self) {
        self.inner.normalize_mut();
    }
    
    /// Euclidean distance to another vector
    fn euclidean_distance(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.euclidean_distance(&other.inner))
    }
    
    /// Manhattan distance
    fn manhattan_distance(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.manhattan_distance(&other.inner))
    }
    
    /// Cosine similarity
    fn cosine_similarity(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.cosine_similarity(&other.inner))
    }
    
    /// Cosine distance
    fn cosine_distance(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.cosine_distance(&other.inner))
    }

    /// Angular distance with another vector
    fn angular_distance(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.angular_distance(&other.inner))
    }

    /// Chebyshev distance with another vector
    fn chebyshev_distance(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.chebyshev_distance(&other.inner))
    }

    /// Jaccard similarity with another vector (for binary vectors)
    fn jaccard_similarity(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.jaccard_similarity(&other.inner))
    }

    /// Hamming distance with another vector (for binary vectors)
    fn hamming_distance(&self, other: &Vector) -> PyResult<f32> {
        if self.inner.dim() != other.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.hamming_distance(&other.inner))
    }
}

/// Distance metric enumeration
#[pyclass]
#[derive(Clone)]
pub struct DistanceMetric {
    inner: CoreDistanceMetric,
}

#[pymethods]
impl DistanceMetric {
    /// Euclidean distance
    #[staticmethod]
    fn euclidean() -> Self {
        DistanceMetric { inner: CoreDistanceMetric::Euclidean }
    }
    
    /// Manhattan distance
    #[staticmethod]
    fn manhattan() -> Self {
        DistanceMetric { inner: CoreDistanceMetric::Manhattan }
    }
    
    /// Cosine distance
    #[staticmethod]
    fn cosine() -> Self {
        DistanceMetric { inner: CoreDistanceMetric::Cosine }
    }
    
    /// Angular distance
    #[staticmethod]
    fn angular() -> Self {
        DistanceMetric { inner: CoreDistanceMetric::Angular }
    }

    /// Chebyshev distance
    #[staticmethod]
    fn chebyshev() -> Self {
        DistanceMetric { inner: CoreDistanceMetric::Chebyshev }
    }

    /// Jaccard distance
    #[staticmethod]
    fn jaccard() -> Self {
        DistanceMetric { inner: CoreDistanceMetric::Jaccard }
    }

    /// Hamming distance
    #[staticmethod]
    fn hamming() -> Self {
        DistanceMetric { inner: CoreDistanceMetric::Hamming }
    }
    
    /// Calculate distance between two vectors
    fn distance(&self, a: &Vector, b: &Vector) -> PyResult<f32> {
        if a.inner.dim() != b.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.distance(&a.inner, &b.inner))
    }
    
    /// Calculate similarity between two vectors
    fn similarity(&self, a: &Vector, b: &Vector) -> PyResult<f32> {
        if a.inner.dim() != b.inner.dim() {
            return Err(PyValueError::new_err("Vector dimensions must match"));
        }
        Ok(self.inner.similarity(&a.inner, &b.inner))
    }
    
    fn __repr__(&self) -> String {
        format!("DistanceMetric::{:?}", self.inner)
    }
}

/// Metadata wrapper for vectors
#[pyclass]
#[derive(Clone)]
pub struct Metadata {
    inner: StorageMeta,
}

#[pymethods]
impl Metadata {
    #[new]
    fn new() -> Self {
        Metadata { inner: StorageMeta::new() }
    }
    
    /// Create metadata with initial data
    #[staticmethod]
    fn with_data(data: HashMap<String, String>) -> Self {
        Metadata { inner: StorageMeta::with_data(data) }
    }
    
    /// Set a key-value pair
    fn set(&mut self, key: String, value: String) {
        self.inner.set(key, value);
    }
    
    /// Get a value by key
    fn get(&self, key: &str) -> Option<String> {
        self.inner.get(key).cloned()
    }
    
    /// Get all keys
    fn keys(&self) -> Vec<String> {
        self.inner.keys().cloned().collect()
    }
    
    /// Add a tag
    fn add_tag(&mut self, tag: String) {
        self.inner.add_tag(tag);
    }
    
    /// Get all tags
    fn tags(&self) -> Vec<String> {
        self.inner.tags.clone()
    }
    
    /// Check if has tag
    fn has_tag(&self, tag: &str) -> bool {
        self.inner.has_tag(tag)
    }

    /// Check if contains key
    fn contains_key(&self, key: &str) -> bool {
        self.inner.data.contains_key(key)
    }

    /// Create new metadata with tags (static method)
    #[staticmethod]
    fn with_tags(tags: Vec<String>) -> Self {
        let meta = StorageMeta::new().with_tags(tags);
        Metadata { inner: meta }
    }
    
    /// Remove a tag
    fn remove_tag(&mut self, tag: &str) -> bool {
        self.inner.remove_tag(tag)
    }

    /// Remove a key
    fn remove(&mut self, key: &str) -> Option<String> {
        self.inner.remove(key)
    }

    /// Check if metadata is empty
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Get number of keys
    fn len(&self) -> usize {
        self.inner.len()
    }

    /// Get age in seconds
    fn age_seconds(&self) -> u64 {
        self.inner.age_seconds()
    }

    // Property getters
    #[getter]
    fn created_at(&self) -> u64 {
        self.inner.created_at
    }

    #[getter]
    fn updated_at(&self) -> u64 {
        self.inner.updated_at
    }

    #[getter]
    fn version(&self) -> u32 {
        self.inner.version
    }
    
    fn __repr__(&self) -> String {
        format!("Metadata(keys={}, tags={}, version={})", 
                self.inner.len(), self.inner.tags.len(), self.inner.version)
    }
}

/// HNSW configuration
#[pyclass]
#[derive(Clone)]
pub struct HNSWConfig {
    inner: HnswConfig,
}

#[pymethods]
impl HNSWConfig {
    #[new]
    #[pyo3(signature = (
        max_nb_connection=16, 
        max_nb_elements=1024, 
        max_layer=16, 
        ef_construction=200, 
        ef_search=None, 
        use_heuristic=true
    ))]
    fn new(
        max_nb_connection: usize,
        max_nb_elements: usize,
        max_layer: usize,
        ef_construction: usize,
        ef_search: Option<usize>,
        use_heuristic: bool,
    ) -> Self {
        HNSWConfig {
            inner: HnswConfig {
                max_nb_connection,
                max_nb_elements,
                max_layer,
                ef_construction,
                ef_search,
                use_heuristic,
            }
        }
    }
    
    /// Create default HNSW configuration
    #[staticmethod]
    fn default() -> Self {
        HNSWConfig { inner: HnswConfig::default() }
    }
    
    // Property getters
    #[getter]
    fn max_nb_connection(&self) -> usize {
        self.inner.max_nb_connection
    }

    #[getter]
    fn max_nb_elements(&self) -> usize {
        self.inner.max_nb_elements
    }

    #[getter]
    fn max_layer(&self) -> usize {
        self.inner.max_layer
    }

    #[getter]
    fn ef_construction(&self) -> usize {
        self.inner.ef_construction
    }

    #[getter]
    fn ef_search(&self) -> Option<usize> {
        self.inner.ef_search
    }

    #[getter]
    fn use_heuristic(&self) -> bool {
        self.inner.use_heuristic
    }
    
    fn __repr__(&self) -> String {
        format!("HNSWConfig(m={}, ef_construction={}, max_elements={})", 
                self.inner.max_nb_connection, self.inner.ef_construction, self.inner.max_nb_elements)
    }
}

/// Flat index configuration
#[pyclass]
#[derive(Clone)]
pub struct FlatIndexConfig {
    inner: FlatConfig,
}

#[pymethods]
impl FlatIndexConfig {
    #[new]
    fn new() -> Self {
        FlatIndexConfig {
            inner: FlatConfig::default(),
        }
    }
    
    /// Create default flat configuration
    #[staticmethod]
    fn default() -> Self {
        FlatIndexConfig { inner: FlatConfig::default() }
    }
    
    fn __repr__(&self) -> String {
        "FlatIndexConfig()".to_string()
    }
}

/// Storage configuration with advanced options
#[pyclass]
#[derive(Clone)]
pub struct StorageConfiguration {
    inner: StorageConfig,
}

#[pymethods]
impl StorageConfiguration {
    #[new]
    #[pyo3(signature = (
        cache_size_mb=256,
        write_buffer_size_mb=64,
        max_write_buffer_number=3,
        compression="lz4",
        enable_statistics=true,
        enable_bloom_filter=true,
        bloom_filter_bits_per_key=10,
        max_background_jobs=4
    ))]
    fn new(
        cache_size_mb: u64,
        write_buffer_size_mb: u64,
        max_write_buffer_number: i32,
        compression: &str,
        enable_statistics: bool,
        enable_bloom_filter: bool,
        bloom_filter_bits_per_key: i32,
        max_background_jobs: i32,
    ) -> PyResult<Self> {
        use storage::CompressionType;
        use storage::CompactionStyle;
        
        let compression_type = match compression.to_lowercase().as_str() {
            "none" => CompressionType::None,
            "snappy" => CompressionType::Snappy,
            "lz4" => CompressionType::LZ4,
            "zstd" => CompressionType::ZSTD,
            _ => return Err(PyValueError::new_err("compression must be one of: none, snappy, lz4, zstd")),
        };
        
        Ok(StorageConfiguration {
            inner: StorageConfig {
                compression: compression_type,
                cache_size_mb,
                write_buffer_size_mb,
                max_write_buffer_number,
                enable_statistics,
                enable_bloom_filter,
                bloom_filter_bits_per_key,
                compaction_style: CompactionStyle::Level,
                max_background_jobs,
            },
        })
    }
    
    /// Create default storage configuration
    #[staticmethod]
    fn default() -> Self {
        StorageConfiguration { inner: StorageConfig::default() }
    }
    
    fn __repr__(&self) -> String {
        format!("StorageConfiguration(cache_size_mb={}, compression={:?})", 
                self.inner.cache_size_mb, self.inner.compression)
    }
}

/// Database configuration with all advanced options
#[pyclass]
#[derive(Clone)]
pub struct DatabaseConfig {
    inner: ServiceConfig,
    index_config: IndexConfig,
    storage_config: StorageConfig,
}

#[pymethods]
impl DatabaseConfig {
    #[new]
    #[pyo3(signature = (
        dim,
        index_type="flat",
        distance_metric=None,
        hnsw_config=None,
        auto_snapshot=false,
        snapshot_interval_secs=3600
    ))]
    fn new(
        dim: usize,
        index_type: &str,
        distance_metric: Option<&DistanceMetric>,
        hnsw_config: Option<&HNSWConfig>,
        auto_snapshot: bool,
        snapshot_interval_secs: u64,
    ) -> PyResult<Self> {
        let idx_type = match index_type.to_lowercase().as_str() {
            "flat" => IndexType::Flat,
            "hnsw" => IndexType::Hnsw,
            "optimized-flat" | "optimized_flat" => IndexType::OptimizedFlat,
            "ultra-fast-flat" | "ultra_fast_flat" => IndexType::UltraFastFlat,
            "super-optimized-flat" | "super_optimized_flat" => IndexType::SuperOptimizedFlat,
            _ => return Err(PyValueError::new_err("index_type must be 'flat', 'hnsw', 'optimized-flat', 'ultra-fast-flat', or 'super-optimized-flat'")),
        };
        
        let dist_metric = distance_metric
            .map(|dm| dm.inner)
            .unwrap_or(CoreDistanceMetric::Euclidean);
        
        let service_config = ServiceConfig {
            dim,
            use_hnsw: matches!(idx_type, IndexType::Hnsw),
            hnsw_m: hnsw_config.map(|hc| hc.inner.max_nb_connection).unwrap_or(16),
            hnsw_ef_construction: hnsw_config.map(|hc| hc.inner.ef_construction).unwrap_or(200),
            auto_snapshot,
            snapshot_interval_secs,
        };
        
        let index_config = IndexConfig {
            dim,
            distance_metric: dist_metric,
            index_type: idx_type,
            hnsw_config: hnsw_config.map(|hc| hc.inner.clone()),
            flat_config: Some(FlatConfig::default()),
        };
        
        let storage_config = StorageConfig::default();
        
        Ok(DatabaseConfig {
            inner: service_config,
            index_config,
            storage_config,
        })
    }
    
    /// Create simple configuration
    #[staticmethod]
    fn simple(dim: usize, use_hnsw: bool) -> Self {
        let service_config = ServiceConfig {
            dim,
            use_hnsw,
            ..Default::default()
        };
        
        let index_config = IndexConfig {
            dim,
            distance_metric: CoreDistanceMetric::Euclidean,
            index_type: if use_hnsw { IndexType::Hnsw } else { IndexType::Flat },
            hnsw_config: if use_hnsw { Some(HnswConfig::default()) } else { None },
            flat_config: Some(FlatConfig::default()),
        };
        
        DatabaseConfig {
            inner: service_config,
            index_config,
            storage_config: StorageConfig::default(),
        }
    }
    
    /// Create configuration for OptimizedFlat index
    #[staticmethod]
    fn optimized_flat(dim: usize) -> Self {
        let service_config = ServiceConfig {
            dim,
            use_hnsw: false,
            ..Default::default()
        };
        
        let index_config = IndexConfig {
            dim,
            distance_metric: CoreDistanceMetric::Euclidean,
            index_type: IndexType::OptimizedFlat,
            hnsw_config: None,
            flat_config: Some(FlatConfig::default()),
        };
        
        DatabaseConfig {
            inner: service_config,
            index_config,
            storage_config: StorageConfig::default(),
        }
    }
    
    /// Create configuration for UltraFastFlat index
    #[staticmethod]
    fn ultra_fast_flat(dim: usize) -> Self {
        let service_config = ServiceConfig {
            dim,
            use_hnsw: false,
            ..Default::default()
        };
        
        let index_config = IndexConfig {
            dim,
            distance_metric: CoreDistanceMetric::Euclidean,
            index_type: IndexType::UltraFastFlat,
            hnsw_config: None,
            flat_config: Some(FlatConfig::default()),
        };
        
        DatabaseConfig {
            inner: service_config,
            index_config,
            storage_config: StorageConfig::default(),
        }
    }
    
    /// Create configuration for SuperOptimizedFlat index
    #[staticmethod]
    fn super_optimized_flat(dim: usize) -> Self {
        let service_config = ServiceConfig {
            dim,
            use_hnsw: false,
            ..Default::default()
        };
        
        let index_config = IndexConfig {
            dim,
            distance_metric: CoreDistanceMetric::Euclidean,
            index_type: IndexType::SuperOptimizedFlat,
            hnsw_config: None,
            flat_config: Some(FlatConfig::default()),
        };
        
        DatabaseConfig {
            inner: service_config,
            index_config,
            storage_config: StorageConfig::default(),
        }
    }
    
    fn __repr__(&self) -> String {
        format!("DatabaseConfig(dim={}, index={}, auto_snapshot={})", 
                self.inner.dim, 
                if self.inner.use_hnsw { "HNSW" } else { "Flat" },
                self.inner.auto_snapshot)
    }
}

/// Database statistics
#[pyclass]
#[derive(Clone)]
pub struct DatabaseStats {
    pub vector_count: usize,
    pub dimension: usize,
    pub index_type: String,
    pub metadata_keys: Vec<String>,
}

#[pymethods]
impl DatabaseStats {
    // Property getters
    #[getter]
    fn vector_count(&self) -> usize {
        self.vector_count
    }

    #[getter]
    fn dimension(&self) -> usize {
        self.dimension
    }

    #[getter]
    fn index_type(&self) -> String {
        self.index_type.clone()
    }

    #[getter]
    fn metadata_keys(&self) -> Vec<String> {
        self.metadata_keys.clone()
    }

    fn __repr__(&self) -> String {
        format!("DatabaseStats(vectors={}, dim={}, index={})", 
                self.vector_count, self.dimension, self.index_type)
    }
}

/// Advanced NusterDB implementation with all features
#[pyclass]
pub struct NusterDB {
    service: Service,
    path: String,
}

#[pymethods]
impl NusterDB {
    #[new]
    fn new(path: String, config: DatabaseConfig) -> PyResult<Self> {
        let service = api::Service::new_with_configs(&path, config.index_config, config.storage_config)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create database: {}", e)))?;
        
        Ok(NusterDB { service, path })
    }
    
    /// Create database with simple configuration
    #[staticmethod]
    fn simple(path: String, dim: usize, use_hnsw: bool) -> PyResult<Self> {
        let service = api::Service::new(&path, dim, use_hnsw)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create database: {}", e)))?;
        
        Ok(NusterDB { service, path })
    }
    
    /// Create database with OptimizedFlat index
    #[staticmethod]
    fn optimized_flat(path: String, dim: usize) -> PyResult<Self> {
        let config = DatabaseConfig::optimized_flat(dim);
        let service = api::Service::new_with_configs(&path, config.index_config, config.storage_config)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create database: {}", e)))?;
        
        Ok(NusterDB { service, path })
    }
    
    /// Create database with UltraFastFlat index
    #[staticmethod]
    fn ultra_fast_flat(path: String, dim: usize) -> PyResult<Self> {
        let config = DatabaseConfig::ultra_fast_flat(dim);
        let service = api::Service::new_with_configs(&path, config.index_config, config.storage_config)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create database: {}", e)))?;
        
        Ok(NusterDB { service, path })
    }
    
    fn dimension(&self) -> usize {
        self.service.dimension()
    }
    
    fn index_type(&self) -> String {
        self.service.index_type().to_string()
    }
    
    /// Add a vector with metadata
    fn add(&mut self, id: usize, vector: &Vector, metadata: Option<&Metadata>) -> PyResult<()> {
        let meta = metadata
            .map(|m| m.inner.clone())
            .unwrap_or_else(|| StorageMeta::new());
        
        self.service.add(id, vector.inner.clone(), meta)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to add vector: {}", e)))
    }
    
    /// Add multiple vectors with metadata (bulk insertion)
    fn bulk_add(&mut self, ids: Vec<usize>, vectors: Vec<Vector>, metadata: Option<Vec<Metadata>>) -> PyResult<usize> {
        let vecs: Vec<_> = vectors.into_iter().map(|v| v.inner).collect();
        let metas: Vec<_> = if let Some(meta_list) = metadata {
            meta_list.into_iter().map(|m| m.inner).collect()
        } else {
            vec![StorageMeta::new(); ids.len()]
        };
        
        if ids.len() != vecs.len() || ids.len() != metas.len() {
            return Err(PyValueError::new_err("IDs, vectors, and metadata lists must have the same length"));
        }
        
        self.service.bulk_add(&ids, &vecs, &metas)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to bulk add vectors: {}", e)))
    }
    
    /// Search for k nearest neighbors with optional metadata filtering
    fn search(&self, query: &Vector, k: usize, filter: Option<HashMap<String, String>>) -> PyResult<Vec<(usize, f32)>> {
        let filter_map = filter.unwrap_or_default();
        let results = self.service.search(&query.inner, k, &filter_map);
        Ok(results)
    }
    
    /// Get vector by ID
    fn get(&self, id: usize) -> PyResult<Option<Vector>> {
        match self.service.get(id) {
            Ok(vector) => Ok(Some(Vector { inner: vector })),
            Err(_) => Ok(None),
        }
    }
    
    /// Get metadata by ID
    fn get_metadata(&self, id: usize) -> Option<Metadata> {
        self.service.get_metadata(id)
            .map(|meta| Metadata { inner: meta.clone() })
    }
    
    /// Remove vector by ID
    fn remove(&mut self, id: usize) -> PyResult<()> {
        self.service.remove(id)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to remove vector: {}", e)))
    }
    
    /// List all vector IDs
    fn list_ids(&self) -> PyResult<Vec<usize>> {
        self.service.list_ids()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to list IDs: {}", e)))
    }
    
    /// Get database statistics
    fn stats(&self) -> PyResult<DatabaseStats> {
        let stats = self.service.stats()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to get stats: {}", e)))?;
        
        Ok(DatabaseStats {
            vector_count: stats.vector_count,
            dimension: stats.dimension,
            index_type: stats.index_type,
            metadata_keys: stats.metadata_keys,
        })
    }
    
    /// Create a snapshot
    fn snapshot(&self) -> PyResult<()> {
        self.service.snapshot()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create snapshot: {}", e)))
    }
    
    /// Create a named snapshot
    fn snapshot_named(&self, name: &str) -> PyResult<()> {
        self.service.snapshot_named(name)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create snapshot '{}': {}", name, e)))
    }
    
    /// Create a named snapshot with metadata
    fn snapshot_with_metadata(&self, name: &str, metadata: HashMap<String, String>) -> PyResult<()> {
        self.service.snapshot_with_metadata(name, metadata)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create snapshot '{}' with metadata: {}", name, e)))
    }
    
    /// Check if database is using HNSW
    fn is_hnsw(&self) -> bool {
        self.service.index_type() == "HNSW"
    }
    
    /// Check if database is using Flat index
    fn is_flat(&self) -> bool {
        self.service.index_type() == "Flat"
    }
    
    fn __repr__(&self) -> String {
        format!("NusterDB(path='{}', dim={}, index={}, vectors={})", 
                self.path, 
                self.service.dimension(), 
                self.service.index_type(),
                self.service.list_ids().unwrap_or_default().len())
    }
}

/// Python module definition
#[pymodule]
fn nusterdb(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Vector>()?;
    m.add_class::<DistanceMetric>()?;
    m.add_class::<Metadata>()?;
    m.add_class::<HNSWConfig>()?;
    m.add_class::<DatabaseConfig>()?;
    m.add_class::<DatabaseStats>()?;
    m.add_class::<NusterDB>()?;
    m.add_class::<FlatIndexConfig>()?;
    m.add_class::<StorageConfiguration>()?;
    
    // Add version
    m.add("__version__", "0.1.6")?;
    
    // Add constants
    m.add("DEFAULT_HNSW_M", 16)?;
    m.add("DEFAULT_HNSW_EF_CONSTRUCTION", 200)?;
    m.add("DEFAULT_CACHE_SIZE_MB", 256)?;
    
    Ok(())
}
