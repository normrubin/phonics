"""
Phonics content generation module.
Generates text and illustration descriptions for phonics books.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from config import PersonConfig, ModelConfig


@dataclass
class PhonicsLesson:
    """Represents a phonics lesson with concept, words, and content."""
    concept: str  # e.g., "short a", "long e", "ch sound"
    target_words: List[str]  # Words demonstrating the concept
    story_text: str  # The story text
    illustration_descriptions: List[str]  # Descriptions for illustrations
    

class PhonicsContentGenerator:
    """
    Generates phonics book content including text and illustration descriptions.
    """
    
    def __init__(self, person_config: PersonConfig, model_config: ModelConfig):
        """
        Initialize the content generator.
        
        Args:
            person_config: Configuration for personalization
            model_config: Configuration for AI models
        """
        self.person_config = person_config
        self.model_config = model_config
        self._setup_client()
    
    def _setup_client(self):
        """Set up the API client for text generation."""
        if self.model_config.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.model_config.openai_api_key)
                self.has_client = True
            except ImportError:
                print("OpenAI package not installed. Install with: pip install openai")
                self.has_client = False
        else:
            print("No OpenAI API key configured. Set OPENAI_API_KEY environment variable.")
            self.has_client = False
    
    def generate_phonics_story(
        self, 
        phonics_concept: str, 
        target_words: List[str],
        num_pages: int = 8
    ) -> PhonicsLesson:
        """
        Generate a phonics story with text and illustration descriptions.
        
        Args:
            phonics_concept: The phonics pattern to teach (e.g., "short a")
            target_words: List of words to include that demonstrate the concept
            num_pages: Number of pages in the book
            
        Returns:
            A PhonicsLesson object with story and illustrations
        """
        if not self.has_client:
            # Return a template if no API available
            return self._generate_template_story(phonics_concept, target_words, num_pages)
        
        try:
            prompt = self._create_story_prompt(phonics_concept, target_words, num_pages)
            
            response = self.client.chat.completions.create(
                model=self.model_config.text_model,
                messages=[
                    {"role": "system", "content": "You are an expert in creating phonics books for early readers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_story_response(content, phonics_concept, target_words)
            
        except Exception as e:
            print(f"Error generating story: {e}")
            return self._generate_template_story(phonics_concept, target_words, num_pages)
    
    def _create_story_prompt(
        self, 
        phonics_concept: str, 
        target_words: List[str],
        num_pages: int
    ) -> str:
        """Create a prompt for story generation."""
        words_str = ", ".join(target_words)
        
        return f"""Create a {num_pages}-page phonics story for early readers that teaches the '{phonics_concept}' sound pattern.

Character: {self.person_config.name}, {self.person_config.description}

Requirements:
1. Use simple, repetitive sentences appropriate for {self.person_config.age_range}
2. Include these target words: {words_str}
3. Each page should have 1-2 short sentences
4. The story should be engaging and fun
5. Use the target words naturally in context

Format your response as:
PAGE 1:
[Text for page 1]
ILLUSTRATION: [Description of illustration for page 1]

PAGE 2:
[Text for page 2]
ILLUSTRATION: [Description of illustration for page 2]

... and so on for all {num_pages} pages.
"""
    
    def _parse_story_response(
        self, 
        response: str, 
        phonics_concept: str, 
        target_words: List[str]
    ) -> PhonicsLesson:
        """Parse the AI response into a PhonicsLesson."""
        pages = []
        illustrations = []
        
        # Simple parsing - split by PAGE markers
        lines = response.split('\n')
        current_text = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('PAGE'):
                if current_text:
                    pages.append(' '.join(current_text))
                    current_text = []
            elif line.startswith('ILLUSTRATION:'):
                illustrations.append(line.replace('ILLUSTRATION:', '').strip())
            elif line and not line.startswith('PAGE'):
                current_text.append(line)
        
        # Add last page if exists
        if current_text:
            pages.append(' '.join(current_text))
        
        story_text = '\n\n'.join(pages)
        
        return PhonicsLesson(
            concept=phonics_concept,
            target_words=target_words,
            story_text=story_text,
            illustration_descriptions=illustrations
        )
    
    def _generate_template_story(
        self, 
        phonics_concept: str, 
        target_words: List[str],
        num_pages: int
    ) -> PhonicsLesson:
        """Generate a simple template story when API is not available."""
        story_pages = []
        illustrations = []
        
        # Create a simple story template
        story_pages.append(f"{self.person_config.name} loves to learn!")
        illustrations.append(
            f"{self.person_config.name} sitting with a book, smiling excitedly"
        )
        
        for i, word in enumerate(target_words[:num_pages-2]):
            story_pages.append(f"{self.person_config.name} sees a {word}.")
            illustrations.append(
                f"{self.person_config.name} pointing at a {word} with joy"
            )
        
        story_pages.append(f"{self.person_config.name} learned new words!")
        illustrations.append(
            f"{self.person_config.name} holding a completed book proudly"
        )
        
        return PhonicsLesson(
            concept=phonics_concept,
            target_words=target_words,
            story_text='\n\n'.join(story_pages),
            illustration_descriptions=illustrations
        )
    
    def generate_illustration_description(
        self, 
        page_text: str, 
        phonics_concept: str,
        word_focus: Optional[str] = None
    ) -> str:
        """
        Generate a detailed illustration description for a page.
        
        Args:
            page_text: The text on the page
            phonics_concept: The phonics concept being taught
            word_focus: Optional specific word to focus on in the illustration
            
        Returns:
            A detailed description for the illustration
        """
        description = (
            f"Illustration showing {self.person_config.name} in a scene where: {page_text}. "
        )
        
        if word_focus:
            description += f"The illustration prominently features a {word_focus}. "
        
        description += (
            f"The style is colorful, child-friendly, and clearly demonstrates "
            f"the '{phonics_concept}' concept. "
            f"{self.person_config.name} appears {self.person_config.description}."
        )
        
        return description


class PhonicsBookBuilder:
    """
    Builds complete phonics books with text and illustrations.
    """
    
    def __init__(self, content_generator: PhonicsContentGenerator):
        """
        Initialize the book builder.
        
        Args:
            content_generator: The content generator to use
        """
        self.content_generator = content_generator
    
    def create_book(
        self, 
        title: str,
        phonics_concept: str, 
        target_words: List[str],
        num_pages: int = 8
    ) -> Dict:
        """
        Create a complete phonics book.
        
        Args:
            title: Book title
            phonics_concept: Phonics concept to teach
            target_words: Words to include
            num_pages: Number of pages
            
        Returns:
            Dictionary containing the complete book data
        """
        lesson = self.content_generator.generate_phonics_story(
            phonics_concept, 
            target_words, 
            num_pages
        )
        
        return {
            "title": title,
            "concept": phonics_concept,
            "target_words": target_words,
            "pages": self._split_into_pages(lesson.story_text),
            "illustrations": lesson.illustration_descriptions,
            "lesson": lesson
        }
    
    def _split_into_pages(self, story_text: str) -> List[str]:
        """Split story text into individual pages."""
        return [page.strip() for page in story_text.split('\n\n') if page.strip()]
