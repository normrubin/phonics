"""
Advanced examples showing different phonics patterns and customization options.
"""
from config import BookConfig, PersonConfig, ModelConfig
from vlim_customizer import VLIMCustomizer
from phonics_generator import PhonicsContentGenerator, PhonicsBookBuilder
import json
from pathlib import Path


def create_long_vowels_series():
    """Create a complete series for long vowels with silent e."""
    print("=" * 60)
    print("ADVANCED EXAMPLE 1: Long Vowels Series")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    content_gen = PhonicsContentGenerator(config.person, config.model)
    book_builder = PhonicsBookBuilder(content_gen)
    vlim = VLIMCustomizer(config.person, config.model)
    
    long_vowels = [
        ("long a with silent e", ["cake", "lake", "make", "take", "bake"]),
        ("long i with silent e", ["bike", "like", "hike", "kite", "bite"]),
        ("long o with silent e", ["home", "bone", "cone", "hope", "rope"]),
    ]
    
    output_dir = Path(config.output_dir) / "long_vowels_series"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for concept, words in long_vowels:
        title = f"{config.person.name} and the Magic E: {words[0].title()}"
        book = book_builder.create_book(
            title=title,
            phonics_concept=concept,
            target_words=words,
            num_pages=len(words) + 2
        )
        
        # Save book
        filename = concept.replace(" ", "_") + ".json"
        with open(output_dir / filename, 'w') as f:
            book_data = {
                "title": book["title"],
                "concept": book["concept"],
                "target_words": book["target_words"],
                "pages": book["pages"],
                "illustrations": book["illustrations"]
            }
            json.dump(book_data, f, indent=2)
        
        print(f"✅ Created: {title}")
        print(f"   Saved to: {filename}")
    
    print(f"\n📚 Series saved to: {output_dir}/")
    print()


def create_consonant_blends_book():
    """Create books for consonant blends."""
    print("=" * 60)
    print("ADVANCED EXAMPLE 2: Consonant Blends")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    content_gen = PhonicsContentGenerator(config.person, config.model)
    book_builder = PhonicsBookBuilder(content_gen)
    
    blends = [
        ("bl blend", ["blue", "black", "block", "blanket"]),
        ("st blend", ["star", "stop", "stick", "step"]),
        ("tr blend", ["tree", "truck", "train", "track"]),
    ]
    
    for concept, words in blends:
        title = f"Let's Blend: {concept.upper()}"
        book = book_builder.create_book(
            title=title,
            phonics_concept=concept,
            target_words=words,
            num_pages=6
        )
        
        print(f"Book: {title}")
        print(f"Words: {', '.join(words)}")
        print(f"Pages created: {len(book['pages'])}")
        print()


def create_custom_character_book():
    """Create a book with custom character configuration."""
    print("=" * 60)
    print("ADVANCED EXAMPLE 3: Custom Character")
    print("=" * 60)
    print()
    
    # Create custom person configuration
    custom_person = PersonConfig(
        name="Sophia",
        description="A curious 5-year-old with curly red hair, green eyes, and freckles, who loves dinosaurs",
        age_range="5-6 years old"
    )
    
    model_config = ModelConfig.from_env()
    config = BookConfig(
        person=custom_person,
        model=model_config,
        output_dir="generated_books/custom"
    )
    
    content_gen = PhonicsContentGenerator(config.person, config.model)
    book_builder = PhonicsBookBuilder(content_gen)
    vlim = VLIMCustomizer(config.person, config.model)
    
    # Create a dinosaur-themed phonics book
    book = book_builder.create_book(
        title=f"{custom_person.name}'s Dinosaur Adventure",
        phonics_concept="short i",
        target_words=["dig", "big", "pit", "sit"],
        num_pages=6
    )
    
    print(f"Character: {custom_person.name}")
    print(f"Description: {custom_person.description}")
    print(f"Book: {book['title']}")
    print()
    
    # Generate special prompts
    print("Sample image prompts for this character:")
    for word in book['target_words'][:3]:
        prompt = vlim.generate_image_prompt(
            "short i",
            word,
            f"Finding a {word} dinosaur fossil"
        )
        print(f"\nWord: {word}")
        print(f"Prompt: {prompt[:200]}...")
    print()


def create_word_family_series():
    """Create books for word families."""
    print("=" * 60)
    print("ADVANCED EXAMPLE 4: Word Families")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    content_gen = PhonicsContentGenerator(config.person, config.model)
    book_builder = PhonicsBookBuilder(content_gen)
    
    word_families = [
        ("-at family", ["cat", "bat", "mat", "hat", "rat", "sat"]),
        ("-an family", ["can", "man", "pan", "ran", "fan", "tan"]),
        ("-ig family", ["big", "dig", "pig", "wig", "fig", "jig"]),
        ("-op family", ["hop", "mop", "pop", "top", "cop", "shop"]),
    ]
    
    output_dir = Path(config.output_dir) / "word_families"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    series_summary = []
    
    for family, words in word_families:
        title = f"The {family} Family"
        book = book_builder.create_book(
            title=title,
            phonics_concept=family,
            target_words=words,
            num_pages=8
        )
        
        series_summary.append({
            "title": title,
            "family": family,
            "words": words,
            "pages": len(book['pages'])
        })
        
        print(f"✅ {title}: {', '.join(words)}")
    
    # Save series summary
    with open(output_dir / "series_summary.json", 'w') as f:
        json.dump(series_summary, f, indent=2)
    
    print(f"\n📚 Word families series summary saved to: {output_dir}/series_summary.json")
    print()


def create_digraph_books():
    """Create books for digraphs (ch, sh, th, wh, ph)."""
    print("=" * 60)
    print("ADVANCED EXAMPLE 5: Digraphs")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    content_gen = PhonicsContentGenerator(config.person, config.model)
    book_builder = PhonicsBookBuilder(content_gen)
    vlim = VLIMCustomizer(config.person, config.model)
    
    digraphs = [
        ("ch sound", ["chip", "chop", "chat", "chin"]),
        ("sh sound", ["ship", "shop", "shell", "fish"]),
        ("th sound", ["this", "that", "them", "path"]),
    ]
    
    for concept, words in digraphs:
        title = f"The {concept.upper()} Sound"
        book = book_builder.create_book(
            title=title,
            phonics_concept=concept,
            target_words=words,
            num_pages=6
        )
        
        print(f"Book: {title}")
        print(f"Concept: {concept}")
        
        # Show one sample prompt
        sample_prompt = vlim.generate_image_prompt(
            concept,
            words[0],
            f"Playing with a {words[0]}"
        )
        print(f"Sample prompt for '{words[0]}': {sample_prompt[:150]}...")
        print()


def main():
    """Run all advanced examples."""
    print("\n🎨 Advanced Phonics Book Examples\n")
    
    create_long_vowels_series()
    create_consonant_blends_book()
    create_custom_character_book()
    create_word_family_series()
    create_digraph_books()
    
    print("=" * 60)
    print("✨ All advanced examples completed!")
    print("=" * 60)
    print()
    print("You now have examples for:")
    print("  ✓ Long vowels with silent e")
    print("  ✓ Consonant blends")
    print("  ✓ Custom character creation")
    print("  ✓ Word families")
    print("  ✓ Digraphs")
    print()
    print("Check the generated_books/ directory for output files.")
    print()


if __name__ == "__main__":
    main()
