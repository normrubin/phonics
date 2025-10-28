"""
Example usage of the phonics book generator.
This script shows various ways to use the system.
"""
from config import BookConfig
from vlim_customizer import VLIMCustomizer, ImageGenerator
from phonics_generator import PhonicsContentGenerator, PhonicsBookBuilder


def example_1_basic_book():
    """Example 1: Create a basic phonics book."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Phonics Book")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    content_gen = PhonicsContentGenerator(config.person, config.model)
    book_builder = PhonicsBookBuilder(content_gen)
    
    book = book_builder.create_book(
        title="Sam and the Van",
        phonics_concept="short a",
        target_words=["sam", "van", "can", "man", "ran", "fan"],
        num_pages=6
    )
    
    print(f"Title: {book['title']}")
    print(f"Concept: {book['concept']}")
    print(f"Number of pages: {len(book['pages'])}")
    print()
    
    for i, page in enumerate(book['pages'], 1):
        print(f"Page {i}: {page}")
    print()


def example_2_custom_prompts():
    """Example 2: Generate custom image prompts."""
    print("=" * 60)
    print("EXAMPLE 2: Custom Image Prompts")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    vlim = VLIMCustomizer(config.person, config.model)
    
    # Different phonics concepts
    concepts = [
        ("long e", "bee", "seeing a bee on a flower"),
        ("sh sound", "ship", "playing with a toy ship"),
        ("ing ending", "jumping", "jumping rope in the park"),
    ]
    
    for concept, word, context in concepts:
        prompt = vlim.generate_image_prompt(concept, word, context)
        print(f"Concept: {concept}")
        print(f"Word: {word}")
        print(f"Prompt: {prompt}")
        print()


def example_3_multiple_books():
    """Example 3: Create multiple books for a series."""
    print("=" * 60)
    print("EXAMPLE 3: Book Series")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    content_gen = PhonicsContentGenerator(config.person, config.model)
    book_builder = PhonicsBookBuilder(content_gen)
    
    # Create a series of books for different short vowels
    vowel_series = [
        ("short a", ["cat", "hat", "bat", "mat"]),
        ("short e", ["bed", "red", "led", "fed"]),
        ("short i", ["big", "dig", "pig", "wig"]),
        ("short o", ["hot", "dot", "pot", "got"]),
        ("short u", ["bug", "rug", "hug", "mug"]),
    ]
    
    for concept, words in vowel_series:
        title = f"{config.person.name}'s {concept.title()} Adventure"
        book = book_builder.create_book(
            title=title,
            phonics_concept=concept,
            target_words=words,
            num_pages=len(words) + 2
        )
        print(f"Created: {book['title']}")
        print(f"  Concept: {book['concept']}")
        print(f"  Words: {', '.join(book['target_words'])}")
        print()


def example_4_cover_generation():
    """Example 4: Generate book covers."""
    print("=" * 60)
    print("EXAMPLE 4: Book Cover Prompts")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    vlim = VLIMCustomizer(config.person, config.model)
    
    books = [
        ("My First Phonics Book", "learning letters"),
        ("The ABC Adventure", "alphabet exploration"),
        ("Fun with Sounds", "phonics patterns"),
    ]
    
    for title, theme in books:
        cover_prompt = vlim.generate_cover_prompt(title, theme)
        print(f"Book: {title}")
        print(f"Cover Prompt: {cover_prompt}")
        print()


def example_5_illustration_descriptions():
    """Example 5: Generate detailed illustration descriptions."""
    print("=" * 60)
    print("EXAMPLE 5: Detailed Illustration Descriptions")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    content_gen = PhonicsContentGenerator(config.person, config.model)
    
    scenes = [
        ("The dog runs fast.", "short o", "dog"),
        ("A big red ball bounces.", "short a", "ball"),
        ("The sun is hot.", "short u", "sun"),
    ]
    
    for page_text, concept, word in scenes:
        description = content_gen.generate_illustration_description(
            page_text, 
            concept, 
            word
        )
        print(f"Page text: {page_text}")
        print(f"Illustration: {description}")
        print()


def main():
    """Run all examples."""
    print("\n🎨 Phonics Book Generator - Usage Examples\n")
    
    example_1_basic_book()
    example_2_custom_prompts()
    example_3_multiple_books()
    example_4_cover_generation()
    example_5_illustration_descriptions()
    
    print("=" * 60)
    print("✨ All examples completed!")
    print("=" * 60)
    print()
    print("You can now:")
    print("1. Modify these examples for your needs")
    print("2. Create your own custom books")
    print("3. Generate images using the prompts with an API key")
    print()


if __name__ == "__main__":
    main()
