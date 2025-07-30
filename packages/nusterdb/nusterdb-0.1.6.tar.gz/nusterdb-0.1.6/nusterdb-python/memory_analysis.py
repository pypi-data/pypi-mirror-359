#!/usr/bin/env python3
"""
Memory Usage Analysis for NusterDB Quantized Index
Compares memory efficiency and explains the differences with FAISS
"""

import sys
import os
import time
import gc
import subprocess

# Add the NusterDB path
sys.path.insert(0, '/Users/shashidharnaidu/nuster_ai/nusterdb-python')

try:
    import nusterdb
    print("✓ NusterDB Python bindings loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import NusterDB: {e}")
    sys.exit(1)

def get_memory_usage():
    """Get current memory usage in MB using ps"""
    try:
        pid = os.getpid()
        result = subprocess.run(['ps', '-o', 'rss=', '-p', str(pid)], capture_output=True, text=True)
        if result.returncode == 0:
            rss_kb = int(result.stdout.strip())
            return rss_kb / 1024.0  # Convert to MB
    except:
        pass
    return 0.0

def create_test_vectors(n_vectors=100000, dim=128):
    """Create test vectors with controlled patterns for better quantization"""
    import random
    random.seed(42)  # For reproducible results
    
    vectors = []
    
    # Create clustered data (better for quantization)
    num_clusters = 20
    cluster_size = n_vectors // num_clusters
    
    for cluster_id in range(num_clusters):
        # Create cluster center
        center = [random.gauss(0, 2) for _ in range(dim)]
        
        # Create vectors around cluster center
        for _ in range(cluster_size):
            vector = [center[i] + random.gauss(0, 0.5) for i in range(dim)]
            vectors.append(vector)
    
    # Fill remaining vectors with random data
    while len(vectors) < n_vectors:
        vector = [random.gauss(0, 1) for _ in range(dim)]
        vectors.append(vector)
    
    return vectors[:n_vectors]

def analyze_memory_usage(index_name, config, vectors, cleanup_func=None):
    """Analyze memory usage for a specific index type"""
    print(f"\n📊 Memory Analysis: {index_name}")
    print("-" * 50)
    
    # Cleanup before test
    if cleanup_func:
        cleanup_func()
    gc.collect()
    
    mem_before = get_memory_usage()
    print(f"Memory before: {mem_before:.1f} MB")
    
    # Create database
    db_path = f"/tmp/nusterdb_memory_test_{index_name.lower().replace('-', '_')}"
    if os.path.exists(db_path):
        import shutil
        shutil.rmtree(db_path)
    
    start_time = time.time()
    db = nusterdb.NusterDB(db_path, config)
    
    mem_after_creation = get_memory_usage()
    print(f"Memory after DB creation: {mem_after_creation:.1f} MB (+{mem_after_creation - mem_before:.1f} MB)")
    
    # Convert vectors
    print("Converting vectors...")
    vector_objects = [nusterdb.Vector(v) for v in vectors]
    
    mem_after_conversion = get_memory_usage()  
    print(f"Memory after conversion: {mem_after_conversion:.1f} MB (+{mem_after_conversion - mem_after_creation:.1f} MB)")
    
    # Insert vectors
    print("Inserting vectors...")
    ids = list(range(len(vectors)))
    
    insert_start = time.time()
    db.bulk_add(ids, vector_objects)
    insert_time = time.time() - insert_start
    
    mem_after_insert = get_memory_usage()
    print(f"Memory after insertion: {mem_after_insert:.1f} MB (+{mem_after_insert - mem_after_conversion:.1f} MB)")
    
    # Test search
    query = vector_objects[0]
    search_start = time.time()
    results = db.search(query, 10)
    search_time = time.time() - search_start
    
    mem_after_search = get_memory_usage()
    print(f"Memory after search: {mem_after_search:.1f} MB")
    
    # Get database stats
    stats = db.stats()
    
    # Calculate theoretical memory usage
    n_vectors = len(vectors)
    dim = len(vectors[0])
    
    # Theoretical minimum for f32 vectors: n_vectors * dim * 4 bytes + IDs
    theoretical_vectors = n_vectors * dim * 4 / (1024 * 1024)  # MB
    theoretical_ids = n_vectors * 4 / (1024 * 1024)  # MB for 32-bit IDs
    theoretical_total = theoretical_vectors + theoretical_ids
    
    # Actual usage (excluding Python overhead)
    actual_index_memory = (mem_after_insert - mem_after_conversion)
    
    print(f"\nMemory Breakdown:")
    print(f"  Theoretical vectors: {theoretical_vectors:.1f} MB")
    print(f"  Theoretical IDs: {theoretical_ids:.1f} MB")
    print(f"  Theoretical total: {theoretical_total:.1f} MB")
    print(f"  Actual index memory: {actual_index_memory:.1f} MB")
    
    if theoretical_total > 0:
        efficiency = theoretical_total / actual_index_memory * 100
        overhead = (actual_index_memory / theoretical_total - 1) * 100
        print(f"  Memory efficiency: {efficiency:.1f}%")
        print(f"  Memory overhead: {overhead:.1f}%")
    
    print(f"\nPerformance:")
    print(f"  Insert time: {insert_time:.3f}s ({n_vectors/insert_time:.0f} vectors/sec)")
    print(f"  Search time: {search_time:.6f}s")
    print(f"  Database stats: {stats}")
    
    # Calculate quantization savings for ultra-optimized
    if "Ultra-Optimized" in index_name:
        # Assume int8 quantization (4x reduction)
        quantized_vectors = theoretical_vectors / 4
        total_with_quantization = quantized_vectors + theoretical_ids
        quantization_savings = (theoretical_total - total_with_quantization) / theoretical_total * 100
        print(f"\nQuantization Analysis:")
        print(f"  Quantized vectors: {quantized_vectors:.1f} MB (4x reduction)")
        print(f"  Total with quantization: {total_with_quantization:.1f} MB")
        print(f"  Theoretical savings: {quantization_savings:.1f}%")
    
    # Clean up vector objects to free memory
    del vector_objects, db
    gc.collect()
    
    return {
        'name': index_name,
        'insert_time': insert_time,
        'search_time': search_time,
        'memory_before': mem_before,
        'memory_after_insert': mem_after_insert,
        'memory_used': actual_index_memory,
        'theoretical_memory': theoretical_total,
        'efficiency': efficiency if theoretical_total > 0 else 0,
        'vectors_per_sec': n_vectors / insert_time
    }

def compare_with_faiss_memory():
    """Explain the memory differences with FAISS"""
    print("\n🧠 Understanding Memory Differences with FAISS")
    print("=" * 60)
    
    n_vectors = 100000
    dim = 128
    
    # Calculate FAISS memory usage
    faiss_vectors = n_vectors * dim * 4 / (1024 * 1024)  # f32 vectors
    faiss_ids = n_vectors * 8 / (1024 * 1024)  # 64-bit IDs in FAISS
    faiss_overhead = faiss_vectors * 0.05  # ~5% overhead for metadata
    faiss_total = faiss_vectors + faiss_ids + faiss_overhead
    
    print(f"FAISS Memory Usage (estimated):")
    print(f"  Vector data: {faiss_vectors:.1f} MB")
    print(f"  IDs (64-bit): {faiss_ids:.1f} MB")
    print(f"  Metadata overhead: {faiss_overhead:.1f} MB")
    print(f"  Total: {faiss_total:.1f} MB")
    
    # NusterDB quantized memory usage
    nuster_quantized_vectors = n_vectors * dim * 1 / (1024 * 1024)  # int8 quantization
    nuster_ids = n_vectors * 4 / (1024 * 1024)  # 32-bit IDs
    nuster_quantization_params = dim * 8 / (1024 * 1024)  # scale + offset per dimension
    nuster_total = nuster_quantized_vectors + nuster_ids + nuster_quantization_params
    
    print(f"\nNusterDB Ultra-Optimized (quantized) Memory Usage:")
    print(f"  Quantized vectors (int8): {nuster_quantized_vectors:.1f} MB")
    print(f"  IDs (32-bit): {nuster_ids:.1f} MB")
    print(f"  Quantization params: {nuster_quantization_params:.1f} MB")
    print(f"  Total: {nuster_total:.1f} MB")
    
    memory_savings = (faiss_total - nuster_total) / faiss_total * 100
    print(f"\nMemory Comparison:")
    print(f"  NusterDB uses {nuster_total/faiss_total:.2f}x less memory than FAISS")
    print(f"  Memory savings: {memory_savings:.1f}%")
    
    print(f"\nKey Optimizations in NusterDB Ultra-Optimized:")
    print(f"  1. Int8 quantization: {nuster_quantized_vectors:.1f} MB vs {faiss_vectors:.1f} MB (4x reduction)")
    print(f"  2. 32-bit IDs: {nuster_ids:.1f} MB vs {faiss_ids:.1f} MB (2x reduction)")
    print(f"  3. Minimal metadata overhead")
    print(f"  4. Optimized memory layout with single allocation")

def main():
    """Main analysis function"""
    print("🔬 NusterDB Memory Usage Analysis")
    print("=" * 50)
    
    # Test parameters
    n_vectors = 50000  # Smaller for detailed analysis
    dim = 128
    
    print(f"Test Parameters:")
    print(f"  Vectors: {n_vectors:,}")
    print(f"  Dimension: {dim}")
    print(f"  Vector size: {dim * 4} bytes (f32)")
    print(f"  Total vector data: {n_vectors * dim * 4 / (1024*1024):.1f} MB")
    
    # Create test data
    print(f"\nCreating test vectors...")
    vectors = create_test_vectors(n_vectors, dim)
    
    # Test configurations
    configs = [
        ("FAISS-Inspired", nusterdb.DatabaseConfig.faiss_inspired_flat(dim)),
        ("Ultra-Optimized", nusterdb.DatabaseConfig.ultra_optimized_flat(dim)),
    ]
    
    results = []
    
    # Cleanup function
    def cleanup():
        gc.collect()
        time.sleep(0.1)
    
    # Run memory analysis
    for name, config in configs:
        try:
            result = analyze_memory_usage(name, config, vectors, cleanup)
            results.append(result)
        except Exception as e:
            print(f"Failed to analyze {name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print comparison
    if len(results) >= 2:
        print(f"\n🏆 COMPARISON SUMMARY")
        print("=" * 60)
        print(f"{'Index':<20} {'Memory (MB)':<15} {'Efficiency':<15} {'Insert/s':<15}")
        print("-" * 65)
        
        for result in results:
            print(f"{result['name']:<20} {result['memory_used']:<15.1f} {result['efficiency']:<15.1f}% {result['vectors_per_sec']:<15.0f}")
        
        # Calculate relative improvements
        faiss_result = results[0]
        ultra_result = results[1]
        
        memory_improvement = faiss_result['memory_used'] / ultra_result['memory_used']
        speed_improvement = ultra_result['vectors_per_sec'] / faiss_result['vectors_per_sec']
        
        print(f"\n📈 IMPROVEMENTS:")
        print(f"  Memory: {memory_improvement:.2f}x better (Ultra-Optimized vs FAISS-Inspired)")
        print(f"  Speed: {speed_improvement:.2f}x faster insertion")
    
    # Explain FAISS differences
    compare_with_faiss_memory()
    
    # Cleanup
    cleanup()
    print(f"\n🧹 Cleanup completed. Final memory: {get_memory_usage():.1f} MB")

if __name__ == "__main__":
    main()
