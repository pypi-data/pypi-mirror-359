#!/bin/bash

# Cross-platform release script for NusterDB Python package
# This script creates a new release and triggers cross-platform builds

set -e

VERSION="0.1.3"
PACKAGE_NAME="nusterdb"

echo "🚀 Releasing $PACKAGE_NAME version $VERSION for all platforms..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Run this script from the nusterdb-python directory."
    exit 1
fi

# Check if git is clean
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: Git working directory is not clean. Please commit your changes first."
    exit 1
fi

# Check if we're on the main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️ Warning: You're not on the main branch (current: $CURRENT_BRANCH)"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verify version in files
echo "🔍 Verifying version numbers..."
if ! grep -q "version = \"$VERSION\"" pyproject.toml; then
    echo "❌ Error: Version $VERSION not found in pyproject.toml"
    exit 1
fi

if ! grep -q "version = \"$VERSION\"" Cargo.toml; then
    echo "❌ Error: Version $VERSION not found in Cargo.toml"
    exit 1
fi

echo "✅ Version $VERSION verified in configuration files"

# Run a quick build test locally
echo "🧪 Running quick build test..."
if ! ./build_cross_platform.sh; then
    echo "❌ Error: Local build test failed"
    exit 1
fi

# Create and push git tag
TAG_NAME="v$VERSION"
echo "🏷️ Creating git tag $TAG_NAME..."

if git tag | grep -q "^$TAG_NAME$"; then
    echo "❌ Error: Tag $TAG_NAME already exists"
    exit 1
fi

git tag -a "$TAG_NAME" -m "Release version $VERSION

🌍 Cross-platform release with support for:
- Linux (x86_64, aarch64)
- macOS (Intel, Apple Silicon)  
- Windows (x86_64)

🚀 Features:
- High-performance vector database
- Multiple distance metrics
- Advanced indexing algorithms
- NumPy integration
- Enterprise-grade features

📦 Install with: pip install $PACKAGE_NAME==$VERSION
"

echo "📤 Pushing tag to GitHub..."
git push origin "$TAG_NAME"

echo "⏳ Triggering GitHub Actions build..."
echo "   The CI/CD pipeline will now:"
echo "   1. Run tests on all platforms"
echo "   2. Build wheels for Linux, macOS, and Windows"
echo "   3. Automatically publish to PyPI"
echo ""
echo "🔗 Monitor the build progress at:"
echo "   https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/' | sed 's/\.git$//')/actions"
echo ""
echo "📦 Once complete, the package will be available at:"
echo "   https://pypi.org/project/$PACKAGE_NAME/$VERSION/"
echo ""
echo "🎯 Installation command for all platforms:"
echo "   pip install $PACKAGE_NAME==$VERSION"
echo ""
echo "✅ Release process initiated for version $VERSION!"

# Optional: Wait for build completion
read -p "🕒 Do you want to wait and monitor the build? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Monitoring GitHub Actions (press Ctrl+C to exit)..."
    
    # Check if gh CLI is available
    if command -v gh &> /dev/null; then
        echo "📊 Watching GitHub Actions run..."
        gh run watch
    else
        echo "ℹ️ Install GitHub CLI for automatic monitoring: brew install gh"
        echo "🔗 Manual monitoring: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/' | sed 's/\.git$//')/actions"
    fi
fi
