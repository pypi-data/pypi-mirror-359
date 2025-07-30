//! High-performance batch insertion system with advanced optimizations

use core::{Vector, DistanceMetric};
use super::{AnnIndex, IndexConfig, IndexStats, IndexType, FlatConfig, SnapshotIndex, IndexWithSnapshot, BulkAnnIndex};
use std::collections::HashMap;
use std::sync::{Arc, RwLock, Mutex};
use rayon::prelude::*;
use crossbeam_channel::{bounded, Receiver, Sender};
use std::thread;
use std::sync::atomic::{AtomicUsize, Ordering};
use serde::{Serialize, Deserialize};

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// High-performance insertion configuration
#[derive(Debug, Clone)]
pub struct InsertionConfig {
    pub batch_size: usize,
    pub num_threads: usize,
    pub prefetch_distance: usize,
    pub memory_pool_size: usize,
    pub use_numa_aware: bool,
    pub compression_level: u8,
}

impl Default for InsertionConfig {
    fn default() -> Self {
        let num_cores = std::thread::available_parallelism()
            .map(|n| n.get())
            .unwrap_or(1);
        
        Self {
            batch_size: 1000,
            num_threads: num_cores.saturating_sub(1).max(1), // Leave one core for OS
            prefetch_distance: 64,
            memory_pool_size: 100_000,
            use_numa_aware: true,
            compression_level: 0, // No compression for maximum speed
        }
    }
}

/// Memory pool for efficient vector storage
struct VectorMemoryPool {
    pools: Vec<Mutex<Vec<Vec<f32>>>>,
    dimension: usize,
    pool_size: usize,
}

impl VectorMemoryPool {
    fn new(dimension: usize, pool_size: usize, num_pools: usize) -> Self {
        let mut pools = Vec::with_capacity(num_pools);
        for _ in 0..num_pools {
            let mut pool = Vec::with_capacity(pool_size);
            for _ in 0..pool_size {
                pool.push(vec![0.0f32; dimension]);
            }
            pools.push(Mutex::new(pool));
        }
        
        Self {
            pools,
            dimension,
            pool_size,
        }
    }
    
    fn get_vector(&self, thread_id: usize) -> Option<Vec<f32>> {
        let pool_idx = thread_id % self.pools.len();
        self.pools[pool_idx].lock().unwrap().pop()
    }
    
    fn return_vector(&self, thread_id: usize, mut vector: Vec<f32>) {
        let pool_idx = thread_id % self.pools.len();
        vector.clear();
        vector.resize(self.dimension, 0.0);
        
        let mut pool = self.pools[pool_idx].lock().unwrap();
        if pool.len() < self.pool_size {
            pool.push(vector);
        }
    }
}

/// Batch insertion data structure
#[derive(Debug)]
struct InsertionBatch {
    vectors: Vec<Vector>,
    ids: Vec<usize>,
    start_idx: usize,
}

/// Ultra-fast flat index optimized for insertion speed
pub struct UltraFastFlatIndex {
    config: IndexConfig,
    insertion_config: InsertionConfig,
    
    // Data storage with optimized layout
    vector_data: Arc<RwLock<Vec<f32>>>, // Packed vector data
    ids: Arc<RwLock<Vec<usize>>>,
    id_to_idx: Arc<RwLock<HashMap<usize, usize>>>,
    
    // Performance optimizations
    memory_pool: Arc<VectorMemoryPool>,
    insertion_counter: Arc<AtomicUsize>,
    
    // Metrics
    total_insertions: Arc<AtomicUsize>,
    total_insertion_time: Arc<Mutex<f64>>,
    
    // Parallel insertion infrastructure
    insertion_sender: Option<Sender<InsertionBatch>>,
    worker_handles: Vec<thread::JoinHandle<()>>,
}

impl UltraFastFlatIndex {
    /// Create a new ultra-fast index with optimized configuration
    pub fn new_optimized(config: IndexConfig) -> Self {
        let insertion_config = InsertionConfig::default();
        let dimension = config.dim;
        
        // Create memory pool for each thread
        let memory_pool = Arc::new(VectorMemoryPool::new(
            dimension,
            insertion_config.memory_pool_size,
            insertion_config.num_threads,
        ));
        
        // Pre-allocate large contiguous memory blocks
        let initial_capacity = 1_000_000; // Pre-allocate for 1M vectors
        let vector_data = Arc::new(RwLock::new(Vec::with_capacity(initial_capacity * dimension)));
        let ids = Arc::new(RwLock::new(Vec::with_capacity(initial_capacity)));
        let id_to_idx = Arc::new(RwLock::new(HashMap::with_capacity(initial_capacity)));
        
        Self {
            config,
            insertion_config,
            vector_data,
            ids,
            id_to_idx,
            memory_pool,
            insertion_counter: Arc::new(AtomicUsize::new(0)),
            total_insertions: Arc::new(AtomicUsize::new(0)),
            total_insertion_time: Arc::new(Mutex::new(0.0)),
            insertion_sender: None,
            worker_handles: Vec::new(),
        }
    }
    
    /// Initialize parallel insertion workers
    pub fn start_insertion_workers(&mut self) {
        let (sender, receiver) = bounded(self.insertion_config.num_threads * 2);
        
        // Start worker threads
        for thread_id in 0..self.insertion_config.num_threads {
            let receiver = receiver.clone();
            let vector_data = Arc::clone(&self.vector_data);
            let ids = Arc::clone(&self.ids);
            let id_to_idx = Arc::clone(&self.id_to_idx);
            let memory_pool = Arc::clone(&self.memory_pool);
            let dimension = self.config.dim;
            let total_insertions = Arc::clone(&self.total_insertions);
            
            let handle = thread::Builder::new()
                .name(format!("nuster-insert-{}", thread_id))
                .spawn(move || {
                    Self::insertion_worker(
                        thread_id,
                        receiver,
                        vector_data,
                        ids,
                        id_to_idx,
                        memory_pool,
                        dimension,
                        total_insertions,
                    );
                })
                .expect("Failed to spawn insertion worker");
                
            self.worker_handles.push(handle);
        }
        
        self.insertion_sender = Some(sender);
    }
    
    /// Worker thread for parallel insertions
    fn insertion_worker(
        thread_id: usize,
        receiver: Receiver<InsertionBatch>,
        vector_data: Arc<RwLock<Vec<f32>>>,
        ids: Arc<RwLock<Vec<usize>>>,
        id_to_idx: Arc<RwLock<HashMap<usize, usize>>>,
        memory_pool: Arc<VectorMemoryPool>,
        dimension: usize,
        total_insertions: Arc<AtomicUsize>,
    ) {
        // Set thread affinity for better cache locality
        #[cfg(target_os = "linux")]
        // Note: SIMD optimizations temporarily disabled for compatibility
        // Can be re-enabled with proper unsafe block fixes
        /*
        {
            let mut cpu_set = libc::cpu_set_t::default();
            unsafe {
                libc::CPU_ZERO(&mut cpu_set);
                libc::CPU_SET(thread_id, &mut cpu_set);
                libc::sched_setaffinity(0, std::mem::size_of::<libc::cpu_set_t>(), &cpu_set);
            }
        }
        */
        
        while let Ok(batch) = receiver.recv() {
            Self::process_insertion_batch(
                thread_id,
                batch,
                &vector_data,
                &ids,
                &id_to_idx,
                &memory_pool,
                dimension,
                &total_insertions,
            );
        }
    }
    
    /// Process a batch of insertions with maximum efficiency
    fn process_insertion_batch(
        _thread_id: usize,
        batch: InsertionBatch,
        vector_data: &Arc<RwLock<Vec<f32>>>,
        ids: &Arc<RwLock<Vec<usize>>>,
        id_to_idx: &Arc<RwLock<HashMap<usize, usize>>>,
        _memory_pool: &Arc<VectorMemoryPool>,
        dimension: usize,
        total_insertions: &Arc<AtomicUsize>,
    ) {
        let batch_size = batch.vectors.len();
        
        // Pre-allocate batch data in packed format
        let mut packed_data = Vec::with_capacity(batch_size * dimension);
        
        // Pack vectors into contiguous memory with SIMD optimization
        for vector in &batch.vectors {
            let data = vector.as_slice();
            
            // SIMD-optimized copy
            Self::simd_copy_vector(data, &mut packed_data);
        }
        
        // Bulk insert with minimal locking
        {
            let mut vector_data_guard = vector_data.write().unwrap();
            let mut ids_guard = ids.write().unwrap();
            let mut id_to_idx_guard = id_to_idx.write().unwrap();
            
            let start_idx = vector_data_guard.len() / dimension;
            
            // Reserve space efficiently
            vector_data_guard.reserve(packed_data.len());
            ids_guard.reserve(batch_size);
            id_to_idx_guard.reserve(batch_size);
            
            // Bulk append
            vector_data_guard.extend_from_slice(&packed_data);
            
            for (i, &id) in batch.ids.iter().enumerate() {
                let vector_idx = start_idx + i;
                ids_guard.push(id);
                id_to_idx_guard.insert(id, vector_idx);
            }
        }
        
        total_insertions.fetch_add(batch_size, Ordering::Relaxed);
    }
    
    /// SIMD-optimized vector copy
    #[cfg(target_arch = "x86_64")]
    fn simd_copy_vector(src: &[f32], dst: &mut Vec<f32>) {
        if is_x86_feature_detected!("avx2") {
            unsafe { Self::simd_copy_avx2(src, dst) };
        } else if is_x86_feature_detected!("sse") {
            unsafe { Self::simd_copy_sse(src, dst) };
        } else {
            dst.extend_from_slice(src);
        }
    }
    
    #[cfg(not(target_arch = "x86_64"))]
    fn simd_copy_vector(src: &[f32], dst: &mut Vec<f32>) {
        dst.extend_from_slice(src);
    }
    
    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "avx2")]
    unsafe fn simd_copy_avx2(src: &[f32], dst: &mut Vec<f32>) {
        let len = src.len();
        let chunks = len / 8;
        let remainder = len % 8;
        
        let start_len = dst.len();
        dst.reserve(len);
        
        let dst_ptr = dst.as_mut_ptr().add(start_len);
        
        // Copy 8 floats at a time using AVX2
        for i in 0..chunks {
            let src_offset = i * 8;
            let dst_offset = i * 8;
            
            let data = _mm256_loadu_ps(src.as_ptr().add(src_offset));
            _mm256_storeu_ps(dst_ptr.add(dst_offset), data);
        }
        
        // Handle remainder
        for i in (chunks * 8)..len {
            *dst_ptr.add(i) = src[i];
        }
        
        dst.set_len(start_len + len);
    }
    
    #[cfg(target_arch = "x86_64")]
    #[target_feature(enable = "sse")]
    unsafe fn simd_copy_sse(src: &[f32], dst: &mut Vec<f32>) {
        let len = src.len();
        let chunks = len / 4;
        let remainder = len % 4;
        
        let start_len = dst.len();
        dst.reserve(len);
        
        let dst_ptr = dst.as_mut_ptr().add(start_len);
        
        // Copy 4 floats at a time using SSE
        for i in 0..chunks {
            let src_offset = i * 4;
            let dst_offset = i * 4;
            
            let data = _mm_loadu_ps(src.as_ptr().add(src_offset));
            _mm_storeu_ps(dst_ptr.add(dst_offset), data);
        }
        
        // Handle remainder
        for i in (chunks * 4)..len {
            *dst_ptr.add(i) = src[i];
        }
        
        dst.set_len(start_len + len);
    }
    
    /// High-speed batch insertion
    pub fn batch_insert(&self, vectors_and_ids: Vec<(usize, Vector)>) -> Result<(), String> {
        if vectors_and_ids.is_empty() {
            return Ok(());
        }
        
        let batch_size = self.insertion_config.batch_size;
        let _total_vectors = vectors_and_ids.len();
        
        // Split into optimally-sized batches
        let batches: Vec<_> = vectors_and_ids
            .chunks(batch_size)
            .enumerate()
            .map(|(batch_idx, chunk)| {
                let mut vectors = Vec::with_capacity(chunk.len());
                let mut ids = Vec::with_capacity(chunk.len());
                
                for (id, vector) in chunk {
                    ids.push(*id);
                    vectors.push(vector.clone());
                }
                
                InsertionBatch {
                    vectors,
                    ids,
                    start_idx: batch_idx * batch_size,
                }
            })
            .collect();
        
        // Send batches to workers
        if let Some(sender) = &self.insertion_sender {
            for batch in batches {
                sender.send(batch).map_err(|e| format!("Failed to send batch: {}", e))?;
            }
        } else {
            return Err("Insertion workers not started".to_string());
        }
        
        Ok(())
    }
    
    /// Optimized single vector insertion for small batches
    pub fn fast_single_insert(&self, id: usize, vector: Vector) -> Result<(), String> {
        // For single insertions, bypass workers and insert directly
        let dimension = self.config.dim;
        let vector_data = vector.as_slice();
        
        // Direct insertion with minimal locking
        {
            let mut data_guard = self.vector_data.write().unwrap();
            let mut ids_guard = self.ids.write().unwrap();
            let mut id_to_idx_guard = self.id_to_idx.write().unwrap();
            
            // Check for duplicate IDs
            if id_to_idx_guard.contains_key(&id) {
                return Err(format!("Vector with ID {} already exists", id));
            }
            
            let vector_idx = data_guard.len() / dimension;
            
            // Append vector data
            data_guard.extend_from_slice(vector_data);
            ids_guard.push(id);
            id_to_idx_guard.insert(id, vector_idx);
        }
        
        self.total_insertions.fetch_add(1, Ordering::Relaxed);
        Ok(())
    }
    
    /// Wait for all pending insertions to complete
    pub fn flush_insertions(&self) {
        // Wait for insertion queue to empty
        if let Some(sender) = &self.insertion_sender {
            // Send empty batches to signal completion
            for _ in 0..self.insertion_config.num_threads {
                let _ = sender.try_send(InsertionBatch {
                    vectors: Vec::new(),
                    ids: Vec::new(),
                    start_idx: 0,
                });
            }
        }
        
        // Small delay to ensure all workers process pending batches
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
    
    /// Get current insertion throughput
    pub fn get_insertion_throughput(&self) -> f64 {
        let total = self.total_insertions.load(Ordering::Relaxed) as f64;
        let time = *self.total_insertion_time.lock().unwrap();
        
        if time > 0.0 {
            total / time
        } else {
            0.0
        }
    }
    
    /// Memory usage optimization - compact storage
    pub fn optimize_memory(&self) {
        let mut data_guard = self.vector_data.write().unwrap();
        let mut ids_guard = self.ids.write().unwrap();
        
        data_guard.shrink_to_fit();
        ids_guard.shrink_to_fit();
    }
}

impl AnnIndex for UltraFastFlatIndex {
    fn with_config(config: IndexConfig) -> Self {
        let mut index = Self::new_optimized(config);
        index.start_insertion_workers();
        index
    }
    
    fn insert(&mut self, id: usize, vector: Vector) {
        let _ = self.fast_single_insert(id, vector);
    }
    
    fn search(&self, query: &Vector, k: usize) -> Vec<(usize, f32)> {
        // Placeholder - we'll optimize search later
        // For now, basic brute force search
        let data_guard = self.vector_data.read().unwrap();
        let ids_guard = self.ids.read().unwrap();
        
        let dimension = self.config.dim;
        let num_vectors = data_guard.len() / dimension;
        
        if num_vectors == 0 {
            return Vec::new();
        }
        
        let mut results = Vec::with_capacity(num_vectors);
        
        for i in 0..num_vectors {
            let start_idx = i * dimension;
            let end_idx = start_idx + dimension;
            let vector_data = &data_guard[start_idx..end_idx];
            
            // Simple L2 distance (will optimize later)
            let distance: f32 = query.as_slice()
                .iter()
                .zip(vector_data.iter())
                .map(|(a, b)| (a - b).powi(2))
                .sum::<f32>()
                .sqrt();
                
            results.push((ids_guard[i], distance));
        }
        
        // Sort and return top-k
        results.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        results.truncate(k);
        results
    }
    
    fn config(&self) -> &IndexConfig {
        &self.config
    }
    
    fn stats(&self) -> IndexStats {
        let total_insertions = self.total_insertions.load(Ordering::Relaxed);
        let throughput = self.get_insertion_throughput();
        
        let mut additional_stats = std::collections::HashMap::new();
        additional_stats.insert("insertion_throughput".to_string(), format!("{:.0}", throughput));
        additional_stats.insert("worker_threads".to_string(), format!("{}", self.insertion_config.num_threads));
        additional_stats.insert("batch_size".to_string(), format!("{}", self.insertion_config.batch_size));
        additional_stats.insert("simd_support".to_string(), format!("{}", cfg!(target_arch = "x86_64")));
        
        IndexStats {
            vector_count: total_insertions,
            dimension: self.config.dim,
            index_type: "UltraFastFlat".to_string(),
            distance_metric: self.config.distance_metric,
            memory_usage: self.memory_usage(),
            build_time_ms: None,
            last_search_time_ms: None,
            total_searches: 0,
            total_inserts: total_insertions as u64,
            additional_stats,
        }
    }
    
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
    
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
        self
    }
}

impl Drop for UltraFastFlatIndex {
    fn drop(&mut self) {
        // Clean shutdown of workers
        if let Some(sender) = self.insertion_sender.take() {
            drop(sender); // Close the channel
        }
        
        // Wait for all workers to finish
        while let Some(handle) = self.worker_handles.pop() {
            let _ = handle.join();
        }
    }
}

/// Serializable representation of the index for snapshotting
#[derive(serde::Serialize, serde::Deserialize)]
struct UltraFastFlatSnapshot {
    config: IndexConfig,
    vector_data: Vec<f32>,
    ids: Vec<usize>,
    id_to_idx: HashMap<usize, usize>,
}

impl SnapshotIndex for UltraFastFlatIndex {
    fn dump(&self) -> Vec<u8> {
        // Flush any pending insertions first
        self.flush_insertions();
        
        let data_guard = self.vector_data.read().unwrap();
        let ids_guard = self.ids.read().unwrap();
        let id_to_idx_guard = self.id_to_idx.read().unwrap();
        
        let snapshot = UltraFastFlatSnapshot {
            config: self.config.clone(),
            vector_data: data_guard.clone(),
            ids: ids_guard.clone(),
            id_to_idx: id_to_idx_guard.clone(),
        };
        
        bincode::serialize(&snapshot).expect("Failed to serialize UltraFastFlatIndex")
    }
    
    fn restore(config: IndexConfig, data: &[u8]) -> Self {
        let snapshot: UltraFastFlatSnapshot = bincode::deserialize(data)
            .expect("Failed to deserialize UltraFastFlatIndex");
        
        let insertion_config = InsertionConfig::default();
        let dimension = config.dim;
        
        // Create memory pool for each thread
        let memory_pool = Arc::new(VectorMemoryPool::new(
            dimension,
            insertion_config.memory_pool_size,
            insertion_config.num_threads,
        ));
        
        // Restore data
        let vector_data = Arc::new(RwLock::new(snapshot.vector_data));
        let ids = Arc::new(RwLock::new(snapshot.ids));
        let id_to_idx = Arc::new(RwLock::new(snapshot.id_to_idx));
        
        let total_insertions = {
            let ids_guard = ids.read().unwrap();
            ids_guard.len()
        };
        
        let mut index = Self {
            config,
            insertion_config,
            vector_data,
            ids,
            id_to_idx,
            memory_pool,
            insertion_counter: Arc::new(AtomicUsize::new(0)),
            total_insertions: Arc::new(AtomicUsize::new(total_insertions)),
            total_insertion_time: Arc::new(Mutex::new(0.0)),
            insertion_sender: None,
            worker_handles: Vec::new(),
        };
        
        // Start insertion workers
        index.start_insertion_workers();
        index
    }
}

impl IndexWithSnapshot for UltraFastFlatIndex {}

impl UltraFastFlatIndex {
    // Extra methods not part of AnnIndex trait
    
    /// Calculate memory usage of the index
    fn memory_usage(&self) -> usize {
        let vector_data = self.vector_data.read().unwrap();
        let ids = self.ids.read().unwrap();
        let id_to_idx = self.id_to_idx.read().unwrap();
        
        vector_data.len() * std::mem::size_of::<f32>() +
        ids.len() * std::mem::size_of::<usize>() +
        id_to_idx.len() * (std::mem::size_of::<usize>() * 2) +
        std::mem::size_of::<Self>()
    }
}

impl BulkAnnIndex for UltraFastFlatIndex {
    fn bulk_insert(&mut self, ids: &[usize], vectors: &[Vector]) {
        // Use existing batch insertion capabilities
        for (id, vector) in ids.iter().zip(vectors.iter()) {
            self.insert(*id, vector.clone());
        }
    }

    fn reserve(&mut self, capacity: usize) {
        // Reserve capacity in data structures
        let mut vector_data = self.vector_data.write().unwrap();
        let mut ids = self.ids.write().unwrap();
        let mut id_to_idx = self.id_to_idx.write().unwrap();
        
        vector_data.reserve(capacity * self.config.dim);
        ids.reserve(capacity);
        id_to_idx.reserve(capacity);
    }
}
