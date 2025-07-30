#!/usr/bin/env python3
"""
Quick Performance Test for Optimized NusterDB
Tests the SIMD and performance improvements
"""

import time
import random
import sys
import psutil
from typing import List, Dict, Any

# Import NusterDB
try:
    import nusterdb
    print("✅ NusterDB imported successfully")
except ImportError as e:
    print(f"❌ Failed to import NusterDB: {e}")
    sys.exit(1)

# Try to import FAISS for comparison
try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
    print("✅ FAISS available for comparison")
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not available")

def get_memory_usage() -> float:
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def generate_random_vectors(n: int, dim: int) -> List[List[float]]:
    """Generate random vectors for testing"""
    print(f"🔧 Generating {n:,} random vectors of dimension {dim}...")
    vectors = []
    for i in range(n):
        vector = [random.gauss(0, 1) for _ in range(dim)]
        # Normalize for better comparison
        norm = sum(x*x for x in vector) ** 0.5
        if norm > 0:
            vector = [x/norm for x in vector]
        vectors.append(vector)
    return vectors

def benchmark_nusterdb(vectors: List[List[float]], queries: List[List[float]], k: int = 10) -> Dict[str, Any]:
    """Benchmark NusterDB performance"""
    print(f"🚀 Benchmarking NusterDB (Optimized)")
    print(f"  Dataset: {len(vectors):,} vectors, {len(vectors[0])}D")
    print(f"  Queries: {len(queries):,} queries, k={k}")
    
    # Setup
    dim = len(vectors[0])
    metadata = nusterdb.Metadata.with_data({"test": "optimized_benchmark"})
    
    # Create database
    db = nusterdb.NusterDB.simple("./test_opt_db", dim=dim, use_hnsw=False)  # Use flat index
    
    # Measure insertion
    start_memory = get_memory_usage()
    start_time = time.time()
    
    print(f"  📥 Inserting vectors...")
    for i, vector in enumerate(vectors):
        db.add(i, nusterdb.Vector(vector), metadata)
        if (i + 1) % 1000 == 0:
            print(f"    Progress: {i+1:,}/{len(vectors):,} vectors")
    
    insert_time = time.time() - start_time
    insert_memory = get_memory_usage() - start_memory
    insert_throughput = len(vectors) / insert_time
    
    print(f"  ✅ Insertion completed in {insert_time:.2f}s")
    print(f"  📊 Insert throughput: {insert_throughput:,.0f} vectors/sec")
    print(f"  💾 Memory used: {insert_memory:.1f} MB")
    
    # Measure search
    start_time = time.time()
    
    print(f"  🔍 Searching...")
    total_results = 0
    for i, query in enumerate(queries):
        results = db.search(nusterdb.Vector(query), k)
        total_results += len(results)
        if (i + 1) % 10 == 0:
            print(f"    Progress: {i+1:,}/{len(queries):,} queries")
    
    search_time = time.time() - start_time
    search_memory = get_memory_usage() - start_memory
    search_throughput = len(queries) / search_time
    
    print(f"  ✅ Search completed in {search_time:.2f}s")
    print(f"  📊 Search throughput: {search_throughput:,.0f} queries/sec")
    print(f"  🎯 Average results per query: {total_results / len(queries):.1f}")
    
    # Cleanup
    db.close()
    import shutil
    try:
        shutil.rmtree("./test_opt_db")
    except:
        pass
    
    return {
        "database": "NusterDB-Optimized",
        "vectors": len(vectors),
        "dimension": dim,
        "queries": len(queries),
        "insert_time": insert_time,
        "insert_throughput": insert_throughput,
        "insert_memory": insert_memory,
        "search_time": search_time,
        "search_throughput": search_throughput,
        "search_memory": search_memory,
        "avg_results": total_results / len(queries)
    }

def benchmark_faiss(vectors: List[List[float]], queries: List[List[float]], k: int = 10) -> Dict[str, Any]:
    """Benchmark FAISS for comparison"""
    if not FAISS_AVAILABLE:
        return {"error": "FAISS not available"}
    
    print(f"⚡ Benchmarking FAISS")
    print(f"  Dataset: {len(vectors):,} vectors, {len(vectors[0])}D")
    print(f"  Queries: {len(queries):,} queries, k={k}")
    
    # Convert to numpy arrays
    vectors_np = np.array(vectors, dtype=np.float32)
    queries_np = np.array(queries, dtype=np.float32)
    
    # Setup FAISS
    dim = vectors_np.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product for normalized vectors
    
    # Set threads for optimal performance
    faiss.omp_set_num_threads(psutil.cpu_count())
    
    # Measure insertion
    start_memory = get_memory_usage()
    start_time = time.time()
    
    print(f"  📥 Inserting vectors...")
    index.add(vectors_np)
    
    insert_time = time.time() - start_time
    insert_memory = get_memory_usage() - start_memory
    insert_throughput = len(vectors) / insert_time
    
    print(f"  ✅ Insertion completed in {insert_time:.2f}s")
    print(f"  📊 Insert throughput: {insert_throughput:,.0f} vectors/sec")
    print(f"  💾 Memory used: {insert_memory:.1f} MB")
    
    # Measure search
    start_time = time.time()
    
    print(f"  🔍 Searching...")
    distances, indices = index.search(queries_np, k)
    
    search_time = time.time() - start_time
    search_memory = get_memory_usage() - start_memory
    search_throughput = len(queries) / search_time
    
    print(f"  ✅ Search completed in {search_time:.2f}s")
    print(f"  📊 Search throughput: {search_throughput:,.0f} queries/sec")
    print(f"  🎯 Results per query: {indices.shape[1]}")
    
    return {
        "database": "FAISS",
        "vectors": len(vectors),
        "dimension": dim,
        "queries": len(queries),
        "insert_time": insert_time,
        "insert_throughput": insert_throughput,
        "insert_memory": insert_memory,
        "search_time": search_time,
        "search_throughput": search_throughput,
        "search_memory": search_memory,
        "avg_results": indices.shape[1]
    }

def main():
    """Main benchmark function"""
    print("🚀 NusterDB Optimized Performance Test")
    print("=" * 60)
    
    # Test configurations
    test_configs = [
        {"n_vectors": 1000, "dim": 128, "n_queries": 100},
        {"n_vectors": 10000, "dim": 128, "n_queries": 100},
        {"n_vectors": 100000, "dim": 128, "n_queries": 100},
    ]
    
    # Add 1M test if we have enough memory
    available_memory = psutil.virtual_memory().available / 1024**3  # GB
    if available_memory > 4:  # At least 4GB available
        test_configs.append({"n_vectors": 1000000, "dim": 128, "n_queries": 100})
    
    results = []
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n{'='*60}")
        print(f"🔬 Test {i}/{len(test_configs)}: {config['n_vectors']:,} vectors, {config['dim']}D")
        print(f"{'='*60}")
        
        # Generate test data
        vectors = generate_random_vectors(config['n_vectors'], config['dim'])
        queries = generate_random_vectors(config['n_queries'], config['dim'])
        
        # Benchmark NusterDB
        try:
            print(f"\n🧪 Testing NusterDB...")
            nuster_result = benchmark_nusterdb(vectors, queries)
            results.append(nuster_result)
            print(f"✅ NusterDB completed successfully")
        except Exception as e:
            print(f"❌ NusterDB failed: {e}")
        
        # Benchmark FAISS for comparison
        if FAISS_AVAILABLE:
            try:
                print(f"\n🧪 Testing FAISS...")
                faiss_result = benchmark_faiss(vectors, queries)
                results.append(faiss_result)
                print(f"✅ FAISS completed successfully")
            except Exception as e:
                print(f"❌ FAISS failed: {e}")
        
        # Print comparison if both succeeded
        if len(results) >= 2:
            nuster = results[-2] if not FAISS_AVAILABLE else results[-2]
            faiss_res = results[-1] if FAISS_AVAILABLE else None
            
            print(f"\n📊 PERFORMANCE COMPARISON:")
            print(f"  NusterDB Insert: {nuster['insert_throughput']:,.0f} vec/s")
            if faiss_res:
                print(f"  FAISS Insert:    {faiss_res['insert_throughput']:,.0f} vec/s")
                speedup = faiss_res['insert_throughput'] / nuster['insert_throughput']
                print(f"  FAISS is {speedup:.1f}x faster at insertion")
            
            print(f"  NusterDB Search: {nuster['search_throughput']:,.0f} qry/s")
            if faiss_res:
                print(f"  FAISS Search:    {faiss_res['search_throughput']:,.0f} qry/s")
                speedup = faiss_res['search_throughput'] / nuster['search_throughput']
                print(f"  FAISS is {speedup:.1f}x faster at search")
        
        print(f"\n⏳ Cooling down before next test...")
        time.sleep(2)
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"🏁 BENCHMARK SUMMARY")
    print(f"{'='*60}")
    
    if results:
        print(f"📊 Results for {len(results)} tests:")
        for result in results:
            if 'error' not in result:
                print(f"  {result['database']}: {result['vectors']:,} vectors")
                print(f"    Insert: {result['insert_throughput']:,.0f} vec/s")
                print(f"    Search: {result['search_throughput']:,.0f} qry/s")
                print(f"    Memory: {result['insert_memory']:.1f} MB")
                print()
    
    print(f"✅ Benchmark completed!")

if __name__ == "__main__":
    main()
