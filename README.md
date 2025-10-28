# phonics
build custom phonics books for kids

## Image Resizing Tool

This repository includes a tool to resize images to a standard 1024x1024 pixel format, useful for preparing images for phonics books.

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Usage

Resize all images in a folder to 1024x1024 pixels:

```bash
python resize_images.py /path/to/images
```

This will resize the images in-place (overwriting the originals).

To save resized images to a different folder:

```bash
python resize_images.py /path/to/images --output /path/to/resized
```

To resize images to a custom size:

```bash
python resize_images.py /path/to/images --size 512 512
```

### Supported Image Formats

The script supports the following image formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff)
- WebP (.webp)

### Features

- High-quality image resizing using Lanczos resampling
- Automatic conversion of RGBA images to RGB with white background
- Batch processing of entire folders
- Detailed progress reporting
- Error handling for invalid inputs
