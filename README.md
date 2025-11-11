# Phonics Book Generator

Create personalized phonics books using child-specific imagery (e.g., a book that features the child's name, photos, or likeness).

## Overview

This project generates personalized phonics books by combining AI-powered image generation with educational content. The system creates recognizable images of the child and integrates them into professionally formatted phonics learning books.

**Note:** This is a fun educational project, though evidence is limited regarding whether personalized books directly improve reading speed or phonics mastery.

### Research Background

**Current Evidence:**

- Research shows personalized books increase engagement and motivation in young readers ([Kucirkova, 2021](https://www.scientificamerican.com/article/the-educational-power-mdash-and-the-limits-mdash-of-personalized-children-rsquo-s-books/))
- Aesthetic and interactive features influence reading time and engagement for children aged 5-6 ([Frontiers Psychology](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.02155/full))
- Decodable books aligned with phonics instruction are effective for practicing decoding skills

**Important Limitations:**

- Most research focuses on **vocabulary acquisition** and engagement, not specifically phonics decoding skills
- Minimal personalization (name-only) may not improve comprehension or behavior
- Limited evidence that personalized images directly improve phoneme-grapheme mapping or reading fluency
- Adult involvement and interaction quality significantly impact outcomes ([National Literacy Trust](https://cdn.literacytrust.org.uk/media/documents/2017-11-21_Personalised_books_and_family_literacy_outcomes_-_National_Literacy_Trust.pdf))

**Hypothesis:** If personalized imagery increases engagement, and higher engagement leads to more practice time, then personalized books *may* support phonics improvements through increased repetition and practice.

**Commercial Examples:** Several companies sell personalized phonics books, though they typically request a set of photos (one for each page in the book) rather than training a custom model.

- [We Can Books](https://www.wecanbooks.com/) - Personalized books for ages 4-6 aligned to science of reading
- [ROYO](https://www.royo.ai/) - Personalized decodable books tailored to phonics instruction

## Prerequisites

1. **RunPod Account**: Sign up at [RunPod.io](https://runpod.io) for GPU access
   - Recommended GPU: A40 (48GB VRAM) at ~$0.40/hour
   - Add credits to your account (minimum $10 recommended)
   - Storage: At least 50GB (base model ~20GB, training data 1-2GB, output 5-10GB)
2. **Hugging Face Account**: Create account at [HuggingFace.co](https://huggingface.co)
   - Get a READ token from [HuggingFace tokens page](https://huggingface.co/settings/tokens)
   - Accept FLUX.1-schnell license (optional, Apache 2.0)
3. **Training Photos**: 10-20 photos of the child from different angles
   - Mix of headshots and full-body portraits
   - Various settings, poses, and lighting conditions
   - Should be size 1024×1024 pixels in JPEG format

# RunPod Setup Guide

## Creating a RunPod Instance

### Recommended Configuration

**GPU:** A40 (48GB VRAM) or A100 (40GB/80GB VRAM)

### Steps to Create Instance

1. Go to [RunPod](https://runpod.io)
2. Click "Deploy" → "GPU Pods"
3. Select your GPU (A40 recommended)
4. Choose "RunPod PyTorch 2.8" or similar CUDA template
5. Deploy pod

## Initial Setup

### Step 1: Connect to Your Pod

Once your pod is running, click "Connect" and choose: **JupyterLab** (good for interactive work). Then in the lab open a terminal

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
2. **Trigger Word** - Enter your unique identifier

   - Should be a combination of letters and underscores that is not a word the model has already seen
   - This will be automatically added to all image captions during training
   - Saved to `config.json` for you

The script will also:

- Check Python, pip, and PyTorch versions
- Clone the ai-toolkit repository
- Install required Python packages
- Create directory structure

**Note:** If you need to update these values later, you can:

- Edit `ENV` file for the token.
- Edit `config.json` for the trigger word.

## Uploading Training Images

You need to upload 10-20 high-quality training images (1024×1024 JPEG recommended) to `/workspace/phonics/photos/`.

1. Open your pod's JupyterLab interface
2. Navigate to `/workspace/phonics/photos/`
3. Click "Upload" and select your 10-20 training images
4. All images should be 1024×1024 JPEG files

## Training the Model

### Step 1: Navigate to Project Directory

```bash
cd /workspace/phonics
```

### Step 2: Label Images

Generate captions for your training images:

```bash
python3 label_images.py
```

This will:

- Process each image with BLIP captioning model
- Create `.txt` files with captions
- Append your trigger word to each caption
- you should review the labels and update them if they do seem ok

### Step 3: Run Fine-Tuning

Start the training process (training now split from inference):

```bash
python3 finetune_flux_train.py
```

**Training time:** Approximately 1-2  hours on A40 for 800–2000 steps (default config uses 800; can be customized with `--steps` argument).

**What happens:**

- Creates `flux_training_config.yaml` in the model output directory
- Runs ai-toolkit training
- Saves checkpoints every 250 steps to `./output/flux_lora/`
- Generates sample images every 250 steps to `./output/flux_lora/samples/`

**Monitor progress:**

- Watch the terminal for step updates
- Sample images appear under `output/flux_lora/`
- Check GPU usage: `nvidia-smi`

**To stop training:**

- Press `Ctrl+C` (wait for checkpoint message)
- Later restart from the latest checkpoint automatically

## Generating Images

### The prompts.txt file

Edit your prompts:  prompts.txt

the string [trigger] will be relaced by your trigger word when the file is used.

### Step 2: Generate Images

Run the inference script (`flux_infer.py`). The older `generate_images.py` is

```bash
python3 flux_infer.py
```

`flux_infer.py` now contains

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

### JupyterLab Interface

1. Navigate to `/workspace/phonics/output/generated_images/`
2. Right-click files → Download
3. Or select multiple files → Download as Archive
4. Also download the trained LoRA from `/workspace/phonics/output/flux_lora/` for future use

## Inference-Only Mode (Using Pre-Trained LoRA)

If you've already trained a LoRA model and want to generate new images without retraining, follow these steps:

### Step 1: Set Up a New Pod (or Local Environment)

If using RunPod with a fresh pod:

```bash
cd /workspace
git clone https://github.com/normrubin/phonics.git
cd phonics
setup.sh
```

### Step 2: Upload Your LoRA Model

Place your previously trained LoRA weights in the expected location:

```bash
# Create the output directory structure
mkdir -p output/flux_lora

# Upload your LoRA .safetensors file(s)
# Via JupyterLab: Navigate to output/flux_lora/ and upload

```

### Step 3: Configure Your Trigger Word

Edit `config.json` to include your trigger word (must match the one used during training):

### Step 4: Create Your Prompts

Create or edit `prompts.txt` with your prompts

### Step 5: Generate Images

Run inference with your uploaded LoRA:

# Use the latest checkpoint automatically

python3 flux_infer.py

**What happens:**

- Script loads FLUX.1-schnell base model from Hugging Face
- Applies your LoRA weights on top
- Generates images using your prompts
- Saves to `./output/generated_images/` (or custom output path)

### Step 6: Download Generated Images

Download your newly generated images:

- Via JupyterLab: Navigate to `output/generated_images/` and download
- Generated images are named with timestamps for easy organization

### Notes for Inference-Only Setup

**No training dependencies needed:**

- You don't need training images or captions

**LoRA file naming:**

- The script auto-detects the latest `.safetensors` file in `output/flux_lora/`
- Or specify exactly which checkpoint with `--lora` flag
- LoRA files are typically named like `flux_lora_000001000.safetensors` (step number)

**Reusing across projects:**

- Keep your LoRA weights backed up locally
- Upload to new pods as needed for different generation tasks
- The same LoRA can generate unlimited new images with different prompts

### Cost Saving Tips

1. **Stop pod when not in use**

   - Training completed? Stop the pod immediately, download images and LoRA, then terminate
   - Only pay for active time
2.
3. **Download and terminate**

   - Download your LoRA model
   - Terminate pod
   - Spin up new pod only for generation
4. **Batch your work**

   - Prepare all prompts beforehand
   - Generate all images in one session
   - Download everything and stop
