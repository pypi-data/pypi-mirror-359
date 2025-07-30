#!/usr/bin/env python3
"""
Scaling analysis: Test NusterDB performance at different scales
to understand if performance degrades with size.
"""

import os
import time
import tempfile
import shutil
import numpy as np
import nusterdb

def test_scaling_performance():
    """Test NusterDB performance at different scales."""
    print("=== NusterDB Scaling Performance Analysis ===")
    
    dim = 128
    test_sizes = [10000, 50000, 100000, 250000, 500000]
    
    results = []
    
    for n_vectors in test_sizes:
        print(f"\n--- Testing {n_vectors:,} vectors ---")
        
        # Generate test data
        vectors = np.random.randn(n_vectors, dim).astype(np.float32)
        ids = list(range(n_vectors))
        nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in vectors]
        
        test_dir = tempfile.mkdtemp()
        
        try:
            # Create database
            config = nusterdb.DatabaseConfig.super_optimized_flat(dim)
            db = nusterdb.NusterDB(test_dir, config)
            
            # Test insertion
            start_time = time.time()
            added_count = db.bulk_add(ids, nuster_vectors)
            insert_time = time.time() - start_time
            
            insert_rate = n_vectors / insert_time if insert_time > 0 else 0
            
            # Test search
            query_vector = nusterdb.Vector(vectors[0].tolist())
            start_time = time.time()
            search_results = db.search(query_vector, k=10)
            search_time = time.time() - start_time
            
            results.append({
                'vectors': n_vectors,
                'insert_time': insert_time,
                'insert_rate': insert_rate,
                'search_time_ms': search_time * 1000,
                'accuracy': search_results[0][0] == 0
            })
            
            print(f"  Insertion: {insert_rate:,.0f} vectors/sec ({insert_time:.3f}s)")
            print(f"  Search: {search_time * 1000:.2f}ms")
            print(f"  Accuracy: {search_results[0][0] == 0}")
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
    
    # Print scaling analysis
    print(f"\n{'='*70}")
    print("SCALING PERFORMANCE ANALYSIS")
    print(f"{'='*70}")
    print(f"{'Vectors':<10} {'Insert Rate':<15} {'Search Time':<12} {'Efficiency':<12}")
    print("-" * 70)
    
    baseline_rate = results[0]['insert_rate'] if results else 0
    
    for result in results:
        efficiency = (result['insert_rate'] / baseline_rate) if baseline_rate > 0 else 0
        print(f"{result['vectors']:<10,} {result['insert_rate']:<15,.0f} {result['search_time_ms']:<12.2f}ms {efficiency:<12.2f}")
    
    # Analysis
    if len(results) >= 2:
        print(f"\nScaling Analysis:")
        first_rate = results[0]['insert_rate']
        last_rate = results[-1]['insert_rate']
        rate_retention = (last_rate / first_rate) if first_rate > 0 else 0
        
        first_search = results[0]['search_time_ms']
        last_search = results[-1]['search_time_ms']
        search_scaling = last_search / first_search if first_search > 0 else 0
        
        print(f"  Insertion rate retention: {rate_retention:.1%}")
        print(f"  Search time scaling: {search_scaling:.1f}x")
        
        if rate_retention > 0.8:
            print("  ✅ Good insertion rate retention across scales")
        else:
            print("  ⚠️  Insertion rate degrades with scale")
            
        if search_scaling < 3:
            print("  ✅ Reasonable search time scaling")
        else:
            print("  ⚠️  Search time scales poorly with size")

if __name__ == "__main__":
    test_scaling_performance()
