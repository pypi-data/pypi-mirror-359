#!/usr/bin/env python3
"""
Ultra-High-Speed Insertion Test for NusterDB
Target: 500,000+ vectors/second insertion speed
"""

import time
import numpy as np
import os
import gc
from typing import List, Tuple, Dict, Any

# Import our libraries
import nusterdb as ndb
import faiss

def generate_vectors(num_vectors: int, dimension: int, seed: int = 42) -> np.ndarray:
    """Generate random vectors for testing"""
    np.random.seed(seed)
    vectors = np.random.randn(num_vectors, dimension).astype(np.float32)
    # Normalize vectors for better testing
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    vectors = vectors / norms
    return vectors

def test_ultra_high_speed_insertion(num_vectors: int, dimension: int) -> Dict[str, float]:
    """Test ultra-high-speed insertion with different NusterDB configurations"""
    
    print(f"\n=== Testing Ultra-High-Speed Insertion: {num_vectors:,} vectors x {dimension}D ===")
    
    vectors = generate_vectors(num_vectors, dimension)
    ids = list(range(len(vectors)))
    
    results = {}
    
    # Test configurations
    configs = [
        ("UltraHighSpeed", "ultra_high_speed_flat"),
        ("UltraOptimized", "ultra_optimized_flat"),
        ("FAISSInspired", "faiss_inspired_flat"),
    ]
    
    for config_name, index_type in configs:
        print(f"\n--- Testing NusterDB {config_name} ---")
        
        try:
            # Clean up any existing database
            db_path = f"ultra_speed_test_{config_name.lower()}.db"
            if os.path.exists(db_path):
                os.remove(db_path)
            
            # Create database configuration
            config = ndb.DatabaseConfig(
                dim=dimension,
                index_type=index_type,
                distance_metric=ndb.DistanceMetric.euclidean()
            )
            
            # Create database
            start_create = time.time()
            db = ndb.NusterDB(db_path, config)
            create_time = time.time() - start_create
            
            # Time the bulk insertion
            start_time = time.time()
            
            # Convert to Vector objects
            vector_objects = [ndb.Vector(vec.tolist()) for vec in vectors]
            
            # Use bulk insert for maximum speed
            if hasattr(db, 'bulk_add'):
                db.bulk_add(ids, vector_objects)
            else:
                # Fallback - this should not happen with our implementation
                for i, vector in enumerate(vector_objects):
                    db.add(i, vector)
            
            end_time = time.time()
            
            # Calculate metrics
            insertion_time = end_time - start_time
            vectors_per_second = len(vectors) / insertion_time if insertion_time > 0 else 0
            
            results[config_name] = {
                'insertion_time': insertion_time,
                'create_time': create_time,
                'total_time': insertion_time + create_time,
                'vectors_per_second': vectors_per_second,
                'success': True
            }
            
            print(f"  Creation Time: {create_time:.3f}s")
            print(f"  Insertion Time: {insertion_time:.3f}s")
            print(f"  Total Time: {insertion_time + create_time:.3f}s")
            print(f"  Speed: {vectors_per_second:,.0f} vectors/sec")
            print(f"  Target (500K): {'✓ ACHIEVED' if vectors_per_second >= 500000 else '✗ NOT REACHED'}")
            
            # Clean up
            del db
            if os.path.exists(db_path):
                os.remove(db_path)
                
        except Exception as e:
            print(f"  ERROR: {e}")
            results[config_name] = {
                'insertion_time': float('inf'),
                'vectors_per_second': 0,
                'success': False,
                'error': str(e)
            }
        
        gc.collect()
        time.sleep(0.5)
    
    return results

def test_faiss_comparison(num_vectors: int, dimension: int) -> Dict[str, float]:
    """Test FAISS for comparison"""
    print(f"\n--- Testing FAISS Comparison ---")
    
    vectors = generate_vectors(num_vectors, dimension)
    results = {}
    
    # Test FAISS Flat (most comparable to our flat indices)
    try:
        start_time = time.time()
        
        # Create FAISS flat index
        index = faiss.IndexFlatL2(dimension)
        
        # Add vectors
        index.add(vectors)
        
        end_time = time.time()
        
        total_time = end_time - start_time
        vectors_per_second = len(vectors) / total_time if total_time > 0 else 0
        
        results['FAISS_Flat'] = {
            'insertion_time': total_time,
            'vectors_per_second': vectors_per_second,
            'total_vectors': index.ntotal,
            'success': True
        }
        
        print(f"  FAISS Flat Time: {total_time:.3f}s")
        print(f"  FAISS Flat Speed: {vectors_per_second:,.0f} vectors/sec")
        print(f"  FAISS Target (500K): {'✓ ACHIEVED' if vectors_per_second >= 500000 else '✗ NOT REACHED'}")
        
        del index
        
    except Exception as e:
        print(f"  FAISS ERROR: {e}")
        results['FAISS_Flat'] = {
            'insertion_time': float('inf'),
            'vectors_per_second': 0,
            'success': False,
            'error': str(e)
        }
    
    return results

def run_progressive_speed_test():
    """Run progressive speed tests with increasing vector counts"""
    print("Progressive Ultra-High-Speed Insertion Test")
    print("Target: 500,000+ vectors/second insertion speed")
    print("="*80)
    
    # Test configurations: (num_vectors, dimension)
    test_configs = [
        (10000, 128),     # Warm-up
        (50000, 128),     # Medium test
        (100000, 128),    # Large test
        (250000, 128),    # Very large test
        (500000, 128),    # Ultra-large test - main target
        (1000000, 128),   # Million vector test
    ]
    
    all_results = {}
    
    for num_vectors, dimension in test_configs:
        test_name = f"{num_vectors//1000}K_vectors"
        print(f"\n{'='*80}")
        print(f"TEST: {num_vectors:,} vectors × {dimension}D")
        print(f"{'='*80}")
        
        # Test NusterDB
        nuster_results = test_ultra_high_speed_insertion(num_vectors, dimension)
        
        # Test FAISS for comparison
        faiss_results = test_faiss_comparison(num_vectors, dimension)
        
        # Combine results
        combined_results = {**nuster_results, **faiss_results}
        all_results[test_name] = combined_results
        
        # Show immediate comparison
        print(f"\n--- Speed Comparison for {num_vectors:,} vectors ---")
        for system, result in combined_results.items():
            if result['success']:
                speed = result['vectors_per_second']
                target_met = "✓" if speed >= 500000 else "✗"
                print(f"  {system:<15}: {speed:>10,.0f} vectors/sec  {target_met}")
            else:
                print(f"  {system:<15}: {'ERROR':>10}")
        
        # Clean up
        gc.collect()
        time.sleep(1)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL ULTRA-HIGH-SPEED INSERTION SUMMARY")
    print("="*80)
    
    # Find best performers
    best_speed = 0
    best_system = ""
    best_test = ""
    
    for test_name, results in all_results.items():
        print(f"\n{test_name.upper().replace('_', ' ')}:")
        print("-" * 40)
        
        for system, result in results.items():
            if result['success']:
                speed = result['vectors_per_second']
                target = "✓" if speed >= 500000 else "✗"
                print(f"  {system:<15}: {speed:>10,.0f} v/s  {target}")
                
                if speed > best_speed:
                    best_speed = speed
                    best_system = system
                    best_test = test_name
            else:
                print(f"  {system:<15}: {'ERROR':>10}")
    
    print("\n" + "="*80)
    print("BEST PERFORMANCE:")
    print(f"  System: {best_system}")
    print(f"  Test: {best_test}")
    print(f"  Speed: {best_speed:,.0f} vectors/second")
    print(f"  Target Achievement: {'✓ ACHIEVED' if best_speed >= 500000 else '✗ NOT REACHED'} (500K target)")
    
    if best_speed >= 500000:
        print(f"🎉 SUCCESS! NusterDB achieved {best_speed:,.0f} vectors/sec with {best_system}")
    else:
        print(f"⚠️  Target not reached. Best: {best_speed:,.0f} vectors/sec (need 500K+)")
    
    print("="*80)

def main():
    """Main test execution"""
    run_progressive_speed_test()

if __name__ == "__main__":
    main()
