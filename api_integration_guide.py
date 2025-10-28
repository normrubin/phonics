"""
API Integration Guide and Testing Script.
This script demonstrates how to use the system with actual API keys.
"""
from config import BookConfig
from vlim_customizer import VLIMCustomizer, ImageGenerator
from phonics_generator import PhonicsContentGenerator, PhonicsBookBuilder
import os


def check_api_configuration():
    """Check which API services are configured."""
    print("=" * 60)
    print("API Configuration Check")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    
    openai_configured = bool(config.model.openai_api_key)
    anthropic_configured = bool(config.model.anthropic_api_key)
    
    print(f"OpenAI API: {'✅ Configured' if openai_configured else '❌ Not configured'}")
    print(f"Anthropic API: {'✅ Configured' if anthropic_configured else '❌ Not configured'}")
    print()
    
    if not openai_configured and not anthropic_configured:
        print("⚠️  No API keys configured.")
        print()
        print("To use AI features, add your API keys to .env:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your API keys:")
        print("     OPENAI_API_KEY=your_key_here")
        print("     ANTHROPIC_API_KEY=your_key_here")
        print()
        return False
    
    return True


def test_text_generation():
    """Test text generation with configured API."""
    print("=" * 60)
    print("Text Generation Test")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    
    if not config.model.openai_api_key and not config.model.anthropic_api_key:
        print("⚠️  Skipping - No API keys configured")
        print()
        return
    
    content_gen = PhonicsContentGenerator(config.person, config.model)
    
    print("Generating a short phonics story...")
    print(f"Concept: short a")
    print(f"Words: cat, hat, mat")
    print()
    
    lesson = content_gen.generate_phonics_story(
        phonics_concept="short a",
        target_words=["cat", "hat", "mat"],
        num_pages=4
    )
    
    print("Generated Story:")
    print("-" * 60)
    print(lesson.story_text)
    print("-" * 60)
    print()
    
    print("Illustration Descriptions:")
    for i, desc in enumerate(lesson.illustration_descriptions, 1):
        print(f"  {i}. {desc}")
    print()


def test_image_generation():
    """Test image generation with OpenAI API."""
    print("=" * 60)
    print("Image Generation Test")
    print("=" * 60)
    print()
    
    config = BookConfig.from_env()
    
    if not config.model.openai_api_key:
        print("⚠️  Skipping - OpenAI API key not configured")
        print("   Set OPENAI_API_KEY in .env to test image generation")
        print()
        return
    
    vlim = VLIMCustomizer(config.person, config.model)
    image_gen = ImageGenerator(config.model)
    
    # Generate a simple test prompt
    prompt = vlim.generate_image_prompt(
        phonics_concept="short a",
        word="cat",
        context=f"{config.person.name} playing with a friendly cat"
    )
    
    print("Test Prompt:")
    print(prompt)
    print()
    
    print("Generating image (this may take 10-30 seconds)...")
    result = image_gen.generate_image(prompt)
    
    if result["status"] == "success":
        print("✅ Image generated successfully!")
        print(f"   URL: {result['url']}")
        if result.get('revised_prompt'):
            print(f"   Revised prompt: {result['revised_prompt'][:100]}...")
    else:
        print(f"❌ Image generation failed: {result.get('message', 'Unknown error')}")
    print()


def demonstrate_customization_options():
    """Demonstrate different customization options."""
    print("=" * 60)
    print("Customization Options")
    print("=" * 60)
    print()
    
    # Show how to customize via environment
    print("Option 1: Environment Variables (.env file)")
    print("-" * 60)
    print("""
# Add these to your .env file:
PERSON_NAME=Your Child's Name
PERSON_DESCRIPTION=A cheerful 5-year-old with blonde hair
PERSON_AGE_RANGE=5-6 years old
""")
    
    # Show how to customize in code
    print("Option 2: Programmatic Customization")
    print("-" * 60)
    print("""
from config import PersonConfig, ModelConfig, BookConfig

# Create custom configuration
person = PersonConfig(
    name="Emma",
    description="A brave adventurer with brown hair and glasses",
    age_range="6-7 years old"
)

config = BookConfig(
    person=person,
    model=ModelConfig.from_env(),
    output_dir="emma_books"
)

# Use the custom config
vlim = VLIMCustomizer(config.person, config.model)
""")
    print()


def show_usage_tips():
    """Show tips for getting the best results."""
    print("=" * 60)
    print("Tips for Best Results")
    print("=" * 60)
    print()
    
    tips = [
        ("Be Specific", "Include detailed physical descriptions for consistent character appearance"),
        ("Use Simple Words", "Choose age-appropriate target words that kids encounter daily"),
        ("Start Simple", "Begin with basic phonics patterns like short vowels"),
        ("Review Prompts", "Check generated prompts before creating images - adjust if needed"),
        ("Iterate", "Generate multiple versions and pick the best ones"),
        ("Combine Tools", "Use the text generator for stories, then customize prompts as needed"),
        ("Save Work", "Keep track of good prompts and successful configurations"),
        ("Test First", "Run examples.py without API keys to understand the workflow"),
    ]
    
    for i, (title, description) in enumerate(tips, 1):
        print(f"{i}. {title}")
        print(f"   {description}")
        print()


def main():
    """Main function to run API integration tests."""
    print("\n🔧 API Integration Guide\n")
    
    # Check configuration
    apis_configured = check_api_configuration()
    
    # Show customization options
    demonstrate_customization_options()
    
    # Show usage tips
    show_usage_tips()
    
    # Run tests if APIs are configured
    if apis_configured:
        print("=" * 60)
        print("Running API Tests")
        print("=" * 60)
        print()
        
        response = input("Do you want to test the API? This may use API credits. (y/n): ")
        if response.lower() == 'y':
            test_text_generation()
            test_image_generation()
        else:
            print("Skipping API tests.")
            print()
    
    print("=" * 60)
    print("✨ Integration Guide Complete")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Configure your API keys in .env if not already done")
    print("2. Run examples.py to see basic functionality")
    print("3. Run advanced_examples.py for more complex scenarios")
    print("4. Run this script again to test actual API integration")
    print()


if __name__ == "__main__":
    main()
