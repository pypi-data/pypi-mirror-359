#!/usr/bin/env python3
"""
Comprehensive test for quantized ultra-optimized index with memory cleanup
Demonstrates:
1. Memory usage optimization with quantization
2. Speed comparison with FAISS
3. Memory cleanup and garbage collection
4. Quantization accuracy vs memory tradeoffs
"""

import numpy as np
import faiss
import gc
import psutil
import os
import sys
import time
from typing import List, Tuple
import matplotlib.pyplot as plt

# Add the NusterDB path
sys.path.insert(0, '/Users/shashidharnaidu/nuster_ai/nusterdb-python')

try:
    import nusterdb
    print("✓ NusterDB Python bindings loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import NusterDB: {e}")
    print("Building Python bindings...")
    os.system("cd /Users/shashidharnaidu/nuster_ai/nusterdb-python && maturin develop --release")
    import nusterdb

def measure_memory_usage() -> float:
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def cleanup_memory():
    """Force garbage collection and cleanup"""
    gc.collect()
    time.sleep(0.1)  # Allow time for cleanup

def create_test_vectors(n_vectors: int, dim: int, seed: int = 42) -> np.ndarray:
    """Create test vectors with controlled randomness"""
    np.random.seed(seed)
    # Create diverse vectors with different patterns
    vectors = []
    
    # Clustered vectors (better for quantization)
    for cluster in range(10):
        cluster_center = np.random.randn(dim) * 2
        cluster_size = n_vectors // 10
        cluster_vectors = cluster_center + np.random.randn(cluster_size, dim) * 0.5
        vectors.append(cluster_vectors)
    
    # Remaining random vectors
    remaining = n_vectors - len(vectors) * (n_vectors // 10)
    if remaining > 0:
        random_vectors = np.random.randn(remaining, dim)
        vectors.append(random_vectors)
    
    all_vectors = np.vstack(vectors)[:n_vectors]
    return all_vectors.astype(np.float32)

def test_quantized_index(vectors: np.ndarray, k: int = 10) -> dict:
    """Test NusterDB quantized index performance and memory"""
    print("\n🧪 Testing NusterDB UltraOptimizedFlat Index...")
    
    cleanup_memory()
    mem_before = measure_memory_usage()
    
    # Create database with quantized index
    config = nusterdb.DatabaseConfig(
        dimension=vectors.shape[1],
        index_type="ultra_optimized_flat",  # Use quantized index
        storage_path="/tmp/nusterdb_quantized_test"
    )
    
    start_time = time.time()
    db = nusterdb.Database(config)
    
    # Bulk insert all vectors at once (true bulk insertion)
    insert_start = time.time()
    ids = list(range(len(vectors)))
    
    # Insert in one batch for maximum efficiency
    db.bulk_insert(ids, vectors.tolist())
    insert_time = time.time() - insert_start
    
    mem_after_insert = measure_memory_usage()
    
    # Test search performance
    query_vectors = vectors[:100]  # Use first 100 as queries
    search_start = time.time()
    
    results = []
    for query in query_vectors:
        result = db.search(query.tolist(), k)
        results.append(result)
    
    search_time = time.time() - search_start
    mem_after_search = measure_memory_usage()
    
    # Get index statistics
    stats = db.get_stats()
    
    return {
        'name': 'NusterDB UltraOptimized',
        'insert_time': insert_time,
        'search_time': search_time,
        'memory_before': mem_before,
        'memory_after_insert': mem_after_insert,
        'memory_after_search': mem_after_search,
        'memory_used': mem_after_insert - mem_before,
        'vectors_per_second': len(vectors) / insert_time,
        'searches_per_second': len(query_vectors) / search_time,
        'stats': stats,
        'db': db,  # Keep reference for cleanup
        'results': results[:5]  # Sample results
    }

def test_faiss_index(vectors: np.ndarray, k: int = 10) -> dict:
    """Test FAISS flat index for comparison"""
    print("\n🧪 Testing FAISS Flat Index...")
    
    cleanup_memory()
    mem_before = measure_memory_usage()
    
    # Create FAISS index
    start_time = time.time()
    index = faiss.IndexFlatL2(vectors.shape[1])
    
    # Add vectors (FAISS's bulk insert)
    insert_start = time.time()
    index.add(vectors)
    insert_time = time.time() - insert_start
    
    mem_after_insert = measure_memory_usage()
    
    # Test search performance
    query_vectors = vectors[:100]
    search_start = time.time()
    
    distances, indices = index.search(query_vectors, k)
    search_time = time.time() - search_start
    
    mem_after_search = measure_memory_usage()
    
    # Convert results to same format as NusterDB
    results = []
    for i in range(min(5, len(query_vectors))):
        result = [(int(indices[i][j]), float(distances[i][j])) for j in range(k)]
        results.append(result)
    
    return {
        'name': 'FAISS Flat',
        'insert_time': insert_time,
        'search_time': search_time,
        'memory_before': mem_before,
        'memory_after_insert': mem_after_insert,
        'memory_after_search': mem_after_search,
        'memory_used': mem_after_insert - mem_before,
        'vectors_per_second': len(vectors) / insert_time,
        'searches_per_second': len(query_vectors) / search_time,
        'index': index,  # Keep reference for cleanup
        'results': results
    }

def test_faiss_inspired_index(vectors: np.ndarray, k: int = 10) -> dict:
    """Test NusterDB FAISS-inspired index for comparison"""
    print("\n🧪 Testing NusterDB FAISS-Inspired Index...")
    
    cleanup_memory()
    mem_before = measure_memory_usage()
    
    # Create database with FAISS-inspired index
    config = nusterdb.DatabaseConfig(
        dimension=vectors.shape[1],
        index_type="faiss_inspired_flat",
        storage_path="/tmp/nusterdb_faiss_test"
    )
    
    start_time = time.time()
    db = nusterdb.Database(config)
    
    # Bulk insert all vectors at once
    insert_start = time.time()
    ids = list(range(len(vectors)))
    db.bulk_insert(ids, vectors.tolist())
    insert_time = time.time() - insert_start
    
    mem_after_insert = measure_memory_usage()
    
    # Test search performance
    query_vectors = vectors[:100]
    search_start = time.time()
    
    results = []
    for query in query_vectors:
        result = db.search(query.tolist(), k)
        results.append(result)
    
    search_time = time.time() - search_start
    mem_after_search = measure_memory_usage()
    
    return {
        'name': 'NusterDB FAISS-Inspired',
        'insert_time': insert_time,
        'search_time': search_time,
        'memory_before': mem_before,
        'memory_after_insert': mem_after_insert,
        'memory_after_search': mem_after_search,
        'memory_used': mem_after_insert - mem_before,
        'vectors_per_second': len(vectors) / insert_time,
        'searches_per_second': len(query_vectors) / search_time,
        'db': db,
        'results': results[:5]
    }

def cleanup_databases(results: List[dict]):
    """Clean up all database instances and force garbage collection"""
    print("\n🧹 Cleaning up databases and memory...")
    
    for result in results:
        if 'db' in result:
            try:
                del result['db']
            except:
                pass
        if 'index' in result:
            try:
                del result['index']
            except:
                pass
    
    # Force multiple garbage collection cycles
    for _ in range(3):
        gc.collect()
        time.sleep(0.1)
    
    print(f"📊 Memory after cleanup: {measure_memory_usage():.1f} MB")

def print_comparison_table(results: List[dict]):
    """Print a detailed comparison table"""
    print("\n" + "="*120)
    print("🏆 PERFORMANCE COMPARISON")
    print("="*120)
    
    # Header
    header = f"{'Index Type':<25} {'Insert (s)':<12} {'Search (s)':<12} {'Memory (MB)':<12} {'Insert/s':<15} {'Search/s':<15} {'Memory Efficiency':<20}"
    print(header)
    print("-" * 120)
    
    # Data rows
    for result in results:
        name = result['name']
        insert_time = result['insert_time']
        search_time = result['search_time']
        memory_used = result['memory_used']
        insert_rate = result['vectors_per_second']
        search_rate = result['searches_per_second']
        
        # Calculate memory efficiency (lower is better)
        faiss_memory = next((r['memory_used'] for r in results if 'FAISS' in r['name']), memory_used)
        efficiency = memory_used / faiss_memory if faiss_memory > 0 else 1.0
        efficiency_str = f"{efficiency:.2f}x" if efficiency != 1.0 else "baseline"
        
        row = f"{name:<25} {insert_time:<12.3f} {search_time:<12.3f} {memory_used:<12.1f} {insert_rate:<15,.0f} {search_rate:<15.1f} {efficiency_str:<20}"
        print(row)
    
    print("-" * 120)

def analyze_quantization_accuracy(results: List[dict]):
    """Analyze the accuracy impact of quantization"""
    print("\n📊 QUANTIZATION ACCURACY ANALYSIS")
    print("="*60)
    
    # Find FAISS results as ground truth
    faiss_results = None
    quantized_results = None
    
    for result in results:
        if 'FAISS' in result['name']:
            faiss_results = result['results']
        elif 'UltraOptimized' in result['name']:
            quantized_results = result['results']
    
    if faiss_results and quantized_results:
        # Compare top-k accuracy
        total_queries = len(faiss_results)
        matches = 0
        
        for i in range(total_queries):
            faiss_ids = set(item[0] for item in faiss_results[i][:5])  # Top 5
            quantized_ids = set(item[0] for item in quantized_results[i][:5])
            
            matches += len(faiss_ids.intersection(quantized_ids))
        
        accuracy = matches / (total_queries * 5) * 100
        print(f"Top-5 Accuracy: {accuracy:.1f}%")
        
        # Distance correlation
        faiss_distances = [item[1] for result in faiss_results for item in result[:5]]
        quantized_distances = [item[1] for result in quantized_results for item in result[:5]]
        
        if len(faiss_distances) == len(quantized_distances):
            correlation = np.corrcoef(faiss_distances, quantized_distances)[0, 1]
            print(f"Distance Correlation: {correlation:.3f}")

def main():
    """Main test function"""
    print("🚀 NusterDB Quantized Memory Optimization Test")
    print("=" * 60)
    
    # Test parameters
    n_vectors = 100000  # 100K vectors for comprehensive test
    dimension = 128     # Common dimension for embeddings
    k = 10             # Number of nearest neighbors
    
    print(f"📋 Test Parameters:")
    print(f"   Vectors: {n_vectors:,}")
    print(f"   Dimension: {dimension}")
    print(f"   K-nearest: {k}")
    print(f"   Initial Memory: {measure_memory_usage():.1f} MB")
    
    # Create test data
    print("\n📊 Creating test vectors...")
    vectors = create_test_vectors(n_vectors, dimension)
    print(f"   Vector shape: {vectors.shape}")
    print(f"   Memory after vector creation: {measure_memory_usage():.1f} MB")
    
    # Run tests
    results = []
    
    try:
        # Test FAISS (baseline)
        faiss_result = test_faiss_index(vectors, k)
        results.append(faiss_result)
        
        # Test NusterDB FAISS-inspired
        faiss_inspired_result = test_faiss_inspired_index(vectors, k)
        results.append(faiss_inspired_result)
        
        # Test NusterDB quantized
        quantized_result = test_quantized_index(vectors, k)
        results.append(quantized_result)
        
        # Print comparison
        print_comparison_table(results)
        
        # Analyze quantization accuracy
        analyze_quantization_accuracy(results)
        
        # Memory analysis
        print("\n💾 MEMORY ANALYSIS")
        print("="*60)
        for result in results:
            print(f"{result['name']}:")
            print(f"  Memory used: {result['memory_used']:.1f} MB")
            
            # Calculate theoretical minimum
            theoretical = n_vectors * dimension * 4 / (1024 * 1024)  # f32 = 4 bytes
            efficiency = theoretical / result['memory_used'] * 100
            print(f"  Theoretical minimum: {theoretical:.1f} MB")
            print(f"  Efficiency: {efficiency:.1f}%")
            
            if 'stats' in result:
                print(f"  Index stats: {result['stats']}")
            print()
    
    finally:
        # Clean up
        cleanup_databases(results)
        
        # Final memory check
        cleanup_memory()
        final_memory = measure_memory_usage()
        print(f"🎯 Final memory usage: {final_memory:.1f} MB")
        
        # Summary
        if results:
            best_speed = max(results, key=lambda x: x['vectors_per_second'])
            best_memory = min(results, key=lambda x: x['memory_used'])
            
            print(f"\n🏆 SUMMARY:")
            print(f"   Fastest insertion: {best_speed['name']} ({best_speed['vectors_per_second']:,.0f} vectors/sec)")
            print(f"   Most memory efficient: {best_memory['name']} ({best_memory['memory_used']:.1f} MB)")

if __name__ == "__main__":
    main()
