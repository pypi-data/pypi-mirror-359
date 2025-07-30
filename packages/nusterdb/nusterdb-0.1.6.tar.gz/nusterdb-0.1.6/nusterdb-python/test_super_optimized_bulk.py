#!/usr/bin/env python3
"""
Test script for SuperOptimizedFlat index with bulk insertion performance.
This script tests the true bulk insertion capabilities that should approach FAISS performance.
"""

import os
import time
import tempfile
import shutil
import numpy as np
import nusterdb

def generate_random_vectors(n_vectors, dim):
    """Generate random vectors for testing."""
    return np.random.randn(n_vectors, dim).astype(np.float32)

def test_super_optimized_bulk_insertion():
    """Test bulk insertion performance with SuperOptimizedFlat index."""
    print("=== SuperOptimizedFlat Bulk Insertion Test ===")
    
    # Test configuration
    dimensions = [128, 512]
    vector_counts = [1000, 10000, 50000, 100000]
    
    for dim in dimensions:
        print(f"\n--- Testing dimension: {dim} ---")
        
        for n_vectors in vector_counts:
            if n_vectors > 50000 and dim > 128:
                # Skip very large tests to save time
                continue
                
            print(f"\nTesting {n_vectors:,} vectors of dimension {dim}")
            
            # Create temporary directory
            test_dir = tempfile.mkdtemp()
            
            try:
                # Generate test data
                vectors = generate_random_vectors(n_vectors, dim)
                ids = list(range(n_vectors))
                
                # Convert to NusterDB vectors
                nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in vectors]
                
                # Create database with SuperOptimizedFlat index
                config = nusterdb.DatabaseConfig.super_optimized_flat(dim)
                db = nusterdb.NusterDB(test_dir, config)
                
                print(f"Created database with index type: {db.index_type()}")
                
                # Test bulk insertion
                start_time = time.time()
                added_count = db.bulk_add(ids, nuster_vectors)
                bulk_time = time.time() - start_time
                
                vectors_per_sec = n_vectors / bulk_time if bulk_time > 0 else 0
                
                print(f"Bulk inserted {added_count:,} vectors in {bulk_time:.4f}s")
                print(f"Insertion rate: {vectors_per_sec:,.0f} vectors/second")
                print(f"Time per vector: {bulk_time * 1000 / n_vectors:.4f}ms")
                
                # Verify vectors were added
                stats = db.stats()
                print(f"Database now contains {stats.vector_count:,} vectors")
                
                # Test a few searches to verify functionality
                query_vector = nusterdb.Vector(vectors[0].tolist())
                start_time = time.time()
                results = db.search(query_vector, k=10)
                search_time = time.time() - start_time
                
                print(f"Search took {search_time * 1000:.2f}ms for k=10")
                print(f"Top result ID: {results[0][0]} (distance: {results[0][1]:.6f})")
                
                # Compare with single-vector insertion (for comparison)
                if n_vectors <= 10000:  # Only for smaller tests
                    # Create another database for single insertion comparison
                    single_test_dir = tempfile.mkdtemp()
                    try:
                        single_config = nusterdb.DatabaseConfig.super_optimized_flat(dim)
                        single_db = nusterdb.NusterDB(single_test_dir, single_config)
                        
                        start_time = time.time()
                        for i in range(min(1000, n_vectors)):  # Test first 1000 or all if less
                            single_db.add(i, nuster_vectors[i])
                        single_time = time.time() - start_time
                        
                        single_rate = min(1000, n_vectors) / single_time if single_time > 0 else 0
                        speedup = vectors_per_sec / single_rate if single_rate > 0 else 0
                        
                        print(f"Single insertion rate: {single_rate:,.0f} vectors/second")
                        print(f"Bulk insertion speedup: {speedup:.1f}x")
                        
                    finally:
                        shutil.rmtree(single_test_dir, ignore_errors=True)
                
            finally:
                shutil.rmtree(test_dir, ignore_errors=True)
    
    print("\n=== Test completed ===")

def benchmark_against_other_indices():
    """Compare SuperOptimizedFlat against other index types."""
    print("\n=== Index Comparison Benchmark ===")
    
    dim = 128
    n_vectors = 25000
    
    # Generate test data once
    vectors = generate_random_vectors(n_vectors, dim)
    ids = list(range(n_vectors))
    nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in vectors]
    
    index_types = [
        ("flat", nusterdb.DatabaseConfig.simple(dim, False)),
        ("optimized-flat", nusterdb.DatabaseConfig.optimized_flat(dim)),
        ("ultra-fast-flat", nusterdb.DatabaseConfig.ultra_fast_flat(dim)),
        ("super-optimized-flat", nusterdb.DatabaseConfig.super_optimized_flat(dim)),
    ]
    
    results = []
    
    for index_name, config in index_types:
        print(f"\n--- Testing {index_name} ---")
        
        test_dir = tempfile.mkdtemp()
        try:
            db = nusterdb.NusterDB(test_dir, config)
            print(f"Index type: {db.index_type()}")
            
            # Test insertion (use bulk_add if available, otherwise single add)
            start_time = time.time()
            if hasattr(db, 'bulk_add') and index_name in ['super-optimized-flat']:
                added_count = db.bulk_add(ids, nuster_vectors)
                method = "bulk"
            else:
                for i, vec in enumerate(nuster_vectors):
                    db.add(ids[i], vec)
                added_count = len(nuster_vectors)
                method = "single"
                
            insert_time = time.time() - start_time
            insert_rate = n_vectors / insert_time if insert_time > 0 else 0
            
            # Test search
            query_vector = nusterdb.Vector(vectors[0].tolist())
            start_time = time.time()
            search_results = db.search(query_vector, k=10)
            search_time = time.time() - start_time
            
            results.append({
                'index': index_name,
                'method': method,
                'insert_time': insert_time,
                'insert_rate': insert_rate,
                'search_time': search_time * 1000,  # Convert to ms
                'accuracy': search_results[0][0] == 0  # Should find vector 0 as closest to itself
            })
            
            print(f"Insertion ({method}): {insert_rate:,.0f} vectors/second ({insert_time:.4f}s)")
            print(f"Search: {search_time * 1000:.2f}ms")
            print(f"Top result correct: {search_results[0][0] == 0}")
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
    
    # Print summary
    print(f"\n=== Summary for {n_vectors:,} vectors, {dim}D ===")
    print("Index Type".ljust(20) + "Method".ljust(8) + "Insert Rate".ljust(15) + "Search Time".ljust(12) + "Accurate")
    print("-" * 70)
    
    for result in results:
        print(f"{result['index']:<20}{result['method']:<8}{result['insert_rate']:>10,.0f}/s    {result['search_time']:>8.2f}ms    {str(result['accuracy'])}")
    
    # Find best performer
    best_insert = max(results, key=lambda x: x['insert_rate'])
    best_search = min(results, key=lambda x: x['search_time'])
    
    print(f"\nBest insertion: {best_insert['index']} ({best_insert['insert_rate']:,.0f}/s)")
    print(f"Best search: {best_search['index']} ({best_search['search_time']:.2f}ms)")

if __name__ == "__main__":
    print("Testing SuperOptimizedFlat index with bulk insertion")
    print("This tests the true bulk insertion capabilities for maximum performance")
    print()
    
    test_super_optimized_bulk_insertion()
    benchmark_against_other_indices()
    
    print("\nNote: SuperOptimizedFlat with bulk insertion should show significantly")
    print("higher insertion rates compared to single-vector insertion methods.")
