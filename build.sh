#!/bin/bash

# Build script for data-cutter package

set -e

echo "Building data-cutter package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

echo "Build complete! Distribution files are in the dist/ directory."
