#!/bin/bash

# Docker-based cross-platform build script
# This builds Linux wheels using manylinux containers

set -e

echo "🐳 Building Linux wheels using Docker..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not running"
    exit 1
fi

# Clean previous builds
rm -rf target/wheels/linux/
mkdir -p target/wheels/linux/

# Build x86_64 Linux wheels
echo "🔨 Building x86_64 Linux wheels..."
docker build -f Dockerfile.manylinux -t nusterdb-linux-builder .
docker run --rm -v "$(pwd)/target/wheels/linux:/output" nusterdb-linux-builder sh -c "cp /output/*.whl /output/ 2>/dev/null || echo 'No wheels to copy'"

# Build aarch64 Linux wheels (if buildx is available)
if docker buildx version &> /dev/null; then
    echo "🔨 Building aarch64 Linux wheels..."
    docker buildx build --platform linux/arm64 -f Dockerfile.manylinux -t nusterdb-linux-arm64-builder .
    docker run --rm --platform linux/arm64 -v "$(pwd)/target/wheels/linux:/output" nusterdb-linux-arm64-builder sh -c "cp /output/*.whl /output/ 2>/dev/null || echo 'No ARM wheels to copy'"
fi

echo "✅ Docker build completed!"
echo "📦 Linux wheels available in: target/wheels/linux/"
ls -la target/wheels/linux/ || echo "No wheels found"
