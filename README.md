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
   - Recommended GPU: A40 (48GB VRAM) at ~$0.79/hour
   - Add credits to your account (minimum $10 recommended)
   - See [RunPod Setup Guide](RUNPOD_GUIDE.md) for detailed instructions
2. **Hugging Face Account**: Create account at [HuggingFace.co](https://huggingface.co)
   - Get a READ token from [HuggingFace tokens page](https://huggingface.co/settings/tokens)
   - Accept FLUX.1-schnell license (optional, Apache 2.0)
3. **Training Photos**: 10-20 photos of the child from different angles
   - Mix of headshots and full-body portraits
   - Various settings, poses, and lighting conditions
   - Should be size  1024×1024 pixels in JPEG format

# RunPod Setup Guide

## Creating a RunPod Instance

### Recommended Configuration

**GPU:** A40 (48GB VRAM) or A100 (40GB/80GB VRAM)

- FLUX.1-schnell training requires at least 24GB VRAM (sometimes more)
- A40 is the most cost-effective option for this project


### Steps to Create Instance

1. Go to [RunPod](https://runpod.io)
2. Click "Deploy" → "GPU Pods"
3. Select your GPU (A40 recommended)
4. Choose a pd template. I used Runpod pytorch 2.8.0.
5. Deploy pod

## Initial Setup

### Step 1: Connect to Your Pod

Once your pod is running, click "Connect" and choose: **JupyterLab** (good for interactive work)

### Step 2: Run Setup Script

In a terminal, run:

```bash
# Download and run setup script
cd /workspace
git clone https://github.com/normrubin/phonics.git -q
cd phonics
chmod +x runpod_setup.sh
./runpod_setup.sh
```

The setup script will **interactively prompt** you for:

1. **Hugging Face Token** - Enter your token (starts with `hf_`)

   - Get one from: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - The token is validated immediately against the Hugging Face API
   - If valid, it's saved to the `ENV` file automatically
2. **Trigger Word** - Enter your unique identifier. You want this to be a combination of letters and underscores that is not a word that the model has already seen

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
- Edit `config.json` for the trigger word

## Uploading Training Images

You need to upload 10-20 high-quality training images (1024×1024 JPEG recommended) to `/workspace/phonics/photos/`.

### Option 1: Using RunPod File Browser

1. Open your pod's JupyterLab interface
2. Navigate to `/workspace/phonics/photos/`
3. Click "Upload" and select your 10-20 training images
4. All images should be 1024×1024 JPEG files

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

**Training time:** Approximately 1-2 hours on A40 for 800–2000 steps (default config uses 800; adjust `steps:` in `flux_training_config.yaml`).

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

### Step 2: Generate Images

Run the inference script (`flux_infer.py`). The older `generate_images.py` is
deprecated and kept only as a compatibility shim.

```bash
python3 flux_infer.py prompts.txt
```

`flux_infer.py` now contains the full inference logic (merged from the former
`generate_images.py`).

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
4. you should also download the trained lora from /workspace/phonics/output/....

## Cost Management

### Estimated Costs (RunPod A40)

- **Training:** 2-4 hours @ ~$0.79/hr = $1.60-$3.20
- **Generation:** 20 images @ 20 sec each = ~$0.10
- **Total project:** ~$2-5 (one-time training + generation)

### Cost Saving Tips

1. **Stop pod when not in use**

   - Training completed? Stop the pod immediately, download the images and the lora, terminate the pod
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
5. **Use cheaper GPUs for generation (not sure if this works)**

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

**Important:** Stop or terminate your pod to avoid ongoing charge

**Running on RunPod?** See the complete [RunPod Setup Guide](RUNPOD_GUIDE.md) for detailed instructions.

Key scripts (train/infer split):

- Training + config generation: `finetune_flux_train.py`
- Inference (image generation): `flux_infer.py` (merged implementation; `generate_images.py` deprecated shim)

## Project Structure

```
phonics/
├── photos/                      # Training images (1024×1024 JPEG)
│   ├── image_001.jpg
│   ├── image_001.txt           # Auto-generated captions
│   └── ...
├── output/                      # All generated outputs
│   ├── flux_lora/              # Model-specific directory
│   │   ├── flux_training_config.yaml   # Training configuration
│   │   ├── *.safetensors      # LoRA weight checkpoints
│   │   └── samples/            # Sample images during training
│   └── generated_images/       # Final inference outputs
├── config.json                  # Project configuration
├── ENV                          # Environment variables (HF_TOKEN)
├── finetune_flux_train.py      # Training script
├── flux_infer.py               # Inference script
├── label_images.py             # Caption generation tool
└── setup_runpod.py             # RunPod setup automation
```

## Project Components

This project consists of four main steps:

1. **Fine-tuning a Vision Model** - Train the model to generate recognizable images of the specific child. The resulting model can be reused for other projects.
2. **Content Generation** - Create the text, image descriptions, and layout for the phonics book
3. **Image Generation** - Generate images for each image description
4. **Book Assembly** - Compile the final formatted book

## Workflow

### Step 1: Image Preparation

Select 10 to 20 images of the child. They should be a mix of headshots and full-body portraits in various settings, poses, and lighting conditions. Place all images directly in the `./photos` directory. All images must be 1024×1024 pixels in JPEG format (may require interactive cropping or upscaling).

### Step 1a: Resize images

Resize your images to 1024×1024 pixels using your preferred image editing tool.

### Step 1b: Create captions

Generate descriptive captions for each image using the automated labeling tool:

```bash
python label_images.py
```

The labeling tool uses the BLIP image captioning model to automatically generate descriptive captions and saves them as `.txt` files alongside each image (e.g., `pict_1.jpg` → `pict_1.txt`). The trigger word is always taken from your config.json.

### Step 2: Model Fine-Tuning

Fine-tune the FLUX.1-schnell model on the prepared images using the ai-toolkit.

**Prerequisites:**

1. Clone and set up ai-toolkit:

```bash
   cd ..
   git clone https://github.com/ostris/ai-toolkit.git
   cd ai-toolkit
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install torch
   pip install -r requirements.txt

```

1. Create an `ENV` file in the phonics project root:

```bash
HF_TOKEN=your_huggingface_token_here
```

   **Note:** FLUX.1-schnell has an Apache 2.0 license and doesn't require a Hugging Face token. The token is optional but recommended for other models.

**Run Fine-tuning:**

```bash
python finetune_flux_train.py
```

The script will:

- Load settings from `config.json` (dataset path, trigger word, output directory)
- Generate a training configuration file (`flux_training_config.yaml`)
- Run the ai-toolkit training process
- Save the trained LoRA model to `./output/flux_lora/`

**Training Configuration:**

The default configuration trains a LoRA adapter with:

- 2000 training steps
- 1024×1024 resolution
- Sample images generated every 250 steps
- Model checkpoints saved every 250 steps

You can modify these settings by editing the generated `flux_training_config.yaml` file before training, or by modifying the `create_flux_config()` function in `finetune_flux_train.py`.

### Step 3: Image Generation

Generate images from text prompts using the fine-tuned model.

**Create a prompts file:**

Create a text file with your prompts (one per line). See `prompts.txt.example` for reference:

```text
# Example prompts
[trigger] reading a book in a cozy library
[trigger] playing with colorful alphabet blocks
[trigger] holding the letter A on a bright sunny day
```

**Generate images:**

```bash
python flux_infer.py prompts.txt
```

The script will:

- Load the fine-tuned FLUX.1-schnell model with your LoRA weights
- Read prompts from the specified file
- Generate 1024×1024 images for each prompt
- Save images to `./output/generated_images/`

**Advanced options:**

```bash
# Use custom LoRA weights
python flux_infer.py prompts.txt --lora path/to/lora

# Generate with specific seed for reproducibility
python flux_infer.py prompts.txt --seed 42

# Generate with more inference steps (slower but potentially higher quality)
python flux_infer.py prompts.txt --steps 8

# Specify output directory
python flux_infer.py prompts.txt --output ./my_images
```

**Generation Settings:**

- Default: 1024×1024 pixels, 4 inference steps (optimized for FLUX.1-schnell)
- Guidance scale: 1.0 (recommended for schnell)
- Supports seeded generation for reproducibility
- Automatically increments seed for variation when generating multiple images

## Image Labeling Tool

This repository includes an automated image labeling tool that uses the BLIP (Bootstrapping Language-Image Pre-training) model to generate descriptive captions for your images.

The tool automatically reads settings from `config.json` for the image directory and trigger word.

### Usage

```bash
python label_images.py

# Overwrite existing captions
python label_images.py --overwrite
```

### Options

- `--max-tokens`: Maximum tokens per caption (default: 30)
- `--overwrite`: Overwrite existing caption files

### How It Works

The tool:

1. Loads the BLIP image captioning model (requires ~2GB GPU memory)
2. Processes each image in the specified directory
3. Generates a descriptive caption
4. Optionally appends a token/trigger word
5. Saves captions as `.txt` files with the same name as the images

**Example Output:**

- Image: `photo_001.jpg`
- Caption file: `photo_001.txt`
- Content: `"a young [trigger] standing in a park"`
