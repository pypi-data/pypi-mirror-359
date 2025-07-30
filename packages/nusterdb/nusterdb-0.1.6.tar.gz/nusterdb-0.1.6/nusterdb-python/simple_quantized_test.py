#!/usr/bin/env python3
"""
Simple test to verify quantized ultra-optimized index works and measure memory usage
"""

import sys
import os
import time
import gc

# Add the NusterDB path
sys.path.insert(0, '/Users/shashidharnaidu/nuster_ai/nusterdb-python')

try:
    import nusterdb
    print("✓ NusterDB Python bindings loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import NusterDB: {e}")
    sys.exit(1)

def create_test_vectors(n_vectors=1000, dim=128):
    """Create simple test vectors"""
    import random
    vectors = []
    for i in range(n_vectors):
        vector = [random.random() * 2 - 1 for _ in range(dim)]  # Random values between -1 and 1
        vectors.append(vector)
    return vectors

def test_ultra_optimized_index():
    """Test the new ultra-optimized quantized index"""
    print("\n🧪 Testing UltraOptimizedFlat (Quantized) Index...")
    
    # Create test data
    n_vectors = 10000
    dim = 128
    print(f"Creating {n_vectors} vectors of dimension {dim}...")
    vectors = create_test_vectors(n_vectors, dim)
    
    # Test with ultra-optimized flat index
    config = nusterdb.DatabaseConfig.ultra_optimized_flat(dim)
    print(f"Config created: {config}")
    
    # Create database
    db_path = "/tmp/nusterdb_ultra_test"
    try:
        # Clean up any existing database
        if os.path.exists(db_path):
            import shutil
            shutil.rmtree(db_path)
        
        db = nusterdb.NusterDB(db_path, config)
        print("✓ Database created successfully")
        
        # Test insertion
        print("Inserting vectors...")
        start_time = time.time()
        
        ids = list(range(len(vectors)))
        # Convert to Vector objects
        vector_objects = [nusterdb.Vector(v) for v in vectors]
        db.bulk_add(ids, vector_objects)
        
        insert_time = time.time() - start_time
        print(f"✓ Inserted {n_vectors} vectors in {insert_time:.3f}s ({n_vectors/insert_time:.0f} vectors/sec)")
        
        # Test search
        print("Testing search...")
        query = nusterdb.Vector(vectors[0])  # Use first vector as query
        k = 10
        
        start_time = time.time()
        results = db.search(query, k)
        search_time = time.time() - start_time
        
        print(f"✓ Search completed in {search_time:.6f}s")
        print(f"✓ Found {len(results)} results")
        print(f"Top 3 results: {results[:3]}")
        
        # Get stats
        stats = db.stats()
        print(f"✓ Database stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comparison():
    """Compare different index types"""
    print("\n🏆 Comparing Index Types...")
    
    n_vectors = 5000
    dim = 64
    vectors = create_test_vectors(n_vectors, dim)
    ids = list(range(len(vectors)))
    
    # Test configurations
    configs = [
        ("FAISS-Inspired", nusterdb.DatabaseConfig.faiss_inspired_flat(dim)),
        ("Ultra-Optimized", nusterdb.DatabaseConfig.ultra_optimized_flat(dim)),
    ]
    
    results = []
    
    for name, config in configs:
        print(f"\n--- Testing {name} ---")
        
        db_path = f"/tmp/nusterdb_{name.lower().replace('-', '_')}_test"
        
        try:
            # Clean up
            if os.path.exists(db_path):
                import shutil
                shutil.rmtree(db_path)
            
            # Create database
            db = nusterdb.NusterDB(db_path, config)
            
            # Insert
            start_time = time.time()
            vector_objects = [nusterdb.Vector(v) for v in vectors]
            db.bulk_add(ids, vector_objects)
            insert_time = time.time() - start_time
            
            # Search
            query = nusterdb.Vector(vectors[0])
            start_time = time.time()
            search_results = db.search(query, 10)
            search_time = time.time() - start_time
            
            # Stats
            stats = db.stats()
            
            result = {
                'name': name,
                'insert_time': insert_time,
                'search_time': search_time,
                'vectors_per_sec': n_vectors / insert_time,
                'stats': stats
            }
            results.append(result)
            
            print(f"  Insert: {insert_time:.3f}s ({result['vectors_per_sec']:.0f} vec/s)")
            print(f"  Search: {search_time:.6f}s")
            print(f"  Stats: {stats}")
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    # Print comparison
    if len(results) > 1:
        print(f"\n📊 COMPARISON SUMMARY:")
        print(f"{'Index':<20} {'Insert/s':<15} {'Search (ms)':<15}")
        print("-" * 50)
        for result in results:
            search_ms = result['search_time'] * 1000
            print(f"{result['name']:<20} {result['vectors_per_sec']:<15.0f} {search_ms:<15.3f}")

def main():
    """Main test function"""
    print("🚀 NusterDB Ultra-Optimized Index Test")
    print("=" * 50)
    
    # Test 1: Basic functionality
    success = test_ultra_optimized_index()
    
    if success:
        print("\n✓ Basic test passed!")
        
        # Test 2: Comparison
        test_comparison()
    else:
        print("\n✗ Basic test failed!")
        return 1
    
    print("\n🎯 All tests completed!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
