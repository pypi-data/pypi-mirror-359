#!/usr/bin/env python3
"""
Cleanup script to remove all test databases and free memory
"""

import os
import shutil
import gc
import sys

def cleanup_databases():
    """Remove all test database directories"""
    print("🧹 Cleaning up test databases...")
    
    # List of potential test database locations
    test_paths = [
        "/tmp/nusterdb_memory_test_faiss_inspired",
        "/tmp/nusterdb_memory_test_ultra_optimized",
        "/tmp/nusterdb_quantized_test",
        "/tmp/nusterdb_ultra_test",
        "/tmp/nusterdb_faiss_test",
        "/tmp/test_db",
    ]
    
    # Find and remove test databases in /tmp
    for root, dirs, files in os.walk("/tmp"):
        for dir_name in dirs:
            if "nusterdb" in dir_name.lower() or "test_db" in dir_name.lower():
                full_path = os.path.join(root, dir_name)
                test_paths.append(full_path)
    
    # Remove duplicates
    test_paths = list(set(test_paths))
    
    removed_count = 0
    for path in test_paths:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"  Removed directory: {path}")
                    removed_count += 1
                elif os.path.isfile(path):
                    os.remove(path)
                    print(f"  Removed file: {path}")
                    removed_count += 1
            except Exception as e:
                print(f"  Failed to remove {path}: {e}")
    
    print(f"✓ Removed {removed_count} test database(s)")

def cleanup_log_files():
    """Remove log files from the nusterdb directory"""
    print("🧹 Cleaning up log files...")
    
    log_patterns = ["*.log", "*.LOG"]
    nusterdb_path = "/Users/shashidharnaidu/nuster_ai/nusterdb"
    
    removed_count = 0
    if os.path.exists(nusterdb_path):
        for root, dirs, files in os.walk(nusterdb_path):
            for file in files:
                if file.endswith('.log') or file.endswith('.LOG'):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"  Removed log: {file_path}")
                        removed_count += 1
                    except Exception as e:
                        print(f"  Failed to remove {file_path}: {e}")
    
    print(f"✓ Removed {removed_count} log file(s)")

def cleanup_memory():
    """Force garbage collection"""
    print("🧹 Cleaning up memory...")
    
    # Force multiple garbage collection cycles
    for i in range(3):
        collected = gc.collect()
        if collected > 0:
            print(f"  GC cycle {i+1}: collected {collected} objects")
    
    print("✓ Memory cleanup completed")

def get_memory_info():
    """Get current memory usage"""
    try:
        import subprocess
        pid = os.getpid()
        result = subprocess.run(['ps', '-o', 'rss=', '-p', str(pid)], capture_output=True, text=True)
        if result.returncode == 0:
            rss_kb = int(result.stdout.strip())
            return rss_kb / 1024.0  # Convert to MB
    except:
        pass
    return 0.0

def main():
    """Main cleanup function"""
    print("🚀 NusterDB Test Cleanup")
    print("=" * 40)
    
    # Show initial memory
    initial_memory = get_memory_info()
    print(f"Initial memory usage: {initial_memory:.1f} MB")
    
    # Cleanup databases
    cleanup_databases()
    
    # Cleanup log files
    cleanup_log_files()
    
    # Cleanup memory
    cleanup_memory()
    
    # Show final memory
    final_memory = get_memory_info()
    memory_freed = initial_memory - final_memory
    
    print(f"\n📊 Cleanup Summary:")
    print(f"  Initial memory: {initial_memory:.1f} MB")
    print(f"  Final memory: {final_memory:.1f} MB")
    if memory_freed > 0:
        print(f"  Memory freed: {memory_freed:.1f} MB")
    else:
        print(f"  Memory change: {abs(memory_freed):.1f} MB")
    
    print("\n✅ Cleanup completed successfully!")

if __name__ == "__main__":
    main()
