#!/usr/bin/env python3
"""
Test the new numpy-optimized bulk_add_numpy method
"""

import time
import numpy as np
import nusterdb as ndb

def test_numpy_optimization():
    """Test the numpy optimized bulk_add method"""
    
    print("=== Testing Numpy-Optimized Bulk Add ===\n")
    
    # Test with different sizes
    test_sizes = [1000, 10000, 50000]
    dimension = 128
    
    for num_vectors in test_sizes:
        print(f"Testing {num_vectors:,} vectors × {dimension}D")
        print("-" * 50)
        
        # Generate test data
        np_vectors = np.random.randn(num_vectors, dimension).astype(np.float32)
        ids = list(range(num_vectors))
        
        # Test regular bulk_add (with Vector objects)
        print("Regular bulk_add:")
        try:
            db_path = f"numpy_test_regular_{num_vectors}.db"
            config = ndb.DatabaseConfig(dimension, "ultra_high_speed_flat")
            db = ndb.NusterDB(db_path, config)
            
            # Convert to Vector objects
            start = time.time()
            vector_objects = [ndb.Vector(vec.tolist()) for vec in np_vectors]
            conversion_time = time.time() - start
            
            # Bulk add
            start = time.time()
            db.bulk_add(ids, vector_objects)
            insertion_time = time.time() - start
            
            total_time = conversion_time + insertion_time
            speed = num_vectors / insertion_time
            total_speed = num_vectors / total_time
            
            print(f"  Conversion Time: {conversion_time:.6f}s")
            print(f"  Insertion Time: {insertion_time:.6f}s") 
            print(f"  Total Time: {total_time:.6f}s")
            print(f"  Pure Insertion Speed: {speed:,.0f} vectors/sec")
            print(f"  End-to-End Speed: {total_speed:,.0f} vectors/sec")
            
            del db
            import os
            try:
                os.remove(db_path)
            except:
                pass
                
        except Exception as e:
            print(f"  ERROR: {e}")
        
        # Test numpy bulk_add_numpy (optimized)
        print("\nNumpy bulk_add_numpy:")
        try:
            db_path = f"numpy_test_optimized_{num_vectors}.db"
            config = ndb.DatabaseConfig(dimension, "ultra_high_speed_flat")
            db = ndb.NusterDB(db_path, config)
            
            # Direct numpy insertion (no conversion needed)
            start = time.time()
            db.bulk_add_numpy(ids, np_vectors)
            insertion_time = time.time() - start
            
            speed = num_vectors / insertion_time
            
            print(f"  Insertion Time: {insertion_time:.6f}s")
            print(f"  Speed: {speed:,.0f} vectors/sec")
            print(f"  Target (500K): {'✓ ACHIEVED' if speed >= 500000 else '✗ NOT REACHED'}")
            
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
    test_numpy_optimization()
