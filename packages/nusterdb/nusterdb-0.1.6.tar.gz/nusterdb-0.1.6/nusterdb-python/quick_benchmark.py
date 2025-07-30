#!/usr/bin/env python3
"""
NusterDB Quick Performance Test
===============================

A simplified version of the benchmark suite for quick testing and validation.
This script runs smaller-scale tests to verify functionality and get initial performance metrics.
"""

import os
import sys
import time
import tempfile
import shutil
from typing import List, Tuple
import numpy as np
from tqdm import tqdm

# Import the libraries
try:
    import nusterdb
    from nusterdb import NusterDB, Vector, Metadata
    print(f"✅ NusterDB v{nusterdb.__version__} loaded")
except ImportError:
    print("❌ NusterDB not available")
    sys.exit(1)

try:
    import faiss
    print("✅ FAISS loaded")
    HAS_FAISS = True
except ImportError:
    print("⚠️  FAISS not available")
    HAS_FAISS = False

try:
    import chromadb
    print("✅ ChromaDB loaded")
    HAS_CHROMA = True
except ImportError:
    print("⚠️  ChromaDB not available")
    HAS_CHROMA = False

def generate_test_data(n: int, dim: int) -> Tuple[np.ndarray, np.ndarray]:
    """Generate test vectors and queries"""
    np.random.seed(42)
    # Generate normalized vectors for cosine similarity
    vectors = np.random.normal(0, 1, (n, dim)).astype(np.float32)
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    
    # Generate query vectors
    np.random.seed(123)
    queries = np.random.normal(0, 1, (100, dim)).astype(np.float32)
    queries = queries / np.linalg.norm(queries, axis=1, keepdims=True)
    
    return vectors, queries

def test_nusterdb(vectors: np.ndarray, queries: np.ndarray) -> dict:
    """Test NusterDB performance"""
    n, dim = vectors.shape
    print(f"\n🔥 Testing NusterDB ({n:,} vectors, {dim}D)")
    
    # Setup
    db_path = tempfile.mkdtemp(prefix="nusterdb_test_")
    
    try:
        # Create database
        start_time = time.time()
        db = NusterDB.simple(db_path, dim=dim, use_hnsw=True if n > 1000 else False)
        setup_time = time.time() - start_time
        
        # Insert vectors
        print("  Inserting vectors...")
        start_time = time.time()
        for i, vector in enumerate(tqdm(vectors, desc="    Progress")):
            vec = Vector(vector.tolist())
            metadata = Metadata.with_data({"id": str(i), "category": f"cat_{i % 5}"})
            db.add(i, vec, metadata)
        
        insert_time = time.time() - start_time
        insert_throughput = n / insert_time
        
        # Search vectors
        print("  Searching vectors...")
        k = min(10, n)
        start_time = time.time()
        total_results = 0
        
        for query in tqdm(queries[:50], desc="    Progress"):  # Test with 50 queries
            query_vec = Vector(query.tolist())
            results = db.search(query_vec, k=k)
            total_results += len(results)
        
        search_time = time.time() - start_time
        search_throughput = 50 / search_time  # 50 queries
        
        # Get some stats
        stats = db.stats()
        
        return {
            "database": "NusterDB",
            "setup_time": setup_time,
            "insert_time": insert_time,
            "insert_throughput": insert_throughput,
            "search_time": search_time,
            "search_throughput": search_throughput,
            "total_results": total_results,
            "index_type": db.index_type(),
            "dimension": db.dimension(),
            "error": None
        }
        
    except Exception as e:
        return {
            "database": "NusterDB",
            "error": str(e)
        }
    finally:
        # Cleanup
        if os.path.exists(db_path):
            shutil.rmtree(db_path, ignore_errors=True)

def test_faiss(vectors: np.ndarray, queries: np.ndarray) -> dict:
    """Test FAISS performance"""
    if not HAS_FAISS:
        return {"database": "FAISS", "error": "FAISS not available"}
        
    n, dim = vectors.shape
    print(f"\n⚡ Testing FAISS ({n:,} vectors, {dim}D)")
    
    try:
        # Setup
        start_time = time.time()
        if n > 10000:
            # Use IVF for large datasets
            nlist = min(4096, n // 50)
            quantizer = faiss.IndexFlatIP(dim)  # Inner product for cosine
            index = faiss.IndexIVFFlat(quantizer, dim, nlist)
        else:
            # Use flat index for small datasets
            index = faiss.IndexFlatIP(dim)
        
        setup_time = time.time() - start_time
        
        # Insert vectors
        print("  Training and inserting vectors...")
        start_time = time.time()
        
        if hasattr(index, 'train') and not index.is_trained:
            index.train(vectors)
        
        index.add(vectors)
        insert_time = time.time() - start_time
        insert_throughput = n / insert_time
        
        # Search vectors
        print("  Searching vectors...")
        k = min(10, n)
        start_time = time.time()
        
        test_queries = queries[:50]  # Test with 50 queries
        distances, indices = index.search(test_queries, k)
        
        search_time = time.time() - start_time
        search_throughput = 50 / search_time
        total_results = np.sum(indices >= 0)  # Count valid results
        
        return {
            "database": "FAISS",
            "setup_time": setup_time,
            "insert_time": insert_time,
            "insert_throughput": insert_throughput,
            "search_time": search_time,
            "search_throughput": search_throughput,
            "total_results": total_results,
            "index_type": "IVF" if hasattr(index, 'train') else "Flat",
            "dimension": dim,
            "error": None
        }
        
    except Exception as e:
        return {
            "database": "FAISS",
            "error": str(e)
        }

def test_chromadb(vectors: np.ndarray, queries: np.ndarray) -> dict:
    """Test ChromaDB performance"""
    if not HAS_CHROMA:
        return {"database": "ChromaDB", "error": "ChromaDB not available"}
        
    n, dim = vectors.shape
    print(f"\n🚀 Testing ChromaDB ({n:,} vectors, {dim}D)")
    
    # Skip ChromaDB for very large datasets as it can be slow
    if n > 50000:
        return {"database": "ChromaDB", "error": "Skipped - dataset too large for ChromaDB test"}
    
    db_path = tempfile.mkdtemp(prefix="chromadb_test_")
    
    try:
        # Setup
        start_time = time.time()
        client = chromadb.PersistentClient(
            path=db_path,
            settings=chromadb.config.Settings(anonymized_telemetry=False)
        )
        collection = client.create_collection(
            name="test_collection",
            metadata={"hnsw:space": "cosine"}
        )
        setup_time = time.time() - start_time
        
        # Insert vectors
        print("  Inserting vectors...")
        start_time = time.time()
        
        # Prepare data
        ids = [str(i) for i in range(n)]
        embeddings = vectors.tolist()
        metadatas = [{"id": i, "category": f"cat_{i % 5}"} for i in range(n)]
        
        # Insert in batches
        batch_size = min(1000, n)
        for i in tqdm(range(0, n, batch_size), desc="    Progress"):
            end_idx = min(i + batch_size, n)
            collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
        
        insert_time = time.time() - start_time
        insert_throughput = n / insert_time
        
        # Search vectors
        print("  Searching vectors...")
        k = min(10, n)
        start_time = time.time()
        total_results = 0
        
        for query in tqdm(queries[:50], desc="    Progress"):  # Test with 50 queries
            results = collection.query(
                query_embeddings=[query.tolist()],
                n_results=k
            )
            total_results += len(results['ids'][0]) if results['ids'] else 0
        
        search_time = time.time() - start_time
        search_throughput = 50 / search_time
        
        return {
            "database": "ChromaDB",
            "setup_time": setup_time,
            "insert_time": insert_time,
            "insert_throughput": insert_throughput,
            "search_time": search_time,
            "search_throughput": search_throughput,
            "total_results": total_results,
            "index_type": "HNSW",
            "dimension": dim,
            "error": None
        }
        
    except Exception as e:
        return {
            "database": "ChromaDB",
            "error": str(e)
        }
    finally:
        # Cleanup
        try:
            if 'client' in locals():
                client.reset()
        except:
            pass
        if os.path.exists(db_path):
            shutil.rmtree(db_path, ignore_errors=True)

def print_results(results: List[dict]):
    """Print benchmark results"""
    print("\n" + "="*80)
    print("📊 PERFORMANCE COMPARISON RESULTS")
    print("="*80)
    
    successful_results = [r for r in results if not r.get('error')]
    failed_results = [r for r in results if r.get('error')]
    
    if successful_results:
        print("\n🏆 SUCCESSFUL TESTS")
        print("-" * 70)
        print(f"{'Database':<12} {'Insert (vec/s)':<15} {'Search (q/s)':<15} {'Index Type':<12}")
        print("-" * 70)
        
        for result in successful_results:
            print(f"{result['database']:<12} "
                  f"{result['insert_throughput']:>12,.0f}   "
                  f"{result['search_throughput']:>12,.1f}   "
                  f"{result['index_type']:<12}")
    
    if failed_results:
        print("\n❌ FAILED TESTS")
        print("-" * 50)
        for result in failed_results:
            print(f"{result['database']:<12} {result['error']}")
    
    print("\n" + "="*80)

def main():
    """Run quick performance test"""
    print("🧪 NusterDB Quick Performance Test")
    print("=" * 50)
    
    # Test configurations - start small and scale up
    test_configs = [
        (1000, 128),    # 1K vectors, 128D
        (10000, 128),   # 10K vectors, 128D  
        (100000, 128),  # 100K vectors, 128D
        (1000000, 128), # 1M vectors, 128D
    ]
    
    for n_vectors, dimension in test_configs:
        print(f"\n{'='*60}")
        print(f"🔬 Testing with {n_vectors:,} vectors, {dimension} dimensions")
        print(f"{'='*60}")
        
        # Generate test data
        print("Generating test data...")
        vectors, queries = generate_test_data(n_vectors, dimension)
        print(f"✓ Generated {len(vectors):,} vectors and {len(queries)} queries")
        
        # Run tests
        results = []
        
        # Test NusterDB
        result = test_nusterdb(vectors, queries)
        results.append(result)
        
        # Test FAISS
        result = test_faiss(vectors, queries)
        results.append(result)
        
        # Test ChromaDB (skip for large datasets)
        if n_vectors <= 50000:
            result = test_chromadb(vectors, queries)
            results.append(result)
        
        # Print results for this configuration
        print_results(results)
        
        # Quick summary
        successful = [r for r in results if not r.get('error')]
        if successful:
            best_insert = max(successful, key=lambda x: x['insert_throughput'])
            best_search = max(successful, key=lambda x: x['search_throughput'])
            
            print(f"\n🥇 Best Insert Performance: {best_insert['database']} "
                  f"({best_insert['insert_throughput']:,.0f} vectors/sec)")
            print(f"🥇 Best Search Performance: {best_search['database']} "
                  f"({best_search['search_throughput']:.1f} queries/sec)")
        
        # Memory cleanup
        del vectors, queries
        import gc
        gc.collect()

if __name__ == "__main__":
    main()
