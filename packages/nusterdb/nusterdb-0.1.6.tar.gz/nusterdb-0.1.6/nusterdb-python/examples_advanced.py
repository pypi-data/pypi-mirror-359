#!/usr/bin/env python3
"""
Advanced NusterDB Examples

This file demonstrates all the advanced features of NusterDB:
- HNSW and Flat indexing with custom configurations
- Multiple distance metrics (Euclidean, Cosine, Manhattan, etc.)
- Metadata support with tags and timestamps
- Persistent storage with custom configurations
- Snapshot functionality for backup and restore
- Performance optimizations and batch operations
"""

import nusterdb
import numpy as np
import time
import os
import shutil
from typing import List, Tuple, Dict, Any

def cleanup_test_dbs():
    """Clean up test databases"""
    test_paths = ["./test_flat", "./test_hnsw", "./test_advanced", "./test_snapshots"]
    for path in test_paths:
        if os.path.exists(path):
            shutil.rmtree(path)

def example_1_basic_operations():
    """Example 1: Basic vector operations and distance metrics"""
    print("=== Example 1: Basic Vector Operations ===")
    
    # Create vectors with different methods
    v1 = nusterdb.Vector([1.0, 2.0, 3.0])
    v2 = nusterdb.Vector.zeros(3)
    v3 = nusterdb.Vector.ones(3)
    v4 = nusterdb.Vector.random(3, -1.0, 1.0)
    v5 = nusterdb.Vector.unit_random(3)  # Normalized random vector
    
    print(f"v1: {v1}")
    print(f"v2 (zeros): {v2}")
    print(f"v3 (ones): {v3}")
    print(f"v4 (random): {v4}")
    print(f"v5 (unit random): {v5}")
    print(f"v5 is normalized: {v5.is_normalized()}")
    
    # Distance calculations
    print(f"\nDot product v1·v3: {v1.dot(v3)}")
    print(f"Euclidean distance v1-v3: {v1.euclidean_distance(v3)}")
    print(f"Manhattan distance v1-v3: {v1.manhattan_distance(v3)}")
    print(f"Cosine similarity v1-v3: {v1.cosine_similarity(v3)}")
    print(f"Cosine distance v1-v3: {v1.cosine_distance(v3)}")
    
    # Vector norms
    print(f"\nv1 L2 norm: {v1.norm()}")
    print(f"v1 L1 norm: {v1.l1_norm()}")
    print(f"v1 L∞ norm: {v1.linf_norm()}")
    
    # Vector normalization
    v1_normalized = v1.normalize()
    print(f"v1 normalized: {v1_normalized}")
    print(f"v1 normalized is unit: {v1_normalized.is_normalized()}")

def example_2_distance_metrics():
    """Example 2: All distance metrics"""
    print("\n=== Example 2: Distance Metrics ===")
    
    v1 = nusterdb.Vector([1.0, 2.0, 3.0])
    v2 = nusterdb.Vector([2.0, 3.0, 4.0])
    
    metrics = [
        ("Euclidean", nusterdb.DistanceMetric.euclidean()),
        ("Manhattan", nusterdb.DistanceMetric.manhattan()),
        ("Chebyshev", nusterdb.DistanceMetric.chebyshev()),
        ("Cosine", nusterdb.DistanceMetric.cosine()),
        ("Angular", nusterdb.DistanceMetric.angular()),
        ("Jaccard", nusterdb.DistanceMetric.jaccard()),
        ("Hamming", nusterdb.DistanceMetric.hamming()),
    ]
    
    for name, metric in metrics:
        try:
            dist = metric.distance(v1, v2)
            sim = metric.similarity(v1, v2)
            print(f"{name:12} - Distance: {dist:.6f}, Similarity: {sim:.6f}")
        except Exception as e:
            print(f"{name:12} - Error: {e}")

def example_3_metadata_operations():
    """Example 3: Advanced metadata operations"""
    print("\n=== Example 3: Metadata Operations ===")
    
    # Create metadata with various methods
    meta1 = nusterdb.Metadata()
    meta1.set("category", "document")
    meta1.set("language", "en")
    meta1.add_tag("important")
    meta1.add_tag("processed")
    
    data = {"type": "image", "format": "jpg", "size": "1024x768"}
    meta2 = nusterdb.Metadata.with_data(data)
    meta2.add_tag("visual")
    meta2.add_tag("high-res")
    
    print(f"Meta1: {meta1}")
    print(f"Meta1 keys: {meta1.keys()}")
    print(f"Meta1 tags: {meta1.tags()}")
    print(f"Meta1 created at: {meta1.created_at}")
    print(f"Meta1 version: {meta1.version}")
    
    print(f"\nMeta2: {meta2}")
    print(f"Meta2 has tag 'visual': {meta2.has_tag('visual')}")
    print(f"Meta2 contains key 'type': {meta2.contains_key('type')}")
    print(f"Meta2 get 'format': {meta2.get('format')}")

def example_4_flat_indexing():
    """Example 4: Flat indexing with custom configuration"""
    print("\n=== Example 4: Flat Indexing ===")
    
    # Create flat index configuration
    flat_config = nusterdb.FlatIndexConfig(
        use_simd=True,
        batch_size=1000,
        sort_algorithm="unstable"
    )
    
    # Create storage configuration
    storage_config = nusterdb.StorageConfiguration(
        compression="lz4",
        cache_size_mb=128,
        write_buffer_size_mb=32,
        enable_bloom_filter=True
    )
    
    # Create database configuration
    db_config = nusterdb.DatabaseConfig(
        dim=5,
        index_type="flat",
        distance_metric=nusterdb.DistanceMetric.euclidean(),
        flat_config=flat_config,
        storage_config=storage_config,
        auto_snapshot=False
    )
    
    # Create database
    db = nusterdb.NusterDB("./test_flat", db_config)
    
    print(f"Database: {db}")
    print(f"Dimension: {db.dimension()}")
    print(f"Index type: {db.index_type()}")
    print(f"Is flat: {db.is_flat()}")
    print(f"Is HNSW: {db.is_hnsw()}")
    
    # Add vectors with metadata
    for i in range(100):
        vector = nusterdb.Vector.random(5, -1.0, 1.0)
        metadata = nusterdb.Metadata()
        metadata.set("id", str(i))
        metadata.set("batch", str(i // 10))
        metadata.add_tag(f"group_{i % 5}")
        
        db.add(i, vector, metadata)
    
    # Get statistics
    stats = db.stats()
    print(f"\nDatabase stats: {stats}")
    print(f"Vector count: {stats.vector_count}")
    print(f"Metadata keys: {stats.metadata_keys}")
    
    # Search without filter
    query = nusterdb.Vector.random(5, -1.0, 1.0)
    results = db.search(query, k=5)
    print(f"\nTop 5 results (no filter): {results}")
    
    # Search with metadata filter
    filter_dict = {"batch": "0"}
    filtered_results = db.search(query, k=5, filter=filter_dict)
    print(f"Top 5 results (batch=0): {filtered_results}")

def example_5_hnsw_indexing():
    """Example 5: HNSW indexing with custom configuration"""
    print("\n=== Example 5: HNSW Indexing ===")
    
    # Create HNSW configuration
    hnsw_config = nusterdb.HNSWConfig(
        max_nb_connection=32,        # Higher connectivity
        max_nb_elements=10000,       # Initial capacity
        max_layer=16,                # Number of layers
        ef_construction=400,         # Higher build quality
        ef_search=100,               # Search quality
        use_heuristic=True
    )
    
    print(f"HNSW Config: {hnsw_config}")
    
    # Create database with HNSW
    db_config = nusterdb.DatabaseConfig(
        dim=128,
        index_type="hnsw",
        distance_metric=nusterdb.DistanceMetric.cosine(),
        hnsw_config=hnsw_config,
        auto_snapshot=True,
        snapshot_interval_secs=1800  # 30 minutes
    )
    
    db = nusterdb.NusterDB("./test_hnsw", db_config)
    print(f"HNSW Database: {db}")
    
    # Add high-dimensional vectors
    print("Adding 1000 128-dimensional vectors...")
    start_time = time.time()
    
    for i in range(1000):
        vector = nusterdb.Vector.unit_random(128)  # Unit vectors for cosine similarity
        metadata = nusterdb.Metadata()
        metadata.set("doc_id", f"doc_{i}")
        metadata.set("category", ["text", "image", "audio"][i % 3])
        metadata.add_tag(f"cluster_{i // 100}")
        
        db.add(i, vector, metadata)
        
        if (i + 1) % 100 == 0:
            print(f"  Added {i + 1} vectors")
    
    add_time = time.time() - start_time
    print(f"Adding completed in {add_time:.2f} seconds")
    
    # Perform searches
    query = nusterdb.Vector.unit_random(128)
    
    print("\nPerforming searches...")
    start_time = time.time()
    
    # Search without filter
    results = db.search(query, k=10)
    search_time = time.time() - start_time
    print(f"Search (no filter) completed in {search_time:.4f} seconds")
    print(f"Top 3 results: {results[:3]}")
    
    # Search with filter
    start_time = time.time()
    filter_dict = {"category": "text"}
    filtered_results = db.search(query, k=10, filter=filter_dict)
    filtered_search_time = time.time() - start_time
    print(f"Search (with filter) completed in {filtered_search_time:.4f} seconds")
    print(f"Top 3 filtered results: {filtered_results[:3]}")

def example_6_snapshots():
    """Example 6: Snapshot functionality"""
    print("\n=== Example 6: Snapshots ===")
    
    # Create database
    db = nusterdb.NusterDB.simple("./test_snapshots", 10, False)
    
    # Add some data
    for i in range(50):
        vector = nusterdb.Vector.random(10, 0.0, 1.0)
        metadata = nusterdb.Metadata()
        metadata.set("item", f"item_{i}")
        db.add(i, vector, metadata)
    
    print(f"Added 50 vectors to database")
    
    # Create default snapshot
    print("Creating default snapshot...")
    db.snapshot()
    
    # Create named snapshots
    print("Creating named snapshots...")
    db.snapshot_named("backup_v1")
    
    # Create snapshot with metadata
    snapshot_meta = {
        "version": "1.0",
        "created_by": "example_script",
        "purpose": "demo"
    }
    db.snapshot_with_metadata("backup_with_meta", snapshot_meta)
    
    print("All snapshots created successfully")
    
    # Add more data after snapshot
    for i in range(50, 75):
        vector = nusterdb.Vector.random(10, 0.0, 1.0)
        metadata = nusterdb.Metadata()
        metadata.set("item", f"item_{i}")
        db.add(i, vector, metadata)
    
    stats = db.stats()
    print(f"Database now has {stats.vector_count} vectors")

def example_7_performance_comparison():
    """Example 7: Performance comparison between Flat and HNSW"""
    print("\n=== Example 7: Performance Comparison ===")
    
    dimensions = 64
    num_vectors = 5000
    num_queries = 100
    k = 10
    
    print(f"Performance test: {num_vectors} vectors, {dimensions}D, {num_queries} queries, k={k}")
    
    # Generate test data
    print("Generating test data...")
    vectors = []
    for i in range(num_vectors):
        vectors.append(nusterdb.Vector.random(dimensions, -1.0, 1.0))
    
    queries = []
    for i in range(num_queries):
        queries.append(nusterdb.Vector.random(dimensions, -1.0, 1.0))
    
    # Test Flat index
    print("\n--- Flat Index ---")
    db_flat = nusterdb.NusterDB.simple("./test_perf_flat", dimensions, False)
    
    start_time = time.time()
    for i, vector in enumerate(vectors):
        db_flat.add(i, vector)
    flat_build_time = time.time() - start_time
    print(f"Build time: {flat_build_time:.2f} seconds")
    
    start_time = time.time()
    for query in queries:
        results = db_flat.search(query, k)
    flat_search_time = time.time() - start_time
    print(f"Search time ({num_queries} queries): {flat_search_time:.2f} seconds")
    print(f"Average search time: {flat_search_time/num_queries*1000:.2f} ms")
    
    # Test HNSW index
    print("\n--- HNSW Index ---")
    db_hnsw = nusterdb.NusterDB.simple("./test_perf_hnsw", dimensions, True)
    
    start_time = time.time()
    for i, vector in enumerate(vectors):
        db_hnsw.add(i, vector)
    hnsw_build_time = time.time() - start_time
    print(f"Build time: {hnsw_build_time:.2f} seconds")
    
    start_time = time.time()
    for query in queries:
        results = db_hnsw.search(query, k)
    hnsw_search_time = time.time() - start_time
    print(f"Search time ({num_queries} queries): {hnsw_search_time:.2f} seconds")
    print(f"Average search time: {hnsw_search_time/num_queries*1000:.2f} ms")
    
    # Compare results
    print(f"\n--- Comparison ---")
    print(f"Build time ratio (HNSW/Flat): {hnsw_build_time/flat_build_time:.2f}x")
    print(f"Search time ratio (HNSW/Flat): {hnsw_search_time/flat_search_time:.2f}x")
    print(f"Search speedup (Flat/HNSW): {flat_search_time/hnsw_search_time:.2f}x")

def example_8_comprehensive_workflow():
    """Example 8: Comprehensive workflow with all features"""
    print("\n=== Example 8: Comprehensive Workflow ===")
    
    # Create advanced configuration
    hnsw_config = nusterdb.HNSWConfig(
        max_nb_connection=16,
        ef_construction=200,
        ef_search=50
    )
    
    storage_config = nusterdb.StorageConfiguration(
        compression="lz4",
        cache_size_mb=256,
        enable_statistics=True
    )
    
    db_config = nusterdb.DatabaseConfig(
        dim=256,
        index_type="hnsw",
        distance_metric=nusterdb.DistanceMetric.cosine(),
        hnsw_config=hnsw_config,
        storage_config=storage_config,
        auto_snapshot=True,
        snapshot_interval_secs=3600
    )
    
    db = nusterdb.NusterDB("./test_advanced", db_config)
    print(f"Created advanced database: {db}")
    
    # Add vectors with rich metadata
    categories = ["document", "image", "audio", "video"]
    languages = ["en", "es", "fr", "de", "zh"]
    
    print("Adding vectors with rich metadata...")
    for i in range(1000):
        # Create high-dimensional vector
        vector = nusterdb.Vector.unit_random(256)
        
        # Create rich metadata
        metadata = nusterdb.Metadata()
        metadata.set("id", f"item_{i:04d}")
        metadata.set("category", categories[i % len(categories)])
        metadata.set("language", languages[i % len(languages)])
        metadata.set("score", str(np.random.uniform(0.0, 1.0)))
        metadata.set("created", str(int(time.time())))
        
        # Add tags
        metadata.add_tag(f"batch_{i // 100}")
        metadata.add_tag("processed")
        if i % 10 == 0:
            metadata.add_tag("featured")
        
        db.add(i, vector, metadata)
        
        if (i + 1) % 200 == 0:
            print(f"  Added {i + 1} vectors")
    
    # Get comprehensive statistics
    stats = db.stats()
    print(f"\nDatabase statistics:")
    print(f"  Vector count: {stats.vector_count}")
    print(f"  Dimension: {stats.dimension}")
    print(f"  Index type: {stats.index_type}")
    print(f"  Metadata keys: {stats.metadata_keys}")
    
    # Perform various searches
    print("\nPerforming various searches...")
    query = nusterdb.Vector.unit_random(256)
    
    # Search without filter
    results1 = db.search(query, k=5)
    print(f"Top 5 (no filter): {[r[0] for r in results1]}")
    
    # Search with category filter
    results2 = db.search(query, k=5, filter={"category": "document"})
    print(f"Top 5 (documents): {[r[0] for r in results2]}")
    
    # Search with language filter
    results3 = db.search(query, k=5, filter={"language": "en"})
    print(f"Top 5 (English): {[r[0] for r in results3]}")
    
    # Search with multiple filters
    results4 = db.search(query, k=5, filter={"category": "image", "language": "zh"})
    print(f"Top 5 (Chinese images): {[r[0] for r in results4]}")
    
    # Create multiple snapshots
    print("\nCreating snapshots...")
    db.snapshot_named("full_dataset")
    
    snapshot_meta = {
        "version": "2.0",
        "total_vectors": str(stats.vector_count),
        "categories": ",".join(categories),
        "languages": ",".join(languages)
    }
    db.snapshot_with_metadata("production_backup", snapshot_meta)
    
    print("Comprehensive workflow completed successfully!")

def main():
    """Run all examples"""
    print("NusterDB Advanced Examples")
    print("=" * 50)
    
    # Clean up any existing test databases
    cleanup_test_dbs()
    
    try:
        example_1_basic_operations()
        example_2_distance_metrics()
        example_3_metadata_operations()
        example_4_flat_indexing()
        example_5_hnsw_indexing()
        example_6_snapshots()
        example_7_performance_comparison()
        example_8_comprehensive_workflow()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up test databases
        cleanup_test_dbs()

if __name__ == "__main__":
    main()
