"""
Test script to verify NusterDB functionality
"""

import numpy as np
import time
import sys
import os

# Add the current directory to Python path for testing
sys.path.insert(0, os.path.abspath('.'))

try:
    from nusterdb import NusterDB, DatabaseConfig, Vector, DistanceMetric
    print("✓ Successfully imported NusterDB")
except ImportError as e:
    print(f"✗ Failed to import NusterDB: {e}")
    sys.exit(1)

def test_vector_operations():
    """Test basic vector operations"""
    print("\n--- Testing Vector Operations ---")
    
    # Test vector creation
    v1 = Vector([1.0, 2.0, 3.0])
    v2 = Vector([4.0, 5.0, 6.0])
    print(f"✓ Created vectors: {v1} and {v2}")
    
    # Test vector arithmetic
    v3 = v1 + v2
    print(f"✓ Addition: {v1} + {v2} = {v3}")
    
    v4 = v2 - v1
    print(f"✓ Subtraction: {v2} - {v1} = {v4}")
    
    v5 = v1 * 2.0
    print(f"✓ Scalar multiplication: {v1} * 2.0 = {v5}")
    
    # Test vector properties
    print(f"✓ Dimension: {v1.dim()}")
    print(f"✓ L2 norm: {v1.norm():.3f}")
    print(f"✓ Dot product: {v1.dot(v2):.3f}")
    
    # Test normalization
    v1_norm = v1.normalize()
    print(f"✓ Normalized: {v1_norm}")
    print(f"✓ Is normalized: {v1_norm.is_normalized()}")

def test_database_operations():
    """Test database operations"""
    print("\n--- Testing Database Operations ---")
    
    # Clean up any existing test database
    import shutil
    test_db_path = "./test_nusterdb"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
    
    # Create database configuration
    config = DatabaseConfig(
        dim=128,
        index_type=IndexType.Flat,  # Start with Flat for simplicity
        distance_metric=DistanceMetric.Euclidean,
        compression=Compression.LZ4,
        cache_size_mb=64
    )
    
    # Initialize database
    db = NusterDB(test_db_path, config)
    print(f"✓ Created database: {db}")
    
    # Test vector insertion
    vectors = []
    ids = []
    for i in range(10):
        vector = Vector.random(128, -1.0, 1.0)
        metadata = {"index": str(i), "category": f"test_{i % 3}"}
        vector_id = db.insert(vector, metadata)
        vectors.append(vector)
        ids.append(vector_id)
    
    print(f"✓ Inserted {len(ids)} vectors")
    
    # Test count
    count = db.count()
    print(f"✓ Vector count: {count}")
    
    # Test retrieval
    retrieved_vector = db.get(ids[0])
    retrieved_metadata = db.get_metadata(ids[0])
    print(f"✓ Retrieved vector: {retrieved_vector}")
    print(f"✓ Retrieved metadata: {retrieved_metadata}")
    
    # Test search
    query = vectors[0]  # Use first vector as query
    results = db.search(query, k=3)
    print(f"✓ Search results: {results}")
    
    # Test batch insert
    batch_vectors = [Vector.random(128, -1.0, 1.0) for _ in range(5)]
    batch_metadata = [{"batch": str(i)} for i in range(5)]
    batch_ids = db.batch_insert(batch_vectors, batch_metadata)
    print(f"✓ Batch inserted {len(batch_ids)} vectors")
    
    # Test update
    new_vector = Vector.random(128, -1.0, 1.0)
    updated = db.update(ids[0], new_vector)
    print(f"✓ Updated vector: {updated}")
    
    # Test update metadata
    new_metadata = {"updated": "true", "timestamp": str(time.time())}
    metadata_updated = db.update_metadata(ids[0], new_metadata)
    print(f"✓ Updated metadata: {metadata_updated}")
    
    # Test statistics
    stats = db.stats()
    print(f"✓ Database stats: total_vectors={stats['total_vectors']}, "
          f"database_size={stats['database_size_bytes']} bytes")
    
    # Test snapshot
    db.snapshot("test_snapshot", {"test": "true"})
    snapshots = db.list_snapshots()
    print(f"✓ Created snapshot, total snapshots: {len(snapshots)}")
    
    # Test delete
    deleted = db.delete(ids[-1])
    print(f"✓ Deleted vector: {deleted}")
    
    # Clean up
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
    print("✓ Cleaned up test database")

def test_hnsw_index():
    """Test HNSW index specifically"""
    print("\n--- Testing HNSW Index ---")
    
    # Clean up any existing test database
    import shutil
    test_db_path = "./test_hnsw_db"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
    
    # Create HNSW configuration
    config = DatabaseConfig(
        dim=64,
        index_type=IndexType.Hnsw,
        distance_metric=DistanceMetric.Cosine,
        hnsw_max_connections=16,
        hnsw_ef_construction=200,
        hnsw_max_elements=1000
    )
    
    # Initialize database
    db = NusterDB(test_db_path, config)
    print(f"✓ Created HNSW database: {db}")
    
    # Insert test vectors
    print("Inserting test vectors...")
    vectors = []
    for i in range(100):
        vector = Vector.unit_random(64)  # Unit vectors for cosine similarity
        metadata = {"id": str(i)}
        db.insert(vector, metadata)
        if i == 0:
            vectors.append(vector)  # Keep first vector as query
    
    print("✓ Inserted 100 unit vectors")
    
    # Test search with different ef_search values
    query = vectors[0]
    for ef_search in [10, 50, 100]:
        start_time = time.time()
        results = db.search(query, k=10, ef_search=ef_search)
        search_time = time.time() - start_time
        print(f"✓ Search with ef_search={ef_search}: found {len(results)} results in {search_time*1000:.2f}ms")
    
    # Clean up
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
    print("✓ Cleaned up HNSW test database")

def benchmark():
    """Simple benchmark"""
    print("\n--- Simple Benchmark ---")
    
    # Clean up any existing test database
    import shutil
    test_db_path = "./benchmark_db"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
    
    config = DatabaseConfig(
        dim=256,
        index_type=IndexType.Hnsw,
        distance_metric=DistanceMetric.Euclidean,
        hnsw_max_connections=32,
        hnsw_ef_construction=400
    )
    
    db = NusterDB(test_db_path, config)
    
    # Benchmark insertion
    num_vectors = 1000
    print(f"Inserting {num_vectors} vectors...")
    
    start_time = time.time()
    vectors = []
    for i in range(num_vectors):
        vector = Vector.random(256, -1.0, 1.0)
        vectors.append(vector)
        db.insert(vector, {"id": str(i)})
    
    insert_time = time.time() - start_time
    print(f"✓ Insertion: {insert_time:.2f}s ({num_vectors/insert_time:.1f} vectors/sec)")
    
    # Benchmark search
    num_queries = 100
    print(f"Performing {num_queries} searches...")
    
    start_time = time.time()
    for i in range(num_queries):
        query = Vector.random(256, -1.0, 1.0)
        results = db.search(query, k=10)
    
    search_time = time.time() - start_time
    print(f"✓ Search: {search_time:.2f}s ({num_queries/search_time:.1f} queries/sec)")
    
    # Clean up
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
    print("✓ Cleaned up benchmark database")

def main():
    """Run all tests"""
    print("NusterDB Test Suite")
    print("==================")
    
    try:
        test_vector_operations()
        test_database_operations()
        test_hnsw_index()
        benchmark()
        
        print("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
