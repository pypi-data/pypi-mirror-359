#!/usr/bin/env bash

# Pure Rust Performance Benchmark
# This will test the actual Rust implementation performance without Python overhead

echo "Building NusterDB with optimizations..."
cd /Users/shashidharnaidu/nuster_ai/nusterdb
cargo build --release

echo "Running Rust benchmarks..."
cd /Users/shashidharnaidu/nuster_ai/nusterdb
cargo run --release --bin cli -- benchmark
