"""
Main script for generating personalized phonics books.
This script demonstrates how to use the VLIM customizer and phonics generator
to create custom phonics books featuring a specific person.
"""
import os
import json
from pathlib import Path
from config import BookConfig
from vlim_customizer import VLIMCustomizer, ImageGenerator
from phonics_generator import PhonicsContentGenerator, PhonicsBookBuilder


def create_output_directory(config: BookConfig) -> Path:
    """Create the output directory if it doesn't exist."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_sample_book(config: BookConfig):
    """
    Generate a sample phonics book.
    
    Args:
        config: Book configuration
    """
    print(f"🎨 Generating phonics book for {config.person.name}...")
    print(f"📝 Person description: {config.person.description}")
    print()
    
    # Initialize components
    vlim = VLIMCustomizer(config.person, config.model)
    content_gen = PhonicsContentGenerator(config.person, config.model)
    book_builder = PhonicsBookBuilder(content_gen)
    image_gen = ImageGenerator(config.model)
    
    # Create a sample book about "short a" sound
    book_title = "The Cat and the Hat"
    phonics_concept = "short a"
    target_words = ["cat", "hat", "mat", "rat", "sat", "pat"]
    
    print(f"📚 Creating book: '{book_title}'")
    print(f"🔤 Teaching concept: {phonics_concept}")
    print(f"📖 Target words: {', '.join(target_words)}")
    print()
    
    # Generate the book content
    book = book_builder.create_book(
        title=book_title,
        phonics_concept=phonics_concept,
        target_words=target_words,
        num_pages=8
    )
    
    # Save book data
    output_dir = create_output_directory(config)
    book_file = output_dir / "sample_book.json"
    
    # Create a JSON-serializable version of the book
    book_data = {
        "title": book["title"],
        "concept": book["concept"],
        "target_words": book["target_words"],
        "pages": book["pages"],
        "illustrations": book["illustrations"]
    }
    
    with open(book_file, 'w') as f:
        json.dump(book_data, f, indent=2)
    
    print(f"✅ Book content saved to: {book_file}")
    print()
    
    # Display the book content
    print("=" * 60)
    print(f"BOOK: {book['title']}")
    print(f"CONCEPT: {book['concept']}")
    print("=" * 60)
    print()
    
    for i, (page_text, illustration_desc) in enumerate(
        zip(book['pages'], book['illustrations']), 
        start=1
    ):
        print(f"--- PAGE {i} ---")
        print(f"Text: {page_text}")
        print(f"Illustration: {illustration_desc}")
        print()
    
    # Generate image prompts for each illustration
    print("=" * 60)
    print("IMAGE GENERATION PROMPTS")
    print("=" * 60)
    print()
    
    prompts_file = output_dir / "image_prompts.txt"
    with open(prompts_file, 'w') as f:
        # Cover
        cover_prompt = vlim.generate_cover_prompt(book_title, phonics_concept)
        f.write("COVER IMAGE PROMPT:\n")
        f.write(cover_prompt + "\n\n")
        print("COVER:")
        print(cover_prompt)
        print()
        
        # Generate prompts for each page
        for i, (page_text, word) in enumerate(
            zip(book['pages'], target_words[:len(book['pages'])]), 
            start=1
        ):
            prompt = vlim.generate_image_prompt(
                phonics_concept, 
                word,
                context=page_text
            )
            f.write(f"PAGE {i} IMAGE PROMPT:\n")
            f.write(prompt + "\n\n")
            print(f"PAGE {i}:")
            print(prompt)
            print()
    
    print(f"✅ Image prompts saved to: {prompts_file}")
    print()
    
    # If API keys are configured, demonstrate image generation
    if config.model.openai_api_key:
        print("🎨 Generating sample cover image...")
        result = image_gen.generate_image(cover_prompt)
        
        if result["status"] == "success":
            print(f"✅ Image generated successfully!")
            print(f"URL: {result['url']}")
            if result.get('revised_prompt'):
                print(f"Revised prompt: {result['revised_prompt']}")
        else:
            print(f"❌ Image generation failed: {result.get('message', 'Unknown error')}")
        print()
    else:
        print("ℹ️  To generate actual images, set OPENAI_API_KEY in your .env file")
        print()


def demonstrate_vlim_customization(config: BookConfig):
    """
    Demonstrate VLIM customization capabilities.
    
    Args:
        config: Book configuration
    """
    print("=" * 60)
    print("VLIM CUSTOMIZATION DEMONSTRATION")
    print("=" * 60)
    print()
    
    vlim = VLIMCustomizer(config.person, config.model)
    
    print(f"Base person prompt:")
    print(vlim.base_person_prompt)
    print()
    
    # Example customizations
    examples = [
        ("short a", "cat", "The cat is playing with yarn"),
        ("long e", "tree", "A beautiful tree in the park"),
        ("ch sound", "cheese", "Enjoying a cheese sandwich"),
    ]
    
    print("Example customized prompts:")
    print()
    
    for concept, word, context in examples:
        print(f"Concept: {concept}, Word: {word}")
        prompt = vlim.generate_image_prompt(concept, word, context)
        print(f"Prompt: {prompt}")
        print()


def main():
    """Main entry point."""
    print("🎨 Phonics Book Generator")
    print("Creating personalized phonics books with custom illustrations")
    print()
    
    # Load configuration
    config = BookConfig.from_env()
    
    print(f"Configuration loaded:")
    print(f"  Person: {config.person.name}")
    print(f"  Age range: {config.person.age_range}")
    print(f"  Output directory: {config.output_dir}")
    print()
    
    # Demonstrate VLIM customization
    demonstrate_vlim_customization(config)
    
    # Generate a sample book
    generate_sample_book(config)
    
    print("=" * 60)
    print("✨ Done! Your personalized phonics book has been generated.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the generated book content in the output directory")
    print("2. Use the image prompts to generate illustrations")
    print("3. Configure your API keys in .env to enable automatic image generation")
    print("4. Customize the person description in .env or config.py")
    print()


if __name__ == "__main__":
    main()
