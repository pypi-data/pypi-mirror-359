#!/usr/bin/env python3
"""
End-to-End Vector Database Performance Test
===========================================

Complete performance comparison of NusterDB vs FAISS vs ChromaDB
with datasets up to 1 million vectors.

This script tests:
- Insert performance (throughput)
- Search performance (queries/sec)
- Memory usage
- Scalability across different dataset sizes
- Performance across different vector dimensions

Results are saved as JSON and visualizations are created.
"""

import os
import sys
import time
import json
import tempfile
import shutil
from typing import Dict, List, Any
import gc

import numpy as np
import psutil
from tqdm import tqdm

# Import libraries with availability checks
HAS_PLOTTING = False
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
    plt.style.use('default')
except ImportError:
    print("⚠️  Plotting libraries not available")

HAS_FAISS = False
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    print("⚠️  FAISS not available")

HAS_CHROMA = False
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    print("⚠️  ChromaDB not available")

try:
    import nusterdb
    from nusterdb import NusterDB, Vector, Metadata
    print(f"✅ NusterDB v{nusterdb.__version__} available")
except ImportError:
    print("❌ NusterDB not available. Install with: pip install nusterdb")
    sys.exit(1)


class TestResult:
    """Test result container"""
    def __init__(self):
        self.database = ""
        self.operation = ""
        self.dataset_size = 0
        self.dimension = 0
        self.k = None
        self.duration = 0.0
        self.throughput = 0.0
        self.memory_mb = 0.0
        self.error = None
    
    def to_dict(self):
        return {
            'database': self.database,
            'operation': self.operation,
            'dataset_size': self.dataset_size,
            'dimension': self.dimension,
            'k': self.k,
            'duration_seconds': self.duration,
            'throughput': self.throughput,
            'memory_usage_mb': self.memory_mb,
            'error': self.error
        }


def get_memory_usage():
    """Get current memory usage in MB"""
    return psutil.Process().memory_info().rss / 1024 / 1024


def generate_test_data(n_vectors: int, dimension: int, n_queries: int = 100):
    """Generate normalized test vectors and queries"""
    np.random.seed(42)
    vectors = np.random.normal(0, 1, (n_vectors, dimension)).astype(np.float32)
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    
    np.random.seed(999)
    queries = np.random.normal(0, 1, (n_queries, dimension)).astype(np.float32)
    queries = queries / np.linalg.norm(queries, axis=1, keepdims=True)
    
    return vectors, queries


def test_nusterdb(vectors: np.ndarray, queries: np.ndarray, k_values: List[int]) -> List[TestResult]:
    """Test NusterDB performance"""
    results = []
    n_vectors, dimension = vectors.shape
    n_queries = len(queries)
    
    # Setup
    db_path = tempfile.mkdtemp(prefix="nusterdb_perf_")
    
    try:
        print(f"    Setting up NusterDB...")
        mem_start = get_memory_usage()
        setup_start = time.time()
        
        db = NusterDB.simple(db_path, dim=dimension, use_hnsw=False)
        
        setup_time = time.time() - setup_start
        print(f"    Setup completed in {setup_time:.3f}s")
        
        # Test insertion
        print(f"    Testing insertion of {n_vectors:,} vectors...")
        insert_result = TestResult()
        insert_result.database = "NusterDB"
        insert_result.operation = "insert"
        insert_result.dataset_size = n_vectors
        insert_result.dimension = dimension
        
        gc.collect()
        mem_before = get_memory_usage()
        start_time = time.time()
        
        try:
            for i, vector in enumerate(tqdm(vectors, desc="    Inserting", leave=False)):
                vec = Vector(vector.tolist())
                metadata = Metadata.with_data({"id": str(i)})
                db.add(i, vec, metadata)
            
            insert_result.duration = time.time() - start_time
            insert_result.throughput = n_vectors / insert_result.duration
            insert_result.memory_mb = get_memory_usage() - mem_before
            
        except Exception as e:
            insert_result.error = str(e)
            insert_result.duration = time.time() - start_time
        
        results.append(insert_result)
        
        if not insert_result.error:
            print(f"    ✅ Insert: {insert_result.duration:.2f}s, {insert_result.throughput:,.0f} vectors/s")
            
            # Test search for different k values
            for k in k_values:
                if k > n_vectors:
                    continue
                
                print(f"    Testing search (k={k})...")
                search_result = TestResult()
                search_result.database = "NusterDB"
                search_result.operation = "search"
                search_result.dimension = dimension
                search_result.k = k
                
                gc.collect()
                mem_before = get_memory_usage()
                start_time = time.time()
                
                try:
                    successful_queries = 0
                    for query in tqdm(queries, desc=f"    Searching k={k}", leave=False):
                        query_vec = Vector(query.tolist())
                        results_found = db.search(query_vec, k=k)
                        successful_queries += 1
                    
                    search_result.duration = time.time() - start_time
                    search_result.throughput = successful_queries / search_result.duration
                    search_result.memory_mb = get_memory_usage() - mem_before
                    
                except Exception as e:
                    search_result.error = str(e)
                    search_result.duration = time.time() - start_time
                
                results.append(search_result)
                
                if not search_result.error:
                    print(f"    ✅ Search k={k}: {search_result.duration:.3f}s, {search_result.throughput:,.0f} queries/s")
        else:
            print(f"    ❌ Insert failed: {insert_result.error}")
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            shutil.rmtree(db_path, ignore_errors=True)
    
    return results


def test_faiss(vectors: np.ndarray, queries: np.ndarray, k_values: List[int]) -> List[TestResult]:
    """Test FAISS performance"""
    if not HAS_FAISS:
        return []
    
    results = []
    n_vectors, dimension = vectors.shape
    n_queries = len(queries)
    
    try:
        print(f"    Setting up FAISS...")
        
        # Test insertion
        print(f"    Testing insertion of {n_vectors:,} vectors...")
        insert_result = TestResult()
        insert_result.database = "FAISS"
        insert_result.operation = "insert"
        insert_result.dataset_size = n_vectors
        insert_result.dimension = dimension
        
        gc.collect()
        mem_before = get_memory_usage()
        start_time = time.time()
        
        try:
            # Create index
            index = faiss.IndexFlatIP(dimension)  # Inner product for normalized vectors
            index.add(vectors)
            
            insert_result.duration = time.time() - start_time
            insert_result.throughput = n_vectors / insert_result.duration
            insert_result.memory_mb = get_memory_usage() - mem_before
            
        except Exception as e:
            insert_result.error = str(e)
            insert_result.duration = time.time() - start_time
        
        results.append(insert_result)
        
        if not insert_result.error:
            print(f"    ✅ Insert: {insert_result.duration:.3f}s, {insert_result.throughput:,.0f} vectors/s")
            
            # Test search for different k values
            for k in k_values:
                if k > n_vectors:
                    continue
                
                print(f"    Testing search (k={k})...")
                search_result = TestResult()
                search_result.database = "FAISS"
                search_result.operation = "search"
                search_result.dimension = dimension
                search_result.k = k
                
                gc.collect()
                mem_before = get_memory_usage()
                start_time = time.time()
                
                try:
                    distances, indices = index.search(queries, k)
                    
                    search_result.duration = time.time() - start_time
                    search_result.throughput = n_queries / search_result.duration
                    search_result.memory_mb = get_memory_usage() - mem_before
                    
                except Exception as e:
                    search_result.error = str(e)
                    search_result.duration = time.time() - start_time
                
                results.append(search_result)
                
                if not search_result.error:
                    print(f"    ✅ Search k={k}: {search_result.duration:.3f}s, {search_result.throughput:,.0f} queries/s")
        else:
            print(f"    ❌ Insert failed: {insert_result.error}")
    
    except Exception as e:
        print(f"    ❌ FAISS test failed: {e}")
    
    return results


def test_chromadb(vectors: np.ndarray, queries: np.ndarray, k_values: List[int]) -> List[TestResult]:
    """Test ChromaDB performance"""
    if not HAS_CHROMA:
        return []
    
    results = []
    n_vectors, dimension = vectors.shape
    n_queries = len(queries)
    
    # Setup
    db_path = tempfile.mkdtemp(prefix="chromadb_perf_")
    
    try:
        print(f"    Setting up ChromaDB...")
        
        client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        
        collection = client.create_collection(
            name=f"perf_test_{int(time.time())}",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Test insertion
        print(f"    Testing insertion of {n_vectors:,} vectors...")
        insert_result = TestResult()
        insert_result.database = "ChromaDB"
        insert_result.operation = "insert"
        insert_result.dataset_size = n_vectors
        insert_result.dimension = dimension
        
        gc.collect()
        mem_before = get_memory_usage()
        start_time = time.time()
        
        try:
            # Prepare data
            ids = [str(i) for i in range(n_vectors)]
            embeddings = vectors.tolist()
            metadatas = [{"id": i} for i in range(n_vectors)]
            
            # Insert in batches
            batch_size = min(1000, n_vectors)
            for i in tqdm(range(0, n_vectors, batch_size), desc="    Inserting", leave=False):
                end_idx = min(i + batch_size, n_vectors)
                collection.add(
                    ids=ids[i:end_idx],
                    embeddings=embeddings[i:end_idx],
                    metadatas=metadatas[i:end_idx]
                )
            
            insert_result.duration = time.time() - start_time
            insert_result.throughput = n_vectors / insert_result.duration
            insert_result.memory_mb = get_memory_usage() - mem_before
            
        except Exception as e:
            insert_result.error = str(e)
            insert_result.duration = time.time() - start_time
        
        results.append(insert_result)
        
        if not insert_result.error:
            print(f"    ✅ Insert: {insert_result.duration:.2f}s, {insert_result.throughput:,.0f} vectors/s")
            
            # Test search for different k values
            for k in k_values:
                if k > n_vectors:
                    continue
                
                print(f"    Testing search (k={k})...")
                search_result = TestResult()
                search_result.database = "ChromaDB"
                search_result.operation = "search"
                search_result.dimension = dimension
                search_result.k = k
                
                gc.collect()
                mem_before = get_memory_usage()
                start_time = time.time()
                
                try:
                    successful_queries = 0
                    for query in tqdm(queries, desc=f"    Searching k={k}", leave=False):
                        results_found = collection.query(
                            query_embeddings=[query.tolist()],
                            n_results=k
                        )
                        successful_queries += 1
                    
                    search_result.duration = time.time() - start_time
                    search_result.throughput = successful_queries / search_result.duration
                    search_result.memory_mb = get_memory_usage() - mem_before
                    
                except Exception as e:
                    search_result.error = str(e)
                    search_result.duration = time.time() - start_time
                
                results.append(search_result)
                
                if not search_result.error:
                    print(f"    ✅ Search k={k}: {search_result.duration:.3f}s, {search_result.throughput:,.0f} queries/s")
        else:
            print(f"    ❌ Insert failed: {insert_result.error}")
    
    finally:
        # Cleanup
        try:
            client.reset()
        except:
            pass
        if os.path.exists(db_path):
            shutil.rmtree(db_path, ignore_errors=True)
    
    return results


def create_visualizations(results: List[TestResult], output_dir: str):
    """Create performance visualizations"""
    if not HAS_PLOTTING or not results:
        print("Cannot create visualizations")
        return
    
    # Filter successful results
    successful = [r for r in results if not r.error]
    
    if not successful:
        print("No successful results to visualize")
        return
    
    # 1. Insertion Throughput
    insert_results = [r for r in successful if r.operation == "insert"]
    if len(insert_results) > 1:
        plt.figure(figsize=(12, 8))
        
        # Group by database
        databases = sorted(set(r.database for r in insert_results))
        dataset_sizes = sorted(set(r.dataset_size for r in insert_results))
        
        for db in databases:
            db_results = [r for r in insert_results if r.database == db]
            sizes = [r.dataset_size for r in db_results]
            throughputs = [r.throughput for r in db_results]
            plt.plot(sizes, throughputs, marker='o', label=db, linewidth=3, markersize=8)
        
        plt.xlabel('Dataset Size (vectors)')
        plt.ylabel('Insertion Throughput (vectors/sec)')
        plt.title('Vector Insertion Performance Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xscale('log')
        plt.yscale('log')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'insertion_performance.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 2. Search Throughput (k=10)
    search_results = [r for r in successful if r.operation == "search" and r.k == 10]
    if len(search_results) > 1:
        plt.figure(figsize=(10, 6))
        
        databases = sorted(set(r.database for r in search_results))
        dimensions = sorted(set(r.dimension for r in search_results))
        
        x = np.arange(len(dimensions))
        width = 0.25
        
        for i, db in enumerate(databases):
            db_results = [r for r in search_results if r.database == db]
            throughputs = []
            for dim in dimensions:
                dim_results = [r for r in db_results if r.dimension == dim]
                avg_throughput = np.mean([r.throughput for r in dim_results]) if dim_results else 0
                throughputs.append(avg_throughput)
            
            plt.bar(x + i * width, throughputs, width, label=db, alpha=0.8)
        
        plt.xlabel('Vector Dimension')
        plt.ylabel('Search Throughput (queries/sec)')
        plt.title('Vector Search Performance (k=10)')
        plt.xticks(x + width, dimensions)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'search_performance.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"📊 Visualizations saved to {output_dir}/")


def print_summary(results: List[TestResult]):
    """Print performance summary"""
    successful = [r for r in results if not r.error]
    
    if not successful:
        print("No successful results to summarize")
        return
    
    print("\n" + "=" * 80)
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 80)
    
    # Insertion performance
    insert_results = [r for r in successful if r.operation == "insert"]
    if insert_results:
        print("\n🔥 INSERTION PERFORMANCE")
        print("-" * 70)
        print(f"{'Database':>12} | {'Vectors':>10} | {'Dimension':>9} | {'Throughput':>12} | {'Duration':>8}")
        print("-" * 70)
        
        for result in sorted(insert_results, key=lambda x: (x.dataset_size, x.database)):
            print(f"{result.database:>12} | {result.dataset_size:>10,} | "
                  f"{result.dimension:>9} | {result.throughput:>12,.0f} | "
                  f"{result.duration:>8.2f}s")
    
    # Search performance (k=10)
    search_results = [r for r in successful if r.operation == "search" and r.k == 10]
    if search_results:
        print("\n⚡ SEARCH PERFORMANCE (k=10)")
        print("-" * 60)
        print(f"{'Database':>12} | {'Dimension':>9} | {'Throughput':>12} | {'Duration':>8}")
        print("-" * 60)
        
        for result in sorted(search_results, key=lambda x: (x.dimension, x.database)):
            print(f"{result.database:>12} | {result.dimension:>9} | "
                  f"{result.throughput:>12,.0f} | {result.duration:>8.3f}s")
    
    # Winners
    print("\n🏆 PERFORMANCE CHAMPIONS")
    print("-" * 30)
    
    if insert_results:
        fastest_insert = max(insert_results, key=lambda x: x.throughput)
        print(f"Fastest Insert: {fastest_insert.database} ({fastest_insert.throughput:,.0f} vectors/s)")
    
    if search_results:
        fastest_search = max(search_results, key=lambda x: x.throughput)
        print(f"Fastest Search: {fastest_search.database} ({fastest_search.throughput:,.0f} queries/s)")
    
    # Errors
    error_results = [r for r in results if r.error]
    if error_results:
        print("\n❌ ERRORS")
        print("-" * 30)
        for result in error_results:
            print(f"{result.database} {result.operation}: {result.error}")


def main():
    """Main benchmark function"""
    print("🚀 End-to-End Vector Database Benchmark")
    print("=" * 50)
    print(f"System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total // (1024**3)}GB RAM")
    print()
    
    # Test configuration
    test_configs = [
        (1000, 128),
        (10000, 128),
        (100000, 128),
        (1000000, 128),  # 1 million vectors!
        (10000, 384),
        (10000, 768),
    ]
    
    k_values = [1, 5, 10, 50, 100]
    n_queries = 100
    
    print(f"Test configurations: {len(test_configs)}")
    print(f"Search k values: {k_values}")
    print(f"Queries per test: {n_queries}")
    print()
    
    all_results = []
    total_tests = len(test_configs)
    
    for i, (dataset_size, dimension) in enumerate(test_configs):
        print(f"\n📊 Test {i+1}/{total_tests}: {dataset_size:,} vectors, {dimension}D")
        print("=" * 60)
        
        # Generate test data
        print("  Generating test data...")
        vectors, queries = generate_test_data(dataset_size, dimension, n_queries)
        print(f"  ✅ Generated {len(vectors):,} vectors and {len(queries)} queries")
        
        # Test NusterDB
        print("\n  🧪 Testing NusterDB...")
        nuster_results = test_nusterdb(vectors, queries, k_values)
        all_results.extend(nuster_results)
        
        # Test FAISS
        if HAS_FAISS:
            print("\n  🧪 Testing FAISS...")
            faiss_results = test_faiss(vectors, queries, k_values)
            all_results.extend(faiss_results)
        
        # Test ChromaDB (skip for very large datasets)
        if HAS_CHROMA and dataset_size <= 100000:
            print("\n  🧪 Testing ChromaDB...")
            chroma_results = test_chromadb(vectors, queries, k_values)
            all_results.extend(chroma_results)
        elif dataset_size > 100000:
            print("\n  ⏭️  Skipping ChromaDB (dataset too large)")
    
    # Create output directory
    output_dir = f"benchmark_results_{int(time.time())}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw results
    results_data = [r.to_dict() for r in all_results]
    with open(os.path.join(output_dir, "benchmark_results.json"), 'w') as f:
        json.dump(results_data, f, indent=2)
    
    # Print summary
    print_summary(all_results)
    
    # Create visualizations
    if HAS_PLOTTING:
        create_visualizations(all_results, output_dir)
    
    print(f"\n✅ Benchmark completed!")
    print(f"📁 Results saved to: {output_dir}/")


if __name__ == "__main__":
    main()
