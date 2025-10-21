"""
Configuration utility for LinkedIn Article Generation System
Loads environment variables and provides configuration defaults
"""

import os
from dotenv import load_dotenv
from typing import Optional


class Config:
    """Configuration class for the LinkedIn Article Generation System"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # OpenAI API Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        # Creative model settings (for image generation)
        self.openai_creative_model = os.getenv("OPENAI_CREATIVE_MODEL", "gpt-4-turbo-preview")
        self.openai_creative_temperature = float(os.getenv("OPENAI_CREATIVE_TEMPERATURE", "0.9"))
        
        # Output settings
        self.default_output_dir = os.getenv("DEFAULT_OUTPUT_DIR", "output")
        self.max_revisions = int(os.getenv("MAX_REVISIONS", "3"))
        
        # Export settings
        self.export_word_documents = os.getenv("EXPORT_WORD_DOCUMENTS", "true").lower() == "true"
        self.export_jpeg_images = os.getenv("EXPORT_JPEG_IMAGES", "true").lower() == "true"
        self.create_placeholder_images = os.getenv("CREATE_PLACEHOLDER_IMAGES", "true").lower() == "true"
    
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if not self.openai_api_key or self.openai_api_key == "your-openai-api-key-here":
            return False
        return True
    
    def get_api_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        return self.openai_api_key
    
    def get_model_config(self) -> dict:
        """Get model configuration"""
        return {
            "model": self.openai_model,
            "temperature": self.openai_temperature
        }
    
    def get_creative_model_config(self) -> dict:
        """Get creative model configuration"""
        return {
            "model": self.openai_creative_model,
            "temperature": self.openai_creative_temperature
        }
    
    def get_export_config(self) -> dict:
        """Get export configuration"""
        return {
            "export_word_documents": self.export_word_documents,
            "export_jpeg_images": self.export_jpeg_images,
            "create_placeholder_images": self.create_placeholder_images,
            "default_output_dir": self.default_output_dir
        }
    
    def get_workflow_config(self) -> dict:
        """Get workflow configuration"""
        return {
            "max_revisions": self.max_revisions
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


def validate_config() -> bool:
    """Validate the global configuration"""
    return config.validate()


def print_config_status():
    """Print configuration status"""
    print("Configuration Status:")
    print("=" * 30)
    
    # API Key status
    if config.openai_api_key and config.openai_api_key != "your-openai-api-key-here":
        print("✅ OpenAI API Key: Set")
    else:
        print("❌ OpenAI API Key: Not set")
        print("   Please set OPENAI_API_KEY in .env file")
    
    # Model settings
    print(f"📝 Default Model: {config.openai_model}")
    print(f"🎨 Creative Model: {config.openai_creative_model}")
    print(f"🌡️  Temperature: {config.openai_temperature}")
    print(f"🎨 Creative Temperature: {config.openai_creative_temperature}")
    
    # Export settings
    print(f"📄 Export Word Documents: {config.export_word_documents}")
    print(f"🖼️  Export JPEG Images: {config.export_jpeg_images}")
    print(f"📁 Default Output Directory: {config.default_output_dir}")
    print(f"🔄 Max Revisions: {config.max_revisions}")
    
    print("=" * 30)
