//! storage: persisting vectors and index snapshots

use core as core_crate;
use core_crate::Vector;
use rocksdb::{DB, Options, Error as RocksDBError, WriteBatch, IteratorMode, BlockBasedOptions, Cache};
use bincode;
use std::fmt;
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH, Instant};
use std::sync::{Arc, Mutex};
use serde::{Serialize, Deserialize};

/// Storage configuration options
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StorageConfig {
    pub compression: CompressionType,
    pub cache_size_mb: u64,
    pub write_buffer_size_mb: u64,
    pub max_write_buffer_number: i32,
    pub enable_statistics: bool,
    pub enable_bloom_filter: bool,
    pub bloom_filter_bits_per_key: i32,
    pub compaction_style: CompactionStyle,
    pub max_background_jobs: i32,
}

impl Default for StorageConfig {
    fn default() -> Self {
        Self {
            compression: CompressionType::LZ4,
            cache_size_mb: 256,
            write_buffer_size_mb: 64,
            max_write_buffer_number: 3,
            enable_statistics: true,
            enable_bloom_filter: true,
            bloom_filter_bits_per_key: 10,
            compaction_style: CompactionStyle::Level,
            max_background_jobs: 4,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum CompressionType {
    None,
    Snappy,
    LZ4,
    ZSTD,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CompactionStyle {
    Level,
    Universal,
    FIFO,
}

/// Enhanced metadata wrapper with timestamps and version tracking
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Meta {
    pub data: HashMap<String, String>,
    pub created_at: u64,
    pub updated_at: u64,
    pub version: u32,
    pub tags: Vec<String>,
}

impl Meta {
    pub fn new() -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        Meta {
            data: HashMap::new(),
            created_at: now,
            updated_at: now,
            version: 1,
            tags: Vec::new(),
        }
    }
    
    pub fn with_data(data: HashMap<String, String>) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        Meta {
            data,
            created_at: now,
            updated_at: now,
            version: 1,
            tags: Vec::new(),
        }
    }

    pub fn with_tags(mut self, tags: Vec<String>) -> Self {
        self.tags = tags;
        self
    }

    pub fn add_tag(&mut self, tag: String) {
        if !self.tags.contains(&tag) {
            self.tags.push(tag);
        }
        self.touch();
    }

    pub fn remove_tag(&mut self, tag: &str) -> bool {
        if let Some(pos) = self.tags.iter().position(|t| t == tag) {
            self.tags.remove(pos);
            self.touch();
            true
        } else {
            false
        }
    }

    pub fn has_tag(&self, tag: &str) -> bool {
        self.tags.contains(&String::from(tag))
    }

    pub fn get(&self, key: &str) -> Option<&String> {
        self.data.get(key)
    }

    pub fn set(&mut self, key: String, value: String) {
        self.data.insert(key, value);
        self.touch();
    }

    pub fn remove(&mut self, key: &str) -> Option<String> {
        let result = self.data.remove(key);
        if result.is_some() {
            self.touch();
        }
        result
    }

    pub fn keys(&self) -> impl Iterator<Item = &String> {
        self.data.keys()
    }

    pub fn values(&self) -> impl Iterator<Item = &String> {
        self.data.values()
    }

    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    pub fn len(&self) -> usize {
        self.data.len()
    }

    fn touch(&mut self) {
        self.updated_at = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        self.version += 1;
    }

    /// Check if metadata matches a filter
    pub fn matches_filter(&self, filter: &HashMap<String, String>) -> bool {
        filter.iter().all(|(k, v)| {
            self.data.get(k).map(|mv| mv == v).unwrap_or(false)
        })
    }

    /// Get age in seconds
    pub fn age_seconds(&self) -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs() - self.created_at
    }
}

/// Batch operation for bulk inserts/updates
#[derive(Debug)]
pub struct VectorBatch {
    pub vectors: Vec<(usize, Vector)>,
    pub metadata: Vec<(usize, Meta)>,
}

impl VectorBatch {
    pub fn new() -> Self {
        Self {
            vectors: Vec::new(),
            metadata: Vec::new(),
        }
    }

    pub fn add_vector(&mut self, id: usize, vector: Vector) {
        self.vectors.push((id, vector));
    }

    pub fn add_metadata(&mut self, id: usize, meta: Meta) {
        self.metadata.push((id, meta));
    }

    pub fn add_vector_with_metadata(&mut self, id: usize, vector: Vector, meta: Meta) {
        self.vectors.push((id, vector));
        self.metadata.push((id, meta));
    }

    pub fn len(&self) -> usize {
        self.vectors.len().max(self.metadata.len())
    }

    pub fn is_empty(&self) -> bool {
        self.vectors.is_empty() && self.metadata.is_empty()
    }

    pub fn clear(&mut self) {
        self.vectors.clear();
        self.metadata.clear();
    }
}

/// Storage statistics and metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StorageStats {
    pub total_vectors: usize,
    pub total_snapshots: usize,
    pub total_metadata: usize,
    pub database_size_bytes: u64,
    pub memory_usage_bytes: u64,
    pub total_reads: u64,
    pub total_writes: u64,
    pub average_read_time_ms: f64,
    pub average_write_time_ms: f64,
    pub cache_hit_rate: f64,
    pub compaction_stats: HashMap<String, u64>,
}

/// Custom error type for storage operations
#[derive(Debug)]
pub enum StorageError {
    RocksDB(RocksDBError),
    Serialization(String),
    NotFound(String),
    InvalidConfiguration(String),
    BatchTooLarge(String),
    VersionMismatch(String),
}

impl fmt::Display for StorageError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            StorageError::RocksDB(e) => write!(f, "RocksDB error: {}", e),
            StorageError::Serialization(msg) => write!(f, "Serialization error: {}", msg),
            StorageError::NotFound(msg) => write!(f, "Not found: {}", msg),
            StorageError::InvalidConfiguration(msg) => write!(f, "Invalid configuration: {}", msg),
            StorageError::BatchTooLarge(msg) => write!(f, "Batch too large: {}", msg),
            StorageError::VersionMismatch(msg) => write!(f, "Version mismatch: {}", msg),
        }
    }
}

impl std::error::Error for StorageError {}

impl From<RocksDBError> for StorageError {
    fn from(err: RocksDBError) -> Self {
        StorageError::RocksDB(err)
    }
}

/// Snapshot metadata for better snapshot management
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotInfo {
    pub name: String,
    pub created_at: u64,
    pub size_bytes: u64,
    pub vector_count: usize,
    pub index_type: String,
    pub compression: CompressionType,
    pub checksum: u64,
    pub metadata: HashMap<String, String>,
}

/// A enhanced wrapper around RocksDB for vector + snapshot storage.
pub struct Storage {
    db: DB,
    config: StorageConfig,
    stats: Arc<Mutex<StorageStats>>,
}

impl Storage {
    /// Open (or create) a RocksDB at `path` with default configuration.
    pub fn open(path: &str) -> Result<Self, StorageError> {
        Self::with_config(path, StorageConfig::default())
    }

    /// Open (or create) a RocksDB at `path` with custom configuration.
    pub fn with_config(path: &str, config: StorageConfig) -> Result<Self, StorageError> {
        let mut opts = Options::default();
        opts.create_if_missing(true);
        
        // Apply configuration
        Self::apply_config_to_options(&mut opts, &config)?;
        
        let db = DB::open(&opts, path)?;
        
        let stats = StorageStats {
            total_vectors: 0,
            total_snapshots: 0,
            total_metadata: 0,
            database_size_bytes: 0,
            memory_usage_bytes: 0,
            total_reads: 0,
            total_writes: 0,
            average_read_time_ms: 0.0,
            average_write_time_ms: 0.0,
            cache_hit_rate: 0.0,
            compaction_stats: HashMap::new(),
        };
        
        let mut storage = Self { 
            db, 
            config, 
            stats: Arc::new(Mutex::new(stats))
        };
        storage.refresh_stats()?;
        Ok(storage)
    }

    fn apply_config_to_options(opts: &mut Options, config: &StorageConfig) -> Result<(), StorageError> {
        // Compression
        match config.compression {
            CompressionType::None => opts.set_compression_type(rocksdb::DBCompressionType::None),
            CompressionType::Snappy => opts.set_compression_type(rocksdb::DBCompressionType::Snappy),
            CompressionType::LZ4 => opts.set_compression_type(rocksdb::DBCompressionType::Lz4),
            CompressionType::ZSTD => opts.set_compression_type(rocksdb::DBCompressionType::Zstd),
        }

        // Memory and write settings - fix type conversion
        opts.set_write_buffer_size((config.write_buffer_size_mb * 1024 * 1024) as usize);
        opts.set_max_write_buffer_number(config.max_write_buffer_number);
        opts.set_max_background_jobs(config.max_background_jobs);

        // Block cache - use proper RocksDB API
        let cache_size = (config.cache_size_mb * 1024 * 1024) as usize;
        let cache = Cache::new_lru_cache(cache_size);
        let mut block_opts = BlockBasedOptions::default();
        block_opts.set_block_cache(&cache);
        opts.set_block_based_table_factory(&block_opts);

        // Bloom filter
        if config.enable_bloom_filter {
            block_opts.set_bloom_filter(config.bloom_filter_bits_per_key as f64, false);
            opts.set_block_based_table_factory(&block_opts);
        }

        // Statistics
        if config.enable_statistics {
            opts.enable_statistics();
        }

        // Compaction style
        match config.compaction_style {
            CompactionStyle::Level => opts.set_compaction_style(rocksdb::DBCompactionStyle::Level),
            CompactionStyle::Universal => opts.set_compaction_style(rocksdb::DBCompactionStyle::Universal),
            CompactionStyle::FIFO => opts.set_compaction_style(rocksdb::DBCompactionStyle::Fifo),
        }

        Ok(())
    }

    /// Get storage configuration
    pub fn config(&self) -> &StorageConfig {
        &self.config
    }

    /// Get storage statistics
    pub fn stats(&self) -> StorageStats {
        self.stats.lock().unwrap().clone()
    }

    /// Refresh storage statistics
    pub fn refresh_stats(&mut self) -> Result<(), StorageError> {
        // Count vectors, metadata, and snapshots
        let mut vector_count = 0;
        let mut metadata_count = 0;
        let mut snapshot_count = 0;

        let iter = self.db.iterator(IteratorMode::Start);
        for item in iter {
            let (key, _) = item?;
            let key_str = String::from_utf8_lossy(&key);
            
            if key_str.starts_with("vec:") {
                vector_count += 1;
            } else if key_str.starts_with("meta:") {
                metadata_count += 1;
            } else if key_str.starts_with("snap:") {
                snapshot_count += 1;
            }
        }

        let mut stats = self.stats.lock().unwrap();
        stats.total_vectors = vector_count;
        stats.total_metadata = metadata_count;
        stats.total_snapshots = snapshot_count;

        // Get database size
        if let Ok(Some(size)) = self.db.property_value("rocksdb.total-sst-files-size") {
            if let Ok(size_bytes) = size.parse::<u64>() {
                stats.database_size_bytes = size_bytes;
            }
        }

        // Get memory usage
        if let Ok(Some(mem)) = self.db.property_value("rocksdb.cur-size-all-mem-tables") {
            if let Ok(mem_bytes) = mem.parse::<u64>() {
                stats.memory_usage_bytes = mem_bytes;
            }
        }

        Ok(())
    }

    /// Persist a vector under key `vec:<id>`.
    pub fn save_vector(&self, id: usize, vector: &Vector) -> Result<(), StorageError> {
        let start = Instant::now();
        
        let key = format!("vec:{}", id);
        let raw = vector.raw();
        let encoded = bincode::serialize(&raw)
            .map_err(|e| StorageError::Serialization(format!("Vector serialization failed: {}", e)))?;
        
        self.db.put(key.as_bytes(), &encoded)?;
        
        // Update stats safely
        let write_time = start.elapsed().as_secs_f64() * 1000.0;
        let mut stats = self.stats.lock().unwrap();
        stats.total_writes += 1;
        stats.average_write_time_ms = 
            (stats.average_write_time_ms * (stats.total_writes - 1) as f64 + write_time) 
            / stats.total_writes as f64;
        
        Ok(())
    }

    /// Load a vector by its `id`.
    pub fn load_vector(&self, id: usize) -> Result<Vector, StorageError> {
        let start = Instant::now();
        
        let key = format!("vec:{}", id);
        let result = if let Some(data) = self.db.get(key.as_bytes())? {
            let raw: Vec<f32> = bincode::deserialize(&data)
                .map_err(|e| StorageError::Serialization(format!("Vector deserialization failed: {}", e)))?;
            Ok(Vector::new(raw))
        } else {
            Err(StorageError::NotFound(format!("Vector with id {} not found", id)))
        };

        // Update stats safely
        let read_time = start.elapsed().as_secs_f64() * 1000.0;
        let mut stats = self.stats.lock().unwrap();
        stats.total_reads += 1;
        stats.average_read_time_ms = 
            (stats.average_read_time_ms * (stats.total_reads - 1) as f64 + read_time) 
            / stats.total_reads as f64;

        result
    }

    /// Save metadata under `meta:<id>`
    pub fn save_metadata(&self, id: usize, meta: &Meta) -> Result<(), StorageError> {
        let key = format!("meta:{}", id);
        let encoded = bincode::serialize(meta)
            .map_err(|e| StorageError::Serialization(format!("Metadata serialization failed: {}", e)))?;
        self.db.put(key.as_bytes(), &encoded)?;
        Ok(())
    }

    /// Load metadata for `id` (empty if none)
    pub fn load_metadata(&self, id: usize) -> Result<Meta, StorageError> {
        let key = format!("meta:{}", id);
        if let Some(data) = self.db.get(key.as_bytes())? {
            let meta: Meta = bincode::deserialize(&data)
                .map_err(|e| StorageError::Serialization(format!("Metadata deserialization failed: {}", e)))?;
            Ok(meta)
        } else {
            Ok(Meta::new())
        }
    }

    /// Batch save vectors and metadata for better performance
    pub fn save_batch(&self, batch: &VectorBatch) -> Result<(), StorageError> {
        if batch.len() > 10000 {
            return Err(StorageError::BatchTooLarge(
                "Batch size exceeds maximum of 10,000 items".to_string()
            ));
        }

        let mut write_batch = WriteBatch::default();

        // Add vectors to batch
        for (id, vector) in &batch.vectors {
            let key = format!("vec:{}", id);
            let raw = vector.raw();
            let encoded = bincode::serialize(&raw)
                .map_err(|e| StorageError::Serialization(format!("Vector serialization failed: {}", e)))?;
            write_batch.put(key.as_bytes(), &encoded);
        }

        // Add metadata to batch
        for (id, meta) in &batch.metadata {
            let key = format!("meta:{}", id);
            let encoded = bincode::serialize(meta)
                .map_err(|e| StorageError::Serialization(format!("Metadata serialization failed: {}", e)))?;
            write_batch.put(key.as_bytes(), &encoded);
        }

        // Execute batch write
        self.db.write(write_batch)?;
        Ok(())
    }

    /// Query vectors by metadata filter
    pub fn query_by_metadata(&self, filter: &HashMap<String, String>) -> Result<Vec<usize>, StorageError> {
        let mut matching_ids = Vec::new();
        
        let iter = self.db.iterator(IteratorMode::Start);
        for item in iter {
            let (key, value) = item?;
            let key_str = String::from_utf8_lossy(&key);
            
            if let Some(id_str) = key_str.strip_prefix("meta:") {
                if let Ok(id) = id_str.parse::<usize>() {
                    let meta: Meta = bincode::deserialize(&value)
                        .map_err(|e| StorageError::Serialization(format!("Metadata deserialization failed: {}", e)))?;
                    
                    if meta.matches_filter(filter) {
                        matching_ids.push(id);
                    }
                }
            }
        }
        
        Ok(matching_ids)
    }

    /// Query vectors by tags
    pub fn query_by_tags(&self, tags: &[String], require_all: bool) -> Result<Vec<usize>, StorageError> {
        let mut matching_ids = Vec::new();
        
        let iter = self.db.iterator(IteratorMode::Start);
        for item in iter {
            let (key, value) = item?;
            let key_str = String::from_utf8_lossy(&key);
            
            if let Some(id_str) = key_str.strip_prefix("meta:") {
                if let Ok(id) = id_str.parse::<usize>() {
                    let meta: Meta = bincode::deserialize(&value)
                        .map_err(|e| StorageError::Serialization(format!("Metadata deserialization failed: {}", e)))?;
                    
                    let matches = if require_all {
                        tags.iter().all(|tag| meta.has_tag(tag))
                    } else {
                        tags.iter().any(|tag| meta.has_tag(tag))
                    };
                    
                    if matches {
                        matching_ids.push(id);
                    }
                }
            }
        }
        
        Ok(matching_ids)
    }

    /// Delete a vector by its `id`.
    pub fn delete_vector(&self, id: usize) -> Result<(), StorageError> {
        let key = format!("vec:{}", id);
        self.db.delete(key.as_bytes())?;
        Ok(())
    }

    /// Delete metadata by its `id`.
    pub fn delete_metadata(&self, id: usize) -> Result<(), StorageError> {
        let key = format!("meta:{}", id);
        self.db.delete(key.as_bytes())?;
        Ok(())
    }

    /// Delete both vector and metadata by id
    pub fn delete_complete(&self, id: usize) -> Result<(), StorageError> {
        let mut batch = WriteBatch::default();
        
        let vec_key = format!("vec:{}", id);
        let meta_key = format!("meta:{}", id);
        
        batch.delete(vec_key.as_bytes());
        batch.delete(meta_key.as_bytes());
        
        self.db.write(batch)?;
        Ok(())
    }

    /// List all stored vector IDs.
    pub fn list_ids(&self) -> Result<Vec<usize>, StorageError> {
        let mut ids = Vec::new();
        let iter = self.db.iterator(IteratorMode::Start);
        for item in iter {
            let (key, _) = item?;
            let s = String::from_utf8(key.to_vec())
                .map_err(|e| StorageError::Serialization(format!("Invalid UTF-8 in key: {}", e)))?;
            if let Some(id_str) = s.strip_prefix("vec:") {
                let id = id_str.parse::<usize>()
                    .map_err(|e| StorageError::Serialization(format!("Invalid ID format: {}", e)))?;
                ids.push(id);
            }
        }
        Ok(ids)
    }

    /// List all snapshot names
    pub fn list_snapshots(&self) -> Result<Vec<String>, StorageError> {
        let mut names = Vec::new();
        let iter = self.db.iterator(IteratorMode::Start);
        for item in iter {
            let (key, _) = item?;
            let s = String::from_utf8(key.to_vec())
                .map_err(|e| StorageError::Serialization(format!("Invalid UTF-8 in key: {}", e)))?;
            if let Some(name) = s.strip_prefix("snap:") {
                names.push(name.to_string());
            }
        }
        Ok(names)
    }

    /// Save a raw index snapshot under `snap:<name>` with metadata.
    pub fn save_snapshot(&self, name: &str, bytes: &[u8]) -> Result<(), StorageError> {
        self.save_snapshot_with_info(name, bytes, SnapshotInfo {
            name: name.to_string(),
            created_at: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            size_bytes: bytes.len() as u64,
            vector_count: 0, // Will be filled by caller if needed
            index_type: "unknown".to_string(),
            compression: self.config.compression.clone(),
            checksum: Self::calculate_checksum(bytes),
            metadata: HashMap::new(),
        })
    }

    /// Save snapshot with full metadata
    pub fn save_snapshot_with_info(&self, name: &str, bytes: &[u8], info: SnapshotInfo) -> Result<(), StorageError> {
        let mut batch = WriteBatch::default();
        
        // Save snapshot data
        let data_key = format!("snap:{}", name);
        batch.put(data_key.as_bytes(), bytes);
        
        // Save snapshot metadata
        let info_key = format!("snap-info:{}", name);
        let info_bytes = bincode::serialize(&info)
            .map_err(|e| StorageError::Serialization(format!("Snapshot info serialization failed: {}", e)))?;
        batch.put(info_key.as_bytes(), &info_bytes);
        
        self.db.write(batch)?;
        Ok(())
    }

    /// Load a snapshot by its `name`.
    pub fn load_snapshot(&self, name: &str) -> Result<Vec<u8>, StorageError> {
        let key = format!("snap:{}", name);
        if let Some(data) = self.db.get(key.as_bytes())? {
            Ok(data.to_vec())
        } else {
            Err(StorageError::NotFound(format!("Snapshot '{}' not found", name)))
        }
    }

    /// Load snapshot metadata
    pub fn load_snapshot_info(&self, name: &str) -> Result<SnapshotInfo, StorageError> {
        let key = format!("snap-info:{}", name);
        if let Some(data) = self.db.get(key.as_bytes())? {
            let info: SnapshotInfo = bincode::deserialize(&data)
                .map_err(|e| StorageError::Serialization(format!("Snapshot info deserialization failed: {}", e)))?;
            Ok(info)
        } else {
            Err(StorageError::NotFound(format!("Snapshot info for '{}' not found", name)))
        }
    }

    /// Delete a snapshot by its `name`.
    pub fn delete_snapshot(&self, name: &str) -> Result<(), StorageError> {
        let mut batch = WriteBatch::default();
        
        let data_key = format!("snap:{}", name);
        let info_key = format!("snap-info:{}", name);
        
        batch.delete(data_key.as_bytes());
        batch.delete(info_key.as_bytes());
        
        self.db.write(batch)?;
        Ok(())
    }

    /// Get database size on disk
    pub fn database_size(&self) -> Result<u64, StorageError> {
        if let Ok(Some(size_str)) = self.db.property_value("rocksdb.total-sst-files-size") {
            size_str.parse::<u64>()
                .map_err(|e| StorageError::Serialization(format!("Failed to parse database size: {}", e)))
        } else {
            Ok(0)
        }
    }

    /// Compact database to reclaim space
    pub fn compact(&self) -> Result<(), StorageError> {
        self.db.compact_range::<&[u8], &[u8]>(None, None);
        Ok(())
    }

    /// Create a backup of the database
    pub fn backup(&self, _backup_path: &str) -> Result<(), StorageError> {
        // This would require implementing backup engine
        // For now, return an error indicating it's not implemented
        Err(StorageError::InvalidConfiguration(
            "Backup functionality requires backup engine implementation".to_string()
        ))
    }

    /// Calculate simple checksum for data integrity
    fn calculate_checksum(data: &[u8]) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        data.hash(&mut hasher);
        hasher.finish()
    }

    /// Verify snapshot integrity
    pub fn verify_snapshot(&self, name: &str) -> Result<bool, StorageError> {
        let data = self.load_snapshot(name)?;
        let info = self.load_snapshot_info(name)?;
        
        let calculated_checksum = Self::calculate_checksum(&data);
        Ok(calculated_checksum == info.checksum)
    }
}

// Legacy support for old Meta structure
impl From<HashMap<String, String>> for Meta {
    fn from(data: HashMap<String, String>) -> Self {
        Meta::with_data(data)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core_crate::Vector;
    use std::fs;

    #[test]
    fn enhanced_storage_config() {
        let config = StorageConfig {
            compression: CompressionType::ZSTD,
            cache_size_mb: 512,
            enable_bloom_filter: true,
            ..Default::default()
        };
        
        let path = "_test_config";
        let _ = fs::remove_dir_all(path);
        let storage = Storage::with_config(path, config.clone()).unwrap();
        
        assert_eq!(storage.config().compression, CompressionType::ZSTD);
        assert_eq!(storage.config().cache_size_mb, 512);
        
        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn enhanced_metadata() {
        let path = "_test_enhanced_meta";
        let _ = fs::remove_dir_all(path);
        let storage = Storage::open(path).unwrap();

        let mut meta = Meta::new();
        meta.set("lang".to_string(), "en".to_string());
        meta.add_tag("important".to_string());
        meta.add_tag("test".to_string());

        storage.save_metadata(42, &meta).unwrap();
        let loaded = storage.load_metadata(42).unwrap();
        
        assert_eq!(loaded.get("lang"), Some(&"en".to_string()));
        assert!(loaded.has_tag("important"));
        assert!(loaded.has_tag("test"));
        assert!(!loaded.has_tag("nonexistent"));
        assert_eq!(loaded.version, 4); // incremented by set + 2 add_tag calls (1->2->3->4)

        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn batch_operations() {
        let path = "_test_batch";
        let _ = fs::remove_dir_all(path);
        let storage = Storage::open(path).unwrap();

        let mut batch = VectorBatch::new();
        
        for i in 0..5 {
            let vector = Vector::new(vec![i as f32, (i + 1) as f32]);
            let mut meta = Meta::new();
            meta.set("index".to_string(), i.to_string());
            
            batch.add_vector_with_metadata(i, vector, meta);
        }

        storage.save_batch(&batch).unwrap();

        // Verify all vectors were saved
        for i in 0..5 {
            let vector = storage.load_vector(i).unwrap();
            assert_eq!(vector.raw(), vec![i as f32, (i + 1) as f32]);
            
            let meta = storage.load_metadata(i).unwrap();
            assert_eq!(meta.get("index"), Some(&i.to_string()));
        }

        let _ = fs::remove_dir_all(path);
    }

    #[test]
    fn storage_stats() {
        let path = "_test_stats";
        let _ = fs::remove_dir_all(path);
        let mut storage = Storage::open(path).unwrap();

        // Add some data
        for i in 0..5 {
            let vector = Vector::new(vec![i as f32, 0.0]);
            let meta = Meta::new();
            storage.save_vector(i, &vector).unwrap();
            storage.save_metadata(i, &meta).unwrap();
        }

        storage.save_snapshot("test", &vec![1, 2, 3]).unwrap();

        // Refresh and check stats
        storage.refresh_stats().unwrap();
        let stats = storage.stats();
        
        assert_eq!(stats.total_vectors, 5);
        assert_eq!(stats.total_metadata, 5);
        assert_eq!(stats.total_snapshots, 1);
        assert!(stats.total_writes > 0);

        let _ = fs::remove_dir_all(path);
    }
}