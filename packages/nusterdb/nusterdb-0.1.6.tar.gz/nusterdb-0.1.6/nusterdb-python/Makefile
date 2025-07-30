# Makefile for NusterDB Python Package

.PHONY: help dev build test clean install upload-test upload-prod release

# Default target
help:
	@echo "NusterDB Python Package - Available Commands:"
	@echo ""
	@echo "  dev          - Build and install for development"
	@echo "  build        - Build production wheels"
	@echo "  test         - Run test suite"
	@echo "  examples     - Run example scripts"
	@echo "  clean        - Clean build artifacts"
	@echo "  install      - Install from built wheel"
	@echo "  upload-test  - Upload to Test PyPI"
	@echo "  upload-prod  - Upload to Production PyPI"
	@echo "  release      - Complete build and upload pipeline"
	@echo "  fmt          - Format Rust code"
	@echo "  lint         - Run Rust linter"
	@echo ""

# Development build
dev:
	@echo "🔧 Building for development..."
	maturin develop

# Production build
build:
	@echo "🔨 Building production wheels..."
	@./build.sh

# Run tests
test:
	@echo "🧪 Running tests..."
	python test_nusterdb.py

# Run examples
examples:
	@echo "📚 Running examples..."
	python examples.py

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf target/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf python/nusterdb/__pycache__/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*_db" -type d -exec rm -rf {} + 2>/dev/null || true

# Install from built wheel
install: build
	@echo "📦 Installing from wheel..."
	pip install --force-reinstall dist/*.whl

# Upload to Test PyPI
upload-test: build
	@echo "🧪 Uploading to Test PyPI..."
	twine upload --repository testpypi dist/*

# Upload to Production PyPI
upload-prod: build
	@echo "🚀 Uploading to Production PyPI..."
	twine upload dist/*

# Complete release pipeline
release:
	@echo "🎉 Running complete release pipeline..."
	@./release.sh

# Format Rust code
fmt:
	@echo "🎨 Formatting Rust code..."
	cargo fmt

# Run Rust linter
lint:
	@echo "🔍 Running Rust linter..."
	cargo clippy -- -D warnings

# Check dependencies
check-deps:
	@echo "🔍 Checking dependencies..."
	@command -v rustc >/dev/null 2>&1 || { echo "❌ Rust not installed. Please install from https://rustup.rs/"; exit 1; }
	@command -v python >/dev/null 2>&1 || { echo "❌ Python not installed."; exit 1; }
	@python -c "import maturin" 2>/dev/null || { echo "❌ maturin not installed. Run: pip install maturin"; exit 1; }
	@echo "✅ All dependencies are installed"

# Development environment setup
setup: check-deps
	@echo "🛠️ Setting up development environment..."
	pip install --upgrade pip
	pip install maturin twine pytest numpy
	@echo "✅ Development environment ready"

# All-in-one development command
all: clean setup dev test
	@echo "🎉 Development build completed successfully!"
