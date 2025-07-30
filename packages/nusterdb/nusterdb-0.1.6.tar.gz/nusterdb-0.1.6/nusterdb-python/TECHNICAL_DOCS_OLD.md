# NusterDB Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Directory Structure](#directory-structure)
5. [Core Components](#core-components)
6. [Features Implementation](#features-implementation)
7. [Execution Flow](#execution-flow)
8. [API Design](#api-design)
9. [Performance Considerations](#performance-considerations)
10. [Testing Strategy](#testing-strategy)

## Overview

NusterDB is a high-performance vector database implemented in Rust with Python bindings using PyO3. It provides efficient similarity search capabilities using multiple indexing algorithms (HNSW and Flat) and supports various distance metrics. The project is designed for machine learning applications, recommendation systems, and any use case requiring fast vector operations.

## Technology Stack

### Core Technologies
- **Rust** (Backend): High-performance systems programming language
  - Memory safety without garbage collection
  - Zero-cost abstractions
  - Excellent concurrency support
  
- **PyO3** (Python Bindings): Rust bindings for Python
  - Seamless integration between Rust and Python
  - Automatic memory management
  - Type conversion between Rust and Python types

### Dependencies

#### Rust Dependencies
```toml
# Core Dependencies
pyo3 = "0.20"           # Python bindings
anyhow = "1.0"          # Error handling
serde = "1.0"           # Serialization
serde_json = "1.0"      # JSON serialization
rocksdb = "0.21"        # Storage engine
hnsw_rs = "0.2"         # HNSW algorithm implementation
bincode = "1.3"         # Binary serialization

# Internal Dependencies
nuster_core             # Vector operations and math
index                   # Indexing algorithms
storage                 # Persistence layer
api                     # Service layer
```

#### Python Dependencies
```toml
numpy = ">=1.19.0"      # Numerical computing (optional)
```

### Build Tools
- **Maturin**: Rust-Python package builder
- **Cargo**: Rust package manager and build system

## Architecture

```
┌─────────────────────────────────────────┐
│            Python Layer                 │
│  ┌─────────────────────────────────────┐ │
│  │        Python API                   │ │
│  │  - NusterDB class                   │ │
│  │  - Vector operations                │ │
│  │  - Configuration classes            │ │
│  └─────────────────────────────────────┘ │
└─────────────────┬───────────────────────┘
                  │ PyO3 Bindings
┌─────────────────▼───────────────────────┐
│             Rust Layer                  │
│  ┌─────────────────────────────────────┐ │
│  │           API Layer                 │ │
│  │  - Service management               │ │
│  │  - Configuration handling           │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │          Index Layer                │ │
│  │  - HNSW implementation              │ │
│  │  - Flat index                       │ │
│  │  - Distance calculations            │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │         Storage Layer               │ │
│  │  - RocksDB persistence              │ │
│  │  - Metadata management              │ │
│  │  - Snapshot functionality           │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │          Core Layer                 │ │
│  │  - Vector mathematics               │ │
│  │  - Distance metrics                 │ │
│  │  - Basic data structures            │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Directory Structure

```
nusterdb-python/                    # Python bindings project root
├── Cargo.toml                      # Rust package configuration
├── pyproject.toml                  # Python package configuration
├── README.md                       # Project documentation
├── LICENSE                         # License file
├── Makefile                        # Build automation
├── .gitignore                      # Git ignore rules
│
├── src/                            # Rust source code
│   └── lib.rs                      # Main PyO3 bindings implementation
│
├── python/                         # Python package
│   └── nusterdb/
│       ├── __init__.py             # Python package initialization
│       └── py.typed                # Type checking marker
│
├── examples_advanced.py            # Advanced usage examples
├── test_advanced.py               # Comprehensive test suite
├── summary.py                     # Feature demonstration
│
└── target/                        # Build artifacts (generated)
    ├── debug/                     # Debug build output
    ├── release/                   # Release build output
    └── wheels/                    # Python wheel packages

../nusterdb/                       # Core Rust implementation
├── Cargo.toml                     # Workspace configuration
├── core/                          # Core mathematics and data structures
│   ├── Cargo.toml
│   └── src/lib.rs                 # Vector operations, distance metrics
├── index/                         # Indexing algorithms
│   ├── Cargo.toml
│   └── src/lib.rs                 # HNSW, Flat index implementations
├── storage/                       # Persistence layer
│   ├── Cargo.toml
│   └── src/lib.rs                 # RocksDB integration, metadata
├── api/                          # Service layer
│   ├── Cargo.toml
│   └── src/lib.rs                # High-level database operations
└── cli/                          # Command-line interface
    ├── Cargo.toml
    └── src/main.rs               # CLI application
```

## Core Components

### 1. Python Bindings (`src/lib.rs`)

The main PyO3 implementation file that exposes Rust functionality to Python:

#### Key Classes:
- **Vector**: Wrapper around core::Vector with all mathematical operations
- **DistanceMetric**: Enum for different distance calculation methods
- **Metadata**: Rich metadata with timestamps, tags, and versioning
- **HNSWConfig**: Configuration for HNSW index parameters
- **FlatIndexConfig**: Configuration for flat index
- **StorageConfiguration**: Storage engine settings
- **DatabaseConfig**: High-level database configuration
- **DatabaseStats**: Database statistics and metrics
- **NusterDB**: Main database interface

#### Implementation Pattern:
```rust
#[pyclass]
pub struct Vector {
    inner: CoreVector,  // Wraps Rust implementation
}

#[pymethods]
impl Vector {
    #[new]
    fn new(data: Vec<f32>) -> PyResult<Self> { ... }
    
    #[getter]
    fn dimension(&self) -> usize { ... }
    
    fn dot(&self, other: &Vector) -> PyResult<f32> { ... }
}
```

### 2. Core Layer (`../nusterdb/core/src/lib.rs`)

Mathematical foundation and basic data structures:

#### Key Components:
- **Vector struct**: N-dimensional float vector with operations
- **DistanceMetric enum**: All supported distance calculations
- **Mathematical operations**: Dot product, norms, normalization, distances

#### Features:
```rust
impl Vector {
    pub fn new(data: Vec<f32>) -> Self
    pub fn zeros(dim: usize) -> Self
    pub fn ones(dim: usize) -> Self
    pub fn random(dim: usize, min: f32, max: f32) -> Self
    pub fn dot(&self, other: &Self) -> f32
    pub fn norm(&self) -> f32
    pub fn l1_norm(&self) -> f32
    pub fn linf_norm(&self) -> f32
    pub fn euclidean_distance(&self, other: &Self) -> f32
    pub fn cosine_similarity(&self, other: &Self) -> f32
    // ... many more operations
}
```

### 3. Index Layer (`../nusterdb/index/src/lib.rs`)

Indexing algorithms for efficient similarity search:

#### HNSW (Hierarchical Navigable Small World):
- Multi-layer graph structure
- Logarithmic search complexity
- Configurable parameters (M, ef_construction, ef_search)

#### Flat Index:
- Brute-force linear search
- Exact results
- Simple and reliable

#### Configuration:
```rust
pub struct IndexConfig {
    pub dim: usize,
    pub distance_metric: DistanceMetric,
    pub index_type: IndexType,
    pub hnsw_config: Option<HnswConfig>,
    pub flat_config: Option<FlatConfig>,
}
```

### 4. Storage Layer (`../nusterdb/storage/src/lib.rs`)

Persistence and metadata management:

#### Key Features:
- **RocksDB integration**: High-performance key-value storage
- **Metadata system**: Rich metadata with timestamps and versioning
- **Compression**: Multiple compression algorithms (LZ4, Snappy, ZSTD)
- **Snapshots**: Database backup and versioning

#### Metadata Structure:
```rust
pub struct Meta {
    pub data: HashMap<String, String>,
    pub created_at: u64,
    pub updated_at: u64,
    pub version: u32,
    pub tags: Vec<String>,
}
```

### 5. API Layer (`../nusterdb/api/src/lib.rs`)

High-level database operations and service management:

#### Service Interface:
```rust
pub struct Service {
    // Database operations
    pub fn add(&mut self, id: u64, vector: Vector, metadata: Option<Meta>) -> Result<()>
    pub fn search(&self, query: Vector, k: usize) -> Result<Vec<(u64, f32)>>
    pub fn remove(&mut self, id: u64) -> Result<bool>
    pub fn get(&self, id: u64) -> Result<Option<(Vector, Meta)>>
    
    // Management operations
    pub fn create_snapshot(&self, name: Option<String>) -> Result<String>
    pub fn list_snapshots(&self) -> Result<Vec<String>>
    pub fn stats(&self) -> Result<DatabaseStats>
}
```

## Features Implementation

### 1. Vector Operations

All vector mathematical operations are implemented in the core layer and exposed through PyO3:

```python
# Vector creation
v1 = nusterdb.Vector([1.0, 2.0, 3.0])
v2 = nusterdb.Vector.zeros(3)
v3 = nusterdb.Vector.ones(3)
v4 = nusterdb.Vector.random(3, -1.0, 1.0)

# Mathematical operations
dot_product = v1.dot(v2)
distance = v1.euclidean_distance(v2)
norm = v1.norm()
normalized = v1.normalize()
```

### 2. Distance Metrics

Seven distance metrics are supported:

```python
euclidean = nusterdb.DistanceMetric.euclidean()
manhattan = nusterdb.DistanceMetric.manhattan()
cosine = nusterdb.DistanceMetric.cosine()
angular = nusterdb.DistanceMetric.angular()
chebyshev = nusterdb.DistanceMetric.chebyshev()
jaccard = nusterdb.DistanceMetric.jaccard()
hamming = nusterdb.DistanceMetric.hamming()

distance = euclidean.distance(v1, v2)
similarity = euclidean.similarity(v1, v2)
```

### 3. Metadata System

Rich metadata with automatic timestamping and versioning:

```python
meta = nusterdb.Metadata()
meta.set("category", "image")
meta.set("format", "jpg")
meta.add_tag("processed")
meta.add_tag("high-res")

# Automatic timestamps and versioning
print(f"Created: {meta.created_at}")
print(f"Version: {meta.version}")
print(f"Tags: {meta.tags()}")
```

### 4. Index Configuration

Flexible configuration for different use cases:

```python
# HNSW for fast approximate search
hnsw_config = nusterdb.HNSWConfig(
    max_nb_connection=32,
    ef_construction=400,
    max_nb_elements=10000
)

# Database configuration
config = nusterdb.DatabaseConfig(
    dim=128,
    index_type="hnsw",
    distance_metric=nusterdb.DistanceMetric.cosine(),
    hnsw_config=hnsw_config
)
```

### 5. Storage Configuration

Advanced storage options:

```python
storage_config = nusterdb.StorageConfiguration(
    cache_size_mb=512,
    compression="lz4",
    enable_bloom_filter=True,
    bloom_filter_bits_per_key=10
)
```

## Execution Flow

### 1. Database Initialization

```
Python: NusterDB("path", dim=128)
    ↓
PyO3: Create Service with configuration
    ↓
Rust API: Initialize storage and index
    ↓
Storage: Open RocksDB database
    ↓
Index: Load or create index structure
```

### 2. Vector Addition

```
Python: db.add(id, vector, metadata)
    ↓
PyO3: Convert Python types to Rust
    ↓
API: Service.add(id, vector, metadata)
    ↓
Storage: Store vector and metadata in RocksDB
    ↓
Index: Add vector to search index
    ↓
Result: Return success/error to Python
```

### 3. Vector Search

```
Python: db.search(query_vector, k=10)
    ↓
PyO3: Convert query vector to Rust
    ↓
API: Service.search(query, k)
    ↓
Index: Find k nearest neighbors
    ↓
Storage: Retrieve metadata for results
    ↓
PyO3: Convert results back to Python
    ↓
Python: Return list of (id, distance) tuples
```

### 4. Snapshot Creation

```
Python: db.create_snapshot("backup_v1")
    ↓
API: Service.create_snapshot(name)
    ↓
Storage: Create RocksDB snapshot
    ↓
Index: Serialize index state
    ↓
Storage: Save snapshot metadata
    ↓
Result: Return snapshot name to Python
```

## API Design

### Design Principles

1. **Pythonic Interface**: Natural Python syntax and conventions
2. **Type Safety**: PyO3 provides automatic type checking
3. **Error Handling**: Comprehensive error propagation from Rust to Python
4. **Performance**: Zero-copy operations where possible
5. **Memory Safety**: Rust's ownership system prevents memory leaks

### Error Handling Pattern

```rust
fn add(&mut self, id: u64, vector: &Vector, metadata: Option<&Metadata>) -> PyResult<()> {
    match self.service.add(id, vector.inner.clone(), metadata.map(|m| m.inner.clone())) {
        Ok(_) => Ok(()),
        Err(e) => Err(PyRuntimeError::new_err(format!("Failed to add vector: {}", e))),
    }
}
```

### Property Getters

All classes expose their internal state through properties:

```rust
#[getter]
fn dimension(&self) -> usize {
    self.inner.dim()
}

#[getter]
fn vector_count(&self) -> usize {
    self.vector_count
}
```

## Performance Considerations

### 1. Memory Management
- **Zero-copy operations**: Direct memory access where possible
- **Reference counting**: PyO3 handles Python reference counting
- **Rust ownership**: Prevents memory leaks and data races

### 2. Computational Efficiency
- **SIMD optimizations**: Rust compiler optimizations for vector operations
- **Efficient algorithms**: HNSW for logarithmic search complexity
- **Minimal allocations**: Reuse of memory where possible

### 3. Storage Optimization
- **Compression**: Multiple compression algorithms available
- **Bloom filters**: Fast negative lookups
- **Write batching**: Efficient batch operations

### 4. Concurrency
- **Thread safety**: Rust's ownership system ensures thread safety
- **Async support**: Future extension point for async operations
- **Lock-free operations**: Where possible, avoid locking

## Testing Strategy

### 1. Unit Tests (`test_advanced.py`)

Comprehensive testing of all features:

```python
def test_vector_operations():
    """Test all vector mathematical operations"""
    
def test_distance_metrics():
    """Test all distance metric calculations"""
    
def test_metadata_operations():
    """Test metadata management"""
    
def test_database_operations():
    """Test CRUD operations"""
    
def test_configuration():
    """Test all configuration options"""
```

### 2. Integration Tests

Real-world usage scenarios:

```python
def test_large_dataset():
    """Test with large number of vectors"""
    
def test_persistence():
    """Test database persistence across restarts"""
    
def test_snapshots():
    """Test snapshot functionality"""
```

### 3. Performance Tests

Benchmark critical operations:

```python
def benchmark_search_performance():
    """Measure search speed with different configurations"""
    
def benchmark_insertion_speed():
    """Measure vector insertion performance"""
```

### 4. Error Handling Tests

Verify proper error propagation:

```python
def test_error_conditions():
    """Test various error conditions"""
    
def test_validation():
    """Test input validation"""
```

This technical documentation provides a complete understanding of the NusterDB project architecture, implementation details, and execution flow. The modular design and clear separation of concerns make it maintainable and extensible for future enhancements.
