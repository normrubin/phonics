"""
Vision-Language Image Model (VLIM) customization for person-specific image generation.
This module handles the generation of images featuring a specific person.
"""
from typing import Optional, List
import os
from config import PersonConfig, ModelConfig


class VLIMCustomizer:
    """
    Customizes image generation prompts to consistently feature a specific person.
    """
    
    def __init__(self, person_config: PersonConfig, model_config: ModelConfig):
        """
        Initialize the VLIM customizer.
        
        Args:
            person_config: Configuration for the person to feature
            model_config: Configuration for AI models
        """
        self.person_config = person_config
        self.model_config = model_config
        self.base_person_prompt = self._create_base_person_prompt()
    
    def _create_base_person_prompt(self) -> str:
        """
        Create a consistent base prompt for the person.
        
        Returns:
            A prompt string describing the person consistently
        """
        return (
            f"The main character is {self.person_config.name}, "
            f"{self.person_config.description}. "
            f"The character is {self.person_config.age_range}. "
            "The style should be child-friendly, colorful, and engaging. "
            "Illustrations should be clear and simple for early readers."
        )
    
    def customize_prompt(self, scene_description: str) -> str:
        """
        Customize an image generation prompt to feature the specific person.
        
        Args:
            scene_description: Description of the scene to illustrate
            
        Returns:
            A complete prompt for image generation
        """
        return f"{self.base_person_prompt}\n\nScene: {scene_description}"
    
    def generate_image_prompt(
        self, 
        phonics_concept: str, 
        word: str, 
        context: str = ""
    ) -> str:
        """
        Generate an image prompt for a phonics concept.
        
        Args:
            phonics_concept: The phonics pattern being taught (e.g., "short a")
            word: The target word to illustrate (e.g., "cat")
            context: Optional additional context for the scene
            
        Returns:
            A complete image generation prompt
        """
        scene = f"{self.person_config.name} interacting with a {word}. "
        
        if context:
            scene += context + " "
        
        scene += (
            f"The illustration clearly shows the word '{word}' which demonstrates "
            f"the '{phonics_concept}' sound pattern."
        )
        
        return self.customize_prompt(scene)
    
    def generate_cover_prompt(self, book_title: str, theme: str = "") -> str:
        """
        Generate a prompt for a book cover image.
        
        Args:
            book_title: Title of the phonics book
            theme: Optional theme for the cover
            
        Returns:
            A complete cover image prompt
        """
        scene = (
            f"{self.person_config.name} on the cover of a phonics book titled '{book_title}'. "
        )
        
        if theme:
            scene += f"The theme is {theme}. "
        
        scene += (
            f"{self.person_config.name} looks excited and ready to learn. "
            "The cover should be colorful and inviting for young readers."
        )
        
        return self.customize_prompt(scene)


class ImageGenerator:
    """
    Handles actual image generation using AI services.
    """
    
    def __init__(self, model_config: ModelConfig):
        """
        Initialize the image generator.
        
        Args:
            model_config: Configuration for AI models
        """
        self.model_config = model_config
        self._setup_client()
    
    def _setup_client(self):
        """Set up the API client for image generation."""
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
    
    def generate_image(self, prompt: str, output_path: Optional[str] = None) -> dict:
        """
        Generate an image from a prompt.
        
        Args:
            prompt: The image generation prompt
            output_path: Optional path to save the image
            
        Returns:
            Dictionary with image URL and metadata
        """
        if not self.has_client:
            return {
                "status": "error",
                "message": "No API client configured",
                "prompt": prompt
            }
        
        try:
            response = self.client.images.generate(
                model=self.model_config.image_model,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            result = {
                "status": "success",
                "url": response.data[0].url,
                "prompt": prompt,
                "revised_prompt": getattr(response.data[0], 'revised_prompt', None)
            }
            
            # Optionally save the image
            if output_path:
                result["saved_path"] = output_path
                # Note: Actual download would require additional code
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "prompt": prompt
            }
