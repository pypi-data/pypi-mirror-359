#!/usr/bin/env python3
"""
Large-scale performance benchmark comparing NusterDB's new index types with FAISS.
This script tests insertion and search performance on larger datasets.
"""

import os
import sys  
import shutil
import time
import random
import gc
from typing import List, Tuple, Dict, Any

# Try to import FAISS, but make it optional
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    print("FAISS not available - will only test NusterDB")
    FAISS_AVAILABLE = False

import nusterdb

def create_test_vectors(num_vectors: int, dim: int, seed: int = 42) -> List[List[float]]:
    """Create test vectors with reproducible random data."""
    random.seed(seed)
    vectors = []
    for i in range(num_vectors):
        data = [random.gauss(0, 1) for _ in range(dim)]
        vectors.append(data)
    return vectors

def benchmark_nusterdb_index(index_type: str, vectors: List[List[float]], dim: int, 
                           num_search_queries: int = 100) -> Dict[str, Any]:
    """Benchmark a NusterDB index type."""
    db_path = f"./benchmark_db_{index_type.replace('-', '_')}"
    
    # Cleanup
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    
    try:
        print(f"\n--- Benchmarking NusterDB {index_type} ---")
        
        # Create database
        if index_type == "flat":
            db = nusterdb.NusterDB.simple(db_path, dim, False)
        elif index_type == "hnsw":
            db = nusterdb.NusterDB.simple(db_path, dim, True)
        elif index_type == "optimized-flat":
            db = nusterdb.NusterDB.optimized_flat(db_path, dim)
        elif index_type == "ultra-fast-flat":
            db = nusterdb.NusterDB.ultra_fast_flat(db_path, dim)
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        print(f"Created {index_type} database with dimension {dim}")
        
        # Insertion benchmark
        print(f"Inserting {len(vectors)} vectors...")
        start_time = time.time()
        
        for i, vector_data in enumerate(vectors):
            vector = nusterdb.Vector(vector_data)
            metadata = nusterdb.Metadata()
            metadata.set("id", str(i))
            metadata.set("category", f"cat_{i % 10}")
            
            db.add(i, vector, metadata)
            
            if (i + 1) % 5000 == 0:
                print(f"  Inserted {i + 1}/{len(vectors)} vectors...")
        
        insertion_time = time.time() - start_time
        insertion_rate = len(vectors) / insertion_time
        
        print(f"Insertion completed: {insertion_time:.2f}s ({insertion_rate:.0f} vec/s)")
        
        # Search benchmark
        print(f"Running {num_search_queries} search queries...")
        query_vectors = vectors[:num_search_queries]  
        search_times = []
        
        for i, query_data in enumerate(query_vectors):
            query_vector = nusterdb.Vector(query_data)
            
            start_time = time.time()
            results = db.search(query_vector, k=10)
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{num_search_queries} queries...")
        
        avg_search_time = sum(search_times) / len(search_times)
        total_search_time = sum(search_times)
        search_qps = num_search_queries / total_search_time
        
        print(f"Search completed: avg {avg_search_time*1000:.2f}ms, {search_qps:.0f} QPS")
        
        return {
            "index_type": index_type,
            "library": "NusterDB",
            "num_vectors": len(vectors),
            "dimension": dim,
            "insertion_time": insertion_time,
            "insertion_rate": insertion_rate,
            "avg_search_time": avg_search_time,
            "search_qps": search_qps,
            "success": True
        }
        
    except Exception as e:
        print(f"Error benchmarking NusterDB {index_type}: {e}")
        return {
            "index_type": index_type,
            "library": "NusterDB",
            "error": str(e),
            "success": False
        }
    
    finally:
        if os.path.exists(db_path):
            shutil.rmtree(db_path)

def benchmark_faiss(vectors: List[List[float]], dim: int, 
                   num_search_queries: int = 100) -> Dict[str, Any]:
    """Benchmark FAISS IndexFlatL2."""
    if not FAISS_AVAILABLE:
        return {
            "index_type": "FlatL2", 
            "library": "FAISS",
            "error": "FAISS not available",
            "success": False
        }
    
    try:
        print(f"\n--- Benchmarking FAISS FlatL2 ---")
        
        # Convert to numpy array
        import numpy as np
        vectors_np = np.array(vectors, dtype=np.float32)
        
        # Create FAISS index
        index = faiss.IndexFlatL2(dim)
        print(f"Created FAISS FlatL2 index with dimension {dim}")
        
        # Insertion benchmark
        print(f"Inserting {len(vectors)} vectors...")
        start_time = time.time()
        index.add(vectors_np)
        insertion_time = time.time() - start_time
        insertion_rate = len(vectors) / insertion_time
        
        print(f"Insertion completed: {insertion_time:.2f}s ({insertion_rate:.0f} vec/s)")
        
        # Search benchmark
        print(f"Running {num_search_queries} search queries...")
        query_vectors_np = vectors_np[:num_search_queries]
        
        start_time = time.time()
        distances, indices = index.search(query_vectors_np, 10)
        total_search_time = time.time() - start_time
        
        avg_search_time = total_search_time / num_search_queries
        search_qps = num_search_queries / total_search_time
        
        print(f"Search completed: avg {avg_search_time*1000:.2f}ms, {search_qps:.0f} QPS")
        
        return {
            "index_type": "FlatL2",
            "library": "FAISS", 
            "num_vectors": len(vectors),
            "dimension": dim,
            "insertion_time": insertion_time,
            "insertion_rate": insertion_rate,
            "avg_search_time": avg_search_time,
            "search_qps": search_qps,
            "success": True
        }
        
    except Exception as e:
        print(f"Error benchmarking FAISS: {e}")
        return {
            "index_type": "FlatL2",
            "library": "FAISS",
            "error": str(e),
            "success": False
        }

def run_large_scale_benchmark():
    """Run comprehensive large-scale benchmark."""
    print("=" * 80)
    print("NUSTERDB vs FAISS - LARGE SCALE PERFORMANCE BENCHMARK")
    print("=" * 80)
    
    # Test configurations
    configs = [
        {"num_vectors": 10000, "dim": 128, "name": "Small (10K vectors)"},
        {"num_vectors": 50000, "dim": 128, "name": "Medium (50K vectors)"},
        {"num_vectors": 100000, "dim": 128, "name": "Large (100K vectors)"},
    ]
    
    # Add larger config if system can handle it
    try:
        import psutil
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        if available_memory_gb > 4:  # At least 4GB available
            configs.append({"num_vectors": 250000, "dim": 128, "name": "Extra Large (250K vectors)"})
    except ImportError:
        pass
    
    nusterdb_indices = ["optimized-flat", "ultra-fast-flat", "flat"]
    
    all_results = []
    
    for config in configs:
        num_vectors = config["num_vectors"]
        dim = config["dim"]
        name = config["name"]
        
        print(f"\n{'='*60}")
        print(f"BENCHMARK: {name}")
        print(f"Vectors: {num_vectors:,}, Dimension: {dim}")
        print(f"{'='*60}")
        
        # Create test vectors
        print("Generating test vectors...")
        vectors = create_test_vectors(num_vectors, dim)
        num_queries = min(100, num_vectors // 10)
        
        # Benchmark NusterDB indices
        for index_type in nusterdb_indices:
            result = benchmark_nusterdb_index(index_type, vectors, dim, num_queries)
            result.update({"config": name})
            all_results.append(result)
            
            # Memory cleanup
            gc.collect()
        
        # Benchmark FAISS
        faiss_result = benchmark_faiss(vectors, dim, num_queries)
        faiss_result.update({"config": name})
        all_results.append(faiss_result)
        
        # Memory cleanup
        del vectors
        gc.collect()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BENCHMARK RESULTS")
    print("=" * 80)
    
    successful_results = [r for r in all_results if r.get("success", False)]
    
    if successful_results:
        # Group by config
        configs_tested = list(set(r["config"] for r in successful_results))
        
        for config_name in configs_tested:
            config_results = [r for r in successful_results if r["config"] == config_name]
            
            print(f"\n{config_name}:")
            print(f"{'Library':<12} {'Index':<18} {'Insert (vec/s)':<15} {'Search (ms)':<12} {'Search (QPS)':<12}")
            print("-" * 75)
            
            for result in config_results:
                library = result["library"]
                index_type = result["index_type"]
                insertion_rate = result.get("insertion_rate", 0)
                avg_search_time = result.get("avg_search_time", 0) * 1000
                search_qps = result.get("search_qps", 0)
                
                print(f"{library:<12} {index_type:<18} {insertion_rate:<15.0f} {avg_search_time:<12.2f} {search_qps:<12.0f}")
        
        # Overall comparison
        print(f"\n{'='*60}")
        print("OVERALL PERFORMANCE ANALYSIS")
        print(f"{'='*60}")
        
        # Find best performers for largest dataset
        largest_config = max(configs_tested, key=lambda x: int(x.split()[2].strip('(').replace('K', '000').replace('k', '000')))
        largest_results = [r for r in successful_results if r["config"] == largest_config]
        
        if largest_results:
            best_insertion = max(largest_results, key=lambda x: x.get("insertion_rate", 0))
            best_search = min(largest_results, key=lambda x: x.get("avg_search_time", float('inf')))
            
            print(f"\nBest insertion performance ({largest_config}):")
            print(f"  {best_insertion['library']} {best_insertion['index_type']}: {best_insertion['insertion_rate']:.0f} vec/s")
            
            print(f"\nBest search performance ({largest_config}):")
            print(f"  {best_search['library']} {best_search['index_type']}: {best_search['avg_search_time']*1000:.2f} ms")
            
            # Compare NusterDB vs FAISS
            nusterdb_results = [r for r in largest_results if r["library"] == "NusterDB"]
            faiss_results = [r for r in largest_results if r["library"] == "FAISS"]
            
            if nusterdb_results and faiss_results:
                best_nusterdb = max(nusterdb_results, key=lambda x: x.get("insertion_rate", 0))
                faiss_result = faiss_results[0]
                
                insertion_ratio = faiss_result["insertion_rate"] / best_nusterdb["insertion_rate"]
                search_ratio = best_nusterdb["avg_search_time"] / faiss_result["avg_search_time"]
                
                print(f"\nNusterDB vs FAISS Comparison ({largest_config}):")
                print(f"  FAISS insertion is {insertion_ratio:.1f}x faster than best NusterDB")
                print(f"  Best NusterDB search is {search_ratio:.1f}x {'faster' if search_ratio < 1 else 'slower'} than FAISS")
    
    # Print any errors
    failed_results = [r for r in all_results if not r.get("success", False)]
    if failed_results:
        print(f"\nFailed benchmarks:")
        for result in failed_results:
            print(f"- {result['library']} {result['index_type']}: {result.get('error', 'Unknown error')}")
    
    return all_results

if __name__ == "__main__":
    try:
        results = run_large_scale_benchmark()
        
        # Check if our new index types worked
        new_index_types = ["optimized-flat", "ultra-fast-flat"]
        new_results = [r for r in results if r.get("index_type") in new_index_types and r.get("library") == "NusterDB"]
        successful_new = [r for r in new_results if r.get("success", False)]
        
        print(f"\n{'='*60}")
        if len(successful_new) >= len(new_index_types):
            print("✅ SUCCESS: New high-performance index types are working at scale!")
        else:
            print("⚠️  WARNING: Some new index types had issues at scale")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        sys.exit(1)
