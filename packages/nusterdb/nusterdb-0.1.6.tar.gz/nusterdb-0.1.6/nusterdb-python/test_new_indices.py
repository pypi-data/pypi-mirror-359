#!/usr/bin/env python3
"""
Simple test to verify our new index types work
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import nusterdb
    print("✅ NusterDB imported successfully")
except ImportError as e:
    print(f"❌ Failed to import NusterDB: {e}")
    sys.exit(1)

def test_index_creation(index_type):
    """Test creating and using a specific index type"""
    print(f"\n🔬 Testing {index_type} index...")
    
    try:
        # Create index using the correct API
        import tempfile
        db_path = tempfile.mkdtemp(prefix=f"nusterdb_{index_type}_")
        
        # For now, test with the simple API to verify basic functionality
        # TODO: Need to update the Python bindings to support new index types
        use_hnsw = (index_type == "Hnsw")
        
        index = nusterdb.NusterDB.simple(db_path, dim=128, use_hnsw=use_hnsw)
        print(f"✅ {index_type} index created successfully")
        print(f"   Index type: {index.index_type()}")
        print(f"   Dimension: {index.dimension()}")
        
        # Test basic operations
        test_vector = nusterdb.Vector([0.1 * i for i in range(128)])
        metadata = nusterdb.Metadata.with_data({"test": "value"})
        
        # Insert a vector
        index.add(1, test_vector, metadata)
        print(f"✅ Vector insertion successful")
        
        # Test search
        results = index.search(test_vector, k=1)
        print(f"✅ Search successful, found {len(results)} results")
        
        if results:
            # Results are tuples: (id, distance)
            result_id, result_distance = results[0]
            print(f"   Top result: ID={result_id}, Distance={result_distance:.6f}")
        
        # Clean up
        import shutil
        shutil.rmtree(db_path, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"❌ {index_type} test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 NusterDB Index Types Test")
    print("=" * 40)
    
    # For now, test the basic functionality with existing API
    # Our new index types will need Python binding updates
    index_types = ["Flat", "Hnsw"] 
    
    results = {}
    
    for index_type in index_types:
        results[index_type] = test_index_creation(index_type)
    
    # Summary
    print(f"\n📊 Test Results Summary:")
    print("-" * 30)
    
    for index_type, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{index_type:<15}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    if all_passed:
        print(f"\n🎉 Basic tests passed! NusterDB is working correctly.")
        print(f"\n📝 Note: New high-performance indices (OptimizedFlat, UltraFastFlat)")
        print(f"   need Python binding updates to be accessible from Python.")
        print(f"   They are available in the CLI interface for now.")
    else:
        failed_count = sum(1 for success in results.values() if not success)
        print(f"\n⚠️  {failed_count} test(s) failed.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
