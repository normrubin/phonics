# Phonics Book Generator - Instructions

Complete workflow guide for creating personalized phonics books with AI-generated images.

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Setup](#setup)
3. [Workflow Steps](#workflow-steps)
4. [Command Reference](#command-reference)
5. [File Descriptions](#file-descriptions)
6. [Troubleshooting](#troubleshooting)

## Quick Reference

### Core Scripts (Training/Inference Split)

- **Training**: `finetune_flux_train.py` - Fine-tune the model, generate training config
- **Inference**: `flux_infer.py` - Generate images from prompts using trained model
- **Labeling**: `label_images.py` - Auto-generate captions for training images
- **Config**: `config.py` - Manage project configuration and directories

### Essential Commands

```bash
# Setup (RunPod)
./runpod_setup.sh

# Full workflow
./quick_start.sh

# Individual steps
python3 label_images.py                    # Label images
python3 finetune_flux_train.py             # Train model
python3 flux_infer.py prompts.txt          # Generate images
```

## Setup

### Prerequisites

1. **GPU Environment**: RunPod instance with A40/A100 GPU (or local with 24GB+ VRAM)
2. **Hugging Face Account**: Get token from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. **Training Images**: 10-20 photos of the child (1024×1024 JPEG)

### Initial Setup (RunPod)

```bash
cd /workspace
git clone https://github.com/normrubin/phonics.git
cd phonics
chmod +x runpod_setup.sh
./runpod_setup.sh
```

The setup script will:

- Prompt for your Hugging Face token (validated immediately)
- Prompt for your trigger word (unique identifier for your child)
- Install all dependencies
- Create directory structure
- Generate initial training configuration
- Test GPU availability

### Configuration File

Edit `config.json` to customize paths and settings:

```json
{
  "directories": {
    "photo_images": "./photos",
    "output": "./output"
  },
  "image_settings": {
    "target_size": 1024,
    "format": "JPEG",
    "quality": 95
  },
  "model_settings": {
    "base_model": "flux.1-schnell",
    "training_method": "LoRA",
    "trigger_word": "your_child_name_trigger"
  }
}
```

### Environment Variables

Create/edit `ENV` file:

```bash
HF_TOKEN=hf_your_token_here
```

## Workflow Steps

### Step 1: Prepare Training Images

1. Select 10-20 photos of your child

   - Mix of headshots and full-body portraits
   - Various settings, poses, lighting conditions
   - Different angles and expressions
2. Resize all images to 1024×1024 pixels (JPEG format)
3. Upload to `./photos/` directory

   - RunPod: Use JupyterLab file browser or SCP
   - Local: Copy directly to folder

### Step 2: Generate Captions

Automatically caption your images using BLIP:

```bash
python3 label_images.py
```

**What it does:**

- Processes each image with BLIP captioning model
- Generates descriptive captions
- Injects your trigger word from config.json
- Saves as `.txt` files alongside images
- Validates trigger word appears in all captions

**Options:**

```bash
python3 label_images.py --overwrite         # Replace existing captions
python3 label_images.py --max-tokens 50     # Longer captions
python3 label_images.py --device cuda       # Force GPU
```

**Validation:**

The script will exit with an error if any caption is missing the trigger word. Fix by:

1. Checking trigger_word in config.json
2. Re-running with --overwrite
3. Manually editing caption .txt files

### Step 3: Train the Model

Fine-tune FLUX.1-schnell on your images:

```bash
python3 finetune_flux_train.py
```

**What it does:**

- Validates your Hugging Face token
- Generates `flux_training_config.yaml` (if not present)
- Runs ai-toolkit training via ../ai-toolkit/run.py
- Saves checkpoints every 250 steps to `./output/flux_lora/`
- Generates sample images every 250 steps

**Training time:** 2-4 hours on A40 for 800 steps (default)

**Config-only mode:**

```bash
python3 finetune_flux_train.py --generate-config-only
```

Generate the YAML config without starting training. Useful for:

- Reviewing/editing training parameters
- Setup scripts
- Troubleshooting configuration

**Key training parameters** (edit `flux_training_config.yaml`):

```yaml
train:
  steps: 800                    # Total training steps
  batch_size: 1                 # Increase if you have VRAM
  lr: 1e-4                      # Learning rate

network:
  linear: 16                    # LoRA rank (8-32)
  linear_alpha: 32              # LoRA alpha

sample:
  sample_every: 250             # Generate samples every N steps
  sample_steps: 4               # Inference steps for samples
```

**Monitor training:**

- Watch terminal for step progress
- Check `./output/flux_lora/` for sample images
- Run `nvidia-smi` to monitor GPU usage

**Stop training:**

- Press `Ctrl+C` (wait for checkpoint save message)
- Training can resume from last checkpoint

### Step 4: Generate Images

Create images from text prompts using your trained model:

```bash
python3 flux_infer.py prompts.txt
```

**Create prompts file:**

Edit `prompts.txt` with one prompt per line:

```text
your_trigger reading a phonics book in a cozy library
your_trigger holding the letter A on a bright sunny day
your_trigger playing with colorful alphabet blocks
your_trigger writing letters on a whiteboard
```

**What the script does:**

- Auto-loads LoRA weights from `./output/flux_lora/`
- Prefixes prompts with "photo of [trigger_word] " (idempotent)
- Generates 1024×1024 images
- Saves to `./output/generated_images/`

**Advanced options:**

```bash
# Use specific checkpoint
python3 flux_infer.py prompts.txt --lora ./output/flux_lora/checkpoint-1000

# Reproducible generation
python3 flux_infer.py prompts.txt --seed 42

# Higher quality (more steps, slower)
python3 flux_infer.py prompts.txt --steps 8

# Custom output directory
python3 flux_infer.py prompts.txt --output ./my_images

# Different image size
python3 flux_infer.py prompts.txt --width 768 --height 768

# Use specific base model
python3 flux_infer.py prompts.txt --model black-forest-labs/FLUX.1-schnell
```

**Generation time:** ~10-30 seconds per image on A40

## Command Reference

### Training Commands

```bash
# Generate config only
python3 finetune_flux_train.py --generate-config-only

# Train with default settings
python3 finetune_flux_train.py

# Override trigger word
python3 finetune_flux_train.py --trigger-word my_custom_trigger

# Custom config output path
python3 finetune_flux_train.py --config-path my_config.yaml
```

### Inference Commands

```bash
# Basic generation
python3 flux_infer.py prompts.txt

# With options
python3 flux_infer.py prompts.txt \
  --lora ./output/flux_lora/checkpoint-1500 \
  --seed 42 \
  --steps 8 \
  --output ./final_images
```

### Labeling Commands

```bash
# Label all images
python3 label_images.py

# Overwrite existing captions
python3 label_images.py --overwrite

# Custom max tokens
python3 label_images.py --max-tokens 50

# Force specific device
python3 label_images.py --device cuda
```

### Configuration Commands

```bash
# Test configuration and create directories
python3 config.py

# View current settings
cat config.json
```

## File Descriptions

### Scripts

- **finetune_flux_train.py** - Training script; generates YAML config and runs ai-toolkit
- **flux_infer.py** - Inference script; loads model/LoRA and generates images
- **label_images.py** - BLIP-based auto-captioning tool
- **generate_images.py** - (DEPRECATED) Thin shim that forwards to flux_infer.py
- **config.py** - Configuration manager with typed accessors
- **runpod_setup.sh** - Automated RunPod environment setup
- **quick_start.sh** - Complete workflow automation
- **finetune_flux.py** - (DEPRECATED) Forwards to finetune_flux_train.py

### Configuration Files

- **config.json** - Project configuration (paths, settings, trigger word)
- **ENV** - Environment variables (HF_TOKEN)
- **flux_training_config.yaml** - Generated training configuration for ai-toolkit

### Data Files

- **prompts.txt** - Text prompts for image generation (one per line)
- **prompts.txt.example** - Example prompts template
- **photos/** - Training images directory (1024×1024 JPEG + .txt captions)
- **output/flux_lora/** - Trained LoRA checkpoints and sample images
- **output/generated_images/** - Final generated images

### Documentation

- **README.md** - Project overview and setup guide
- **RUNPOD_GUIDE.md** - Detailed RunPod-specific instructions
- **INSTRUCTIONS.md** - This file (workflow and command reference)

## Troubleshooting

### Common Issues

#### "No HF_TOKEN found in ENV file"

- Edit `ENV` file and add: `HF_TOKEN=hf_your_token_here`
- Get token from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Ensure token has "Read access to gated repos"

#### "Trigger word not found in captions"

- Check `trigger_word` in config.json
- Re-run labeling with `--overwrite` flag
- Manually edit .txt caption files if needed

#### Out of memory errors during training

Edit `flux_training_config.yaml`:

```yaml
train:
  batch_size: 1
  gradient_accumulation_steps: 2

model:
  quantize: true
```

#### No LoRA weights found

- Ensure training completed successfully
- Check `./output/flux_lora/` for .safetensors files
- Verify checkpoint directories match the step count

#### Slow image generation

- Reduce steps: `--steps 4` (default for schnell)
- Reduce resolution: `--width 768 --height 768`
- Use GPU: Ensure CUDA is available

#### Training interrupted

- Training resumes automatically from last checkpoint
- Re-run `python3 finetune_flux_train.py`

#### ai-toolkit not found

```bash
cd /workspace
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit
git submodule update --init --recursive
pip install -r requirements.txt
```

### Validation Checks

**Check GPU availability:**

```bash
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

**Check token validity:**

```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv('ENV'); print('Token:', os.getenv('HF_TOKEN')[:10] + '...')"
```

**Count training images:**

```bash
ls photos/*.jpg | wc -l
```

**Verify config:**

```bash
python3 config.py
```

### Performance Tips

1. **Training:**

   - Use A40 or A100 GPUs for fastest training
   - Reduce steps for quicker iteration (400-600 for testing)
   - Monitor sample images to detect when model converges
2. **Generation:**

   - Batch prompts into a single file for efficiency
   - Use fixed seed for consistent results
   - Start with 4 steps (schnell default), increase only if needed
3. **Cost Management (RunPod):**

   - Stop pod immediately after training/generation
   - Use spot instances for 50-70% savings
   - Download results and terminate pod
   - Spin up cheaper GPU for generation only

### Getting Help

1. Review [README.md](README.md) for project overview
2. Check [RUNPOD_GUIDE.md](RUNPOD_GUIDE.md) for platform-specific setup
3. Visit [ai-toolkit issues](https://github.com/ostris/ai-toolkit/issues)
4. Check FLUX.1-schnell documentation at [Hugging Face](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

## Advanced Usage

### Custom Training Configuration

Modify `flux_training_config.yaml` before training for advanced control:

```yaml
config:
  process:
    - type: sd_trainer
      # Adjust network architecture
      network:
        linear: 32              # Higher rank = more capacity
        linear_alpha: 64        # Match or exceed rank

      # Fine-tune learning
      train:
        steps: 2000             # More steps for complex subjects
        lr: 5e-5                # Lower LR for fine-tuning

      # Sample configuration
      sample:
        sample_every: 100       # More frequent samples
        prompts:
          - "your_trigger specific_scenario_1"
          - "your_trigger specific_scenario_2"
```

### Multiple Trigger Words

Train separate models for different subjects or use composite triggers:

```json
{
  "model_settings": {
    "trigger_word": "alice_girl"
  }
}
```

### Batch Generation

Create large prompt files for batch processing:

```bash
# Generate from 100 prompts
python3 flux_infer.py large_prompts.txt --seed 1000
```

### Checkpoint Selection

Use different checkpoints for different styles:

```bash
# Early checkpoint (less overtrained)
python3 flux_infer.py prompts.txt --lora ./output/flux_lora/checkpoint-500

# Final checkpoint
python3 flux_infer.py prompts.txt --lora ./output/flux_lora/checkpoint-1500
```

---

**Last Updated:** November 2025
**Version:** 2.0 (Training/Inference Split)
