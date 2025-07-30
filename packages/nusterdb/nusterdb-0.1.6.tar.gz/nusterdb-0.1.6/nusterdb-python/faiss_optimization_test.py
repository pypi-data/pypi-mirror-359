#!/usr/bin/env python3
"""
FAISS-Inspired NusterDB Optimization Test

This script addresses the key issues identified:
1. Memory usage optimization (FAISS uses ~40% less memory)
2. True bulk insertion of 1M vectors at once (vs 50K chunks)
3. Target 2x+ speed improvement over current implementation

Test Goals:
- Insert 1M vectors in a single bulk operation
- Match or exceed FAISS memory efficiency
- Achieve 2x+ performance improvement
- Test different batch sizes and memory strategies
"""

import time
import psutil
import gc
import numpy as np
import nusterdb

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def test_memory_layout_optimization():
    """Test different memory layouts and their efficiency"""
    print("=== Memory Layout Optimization Test ===")
    
    # Test parameters
    dimensions = [128, 256, 512]
    vector_counts = [100_000, 500_000, 1_000_000]
    
    for dim in dimensions:
        print(f"\n--- Testing dimension: {dim} ---")
        
        for n_vectors in vector_counts:
            print(f"\nTesting {n_vectors:,} vectors of dimension {dim}")
            
            # Generate test data
            vectors = np.random.random((n_vectors, dim)).astype(np.float32)
            ids = list(range(n_vectors))
            
            # Test FAISS-inspired flat index
            start_mem = get_memory_usage()
            gc.collect()
            
            config = nusterdb.DatabaseConfig.faiss_inspired_flat(dim=dim)
            db = nusterdb.NusterDB("test_faiss_mem.db", config)
            
            print(f"Database created, memory: {get_memory_usage() - start_mem:.1f} MB")
            
            # Single bulk insertion (like FAISS)
            start_time = time.time()
            start_insert_mem = get_memory_usage()
            
            # Convert to NusterDB vectors in batches to manage Python memory
            batch_size = 50000  # For conversion only, actual insertion is bulk
            nuster_vectors = []
            
            for i in range(0, n_vectors, batch_size):
                end_idx = min(i + batch_size, n_vectors)
                batch_vectors = [nusterdb.Vector(vec.tolist()) for vec in vectors[i:end_idx]]
                nuster_vectors.extend(batch_vectors)
                
                # Progress tracking
                if i % (batch_size * 4) == 0:
                    progress = (end_idx / n_vectors) * 100
                    current_mem = get_memory_usage()
                    print(f"  Converted {end_idx:,}/{n_vectors:,} vectors ({progress:.1f}%), Memory: {current_mem - start_mem:.1f} MB")
            
            conversion_time = time.time() - start_time
            conversion_mem = get_memory_usage() - start_insert_mem
            
            print(f"Vector conversion completed in {conversion_time:.2f}s, Memory used: {conversion_mem:.1f} MB")
            
            # Now perform the actual bulk insertion - ALL VECTORS AT ONCE
            print("Performing TRUE bulk insertion of ALL vectors...")
            bulk_start_time = time.time()
            bulk_start_mem = get_memory_usage()
            
            try:
                # This is the key: insert ALL vectors in one operation
                inserted_count = db.bulk_add(ids, nuster_vectors)
                
                bulk_time = time.time() - bulk_start_time
                bulk_mem = get_memory_usage() - bulk_start_mem
                
                insertion_rate = n_vectors / bulk_time
                
                print(f"✓ Bulk insertion completed:")
                print(f"  Inserted: {inserted_count:,} vectors")
                print(f"  Time: {bulk_time:.4f}s")
                print(f"  Rate: {insertion_rate:,.0f} vectors/second")
                print(f"  Memory used during insertion: {bulk_mem:.1f} MB")
                
                # Test search performance
                query = np.random.random(dim).astype(np.float32)
                query_vector = nusterdb.Vector(query.tolist())
                
                search_start = time.time()
                results = db.search(query_vector, 10)
                search_time = (time.time() - search_start) * 1000
                
                print(f"  Search time: {search_time:.2f}ms")
                
                # Memory efficiency analysis
                total_mem = get_memory_usage() - start_mem
                theoretical_min = (n_vectors * dim * 4) / (1024 * 1024)  # 4 bytes per float
                memory_overhead = (total_mem / theoretical_min - 1) * 100
                
                print(f"  Total memory usage: {total_mem:.1f} MB")
                print(f"  Theoretical minimum: {theoretical_min:.1f} MB") 
                print(f"  Memory overhead: {memory_overhead:.1f}%")
                
                # Cleanup
                del db
                
            except Exception as e:
                print(f"✗ Bulk insertion failed: {e}")
                
            # Force cleanup
            gc.collect()
            time.sleep(0.5)
            
            if n_vectors >= 1_000_000:  # Only test up to 1M for now
                break

def test_batch_size_optimization():
    """Test optimal batch sizes for bulk insertion"""
    print("\n=== Batch Size Optimization Test ===")
    
    dim = 128
    base_vectors = 100_000
    
    # Test different strategies
    strategies = [
        ("Single Bulk", [base_vectors]),  # All at once
        ("Large Chunks", [50_000, 50_000]),  # Current approach
        ("Medium Chunks", [25_000] * 4),
        ("Small Chunks", [10_000] * 10),
    ]
    
    for strategy_name, chunk_sizes in strategies:
        print(f"\n--- Testing: {strategy_name} ---")
        
        # Generate test data
        total_vectors = sum(chunk_sizes)
        vectors = np.random.random((total_vectors, dim)).astype(np.float32)
        
        start_mem = get_memory_usage()
        config = nusterdb.DatabaseConfig.faiss_inspired_flat(dim=dim)
        db = nusterdb.NusterDB(f"test_batch_{strategy_name.replace(' ', '_').lower()}.db", config)
        
        total_time = 0
        current_idx = 0
        
        for chunk_size in chunk_sizes:
            end_idx = current_idx + chunk_size
            chunk_vectors = vectors[current_idx:end_idx]
            chunk_ids = list(range(current_idx, end_idx))
            
            nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in chunk_vectors]
            
            start_time = time.time()
            inserted = db.bulk_add(chunk_ids, nuster_vectors)
            chunk_time = time.time() - start_time
            
            total_time += chunk_time
            current_idx = end_idx
            
            print(f"  Chunk {chunk_size:,} vectors: {chunk_time:.4f}s ({chunk_size/chunk_time:,.0f} vec/s)")
        
        overall_rate = total_vectors / total_time
        total_mem = get_memory_usage() - start_mem
        
        print(f"  Overall rate: {overall_rate:,.0f} vectors/second")
        print(f"  Total time: {total_time:.4f}s") 
        print(f"  Memory usage: {total_mem:.1f} MB")
        
        # Quick search test
        query = np.random.random(dim).astype(np.float32)
        query_vector = nusterdb.Vector(query.tolist())
        
        search_start = time.time()
        results = db.search(query_vector, 5)
        search_time = (time.time() - search_start) * 1000
        
        print(f"  Search time: {search_time:.2f}ms")
        
        del db
        gc.collect()

def benchmark_vs_baseline():
    """Benchmark new FAISS-inspired index vs previous implementations"""
    print("\n=== Index Type Comparison ===")
    
    dim = 128
    n_vectors = 250_000  # Reasonable size for comparison
    
    vectors = np.random.random((n_vectors, dim)).astype(np.float32)
    ids = list(range(n_vectors))
    nuster_vectors = [nusterdb.Vector(vec.tolist()) for vec in vectors]
    
    index_types = [
        ("SuperOptimizedFlat", nusterdb.DatabaseConfig.super_optimized_flat(dim)),
        ("FaissInspiredFlat", nusterdb.DatabaseConfig.faiss_inspired_flat(dim)),
    ]
    
    results = {}
    
    for index_name, config in index_types:
        print(f"\n--- Testing {index_name} ---")
        
        start_mem = get_memory_usage()
        db = nusterdb.NusterDB(f"test_{index_name.lower()}.db", config)
        
        # Insertion test
        start_time = time.time()
        inserted = db.bulk_add(ids, nuster_vectors)
        insert_time = time.time() - start_time
        
        insert_rate = n_vectors / insert_time
        memory_used = get_memory_usage() - start_mem
        
        # Search test
        query = np.random.random(dim).astype(np.float32)
        query_vector = nusterdb.Vector(query.tolist())
        
        search_times = []
        for _ in range(5):
            start_search = time.time()
            results_list = db.search(query_vector, 10)
            search_time = (time.time() - start_search) * 1000
            search_times.append(search_time)
        
        avg_search_time = sum(search_times) / len(search_times)
        
        results[index_name] = {
            'insert_rate': insert_rate,
            'memory_mb': memory_used,
            'search_ms': avg_search_time
        }
        
        print(f"  Insertion rate: {insert_rate:,.0f} vectors/second")
        print(f"  Memory usage: {memory_used:.1f} MB")
        print(f"  Search time: {avg_search_time:.2f}ms")
        
        del db
        gc.collect()
    
    # Compare results
    print("\n=== Performance Comparison ===")
    if 'SuperOptimizedFlat' in results and 'FaissInspiredFlat' in results:
        super_result = results['SuperOptimizedFlat']
        faiss_result = results['FaissInspiredFlat']
        
        insert_improvement = faiss_result['insert_rate'] / super_result['insert_rate']
        memory_improvement = super_result['memory_mb'] / faiss_result['memory_mb']
        search_improvement = super_result['search_ms'] / faiss_result['search_ms']
        
        print(f"FaissInspiredFlat vs SuperOptimizedFlat:")
        print(f"  Insertion speed: {insert_improvement:.2f}x {'improvement' if insert_improvement > 1 else 'slower'}")
        print(f"  Memory efficiency: {memory_improvement:.2f}x {'better' if memory_improvement > 1 else 'worse'}")
        print(f"  Search speed: {search_improvement:.2f}x {'faster' if search_improvement > 1 else 'slower'}")

def main():
    """Main test runner"""
    print("🚀 FAISS-Inspired NusterDB Optimization Tests")
    print("=" * 60)
    
    try:
        # Test 1: Memory layout optimization with true bulk insertion
        test_memory_layout_optimization()
        
        # Test 2: Batch size optimization  
        test_batch_size_optimization()
        
        # Test 3: Benchmark vs existing implementations
        benchmark_vs_baseline()
        
        print("\n" + "=" * 60)
        print("✅ All optimization tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
