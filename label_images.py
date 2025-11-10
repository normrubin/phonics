#!/usr/bin/env python3
"""
Image Labeling Tool for Phonics Book Generator

This script automatically generates captions for images using the
Salesforce BLIP image captioning model. Captions are saved as .txt
files with the same name as the images.
"""

import argparse
import re
import sys
from pathlib import Path
from PIL import Image  # type: ignore
from transformers import (  # type: ignore
    BlipProcessor,
    BlipForConditionalGeneration,
)
import torch  # type: ignore

from config import get_config


def setup_model(device=None):
    """
    Load the BLIP image captioning model

    Args:
        device: Device to use ('cuda', 'cpu', or None for auto-detect)

    Returns:
        Tuple of (processor, model)
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading BLIP model on {device}...")
    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    ).to(device)

    print("✓ Model loaded successfully")
    return processor, model, device


def generate_caption(
    image_path,
    processor,
    model,
    device,
    token=None,
    max_tokens=30,
):
    """
    Generate a caption for a single image

    Args:
        image_path: Path to the image file
        processor: BLIP processor
        model: BLIP model
        device: Device to run on
        token: Optional token to append to caption (e.g., child's name)
        max_tokens: Maximum number of tokens to generate

    Returns:
        Generated caption string
    """
    # Load and process image
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)

    # Generate caption
    out = model.generate(**inputs, max_new_tokens=max_tokens)
    caption = processor.decode(out[0], skip_special_tokens=True)

    # insert token if provided
    if token:
        caption = re.sub(
            r"\b (woman|girl|person|man|boy)\b",
            " " + token, caption)

    return caption


def label_images(
    data_dir,
    token=None,
    max_tokens=30,
    device=None,
    overwrite=False,
    extensions=None,
):
    """
    Label all images in a directory

    Args:
        data_dir: Directory containing images
        token: Optional token to append to captions
        max_tokens: Maximum tokens per caption
        device: Device to use
        overwrite: Whether to overwrite existing captions
        extensions: List of image file extensions to process

    Returns:
        Number of images processed
    """
    if extensions is None:
        extensions = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]

    # Setup model
    processor, model, device = setup_model(device)

    # Find all image files
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"Error: Directory '{data_dir}' does not exist")
        return 0

    image_files = []
    for ext in extensions:
        image_files.extend(data_path.glob(f"*{ext}"))
        image_files.extend(data_path.glob(f"*{ext.upper()}"))

    if not image_files:
        print(f"No image files found in {data_dir}")
        return 0

    print(f"\nFound {len(image_files)} image(s) to label")
    if token:
        print(f"Token to append: '{token}'")
    print()

    # Process each image
    processed = 0
    skipped = 0

    for img_path in sorted(image_files):
        txt_path = img_path.with_suffix(".txt")

        # Check if caption already exists
        if txt_path.exists() and not overwrite:
            print("⊘ {}: Caption exists, skipping".format(img_path.name))
            print("    (use --overwrite to replace)")
            skipped += 1
            continue

        # Check image size
        try:
            with Image.open(img_path) as im:
                if im.size != (1024, 1024):
                    print("⚠ {}: Skipped (image size)".format(img_path.name))
                    print("    Must be 1024x1024")
                    print("    Actual size:", im.size[0], "x", im.size[1])
                    skipped += 1
                    continue
        except Exception as e:
            print("✗ {}: Error opening image - {}".format(img_path.name, e))
            skipped += 1
            continue

        try:
            # Generate caption
            caption = generate_caption(
                img_path, processor, model, device, token, max_tokens
            )

            # Save caption
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(caption)

            print("✓ {}: {}".format(img_path.name, caption))
            processed += 1

        except Exception as e:
            print(f"✗ {img_path.name}: Error - {e}")

    # Summary
    print("\n{}".format("=" * 60))
    print("Labeling complete!")
    print("Processed: {}".format(processed))
    print("Skipped: {}".format(skipped))
    print("Output: {}".format(data_dir))
    print("{}".format("=" * 60))

    # Validate that trigger word appears in all captions if token was provided
    if token and processed > 0:
        print("\nValidating trigger word in captions...")
        missing_trigger = []
        for img_path in sorted(image_files):
            txt_path = img_path.with_suffix(".txt")
            if txt_path.exists():
                try:
                    with open(txt_path, "r", encoding="utf-8") as f:
                        caption_text = f.read().strip()
                        if token.lower() not in caption_text.lower():
                            missing_trigger.append(img_path.name)
                            print(
                                f"✗ {img_path.name}: Trigger word '{token}' "
                                "NOT found in caption"
                            )
                            print(f"   Caption: {caption_text}")
                except Exception as e:
                    print(f"Warning: Could not validate {txt_path.name}: {e}")

        if missing_trigger:
            print("\n" + "=" * 60)
            print("ERROR: Trigger word validation failed!")
            print(
                f"The trigger word '{token}' is missing from "
                f"{len(missing_trigger)} caption(s)."
            )
            print("\nThis will cause training problems. Please:")
            print("1. Check your config.json trigger_word setting")
            print("2. Re-run with --overwrite to regenerate captions")
            print(
                "3. Or manually edit the caption files to include the trigger")
            print("=" * 60)
            sys.exit(1)
        else:
            print(f"✓ All captions contain the trigger word '{token}'")

    return processed


def main():
    parser = argparse.ArgumentParser(
        description="Generate captions for images using BLIP model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Label images using config.json settings
  python label_images.py

  # Override trigger word from config
  python label_images.py --token "custom_token"

  # Overwrite existing captions
  python label_images.py --overwrite
        """,
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=30,
        help="Maximum tokens to generate per caption (default: 30)",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing captions"
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = get_config()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease create a config.json file in the project root.")
        print("See README.md for configuration details.")
        sys.exit(1)

    # Get directory from config
    directory = str(config.photo_images_dir)
    print(f"Using directory from config: {directory}")

    # Always use trigger word from config
    token = config.trigger_word
    if token:
        print(f"Using trigger word from config: '{token}'")
    else:
        print("No trigger word specified")

    # Run labeling
    label_images(
        data_dir=directory,
        token=token,
        max_tokens=args.max_tokens,
        device=None,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
