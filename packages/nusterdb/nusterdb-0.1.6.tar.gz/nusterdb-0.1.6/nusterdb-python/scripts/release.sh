#!/bin/bash
set -e

VERSION=$1
UPLOAD_TYPE=${2:-testpypi}

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version> [testpypi|pypi]"
    echo "Example: $0 0.3.0 testpypi"
    echo "Example: $0 0.3.0 pypi"
    exit 1
fi

echo "🚀 Starting release process for version $VERSION"

# Validate version format (basic check)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format. Use semantic versioning (e.g., 1.0.0)"
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "⚠️  Warning: You're not on the main branch (current: $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ You have uncommitted changes. Please commit or stash them first."
    git status --porcelain
    exit 1
fi

# Update version numbers
echo "📝 Updating version numbers..."
./scripts/update_version.sh $VERSION

# Build the package
echo "🏗️  Building package..."
./scripts/build.sh

# Ask for confirmation before uploading
echo ""
echo "📋 Release Summary:"
echo "  Version: $VERSION"
echo "  Upload to: $UPLOAD_TYPE"
echo "  Branch: $CURRENT_BRANCH"
echo "  Wheel files:"
ls -la target/wheels/

echo ""
read -p "Proceed with upload? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled"
    exit 1
fi

# Upload to registry
if [ "$UPLOAD_TYPE" = "pypi" ]; then
    echo "📤 Uploading to PyPI..."
    maturin upload
    REGISTRY_URL="https://pypi.org/project/nusterdb/"
else
    echo "📤 Uploading to Test PyPI..."
    maturin upload --repository testpypi
    REGISTRY_URL="https://test.pypi.org/project/nusterdb/"
fi

# Commit version changes
echo "💾 Committing version changes..."
git add Cargo.toml pyproject.toml src/lib.rs
git commit -m "Release version $VERSION"

# Create and push git tag
echo "🏷️  Creating git tag..."
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin main
git push origin "v$VERSION"

# Test installation from registry
echo "🧪 Testing installation from registry..."
if [ "$UPLOAD_TYPE" = "pypi" ]; then
    pip install --upgrade nusterdb
else
    pip install --index-url https://test.pypi.org/simple/ nusterdb --upgrade
fi

# Verify installation
python -c "
import nusterdb
print(f'✅ Successfully installed version {nusterdb.__version__} from registry')
"

echo ""
echo "🎉 Release $VERSION completed successfully!"
echo ""
echo "📋 What was done:"
echo "  ✅ Version updated in all files"
echo "  ✅ Package built and tested"
echo "  ✅ Uploaded to $UPLOAD_TYPE"
echo "  ✅ Git tagged and pushed"
echo "  ✅ Installation verified"
echo ""
echo "🔗 Links:"
echo "  📦 Package: $REGISTRY_URL"
echo "  🏷️  Tag: https://github.com/your-org/nusterdb-python/releases/tag/v$VERSION"
echo ""
echo "📝 Next steps:"
if [ "$UPLOAD_TYPE" = "testpypi" ]; then
    echo "  1. Test the package from Test PyPI"
    echo "  2. If everything works, run: ./scripts/release.sh $VERSION pypi"
else
    echo "  1. Create GitHub release at: https://github.com/your-org/nusterdb-python/releases"
    echo "  2. Update documentation and announcements"
    echo "  3. Monitor package downloads and user feedback"
fi
