# NusterDB Release Process Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Development Workflow](#development-workflow)
4. [Version Management](#version-management)
5. [Testing Process](#testing-process)
6. [Build Process](#build-process)
7. [Release Preparation](#release-preparation)
8. [Publication Process](#publication-process)
9. [Post-Release Activities](#post-release-activities)
10. [Troubleshooting](#troubleshooting)
11. [Automation Scripts](#automation-scripts)

## Overview

This guide provides comprehensive steps for releasing new versions of NusterDB Python bindings, from development to publication. The process ensures quality, consistency, and proper distribution of the package.

## Prerequisites

### Development Environment
```bash
# Required tools
brew install rust python3
pip install maturin twine build
cargo install cargo-edit

# Optional but recommended
pip install black isort mypy pytest pytest-benchmark
```

### Account Setup
- **PyPI Account**: Register at https://pypi.org
- **Test PyPI Account**: Register at https://test.pypi.org
- **GitHub Access**: Repository access with push permissions

### Configuration Files

#### `.pypirc` (in home directory)
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## Development Workflow

### 1. Feature Development

#### Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

#### Make Changes
- Implement features in `src/lib.rs`
- Update Python API in `python/nusterdb/__init__.py`
- Add tests to `test_advanced.py`
- Update examples in `examples_advanced.py`

#### Local Testing
```bash
# Build and install locally
maturin develop

# Run tests
python test_advanced.py

# Run examples
python examples_advanced.py
```

### 2. Code Quality Checks

#### Format Code
```bash
# Format Python code
black python/ *.py

# Sort imports
isort python/ *.py

# Format Rust code
cargo fmt
```

#### Linting
```bash
# Check Python code
mypy python/nusterdb/

# Check Rust code
cargo clippy -- -D warnings
```

### 3. Documentation Updates

#### Update Documentation
- Update `README.md` with new features
- Update `TECHNICAL_DOCS.md` if architecture changes
- Update docstrings in Python code
- Update Rust documentation comments

#### Generate Documentation
```bash
# Generate Rust docs
cargo doc --no-deps

# Verify Python imports work
python -c "import nusterdb; help(nusterdb)"
```

## Version Management

### Semantic Versioning
Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Files to Update

#### 1. `Cargo.toml`
```toml
[package]
name = "nusterdb-python"
version = "0.3.0"  # ← Update here
```

#### 2. `pyproject.toml`
```toml
[project]
name = "nusterdb"
version = "0.3.0"  # ← Update here
```

#### 3. `src/lib.rs`
```rust
m.add("__version__", "0.3.0")?;  // ← Update here
```

### Automated Version Updates
```bash
# Update all version references
./scripts/update_version.sh 0.3.0
```

## Testing Process

### 1. Local Testing

#### Basic Functionality
```bash
# Clean build
cargo clean
maturin develop --release

# Run comprehensive tests
python test_advanced.py

# Run examples
python examples_advanced.py

# Performance tests
python -m pytest test_performance.py --benchmark-only
```

#### Memory Testing
```bash
# Memory leak detection (if valgrind available)
valgrind --tool=memcheck python test_advanced.py

# Memory usage profiling
python -m memory_profiler examples_advanced.py
```

### 2. Cross-Platform Testing

#### Docker Testing
```bash
# Test on different Python versions
docker run -v $(pwd):/work python:3.8 /bin/bash -c "cd /work && pip install maturin && maturin develop && python test_advanced.py"
docker run -v $(pwd):/work python:3.9 /bin/bash -c "cd /work && pip install maturin && maturin develop && python test_advanced.py"
docker run -v $(pwd):/work python:3.10 /bin/bash -c "cd /work && pip install maturin && maturin develop && python test_advanced.py"
docker run -v $(pwd):/work python:3.11 /bin/bash -c "cd /work && pip install maturin && maturin develop && python test_advanced.py"
docker run -v $(pwd):/work python:3.12 /bin/bash -c "cd /work && pip install maturin && maturin develop && python test_advanced.py"
```

### 3. Integration Testing

#### Test Installation from Wheel
```bash
# Build wheel
maturin build --release

# Test installation
pip install target/wheels/nusterdb-*.whl

# Test import
python -c "import nusterdb; print(nusterdb.__version__)"
```

## Build Process

### 1. Local Build

#### Development Build
```bash
maturin develop
```

#### Release Build
```bash
maturin build --release
```

#### Build for Multiple Targets
```bash
# Build for current platform
maturin build --release

# Build universal wheel (if supported)
maturin build --release --universal
```

### 2. Automated Builds

#### GitHub Actions (`.github/workflows/build.yml`)
```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install maturin
    
    - name: Build and test
      run: |
        maturin develop
        python test_advanced.py
```

### 3. Build Verification

#### Check Wheel Contents
```bash
# Extract and inspect wheel
unzip -l target/wheels/nusterdb-*.whl

# Verify wheel metadata
python -m pip show nusterdb
```

## Release Preparation

### 1. Pre-Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] CHANGELOG.md updated
- [ ] No debug code or TODO comments
- [ ] Performance benchmarks acceptable
- [ ] Memory usage acceptable

### 2. Create Release Branch
```bash
git checkout -b release/v0.3.0
git push origin release/v0.3.0
```

### 3. Update Changelog

#### `CHANGELOG.md`
```markdown
# Changelog

## [0.3.0] - 2025-06-19

### Added
- New distance metric: Hamming distance
- Batch operations for improved performance
- Advanced metadata filtering

### Changed
- Improved HNSW performance by 15%
- Updated dependencies

### Fixed
- Memory leak in large dataset operations
- Thread safety issues in concurrent access

### Deprecated
- Old configuration format (will be removed in v1.0.0)
```

### 4. Final Testing
```bash
# Clean environment test
python -m venv test_env
source test_env/bin/activate
pip install target/wheels/nusterdb-*.whl
python test_advanced.py
deactivate
rm -rf test_env
```

## Publication Process

### 1. Test PyPI Release

#### Build and Upload to Test PyPI
```bash
# Clean build
cargo clean
maturin build --release

# Upload to Test PyPI
maturin upload --repository testpypi
```

#### Test Installation from Test PyPI
```bash
# Create clean environment
python -m venv test_pypi_env
source test_pypi_env/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ nusterdb

# Test functionality
python test_advanced.py

# Cleanup
deactivate
rm -rf test_pypi_env
```

### 2. Production PyPI Release

#### Upload to PyPI
```bash
# Upload to production PyPI
maturin upload
```

#### Verify Release
```bash
# Check package page
open https://pypi.org/project/nusterdb/

# Test installation
pip install --upgrade nusterdb
python -c "import nusterdb; print(nusterdb.__version__)"
```

### 3. GitHub Release

#### Create Git Tag
```bash
git tag -a v0.3.0 -m "Release version 0.3.0"
git push origin v0.3.0
```

#### Create GitHub Release
1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag: `v0.3.0`
4. Title: `NusterDB v0.3.0`
5. Description: Copy from CHANGELOG.md
6. Attach wheel files
7. Publish release

## Post-Release Activities

### 1. Update Documentation

#### Update README Badges
```markdown
[![PyPI version](https://badge.fury.io/py/nusterdb.svg)](https://badge.fury.io/py/nusterdb)
[![Downloads](https://pepy.tech/badge/nusterdb)](https://pepy.tech/project/nusterdb)
```

#### Documentation Sites
- Update project website
- Update API documentation
- Update tutorial examples

### 2. Notifications

#### Community Updates
- Update project Discord/Slack
- Post on relevant forums/communities
- Update social media

#### Internal Communications
- Notify team members
- Update project roadmap
- Schedule retrospective meeting

### 3. Monitoring

#### Track Metrics
- Download statistics
- PyPI package health
- User feedback/issues

#### Performance Monitoring
```bash
# Set up monitoring alerts
# Monitor memory usage trends
# Track performance regressions
```

## Troubleshooting

### Common Build Issues

#### Rust Compilation Errors
```bash
# Update Rust toolchain
rustup update

# Clean and rebuild
cargo clean
maturin develop
```

#### PyO3 Version Conflicts
```bash
# Check PyO3 version compatibility
pip list | grep pyo3

# Update PyO3
cargo update -p pyo3
```

#### Missing Dependencies
```bash
# Install system dependencies (Ubuntu)
sudo apt-get install build-essential libssl-dev pkg-config

# Install system dependencies (macOS)
brew install openssl pkg-config
```

### Upload Issues

#### Authentication Errors
```bash
# Regenerate PyPI tokens
# Update .pypirc file
# Test with: twine check dist/*
```

#### Wheel Format Issues
```bash
# Check wheel format
python -m wheel unpack target/wheels/nusterdb-*.whl

# Rebuild with specific options
maturin build --release --strip
```

### Version Conflicts

#### Tag Already Exists
```bash
# Delete local and remote tag
git tag -d v0.3.0
git push origin :refs/tags/v0.3.0

# Create new tag
git tag -a v0.3.1 -m "Release version 0.3.1"
git push origin v0.3.1
```

## Automation Scripts

### Version Update Script (`scripts/update_version.sh`)
```bash
#!/bin/bash
set -e

NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
    echo "Usage: $0 <new_version>"
    exit 1
fi

echo "Updating version to $NEW_VERSION"

# Update Cargo.toml
sed -i.bak "s/version = \".*\"/version = \"$NEW_VERSION\"/" Cargo.toml

# Update pyproject.toml
sed -i.bak "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Update lib.rs
sed -i.bak "s/__version__\", \".*\"/__version__\", \"$NEW_VERSION\"/" src/lib.rs

# Cleanup backup files
rm -f Cargo.toml.bak pyproject.toml.bak src/lib.rs.bak

echo "Version updated to $NEW_VERSION"
echo "Please review changes and commit:"
echo "  git add ."
echo "  git commit -m \"Bump version to $NEW_VERSION\""
```

### Build Script (`scripts/build.sh`)
```bash
#!/bin/bash
set -e

echo "Building NusterDB Python package..."

# Clean previous builds
cargo clean
rm -rf target/wheels/*

# Run tests first
echo "Running tests..."
maturin develop
python test_advanced.py

# Build release
echo "Building release..."
maturin build --release

# Verify wheel
echo "Verifying wheel..."
ls -la target/wheels/
python -m pip install target/wheels/nusterdb-*.whl --force-reinstall
python -c "import nusterdb; print(f'Successfully built version {nusterdb.__version__}')"

echo "Build complete!"
```

### Release Script (`scripts/release.sh`)
```bash
#!/bin/bash
set -e

VERSION=$1
UPLOAD_TYPE=${2:-testpypi}

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version> [testpypi|pypi]"
    exit 1
fi

echo "Starting release process for version $VERSION"

# Update version
./scripts/update_version.sh $VERSION

# Build
./scripts/build.sh

# Upload
if [ "$UPLOAD_TYPE" = "pypi" ]; then
    echo "Uploading to PyPI..."
    maturin upload
else
    echo "Uploading to Test PyPI..."
    maturin upload --repository testpypi
fi

# Create git tag
git add .
git commit -m "Release version $VERSION"
git tag -a v$VERSION -m "Release version $VERSION"
git push origin main
git push origin v$VERSION

echo "Release $VERSION complete!"
```

### Test Script (`scripts/test_all.sh`)
```bash
#!/bin/bash
set -e

echo "Running comprehensive test suite..."

# Clean build
maturin develop --release

# Run all tests
echo "Running advanced tests..."
python test_advanced.py

echo "Running examples..."
python examples_advanced.py

echo "Running performance tests..."
python -c "
import time
import nusterdb

# Performance test
start = time.time()
db = nusterdb.NusterDB('./perf_test', dim=128)
for i in range(1000):
    v = nusterdb.Vector.random(128, -1.0, 1.0)
    db.add(i, v)

search_start = time.time()
query = nusterdb.Vector.random(128, -1.0, 1.0)
results = db.search(query, k=10)
search_time = time.time() - search_start

total_time = time.time() - start
print(f'Added 1000 vectors in {total_time:.2f}s')
print(f'Search took {search_time*1000:.2f}ms')

import shutil
shutil.rmtree('./perf_test')
"

echo "All tests passed!"
```

This comprehensive release guide ensures a systematic, quality-focused approach to releasing new versions of NusterDB Python bindings. Following these steps will help maintain consistency, quality, and reliability across all releases.
