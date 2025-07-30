#!/bin/bash
set -e

NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
    echo "Usage: $0 <new_version>"
    echo "Example: $0 0.3.0"
    exit 1
fi

echo "🔄 Updating version to $NEW_VERSION"

# Backup original files
cp Cargo.toml Cargo.toml.bak
cp pyproject.toml pyproject.toml.bak
cp src/lib.rs src/lib.rs.bak

# Update Cargo.toml
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/version = \".*\"/version = \"$NEW_VERSION\"/" Cargo.toml
else
    # Linux
    sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" Cargo.toml
fi

# Update pyproject.toml
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
else
    # Linux
    sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
fi

# Update lib.rs
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/__version__\", \".*\"/__version__\", \"$NEW_VERSION\"/" src/lib.rs
else
    # Linux
    sed -i "s/__version__\", \".*\"/__version__\", \"$NEW_VERSION\"/" src/lib.rs
fi

# Verify changes
echo "📋 Changes made:"
echo "Cargo.toml:"
grep "version =" Cargo.toml | head -1
echo "pyproject.toml:"
grep "version =" pyproject.toml | head -1
echo "lib.rs:"
grep "__version__" src/lib.rs

# Cleanup backup files
rm -f Cargo.toml.bak pyproject.toml.bak src/lib.rs.bak

echo "✅ Version updated to $NEW_VERSION"
echo ""
echo "📝 Next steps:"
echo "  1. Review the changes"
echo "  2. Test the build: ./scripts/build.sh"
echo "  3. Commit changes: git add . && git commit -m \"Bump version to $NEW_VERSION\""
echo "  4. Create release: ./scripts/release.sh $NEW_VERSION"
