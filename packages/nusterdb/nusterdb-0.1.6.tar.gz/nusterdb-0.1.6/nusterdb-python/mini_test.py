#!/usr/bin/env python3
"""
NusterDB Mini Performance Test
==============================
A very quick test to validate the setup and get initial performance metrics.
"""

import time
import tempfile
import shutil
import os
import numpy as np

# Test imports
try:
    import nusterdb
    from nusterdb import NusterDB, Vector, Metadata
    print(f"✅ NusterDB v{nusterdb.__version__} loaded")
except ImportError as e:
    print(f"❌ NusterDB import failed: {e}")
    exit(1)

def mini_test():
    """Run a mini performance test"""
    print("\n🧪 Running Mini Performance Test")
    print("=" * 40)
    
    # Test parameters
    n_vectors = 1000
    dimension = 128
    n_queries = 10
    
    print(f"Dataset: {n_vectors:,} vectors, {dimension}D")
    print(f"Queries: {n_queries}")
    
    # Generate test data
    print("\n1. Generating test data...")
    np.random.seed(42)
    vectors = np.random.normal(0, 1, (n_vectors, dimension)).astype(np.float32)
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    
    np.random.seed(123)
    queries = np.random.normal(0, 1, (n_queries, dimension)).astype(np.float32)
    queries = queries / np.linalg.norm(queries, axis=1, keepdims=True)
    print("✓ Test data generated")
    
    # Setup database
    print("\n2. Setting up NusterDB...")
    db_path = tempfile.mkdtemp(prefix="nusterdb_mini_")
    
    try:
        start_time = time.time()
        db = NusterDB.simple(db_path, dim=dimension, use_hnsw=False)  # Use flat index for small dataset
        setup_time = time.time() - start_time
        print(f"✓ Database created in {setup_time:.3f}s")
        print(f"  Index type: {db.index_type()}")
        print(f"  Dimension: {db.dimension()}")
        
        # Insert vectors
        print("\n3. Inserting vectors...")
        start_time = time.time()
        
        for i, vector in enumerate(vectors):
            vec = Vector(vector.tolist())
            metadata = Metadata.with_data({"id": str(i), "category": f"cat_{i % 3}"})
            db.add(i, vec, metadata)
            
            if (i + 1) % 100 == 0:
                print(f"  Inserted {i + 1:,} vectors...")
        
        insert_time = time.time() - start_time
        insert_throughput = n_vectors / insert_time
        print(f"✓ Inserted {n_vectors:,} vectors in {insert_time:.3f}s")
        print(f"  Throughput: {insert_throughput:,.0f} vectors/sec")
        
        # Search vectors
        print("\n4. Searching vectors...")
        k = 5
        start_time = time.time()
        total_found = 0
        
        for i, query in enumerate(queries):
            query_vec = Vector(query.tolist())
            results = db.search(query_vec, k=k)
            total_found += len(results)
            print(f"  Query {i+1}: found {len(results)} results")
        
        search_time = time.time() - start_time
        search_throughput = n_queries / search_time
        avg_results = total_found / n_queries
        
        print(f"✓ Completed {n_queries} searches in {search_time:.3f}s")
        print(f"  Throughput: {search_throughput:.1f} queries/sec")
        print(f"  Average results per query: {avg_results:.1f}")
        
        # Test metadata retrieval
        print("\n5. Testing metadata retrieval...")
        start_time = time.time()
        for i in range(min(10, n_vectors)):
            metadata = db.get_metadata(i)
            if metadata:
                meta_value = metadata.get('id')
                assert meta_value == str(i)
        
        metadata_time = time.time() - start_time
        print(f"✓ Metadata retrieval tested in {metadata_time:.3f}s")
        
        # Get database stats
        print("\n6. Database statistics...")
        try:
            stats = db.stats()
            print(f"  Vector count: {stats.vector_count}")
            print(f"  Dimension: {stats.dimension}")
            print(f"  Index type: {stats.index_type}")
        except Exception as e:
            print(f"  Stats not available: {e}")
        
        print("\n" + "="*50)
        print("🎉 MINI TEST COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Insert Performance: {insert_throughput:,.0f} vectors/sec")
        print(f"Search Performance: {search_throughput:.1f} queries/sec")
        print(f"Total Test Time: {(time.time() - start_time + insert_time + setup_time):.2f}s")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            shutil.rmtree(db_path, ignore_errors=True)
            print(f"\n🧹 Cleaned up test database")

if __name__ == "__main__":
    success = mini_test()
    if success:
        print("\n✅ Ready to run full benchmarks!")
    else:
        print("\n❌ Please fix issues before running full benchmarks")
