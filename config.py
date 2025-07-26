import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from core.config_validator import validate_config, ValidationError

load_dotenv()

class Config:
    """Configuration management for AI Tutor"""
    
    DEFAULT_CONFIG = {
        "ai_provider": "openai",  # "openai" or "claude"
        "models": {
            "openai": "gpt-3.5-turbo",
            "claude": "claude-sonnet-4-20250514"
        },
        "max_tokens": 1000,
        "temperature": 0.7,
        "conversation_history_limit": 10,
        "role": "tutor"  # Default role: "tutor", "simple", or "short"
    }
    
    def __init__(self, config_file: str | None = None):
        if config_file is None:
            # Use XDG config directory standard
            config_dir = Path.home() / ".config" / "ai-tutor"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = str(config_dir / "tutor_config.json")
        else:
            self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        config = self.DEFAULT_CONFIG.copy()
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                # Merge with defaults
                config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Validate configuration
        try:
            validate_config(config)
        except ValidationError as e:
            print(f"Configuration validation failed: {e}")
            print("Using default configuration...")
            config = self.DEFAULT_CONFIG.copy()
        
        return config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Validate configuration before saving
            validate_config(self.config)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except ValidationError as e:
            print(f"Cannot save invalid configuration: {e}")
        except Exception as e:
            print(f"Warning: Could not save config file {self.config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for specified provider"""
        if provider == "openai":
            return os.getenv('OPENAI_API_KEY')
        elif provider == "claude":
            return os.getenv('ANTHROPIC_API_KEY')
        return None
    
    def get_current_provider(self) -> str:
        """Get current AI provider"""
        return self.get("ai_provider", "openai")
    
    def set_provider(self, provider: str):
        """Set AI provider"""
        if provider in ["openai", "claude"]:
            self.set("ai_provider", provider)
            self.save_config()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def get_model_for_provider(self, provider: str | None = None) -> str:
        """Get model name for specified provider"""
        if provider is None:
            provider = self.get_current_provider()
        
        models = self.get("models", {})
        return models.get(provider, self.DEFAULT_CONFIG["models"][provider])
    
    def get_role(self) -> str:
        """Get current role"""
        return self.get("role", "tutor")
    
    def set_role(self, role: str):
        """Set role and save to config"""
        if role in ["tutor", "simple", "short"]:
            self.set("role", role)
            self.save_config()
        else:
            raise ValueError(f"Unsupported role: {role}")
