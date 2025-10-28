"""
Configuration module for phonics book generation.
"""
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class PersonConfig:
    """Configuration for person-specific customization."""
    name: str
    description: str
    age_range: str = "4-6 years old"
    
    @classmethod
    def from_env(cls) -> "PersonConfig":
        """Load person configuration from environment variables."""
        return cls(
            name=os.getenv("PERSON_NAME", "Alex"),
            description=os.getenv("PERSON_DESCRIPTION", "A happy child learning to read"),
            age_range=os.getenv("PERSON_AGE_RANGE", "4-6 years old")
        )


@dataclass
class ModelConfig:
    """Configuration for AI model settings."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    image_model: str = "dall-e-3"
    text_model: str = "gpt-4"
    
    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Load model configuration from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            image_model=os.getenv("IMAGE_MODEL", "dall-e-3"),
            text_model=os.getenv("TEXT_MODEL", "gpt-4")
        )


@dataclass
class BookConfig:
    """Configuration for phonics book generation."""
    person: PersonConfig
    model: ModelConfig
    output_dir: str = "generated_books"
    
    @classmethod
    def from_env(cls) -> "BookConfig":
        """Load complete configuration from environment variables."""
        return cls(
            person=PersonConfig.from_env(),
            model=ModelConfig.from_env(),
            output_dir=os.getenv("OUTPUT_DIR", "generated_books")
        )
