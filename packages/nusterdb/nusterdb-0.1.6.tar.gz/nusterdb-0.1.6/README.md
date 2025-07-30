# NusterDB

A high-performance vector database for similarity search and machine learning applications. Built with Rust for speed and efficiency.

## Features

- **Fast Vector Search**: HNSW and Flat indices with sub-millisecond search times
- **Multiple Distance Metrics**: Cosine, Euclidean, Manhattan, and Dot Product
- **Metadata Support**: Store and query structured data alongside vectors
- **Persistent Storage**: RocksDB backend with compression and snapshots
- **Python Interface**: Simple, intuitive API for seamless integration

## Installation

```bash
pip install nusterdb
```

**Requirements**: Python 3.8+, 64-bit OS

## Quick Start

```python
from nusterdb import NusterDB, Vector, Metadata

# Create database (simple method)
db = NusterDB.simple("./vector_db", dim=4, use_hnsw=True)

# Create vectors
vector1 = Vector([0.1, 0.2, 0.3, 0.4])
vector2 = Vector([0.5, 0.6, 0.7, 0.8])

# Add vectors with optional metadata
metadata1 = Metadata({"category": "tech", "source": "doc1"})
metadata2 = Metadata({"category": "science", "source": "doc2"})

db.add(1, vector1, metadata1)
db.add(2, vector2, metadata2)

# Search for similar vectors
query = Vector([0.1, 0.2, 0.3, 0.4])
results = db.search(query, k=2)

for vector_id, distance in results:
    print(f"ID: {vector_id}, Distance: {distance:.4f}")
    metadata = db.get_metadata(vector_id)
    if metadata:
        print(f"  Metadata: {metadata.get_all()}")
```

## Advanced Usage

```python
from nusterdb import NusterDB, DatabaseConfig, HNSWConfig, DistanceMetric

# Advanced configuration
hnsw_config = HNSWConfig(m=16, ef_construction=200)
config = DatabaseConfig(
    dim=384,
    index_type="hnsw",
    distance_metric=DistanceMetric.cosine(),
    hnsw_config=hnsw_config,
    auto_snapshot=True,
    snapshot_interval_secs=1800
)

# Create database with custom configuration
db = NusterDB("./advanced_db", config)

# Use the database as normal
vector = Vector([0.1] * 384)
db.add(1, vector)
results = db.search(vector, k=10)
```

## Use Cases

- **Machine Learning**: Embedding search, recommendation systems, similarity matching
- **Information Retrieval**: Document search, semantic search, content discovery  
- **Computer Vision**: Image similarity, visual search, feature matching
- **Natural Language Processing**: Text similarity, document clustering, search

## Documentation

For detailed API documentation and advanced usage examples, see the [User Manual](USER_MANUAL.md).

## License

Proprietary. See LICENSE for details.
