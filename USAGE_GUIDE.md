# Usage Guide

This guide provides detailed instructions for using the Phonics Book Generator.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [API Integration](#api-integration)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/normrubin/phonics.git
cd phonics
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up configuration:**
```bash
cp .env.example .env
```

Edit `.env` with your settings (see Configuration section below).

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Person Customization (Required)
PERSON_NAME=Alex
PERSON_DESCRIPTION=A happy child learning to read
PERSON_AGE_RANGE=4-6 years old

# API Keys (Optional - for AI-powered generation)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model Configuration (Optional)
IMAGE_MODEL=dall-e-3
TEXT_MODEL=gpt-4

# Output (Optional)
OUTPUT_DIR=generated_books
```

### Configuration in Code

You can also configure settings programmatically:

```python
from config import PersonConfig, ModelConfig, BookConfig

# Custom person
person = PersonConfig(
    name="Sophia",
    description="A curious child with curly red hair",
    age_range="5-6 years old"
)

# Create configuration
config = BookConfig(
    person=person,
    model=ModelConfig.from_env(),
    output_dir="my_books"
)
```

## Basic Usage

### Generate Your First Book

Run the main generator:

```bash
python generate_book.py
```

This will:
- Generate a sample phonics book about "short a"
- Create text content for 8 pages
- Generate illustration descriptions
- Create customized image prompts
- Save everything to `generated_books/`

### View Examples

```bash
python examples.py
```

This demonstrates:
- Creating basic phonics books
- Generating custom image prompts
- Building book series
- Creating covers
- Generating illustrations

### Advanced Examples

```bash
python advanced_examples.py
```

This shows:
- Long vowel patterns
- Consonant blends
- Custom characters
- Word families
- Digraphs

## Advanced Features

### 1. VLIM (Vision-Language Image Model) Customization

The VLIM customizer ensures consistent character appearance across all illustrations:

```python
from vlim_customizer import VLIMCustomizer
from config import BookConfig

config = BookConfig.from_env()
vlim = VLIMCustomizer(config.person, config.model)

# Generate a customized prompt
prompt = vlim.generate_image_prompt(
    phonics_concept="short a",
    word="cat",
    context="playing with a friendly cat"
)

print(prompt)
```

### 2. Phonics Content Generation

Generate age-appropriate stories with target words:

```python
from phonics_generator import PhonicsContentGenerator
from config import BookConfig

config = BookConfig.from_env()
generator = PhonicsContentGenerator(config.person, config.model)

lesson = generator.generate_phonics_story(
    phonics_concept="long e",
    target_words=["bee", "tree", "see", "free"],
    num_pages=6
)

print(lesson.story_text)
```

### 3. Complete Book Building

Build complete books with all components:

```python
from phonics_generator import PhonicsBookBuilder, PhonicsContentGenerator
from config import BookConfig

config = BookConfig.from_env()
content_gen = PhonicsContentGenerator(config.person, config.model)
builder = PhonicsBookBuilder(content_gen)

book = builder.create_book(
    title="My Phonics Adventure",
    phonics_concept="sh sound",
    target_words=["ship", "shop", "shell", "fish"],
    num_pages=6
)

# Access book components
print(book['title'])
print(book['pages'])
print(book['illustrations'])
```

## API Integration

### Without API Keys

The system works without API keys by generating:
- Template stories with your customized character
- Detailed image prompts ready for any image generator
- Structured book data

### With OpenAI API

When you add `OPENAI_API_KEY` to `.env`:
- AI generates custom story text
- DALL-E creates actual images
- Content is more varied and creative

### With Anthropic API

Add `ANTHROPIC_API_KEY` for:
- Alternative text generation using Claude
- Different writing styles

### Testing API Integration

```bash
python api_integration_guide.py
```

This checks your configuration and offers to run API tests.

## Examples

### Example 1: Short Vowel Book

```python
from config import BookConfig
from phonics_generator import PhonicsContentGenerator, PhonicsBookBuilder

config = BookConfig.from_env()
content_gen = PhonicsContentGenerator(config.person, config.model)
builder = PhonicsBookBuilder(content_gen)

book = builder.create_book(
    title="The Big Pig",
    phonics_concept="short i",
    target_words=["big", "pig", "dig", "wig"],
    num_pages=6
)
```

### Example 2: Word Family Series

```python
families = [
    ("-at family", ["cat", "bat", "mat", "hat"]),
    ("-an family", ["can", "man", "pan", "ran"]),
]

for family, words in families:
    book = builder.create_book(
        title=f"The {family}",
        phonics_concept=family,
        target_words=words,
        num_pages=6
    )
    # Save or process book
```

### Example 3: Custom Character Book

```python
from config import PersonConfig, ModelConfig, BookConfig

# Create a custom character
person = PersonConfig(
    name="Leo",
    description="An adventurous boy with glasses who loves space",
    age_range="6-7 years old"
)

config = BookConfig(
    person=person,
    model=ModelConfig.from_env()
)

# Generate space-themed phonics book
content_gen = PhonicsContentGenerator(config.person, config.model)
builder = PhonicsBookBuilder(content_gen)

book = builder.create_book(
    title="Leo's Space Adventure",
    phonics_concept="long o",
    target_words=["go", "so", "no", "home"],
    num_pages=6
)
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'openai'`

**Solution:**
```bash
pip install -r requirements.txt
```

### No Output Directory

**Problem:** Output directory not created

**Solution:** The system creates it automatically. Check file permissions:
```bash
chmod 755 .
```

### API Key Errors

**Problem:** API calls fail even with key set

**Solution:**
1. Verify key is correct in `.env`
2. Check API credits/quota
3. Verify API key has proper permissions

### Template Content Instead of AI Content

**Problem:** Getting template stories instead of AI-generated ones

**Reason:** This happens when:
- No API key is configured (expected behavior)
- API key is invalid
- API service is down

**Solution:** 
- Check your `.env` file
- Verify API key is valid
- Template content still works for generating prompts!

### Character Inconsistency in Images

**Problem:** Generated images show different-looking characters

**Solution:**
1. Be very specific in `PERSON_DESCRIPTION`
2. Include: age, hair color, eye color, distinctive features
3. Keep description under 100 characters
4. Use the same description across all books

### Python Version Issues

**Problem:** Syntax errors or import failures

**Solution:** Ensure Python 3.8+:
```bash
python --version
```

## Output Files

### Generated Book JSON
```json
{
  "title": "Book Title",
  "concept": "short a",
  "target_words": ["cat", "hat", "mat"],
  "pages": ["Page 1 text", "Page 2 text"],
  "illustrations": ["Description 1", "Description 2"]
}
```

### Image Prompts File
```
COVER IMAGE PROMPT:
[Detailed prompt for cover]

PAGE 1 IMAGE PROMPT:
[Detailed prompt for page 1]

PAGE 2 IMAGE PROMPT:
[Detailed prompt for page 2]
```

## Next Steps

1. **Customize your character** in `.env`
2. **Run the examples** to see what's possible
3. **Generate your first book** with `generate_book.py`
4. **Add API keys** for AI-powered generation
5. **Create a series** of phonics books
6. **Generate images** using the prompts

## Support

For issues or questions:
- Check this guide first
- Review the examples
- Check the README.md
- Open an issue on GitHub

## Contributing

Ideas for improvements:
- Additional phonics patterns
- Better story templates
- PDF generation
- Web interface
- More customization options

Feel free to contribute!
