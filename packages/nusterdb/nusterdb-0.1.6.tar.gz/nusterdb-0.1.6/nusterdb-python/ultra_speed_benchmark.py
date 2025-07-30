#!/usr/bin/env python3
"""
Ultra-Speed Insertion Benchmark for NusterDB vs FAISS
Target: 500,000+ vectors/second insertion speed
"""

import time
import psutil
import numpy as np
import matplotlib.pyplot as plt
import os
import gc
from typing import List, Tuple, Dict, Any
import tracemalloc

# Import our libraries
import nusterdb_python as ndb
import faiss

def measure_memory():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def generate_vectors(num_vectors: int, dimension: int, seed: int = 42) -> np.ndarray:
    """Generate random vectors for testing"""
    np.random.seed(seed)
    vectors = np.random.randn(num_vectors, dimension).astype(np.float32)
    # Normalize vectors for better testing
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    vectors = vectors / norms
    return vectors

def test_nusterdb_insertion_modes(vectors: np.ndarray, test_name: str) -> Dict[str, Any]:
    """Test different NusterDB insertion modes"""
    dimension = vectors.shape[1]
    results = {}
    
    # Test different configurations
    configs = [
        ("UltraHighSpeed", "ultra_high_speed_flat"),
        ("UltraOptimized", "ultra_optimized_flat"), 
        ("FAISSInspired", "faiss_inspired_flat"),
        ("Standard", "flat_index")
    ]
    
    for config_name, index_type in configs:
        print(f"\n=== Testing NusterDB {config_name} ===")
        
        try:
            # Create database with specific configuration
            config = ndb.DatabaseConfig()
            config.index_type = index_type
            config.dimension = dimension
            config.distance_metric = "euclidean"
            
            # Clean up any existing database
            if os.path.exists("ultra_speed_test.db"):
                os.remove("ultra_speed_test.db")
            
            # Measure memory before
            mem_before = measure_memory()
            tracemalloc.start()
            
            # Create database
            db = ndb.Database("ultra_speed_test.db", config)
            
            # Prepare IDs
            ids = list(range(len(vectors)))
            
            # Time the bulk insertion
            start_time = time.time()
            
            # Insert vectors (using bulk insert for maximum speed)
            if hasattr(db, 'bulk_insert'):
                db.bulk_insert(ids, vectors.tolist())
            else:
                # Fallback to individual inserts
                for i, vector in enumerate(vectors):
                    db.insert(i, vector.tolist())
            
            end_time = time.time()
            
            # Measure memory after
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            mem_after = measure_memory()
            
            # Calculate metrics
            total_time = end_time - start_time
            vectors_per_second = len(vectors) / total_time if total_time > 0 else 0
            memory_used = mem_after - mem_before
            
            results[config_name] = {
                'total_time': total_time,
                'vectors_per_second': vectors_per_second,
                'memory_mb': memory_used,
                'peak_memory_mb': peak / 1024 / 1024,
                'memory_per_vector': memory_used * 1024 * 1024 / len(vectors) if len(vectors) > 0 else 0,
                'success': True
            }
            
            print(f"  Time: {total_time:.3f}s")
            print(f"  Speed: {vectors_per_second:,.0f} vectors/sec")
            print(f"  Memory: {memory_used:.1f} MB ({memory_used * 1024 / len(vectors):.1f} KB/vector)")
            print(f"  Peak Memory: {peak / 1024 / 1024:.1f} MB")
            
            # Clean up
            del db
            if os.path.exists("ultra_speed_test.db"):
                os.remove("ultra_speed_test.db")
                
        except Exception as e:
            print(f"  ERROR: {e}")
            results[config_name] = {
                'total_time': float('inf'),
                'vectors_per_second': 0,
                'memory_mb': float('inf'),
                'memory_per_vector': float('inf'),
                'success': False,
                'error': str(e)
            }
        
        gc.collect()
        time.sleep(1)  # Brief pause between tests
    
    return results

def test_faiss_insertion(vectors: np.ndarray, test_name: str) -> Dict[str, Any]:
    """Test FAISS insertion performance"""
    dimension = vectors.shape[1]
    results = {}
    
    # Test different FAISS index types
    index_configs = [
        ("FAISS_Flat", lambda d: faiss.IndexFlatL2(d)),
        ("FAISS_IVF", lambda d: faiss.index_factory(d, "IVF100,Flat")),
        ("FAISS_HNSW", lambda d: faiss.IndexHNSWFlat(d, 32)),
    ]
    
    for config_name, index_factory in index_configs:
        print(f"\n=== Testing {config_name} ===")
        
        try:
            # Measure memory before
            mem_before = measure_memory()
            tracemalloc.start()
            
            # Create FAISS index
            index = index_factory(dimension)
            
            # For IVF, we need to train first
            if "IVF" in config_name:
                print("  Training IVF index...")
                train_vectors = vectors[:min(10000, len(vectors))]
                index.train(train_vectors)
            
            # Time the insertion
            start_time = time.time()
            
            # Add vectors to FAISS index
            index.add(vectors)
            
            end_time = time.time()
            
            # Measure memory after
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            mem_after = measure_memory()
            
            # Calculate metrics
            total_time = end_time - start_time
            vectors_per_second = len(vectors) / total_time if total_time > 0 else 0
            memory_used = mem_after - mem_before
            
            results[config_name] = {
                'total_time': total_time,
                'vectors_per_second': vectors_per_second,
                'memory_mb': memory_used,
                'peak_memory_mb': peak / 1024 / 1024,
                'memory_per_vector': memory_used * 1024 * 1024 / len(vectors) if len(vectors) > 0 else 0,
                'success': True,
                'index_size': index.ntotal
            }
            
            print(f"  Time: {total_time:.3f}s")
            print(f"  Speed: {vectors_per_second:,.0f} vectors/sec")
            print(f"  Memory: {memory_used:.1f} MB ({memory_used * 1024 / len(vectors):.1f} KB/vector)")
            print(f"  Peak Memory: {peak / 1024 / 1024:.1f} MB")
            print(f"  Index size: {index.ntotal}")
            
            # Clean up
            del index
            
        except Exception as e:
            print(f"  ERROR: {e}")
            results[config_name] = {
                'total_time': float('inf'),
                'vectors_per_second': 0,
                'memory_mb': float('inf'),
                'memory_per_vector': float('inf'),
                'success': False,
                'error': str(e)
            }
        
        gc.collect()
        time.sleep(1)
    
    return results

def create_comparison_plots(all_results: Dict[str, Dict[str, Any]], test_configs: List[Tuple[int, int]]):
    """Create comparison plots for speed and memory"""
    
    # Prepare data for plotting
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    
    # Plot 1: Insertion Speed Comparison
    test_names = list(all_results.keys())
    systems = set()
    for results in all_results.values():
        systems.update(results.keys())
    systems = sorted(list(systems))
    
    x = np.arange(len(test_names))
    width = 0.8 / len(systems)
    
    for i, system in enumerate(systems):
        speeds = []
        for test_name in test_names:
            if system in all_results[test_name] and all_results[test_name][system]['success']:
                speeds.append(all_results[test_name][system]['vectors_per_second'])
            else:
                speeds.append(0)
        
        ax1.bar(x + i * width, speeds, width, label=system, color=colors[i])
    
    ax1.set_xlabel('Test Configuration')
    ax1.set_ylabel('Vectors/Second')
    ax1.set_title('Insertion Speed Comparison')
    ax1.set_xticks(x + width * (len(systems) - 1) / 2)
    ax1.set_xticklabels([name.replace('_', '\n') for name in test_names], rotation=45)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Add horizontal line at 500K vectors/sec target
    ax1.axhline(y=500000, color='red', linestyle='--', alpha=0.7, label='500K target')
    
    # Plot 2: Memory Usage Comparison
    for i, system in enumerate(systems):
        memory_usage = []
        for test_name in test_names:
            if system in all_results[test_name] and all_results[test_name][system]['success']:
                memory_usage.append(all_results[test_name][system]['memory_mb'])
            else:
                memory_usage.append(0)
        
        ax2.bar(x + i * width, memory_usage, width, label=system, color=colors[i])
    
    ax2.set_xlabel('Test Configuration')
    ax2.set_ylabel('Memory Usage (MB)')
    ax2.set_title('Memory Usage Comparison')
    ax2.set_xticks(x + width * (len(systems) - 1) / 2)
    ax2.set_xticklabels([name.replace('_', '\n') for name in test_names], rotation=45)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Memory Efficiency (KB per vector)
    for i, system in enumerate(systems):
        efficiency = []
        for test_name in test_names:
            if system in all_results[test_name] and all_results[test_name][system]['success']:
                efficiency.append(all_results[test_name][system]['memory_per_vector'] / 1024)  # Convert to KB
            else:
                efficiency.append(0)
        
        ax3.bar(x + i * width, efficiency, width, label=system, color=colors[i])
    
    ax3.set_xlabel('Test Configuration')
    ax3.set_ylabel('Memory per Vector (KB)')
    ax3.set_title('Memory Efficiency Comparison')
    ax3.set_xticks(x + width * (len(systems) - 1) / 2)
    ax3.set_xticklabels([name.replace('_', '\n') for name in test_names], rotation=45)
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Speed vs Memory scatter plot (for largest test)
    largest_test = max(test_names, key=lambda x: int(x.split('_')[0]))
    
    for system in systems:
        if system in all_results[largest_test] and all_results[largest_test][system]['success']:
            result = all_results[largest_test][system]
            ax4.scatter(result['vectors_per_second'], result['memory_per_vector'] / 1024, 
                       s=100, label=system, alpha=0.7)
            
            # Annotate point
            ax4.annotate(system, 
                        (result['vectors_per_second'], result['memory_per_vector'] / 1024),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax4.set_xlabel('Insertion Speed (vectors/sec)')
    ax4.set_ylabel('Memory per Vector (KB)')
    ax4.set_title(f'Speed vs Memory Efficiency ({largest_test})')
    ax4.grid(True, alpha=0.3)
    ax4.axvline(x=500000, color='red', linestyle='--', alpha=0.7, label='500K target')
    
    plt.tight_layout()
    plt.savefig('ultra_speed_benchmark_results.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_summary_table(all_results: Dict[str, Dict[str, Any]]):
    """Print a comprehensive summary table"""
    print("\n" + "="*100)
    print("ULTRA-SPEED INSERTION BENCHMARK SUMMARY")
    print("="*100)
    
    # Find the best performer for each metric
    best_speed = 0
    best_speed_system = ""
    best_memory = float('inf')
    best_memory_system = ""
    
    for test_name, results in all_results.items():
        print(f"\n{test_name.upper()}:")
        print("-" * 50)
        print(f"{'System':<20} {'Speed (K/s)':<12} {'Memory (MB)':<12} {'KB/vector':<12} {'Status':<10}")
        print("-" * 50)
        
        for system, result in results.items():
            if result['success']:
                speed_k = result['vectors_per_second'] / 1000
                memory_mb = result['memory_mb']
                kb_per_vector = result['memory_per_vector'] / 1024
                status = "✓"
                
                # Track best performers
                if result['vectors_per_second'] > best_speed:
                    best_speed = result['vectors_per_second']
                    best_speed_system = f"{system} ({test_name})"
                
                if result['memory_per_vector'] < best_memory and result['memory_per_vector'] > 0:
                    best_memory = result['memory_per_vector']
                    best_memory_system = f"{system} ({test_name})"
                
                print(f"{system:<20} {speed_k:<12.1f} {memory_mb:<12.1f} {kb_per_vector:<12.1f} {status:<10}")
            else:
                print(f"{system:<20} {'ERROR':<12} {'ERROR':<12} {'ERROR':<12} {'✗':<10}")
    
    print("\n" + "="*100)
    print("OVERALL BEST PERFORMERS:")
    print(f"  Fastest Insertion: {best_speed_system} - {best_speed:,.0f} vectors/sec")
    print(f"  Most Memory Efficient: {best_memory_system} - {best_memory/1024:.1f} KB/vector") 
    print(f"  Target Achievement: {'✓ ACHIEVED' if best_speed >= 500000 else '✗ NOT REACHED'} (Target: 500K vectors/sec)")
    print("="*100)

def main():
    """Main benchmark execution"""
    print("Ultra-Speed Insertion Benchmark: NusterDB vs FAISS")
    print("Target: 500,000+ vectors/second insertion speed")
    print("="*80)
    
    # Test configurations: (num_vectors, dimension)
    test_configs = [
        (10000, 128),    # Small test
        (50000, 128),    # Medium test  
        (100000, 128),   # Large test
        (500000, 128),   # Ultra large test
        (1000000, 128),  # Million vector test
    ]
    
    all_results = {}
    
    for num_vectors, dimension in test_configs:
        test_name = f"{num_vectors}_{dimension}d"
        print(f"\n{'='*80}")
        print(f"TESTING: {num_vectors:,} vectors × {dimension}D")
        print(f"{'='*80}")
        
        # Generate test vectors
        print("Generating test vectors...")
        vectors = generate_vectors(num_vectors, dimension)
        print(f"Generated {len(vectors)} vectors of dimension {dimension}")
        
        # Test NusterDB
        print("\n--- Testing NusterDB ---")
        nuster_results = test_nusterdb_insertion_modes(vectors, test_name)
        
        # Test FAISS
        print("\n--- Testing FAISS ---")
        faiss_results = test_faiss_insertion(vectors, test_name)
        
        # Combine results
        all_results[test_name] = {**nuster_results, **faiss_results}
        
        # Clean up vectors
        del vectors
        gc.collect()
        
        print(f"\nCompleted test: {test_name}")
    
    # Create visualizations and summary
    print("\nGenerating comparison plots...")
    create_comparison_plots(all_results, test_configs)
    
    print_summary_table(all_results)
    
    print("\nBenchmark completed! Check 'ultra_speed_benchmark_results.png' for visualizations.")

if __name__ == "__main__":
    main()
