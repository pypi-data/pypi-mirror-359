#!/usr/bin/env python3
"""
Large-scale performance comparison: NusterDB SuperOptimizedFlat vs FAISS
Testing on 1 million vectors to evaluate true large-scale performance.
"""

import os
import time
import tempfile
import shutil
import numpy as np
import faiss
import nusterdb
import gc
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def generate_test_data(n_vectors, dim, chunk_size=50000):
    """Generate test data in chunks to manage memory."""
    print(f"Generating {n_vectors:,} vectors of dimension {dim}...")
    
    vectors = np.empty((n_vectors, dim), dtype=np.float32)
    
    for i in range(0, n_vectors, chunk_size):
        end_idx = min(i + chunk_size, n_vectors)
        current_chunk = end_idx - i
        vectors[i:end_idx] = np.random.randn(current_chunk, dim).astype(np.float32)
        
        if i % (chunk_size * 4) == 0:  # Progress every 200K vectors
            print(f"  Generated {end_idx:,}/{n_vectors:,} vectors...")
    
    # Normalize vectors for better comparison
    faiss.normalize_L2(vectors)
    
    print(f"✓ Generated {n_vectors:,} normalized vectors")
    return vectors

def test_faiss_performance(vectors, n_queries=100):
    """Test FAISS IndexFlatL2 performance."""
    print("\n=== FAISS Performance Test ===")
    
    n_vectors, dim = vectors.shape
    print(f"Testing FAISS with {n_vectors:,} vectors of dimension {dim}")
    
    # Create FAISS index
    print("Creating FAISS IndexFlatL2...")
    start_mem = get_memory_usage()
    
    index = faiss.IndexFlatL2(dim)
    
    # Test insertion performance
    print("Starting FAISS insertion...")
    start_time = time.time()
    index.add(vectors)
    insert_time = time.time() - start_time
    
    end_mem = get_memory_usage()
    mem_usage = end_mem - start_mem
    
    insert_rate = n_vectors / insert_time if insert_time > 0 else 0
    
    print(f"✓ FAISS insertion completed:")
    print(f"  Time: {insert_time:.4f}s")
    print(f"  Rate: {insert_rate:,.0f} vectors/second")
    print(f"  Memory usage: {mem_usage:.1f} MB")
    print(f"  Vectors in index: {index.ntotal:,}")
    
    # Test search performance
    print("\nTesting FAISS search performance...")
    query_vectors = vectors[:n_queries]  # Use first n_queries vectors as queries
    
    # Warm up
    index.search(query_vectors[:10], 10)
    
    # Measure search performance
    search_times = []
    for i in range(5):  # 5 rounds of testing
        start_time = time.time()
        distances, indices = index.search(query_vectors, 10)
        search_time = time.time() - start_time
        search_times.append(search_time * 1000)  # Convert to ms
    
    avg_search_time = sum(search_times) / len(search_times)
    search_per_query = avg_search_time / n_queries
    
    print(f"✓ FAISS search performance:")
    print(f"  Average total time: {avg_search_time:.2f}ms ({n_queries} queries)")
    print(f"  Time per query: {search_per_query:.3f}ms")
    print(f"  Top result accuracy: {(indices[0][0] == 0)}")
    
    return {
        'insert_time': insert_time,
        'insert_rate': insert_rate,
        'memory_usage_mb': mem_usage,
        'search_time_per_query_ms': search_per_query,
        'avg_search_time_ms': avg_search_time,
        'total_vectors': index.ntotal
    }

def test_nusterdb_performance(vectors, n_queries=100, chunk_size=50000):
    """Test NusterDB SuperOptimizedFlat performance."""
    print("\n=== NusterDB SuperOptimizedFlat Performance Test ===")
    
    n_vectors, dim = vectors.shape
    print(f"Testing NusterDB with {n_vectors:,} vectors of dimension {dim}")
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp()
    
    try:
        # Create database
        print("Creating NusterDB with SuperOptimizedFlat...")
        start_mem = get_memory_usage()
        
        config = nusterdb.DatabaseConfig.super_optimized_flat(dim)
        db = nusterdb.NusterDB(test_dir, config)
        
        print(f"Created database with index type: {db.index_type()}")
        
        # Test bulk insertion performance (in chunks to manage memory)
        print("Starting NusterDB bulk insertion...")
        total_insert_time = 0
        total_inserted = 0
        
        start_time = time.time()
        
        for i in range(0, n_vectors, chunk_size):
            end_idx = min(i + chunk_size, n_vectors)
            current_chunk = end_idx - i
            
            # Prepare chunk data
            chunk_vectors = vectors[i:end_idx]
            chunk_ids = list(range(i, end_idx))
            nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in chunk_vectors]
            
            # Insert chunk
            chunk_start = time.time()
            added_count = db.bulk_add(chunk_ids, nuster_vectors)
            chunk_time = time.time() - chunk_start
            
            total_insert_time += chunk_time
            total_inserted += added_count
            
            if i % (chunk_size * 4) == 0:  # Progress every 200K vectors
                current_rate = current_chunk / chunk_time if chunk_time > 0 else 0
                print(f"  Inserted {end_idx:,}/{n_vectors:,} vectors (chunk rate: {current_rate:,.0f}/s)")
        
        total_time = time.time() - start_time
        end_mem = get_memory_usage()
        mem_usage = end_mem - start_mem
        
        insert_rate = n_vectors / total_time if total_time > 0 else 0
        
        print(f"✓ NusterDB insertion completed:")
        print(f"  Time: {total_time:.4f}s")
        print(f"  Rate: {insert_rate:,.0f} vectors/second")
        print(f"  Memory usage: {mem_usage:.1f} MB")
        
        # Verify insertion
        stats = db.stats()
        print(f"  Vectors in database: {stats.vector_count:,}")
        
        # Test search performance
        print("\nTesting NusterDB search performance...")
        query_vectors = vectors[:n_queries]
        
        # Convert queries to NusterDB format
        nuster_queries = [nusterdb.Vector(vec.tolist()) for vec in query_vectors]
        
        # Warm up
        db.search(nuster_queries[0], 10)
        
        # Measure search performance
        search_times = []
        for i in range(5):  # 5 rounds of testing
            start_time = time.time()
            for query in nuster_queries:
                results = db.search(query, 10)
            search_time = time.time() - start_time
            search_times.append(search_time * 1000)  # Convert to ms
        
        avg_search_time = sum(search_times) / len(search_times)
        search_per_query = avg_search_time / n_queries
        
        # Test accuracy with first query
        first_results = db.search(nuster_queries[0], 10)
        
        print(f"✓ NusterDB search performance:")
        print(f"  Average total time: {avg_search_time:.2f}ms ({n_queries} queries)")
        print(f"  Time per query: {search_per_query:.3f}ms")
        print(f"  Top result accuracy: {first_results[0][0] == 0}")
        
        return {
            'insert_time': total_time,
            'insert_rate': insert_rate,
            'memory_usage_mb': mem_usage,
            'search_time_per_query_ms': search_per_query,
            'avg_search_time_ms': avg_search_time,
            'total_vectors': stats.vector_count
        }
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def run_million_vector_comparison():
    """Run the complete 1 million vector comparison."""
    print("="*80)
    print("LARGE-SCALE PERFORMANCE COMPARISON: NusterDB vs FAISS")
    print("Testing with 1 Million Vectors")
    print("="*80)
    
    # Test configuration
    n_vectors = 1000000  # 1 million vectors
    dim = 128
    n_queries = 1000     # Test with 1000 queries for statistical significance
    
    print(f"Configuration:")
    print(f"  Vectors: {n_vectors:,}")
    print(f"  Dimensions: {dim}")
    print(f"  Query vectors: {n_queries}")
    print(f"  Initial memory: {get_memory_usage():.1f} MB")
    
    # Generate test data
    print(f"\n{'-'*60}")
    vectors = generate_test_data(n_vectors, dim)
    print(f"Memory after data generation: {get_memory_usage():.1f} MB")
    
    results = {}
    
    # Test FAISS performance
    print(f"\n{'-'*60}")
    try:
        faiss_results = test_faiss_performance(vectors, n_queries)
        results['faiss'] = faiss_results
        print(f"Memory after FAISS test: {get_memory_usage():.1f} MB")
    except Exception as e:
        print(f"FAISS test failed: {e}")
        results['faiss'] = {'error': str(e)}
    
    # Clean up memory before NusterDB test
    gc.collect()
    
    # Test NusterDB performance
    print(f"\n{'-'*60}")
    try:
        nusterdb_results = test_nusterdb_performance(vectors, n_queries)
        results['nusterdb'] = nusterdb_results
        print(f"Memory after NusterDB test: {get_memory_usage():.1f} MB")
    except Exception as e:
        print(f"NusterDB test failed: {e}")
        results['nusterdb'] = {'error': str(e)}
    
    # Print comprehensive comparison
    print_comparison_results(results, n_vectors, dim, n_queries)
    
    return results

def print_comparison_results(results, n_vectors, dim, n_queries):
    """Print detailed comparison results."""
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE PERFORMANCE COMPARISON RESULTS")
    print(f"{'='*80}")
    print(f"Dataset: {n_vectors:,} vectors × {dim}D, {n_queries} queries")
    
    if 'error' in results.get('faiss', {}) or 'error' in results.get('nusterdb', {}):
        print("\n❌ Some tests failed:")
        if 'error' in results.get('faiss', {}):
            print(f"  FAISS: {results['faiss']['error']}")
        if 'error' in results.get('nusterdb', {}):
            print(f"  NusterDB: {results['nusterdb']['error']}")
        return
    
    faiss_res = results.get('faiss', {})
    nuster_res = results.get('nusterdb', {})
    
    if not faiss_res or not nuster_res:
        print("❌ Insufficient test results for comparison")
        return
    
    # Insertion performance comparison
    print(f"\n🚀 INSERTION PERFORMANCE")
    print(f"{'-'*50}")
    print(f"{'Method':<20} {'Time (s)':<10} {'Rate (vec/s)':<15} {'Memory (MB)':<12}")
    print(f"{'-'*50}")
    print(f"{'FAISS':<20} {faiss_res['insert_time']:<10.3f} {faiss_res['insert_rate']:<15,.0f} {faiss_res['memory_usage_mb']:<12.1f}")
    print(f"{'NusterDB':<20} {nuster_res['insert_time']:<10.3f} {nuster_res['insert_rate']:<15,.0f} {nuster_res['memory_usage_mb']:<12.1f}")
    
    # Calculate speedup
    insert_speedup = faiss_res['insert_rate'] / nuster_res['insert_rate'] if nuster_res['insert_rate'] > 0 else float('inf')
    print(f"\n📊 Insertion Analysis:")
    print(f"  FAISS is {insert_speedup:.1f}x faster at insertion")
    print(f"  NusterDB achieves {(nuster_res['insert_rate'] / faiss_res['insert_rate'] * 100):.1f}% of FAISS insertion speed")
    
    # Search performance comparison
    print(f"\n🔍 SEARCH PERFORMANCE")
    print(f"{'-'*50}")
    print(f"{'Method':<20} {'Per Query (ms)':<15} {'Total Time (ms)':<15}")
    print(f"{'-'*50}")
    print(f"{'FAISS':<20} {faiss_res['search_time_per_query_ms']:<15.3f} {faiss_res['avg_search_time_ms']:<15.2f}")
    print(f"{'NusterDB':<20} {nuster_res['search_time_per_query_ms']:<15.3f} {nuster_res['avg_search_time_ms']:<15.2f}")
    
    # Calculate search speedup
    search_speedup = nuster_res['search_time_per_query_ms'] / faiss_res['search_time_per_query_ms'] if faiss_res['search_time_per_query_ms'] > 0 else float('inf')
    if search_speedup < 1:
        print(f"\n📊 Search Analysis:")
        print(f"  NusterDB is {1/search_speedup:.1f}x faster at search!")
        print(f"  NusterDB search time is {(nuster_res['search_time_per_query_ms'] / faiss_res['search_time_per_query_ms'] * 100):.1f}% of FAISS")
    else:
        print(f"\n📊 Search Analysis:")
        print(f"  FAISS is {search_speedup:.1f}x faster at search")
        print(f"  NusterDB achieves {(faiss_res['search_time_per_query_ms'] / nuster_res['search_time_per_query_ms'] * 100):.1f}% of FAISS search speed")
    
    # Overall assessment
    print(f"\n🎯 OVERALL PERFORMANCE ASSESSMENT")
    print(f"{'-'*50}")
    
    # Calculate composite score (insertion weight = 0.3, search weight = 0.7)
    faiss_composite = (faiss_res['insert_rate'] * 0.3) + ((1/faiss_res['search_time_per_query_ms']) * 1000 * 0.7)
    nuster_composite = (nuster_res['insert_rate'] * 0.3) + ((1/nuster_res['search_time_per_query_ms']) * 1000 * 0.7)
    
    print(f"Memory efficiency:")
    if nuster_res['memory_usage_mb'] < faiss_res['memory_usage_mb']:
        mem_saving = ((faiss_res['memory_usage_mb'] - nuster_res['memory_usage_mb']) / faiss_res['memory_usage_mb']) * 100
        print(f"  ✅ NusterDB uses {mem_saving:.1f}% less memory")
    else:
        mem_overhead = ((nuster_res['memory_usage_mb'] - faiss_res['memory_usage_mb']) / faiss_res['memory_usage_mb']) * 100
        print(f"  ⚠️  NusterDB uses {mem_overhead:.1f}% more memory")
    
    print(f"\nKey strengths:")
    if nuster_res['insert_rate'] > faiss_res['insert_rate']:
        print(f"  ✅ NusterDB: Superior insertion speed")
    if nuster_res['search_time_per_query_ms'] < faiss_res['search_time_per_query_ms']:
        print(f"  ✅ NusterDB: Superior search speed")
    if faiss_res['insert_rate'] > nuster_res['insert_rate']:
        print(f"  ✅ FAISS: Superior insertion speed")
    if faiss_res['search_time_per_query_ms'] < nuster_res['search_time_per_query_ms']:
        print(f"  ✅ FAISS: Superior search speed")
    
    # Performance gap analysis
    print(f"\n📈 PERFORMANCE GAP ANALYSIS")
    print(f"{'-'*50}")
    print(f"Previous gap estimate: ~10x (FAISS advantage)")
    print(f"Actual measured gap: {insert_speedup:.1f}x insertion, {search_speedup:.1f}x search")
    
    if insert_speedup < 5 and search_speedup < 3:
        print(f"🎉 EXCELLENT: NusterDB is highly competitive with FAISS!")
    elif insert_speedup < 15 and search_speedup < 5:
        print(f"✅ GOOD: NusterDB performance is within reasonable range of FAISS")
    else:
        print(f"🔧 ROOM FOR IMPROVEMENT: Significant optimization opportunities remain")

def quick_verification_test():
    """Run a quick verification test with smaller dataset."""
    print("Running quick verification test with 50K vectors...")
    
    n_vectors = 50000
    dim = 128
    
    vectors = generate_test_data(n_vectors, dim)
    
    # Quick FAISS test
    print("\nQuick FAISS test...")
    index = faiss.IndexFlatL2(dim)
    start_time = time.time()
    index.add(vectors)
    faiss_time = time.time() - start_time
    print(f"FAISS: {n_vectors / faiss_time:,.0f} vectors/second")
    
    # Quick NusterDB test
    print("Quick NusterDB test...")
    test_dir = tempfile.mkdtemp()
    try:
        config = nusterdb.DatabaseConfig.super_optimized_flat(dim)
        db = nusterdb.NusterDB(test_dir, config)
        
        ids = list(range(n_vectors))
        nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in vectors]
        
        start_time = time.time()
        db.bulk_add(ids, nuster_vectors)
        nuster_time = time.time() - start_time
        print(f"NusterDB: {n_vectors / nuster_time:,.0f} vectors/second")
        
        print(f"Speed ratio: {(n_vectors / faiss_time) / (n_vectors / nuster_time):.1f}x (FAISS advantage)")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    print("Large-Scale Vector Database Performance Comparison")
    print("NusterDB SuperOptimizedFlat vs FAISS IndexFlatL2")
    print()
    
    # Check system resources
    print(f"System info:")
    print(f"  Available memory: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.1f} GB")
    print(f"  CPU cores: {psutil.cpu_count()}")
    print()
    
    choice = input("Run full 1M vector test? (y/n, default=y): ").strip().lower()
    
    if choice == 'n':
        quick_verification_test()
    else:
        print("Starting full 1 million vector comparison...")
        print("This may take several minutes and use significant memory.")
        print()
        
        results = run_million_vector_comparison()
        
        print(f"\n{'='*80}")
        print("TEST COMPLETED - Results saved to results object")
        print(f"{'='*80}")
