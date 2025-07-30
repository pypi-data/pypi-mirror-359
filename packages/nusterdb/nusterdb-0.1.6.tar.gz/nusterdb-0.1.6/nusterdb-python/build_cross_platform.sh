#!/bin/bash

# Cross-platform build script for NusterDB Python package
# This script builds wheels for multiple platforms using GitHub Actions or local cross-compilation

set -e

echo "🚀 Building NusterDB Python package for multiple platforms..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
make clean || true
rm -rf target/wheels/
rm -rf dist/

# Check if we're running in CI
if [ "$CI" = "true" ]; then
    echo "🔧 Running in CI environment"
    # Build for current platform
    PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 maturin build --release
else
    echo "🔧 Running in local environment - building cross-platform wheels"
    
    # Install cross-compilation targets if not present
    echo "📦 Installing cross-compilation targets..."
    
    # For Linux targets (if on macOS/Windows)
    if command -v rustup &> /dev/null; then
        rustup target add x86_64-unknown-linux-gnu || true
        rustup target add aarch64-unknown-linux-gnu || true
        rustup target add x86_64-pc-windows-gnu || true
        rustup target add aarch64-apple-darwin || true
        rustup target add x86_64-apple-darwin || true
    fi
    
    # Build for current platform first
    echo "🔨 Building for current platform..."
    PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 maturin build --release
    
    # Try to build for other platforms if tools are available
    echo "🔨 Attempting cross-platform builds..."
    
    # macOS builds (if on macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 Building for macOS platforms..."
        maturin build --release --target x86_64-apple-darwin || echo "⚠️ x86_64-apple-darwin build failed"
        maturin build --release --target aarch64-apple-darwin || echo "⚠️ aarch64-apple-darwin build failed"
    fi
    
    # Note: Cross-compilation for Linux and Windows from macOS requires additional setup
    echo "ℹ️ For complete cross-platform builds, use GitHub Actions or Docker"
fi

# Create dist directory and copy wheels
mkdir -p dist
cp target/wheels/*.whl dist/ 2>/dev/null || echo "⚠️ No wheels found in target/wheels/"

# Validate all wheels
echo "✅ Validating wheels..."
if command -v twine &> /dev/null; then
    python -m twine check dist/*.whl || echo "⚠️ Wheel validation failed"
else
    echo "ℹ️ Install twine for wheel validation: pip install twine"
fi

# Test install one wheel locally
if ls dist/*.whl 1> /dev/null 2>&1; then
    echo "🧪 Testing local installation..."
    WHEEL_FILE=$(ls dist/*.whl | head -n 1)
    pip install "$WHEEL_FILE" --force-reinstall
    
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
fi

echo "📦 Cross-platform build completed!"
echo "   Wheels location: dist/"
echo ""
echo "🌍 Available platforms:"
ls -la dist/*.whl 2>/dev/null || echo "No wheels found"
echo ""
echo "📝 Next steps:"
echo "   1. For complete cross-platform support, push to GitHub and create a release tag"
echo "   2. To upload to TestPyPI: python -m twine upload --repository testpypi dist/*.whl"
echo "   3. To upload to PyPI: python -m twine upload dist/*.whl"
echo ""
echo "🎯 For all platforms, use: git tag v0.1.3 && git push origin v0.1.3"
