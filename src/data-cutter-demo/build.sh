#!/bin/bash
# build.sh - Launch the data-cutter-demo frontend

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  Data-Cutter Demo Setup"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Install parent package in editable mode
echo "Installing data-cutter package..."
cd ../..
pip install -q -e .
cd "$SCRIPT_DIR"

echo ""
echo "========================================"
echo "  Starting Server"
echo "========================================"
echo ""

# Launch server
python server.py
