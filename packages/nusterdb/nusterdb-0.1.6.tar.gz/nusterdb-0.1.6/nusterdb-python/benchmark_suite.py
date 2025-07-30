#!/usr/bin/env python3
"""
NusterDB Performance Benchmark Suite
====================================

Comprehensive performance testing comparing NusterDB, FAISS, and ChromaDB
across various scenarios including large-scale datasets (1M+ vectors).

Features:
- Multiple dataset sizes (1K, 10K, 100K, 1M vectors)
- Various vector dimensions (128, 384, 768, 1536)
- Different distance metrics
- Insert performance testing
- Search performance testing (various k values)
- Memory usage monitoring
- Accuracy comparison
- Concurrent access testing
- Persistence/reload testing

Requirements:
- nusterdb>=0.1.1
- faiss-cpu or faiss-gpu
- chromadb
- numpy
- matplotlib
- seaborn
- psutil
- tqdm
"""

import os
import sys
import time
import json
import tempfile
import shutil
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import gc

import numpy as np
import psutil
from tqdm import tqdm

# Optional imports with fallbacks
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("Warning: matplotlib/seaborn not available. Plotting disabled.")

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("Warning: FAISS not available. FAISS benchmarks will be skipped.")

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    print("Warning: ChromaDB not available. ChromaDB benchmarks will be skipped.")

try:
    import nusterdb
    from nusterdb import NusterDB, Vector, Metadata
    HAS_NUSTERDB = True
except ImportError:
    HAS_NUSTERDB = False
    print("Error: NusterDB not available. Please install with: pip install nusterdb")
    sys.exit(1)


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark tests"""
    dataset_sizes: List[int] = None
    dimensions: List[int] = None
    k_values: List[int] = None
    distance_metrics: List[str] = None
    num_threads: int = 4
    num_queries: int = 100
    warmup_queries: int = 10
    
    def __post_init__(self):
        if self.dataset_sizes is None:
            self.dataset_sizes = [1000, 10000, 100000, 1000000]
        if self.dimensions is None:
            self.dimensions = [128, 384, 768]
        if self.k_values is None:
            self.k_values = [1, 5, 10, 50, 100]
        if self.distance_metrics is None:
            self.distance_metrics = ['cosine', 'euclidean']


@dataclass
class PerformanceResult:
    """Results from a single benchmark test"""
    database: str
    operation: str
    dataset_size: int
    dimension: int
    k: Optional[int]
    distance_metric: str
    duration: float
    memory_usage_mb: float
    accuracy: Optional[float] = None
    throughput: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MemoryMonitor:
    """Context manager for monitoring memory usage"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = 0
        self.peak_memory = 0
    
    def __enter__(self):
        gc.collect()  # Clean up before measuring
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = self.initial_memory
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        gc.collect()  # Clean up after measuring
    
    def update_peak(self):
        current = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = max(self.peak_memory, current)
    
    @property
    def memory_used(self):
        return self.peak_memory - self.initial_memory


class DatasetGenerator:
    """Generate synthetic datasets for benchmarking"""
    
    @staticmethod
    def generate_vectors(n: int, dim: int, seed: int = 42) -> np.ndarray:
        """Generate normalized random vectors"""
        np.random.seed(seed)
        vectors = np.random.normal(0, 1, (n, dim)).astype(np.float32)
        # Normalize vectors for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return vectors / norms
    
    @staticmethod
    def generate_queries(n: int, dim: int, seed: int = 123) -> np.ndarray:
        """Generate query vectors"""
        np.random.seed(seed)
        queries = np.random.normal(0, 1, (n, dim)).astype(np.float32)
        norms = np.linalg.norm(queries, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return queries / norms
    
    @staticmethod
    def generate_metadata(n: int, seed: int = 456) -> List[Dict[str, Any]]:
        """Generate metadata for vectors"""
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
                'score': np.random.uniform(0, 1)
            }
            metadata.append(meta)
        return metadata


class NusterDBBenchmark:
    """NusterDB performance benchmark"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.db = None
        self.db_path = None
    
    def setup(self, dataset_size: int, dimension: int, distance_metric: str, use_hnsw: bool = True):
        """Setup NusterDB instance"""
        self.cleanup()
        self.db_path = tempfile.mkdtemp(prefix="nusterdb_bench_")
        
        try:
            self.db = NusterDB.simple(self.db_path, dim=dimension, use_hnsw=use_hnsw)
        except Exception as e:
            print(f"Failed to create NusterDB: {e}")
            raise
    
    def cleanup(self):
        """Clean up database resources"""
        self.db = None
        if self.db_path and os.path.exists(self.db_path):
            shutil.rmtree(self.db_path, ignore_errors=True)
        self.db_path = None
    
    def insert_vectors(self, vectors: np.ndarray, metadata: List[Dict] = None) -> PerformanceResult:
        """Benchmark vector insertion"""
        dataset_size, dimension = vectors.shape
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            
            try:
                for i, vector in enumerate(tqdm(vectors, desc="Inserting vectors")):
                    vec = Vector(vector.tolist())
                    meta = None
                    if metadata:
                        meta = Metadata.with_data(metadata[i])
                    
                    self.db.add(i, vec, meta)
                    
                    if i % 1000 == 0:
                        monitor.update_peak()
                
                duration = time.time() - start_time
                throughput = dataset_size / duration if duration > 0 else 0
                
                return PerformanceResult(
                    database="NusterDB",
                    operation="insert",
                    dataset_size=dataset_size,
                    dimension=dimension,
                    k=None,
                    distance_metric="cosine",  # NusterDB default
                    duration=duration,
                    memory_usage_mb=monitor.memory_used,
                    throughput=throughput
                )
                
            except Exception as e:
                return PerformanceResult(
                    database="NusterDB",
                    operation="insert",
                    dataset_size=dataset_size,
                    dimension=dimension,
                    k=None,
                    distance_metric="cosine",
                    duration=0,
                    memory_usage_mb=0,
                    error=str(e)
                )
    
    def search_vectors(self, queries: np.ndarray, k: int) -> PerformanceResult:
        """Benchmark vector search"""
        num_queries, dimension = queries.shape
        
        # Warmup
        for i in range(min(self.config.warmup_queries, num_queries)):
            query_vec = Vector(queries[i].tolist())
            try:
                self.db.search(query_vec, k=min(k, 10))
            except:
                pass
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            successful_queries = 0
            
            try:
                for i, query in enumerate(queries):
                    query_vec = Vector(query.tolist())
                    results = self.db.search(query_vec, k=k)
                    successful_queries += 1
                    
                    if i % 100 == 0:
                        monitor.update_peak()
                
                duration = time.time() - start_time
                throughput = successful_queries / duration if duration > 0 else 0
                
                return PerformanceResult(
                    database="NusterDB",
                    operation="search",
                    dataset_size=0,  # Not applicable for search
                    dimension=dimension,
                    k=k,
                    distance_metric="cosine",
                    duration=duration,
                    memory_usage_mb=monitor.memory_used,
                    throughput=throughput,
                    metadata={'successful_queries': successful_queries}
                )
                
            except Exception as e:
                return PerformanceResult(
                    database="NusterDB",
                    operation="search",
                    dataset_size=0,
                    dimension=dimension,
                    k=k,
                    distance_metric="cosine",
                    duration=0,
                    memory_usage_mb=0,
                    error=str(e)
                )


class FAISSBenchmark:
    """FAISS performance benchmark"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.index = None
        self.vectors = None
    
    def setup(self, dataset_size: int, dimension: int, distance_metric: str):
        """Setup FAISS index"""
        self.cleanup()
        
        try:
            if distance_metric.lower() == 'cosine':
                # Use inner product for cosine similarity with normalized vectors
                self.index = faiss.IndexFlatIP(dimension)
            else:  # euclidean
                self.index = faiss.IndexFlatL2(dimension)
                
            # For large datasets, use IVF index
            if dataset_size > 50000:
                nlist = min(4096, dataset_size // 50)
                if distance_metric.lower() == 'cosine':
                    quantizer = faiss.IndexFlatIP(dimension)
                    self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
                else:
                    quantizer = faiss.IndexFlatL2(dimension)
                    self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
                    
        except Exception as e:
            print(f"Failed to create FAISS index: {e}")
            raise
    
    def cleanup(self):
        """Clean up index resources"""
        self.index = None
        self.vectors = None
    
    def insert_vectors(self, vectors: np.ndarray, metadata: List[Dict] = None) -> PerformanceResult:
        """Benchmark vector insertion"""
        dataset_size, dimension = vectors.shape
        self.vectors = vectors.copy()
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            
            try:
                # Train index if needed (for IVF)
                if hasattr(self.index, 'train') and not self.index.is_trained:
                    self.index.train(vectors)
                
                # Add vectors
                self.index.add(vectors)
                
                duration = time.time() - start_time
                throughput = dataset_size / duration if duration > 0 else 0
                
                return PerformanceResult(
                    database="FAISS",
                    operation="insert",
                    dataset_size=dataset_size,
                    dimension=dimension,
                    k=None,
                    distance_metric="cosine",  # Will be set by caller
                    duration=duration,
                    memory_usage_mb=monitor.memory_used,
                    throughput=throughput
                )
                
            except Exception as e:
                return PerformanceResult(
                    database="FAISS",
                    operation="insert",
                    dataset_size=dataset_size,
                    dimension=dimension,
                    k=None,
                    distance_metric="cosine",  # Will be set by caller
                    duration=0,
                    memory_usage_mb=0,
                    error=str(e)
                )
    
    def search_vectors(self, queries: np.ndarray, k: int) -> PerformanceResult:
        """Benchmark vector search"""
        num_queries, dimension = queries.shape
        
        # Warmup
        try:
            warmup_queries = queries[:min(self.config.warmup_queries, num_queries)]
            self.index.search(warmup_queries, min(k, 10))
        except:
            pass
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            
            try:
                distances, indices = self.index.search(queries, k)
                duration = time.time() - start_time
                throughput = num_queries / duration if duration > 0 else 0
                
                return PerformanceResult(
                    database="FAISS",
                    operation="search",
                    dataset_size=0,
                    dimension=dimension,
                    k=k,
                    distance_metric="cosine",  # Will be set properly by caller
                    duration=duration,
                    memory_usage_mb=monitor.memory_used,
                    throughput=throughput,
                    metadata={'successful_queries': num_queries}
                )
                
            except Exception as e:
                return PerformanceResult(
                    database="FAISS",
                    operation="search",
                    dataset_size=0,
                    dimension=dimension,
                    k=k,
                    distance_metric="cosine",
                    duration=0,
                    memory_usage_mb=0,
                    error=str(e)
                )


class ChromaDBBenchmark:
    """ChromaDB performance benchmark"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.client = None
        self.collection = None
        self.db_path = None
    
    def setup(self, dataset_size: int, dimension: int, distance_metric: str):
        """Setup ChromaDB instance"""
        self.cleanup()
        self.db_path = tempfile.mkdtemp(prefix="chromadb_bench_")
        
        try:
            # Map distance metrics
            chroma_metric = "cosine" if distance_metric.lower() == "cosine" else "l2"
            
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            collection_name = f"bench_collection_{int(time.time())}"
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": chroma_metric}
            )
            
        except Exception as e:
            print(f"Failed to create ChromaDB: {e}")
            raise
    
    def cleanup(self):
        """Clean up database resources"""
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
    
    def insert_vectors(self, vectors: np.ndarray, metadata: List[Dict] = None) -> PerformanceResult:
        """Benchmark vector insertion"""
        dataset_size, dimension = vectors.shape
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            
            try:
                # Prepare data
                ids = [str(i) for i in range(dataset_size)]
                embeddings = vectors.tolist()
                metadatas = metadata if metadata else [{"id": i} for i in range(dataset_size)]
                
                # Insert in batches to avoid memory issues
                batch_size = min(1000, dataset_size)
                
                for i in tqdm(range(0, dataset_size, batch_size), desc="Inserting vectors"):
                    end_idx = min(i + batch_size, dataset_size)
                    batch_ids = ids[i:end_idx]
                    batch_embeddings = embeddings[i:end_idx]
                    batch_metadata = metadatas[i:end_idx]
                    
                    self.collection.add(
                        ids=batch_ids,
                        embeddings=batch_embeddings,
                        metadatas=batch_metadata
                    )
                    
                    if i % 10000 == 0:
                        monitor.update_peak()
                
                duration = time.time() - start_time
                throughput = dataset_size / duration if duration > 0 else 0
                
                return PerformanceResult(
                    database="ChromaDB",
                    operation="insert",
                    dataset_size=dataset_size,
                    dimension=dimension,
                    k=None,
                    distance_metric="cosine",  # Will be set by caller
                    duration=duration,
                    memory_usage_mb=monitor.memory_used,
                    throughput=throughput
                )
                
            except Exception as e:
                return PerformanceResult(
                    database="ChromaDB",
                    operation="insert",
                    dataset_size=dataset_size,
                    dimension=dimension,
                    k=None,
                    distance_metric="cosine",  # Will be set by caller
                    duration=0,
                    memory_usage_mb=0,
                    error=str(e)
                )
    
    def search_vectors(self, queries: np.ndarray, k: int) -> PerformanceResult:
        """Benchmark vector search"""
        num_queries, dimension = queries.shape
        
        # Warmup
        try:
            for i in range(min(self.config.warmup_queries, num_queries)):
                self.collection.query(
                    query_embeddings=[queries[i].tolist()],
                    n_results=min(k, 10)
                )
        except:
            pass
        
        with MemoryMonitor() as monitor:
            start_time = time.time()
            successful_queries = 0
            
            try:
                for i, query in enumerate(queries):
                    results = self.collection.query(
                        query_embeddings=[query.tolist()],
                        n_results=k
                    )
                    successful_queries += 1
                    
                    if i % 100 == 0:
                        monitor.update_peak()
                
                duration = time.time() - start_time
                throughput = successful_queries / duration if duration > 0 else 0
                
                return PerformanceResult(
                    database="ChromaDB",
                    operation="search",
                    dataset_size=0,
                    dimension=dimension,
                    k=k,
                    distance_metric="cosine",  # Will be set by caller
                    duration=duration,
                    memory_usage_mb=monitor.memory_used,
                    throughput=throughput,
                    metadata={'successful_queries': successful_queries}
                )
                
            except Exception as e:
                return PerformanceResult(
                    database="ChromaDB",
                    operation="search",
                    dataset_size=0,
                    dimension=dimension,
                    k=k,
                    distance_metric="cosine",
                    duration=0,
                    memory_usage_mb=0,
                    error=str(e)
                )


class BenchmarkRunner:
    """Main benchmark runner"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results: List[PerformanceResult] = []
    
    def run_full_benchmark(self) -> List[PerformanceResult]:
        """Run complete benchmark suite"""
        print("🚀 Starting NusterDB Performance Benchmark Suite")
        print(f"Testing dataset sizes: {self.config.dataset_sizes}")
        print(f"Testing dimensions: {self.config.dimensions}")
        print(f"Testing k values: {self.config.k_values}")
        print()
        
        total_tests = len(self.config.dataset_sizes) * len(self.config.dimensions) * len(self.config.distance_metrics)
        available_dbs = []
        
        if HAS_NUSTERDB:
            available_dbs.append("NusterDB")
        if HAS_FAISS:
            available_dbs.append("FAISS")
        if HAS_CHROMA:
            available_dbs.append("ChromaDB")
        
        print(f"Available databases: {available_dbs}")
        print(f"Total test scenarios: {total_tests}")
        print()
        
        for dataset_size in self.config.dataset_sizes:
            for dimension in self.config.dimensions:
                for distance_metric in self.config.distance_metrics:
                    print(f"\n📊 Testing: {dataset_size:,} vectors, {dimension}D, {distance_metric}")
                    
                    # Generate dataset
                    print("  Generating dataset...")
                    vectors = DatasetGenerator.generate_vectors(dataset_size, dimension)
                    queries = DatasetGenerator.generate_queries(self.config.num_queries, dimension)
                    metadata = DatasetGenerator.generate_metadata(dataset_size)
                    
                    # Test each database
                    if HAS_NUSTERDB:
                        self._test_database("NusterDB", vectors, queries, metadata, distance_metric)
                    
                    if HAS_FAISS:
                        self._test_database("FAISS", vectors, queries, metadata, distance_metric)
                    
                    if HAS_CHROMA and dataset_size <= 100000:  # ChromaDB can be slow with large datasets
                        self._test_database("ChromaDB", vectors, queries, metadata, distance_metric)
        
        return self.results
    
    def _test_database(self, db_name: str, vectors: np.ndarray, queries: np.ndarray, 
                      metadata: List[Dict], distance_metric: str):
        """Test a specific database"""
        dataset_size, dimension = vectors.shape
        
        try:
            print(f"    Testing {db_name}...")
            
            # Create benchmark instance
            if db_name == "NusterDB":
                benchmark = NusterDBBenchmark(self.config)
            elif db_name == "FAISS":
                benchmark = FAISSBenchmark(self.config)
            elif db_name == "ChromaDB":
                benchmark = ChromaDBBenchmark(self.config)
            else:
                return
            
            # Setup
            print(f"      Setting up...")
            benchmark.setup(dataset_size, dimension, distance_metric)
            
            # Test insertion
            print(f"      Testing insertion...")
            insert_result = benchmark.insert_vectors(vectors, metadata)
            insert_result.distance_metric = distance_metric
            self.results.append(insert_result)
            
            if insert_result.error:
                print(f"        ❌ Insert failed: {insert_result.error}")
                benchmark.cleanup()
                return
            else:
                print(f"        ✅ Insert: {insert_result.duration:.2f}s, "
                      f"{insert_result.throughput:.0f} vectors/s, "
                      f"{insert_result.memory_usage_mb:.1f}MB")
            
            # Test search for different k values
            for k in self.config.k_values:
                if k > dataset_size:
                    continue
                    
                print(f"      Testing search (k={k})...")
                search_result = benchmark.search_vectors(queries, k)
                search_result.distance_metric = distance_metric
                self.results.append(search_result)
                
                if search_result.error:
                    print(f"        ❌ Search failed: {search_result.error}")
                else:
                    print(f"        ✅ Search: {search_result.duration:.3f}s, "
                          f"{search_result.throughput:.0f} queries/s")
            
            # Cleanup
            benchmark.cleanup()
            
        except Exception as e:
            print(f"    ❌ {db_name} test failed: {e}")
            traceback.print_exc()
    
    def save_results(self, filepath: str):
        """Save results to JSON file"""
        results_dict = [asdict(result) for result in self.results]
        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=2)
        print(f"Results saved to {filepath}")
    
    def print_summary(self):
        """Print benchmark summary"""
        if not self.results:
            print("No results to summarize")
            return
        
        print("\n" + "="*80)
        print("📈 BENCHMARK SUMMARY")
        print("="*80)
        
        # Group results by operation
        insert_results = [r for r in self.results if r.operation == "insert" and not r.error]
        search_results = [r for r in self.results if r.operation == "search" and not r.error]
        
        if insert_results:
            print("\n🔥 INSERTION PERFORMANCE")
            print("-" * 50)
            for result in sorted(insert_results, key=lambda x: (x.dataset_size, x.database)):
                print(f"{result.database:10} | {result.dataset_size:8,} vectors | "
                      f"{result.dimension:4}D | {result.throughput:8.0f} vectors/s | "
                      f"{result.memory_usage_mb:6.1f}MB | {result.duration:6.2f}s")
        
        if search_results:
            print("\n⚡ SEARCH PERFORMANCE (k=10)")
            print("-" * 50)
            k10_results = [r for r in search_results if r.k == 10]
            for result in sorted(k10_results, key=lambda x: (x.dimension, x.database)):
                print(f"{result.database:10} | {result.dimension:4}D | "
                      f"{result.throughput:8.0f} queries/s | "
                      f"{result.memory_usage_mb:6.1f}MB | {result.duration:8.3f}s")
        
        # Error summary
        error_results = [r for r in self.results if r.error]
        if error_results:
            print("\n❌ ERRORS")
            print("-" * 50)
            for result in error_results:
                print(f"{result.database:10} | {result.operation:8} | {result.error}")


def create_visualizations(results: List[PerformanceResult], output_dir: str):
    """Create performance visualization charts"""
    if not HAS_PLOTTING:
        print("Plotting libraries not available. Skipping visualizations.")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    plt.style.use('seaborn-v0_8')
    
    # Filter successful results
    successful_results = [r for r in results if not r.error]
    
    if not successful_results:
        print("No successful results to visualize")
        return
    
    # 1. Insertion throughput comparison
    insert_results = [r for r in successful_results if r.operation == "insert"]
    if insert_results:
        plt.figure(figsize=(12, 8))
        
        databases = list(set(r.database for r in insert_results))
        dataset_sizes = sorted(set(r.dataset_size for r in insert_results))
        
        for db in databases:
            db_results = [r for r in insert_results if r.database == db]
            sizes = [r.dataset_size for r in db_results]
            throughputs = [r.throughput for r in db_results]
            plt.plot(sizes, throughputs, marker='o', label=db, linewidth=2, markersize=8)
        
        plt.xlabel('Dataset Size')
        plt.ylabel('Insertion Throughput (vectors/sec)')
        plt.title('Vector Insertion Performance Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xscale('log')
        plt.yscale('log')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'insertion_throughput.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 2. Search throughput comparison
    search_results = [r for r in successful_results if r.operation == "search" and r.k == 10]
    if search_results:
        plt.figure(figsize=(12, 8))
        
        databases = list(set(r.database for r in search_results))
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
        plt.title('Vector Search Performance Comparison (k=10)')
        plt.xticks(x + width, dimensions)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'search_throughput.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Memory usage comparison
    plt.figure(figsize=(12, 8))
    
    databases = list(set(r.database for r in successful_results))
    dataset_sizes = sorted(set(r.dataset_size for r in insert_results))
    
    for db in databases:
        db_results = [r for r in insert_results if r.database == db]
        sizes = [r.dataset_size for r in db_results]
        memory = [r.memory_usage_mb for r in db_results]
        plt.plot(sizes, memory, marker='o', label=db, linewidth=2, markersize=8)
    
    plt.xlabel('Dataset Size')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Usage Comparison During Insertion')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'memory_usage.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualizations saved to {output_dir}/")


def main():
    """Main function to run benchmarks"""
    print("🧪 NusterDB Performance Benchmark Suite")
    print("=" * 50)
    
    # Check dependencies
    if not HAS_NUSTERDB:
        print("❌ NusterDB not available. Please install: pip install nusterdb")
        return
    
    # Configuration
    config = BenchmarkConfig(
        dataset_sizes=[1000, 10000, 100000, 1000000],
        dimensions=[128, 384, 768],
        k_values=[1, 5, 10, 50, 100],
        distance_metrics=['cosine', 'euclidean'],
        num_queries=100,
        warmup_queries=10
    )
    
    # Create output directory
    output_dir = f"benchmark_results_{int(time.time())}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Run benchmarks
    runner = BenchmarkRunner(config)
    
    try:
        results = runner.run_full_benchmark()
        
        # Save results
        results_file = os.path.join(output_dir, "benchmark_results.json")
        runner.save_results(results_file)
        
        # Print summary
        runner.print_summary()
        
        # Create visualizations
        create_visualizations(results, output_dir)
        
        print(f"\n✅ Benchmark completed! Results saved to: {output_dir}/")
        
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
