import json
import os
from pathlib import Path
from typing import Any, Dict
from core.interfaces import ConfigManagerInterface


class JSONConfigManager(ConfigManagerInterface):
    """JSON file-based configuration manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config from {self.config_file}: {e}")
                self._config = {}
        else:
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the final key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the final value
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save configuration to persistent storage"""
        try:
            # Create directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Could not save config to {self.config_file}: {e}")
    
    def validate(self) -> bool:
        """Validate current configuration"""
        # Basic validation - check if required keys exist
        required_keys = [
            "ai_provider",
            "max_tokens", 
            "temperature"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                return False
        
        # Validate value ranges
        max_tokens = self.get("max_tokens")
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            return False
        
        temperature = self.get("temperature")
        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 2):
            return False
        
        ai_provider = self.get("ai_provider")
        if ai_provider not in ["openai", "claude"]:
            return False
        
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration with dictionary"""
        self._config.update(config_dict)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        defaults = {
            "ai_provider": "openai",
            "max_tokens": 1000,
            "temperature": 0.7,
            "conversation_history_limit": 10,
            "models": {
                "openai": "gpt-3.5-turbo",
                "claude": "claude-3-sonnet-20240229"
            }
        }
        self._config = defaults