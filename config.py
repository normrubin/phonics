#!/usr/bin/env python3
"""
Configuration manager for Phonics Book Generator

This module handles loading and accessing configuration settings
from config.json, and provides validation utilities for tokens
and trigger words.
"""

import json
import re
from json import JSONDecodeError
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for the phonics book generator"""

    def __init__(self, config_path: str = "config.json"):
        """
        Load configuration from JSON file

        Args:
            config_path: Path to the config.json file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please create a config.json file in the project root."
            )

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.config_path}: {e}") from e

    def get(self, key: str, default=None) -> Any:
        """
        Get a configuration value by key

        Args:
            key: Dot-separated key path (e.g., 'directories.photo_images')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    # Typed helper accessors to satisfy type-checkers and add resilience
    def get_str(self, key: str, default: str) -> str:
        """Return a string config value, or default if missing/invalid."""
        val = self.get(key, default)
        if isinstance(val, str):
            return val
        # Accept Path-like values just in case
        if isinstance(val, Path):
            return str(val)
        try:
            return str(val) if val is not None else default
        except Exception:
            return default

    def get_int(self, key: str, default: int) -> int:
        """Return an int config value, or default if missing/invalid."""
        val = self.get(key, default)
        try:
            return int(val)
        except Exception:
            return default

    @property
    def photo_images_dir(self) -> Path:
        """Get the unified photos directory as a Path object"""
        path_str = self.get_str("directories.photo_images", "./photos")
        return Path(path_str)

    @property
    def output_dir(self) -> Path:
        """Get the output directory as a Path object"""
        path_str = self.get_str("directories.output", "./output")
        return Path(path_str)

    @property
    def target_size(self) -> int:
        """Get the target image size"""
        return self.get_int("image_settings.target_size", 1024)

    @property
    def image_format(self) -> str:
        """Get the target image format"""
        return self.get_str("image_settings.format", "JPEG")

    @property
    def image_quality(self) -> int:
        """Get the image quality setting"""
        return self.get_int("image_settings.quality", 95)

    @property
    def base_model(self) -> str:
        """Get the base model name"""
        return self.get_str("model_settings.base_model", "flux.1-schnell")

    @property
    def training_method(self) -> str:
        """Get the training method"""
        return self.get_str("model_settings.training_method", "LoRA")

    @property
    def trigger_word(self) -> str:
        """Get the trigger word for model training"""
        return self.get_str("model_settings.trigger_word", "")

    @property
    def flux_training_config_path(self) -> Path:
        """Get the path to the FLUX training config YAML file"""
        return self.output_dir / "flux_lora" / "flux_training_config.yaml"

    def ensure_directories(self):
        """Create all configured directories if they don't exist"""
        self.photo_images_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print("✓ Directories ensured:")
        print(f"  - Photos: {self.photo_images_dir}")
        print(f"  - Output: {self.output_dir}")

    def update_trigger_word(self, new_trigger: str) -> bool:
        """
        Update the trigger word in config.json

        Args:
            new_trigger: The new trigger word to set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if "model_settings" not in self.config:
                self.config["model_settings"] = {}
            self.config["model_settings"]["trigger_word"] = new_trigger

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)

            print(f"✓ Updated config.json with trigger_word: {new_trigger}")
            return True
        except Exception as e:
            print(f"ERROR: Could not update config.json: {e}")
            return False


# Validation utilities
def validate_hf_token(token: str) -> bool:
    """
    Validate a Hugging Face token via the API

    Args:
        token: The HF token to validate

    Returns:
        bool: True if token is valid, False otherwise
    """
    if not token or not token.startswith("hf_"):
        return False

    try:
        from huggingface_hub import whoami  # type: ignore

        whoami(token=token)
        return True
    except Exception:
        return False


def validate_trigger_word(trigger: str) -> bool:
    """
    Validate a trigger word format

    Args:
        trigger: The trigger word to validate

    Returns:
        bool: True if valid format (alphanumeric + underscores only)
    """
    if not trigger:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_]+$", trigger))


def read_env_token(env_file: str = "ENV") -> str:
    """
    Read HF_TOKEN from ENV file

    Args:
        env_file: Path to ENV file

    Returns:
        str: The token, or empty string if not found
    """
    env_path = Path(env_file)
    if not env_path.exists():
        return ""

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("HF_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    if token and token != "your_huggingface_token_here":
                        return token
    except Exception:
        pass

    return ""


def write_env_token(token: str, env_file: str = "ENV") -> bool:
    """
    Write HF_TOKEN to ENV file

    Args:
        token: The token to write
        env_file: Path to ENV file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from datetime import datetime

        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        content = f"""# Hugging Face Token
# Retrieved interactively on {timestamp}
HF_TOKEN={token}
"""
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"ERROR: Could not write ENV file: {e}")
        return False


# Convenience function to get config instance
def get_config(config_path: str = "config.json") -> Config:
    """
    Get a Config instance

    Args:
        config_path: Path to config.json file

    Returns:
        Config instance
    """
    return Config(config_path)


if __name__ == "__main__":
    # Test the configuration
    config = get_config()

    print("Configuration loaded successfully!")
    print("\nDirectories:")
    print(f"  Photos: {config.photo_images_dir}")
    print(f"  Output: {config.output_dir}")

    print("\nImage Settings:")
    print(f"  Target size: {config.target_size}x{config.target_size}")
    print(f"  Format: {config.image_format}")
    print(f"  Quality: {config.image_quality}")

    print("\nModel Settings:")
    print(f"  Base model: {config.base_model}")
    print(f"  Training method: {config.training_method}")
    print(f"  Trigger word: {config.trigger_word}")

    print("\nCreating directories...")
    config.ensure_directories()
