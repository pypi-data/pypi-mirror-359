#!/usr/bin/env python3
"""
Large scale bulk insertion test for SuperOptimizedFlat.
This test focuses on maximum performance bulk insertion at scale.
"""

import os
import time
import tempfile
import shutil
import numpy as np
import nusterdb

def large_scale_bulk_insertion_test():
    """Test large scale bulk insertion with SuperOptimizedFlat."""
    print("=== Large Scale SuperOptimizedFlat Bulk Insertion Test ===")
    
    # Test configurations for large scale
    test_configs = [
        (128, 100000),    # 100K vectors, 128D
        (128, 250000),    # 250K vectors, 128D
        (256, 100000),    # 100K vectors, 256D
        (512, 50000),     # 50K vectors, 512D
    ]
    
    results = []
    
    for dim, n_vectors in test_configs:
        print(f"\n--- Testing {n_vectors:,} vectors of dimension {dim} ---")
        
        # Create temporary directory
        test_dir = tempfile.mkdtemp()
        
        try:
            # Generate test data
            print("Generating test data...")
            vectors = np.random.randn(n_vectors, dim).astype(np.float32)
            ids = list(range(n_vectors))
            
            # Convert to NusterDB vectors
            print("Converting to NusterDB vectors...")
            convert_start = time.time()
            nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in vectors]
            convert_time = time.time() - convert_start
            print(f"Conversion took {convert_time:.4f}s")
            
            # Create database with SuperOptimizedFlat index
            config = nusterdb.DatabaseConfig.super_optimized_flat(dim)
            db = nusterdb.NusterDB(test_dir, config)
            
            print(f"Created database with index type: {db.index_type()}")
            
            # Perform bulk insertion
            print("Starting bulk insertion...")
            start_time = time.time()
            added_count = db.bulk_add(ids, nuster_vectors)
            bulk_time = time.time() - start_time
            
            vectors_per_sec = n_vectors / bulk_time if bulk_time > 0 else 0
            time_per_vector_us = (bulk_time * 1000000) / n_vectors
            
            print(f"✓ Bulk inserted {added_count:,} vectors in {bulk_time:.4f}s")
            print(f"✓ Insertion rate: {vectors_per_sec:,.0f} vectors/second")
            print(f"✓ Time per vector: {time_per_vector_us:.2f} microseconds")
            
            # Verify database contents
            stats = db.stats()
            print(f"✓ Database contains {stats.vector_count:,} vectors")
            
            # Test search performance
            query_vector = nusterdb.Vector(vectors[0].tolist())
            
            # Warm up search
            db.search(query_vector, k=1)
            
            # Measure search performance
            search_times = []
            for _ in range(5):
                start_time = time.time()
                results_search = db.search(query_vector, k=10)
                search_time = time.time() - start_time
                search_times.append(search_time * 1000)  # Convert to ms
            
            avg_search_time = sum(search_times) / len(search_times)
            print(f"✓ Average search time: {avg_search_time:.2f}ms (k=10)")
            print(f"✓ Top result ID: {results_search[0][0]} (distance: {results_search[0][1]:.6f})")
            
            # Record results
            results.append({
                'dim': dim,
                'vectors': n_vectors,
                'conversion_time': convert_time,
                'insertion_time': bulk_time,
                'insertion_rate': vectors_per_sec,
                'time_per_vector_us': time_per_vector_us,
                'search_time_ms': avg_search_time,
                'accuracy': results_search[0][0] == 0
            })
            
        except Exception as e:
            print(f"Error during test: {e}")
            results.append({
                'dim': dim,
                'vectors': n_vectors,
                'error': str(e)
            })
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
    
    # Print summary
    print("\n" + "="*80)
    print("BULK INSERTION PERFORMANCE SUMMARY")
    print("="*80)
    print(f"{'Vectors':<10} {'Dim':<5} {'Insert Rate':<15} {'Time/Vec':<12} {'Search':<10} {'Accuracy':<8}")
    print("-" * 80)
    
    for result in results:
        if 'error' not in result:
            print(f"{result['vectors']:<10,} {result['dim']:<5} {result['insertion_rate']:<15,.0f} {result['time_per_vector_us']:<12.2f}μs {result['search_time_ms']:<10.2f}ms {str(result['accuracy']):<8}")
        else:
            print(f"{result['vectors']:<10,} {result['dim']:<5} ERROR: {result['error']}")
    
    # Identify peak performance
    if results and all('error' not in r for r in results):
        best_rate = max(results, key=lambda x: x.get('insertion_rate', 0))
        best_search = min(results, key=lambda x: x.get('search_time_ms', float('inf')))
        
        print(f"\n🚀 PEAK INSERTION PERFORMANCE:")
        print(f"   {best_rate['insertion_rate']:,.0f} vectors/second ({best_rate['vectors']:,} vectors, {best_rate['dim']}D)")
        print(f"   {best_rate['time_per_vector_us']:.2f} microseconds per vector")
        
        print(f"\n🔍 BEST SEARCH PERFORMANCE:")
        print(f"   {best_search['search_time_ms']:.2f}ms ({best_search['vectors']:,} vectors, {best_search['dim']}D)")
        
        # Estimate FAISS comparison
        # FAISS typically achieves ~2-5 million insertions/second for flat index
        faiss_estimate = 2000000  # Conservative estimate
        nuster_best = best_rate['insertion_rate']
        gap_ratio = faiss_estimate / nuster_best if nuster_best > 0 else float('inf')
        
        print(f"\n📊 FAISS COMPARISON ESTIMATE:")
        print(f"   NusterDB: {nuster_best:,.0f} vectors/second")
        print(f"   FAISS (est): {faiss_estimate:,.0f} vectors/second")
        print(f"   Performance gap: {gap_ratio:.1f}x (FAISS advantage)")
        
        if gap_ratio < 10:
            print("   🎯 Getting close to competitive performance!")
        elif gap_ratio < 50:
            print("   📈 Good progress, within reasonable range")
        else:
            print("   🔧 Still room for significant optimization")

def memory_efficiency_test():
    """Test memory efficiency during bulk insertion."""
    print("\n=== Memory Efficiency Test ===")
    
    dim = 128
    n_vectors = 100000
    
    test_dir = tempfile.mkdtemp()
    
    try:
        print(f"Testing memory efficiency with {n_vectors:,} vectors of dimension {dim}")
        
        # Generate test data in chunks to test memory handling
        chunk_size = 10000
        chunks = n_vectors // chunk_size
        
        config = nusterdb.DatabaseConfig.super_optimized_flat(dim)
        db = nusterdb.NusterDB(test_dir, config)
        
        total_insertion_time = 0
        
        for chunk_idx in range(chunks):
            start_idx = chunk_idx * chunk_size
            end_idx = min(start_idx + chunk_size, n_vectors)
            current_chunk_size = end_idx - start_idx
            
            # Generate chunk data
            vectors = np.random.randn(current_chunk_size, dim).astype(np.float32)
            ids = list(range(start_idx, end_idx))
            nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in vectors]
            
            # Insert chunk
            start_time = time.time()
            added_count = db.bulk_add(ids, nuster_vectors)
            chunk_time = time.time() - start_time
            total_insertion_time += chunk_time
            
            chunk_rate = current_chunk_size / chunk_time if chunk_time > 0 else 0
            
            print(f"Chunk {chunk_idx + 1}/{chunks}: {added_count:,} vectors in {chunk_time:.3f}s ({chunk_rate:,.0f}/sec)")
        
        # Final statistics
        total_rate = n_vectors / total_insertion_time if total_insertion_time > 0 else 0
        stats = db.stats()
        
        print(f"\n✓ Total insertion time: {total_insertion_time:.4f}s")
        print(f"✓ Overall insertion rate: {total_rate:,.0f} vectors/second")
        print(f"✓ Final database size: {stats.vector_count:,} vectors")
        
        # Test final search
        query_vector = nusterdb.Vector(np.random.randn(dim).astype(np.float32).tolist())
        start_time = time.time()
        search_results = db.search(query_vector, k=10)
        search_time = time.time() - start_time
        
        print(f"✓ Search time: {search_time * 1000:.2f}ms")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    print("NusterDB SuperOptimizedFlat Large Scale Bulk Insertion Test")
    print("Testing true bulk insertion performance at scale")
    print()
    
    large_scale_bulk_insertion_test()
    memory_efficiency_test()
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)
