# Quick Reference Guide

Quick commands and code snippets for the Phonics Book Generator.

## Installation & Setup

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings
```

## Quick Commands

```bash
# Generate sample book
python generate_book.py

# View basic examples
python examples.py

# View advanced examples
python advanced_examples.py

# Check API configuration
python api_integration_guide.py
```

## Common Code Patterns

### Basic Book Generation

```python
from config import BookConfig
from phonics_generator import PhonicsContentGenerator, PhonicsBookBuilder

config = BookConfig.from_env()
content_gen = PhonicsContentGenerator(config.person, config.model)
builder = PhonicsBookBuilder(content_gen)

book = builder.create_book(
    title="My Book",
    phonics_concept="short a",
    target_words=["cat", "hat", "mat"],
    num_pages=6
)
```

### Custom Image Prompt

```python
from config import BookConfig
from vlim_customizer import VLIMCustomizer

config = BookConfig.from_env()
vlim = VLIMCustomizer(config.person, config.model)

prompt = vlim.generate_image_prompt(
    phonics_concept="short a",
    word="cat",
    context="playing with yarn"
)
```

### Custom Character

```python
from config import PersonConfig, ModelConfig, BookConfig

person = PersonConfig(
    name="Emma",
    description="A cheerful child with blonde hair",
    age_range="5-6 years old"
)

config = BookConfig(
    person=person,
    model=ModelConfig.from_env()
)
```

## Phonics Patterns

### Short Vowels
```python
patterns = ["short a", "short e", "short i", "short o", "short u"]
words = {
    "short a": ["cat", "bat", "mat", "hat"],
    "short e": ["bed", "red", "fed", "led"],
    "short i": ["big", "dig", "pig", "wig"],
    "short o": ["hot", "dot", "pot", "got"],
    "short u": ["bug", "rug", "hug", "mug"],
}
```

### Long Vowels
```python
patterns = ["long a", "long e", "long i", "long o", "long u"]
words = {
    "long a": ["cake", "lake", "make", "take"],
    "long e": ["bee", "tree", "see", "free"],
    "long i": ["bike", "like", "hike", "kite"],
    "long o": ["home", "bone", "cone", "rope"],
    "long u": ["cube", "tube", "huge", "cute"],
}
```

### Consonant Blends
```python
blends = {
    "bl blend": ["blue", "black", "block", "blanket"],
    "cl blend": ["clap", "clay", "clean", "climb"],
    "fl blend": ["flag", "fly", "flip", "flower"],
    "st blend": ["star", "stop", "stick", "step"],
    "tr blend": ["tree", "truck", "train", "track"],
}
```

### Digraphs
```python
digraphs = {
    "ch sound": ["chip", "chop", "chat", "chin"],
    "sh sound": ["ship", "shop", "shell", "fish"],
    "th sound": ["this", "that", "them", "path"],
    "wh sound": ["when", "what", "where", "why"],
    "ph sound": ["phone", "photo", "graph", "alphabet"],
}
```

### Word Families
```python
families = {
    "-at family": ["cat", "bat", "mat", "hat", "rat", "sat"],
    "-an family": ["can", "man", "pan", "ran", "fan", "tan"],
    "-ig family": ["big", "dig", "pig", "wig", "fig", "jig"],
    "-op family": ["hop", "mop", "pop", "top", "cop", "shop"],
}
```

## Configuration Options

### Environment Variables (.env)
```bash
# Required
PERSON_NAME=Your Child's Name
PERSON_DESCRIPTION=Description here
PERSON_AGE_RANGE=4-6 years old

# Optional
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OUTPUT_DIR=generated_books
IMAGE_MODEL=dall-e-3
TEXT_MODEL=gpt-4
```

### Programmatic Config
```python
from config import PersonConfig, ModelConfig, BookConfig

person = PersonConfig(
    name="Name",
    description="Description",
    age_range="4-6 years old"
)

model = ModelConfig(
    openai_api_key="sk-...",
    image_model="dall-e-3",
    text_model="gpt-4"
)

config = BookConfig(
    person=person,
    model=model,
    output_dir="my_books"
)
```

## Output Files

### Book JSON
```python
import json

# Load book
with open('generated_books/sample_book.json', 'r') as f:
    book = json.load(f)

# Access data
title = book['title']
pages = book['pages']
illustrations = book['illustrations']
```

### Image Prompts
```python
# Read prompts
with open('generated_books/image_prompts.txt', 'r') as f:
    prompts = f.read()
```

## Common Tasks

### Generate Multiple Books
```python
concepts = [
    ("short a", ["cat", "hat", "mat"]),
    ("short e", ["bed", "red", "fed"]),
    ("short i", ["big", "dig", "pig"]),
]

for concept, words in concepts:
    book = builder.create_book(
        title=f"{concept.title()} Book",
        phonics_concept=concept,
        target_words=words,
        num_pages=6
    )
    # Save book...
```

### Generate Series
```python
from pathlib import Path

output_dir = Path("generated_books/series")
output_dir.mkdir(parents=True, exist_ok=True)

for i, (concept, words) in enumerate(concepts, 1):
    book = builder.create_book(
        title=f"Book {i}: {concept}",
        phonics_concept=concept,
        target_words=words,
        num_pages=6
    )
    
    with open(output_dir / f"book_{i}.json", 'w') as f:
        json.dump(book, f, indent=2)
```

### Generate with Context
```python
contexts = {
    "cat": "playing with a ball of yarn",
    "dog": "running in the park",
    "bird": "sitting on a tree branch",
}

for word, context in contexts.items():
    prompt = vlim.generate_image_prompt(
        phonics_concept="short vowels",
        word=word,
        context=context
    )
    print(f"{word}: {prompt}")
```

## Troubleshooting

### Check Installation
```bash
python -c "import openai, anthropic, PIL, pydantic, yaml, dotenv; print('✅ All dependencies installed')"
```

### Verify Configuration
```python
from config import BookConfig
config = BookConfig.from_env()
print(f"Person: {config.person.name}")
print(f"Output: {config.output_dir}")
```

### Test Basic Functionality
```python
from config import BookConfig
from vlim_customizer import VLIMCustomizer
from phonics_generator import PhonicsContentGenerator, PhonicsBookBuilder

config = BookConfig.from_env()
vlim = VLIMCustomizer(config.person, config.model)
content_gen = PhonicsContentGenerator(config.person, config.model)
builder = PhonicsBookBuilder(content_gen)

print("✅ All components initialized")
```

## Tips

1. **Start Simple**: Begin with short vowels
2. **Be Specific**: Detailed person descriptions work best
3. **Test First**: Run examples.py before customizing
4. **Save Prompts**: Keep successful prompts for reuse
5. **Iterate**: Generate multiple versions
6. **Check Output**: Review generated files regularly
7. **Use Templates**: Works great without API keys
8. **Build Series**: Create progressive difficulty

## Resources

- `README.md` - Overview and quick start
- `USAGE_GUIDE.md` - Detailed usage instructions
- `PROJECT_SUMMARY.md` - Technical overview
- `examples.py` - Basic examples
- `advanced_examples.py` - Advanced patterns
- `api_integration_guide.py` - API setup

## Support

1. Check documentation
2. Run examples
3. Review error messages
4. Check .env configuration
5. Verify API keys (if using)

## Getting Help

```bash
# View README
cat README.md

# View usage guide
cat USAGE_GUIDE.md

# Run examples
python examples.py

# Check configuration
python api_integration_guide.py
```
