# NusterDB Technical Documentation

## Overview

NusterDB is a high-performance vector database designed for similarity search and retrieval applications. It provides advanced indexing algorithms, multiple distance metrics, and enterprise-grade features optimized for machine learning and AI workloads.

## Table of Contents

1. [Installation](#installation)
2. [Core Classes](#core-classes)
3. [Vector Operations](#vector-operations)
4. [Distance Metrics](#distance-metrics)
5. [Database Configuration](#database-configuration)
6. [Index Types](#index-types)
7. [Storage Configuration](#storage-configuration)
8. [Database Operations](#database-operations)
9. [Metadata Management](#metadata-management)
10. [Bulk Operations](#bulk-operations)
11. [Search and Retrieval](#search-and-retrieval)
12. [Snapshots and Persistence](#snapshots-and-persistence)
13. [Performance Optimization](#performance-optimization)
14. [Advanced Usage](#advanced-usage)
15. [Examples](#examples)

---

## Installation

```bash
pip install nusterdb==0.1.3
```

**Platform Support:**
- Linux (x86_64, aarch64)
- macOS (Intel, Apple Silicon)
- Windows (x86_64)
- Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

---

## Core Classes

### Vector

The `Vector` class represents a multi-dimensional vector with advanced mathematical operations.

#### Constructor

```python
from nusterdb import Vector

# Create from list
vector = Vector([1.0, 2.0, 3.0, 4.0])

# Create from numpy array
import numpy as np
array = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
vector = Vector(array.tolist())
```

#### Static Methods

```python
# Create zero vector
zeros = Vector.zeros(dim=128)

# Create vector of ones  
ones = Vector.ones(dim=128)

# Create random vector with values in range [min, max]
random_vec = Vector.random(dim=128, min=-1.0, max=1.0)

# Create unit random vector (normalized to length 1)
unit_vec = Vector.unit_random(dim=128)
```

#### Properties

```python
vector = Vector([1.0, 2.0, 3.0])

# Get dimension
dim = vector.dimension  # Returns: 3

# Get raw data as list
data = vector.data  # Returns: [1.0, 2.0, 3.0]

# Get dimension (alternative)
dim = vector.dim()  # Returns: 3
dim = len(vector)   # Returns: 3
```

#### Mathematical Operations

```python
v1 = Vector([1.0, 2.0, 3.0])
v2 = Vector([4.0, 5.0, 6.0])

# Dot product
dot_product = v1.dot(v2)  # Returns: 32.0

# Norms
l1_norm = v1.l1_norm()        # Manhattan norm: 6.0
l2_norm = v1.norm()           # Euclidean norm: 3.74...
linf_norm = v1.linf_norm()    # Max norm: 3.0
norm_sq = v1.norm_squared()   # Squared L2 norm: 14.0

# Normalization
normalized = v1.normalize()          # Returns new normalized vector
v1.normalize_mut()                   # Normalizes in-place
is_norm = v1.is_normalized()         # Check if normalized
is_norm_tol = v1.is_normalized(1e-6) # Check with tolerance

# Validation
is_finite = v1.is_finite()  # Check for NaN/Inf values
```

#### Distance and Similarity Methods

```python
v1 = Vector([1.0, 2.0, 3.0])
v2 = Vector([4.0, 5.0, 6.0])

# Distance metrics
euclidean = v1.euclidean_distance(v2)   # L2 distance
manhattan = v1.manhattan_distance(v2)   # L1 distance  
cosine_dist = v1.cosine_distance(v2)    # Cosine distance
angular = v1.angular_distance(v2)       # Angular distance
chebyshev = v1.chebyshev_distance(v2)   # Chebyshev distance
hamming = v1.hamming_distance(v2)       # Hamming distance
jaccard = v1.jaccard_similarity(v2)     # Jaccard similarity

# Similarity metrics
cosine_sim = v1.cosine_similarity(v2)   # Cosine similarity
```

---

## Distance Metrics

The `DistanceMetric` class provides standardized distance calculations.

#### Available Metrics

```python
from nusterdb import DistanceMetric

# Create distance metric instances
euclidean = DistanceMetric.euclidean()    # L2 distance
manhattan = DistanceMetric.manhattan()    # L1 distance
cosine = DistanceMetric.cosine()          # Cosine distance
angular = DistanceMetric.angular()        # Angular distance
chebyshev = DistanceMetric.chebyshev()    # Chebyshev distance
jaccard = DistanceMetric.jaccard()        # Jaccard distance
hamming = DistanceMetric.hamming()        # Hamming distance
```

#### Usage

```python
metric = DistanceMetric.euclidean()
v1 = Vector([1.0, 2.0, 3.0])
v2 = Vector([4.0, 5.0, 6.0])

# Calculate distance
distance = metric.distance(v1, v2)

# Calculate similarity  
similarity = metric.similarity(v1, v2)
```

---

## Database Configuration

### DatabaseConfig

Main configuration class for creating NusterDB instances.

#### Constructor

```python
from nusterdb import DatabaseConfig, DistanceMetric, HNSWConfig

config = DatabaseConfig(
    dim=128,                                    # Vector dimension (required)
    index_type="hnsw",                         # Index type: "flat", "hnsw", "optimized-flat", "ultra-fast-flat", "super-optimized-flat"
    distance_metric=DistanceMetric.euclidean(), # Distance metric (optional, default: euclidean)
    hnsw_config=HNSWConfig(),                  # HNSW configuration (optional)
    auto_snapshot=False,                       # Enable automatic snapshots
    snapshot_interval_secs=3600                # Snapshot interval in seconds
)
```

#### Static Factory Methods

```python
# Simple configuration
config = DatabaseConfig.simple(dim=128, use_hnsw=True)

# Optimized flat index
config = DatabaseConfig.optimized_flat(dim=128)

# Ultra fast flat index
config = DatabaseConfig.ultra_fast_flat(dim=128)

# Super optimized flat index  
config = DatabaseConfig.super_optimized_flat(dim=128)
```

### HNSWConfig

Configuration for Hierarchical Navigable Small World (HNSW) index.

#### Constructor

```python
from nusterdb import HNSWConfig

hnsw_config = HNSWConfig(
    max_nb_connection=16,     # Maximum connections per node (M parameter)
    max_nb_elements=1024,     # Maximum number of elements
    max_layer=16,             # Maximum number of layers
    ef_construction=200,      # Size of dynamic candidate list during construction
    ef_search=None,           # Size of dynamic candidate list during search (optional)
    use_heuristic=True        # Use heuristic for link selection
)

# Default configuration
hnsw_config = HNSWConfig.default()
```

#### Properties

```python
config = HNSWConfig()

# Access properties
m = config.max_nb_connection      # 16
elements = config.max_nb_elements # 1024
layers = config.max_layer         # 16
ef_c = config.ef_construction     # 200
ef_s = config.ef_search          # None
heuristic = config.use_heuristic  # True
```

---

## Index Types

NusterDB supports multiple index types optimized for different use cases:

### 1. Flat Index
- **Use case**: Exact search, small datasets (< 10K vectors)
- **Complexity**: O(n) search time
- **Memory**: Low
- **Accuracy**: 100% (exact)

```python
config = DatabaseConfig.simple(dim=128, use_hnsw=False)
```

### 2. HNSW Index
- **Use case**: Approximate search, large datasets (> 10K vectors)
- **Complexity**: O(log n) search time  
- **Memory**: Higher
- **Accuracy**: 95-99% (configurable)

```python
hnsw_config = HNSWConfig(max_nb_connection=16, ef_construction=200)
config = DatabaseConfig(dim=128, index_type="hnsw", hnsw_config=hnsw_config)
```

### 3. Optimized Flat Index
- **Use case**: Medium datasets with SIMD optimization
- **Complexity**: O(n) with SIMD acceleration
- **Memory**: Low
- **Accuracy**: 100% (exact)

```python
config = DatabaseConfig.optimized_flat(dim=128)
```

### 4. Ultra Fast Flat Index
- **Use case**: High-performance exact search with memory optimization
- **Complexity**: O(n) with advanced optimizations
- **Memory**: Optimized
- **Accuracy**: 100% (exact)

```python
config = DatabaseConfig.ultra_fast_flat(dim=128)
```

### 5. Super Optimized Flat Index
- **Use case**: Maximum performance for exact search
- **Complexity**: O(n) with all optimizations enabled
- **Memory**: Highly optimized
- **Accuracy**: 100% (exact)

```python
config = DatabaseConfig.super_optimized_flat(dim=128)
```

---

## Storage Configuration

### StorageConfiguration

Advanced storage options for performance tuning.

#### Constructor

```python
from nusterdb import StorageConfiguration

storage_config = StorageConfiguration(
    cache_size_mb=256,              # LRU cache size in MB
    write_buffer_size_mb=64,        # Write buffer size in MB
    max_write_buffer_number=3,      # Number of write buffers
    compression="lz4",              # Compression: "none", "snappy", "lz4", "zstd"
    enable_statistics=True,         # Enable performance statistics
    enable_bloom_filter=True,       # Enable bloom filters for faster reads
    bloom_filter_bits_per_key=10,   # Bloom filter bits per key
    max_background_jobs=4           # Background compaction jobs
)

# Default configuration
storage_config = StorageConfiguration.default()
```

---

## Database Operations

### NusterDB

Main database class for vector operations.

#### Creating Database Instances

```python
from nusterdb import NusterDB, DatabaseConfig

# Method 1: Using configuration
config = DatabaseConfig.simple(dim=128, use_hnsw=True)
db = NusterDB("./my_database", config)

# Method 2: Simple creation
db = NusterDB.simple("./my_database", dim=128, use_hnsw=True)

# Method 3: Optimized indexes
db = NusterDB.optimized_flat("./my_database", dim=128)
db = NusterDB.ultra_fast_flat("./my_database", dim=128)
```

#### Basic Operations

```python
# Database properties
dim = db.dimension()        # Get vector dimension
index_type = db.index_type() # Get index type
is_hnsw = db.is_hnsw()      # Check if using HNSW
is_flat = db.is_flat()      # Check if using Flat

# Add single vector
vector = Vector([1.0, 2.0, 3.0, 4.0])
db.add(id=1, vector=vector)

# Add vector with metadata
from nusterdb import Metadata
metadata = Metadata()
metadata.set("category", "image")
metadata.add_tag("processed")
db.add(id=2, vector=vector, metadata=metadata)

# Get vector by ID
retrieved_vector = db.get(id=1)  # Returns Vector or None

# Get metadata by ID  
metadata = db.get_metadata(id=1)  # Returns Metadata or None

# Remove vector
db.remove(id=1)

# List all IDs
ids = db.list_ids()  # Returns list of integers
```

---

## Metadata Management

### Metadata

Rich metadata support for vectors with key-value storage and tagging.

#### Creating Metadata

```python
from nusterdb import Metadata

# Empty metadata
meta = Metadata()

# Metadata with initial data
initial_data = {"category": "image", "source": "camera"}
meta = Metadata.with_data(initial_data)

# Metadata with tags
tags = ["processed", "validated", "public"]
meta = Metadata.with_tags(tags)
```

#### Key-Value Operations

```python
meta = Metadata()

# Set key-value pairs
meta.set("category", "image")
meta.set("confidence", "0.95")
meta.set("timestamp", "2025-07-02T10:30:00Z")

# Get values
category = meta.get("category")  # Returns "image" or None
keys = meta.keys()              # Returns list of all keys

# Check and remove
has_key = meta.contains_key("category")  # Returns bool
removed_value = meta.remove("category")  # Returns removed value or None
```

#### Tag Operations

```python
meta = Metadata()

# Add tags
meta.add_tag("processed")
meta.add_tag("validated")
meta.add_tag("public")

# Get and check tags
tags = meta.tags()              # Returns list of tags
has_tag = meta.has_tag("processed")  # Returns bool
removed = meta.remove_tag("public")  # Returns bool
```

#### Properties and Info

```python
meta = Metadata()

# Size and status
length = meta.len()         # Number of key-value pairs
is_empty = meta.is_empty()  # Check if empty

# Timestamps
created = meta.created_at   # Creation timestamp (Unix seconds)
updated = meta.updated_at   # Last update timestamp
version = meta.version      # Version number
age = meta.age_seconds()    # Age in seconds
```

---

## Bulk Operations

### Bulk Insertion

Efficient bulk operations for high-throughput scenarios.

```python
# Prepare data
ids = [1, 2, 3, 4, 5]
vectors = [
    Vector([1.0, 2.0, 3.0]),
    Vector([4.0, 5.0, 6.0]),
    Vector([7.0, 8.0, 9.0]),
    Vector([10.0, 11.0, 12.0]),
    Vector([13.0, 14.0, 15.0])
]

# Optional metadata for each vector
metadata = [
    Metadata.with_data({"type": "A"}),
    Metadata.with_data({"type": "B"}),
    Metadata.with_data({"type": "A"}),
    Metadata.with_data({"type": "C"}),
    Metadata.with_data({"type": "B"})
]

# Bulk add with metadata
count = db.bulk_add(ids=ids, vectors=vectors, metadata=metadata)
print(f"Added {count} vectors")

# Bulk add without metadata
count = db.bulk_add(ids=ids, vectors=vectors)
print(f"Added {count} vectors")
```

### NumPy Integration

```python
import numpy as np

# Generate random vectors
num_vectors = 1000
dim = 128
data = np.random.randn(num_vectors, dim).astype(np.float32)

# Convert to Vector objects
vectors = [Vector(row.tolist()) for row in data]
ids = list(range(num_vectors))

# Bulk insert
count = db.bulk_add(ids=ids, vectors=vectors)
print(f"Inserted {count} vectors")
```

---

## Search and Retrieval

### Basic Search

```python
# Create query vector
query = Vector([1.0, 2.0, 3.0, 4.0])

# Search for k nearest neighbors
k = 10
results = db.search(query=query, k=k)

# Results format: List[(id, distance), ...]
for vector_id, distance in results:
    print(f"ID: {vector_id}, Distance: {distance:.4f}")
```

### Filtered Search

```python
# Search with metadata filtering
filter_criteria = {
    "category": "image",
    "type": "A"
}

results = db.search(
    query=query, 
    k=10, 
    filter=filter_criteria
)

# Only vectors matching the filter criteria will be returned
for vector_id, distance in results:
    metadata = db.get_metadata(vector_id)
    print(f"ID: {vector_id}, Distance: {distance:.4f}")
    print(f"Metadata: {metadata}")
```

### Search Performance Tips

1. **HNSW Parameters**: Tune `ef_search` for accuracy vs speed tradeoff
2. **Batch Queries**: Process multiple queries together when possible
3. **Filter Selectivity**: Use selective filters to reduce search space
4. **Index Type**: Choose appropriate index for your data size and query patterns

---

## Snapshots and Persistence

### Database Statistics

```python
# Get comprehensive database statistics
stats = db.stats()

print(f"Vector count: {stats.vector_count}")
print(f"Dimension: {stats.dimension}")
print(f"Index type: {stats.index_type}")
print(f"Metadata keys: {stats.metadata_keys}")
```

### Snapshots

```python
# Create automatic snapshot
db.snapshot()

# Create named snapshot
db.snapshot_named("backup_2025_07_02")

# Create snapshot with metadata
snapshot_metadata = {
    "created_by": "user123",
    "purpose": "before_update",
    "version": "1.0.0"
}
db.snapshot_with_metadata("pre_update_backup", snapshot_metadata)
```

### Auto-Snapshots

```python
# Enable auto-snapshots during database creation
config = DatabaseConfig(
    dim=128,
    index_type="hnsw",
    auto_snapshot=True,
    snapshot_interval_secs=3600  # Every hour
)

db = NusterDB("./my_database", config)
```

---

## Performance Optimization

### Index Selection Guide

| Dataset Size | Query Pattern | Recommended Index | Accuracy | Speed |
|-------------|---------------|-------------------|----------|-------|
| < 1K vectors | Exact search | Flat | 100% | Fast |
| 1K - 10K | Exact search | OptimizedFlat | 100% | Faster |
| 10K - 100K | Exact search | UltraFastFlat | 100% | Fastest |
| > 100K | Approx search | HNSW | 95-99% | Very Fast |
| > 1M | Approx search | HNSW (tuned) | 95-99% | Ultra Fast |

### HNSW Tuning

```python
# For higher accuracy (slower)
hnsw_config = HNSWConfig(
    max_nb_connection=32,      # Higher M for better accuracy
    ef_construction=400,       # Higher ef_construction for better graph
    ef_search=100             # Higher ef_search for better recall
)

# For higher speed (lower accuracy)  
hnsw_config = HNSWConfig(
    max_nb_connection=8,       # Lower M for faster search
    ef_construction=100,       # Lower ef_construction for faster indexing
    ef_search=50              # Lower ef_search for faster queries
)
```

### Storage Optimization

```python
# For write-heavy workloads
storage_config = StorageConfiguration(
    write_buffer_size_mb=128,      # Larger write buffers
    max_write_buffer_number=6,     # More write buffers
    max_background_jobs=8          # More compaction jobs
)

# For read-heavy workloads
storage_config = StorageConfiguration(
    cache_size_mb=512,             # Larger cache
    enable_bloom_filter=True,      # Enable bloom filters
    bloom_filter_bits_per_key=15   # More bits for better filtering
)
```

---

## Advanced Usage

### Custom Distance Metrics in Search

```python
# Use specific distance metric for database
euclidean_metric = DistanceMetric.euclidean()
config = DatabaseConfig(
    dim=128,
    index_type="hnsw", 
    distance_metric=euclidean_metric
)

db = NusterDB("./db", config)
```

### Multi-Index Databases

```python
# Create multiple specialized databases
image_db = NusterDB.ultra_fast_flat("./images_db", dim=512)
text_db = NusterDB("./text_db", DatabaseConfig(
    dim=768,
    index_type="hnsw",
    distance_metric=DistanceMetric.cosine()
))

# Use appropriate database for different data types
image_vector = Vector([...])  # 512-dim image embedding
text_vector = Vector([...])   # 768-dim text embedding

image_db.add(1, image_vector)
text_db.add(1, text_vector)
```

### Memory-Efficient Large Dataset Handling

```python
import numpy as np

# Process large datasets in chunks
def add_large_dataset(db, data_generator, chunk_size=1000):
    total_added = 0
    
    for chunk_id, chunk in enumerate(data_generator):
        # Prepare chunk data
        vectors = [Vector(row.tolist()) for row in chunk]
        ids = list(range(chunk_id * chunk_size, (chunk_id + 1) * chunk_size))
        
        # Bulk add chunk
        count = db.bulk_add(ids=ids, vectors=vectors)
        total_added += count
        
        print(f"Added chunk {chunk_id}, total: {total_added}")
    
    return total_added

# Example usage
def data_generator():
    for i in range(10):  # 10 chunks
        chunk = np.random.randn(1000, 128).astype(np.float32)
        yield chunk

db = NusterDB.ultra_fast_flat("./large_db", dim=128)
total = add_large_dataset(db, data_generator())
print(f"Total vectors added: {total}")
```

---

## Examples

### Complete Example: Image Similarity Search

```python
import numpy as np
from nusterdb import NusterDB, Vector, Metadata, DatabaseConfig, HNSWConfig, DistanceMetric

# Setup database for image embeddings
hnsw_config = HNSWConfig(
    max_nb_connection=16,
    ef_construction=200,
    ef_search=100
)

config = DatabaseConfig(
    dim=512,  # Image embedding dimension
    index_type="hnsw",
    distance_metric=DistanceMetric.cosine(),  # Good for embeddings
    hnsw_config=hnsw_config,
    auto_snapshot=True,
    snapshot_interval_secs=3600
)

db = NusterDB("./image_db", config)

# Add images with metadata
images = [
    {"id": 1, "embedding": np.random.randn(512), "path": "cat1.jpg", "category": "animal"},
    {"id": 2, "embedding": np.random.randn(512), "path": "dog1.jpg", "category": "animal"},
    {"id": 3, "embedding": np.random.randn(512), "path": "car1.jpg", "category": "vehicle"},
]

for img in images:
    vector = Vector(img["embedding"].tolist())
    metadata = Metadata()
    metadata.set("path", img["path"])
    metadata.set("category", img["category"])
    metadata.add_tag("indexed")
    
    db.add(img["id"], vector, metadata)

# Search for similar images
query_embedding = np.random.randn(512)
query_vector = Vector(query_embedding.tolist())

# Find similar animals only
results = db.search(
    query=query_vector,
    k=5,
    filter={"category": "animal"}
)

print("Similar animals:")
for img_id, distance in results:
    metadata = db.get_metadata(img_id)
    print(f"ID: {img_id}, Distance: {distance:.4f}")
    print(f"Path: {metadata.get('path')}")
    print(f"Category: {metadata.get('category')}")
    print("---")
```

### Complete Example: Text Similarity with Bulk Operations

```python
import numpy as np
from nusterdb import NusterDB, Vector, Metadata

# Create database optimized for text embeddings
db = NusterDB("./text_db", DatabaseConfig(
    dim=768,  # BERT-like embedding dimension
    index_type="hnsw",
    distance_metric=DistanceMetric.cosine()
))

# Simulate text embeddings with metadata
num_documents = 10000
documents = []
vectors = []
metadata_list = []

for i in range(num_documents):
    # Simulate document embedding
    embedding = np.random.randn(768).astype(np.float32)
    vectors.append(Vector(embedding.tolist()))
    
    # Create metadata
    meta = Metadata()
    meta.set("title", f"Document {i}")
    meta.set("author", f"Author {i % 100}")
    meta.set("topic", ["science", "technology", "health", "sports"][i % 4])
    meta.add_tag("processed")
    if i % 10 == 0:
        meta.add_tag("featured")
    
    metadata_list.append(meta)
    documents.append(i)

# Bulk insert all documents
chunk_size = 1000
for i in range(0, len(documents), chunk_size):
    end_idx = min(i + chunk_size, len(documents))
    
    chunk_ids = documents[i:end_idx]
    chunk_vectors = vectors[i:end_idx]
    chunk_metadata = metadata_list[i:end_idx]
    
    count = db.bulk_add(chunk_ids, chunk_vectors, chunk_metadata)
    print(f"Added {count} documents (total: {end_idx})")

# Search for similar documents by topic
query_embedding = np.random.randn(768).astype(np.float32)
query_vector = Vector(query_embedding.tolist())

# Find science documents
science_results = db.search(
    query=query_vector,
    k=10,
    filter={"topic": "science"}
)

print(f"\nFound {len(science_results)} science documents:")
for doc_id, similarity in science_results:
    metadata = db.get_metadata(doc_id)
    print(f"Document {doc_id}: {metadata.get('title')} by {metadata.get('author')}")
    print(f"Similarity: {similarity:.4f}")

# Get database statistics
stats = db.stats()
print(f"\nDatabase stats:")
print(f"Total documents: {stats.vector_count}")
print(f"Index type: {stats.index_type}")
print(f"Available metadata keys: {stats.metadata_keys}")
```

---

## Best Practices

### 1. Index Selection
- Use **Flat** for exact search with < 10K vectors
- Use **HNSW** for approximate search with > 10K vectors
- Use **OptimizedFlat** for exact search with SIMD acceleration
- Use **UltraFastFlat** for maximum exact search performance

### 2. Memory Management
- Configure appropriate cache sizes based on available RAM
- Use bulk operations for large datasets
- Consider using auto-snapshots for data persistence

### 3. Distance Metrics
- Use **Euclidean** for general-purpose similarity
- Use **Cosine** for normalized embeddings (text, images)
- Use **Manhattan** for high-dimensional sparse data
- Use **Angular** for directional similarity

### 4. HNSW Tuning
- **Higher M**: Better accuracy, more memory
- **Higher ef_construction**: Better quality index, slower building
- **Higher ef_search**: Better recall, slower queries

### 5. Metadata Usage
- Use metadata for filtering to reduce search space
- Index frequently queried metadata fields
- Use tags for categorical information

---

## Error Handling

NusterDB raises specific exceptions for different error conditions:

```python
from nusterdb import NusterDB, Vector, DatabaseConfig
import tempfile

try:
    # Database creation
    db = NusterDB.simple("./test_db", dim=128, use_hnsw=True)
    
    # Vector operations
    vector = Vector([1.0, 2.0, 3.0])  # Wrong dimension
    db.add(1, vector)  # Will raise PyRuntimeError
    
except ValueError as e:
    print(f"Value error: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Constants and Defaults

```python
# Available constants
import nusterdb

print(f"Version: {nusterdb.__version__}")
print(f"Default HNSW M: {nusterdb.DEFAULT_HNSW_M}")
print(f"Default HNSW ef_construction: {nusterdb.DEFAULT_HNSW_EF_CONSTRUCTION}")
print(f"Default cache size: {nusterdb.DEFAULT_CACHE_SIZE_MB} MB")
```

---

This comprehensive documentation covers all classes, methods, parameters, and usage patterns for NusterDB. The library provides a powerful and flexible foundation for building high-performance vector similarity search applications.
