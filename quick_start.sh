#!/bin/bash
# Quick Start Script for RunPod
# Run this after runpod_setup.sh to execute the complete workflow

set -e
export PIP_NO_WARN_SCRIPT_LOCATION=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PYTHONUNBUFFERED=1

echo "=================================================="
echo "Phonics Book Generator - Quick Start"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "config.json" ]; then
    echo "Error: config.json not found. Are you in the project directory?"
    exit 1
fi

# Check for ENV file
if [ ! -f "ENV" ]; then
    echo "ERROR: ENV file not found."
    echo " - Run runpod_setup.sh to create and validate ENV, or manually create an ENV file with:\n   HF_TOKEN=hf_..."
    echo " - Get a token at: https://huggingface.co/settings/tokens"
    exit 1
fi



# Check for training images
IMAGE_COUNT=$(find photos -maxdepth 1 -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) 2>/dev/null | wc -l)
if [ "$IMAGE_COUNT" -lt 5 ]; then
    echo "⚠️  Warning: Only $IMAGE_COUNT training images found in photos/"
    echo "   Upload at least 10-20 images before training."
    exit 1
fi

echo "Found $IMAGE_COUNT training images in ./photos"
echo ""

# Step 1: Label images
echo "Step 1: Labeling images..."
echo "------------------------"
python label_images.py --overwrite > /dev/null 2>&1 && \
    echo "Images labeled (quiet)." || echo "Image labeling failed."

echo ""
echo "Step 2: Training FLUX model (finetune_flux_train.py)..."
echo "------------------------"
echo "This will take 2-4 hours. Press Ctrl+C to cancel (wait for checkpoint save!)"
read -p "Continue with training? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Training cancelled. You can run it manually with: python finetune_flux_train.py"
    exit 0
fi

python finetune_flux_train.py > /dev/null 2>&1 && \
    echo "Training finished (quiet)." || echo "Training failed."

echo ""
echo "Step 3: Generating sample images (flux_infer.py)..."
echo "------------------------"

# Check for prompts file
if [ ! -f "prompts.txt" ]; then
    if [ -f "prompts.txt.example" ]; then
        cp prompts.txt.example prompts.txt
        echo "Created prompts.txt from example"
        echo "⚠️  Edit prompts.txt to use your actual trigger word"
    echo "   Then run: python flux_infer.py prompts.txt"
        exit 0
    else
        echo "⚠️  No prompts.txt found. Create one with your prompts (one per line)"
        exit 1
    fi
fi

python flux_infer.py prompts.txt > /dev/null 2>&1 && \
    echo "Inference complete (quiet)." || echo "Inference failed."

echo ""
echo "=================================================="
echo "Workflow Complete!"
echo "=================================================="
echo ""
echo "Results:"
echo "  Training model: ./output/flux_lora/"
echo "  Generated images: ./output/generated_images/"
echo ""
echo "Next steps:"
echo "  - Review generated images in ./output/generated_images/"
echo "  - Download your results"
echo "  - Stop your RunPod instance to avoid charges!"
echo ""
