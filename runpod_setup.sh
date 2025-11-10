#!/bin/bash
# RunPod Setup Script for Phonics Book Generator
# This script sets up the environment on a RunPod instance
#
# This is a lightweight wrapper that handles repository cloning
# and then delegates to the Python setup script (setup_runpod.py)
# for all interactive setup logic.

set -e  # Exit on error

echo "=================================================="
echo "Phonics Book Generator - RunPod Setup"
echo "=================================================="
echo ""

# Create project directory
PROJECT_DIR="/workspace/phonics"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating project directory: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Clone or update the repository (quiet)
if [ ! -d ".git" ]; then
    echo "Cloning repository..."
    git clone --quiet https://github.com/normrubin/phonics.git .
else
    git pull --quiet --no-rebase --ff-only || git pull --quiet --rebase
fi

# Run the Python setup script which handles all the interactive setup
echo ""
echo "Running Python setup script..."
echo ""
pip install huggingface_hub -q --disable-pip-version-check --no-input \
    --progress-bar off
python3 setup_runpod.py
