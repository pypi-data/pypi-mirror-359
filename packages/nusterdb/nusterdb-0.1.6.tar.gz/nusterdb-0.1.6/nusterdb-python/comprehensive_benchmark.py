#!/usr/bin/env python3
"""
Comprehensive End-to-End Vector Database Benchmark
==================================================

A complete performance comparison of NusterDB vs FAISS vs ChromaDB
Testing with datasets up to 1 million vectors across different dimensions.

Features:
- Multiple dataset sizes (1K, 10K, 100K, 1M vectors)
- Various vector dimensions (128, 384, 768)
- Insertion and search performance
- Memory usage monitoring
- Detailed performance metrics
- Beautiful visualizations
- JSON results export

Author: NusterDB Team
Version: 1.0
"""

import os
import sys
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import traceback
import gc

import numpy as np
import psutil
from tqdm import tqdm

# Import plotting libraries
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
    plt.style.use('default')
    sns.set_palette("husl")
except ImportError:
    HAS_PLOTTING = False
    print("⚠️  Plotting libraries not available. Visualizations disabled.")

# Import database libraries
try:
    import faiss
    HAS_FAISS = True
    print("✅ FAISS available")
except ImportError:
    HAS_FAISS = False
    print("⚠️  FAISS not available")

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
    print("✅ ChromaDB available")
except ImportError:
    HAS_CHROMA = False
    print("⚠️  ChromaDB not available")

try:
    import nusterdb
    from nusterdb import NusterDB, Vector, Metadata
    HAS_NUSTERDB = True
    print("✅ NusterDB available")
except ImportError:
    HAS_NUSTERDB = False
    print("❌ NusterDB not available. Please install: pip install nusterdb")
    sys.exit(1)


class BenchmarkConfig:
    """Configuration for benchmark tests"""
    def __init__(self):
        # Test configurations
        self.dataset_sizes = [1000, 10000, 100000, 1000000]
        self.dimensions = [128, 384, 768]
        self.k_values = [1, 5, 10, 50, 100]
        self.num_queries = 100
        self.warmup_queries = 10
        
        # For large datasets, limit some tests
        self.max_chroma_size = 100000  # ChromaDB can be slow with very large datasets


class PerformanceMetrics:
    """Container for performance metrics"""
    def __init__(self):
        self.database = ""
        self.operation = ""
        self.dataset_size = 0
        self.dimension = 0
        self.k = None
        self.duration = 0.0
        self.throughput = 0.0
        self.memory_usage_mb = 0.0
        self.error = None
        self.metadata = {}
    
    def to_dict(self):
        return {
            'database': self.database,
            'operation': self.operation,
            'dataset_size': self.dataset_size,
            'dimension': self.dimension,
            'k': self.k,
            'duration': self.duration,
            'throughput': self.throughput,
            'memory_usage_mb': self.memory_usage_mb,
            'error': self.error,
            'metadata': self.metadata
        }


class MemoryMonitor:
    """Monitor memory usage during operations"""
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = 0
        self.peak_memory = 0
    
    def __enter__(self):
        gc.collect()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = self.initial_memory
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        gc.collect()
    
    def update_peak(self):
        current = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = max(self.peak_memory, current)
    
    @property
    def memory_used(self):
        return max(0, self.peak_memory - self.initial_memory)


def generate_vectors(n: int, dim: int, seed: int = 42) -> np.ndarray:
    """Generate normalized random vectors"""
    np.random.seed(seed)
    vectors = np.random.normal(0, 1, (n, dim)).astype(np.float32)
    # Normalize for cosine similarity
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    return vectors / norms


def generate_metadata(n: int, seed: int = 456) -> List[Dict[str, Any]]:
    """Generate sample metadata"""
    np.random.seed(seed)
    categories = ['tech', 'science', 'art', 'sports', 'music', 'literature']
    sources = ['doc', 'article', 'book', 'paper', 'blog']
    
    metadata = []
    for i in range(n):
        meta = {
            'id': i,
            'category': np.random.choice(categories),
            'source': np.random.choice(sources),
            'timestamp': int(time.time()) + i,
            'score': float(np.random.uniform(0, 1))
        }
        metadata.append(meta)
    return metadata


class NusterDBBenchmark:
    """NusterDB benchmark implementation"""
    
    def __init__(self):
        self.db = None
        self.db_path = None
    
    def setup(self, dimension: int):
        """Setup NusterDB instance"""
        self.cleanup()
        self.db_path = tempfile.mkdtemp(prefix="nusterdb_bench_")
        self.db = NusterDB.simple(self.db_path, dim=dimension, use_hnsw=False)  # Use flat index for consistent comparison
        return True
    
    def cleanup(self):
        """Cleanup resources"""
        self.db = None
        if self.db_path and os.path.exists(self.db_path):
            shutil.rmtree(self.db_path, ignore_errors=True)
        self.db_path = None
    
    def insert_vectors(self, vectors: np.ndarray, metadata_list: List[Dict] = None) -> PerformanceMetrics:
        """Benchmark vector insertion"""
        metrics = PerformanceMetrics()
        metrics.database = "NusterDB"
        metrics.operation = "insert"
        metrics.dataset_size, metrics.dimension = vectors.shape
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            
            try:
                for i, vector in enumerate(tqdm(vectors, desc="NusterDB Insert", leave=False)):
                    vec = Vector(vector.tolist())
                    meta = None
                    if metadata_list:
                        meta = Metadata.with_data(metadata_list[i])
                    
                    self.db.add(i, vec, meta)
                    
                    if i % 5000 == 0:
                        monitor.update_peak()
                
                metrics.duration = time.time() - start_time
                metrics.throughput = metrics.dataset_size / metrics.duration if metrics.duration > 0 else 0
                metrics.memory_usage_mb = monitor.memory_used
                
            except Exception as e:
                metrics.error = str(e)
                metrics.duration = time.time() - start_time
        
        return metrics
    
    def search_vectors(self, queries: np.ndarray, k: int) -> PerformanceMetrics:
        """Benchmark vector search"""
        metrics = PerformanceMetrics()
        metrics.database = "NusterDB"
        metrics.operation = "search"
        metrics.dimension = queries.shape[1]
        metrics.k = k
        
        # Warmup
        try:
            for i in range(min(10, len(queries))):
                query_vec = Vector(queries[i].tolist())
                self.db.search(query_vec, k=min(k, 10))
        except:
            pass
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            successful = 0
            
            try:
                for query in tqdm(queries, desc=f"NusterDB Search k={k}", leave=False):
                    query_vec = Vector(query.tolist())
                    results = self.db.search(query_vec, k=k)
                    successful += 1
                    monitor.update_peak()
                
                metrics.duration = time.time() - start_time
                metrics.throughput = successful / metrics.duration if metrics.duration > 0 else 0
                metrics.memory_usage_mb = monitor.memory_used
                metrics.metadata['successful_queries'] = successful
                
            except Exception as e:
                metrics.error = str(e)
                metrics.duration = time.time() - start_time
                metrics.metadata['successful_queries'] = successful
        
        return metrics


class FAISSBenchmark:
    """FAISS benchmark implementation"""
    
    def __init__(self):
        self.index = None
        self.vectors = None
    
    def setup(self, dimension: int):
        """Setup FAISS index"""
        self.cleanup()
        try:
            # Use flat index for accurate results
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine
            return True
        except Exception as e:
            print(f"FAISS setup failed: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        self.index = None
        self.vectors = None
    
    def insert_vectors(self, vectors: np.ndarray, metadata_list: List[Dict] = None) -> PerformanceMetrics:
        """Benchmark vector insertion"""
        metrics = PerformanceMetrics()
        metrics.database = "FAISS"
        metrics.operation = "insert"
        metrics.dataset_size, metrics.dimension = vectors.shape
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            
            try:
                self.vectors = vectors.copy()
                self.index.add(vectors)
                
                metrics.duration = time.time() - start_time
                metrics.throughput = metrics.dataset_size / metrics.duration if metrics.duration > 0 else 0
                metrics.memory_usage_mb = monitor.memory_used
                
            except Exception as e:
                metrics.error = str(e)
                metrics.duration = time.time() - start_time
        
        return metrics
    
    def search_vectors(self, queries: np.ndarray, k: int) -> PerformanceMetrics:
        """Benchmark vector search"""
        metrics = PerformanceMetrics()
        metrics.database = "FAISS"
        metrics.operation = "search"
        metrics.dimension = queries.shape[1]
        metrics.k = k
        
        # Warmup
        try:
            warmup_queries = queries[:min(10, len(queries))]
            self.index.search(warmup_queries, min(k, 10))
        except:
            pass
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            
            try:
                distances, indices = self.index.search(queries, k)
                
                metrics.duration = time.time() - start_time
                metrics.throughput = len(queries) / metrics.duration if metrics.duration > 0 else 0
                metrics.memory_usage_mb = monitor.memory_used
                metrics.metadata['successful_queries'] = len(queries)
                
            except Exception as e:
                metrics.error = str(e)
                metrics.duration = time.time() - start_time
        
        return metrics


class ChromaDBBenchmark:
    """ChromaDB benchmark implementation"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.db_path = None
    
    def setup(self, dimension: int):
        """Setup ChromaDB instance"""
        self.cleanup()
        self.db_path = tempfile.mkdtemp(prefix="chromadb_bench_")
        
        try:
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )
            
            collection_name = f"bench_collection_{int(time.time())}"
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"ChromaDB setup failed: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.client:
                self.client.reset()
        except:
            pass
        
        self.client = None
        self.collection = None
        
        if self.db_path and os.path.exists(self.db_path):
            shutil.rmtree(self.db_path, ignore_errors=True)
        self.db_path = None
    
    def insert_vectors(self, vectors: np.ndarray, metadata_list: List[Dict] = None) -> PerformanceMetrics:
        """Benchmark vector insertion"""
        metrics = PerformanceMetrics()
        metrics.database = "ChromaDB"
        metrics.operation = "insert"
        metrics.dataset_size, metrics.dimension = vectors.shape
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            
            try:
                # Prepare data
                ids = [str(i) for i in range(metrics.dataset_size)]
                embeddings = vectors.tolist()
                metadatas = metadata_list if metadata_list else [{"id": i} for i in range(metrics.dataset_size)]
                
                # Insert in batches
                batch_size = min(1000, metrics.dataset_size)
                
                for i in tqdm(range(0, metrics.dataset_size, batch_size), desc="ChromaDB Insert", leave=False):
                    end_idx = min(i + batch_size, metrics.dataset_size)
                    batch_ids = ids[i:end_idx]
                    batch_embeddings = embeddings[i:end_idx]
                    batch_metadata = metadatas[i:end_idx]
                    
                    self.collection.add(
                        ids=batch_ids,
                        embeddings=batch_embeddings,
                        metadatas=batch_metadata
                    )
                    
                    if i % 5000 == 0:
                        monitor.update_peak()
                
                metrics.duration = time.time() - start_time
                metrics.throughput = metrics.dataset_size / metrics.duration if metrics.duration > 0 else 0
                metrics.memory_usage_mb = monitor.memory_used
                
            except Exception as e:
                metrics.error = str(e)
                metrics.duration = time.time() - start_time
        
        return metrics
    
    def search_vectors(self, queries: np.ndarray, k: int) -> PerformanceMetrics:
        """Benchmark vector search"""
        metrics = PerformanceMetrics()
        metrics.database = "ChromaDB"
        metrics.operation = "search"
        metrics.dimension = queries.shape[1]
        metrics.k = k
        
        # Warmup
        try:
            for i in range(min(5, len(queries))):
                self.collection.query(
                    query_embeddings=[queries[i].tolist()],
                    n_results=min(k, 10)
                )
        except:
            pass
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            successful = 0
            
            try:
                for query in tqdm(queries, desc=f"ChromaDB Search k={k}", leave=False):
                    results = self.collection.query(
                        query_embeddings=[query.tolist()],
                        n_results=k
                    )
                    successful += 1
                    
                    if successful % 20 == 0:
                        monitor.update_peak()
                
                metrics.duration = time.time() - start_time
                metrics.throughput = successful / metrics.duration if metrics.duration > 0 else 0
                metrics.memory_usage_mb = monitor.memory_used
                metrics.metadata['successful_queries'] = successful
                
            except Exception as e:
                metrics.error = str(e)
                metrics.duration = time.time() - start_time
                metrics.metadata['successful_queries'] = successful
        
        return metrics


class ComprehensiveBenchmark:
    """Main benchmark runner"""
    
    def __init__(self):
        self.config = BenchmarkConfig()
        self.results = []
        self.start_time = time.time()
    
    def run_benchmark(self):
        """Run the complete benchmark suite"""
        print("🚀 Starting Comprehensive Vector Database Benchmark")
        print("=" * 60)
        print(f"Dataset sizes: {self.config.dataset_sizes}")
        print(f"Dimensions: {self.config.dimensions}")
        print(f"Search k values: {self.config.k_values}")
        print()
        
        # Available databases
        databases = []
        if HAS_NUSTERDB:
            databases.append("NusterDB")
        if HAS_FAISS:
            databases.append("FAISS")
        if HAS_CHROMA:
            databases.append("ChromaDB")
        
        print(f"Testing databases: {databases}")
        print()
        
        total_tests = len(self.config.dataset_sizes) * len(self.config.dimensions)
        current_test = 0
        
        for dataset_size in self.config.dataset_sizes:
            for dimension in self.config.dimensions:
                current_test += 1
                print(f"\n📊 Test {current_test}/{total_tests}: {dataset_size:,} vectors, {dimension}D")
                print("-" * 50)
                
                # Generate test data
                print("  Generating test data...")
                vectors = generate_vectors(dataset_size, dimension)
                queries = generate_vectors(self.config.num_queries, dimension, seed=999)
                metadata_list = generate_metadata(dataset_size)
                
                # Test each database
                for db_name in databases:
                    # Skip ChromaDB for very large datasets
                    if db_name == "ChromaDB" and dataset_size > self.config.max_chroma_size:
                        print(f"  ⏭️  Skipping {db_name} (dataset too large)")
                        continue
                    
                    print(f"  🧪 Testing {db_name}...")
                    self._test_database(db_name, vectors, queries, metadata_list, dimension)
        
        # Generate report
        self._generate_report()
        
        print(f"\n✅ Benchmark completed in {time.time() - self.start_time:.1f} seconds!")
    
    def _test_database(self, db_name: str, vectors: np.ndarray, queries: np.ndarray, 
                      metadata_list: List[Dict], dimension: int):
        """Test a specific database"""
        try:
            # Create benchmark instance
            if db_name == "NusterDB":
                benchmark = NusterDBBenchmark()
            elif db_name == "FAISS":
                benchmark = FAISSBenchmark()
            elif db_name == "ChromaDB":
                benchmark = ChromaDBBenchmark()
            else:
                return
            
            # Setup
            if not benchmark.setup(dimension):
                print(f"    ❌ Setup failed")
                return
            
            # Test insertion
            print(f"    📥 Testing insertion...")
            insert_metrics = benchmark.insert_vectors(vectors, metadata_list)
            self.results.append(insert_metrics)
            
            if insert_metrics.error:
                print(f"    ❌ Insert failed: {insert_metrics.error}")
                benchmark.cleanup()
                return
            else:
                print(f"    ✅ Insert: {insert_metrics.duration:.2f}s, "
                      f"{insert_metrics.throughput:,.0f} vectors/s, "
                      f"{insert_metrics.memory_usage_mb:.1f}MB")
            
            # Test search for different k values
            for k in self.config.k_values:
                if k > len(vectors):
                    continue
                
                print(f"    🔍 Testing search (k={k})...")
                search_metrics = benchmark.search_vectors(queries, k)
                self.results.append(search_metrics)
                
                if search_metrics.error:
                    print(f"    ❌ Search failed: {search_metrics.error}")
                else:
                    print(f"    ✅ Search: {search_metrics.duration:.3f}s, "
                          f"{search_metrics.throughput:,.0f} queries/s")
            
            # Cleanup
            benchmark.cleanup()
            
        except Exception as e:
            print(f"    ❌ {db_name} test failed: {e}")
            traceback.print_exc()
    
    def _generate_report(self):
        """Generate comprehensive benchmark report"""
        if not self.results:
            print("No results to report")
            return
        
        # Create output directory
        output_dir = f"benchmark_results_{int(time.time())}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save raw results
        results_data = [r.to_dict() for r in self.results]
        with open(os.path.join(output_dir, "benchmark_results.json"), 'w') as f:
            json.dump(results_data, f, indent=2)
        
        # Print summary
        self._print_summary()
        
        # Create visualizations
        if HAS_PLOTTING:
            self._create_visualizations(output_dir)
        
        print(f"\n📁 Full results saved to: {output_dir}/")
    
    def _print_summary(self):
        """Print benchmark summary"""
        print("\n" + "=" * 80)
        print("📈 COMPREHENSIVE BENCHMARK RESULTS")
        print("=" * 80)
        
        # Successful results only
        successful_results = [r for r in self.results if not r.error]
        
        # Insertion performance
        insert_results = [r for r in successful_results if r.operation == "insert"]
        if insert_results:
            print("\n🔥 INSERTION PERFORMANCE")
            print("-" * 70)
            print(f"{'Database':>12} | {'Vectors':>10} | {'Dimension':>9} | {'Throughput':>12} | {'Memory':>8} | {'Duration':>8}")
            print("-" * 70)
            
            for result in sorted(insert_results, key=lambda x: (x.dataset_size, x.database)):
                print(f"{result.database:>12} | {result.dataset_size:>10,} | "
                      f"{result.dimension:>9} | {result.throughput:>12,.0f} | "
                      f"{result.memory_usage_mb:>8.1f}MB | {result.duration:>8.2f}s")
        
        # Search performance (k=10)
        search_results = [r for r in successful_results if r.operation == "search" and r.k == 10]
        if search_results:
            print("\n⚡ SEARCH PERFORMANCE (k=10)")
            print("-" * 70)
            print(f"{'Database':>12} | {'Dimension':>9} | {'Throughput':>12} | {'Memory':>8} | {'Duration':>8}")
            print("-" * 70)
            
            for result in sorted(search_results, key=lambda x: (x.dimension, x.database)):
                print(f"{result.database:>12} | {result.dimension:>9} | "
                      f"{result.throughput:>12,.0f} | {result.memory_usage_mb:>8.1f}MB | "
                      f"{result.duration:>8.3f}s")
        
        # Error summary
        error_results = [r for r in self.results if r.error]
        if error_results:
            print("\n❌ ERRORS ENCOUNTERED")
            print("-" * 50)
            for result in error_results:
                print(f"{result.database:>12} | {result.operation:>8} | {result.error}")
        
        # Performance winners
        print("\n🏆 PERFORMANCE WINNERS")
        print("-" * 30)
        
        if insert_results:
            fastest_insert = max(insert_results, key=lambda x: x.throughput)
            print(f"Fastest Insert: {fastest_insert.database} ({fastest_insert.throughput:,.0f} vectors/s)")
            
            lowest_memory = min(insert_results, key=lambda x: x.memory_usage_mb)
            print(f"Lowest Memory: {lowest_memory.database} ({lowest_memory.memory_usage_mb:.1f}MB)")
        
        if search_results:
            fastest_search = max(search_results, key=lambda x: x.throughput)
            print(f"Fastest Search: {fastest_search.database} ({fastest_search.throughput:,.0f} queries/s)")
    
    def _create_visualizations(self, output_dir: str):
        """Create performance visualizations"""
        successful_results = [r for r in self.results if not r.error]
        
        if not successful_results:
            print("No successful results to visualize")
            return
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Insertion Throughput
        insert_results = [r for r in successful_results if r.operation == "insert"]
        if len(insert_results) > 1:
            plt.figure(figsize=(14, 8))
            
            databases = sorted(set(r.database for r in insert_results))
            dataset_sizes = sorted(set(r.dataset_size for r in insert_results))
            
            for db in databases:
                db_results = [r for r in insert_results if r.database == db]
                sizes = [r.dataset_size for r in db_results]
                throughputs = [r.throughput for r in db_results]
                plt.plot(sizes, throughputs, marker='o', label=db, linewidth=3, markersize=8)
            
            plt.xlabel('Dataset Size (vectors)', fontsize=12)
            plt.ylabel('Insertion Throughput (vectors/sec)', fontsize=12)
            plt.title('Vector Insertion Performance Comparison', fontsize=14, fontweight='bold')
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.xscale('log')
            plt.yscale('log')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'insertion_throughput.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Search Throughput
        search_results = [r for r in successful_results if r.operation == "search" and r.k == 10]
        if len(search_results) > 1:
            plt.figure(figsize=(12, 8))
            
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
            
            plt.xlabel('Vector Dimension', fontsize=12)
            plt.ylabel('Search Throughput (queries/sec)', fontsize=12)
            plt.title('Vector Search Performance Comparison (k=10)', fontsize=14, fontweight='bold')
            plt.xticks(x + width, dimensions)
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'search_throughput.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Memory Usage
        if len(insert_results) > 1:
            plt.figure(figsize=(12, 8))
            
            databases = sorted(set(r.database for r in insert_results))
            
            for db in databases:
                db_results = [r for r in insert_results if r.database == db]
                sizes = [r.dataset_size for r in db_results]
                memory = [r.memory_usage_mb for r in db_results]
                plt.plot(sizes, memory, marker='o', label=db, linewidth=3, markersize=8)
            
            plt.xlabel('Dataset Size (vectors)', fontsize=12)
            plt.ylabel('Memory Usage (MB)', fontsize=12)
            plt.title('Memory Usage During Vector Insertion', fontsize=14, fontweight='bold')
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.xscale('log')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'memory_usage.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"📊 Visualizations saved to {output_dir}/")


def main():
    """Main function"""
    print("🧪 Comprehensive Vector Database Benchmark Suite")
    print("Testing NusterDB vs FAISS vs ChromaDB")
    print("=" * 60)
    
    # Check system info
    print(f"System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total // (1024**3)}GB RAM")
    print(f"Python: {sys.version}")
    print()
    
    # Check dependencies
    if not HAS_NUSTERDB:
        print("❌ NusterDB is required but not available")
        sys.exit(1)
    
    # Run benchmark
    benchmark = ComprehensiveBenchmark()
    try:
        benchmark.run_benchmark()
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
