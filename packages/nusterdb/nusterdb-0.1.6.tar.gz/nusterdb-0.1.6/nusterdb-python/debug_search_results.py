#!/usr/bin/env python3
"""
Simple test to check the structure of search results.
"""

import os
import shutil
import random
import nusterdb

def test_search_results():
    db_path = "./test_search_results"
    
    # Cleanup
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    
    try:
        # Create database
        db = nusterdb.NusterDB.optimized_flat(db_path, 128)
        
        # Add a few vectors
        random.seed(42)
        for i in range(10):
            data = [random.gauss(0, 1) for _ in range(128)]
            vector = nusterdb.Vector(data)
            metadata = nusterdb.Metadata()
            metadata.set("id", str(i))
            db.add(i, vector, metadata)
        
        # Search
        query_data = [random.gauss(0, 1) for _ in range(128)]
        query_vector = nusterdb.Vector(query_data)
        results = db.search(query_vector, k=5)
        
        print(f"Results type: {type(results)}")
        print(f"Number of results: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"Result {i}:")
            print(f"  Type: {type(result)}")
            if hasattr(result, '__dict__'):
                print(f"  Attributes: {result.__dict__}")
            if isinstance(result, tuple):
                print(f"  Tuple contents: {result}")
            if hasattr(result, 'id'):
                print(f"  ID: {result.id}")
            if hasattr(result, 'distance'):
                print(f"  Distance: {result.distance}")
            print()
    
    finally:
        # Cleanup
        if os.path.exists(db_path):
            shutil.rmtree(db_path)

if __name__ == "__main__":
    test_search_results()
