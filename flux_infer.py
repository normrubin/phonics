#!/usr/bin/env python3
"""Flux Inference Script (FLUX.1-schnell + optional LoRA)

Merged implementation: previous standalone generate_images.py has been
removed. Use this script for all image generation:

    python flux_infer.py prompts.txt [options]

Features:
    - Auto-detect LoRA weights in ./output/flux_lora/
    - Automatic trigger word prefixing (idempotent)
    - Seeded generation with incremental variation
    - Adjustable size, steps, guidance
    - Single maintained inference entry point (generate_images.py removed)
"""

import argparse
import sys
from pathlib import Path
import dotenv  # type: ignore
import torch  # type: ignore
from diffusers import FluxPipeline  # type: ignore

from config import get_config


def load_pipeline(model_path, lora_path=None, device=None):
    """Load FLUX.1-schnell pipeline with optional LoRA weights."""
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading FLUX.1-schnell model on {device}...")
    print(f"Base model: {model_path}")

    pipeline = FluxPipeline.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
    ).to(device)

    if lora_path:
        print(f"Loading LoRA weights from: {lora_path}")
        pipeline.load_lora_weights(lora_path)
        print("✓ LoRA weights loaded")

    print("✓ Pipeline loaded successfully")
    return pipeline


def read_prompts(prompt_file):
    """Read prompts from text file (skip empty lines and comments)."""
    path = Path(prompt_file)
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    prompts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                prompts.append(line)
    return prompts


def prefix_prompts_with_trigger(prompts, trigger_word):
    """Prefix prompts with 'photo of <trigger> ' unless already present."""
    if not trigger_word:
        return prompts
    prefix = f"photo of {trigger_word} "
    out = []
    for p in prompts:
        if p.lower().startswith(prefix.lower()):
            out.append(p)
        else:
            out.append(prefix + p)
    return out


def generate_images(
    pipeline,
    prompts,
    output_dir,
    width=1024,
    height=1024,
    num_steps=4,
    guidance_scale=1.0,
    seed=None,
):
    """Generate images from prompts and save to output directory."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating {len(prompts)} image(s)...")
    print(f"Output directory: {out_path}")
    print(f"Image size: {width}x{height}")
    print(f"Steps: {num_steps}")
    print(f"Guidance scale: {guidance_scale}")
    if seed is not None:
        print(f"Seed: {seed}")
    print()

    generator = None
    if seed is not None:
        generator = torch.Generator(device=pipeline.device).manual_seed(seed)

    for idx, prompt in enumerate(prompts, start=1):
        short = prompt[:60]
        print(f"[{idx}/{len(prompts)}] Generating: {short}...")
        image = pipeline(
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=num_steps,
            guidance_scale=guidance_scale,
            generator=generator,
        ).images[0]
        out_file = out_path / f"image_{idx:04d}.png"
        image.save(out_file)
        print(f"  ✓ Saved: {out_file}")
        if generator is not None and seed is not None:
            seed += 1
            generator = torch.Generator(device=pipeline.device).manual_seed(
                seed
            )

    bar = "=" * 60
    gen_msg = (
        f"\n{bar}\nGeneration complete!\n"
        f"Generated: {len(prompts)} image(s)"
    )
    print(gen_msg)
    print(f"Output: {out_path}\n{bar}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate images from prompts using FLUX.1-schnell (inference)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate using fine-tuned LoRA
  python flux_infer.py prompts.txt

  # Generate with custom LoRA path
  python flux_infer.py prompts.txt --lora path/to/lora

  # Generate with specific seed for reproducibility
  python flux_infer.py prompts.txt --seed 42

  # Generate larger images with more steps
  python flux_infer.py prompts.txt --width 1024 --height 1024 --steps 8
        """,
    )

    parser.add_argument(
        "prompt_file",
        help="Text file with prompts (one per line)",
    )
    parser.add_argument(
        "--lora",
        type=str,
        help="Path to LoRA weights (default: from config output dir)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="black-forest-labs/FLUX.1-schnell",
        help="Base model path or HF ID (default: FLUX.1-schnell)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory (default: from config)",
    )
    parser.add_argument(
        "--width", type=int, default=1024, help="Image width (default: 1024)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1024,
        help="Image height (default: 1024)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=4,
        help="Inference steps (default: 4 for schnell)",
    )
    parser.add_argument(
        "--guidance",
        type=float,
        default=1.0,
        help="Guidance scale (default: 1.0 for schnell)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu"],
        help="Device to use (default: auto-detect)",
    )

    args = parser.parse_args()

    # Load environment variables (optional)
    dotenv.load_dotenv("ENV")

    # Load configuration
    try:
        config = get_config()
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        config = None

    # Determine LoRA path
    lora_path = args.lora
    if lora_path is None and config:
        default_lora = config.output_dir / "flux_lora"
        if default_lora.exists():
            lora_files = list(default_lora.glob("*.safetensors"))
            if lora_files:
                lora_path = str(default_lora)
                print(f"Using LoRA from config output: {lora_path}")
            else:
                print(f"Warning: No LoRA files found in {default_lora}")
                print("Generating with base model only")

    # Determine output directory
    output_dir = args.output
    if output_dir is None and config:
        output_dir = str(config.output_dir / "generated_images")
    elif output_dir is None:
        output_dir = "./output/generated_images"

    # Read prompts
    try:
        prompts = read_prompts(args.prompt_file)
        print(f"Loaded {len(prompts)} prompt(s) from {args.prompt_file}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Prefix with trigger word from config if available
    trigger_word = getattr(config, "trigger_word", None) if config else None
    if trigger_word:
        original_first = prompts[0] if prompts else ""
        prompts = prefix_prompts_with_trigger(prompts, trigger_word)
        if original_first != (prompts[0] if prompts else ""):
            print(f"Applied trigger word prefix using '{trigger_word}'")
        else:
            print(f"Prompts already had prefix for trigger '{trigger_word}'")

    if not prompts:
        print("Error: No valid prompts found in file")
        sys.exit(1)

    # Load pipeline
    try:
        pipeline = load_pipeline(args.model, lora_path, args.device)
    except Exception as e:
        print(f"Error loading pipeline: {e}")
        sys.exit(1)

    try:
        generate_images(
            pipeline=pipeline,
            prompts=prompts,
            output_dir=output_dir,
            width=args.width,
            height=args.height,
            num_steps=args.steps,
            guidance_scale=args.guidance,
            seed=args.seed,
        )
    except Exception as e:
        print(f"Error generating images: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
