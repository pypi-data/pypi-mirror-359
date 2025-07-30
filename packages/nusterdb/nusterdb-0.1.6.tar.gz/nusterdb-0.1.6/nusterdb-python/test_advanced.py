#!/usr/bin/env python3
"""
Test script for advanced NusterDB Python bindings
"""

import sys
import os

def test_advanced_features():
    """Test all advanced features"""
    try:
        import nusterdb
        print(f"✓ Successfully imported nusterdb version {nusterdb.__version__}")
        
        # Test 1: Vector operations
        print("\n=== Test 1: Vector Operations ===")
        v1 = nusterdb.Vector([1.0, 2.0, 3.0])
        v2 = nusterdb.Vector.zeros(3)
        v3 = nusterdb.Vector.ones(3)
        v4 = nusterdb.Vector.random(3, -1.0, 1.0)
        
        print(f"Vector v1: {v1}")
        print(f"Vector v2 (zeros): {v2}")
        print(f"Vector v3 (ones): {v3}")
        print(f"Vector v4 (random): {v4}")
        print(f"v1 dot v3: {v1.dot(v3)}")
        print(f"v1 euclidean distance to v3: {v1.euclidean_distance(v3)}")
        
        # Test 2: Distance metrics
        print("\n=== Test 2: Distance Metrics ===")
        euclidean = nusterdb.DistanceMetric.euclidean()
        cosine = nusterdb.DistanceMetric.cosine()
        manhattan = nusterdb.DistanceMetric.manhattan()
        
        print(f"Euclidean distance: {euclidean.distance(v1, v3)}")
        print(f"Cosine distance: {cosine.distance(v1, v3)}")
        print(f"Manhattan distance: {manhattan.distance(v1, v3)}")
        
        # Test 3: Metadata
        print("\n=== Test 3: Metadata ===")
        meta = nusterdb.Metadata()
        meta.set("category", "test")
        meta.set("language", "en")
        meta.add_tag("important")
        meta.add_tag("demo")
        
        print(f"Metadata: {meta}")
        print(f"Keys: {meta.keys()}")
        print(f"Tags: {meta.tags()}")
        print(f"Has tag 'important': {meta.has_tag('important')}")
        print(f"Get 'category': {meta.get('category')}")
        
        # Test 4: HNSW Config
        print("\n=== Test 4: HNSW Configuration ===")
        hnsw_config = nusterdb.HNSWConfig(
            max_nb_connection=32,
            ef_construction=400,
            max_nb_elements=5000
        )
        print(f"HNSW Config: {hnsw_config}")
        print(f"Max connections: {hnsw_config.max_nb_connection}")
        print(f"EF construction: {hnsw_config.ef_construction}")
        
        # Test 5: Database with Flat index
        print("\n=== Test 5: Database with Flat Index ===")
        db_flat = nusterdb.NusterDB.simple("./test_advanced_flat", 3, False)
        print(f"Flat database: {db_flat}")
        print(f"Dimension: {db_flat.dimension()}")
        print(f"Index type: {db_flat.index_type()}")
        print(f"Is flat: {db_flat.is_flat()}")
        
        # Add vectors
        for i in range(10):
            vector = nusterdb.Vector([float(i), float(i+1), float(i+2)])
            metadata = nusterdb.Metadata()
            metadata.set("id", str(i))
            metadata.set("group", str(i // 3))
            db_flat.add(i, vector, metadata)
        
        # Search
        query = nusterdb.Vector([1.0, 2.0, 3.0])
        results = db_flat.search(query, k=3)
        print(f"Search results: {results}")
        
        # Search with filter
        filter_results = db_flat.search(query, k=3, filter={"group": "0"})
        print(f"Filtered search results: {filter_results}")
        
        # Get statistics
        stats = db_flat.stats()
        print(f"Database stats: {stats}")
        print(f"Vector count: {stats.vector_count}")
        print(f"Metadata keys: {stats.metadata_keys}")
        
        # Test 6: Database with HNSW index
        print("\n=== Test 6: Database with HNSW Index ===")
        hnsw_config = nusterdb.HNSWConfig(max_nb_connection=16, ef_construction=200)
        db_config = nusterdb.DatabaseConfig(
            dim=5,
            index_type="hnsw",
            distance_metric=nusterdb.DistanceMetric.euclidean(),
            hnsw_config=hnsw_config
        )
        
        db_hnsw = nusterdb.NusterDB("./test_advanced_hnsw", db_config)
        print(f"HNSW database: {db_hnsw}")
        print(f"Is HNSW: {db_hnsw.is_hnsw()}")
        
        # Add vectors
        for i in range(100):
            vector = nusterdb.Vector.random(5, -1.0, 1.0)
            metadata = nusterdb.Metadata()
            metadata.set("id", str(i))
            metadata.set("batch", str(i // 20))
            db_hnsw.add(i, vector, metadata)
        
        # Search
        query = nusterdb.Vector.random(5, -1.0, 1.0)
        results = db_hnsw.search(query, k=5)
        print(f"HNSW search results: {results}")
        
        # Test 7: Snapshots
        print("\n=== Test 7: Snapshots ===")
        db_flat.snapshot()
        print("✓ Created default snapshot")
        
        db_flat.snapshot_named("test_backup")
        print("✓ Created named snapshot")
        
        snapshot_meta = {"version": "1.0", "test": "true"}
        db_flat.snapshot_with_metadata("test_with_meta", snapshot_meta)
        print("✓ Created snapshot with metadata")
        
        print("\n=== All Tests Passed! ===")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import nusterdb: {e}")
        return False
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup():
    """Clean up test directories"""
    import shutil
    test_dirs = ["./test_advanced_flat", "./test_advanced_hnsw"]
    for directory in test_dirs:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Cleaned up {directory}")

if __name__ == "__main__":
    print("Testing Advanced NusterDB Python Bindings")
    print("=" * 50)
    
    success = test_advanced_features()
    
    # Clean up
    cleanup()
    
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
