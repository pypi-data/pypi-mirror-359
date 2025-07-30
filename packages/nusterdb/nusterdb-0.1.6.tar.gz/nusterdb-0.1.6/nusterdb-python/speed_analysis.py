#!/usr/bin/env python3
"""
Focused Speed Analysis: NusterDB vs FAISS
"""

import time
import numpy as np
import nusterdb as ndb
import faiss

def analyze_insertion_bottlenecks():
    """Analyze where the insertion bottlenecks are"""
    
    print("=== NusterDB vs FAISS Insertion Speed Analysis ===\n")
    
    # Test with different sizes
    test_sizes = [1000, 10000, 50000, 100000]
    dimension = 128
    
    for num_vectors in test_sizes:
        print(f"Testing {num_vectors:,} vectors × {dimension}D")
        print("-" * 50)
        
        # Generate test data
        np_vectors = np.random.randn(num_vectors, dimension).astype(np.float32)
        ids = list(range(num_vectors))
        
        # Test FAISS (baseline)
        print("FAISS:")
        try:
            start = time.time()
            faiss_index = faiss.IndexFlatL2(dimension)
            faiss_index.add(np_vectors)
            faiss_time = time.time() - start
            faiss_speed = num_vectors / faiss_time
            print(f"  Time: {faiss_time:.6f}s")
            print(f"  Speed: {faiss_speed:,.0f} vectors/sec")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        # Test different NusterDB indices
        indices = [
            ("UltraHighSpeed", "ultra_high_speed_flat"),
            ("UltraOptimized", "ultra_optimized_flat"),
            ("FAISSInspired", "faiss_inspired_flat"),
        ]
        
        for idx_name, idx_type in indices:
            print(f"\nNusterDB {idx_name}:")
            
            try:
                db_path = f"speed_test_{idx_name.lower()}_{num_vectors}.db"
                
                # Time database creation
                start = time.time()
                config = ndb.DatabaseConfig(dimension, idx_type)
                db = ndb.NusterDB(db_path, config)
                create_time = time.time() - start
                
                # Time vector conversion
                start = time.time()
                vector_objects = [ndb.Vector(vec.tolist()) for vec in np_vectors]
                conversion_time = time.time() - start
                
                # Time actual insertion
                start = time.time()
                db.bulk_add(ids, vector_objects)
                insertion_time = time.time() - start
                
                total_time = create_time + conversion_time + insertion_time
                speed = num_vectors / insertion_time if insertion_time > 0 else 0
                total_speed = num_vectors / total_time if total_time > 0 else 0
                
                print(f"  Create Time: {create_time:.6f}s")
                print(f"  Conversion Time: {conversion_time:.6f}s")
                print(f"  Insertion Time: {insertion_time:.6f}s")
                print(f"  Total Time: {total_time:.6f}s")
                print(f"  Pure Insertion Speed: {speed:,.0f} vectors/sec")
                print(f"  End-to-End Speed: {total_speed:,.0f} vectors/sec")
                
                # Clean up
                del db
                import os
                try:
                    os.remove(db_path)
                except:
                    pass
                    
            except Exception as e:
                print(f"  ERROR: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    analyze_insertion_bottlenecks()
