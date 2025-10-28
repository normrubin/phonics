# Phonics Book Generator

Build custom phonics books for kids with personalized illustrations featuring a specific person.

## Features

### 1. VLIM (Vision-Language Image Model) Customization
- Customize image generation to consistently feature a specific person
- Generate person-specific prompts for illustrations
- Create cover images and page illustrations
- Maintain character consistency across all images

### 2. Phonics Content Generation
- Generate text for phonics books teaching specific sound patterns
- Create age-appropriate stories (default: 4-6 years old)
- Include target words that demonstrate phonics concepts
- Generate detailed illustration descriptions

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/normrubin/phonics.git
cd phonics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings:
```bash
cp .env.example .env
# Edit .env with your API keys and person details
```

### Basic Usage

Run the sample book generator:
```bash
python generate_book.py
```

This will:
- Generate a sample phonics book about the "short a" sound
- Create text content for 8 pages
- Generate illustration descriptions
- Create image prompts customized for your person
- Save all output to the `generated_books/` directory

## Configuration

Edit `.env` to customize:

```env
# API Keys (optional - for automatic image generation)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Person Customization (required for personalization)
PERSON_NAME=Child's Name
PERSON_DESCRIPTION=A young child with brown hair and blue eyes
PERSON_AGE_RANGE=4-6 years old
```

## Usage Examples

### Example 1: Generate a Custom Book

```python
from config import BookConfig
from vlim_customizer import VLIMCustomizer
from phonics_generator import PhonicsContentGenerator, PhonicsBookBuilder

# Load configuration
config = BookConfig.from_env()

# Initialize components
content_gen = PhonicsContentGenerator(config.person, config.model)
book_builder = PhonicsBookBuilder(content_gen)

# Create a book
book = book_builder.create_book(
    title="Fun with Short A",
    phonics_concept="short a",
    target_words=["cat", "hat", "mat", "bat"],
    num_pages=8
)
```

### Example 2: Customize Image Prompts

```python
from config import BookConfig
from vlim_customizer import VLIMCustomizer

config = BookConfig.from_env()
vlim = VLIMCustomizer(config.person, config.model)

# Generate a customized image prompt
prompt = vlim.generate_image_prompt(
    phonics_concept="short a",
    word="cat",
    context="The cat is sitting on a mat"
)

print(prompt)
```

### Example 3: Generate Images (requires API key)

```python
from config import BookConfig
from vlim_customizer import ImageGenerator, VLIMCustomizer

config = BookConfig.from_env()
vlim = VLIMCustomizer(config.person, config.model)
image_gen = ImageGenerator(config.model)

# Generate a cover image
cover_prompt = vlim.generate_cover_prompt("My Phonics Book")
result = image_gen.generate_image(cover_prompt)

if result["status"] == "success":
    print(f"Image URL: {result['url']}")
```

## Project Structure

```
phonics/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment configuration
├── .gitignore               # Git ignore rules
├── config.py                # Configuration management
├── vlim_customizer.py       # VLIM customization for person-specific images
├── phonics_generator.py     # Phonics content generation
├── generate_book.py         # Main script to generate books
└── generated_books/         # Output directory (created automatically)
```

## How It Works

### 1. Person Customization (VLIM)

The `VLIMCustomizer` class creates a consistent base prompt for your person:

```python
base_person_prompt = (
    f"The main character is {name}, {description}. "
    f"The character is {age_range}. "
    "The style should be child-friendly, colorful, and engaging."
)
```

This ensures all generated images feature the same character consistently.

### 2. Content Generation

The `PhonicsContentGenerator` creates:
- Story text with target phonics words
- Age-appropriate sentences
- Repetitive patterns for early readers
- Detailed illustration descriptions

### 3. Book Building

The `PhonicsBookBuilder` combines:
- Story text
- Illustration descriptions  
- Phonics concepts
- Target words

into a complete book structure.

## Phonics Concepts Supported

You can create books for any phonics concept, including:

- **Short vowels**: short a, short e, short i, short o, short u
- **Long vowels**: long a, long e, long i, long o, long u
- **Consonant blends**: bl, cr, st, tr, etc.
- **Digraphs**: ch, sh, th, ph, wh
- **Word families**: -at, -an, -ig, -op, etc.

## Output

The generator creates:

1. **Book JSON file** (`sample_book.json`):
   - Complete book structure
   - Page text
   - Illustration descriptions
   - Target words and concepts

2. **Image prompts** (`image_prompts.txt`):
   - Ready-to-use prompts for image generation
   - Customized for your specific person
   - One prompt per page plus cover

3. **Generated images** (if API key configured):
   - Actual images from AI image generation
   - Featuring your specified person
   - Child-friendly style

## API Integration

### OpenAI (for both text and images)
- Text generation: GPT-4 for story content
- Image generation: DALL-E 3 for illustrations

Set `OPENAI_API_KEY` in your `.env` file to enable.

### Anthropic (optional, for text)
- Alternative text generation using Claude

Set `ANTHROPIC_API_KEY` in your `.env` file to enable.

## Tips for Best Results

1. **Be specific in person description**: Include details like hair color, eye color, age, and personality
2. **Start simple**: Begin with basic phonics concepts like "short a"
3. **Use familiar words**: Choose target words that are meaningful to the child
4. **Review prompts**: Check the generated image prompts before generating images
5. **Iterate**: Regenerate content if it doesn't match your needs

## Troubleshooting

### No API key configured
- The system will work without API keys
- It generates template content and prompts
- You can use the prompts manually with image generation tools

### Import errors
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.8 or higher

### Output directory issues
- The system creates `generated_books/` automatically
- Check file permissions if creation fails

## Contributing

Contributions welcome! Areas for improvement:
- Additional phonics patterns
- Better story templates
- Multi-page PDF generation
- Web interface
- More illustration styles

## License

MIT License - feel free to use and modify for your needs.

## Credits

Created for building personalized phonics books to help children learn to read.
