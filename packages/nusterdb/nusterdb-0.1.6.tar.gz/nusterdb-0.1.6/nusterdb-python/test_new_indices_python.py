#!/usr/bin/env python3
"""
Test script for the new high-performance index types in NusterDB.
This script tests OptimizedFlat and UltraFastFlat indices through the Python API.
"""

import os
import sys
import shutil
import time
import random
import nusterdb
from typing import List, Tuple

def cleanup_db_folder(path: str):
    """Remove database folder if it exists."""
    if os.path.exists(path):
        shutil.rmtree(path)

def create_test_vectors(num_vectors: int, dim: int) -> List[nusterdb.Vector]:
    """Create test vectors with reproducible random data."""
    random.seed(42)
    vectors = []
    for i in range(num_vectors):
        # Create random vector data
        data = [random.gauss(0, 1) for _ in range(dim)]
        vectors.append(nusterdb.Vector(data))
    return vectors

def test_index_type(index_type: str, db_path: str, num_vectors: int = 1000, dim: int = 128):
    """Test a specific index type."""
    print(f"\n=== Testing {index_type} Index ===")
    
    # Cleanup
    cleanup_db_folder(db_path)
    
    try:
        # Create database with the specified index type
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
        
        print(f"✓ Created database with {index_type} index")
        print(f"  - Index type: {db.index_type()}")
        print(f"  - Dimension: {db.dimension()}")
        
        # Create test vectors
        print(f"Creating {num_vectors} test vectors...")
        vectors = create_test_vectors(num_vectors, dim)
        
        # Test insertion
        print("Testing insertion...")
        start_time = time.time()
        
        for i, vector in enumerate(vectors):
            metadata = nusterdb.Metadata()
            metadata.set("id", str(i))
            metadata.set("category", f"test_{i % 10}")
            metadata.add_tag(f"tag_{i % 5}")
            
            db.add(i, vector, metadata)
            
            if (i + 1) % 100 == 0:
                print(f"  Inserted {i + 1}/{num_vectors} vectors")
        
        insertion_time = time.time() - start_time
        insertion_rate = num_vectors / insertion_time
        print(f"✓ Insertion completed in {insertion_time:.2f}s ({insertion_rate:.0f} vectors/sec)")
        
        # Test search
        print("Testing search...")
        query_vector = vectors[0]  # Use first vector as query
        
        start_time = time.time()
        results = db.search(query_vector, k=10)
        search_time = time.time() - start_time
        
        print(f"✓ Search completed in {search_time*1000:.2f}ms")
        print(f"  Found {len(results)} results")
        
        if results:
            # Results are tuples (id, distance)
            result_id, result_distance = results[0]
            print(f"  Top result: ID={result_id}, Distance={result_distance:.6f}")
            
            # First result should be the exact same vector
            if result_id == 0:
                print("  ✓ Exact match found at top position")
            else:
                print("  ⚠ Warning: Exact match not at top position")
        
        # Test with metadata filter
        print("Testing search with metadata filter...")
        filter_dict = {"category": "test_0"}
        start_time = time.time()
        filtered_results = db.search(query_vector, k=5, filter=filter_dict)
        filtered_search_time = time.time() - start_time
        
        print(f"✓ Filtered search completed in {filtered_search_time*1000:.2f}ms")
        print(f"  Found {len(filtered_results)} filtered results")
        
        # Test snapshot functionality
        print("Testing snapshot functionality...")
        snapshot_name = f"test_snapshot_{index_type}"
        db.snapshot_named(snapshot_name)
        print(f"✓ Created snapshot: {snapshot_name}")
        
        # Test statistics
        print("Testing statistics...")
        stats = db.stats()
        print(f"✓ Database statistics retrieved")
        print(f"  Vector count: {stats.vector_count}")
        # Note: index_size_bytes might not be available in all versions
        if hasattr(stats, 'index_size_bytes'):
            print(f"  Index size: {stats.index_size_bytes} bytes")
        else:
            print("  Index size: (not available)")
        
        return {
            "index_type": index_type,
            "insertion_time": insertion_time,
            "insertion_rate": insertion_rate,
            "search_time": search_time,
            "filtered_search_time": filtered_search_time,
            "vector_count": num_vectors,
            "success": True
        }
        
    except Exception as e:
        print(f"✗ Error testing {index_type}: {e}")
        return {
            "index_type": index_type,
            "error": str(e),
            "success": False
        }
    
    finally:
        # Cleanup
        cleanup_db_folder(db_path)

def run_performance_comparison():
    """Run performance comparison between all index types."""
    print("=" * 60)
    print("NUSTERDB NEW INDEX TYPES - PERFORMANCE COMPARISON")
    print("=" * 60)
    
    # Test parameters
    num_vectors = 5000
    dim = 128
    
    index_types = [
        "flat",
        "optimized-flat", 
        "ultra-fast-flat",
        "hnsw"
    ]
    
    results = []
    
    for index_type in index_types:
        db_path = f"./test_db_{index_type.replace('-', '_')}"
        result = test_index_type(index_type, db_path, num_vectors, dim)
        results.append(result)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    
    successful_results = [r for r in results if r.get("success", False)]
    
    if successful_results:
        print(f"{'Index Type':<20} {'Insertion (vec/s)':<15} {'Search (ms)':<15}")
        print("-" * 50)
        
        for result in successful_results:
            insertion_rate = result.get("insertion_rate", 0)
            search_time = result.get("search_time", 0) * 1000
            print(f"{result['index_type']:<20} {insertion_rate:<15.0f} {search_time:<15.2f}")
        
        # Find best performers
        best_insertion = max(successful_results, key=lambda x: x.get("insertion_rate", 0))
        best_search = min(successful_results, key=lambda x: x.get("search_time", float('inf')))
        
        print(f"\nBest insertion performance: {best_insertion['index_type']} "
              f"({best_insertion['insertion_rate']:.0f} vectors/sec)")
        print(f"Best search performance: {best_search['index_type']} "
              f"({best_search['search_time']*1000:.2f} ms)")
    
    # Print any errors
    failed_results = [r for r in results if not r.get("success", False)]
    if failed_results:
        print(f"\nFailed tests:")
        for result in failed_results:
            print(f"- {result['index_type']}: {result.get('error', 'Unknown error')}")
    
    return results

if __name__ == "__main__":
    try:
        results = run_performance_comparison()
        
        # Check if all new index types worked
        new_index_types = ["optimized-flat", "ultra-fast-flat"]
        new_results = [r for r in results if r["index_type"] in new_index_types]
        successful_new = [r for r in new_results if r.get("success", False)]
        
        if len(successful_new) == len(new_index_types):
            print(f"\n✓ SUCCESS: All new index types ({', '.join(new_index_types)}) are working!")
            sys.exit(0)
        else:
            print(f"\n✗ FAILURE: Some new index types failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        sys.exit(1)
