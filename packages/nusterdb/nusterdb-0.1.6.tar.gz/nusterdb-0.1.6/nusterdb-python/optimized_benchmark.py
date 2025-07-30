#!/usr/bin/env python3
"""
High-Performance Benchmark Script for Optimized NusterDB
Tests the SIMD and parallel processing optimizations against FAISS and ChromaDB
"""

import time
import numpy as np
import psutil
import json
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import gc
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Import the databases
try:
    import nusterdb
    NUSTERDB_AVAILABLE = True
except ImportError:
    NUSTERDB_AVAILABLE = False
    print("⚠️  NusterDB not available")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not available")

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not available")

class PerformanceBenchmark:
    def __init__(self):
        self.results = []
        self.process = psutil.Process()
        self.base_memory = self.get_memory_usage()
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return self.process.cpu_percent()
    
    def generate_vectors(self, n: int, dim: int) -> np.ndarray:
        """Generate random vectors for testing"""
        print(f"🔧 Generating {n:,} vectors of dimension {dim}...")
        np.random.seed(42)  # For reproducibility
        vectors = np.random.randn(n, dim).astype(np.float32)
        # Normalize vectors for better performance
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / (norms + 1e-8)
        print(f"✅ Generated {n:,} normalized vectors")
        return vectors
    
    def benchmark_nusterdb_optimized(self, vectors: np.ndarray, queries: np.ndarray, k: int) -> Dict[str, Any]:
        """Benchmark optimized NusterDB with SIMD and parallel processing"""
        if not NUSTERDB_AVAILABLE:
            return {"error": "NusterDB not available"}
        
        print(f"🚀 Benchmarking Optimized NusterDB...")
        
        # Create optimized database instance
        metadata = nusterdb.Metadata.with_data({"source": "performance_test"})
        db = nusterdb.Database(
            path="test_optimized_db", 
            dim=vectors.shape[1],
            index_type="optimized_flat",  # Use the optimized flat index
        )
        
        # Measure insertion performance
        start_memory = self.get_memory_usage()
        start_time = time.time()
        
        print(f"  📥 Inserting {len(vectors):,} vectors...")
        for i, vector in enumerate(tqdm(vectors, desc="Inserting")):
            db.insert(i, nusterdb.Vector(vector.tolist()), metadata)
        
        insert_time = time.time() - start_time
        insert_memory = self.get_memory_usage() - start_memory
        insert_throughput = len(vectors) / insert_time
        
        print(f"  ✅ Insertion: {insert_throughput:,.0f} vectors/sec")
        
        # Measure search performance
        start_time = time.time()
        search_results = []
        
        print(f"  🔍 Searching with k={k}...")
        for query in tqdm(queries, desc="Searching"):
            results = db.search(nusterdb.Vector(query.tolist()), k)
            search_results.append(results)
        
        search_time = time.time() - start_time
        search_memory = self.get_memory_usage() - start_memory
        search_throughput = len(queries) / search_time
        
        print(f"  ✅ Search: {search_throughput:,.0f} queries/sec")
        
        # Cleanup
        db.close()
        
        return {
            "database": "NusterDB-Optimized",
            "insert_time": insert_time,
            "insert_throughput": insert_throughput,
            "insert_memory_mb": insert_memory,
            "search_time": search_time,
            "search_throughput": search_throughput,
            "search_memory_mb": search_memory,
            "results_count": len(search_results[0]) if search_results else 0,
            "error": None
        }
    
    def benchmark_faiss(self, vectors: np.ndarray, queries: np.ndarray, k: int) -> Dict[str, Any]:
        """Benchmark FAISS with optimized settings"""
        if not FAISS_AVAILABLE:
            return {"error": "FAISS not available"}
        
        print(f"⚡ Benchmarking FAISS (Optimized)...")
        
        # Create optimized FAISS index
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)  # Inner product for normalized vectors
        
        # Use multiple threads for better performance
        faiss.omp_set_num_threads(psutil.cpu_count())
        
        # Measure insertion performance
        start_memory = self.get_memory_usage()
        start_time = time.time()
        
        print(f"  📥 Inserting {len(vectors):,} vectors...")
        # FAISS batch insertion for better performance
        index.add(vectors)
        
        insert_time = time.time() - start_time
        insert_memory = self.get_memory_usage() - start_memory
        insert_throughput = len(vectors) / insert_time
        
        print(f"  ✅ Insertion: {insert_throughput:,.0f} vectors/sec")
        
        # Measure search performance
        start_time = time.time()
        
        print(f"  🔍 Searching with k={k}...")
        # FAISS batch search for better performance
        distances, indices = index.search(queries, k)
        
        search_time = time.time() - start_time
        search_memory = self.get_memory_usage() - start_memory
        search_throughput = len(queries) / search_time
        
        print(f"  ✅ Search: {search_throughput:,.0f} queries/sec")
        
        return {
            "database": "FAISS-Optimized",
            "insert_time": insert_time,
            "insert_throughput": insert_throughput,
            "insert_memory_mb": insert_memory,
            "search_time": search_time,
            "search_throughput": search_throughput,
            "search_memory_mb": search_memory,
            "results_count": indices.shape[1] if len(indices) > 0 else 0,
            "error": None
        }
    
    def benchmark_chromadb(self, vectors: np.ndarray, queries: np.ndarray, k: int) -> Dict[str, Any]:
        """Benchmark ChromaDB"""
        if not CHROMADB_AVAILABLE:
            return {"error": "ChromaDB not available"}
        
        print(f"🦠 Benchmarking ChromaDB...")
        
        # Create ChromaDB client
        client = chromadb.PersistentClient(path="./test_chroma")
        collection = client.get_or_create_collection(
            name="performance_test",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Measure insertion performance
        start_memory = self.get_memory_usage()
        start_time = time.time()
        
        print(f"  📥 Inserting {len(vectors):,} vectors...")
        
        # ChromaDB batch insertion
        batch_size = 1000
        for i in tqdm(range(0, len(vectors), batch_size), desc="Inserting"):
            batch_end = min(i + batch_size, len(vectors))
            batch_vectors = vectors[i:batch_end]
            ids = [str(j) for j in range(i, batch_end)]
            
            collection.add(
                embeddings=batch_vectors.tolist(),
                ids=ids
            )
        
        insert_time = time.time() - start_time
        insert_memory = self.get_memory_usage() - start_memory
        insert_throughput = len(vectors) / insert_time
        
        print(f"  ✅ Insertion: {insert_throughput:,.0f} vectors/sec")
        
        # Measure search performance
        start_time = time.time()
        search_results = []
        
        print(f"  🔍 Searching with k={k}...")
        for query in tqdm(queries, desc="Searching"):
            results = collection.query(
                query_embeddings=[query.tolist()],
                n_results=k
            )
            search_results.append(results)
        
        search_time = time.time() - start_time
        search_memory = self.get_memory_usage() - start_memory
        search_throughput = len(queries) / search_time
        
        print(f"  ✅ Search: {search_throughput:,.0f} queries/sec")
        
        # Cleanup
        client.delete_collection("performance_test")
        
        return {
            "database": "ChromaDB",
            "insert_time": insert_time,
            "insert_throughput": insert_throughput,
            "insert_memory_mb": insert_memory,
            "search_time": search_time,
            "search_throughput": search_throughput,
            "search_memory_mb": search_memory,
            "results_count": len(search_results[0]['ids'][0]) if search_results else 0,
            "error": None
        }
    
    def run_benchmark_suite(self):
        """Run comprehensive benchmarks"""
        test_configs = [
            {"n_vectors": 1000, "dim": 128, "n_queries": 100, "k": 10},
            {"n_vectors": 10000, "dim": 128, "n_queries": 100, "k": 10},
            {"n_vectors": 100000, "dim": 128, "n_queries": 100, "k": 10},
            {"n_vectors": 1000000, "dim": 128, "n_queries": 100, "k": 10},
            {"n_vectors": 100000, "dim": 256, "n_queries": 100, "k": 10},
            {"n_vectors": 100000, "dim": 512, "n_queries": 100, "k": 10},
        ]
        
        print(f"🏁 Starting Optimized Performance Benchmark Suite")
        print(f"📊 Testing {len(test_configs)} configurations")
        print(f"💻 System: {psutil.cpu_count()} CPU cores, {psutil.virtual_memory().total / 1024**3:.1f} GB RAM")
        print("=" * 80)
        
        for i, config in enumerate(test_configs, 1):
            print(f"\n🔬 Test {i}/{len(test_configs)}: {config['n_vectors']:,} vectors, {config['dim']}D")
            print("-" * 60)
            
            # Generate test data
            vectors = self.generate_vectors(config['n_vectors'], config['dim'])
            queries = self.generate_vectors(config['n_queries'], config['dim'])
            
            gc.collect()  # Clean up memory
            
            # Benchmark each database
            databases = []
            if NUSTERDB_AVAILABLE:
                databases.append(("NusterDB", self.benchmark_nusterdb_optimized))
            if FAISS_AVAILABLE:
                databases.append(("FAISS", self.benchmark_faiss))
            if CHROMADB_AVAILABLE and config['n_vectors'] <= 100000:  # Skip ChromaDB for large datasets
                databases.append(("ChromaDB", self.benchmark_chromadb))
            
            for db_name, benchmark_func in databases:
                try:
                    print(f"\n🧪 Testing {db_name}...")
                    result = benchmark_func(vectors, queries, config['k'])
                    result.update({
                        "n_vectors": config['n_vectors'],
                        "dimension": config['dim'],
                        "n_queries": config['n_queries'],
                        "k": config['k'],
                        "timestamp": datetime.now().isoformat()
                    })
                    self.results.append(result)
                    
                    if result.get('error'):
                        print(f"  ❌ Error: {result['error']}")
                    else:
                        print(f"  📈 Insert: {result['insert_throughput']:,.0f} vec/s")
                        print(f"  🔍 Search: {result['search_throughput']:,.0f} qry/s")
                        print(f"  💾 Memory: {result['insert_memory_mb']:.1f} MB")
                        
                except Exception as e:
                    print(f"  💥 {db_name} failed: {e}")
                    self.results.append({
                        "database": db_name,
                        "n_vectors": config['n_vectors'],
                        "dimension": config['dim'],
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Clean up between tests
                gc.collect()
                time.sleep(1)
        
        print(f"\n✅ Benchmark suite completed!")
        self.save_results()
        self.generate_visualizations()
    
    def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimized_benchmark_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"💾 Results saved to {filename}")
    
    def generate_visualizations(self):
        """Generate performance comparison charts"""
        if not self.results:
            return
        
        print("📊 Generating performance visualizations...")
        
        # Filter successful results
        valid_results = [r for r in self.results if not r.get('error')]
        
        if not valid_results:
            print("❌ No valid results to visualize")
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Group results by database
        db_results = {}
        for result in valid_results:
            db_name = result['database']
            if db_name not in db_results:
                db_results[db_name] = []
            db_results[db_name].append(result)
        
        # Plot 1: Insertion Throughput vs Dataset Size
        ax1.set_title('Insertion Throughput vs Dataset Size', fontsize=14, fontweight='bold')
        for db_name, results in db_results.items():
            sizes = [r['n_vectors'] for r in results if 'insert_throughput' in r]
            throughputs = [r['insert_throughput'] for r in results if 'insert_throughput' in r]
            if sizes and throughputs:
                ax1.loglog(sizes, throughputs, marker='o', linewidth=2, markersize=8, label=db_name)
        
        ax1.set_xlabel('Dataset Size (vectors)')
        ax1.set_ylabel('Insertion Throughput (vectors/sec)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Search Throughput vs Dataset Size
        ax2.set_title('Search Throughput vs Dataset Size', fontsize=14, fontweight='bold')
        for db_name, results in db_results.items():
            sizes = [r['n_vectors'] for r in results if 'search_throughput' in r]
            throughputs = [r['search_throughput'] for r in results if 'search_throughput' in r]
            if sizes and throughputs:
                ax2.loglog(sizes, throughputs, marker='s', linewidth=2, markersize=8, label=db_name)
        
        ax2.set_xlabel('Dataset Size (vectors)')
        ax2.set_ylabel('Search Throughput (queries/sec)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Memory Usage vs Dataset Size
        ax3.set_title('Memory Usage vs Dataset Size', fontsize=14, fontweight='bold')
        for db_name, results in db_results.items():
            sizes = [r['n_vectors'] for r in results if 'insert_memory_mb' in r]
            memory = [r['insert_memory_mb'] for r in results if 'insert_memory_mb' in r]
            if sizes and memory:
                ax3.loglog(sizes, memory, marker='^', linewidth=2, markersize=8, label=db_name)
        
        ax3.set_xlabel('Dataset Size (vectors)')
        ax3.set_ylabel('Memory Usage (MB)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Performance Comparison Bar Chart (latest results)
        ax4.set_title('Performance Comparison (Latest Results)', fontsize=14, fontweight='bold')
        
        # Get the largest dataset results for comparison
        max_size = max(r['n_vectors'] for r in valid_results)
        latest_results = [r for r in valid_results if r['n_vectors'] == max_size]
        
        if latest_results:
            databases = [r['database'] for r in latest_results]
            insert_perf = [r.get('insert_throughput', 0) for r in latest_results]
            search_perf = [r.get('search_throughput', 0) for r in latest_results]
            
            x = np.arange(len(databases))
            width = 0.35
            
            bars1 = ax4.bar(x - width/2, insert_perf, width, label='Insert (vec/s)', alpha=0.8)
            bars2 = ax4.bar(x + width/2, search_perf, width, label='Search (qry/s)', alpha=0.8)
            
            ax4.set_xlabel('Database')
            ax4.set_ylabel('Throughput')
            ax4.set_xticks(x)
            ax4.set_xticklabels(databases, rotation=45)
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax4.annotate(f'{height:,.0f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=10)
            
            for bar in bars2:
                height = bar.get_height()
                ax4.annotate(f'{height:,.0f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimized_performance_comparison_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Visualizations saved to {filename}")
        
        # Show the plot
        plt.show()

def main():
    """Main function to run the optimized benchmark"""
    print("🚀 NusterDB Optimized Performance Benchmark")
    print("=" * 60)
    
    benchmark = PerformanceBenchmark()
    benchmark.run_benchmark_suite()
    
    # Print summary
    print("\n📋 BENCHMARK SUMMARY")
    print("=" * 40)
    
    valid_results = [r for r in benchmark.results if not r.get('error')]
    
    if valid_results:
        # Find best performers
        best_insert = max(valid_results, key=lambda x: x.get('insert_throughput', 0))
        best_search = max(valid_results, key=lambda x: x.get('search_throughput', 0))
        
        print(f"🏆 Best Insertion: {best_insert['database']} - {best_insert['insert_throughput']:,.0f} vectors/sec")
        print(f"🎯 Best Search: {best_search['database']} - {best_search['search_throughput']:,.0f} queries/sec")
        
        # NusterDB specific results
        nuster_results = [r for r in valid_results if 'NusterDB' in r['database']]
        if nuster_results:
            print(f"\n🔥 NusterDB Optimization Results:")
            for result in nuster_results:
                print(f"  📊 {result['n_vectors']:,} vectors: {result['insert_throughput']:,.0f} insert/sec, {result['search_throughput']:,.0f} search/sec")
    else:
        print("❌ No successful benchmark results")

if __name__ == "__main__":
    main()
