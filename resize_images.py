#!/usr/bin/env python3
"""
Script to resize images in a folder to 1024x1024 pixels.
"""

import argparse
import os
import sys
from pathlib import Path
from PIL import Image


def resize_image(input_path, output_path, size=(1024, 1024)):
    """
    Resize an image to the specified size.
    
    Args:
        input_path: Path to the input image
        output_path: Path to save the resized image
        size: Tuple of (width, height) for the output size
    """
    try:
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Resize the image using high-quality resampling
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Save the resized image
            resized_img.save(output_path, quality=95)
            print(f"Resized: {input_path} -> {output_path}")
            return True
    except Exception as e:
        print(f"Error resizing {input_path}: {e}", file=sys.stderr)
        return False


def process_folder(input_folder, output_folder=None, size=(1024, 1024)):
    """
    Process all images in a folder and resize them.
    
    Args:
        input_folder: Path to folder containing images
        output_folder: Path to folder for resized images (None = overwrite originals)
        size: Tuple of (width, height) for the output size
    """
    input_path = Path(input_folder)
    
    if not input_path.exists():
        print(f"Error: Input folder '{input_folder}' does not exist.", file=sys.stderr)
        return False
    
    if not input_path.is_dir():
        print(f"Error: '{input_folder}' is not a directory.", file=sys.stderr)
        return False
    
    # Determine output folder
    if output_folder:
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    # Find all image files
    image_files = [
        f for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"No image files found in '{input_folder}'.", file=sys.stderr)
        return False
    
    print(f"Found {len(image_files)} image(s) to process.")
    
    # Process each image
    success_count = 0
    for img_file in image_files:
        output_file = output_path / img_file.name
        if resize_image(img_file, output_file, size):
            success_count += 1
    
    print(f"\nSuccessfully resized {success_count}/{len(image_files)} image(s).")
    return success_count > 0


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Resize images in a folder to 1024x1024 pixels.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resize images in-place (overwrite originals)
  python resize_images.py /path/to/images

  # Resize images and save to a different folder
  python resize_images.py /path/to/images --output /path/to/resized

  # Resize to custom dimensions
  python resize_images.py /path/to/images --size 512 512
        """
    )
    
    parser.add_argument(
        'input_folder',
        help='Path to folder containing images to resize'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_folder',
        help='Output folder for resized images (default: overwrite originals)'
    )
    
    parser.add_argument(
        '-s', '--size',
        nargs=2,
        type=int,
        default=[1024, 1024],
        metavar=('WIDTH', 'HEIGHT'),
        help='Target size for images (default: 1024 1024)'
    )
    
    args = parser.parse_args()
    
    # Process the folder
    size = tuple(args.size)
    success = process_folder(args.input_folder, args.output_folder, size)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
