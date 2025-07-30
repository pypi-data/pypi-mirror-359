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
import numpy as np
from nusterdb import NusterDB, Vector

# Create database
db = NusterDB(
    index_type="hnsw",
    distance_metric="cosine", 
    storage_config={"path": "./vector_db"}
)

# Insert vectors with metadata
vectors = [
    Vector("doc1", [0.1, 0.2, 0.3, 0.4], {"category": "tech"}),
    Vector("doc2", [0.5, 0.6, 0.7, 0.8], {"category": "science"}),
]

db.insert_vectors(vectors)

# Search for similar vectors
query = [0.1, 0.2, 0.3, 0.4]
results = db.search_vectors(query, k=5)

for result in results:
    print(f"ID: {result.vector.id}, Distance: {result.distance:.4f}")
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
