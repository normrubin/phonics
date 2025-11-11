# RunPod Setup Guide for Phonics Book Generator

This guide walks you through setting up and running the Phonics Book Generator on RunPod.

## Table of Contents

1. [Creating a RunPod Instance](#creating-a-runpod-instance)
2. [Initial Setup](#initial-setup)
3. [Uploading Training Images](#uploading-training-images)
4. [Training the Model](#training-the-model)
5. [Generating Images](#generating-images)
6. [Downloading Results](#downloading-results)
7. [Cost Management](#cost-management)

## Creating a RunPod Instance

### Recommended Configuration

**GPU:** A40 (48GB VRAM) or A100 (40GB/80GB VRAM)

- FLUX.1-schnell training requires at least 32gb unless special flags are used. (I'm going to leave out describing thouse flags)
- A40 is the most cost-effective option for this project

**Storage:** At least 50GB

- Base model: ~20GB
- Training data: 1-2GB
- Output models: 5-10GB
- Generated images: Variable

**Template:** PyTorch or CUDA-enabled template recommended

### Steps to Create Instance

1. Go to [RunPod](https://runpod.io)
2. Click "Deploy" → "GPU Pods"
3. Select your GPU (A40 recommended)
4. Choose "RunPod PyTorch 2.8" or similar template
5. Set storage to at least 50GB
6. Deploy pod

## Initial Setup

### Step 1: Connect to Your Pod

Once your pod is running, click "Connect" and choose: **JupyterLab** (good for interactive work)

### Step 2: Run Setup Script

In the terminal, run:

```bash
# Download and run setup script
cd /workspace
git clone https://github.com/normrubin/phonics.git
cd phonics
./runpod_setup.sh
```

The setup script will **interactively prompt** you for:

1. **Hugging Face Token** - Enter your token (starts with `hf_`)

   - Get one from: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - The token is validated immediately against the Hugging Face API
   - If valid, it's saved to the `ENV` file automatically
2. **Trigger Word** - Enter your unique identifier (e.g., your child's name)

   - This will be automatically added to all image captions during training
   - Saved to `config.json` for you

The script will also:

- Check Python, pip, and PyTorch versions
- Clone the ai-toolkit repository
- Install required Python packages
- Create directory structure
- Generate the FLUX training configuration

**Note:** If you need to update these values later, you can:

- Edit `ENV` file for the token: `nano ENV`
- Edit `config.json` for the trigger word: `nano config.json`

## Uploading Training Images

You need to upload 10-20 high-quality training images (1024×1024 JPEG recommended) to `/workspace/phonics/photos/`.

### Option 1: Using RunPod File Browser

1. Open your pod's JupyterLab interface
2. Navigate to `/workspace/phonics/photos/`
3. Click "Upload" and select your 10-20 training images
4. All images should be 1024×1024 JPEG files

### Option 2: Using SCP/SFTP

If you enabled SSH access:

```bash
scp -P [PORT] -i ~/.ssh/id_ed25519 /path/to/images/*.jpg \
  root@[POD_IP]:/workspace/phonics/photos/
```

### Option 3: Using wget/curl

If your images are hosted online:

```bash
cd /workspace/phonics/photos/
wget https://your-server.com/image1.jpg
wget https://your-server.com/image2.jpg
# ... etc
```

## Training the Model

### Step 1: Navigate to Project Directory

```bash
cd /workspace/phonics
```

### Step 1: Label Images

Generate captions for your training images:

```bash
python3 label_images.py
```

This will:

- Process each image with BLIP captioning model
- Create `.txt` files with captions
- Append your trigger word to each caption

### Step 3: Run Fine-Tuning

Start the training process (training now split from inference):

```bash
python3 finetune_flux_train.py
```

Or just generate the config without starting training:

```bash
python3 finetune_flux_train.py --generate-config-only
```

**Training time:** Approximately 2-4 hours on A40 for 800–2000 steps (default config uses 800; adjust `steps:` in `flux_training_config.yaml`).

**What happens:**

- Creates or overwrites `flux_training_config.yaml`
- Runs ai-toolkit training
- Saves checkpoints every 250 steps to `./output/flux_lora/`
- Generates sample images every 250 steps into that folder

**Monitor progress:**

- Watch the terminal for step updates
- Sample images appear under `output/flux_lora/`
- Check GPU usage: `nvidia-smi`

**To stop training:**

- Press `Ctrl+C` (wait for checkpoint message)
- Later restart from the latest checkpoint automatically

## Generating Images

### Step 1: Create Prompts File

Edit your prompts:

```bash
nano prompts.txt
```

Add one prompt per line (use the trigger word you configured during setup):

```text
your_trigger_word reading a phonics book in a cozy library
your_trigger_word holding the letter A on a bright sunny day
your_trigger_word playing with alphabet blocks
```

Save with `Ctrl+X`, `Y`, `Enter`

### Step 2: Generate Images

Run the inference script (`flux_infer.py`). The older `generate_images.py` is
deprecated and forwards to `flux_infer.py`.

```bash
python3 flux_infer.py prompts.txt
```

`flux_infer.py` now includes the full generation logic (merged from the
former `generate_images.py`).

**Options:**

```bash
# Use specific LoRA checkpoint
python3 flux_infer.py prompts.txt --lora ./output/flux_lora/checkpoint-1000

# Generate with specific seed
python3 flux_infer.py prompts.txt --seed 42

# Higher quality (more steps)
python3 flux_infer.py prompts.txt --steps 8

# Custom output directory
python3 flux_infer.py prompts.txt --output ./my_book_images
```

**Generation time:** ~10-30 seconds per image on A40

## Downloading Results

### Option 1: JupyterLab Interface

1. Navigate to `/workspace/phonics/output/generated_images/`
2. Right-click files → Download
3. Or select multiple files → Download as Archive

## Cost Management

### Estimated Costs (RunPod A40)

- **Training:** 2-4 hours @ ~$0.79/hr = $1.60-$3.20
- **Generation:** 20 images @ 20 sec each = ~$0.10
- **Total project:** ~$2-5 (one-time training + generation)

### Cost Saving Tips

1. **Stop pod when not in use**

   - Training completed? Stop the pod immediately
   - Only pay for active time
2. **Use spot instances**

   - 50-70% cheaper than on-demand
   - Risk of interruption (save checkpoints frequently!)
3. **Download and terminate**

   - Download your LoRA model
   - Terminate pod
   - Spin up new pod only for generation
4. **Batch your work**

   - Prepare all prompts beforehand
   - Generate all images in one session
   - Download everything and stop
5. **Use cheaper GPUs for generation**

   - Training: A40/A100 required
   - Generation: Can use RTX 4090 or even RTX 3090

## Troubleshooting

### Out of Memory Errors

Edit `flux_training_config.yaml` before training:

```yaml
model:
  low_vram: true
  quantize: true
```

Reduce batch size:

```yaml
train:
  batch_size: 1
  gradient_accumulation_steps: 2
```

### Training Interrupted

Resume from last checkpoint - ai-toolkit does this automatically when you restart.

### CUDA Errors

Check GPU availability:

```bash
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Slow Generation

Reduce image size or steps:

```bash
python3 flux_infer.py prompts.txt --width 768 --height 768 --steps 4
```

## Advanced: Automated Workflow

The `quick_start.sh` script automates the complete workflow:

```bash
cd /workspace/phonics
chmod +x quick_start.sh
./quick_start.sh
```

**Prerequisites:**

- `ENV` file must exist with valid `HF_TOKEN` (created during setup)
- At least 5 training images in `./photos/` directory

This will automatically run:

1. Token validation
2. Image labeling
3. Model training (with confirmation prompt, uses `finetune_flux_train.py` internally)
4. Image generation (if `prompts.txt` exists, via `flux_infer.py`)

## Support

If you encounter issues:

1. Check the main [README.md](README.md) for general documentation
2. Review [ai-toolkit issues](https://github.com/ostris/ai-toolkit/issues)
3. Join the ai-toolkit Discord for support

## Cleanup

When completely done:

```bash
# Optional: Save LoRA model to your local machine first!
# Then delete workspace to free storage
rm -rf /workspace/phonics
rm -rf /workspace/ai-toolkit
```

**Important:** Stop or terminate your pod to avoid ongoing charges!
