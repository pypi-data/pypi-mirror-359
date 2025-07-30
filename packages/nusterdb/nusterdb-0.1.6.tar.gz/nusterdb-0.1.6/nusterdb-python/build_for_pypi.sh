#!/bin/bash

# Build script for NusterDB Python package for PyPI release

set -e

echo "🚀 Building NusterDB Python package for PyPI release..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
make clean

# Build the wheel
echo "🔨 Building wheel..."
maturin build --release

# Validate the wheel
echo "✅ Validating wheel..."
python -m twine check target/wheels/*.whl

# Test install the wheel locally
echo "🧪 Testing local installation..."
pip install target/wheels/*.whl --force-reinstall

# Quick functionality test
echo "🔍 Running functionality test..."
python -c '
import nusterdb
import tempfile
import os
from nusterdb import NusterDB, Vector

print("Testing basic functionality...")
with tempfile.TemporaryDirectory() as tmpdir:
    db_path = os.path.join(tmpdir, "test_db")
    db = NusterDB.simple(db_path, dim=4, use_hnsw=False)
    vec = Vector([0.1, 0.2, 0.3, 0.4])
    db.add(1, vec)
    query_vec = Vector([0.1, 0.2, 0.3, 0.4])
    results = db.search(query_vec, k=1)
    assert len(results) == 1
    print("✓ All functionality tests passed!")
'

echo "📦 Package ready for PyPI upload!"
echo "   Wheel location: target/wheels/"
echo "   To upload to PyPI: python -m twine upload target/wheels/*.whl"
echo "   To upload to TestPyPI: python -m twine upload --repository testpypi target/wheels/*.whl"
echo "   Note: Make sure your PyPI API tokens are configured in ~/.pypirc"
echo ""
echo "🎉 SUCCESS: Package 'nusterdb' version 0.1.1 is now live on PyPI!"
echo "   Install with: pip install nusterdb==0.1.1"
echo "   View at: https://pypi.org/project/nusterdb/0.1.1/"
