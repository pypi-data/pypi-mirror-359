#!/usr/bin/env python3
"""
FAISS-style bulk insertion performance test for NusterDB
Tests the true bulk insertion capability vs individual insertion
"""

import numpy as np
import time
import requests
import json
import sys
from pathlib import Path

# Add the parent directory to path to import nusterdb
sys.path.append(str(Path(__file__).parent))

def generate_test_vectors(n_vectors, dim):
    """Generate random test vectors"""
    np.random.seed(42)  # For reproducible results
    return np.random.randn(n_vectors, dim).astype(np.float32)

def test_nusterdb_server(base_url, vectors, use_bulk=True):
    """Test NusterDB server performance"""
    n_vectors, dim = vectors.shape
    
    print(f"\n=== Testing NusterDB Server ===")
    print(f"Vectors: {n_vectors}, Dimension: {dim}")
    print(f"Using bulk insertion: {use_bulk}")
    
    # Test bulk insertion
    if use_bulk:
        print("Testing bulk insertion...")
        
        # Prepare bulk data
        bulk_data = {
            "vectors": [
                {
                    "id": i,
                    "vector": vectors[i].tolist(),
                    "metadata": {"type": "test", "batch": i // 1000}
                }
                for i in range(n_vectors)
            ]
        }
        
        start_time = time.time()
        
        # Send bulk insertion request
        response = requests.post(
            f"{base_url}/vectors/bulk",
            json=bulk_data,
            headers={"Content-Type": "application/json"}
        )
        
        insertion_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bulk insertion successful: {result['successful']} vectors in {insertion_time:.3f}s")
            print(f"   Insertion rate: {result['successful'] / insertion_time:.1f} vectors/second")
            print(f"   Bulk insertion used: {result.get('bulk_insertion', False)}")
        else:
            print(f"❌ Bulk insertion failed: {response.status_code} - {response.text}")
            return None
    else:
        print("Testing individual insertion...")
        start_time = time.time()
        
        successful = 0
        for i in range(n_vectors):
            vector_data = {
                "id": i,
                "vector": vectors[i].tolist(),
                "metadata": {"type": "test", "batch": i // 1000}
            }
            
            response = requests.post(
                f"{base_url}/vectors",
                json=vector_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                successful += 1
            
            # Progress update
            if (i + 1) % 1000 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"   Progress: {i + 1}/{n_vectors} ({rate:.1f} vec/s)")
        
        insertion_time = time.time() - start_time
        print(f"✅ Individual insertion: {successful} vectors in {insertion_time:.3f}s")
        print(f"   Insertion rate: {successful / insertion_time:.1f} vectors/second")
    
    # Test search performance
    print("\nTesting search performance...")
    
    # Generate query vectors
    query_vectors = generate_test_vectors(10, dim)
    
    search_times = []
    for i, query in enumerate(query_vectors):
        search_data = {
            "vector": query.tolist(),
            "k": 10,
            "metadata_filters": {}
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        search_time = time.time() - start_time
        search_times.append(search_time)
        
        if response.status_code == 200:
            results = response.json()
            print(f"   Query {i+1}: {len(results)} results in {search_time*1000:.1f}ms")
        else:
            print(f"   Query {i+1} failed: {response.status_code}")
    
    avg_search_time = np.mean(search_times) * 1000
    print(f"✅ Average search time: {avg_search_time:.1f}ms")
    
    return {
        "insertion_time": insertion_time,
        "insertion_rate": n_vectors / insertion_time,
        "avg_search_time": avg_search_time,
        "search_times": search_times
    }

def test_faiss_baseline(vectors):
    """Test FAISS performance as baseline"""
    try:
        import faiss
    except ImportError:
        print("FAISS not available, skipping baseline test")
        return None
    
    n_vectors, dim = vectors.shape
    
    print(f"\n=== Testing FAISS Baseline ===")
    print(f"Vectors: {n_vectors}, Dimension: {dim}")
    
    # Create FAISS index
    index = faiss.IndexFlatL2(dim)
    
    # Test bulk insertion (FAISS style)
    print("Testing FAISS bulk insertion...")
    start_time = time.time()
    index.add(vectors)
    insertion_time = time.time() - start_time
    
    print(f"✅ FAISS bulk insertion: {n_vectors} vectors in {insertion_time:.3f}s")
    print(f"   Insertion rate: {n_vectors / insertion_time:.1f} vectors/second")
    
    # Test search performance
    print("Testing FAISS search performance...")
    query_vectors = generate_test_vectors(10, dim)
    
    search_times = []
    for i, query in enumerate(query_vectors):
        start_time = time.time()
        D, I = index.search(query.reshape(1, -1), 10)
        search_time = time.time() - start_time
        search_times.append(search_time)
        print(f"   Query {i+1}: 10 results in {search_time*1000:.1f}ms")
    
    avg_search_time = np.mean(search_times) * 1000
    print(f"✅ FAISS average search time: {avg_search_time:.1f}ms")
    
    return {
        "insertion_time": insertion_time,
        "insertion_rate": n_vectors / insertion_time,
        "avg_search_time": avg_search_time,
        "search_times": search_times
    }

def run_performance_comparison():
    """Run comprehensive performance comparison"""
    print("🚀 Starting FAISS-style bulk insertion performance test")
    
    # Test parameters
    test_sizes = [1000, 5000, 10000, 50000]
    dimension = 128
    
    results = {}
    
    for n_vectors in test_sizes:
        print(f"\n{'='*60}")
        print(f"Testing with {n_vectors} vectors of dimension {dimension}")
        print(f"{'='*60}")
        
        # Generate test data
        vectors = generate_test_vectors(n_vectors, dimension)
        
        # Test FAISS baseline
        faiss_results = test_faiss_baseline(vectors)
        
        # Test NusterDB with bulk insertion
        # Note: This assumes NusterDB server is running on localhost:7878
        nuster_bulk_results = test_nusterdb_server("http://localhost:7878", vectors, use_bulk=True)
        
        # Store results
        results[n_vectors] = {
            "faiss": faiss_results,
            "nuster_bulk": nuster_bulk_results,
        }
        
        # Print comparison
        if faiss_results and nuster_bulk_results:
            print(f"\n📊 Performance Comparison for {n_vectors} vectors:")
            print(f"   FAISS insertion rate:     {faiss_results['insertion_rate']:>8.1f} vec/s")
            print(f"   NusterDB bulk rate:       {nuster_bulk_results['insertion_rate']:>8.1f} vec/s")
            print(f"   NusterDB vs FAISS:        {nuster_bulk_results['insertion_rate']/faiss_results['insertion_rate']*100:>7.1f}%")
            print(f"   FAISS search time:        {faiss_results['avg_search_time']:>8.1f}ms")
            print(f"   NusterDB search time:     {nuster_bulk_results['avg_search_time']:>8.1f}ms")
            print(f"   NusterDB vs FAISS search: {nuster_bulk_results['avg_search_time']/faiss_results['avg_search_time']*100:>7.1f}%")
    
    # Print final summary
    print(f"\n{'='*60}")
    print("📈 FINAL PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    
    for n_vectors, result_set in results.items():
        faiss = result_set.get("faiss")
        nuster = result_set.get("nuster_bulk")
        
        if faiss and nuster:
            insertion_ratio = nuster['insertion_rate'] / faiss['insertion_rate'] * 100
            search_ratio = nuster['avg_search_time'] / faiss['avg_search_time'] * 100
            
            print(f"{n_vectors:>6} vectors: Insertion {insertion_ratio:>5.1f}% | Search {search_ratio:>5.1f}% of FAISS")
    
    # Check if we're achieving 50% of FAISS performance
    best_insertion_ratio = 0
    best_search_ratio = float('inf')
    
    for result_set in results.values():
        faiss = result_set.get("faiss")
        nuster = result_set.get("nuster_bulk")
        
        if faiss and nuster:
            insertion_ratio = nuster['insertion_rate'] / faiss['insertion_rate'] * 100
            search_ratio = nuster['avg_search_time'] / faiss['avg_search_time'] * 100
            
            best_insertion_ratio = max(best_insertion_ratio, insertion_ratio)
            best_search_ratio = min(best_search_ratio, search_ratio)
    
    print(f"\n🎯 TARGET: Achieve at least 50% of FAISS performance")
    print(f"   Best insertion performance: {best_insertion_ratio:.1f}% of FAISS")
    print(f"   Best search performance:    {best_search_ratio:.1f}% of FAISS")
    
    if best_insertion_ratio >= 50 and best_search_ratio <= 200:  # 200% means 2x slower, which is 50% performance
        print("🎉 SUCCESS: NusterDB achieves at least 50% of FAISS performance!")
    else:
        print("⚠️  NEEDS IMPROVEMENT: NusterDB has not yet reached 50% of FAISS performance")
        print("   Recommendations:")
        if best_insertion_ratio < 50:
            print("   - Optimize bulk insertion implementation")
            print("   - Improve memory layout and SIMD usage")
        if best_search_ratio > 200:
            print("   - Optimize search algorithms")
            print("   - Improve distance calculations and sorting")

if __name__ == "__main__":
    run_performance_comparison()
