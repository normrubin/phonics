#!/bin/bash
# Training Monitor for RunPod
# Displays training progress and GPU usage

echo "=================================================="
echo "FLUX Training Monitor"
echo "=================================================="
echo ""

# Check if training is running
if ! pgrep -f "finetune_flux.py\|run.py" > /dev/null; then
    echo "⚠️  No training process detected"
    echo ""
    echo "To start training: python finetune_flux.py"
    exit 0
fi

echo "✓ Training process is running"
echo ""

# Function to get latest checkpoint
get_latest_checkpoint() {
    LORA_DIR="/workspace/phonics/output/flux_lora"
    if [ -d "$LORA_DIR" ]; then
        LATEST=$(ls -t "$LORA_DIR"/*/samples_*.png 2>/dev/null | head -1)
        if [ -n "$LATEST" ]; then
            echo "$LATEST"
        fi
    fi
}

# Function to count samples
count_samples() {
    LORA_DIR="/workspace/phonics/output/flux_lora"
    if [ -d "$LORA_DIR" ]; then
        find "$LORA_DIR" -name "samples_*.png" 2>/dev/null | wc -l
    else
        echo "0"
    fi
}

# Display GPU status
echo "GPU Status:"
echo "----------"
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits | \
    awk -F, '{printf "GPU %s: %s\n  Usage: %s%% | Memory: %s/%s MB | Temp: %s°C\n", $1, $2, $3, $4, $5, $6}'
echo ""

# Display training progress
echo "Training Progress:"
echo "-----------------"
SAMPLE_COUNT=$(count_samples)
echo "Sample batches generated: $SAMPLE_COUNT"

if [ "$SAMPLE_COUNT" -gt 0 ]; then
    # Estimate progress (250 steps per sample batch, 2000 total steps)
    ESTIMATED_STEPS=$((SAMPLE_COUNT * 250))
    PROGRESS=$((ESTIMATED_STEPS * 100 / 2000))
    echo "Estimated progress: ~${PROGRESS}% (${ESTIMATED_STEPS}/2000 steps)"

    # Show latest sample
    LATEST_SAMPLE=$(get_latest_checkpoint)
    if [ -n "$LATEST_SAMPLE" ]; then
        echo "Latest sample: $(basename "$LATEST_SAMPLE")"
    fi
fi

echo ""

# Display output directory size
OUTPUT_SIZE=$(du -sh /workspace/phonics/output 2>/dev/null | cut -f1)
echo "Output directory size: ${OUTPUT_SIZE:-0}"

echo ""
echo "Monitoring commands:"
echo "  watch -n 5 ./monitor_training.sh  # Auto-refresh every 5 seconds"
echo "  tail -f <logfile>                 # Follow training logs (if logging to file)"
echo "  nvidia-smi -l 5                   # Monitor GPU every 5 seconds"
echo ""
