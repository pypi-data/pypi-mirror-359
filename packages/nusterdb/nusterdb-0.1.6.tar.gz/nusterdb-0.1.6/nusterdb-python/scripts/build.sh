#!/bin/bash
set -e

echo "🏗️  Building NusterDB Python package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
cargo clean
rm -rf target/wheels/*

# Check if maturin is installed
if ! command -v maturin &> /dev/null; then
    echo "❌ maturin is not installed. Installing..."
    pip install maturin
fi

# Build development version first for testing
echo "🔨 Building development version for testing..."
maturin develop

# Run tests to ensure everything works
echo "🧪 Running tests..."
if [ -f "test_advanced.py" ]; then
    python test_advanced.py
    echo "✅ Tests passed!"
else
    echo "⚠️  test_advanced.py not found, skipping tests"
fi

# Run examples to verify functionality
echo "📋 Running examples..."
if [ -f "examples_advanced.py" ]; then
    python examples_advanced.py > /dev/null
    echo "✅ Examples ran successfully!"
else
    echo "⚠️  examples_advanced.py not found, skipping examples"
fi

# Build release version
echo "🚀 Building release version..."
maturin build --release

# Verify wheel was created
WHEEL_COUNT=$(ls target/wheels/*.whl 2>/dev/null | wc -l)
if [ "$WHEEL_COUNT" -eq 0 ]; then
    echo "❌ No wheel files found in target/wheels/"
    exit 1
fi

# Display wheel information
echo "📦 Built wheels:"
ls -la target/wheels/

# Test installation of the wheel
echo "🔍 Testing wheel installation..."
WHEEL_FILE=$(ls target/wheels/*.whl | head -1)
pip install "$WHEEL_FILE" --force-reinstall --quiet

# Verify installation
echo "✅ Verifying installation..."
python -c "
import nusterdb
print(f'✅ Successfully built and installed NusterDB version {nusterdb.__version__}')

# Quick functionality test
v1 = nusterdb.Vector([1.0, 2.0, 3.0])
v2 = nusterdb.Vector([4.0, 5.0, 6.0])
dist = v1.euclidean_distance(v2)
print(f'✅ Basic functionality test passed (distance: {dist:.3f})')
"

echo ""
echo "🎉 Build completed successfully!"
echo "📁 Wheel location: $WHEEL_FILE"
echo ""
echo "📝 Next steps:"
echo "  - Upload to Test PyPI: maturin upload --repository testpypi"
echo "  - Upload to PyPI: maturin upload"
echo "  - Create GitHub release with this wheel file"
