#!/usr/bin/env python3
"""
High-Performance Insertion Benchmark for NusterDB
Tests our new UltraFastFlatIndex and OptimizedFlatIndex implementations
"""

import time
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import nusterdb
    NUSTERDB_AVAILABLE = True
except ImportError:
    print("NusterDB not available - please build the Python bindings")
    NUSTERDB_AVAILABLE = False
    sys.exit(1)

def generate_vectors(n_vectors, dim):
    """Generate random test vectors"""
    print(f"Generating {n_vectors:,} vectors of dimension {dim}...")
    vectors = []
    for i in range(n_vectors):
        vector = [random.gauss(0, 1) for _ in range(dim)]
        # Normalize
        norm = sum(x*x for x in vector) ** 0.5
        if norm > 0:
            vector = [x/norm for x in vector]
        vectors.append(vector)
    return vectors

def benchmark_insertion(index_type, vectors, batch_size=1000):
    """Benchmark insertion performance for a specific index type"""
    n_vectors = len(vectors)
    dim = len(vectors[0])
    
    print(f"\n=== {index_type} Index Insertion Benchmark ===")
    print(f"Vectors: {n_vectors:,}, Dimensions: {dim}, Batch Size: {batch_size:,}")
    
    # Create index
    start_time = time.time()
    try:
        if index_type == "UltraFastFlat":
            config = {
                'dimension': dim,
                'index_type': 'UltraFastFlat',
                'metric': 'euclidean'
            }
        elif index_type == "OptimizedFlat":
            config = {
                'dimension': dim,
                'index_type': 'OptimizedFlat',
                'metric': 'euclidean'
            }
        else:
            config = {
                'dimension': dim,
                'index_type': 'Flat',
                'metric': 'euclidean'
            }
        
        index = nusterdb.NusterDB(config)
        creation_time = time.time() - start_time
        print(f"Index creation time: {creation_time:.4f}s")
        
    except Exception as e:
        print(f"❌ Failed to create {index_type} index: {e}")
        return None
    
    # Insertion benchmark
    total_insertion_time = 0
    successful_insertions = 0
    
    print("Starting insertion benchmark...")
    
    for i in range(0, n_vectors, batch_size):
        batch_end = min(i + batch_size, n_vectors)
        batch_vectors = vectors[i:batch_end]
        
        batch_start = time.time()
        
        # Insert batch
        try:
            for j, vector in enumerate(batch_vectors):
                index.insert(i + j, vector)
                successful_insertions += 1
        except Exception as e:
            print(f"❌ Insertion failed at vector {i + j}: {e}")
            break
        
        batch_time = time.time() - batch_start
        total_insertion_time += batch_time
        
        # Progress update
        if (i // batch_size) % 10 == 0 or batch_end == n_vectors:
            progress = (batch_end / n_vectors) * 100
            current_rate = len(batch_vectors) / batch_time if batch_time > 0 else 0
            overall_rate = successful_insertions / total_insertion_time if total_insertion_time > 0 else 0
            print(f"Progress: {progress:5.1f}% | Batch rate: {current_rate:8.0f} vec/s | Overall: {overall_rate:8.0f} vec/s")
    
    # Final results
    if total_insertion_time > 0:
        overall_rate = successful_insertions / total_insertion_time
        print(f"\n📊 Final Results:")
        print(f"✅ Successfully inserted: {successful_insertions:,} vectors")
        print(f"⏱️  Total insertion time: {total_insertion_time:.4f}s")
        print(f"🚀 Overall insertion rate: {overall_rate:.0f} vectors/sec")
        print(f"📈 Index size: {index.len()} vectors")
        
        # Quick search test
        if successful_insertions > 0:
            print(f"\n🔍 Quick search test...")
            search_start = time.time()
            query = vectors[0]  # Use first vector as query
            results = index.search(query, 5)
            search_time = time.time() - search_start
            print(f"Search time: {search_time*1000:.2f}ms")
            print(f"Results: {len(results)} neighbors found")
        
        return {
            'type': index_type,
            'vectors': successful_insertions,
            'insertion_time': total_insertion_time,
            'insertion_rate': overall_rate,
            'creation_time': creation_time,
            'search_time': search_time if 'search_time' in locals() else 0
        }
    else:
        print(f"❌ No successful insertions for {index_type}")
        return None

def run_performance_comparison():
    """Run comprehensive performance comparison"""
    print("🚀 NusterDB High-Performance Insertion Benchmark")
    print("=" * 60)
    
    # Test configuration
    dimensions = [128]
    test_sizes = [50000]  # 50K vectors for initial testing
    batch_size = 5000
    
    # Index types to test
    index_types = ["Flat", "OptimizedFlat", "UltraFastFlat"]
    
    all_results = []
    
    for dim in dimensions:
        for n_vectors in test_sizes:
            print(f"\n📊 Testing {n_vectors:,} vectors, {dim} dimensions")
            print("-" * 60)
            
            # Generate test data once
            vectors = generate_vectors(n_vectors, dim)
            
            results_for_test = []
            
            # Test each index type
            for index_type in index_types:
                print(f"\n🔬 Testing {index_type}...")
                result = benchmark_insertion(index_type, vectors, batch_size)
                if result:
                    results_for_test.append(result)
                    all_results.append(result)
                
                # Small delay between tests
                time.sleep(1)
            
            # Compare results for this test
            if len(results_for_test) > 1:
                print(f"\n📋 Comparison for {n_vectors:,} vectors, {dim}D:")
                print("-" * 50)
                print(f"{'Index Type':<15} {'Rate (vec/s)':<12} {'Time (s)':<10} {'Speedup':<8}")
                print("-" * 50)
                
                # Find baseline (regular Flat)
                baseline_rate = None
                for r in results_for_test:
                    if r['type'] == 'Flat':
                        baseline_rate = r['insertion_rate']
                        break
                
                for result in results_for_test:
                    rate = result['insertion_rate']
                    time_taken = result['insertion_time']
                    
                    if baseline_rate and baseline_rate > 0:
                        speedup = f"{rate/baseline_rate:.1f}x"
                    else:
                        speedup = "N/A"
                    
                    print(f"{result['type']:<15} {rate:<12.0f} {time_taken:<10.2f} {speedup:<8}")
    
    # Overall summary
    if all_results:
        print(f"\n🏆 FINAL PERFORMANCE SUMMARY")
        print("=" * 60)
        
        # Group by type
        type_results = {}
        for result in all_results:
            t = result['type']
            if t not in type_results:
                type_results[t] = []
            type_results[t].append(result['insertion_rate'])
        
        print(f"{'Index Type':<15} {'Avg Rate (vec/s)':<18} {'Best Rate (vec/s)':<18}")
        print("-" * 55)
        
        for index_type, rates in type_results.items():
            avg_rate = sum(rates) / len(rates)
            best_rate = max(rates)
            print(f"{index_type:<15} {avg_rate:<18.0f} {best_rate:<18.0f}")
        
        # Find the best performer
        best_result = max(all_results, key=lambda x: x['insertion_rate'])
        print(f"\n🥇 Best Performance: {best_result['type']} at {best_result['insertion_rate']:.0f} vectors/sec")
        
        # Performance improvement analysis
        flat_rates = type_results.get('Flat', [0])
        ultra_rates = type_results.get('UltraFastFlat', [0])
        optimized_rates = type_results.get('OptimizedFlat', [0])
        
        if flat_rates[0] > 0:
            if ultra_rates and ultra_rates[0] > 0:
                ultra_improvement = (max(ultra_rates) / max(flat_rates)) - 1
                print(f"📈 UltraFastFlat improvement: {ultra_improvement*100:.1f}%")
            
            if optimized_rates and optimized_rates[0] > 0:
                optimized_improvement = (max(optimized_rates) / max(flat_rates)) - 1
                print(f"📈 OptimizedFlat improvement: {optimized_improvement*100:.1f}%")
    
    return all_results

if __name__ == "__main__":
    if not NUSTERDB_AVAILABLE:
        print("❌ NusterDB is not available. Please ensure the Python bindings are built.")
        sys.exit(1)
    
    print("Starting NusterDB high-performance insertion benchmark...")
    results = run_performance_comparison()
    
    if results:
        print(f"\n✅ Benchmark completed successfully!")
        print(f"📊 Total tests run: {len(results)}")
    else:
        print(f"\n❌ Benchmark failed - no results obtained")
