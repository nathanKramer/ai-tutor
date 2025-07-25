from typing import Any, Dict, List, Optional, Union
from enum import Enum
from core.interfaces import LoggerInterface


class ValidationError(Exception):
    """Configuration validation error"""
    pass


class ValidationType(Enum):
    """Types of validation"""
    TYPE = "type"
    RANGE = "range"
    CHOICE = "choice"
    REGEX = "regex"
    CUSTOM = "custom"


class ValidationRule:
    """Represents a validation rule for a configuration value"""
    
    def __init__(self, validation_type: ValidationType, constraint: Any, 
                 message: Optional[str] = None, required: bool = True):
        self.validation_type = validation_type
        self.constraint = constraint
        self.message = message
        self.required = required
    
    def validate(self, value: Any, key: str) -> bool:
        """Validate a value against this rule"""
        if value is None and not self.required:
            return True
        
        if value is None and self.required:
            raise ValidationError(f"Required configuration key '{key}' is missing")
        
        try:
            if self.validation_type == ValidationType.TYPE:
                if not isinstance(value, self.constraint):
                    raise ValidationError(
                        self.message or f"Configuration '{key}' must be of type {self.constraint.__name__}"
                    )
            
            elif self.validation_type == ValidationType.RANGE:
                min_val, max_val = self.constraint
                if not (min_val <= value <= max_val):
                    raise ValidationError(
                        self.message or f"Configuration '{key}' must be between {min_val} and {max_val}"
                    )
            
            elif self.validation_type == ValidationType.CHOICE:
                if value not in self.constraint:
                    raise ValidationError(
                        self.message or f"Configuration '{key}' must be one of: {', '.join(map(str, self.constraint))}"
                    )
            
            elif self.validation_type == ValidationType.REGEX:
                import re
                if not re.match(self.constraint, str(value)):
                    raise ValidationError(
                        self.message or f"Configuration '{key}' does not match required pattern"
                    )
            
            elif self.validation_type == ValidationType.CUSTOM:
                if not self.constraint(value):
                    raise ValidationError(
                        self.message or f"Configuration '{key}' failed custom validation"
                    )
            
            return True
        
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Validation error for '{key}': {str(e)}")


class ConfigValidator:
    """Configuration validator with rules"""
    
    def __init__(self, logger: Optional[LoggerInterface] = None):
        self.logger = logger
        self.rules: Dict[str, List[ValidationRule]] = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules for AI Tutor configuration"""
        
        # AI Provider validation
        self.add_rule("ai_provider", ValidationRule(
            ValidationType.CHOICE, 
            ["openai", "claude"],
            "AI provider must be either 'openai' or 'claude'"
        ))
        
        # Max tokens validation
        self.add_rule("max_tokens", ValidationRule(
            ValidationType.TYPE, int,
            "Max tokens must be an integer"
        ))
        self.add_rule("max_tokens", ValidationRule(
            ValidationType.RANGE, (1, 8192),
            "Max tokens must be between 1 and 8192"
        ))
        
        # Temperature validation
        self.add_rule("temperature", ValidationRule(
            ValidationType.TYPE, (int, float),
            "Temperature must be a number"
        ))
        self.add_rule("temperature", ValidationRule(
            ValidationType.RANGE, (0.0, 2.0),
            "Temperature must be between 0.0 and 2.0"
        ))
        
        # Conversation history limit
        self.add_rule("conversation_history_limit", ValidationRule(
            ValidationType.TYPE, int,
            "Conversation history limit must be an integer"
        ))
        self.add_rule("conversation_history_limit", ValidationRule(
            ValidationType.RANGE, (1, 100),
            "Conversation history limit must be between 1 and 100"
        ))
        
        # Models validation
        self.add_rule("models", ValidationRule(
            ValidationType.TYPE, dict,
            "Models configuration must be a dictionary"
        ))
        
        # Individual model validation
        self.add_rule("models.openai", ValidationRule(
            ValidationType.TYPE, str,
            "OpenAI model must be a string",
            required=False
        ))
        self.add_rule("models.claude", ValidationRule(
            ValidationType.TYPE, str,
            "Claude model must be a string",
            required=False
        ))
        
        # Custom validation for model names
        self.add_rule("models.openai", ValidationRule(
            ValidationType.CUSTOM,
            lambda x: x.startswith("gpt-") if x else True,
            "OpenAI model name should start with 'gpt-'",
            required=False
        ))
    
    def add_rule(self, key: str, rule: ValidationRule):
        """Add a validation rule for a configuration key"""
        if key not in self.rules:
            self.rules[key] = []
        self.rules[key].append(rule)
    
    def remove_rule(self, key: str):
        """Remove all validation rules for a key"""
        if key in self.rules:
            del self.rules[key]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate entire configuration"""
        errors = []
        
        for key, rules in self.rules.items():
            try:
                value = self._get_nested_value(config, key)
                for rule in rules:
                    rule.validate(value, key)
            except ValidationError as e:
                errors.append(str(e))
            except Exception as e:
                errors.append(f"Unexpected validation error for '{key}': {str(e)}")
        
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            if self.logger:
                self.logger.error(error_message)
            raise ValidationError(error_message)
        
        if self.logger:
            self.logger.info("Configuration validation passed")
        
        return True
    
    def validate_key(self, config: Dict[str, Any], key: str) -> bool:
        """Validate a specific configuration key"""
        if key not in self.rules:
            return True  # No rules defined, consider valid
        
        try:
            value = self._get_nested_value(config, key)
            for rule in self.rules[key]:
                rule.validate(value, key)
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Unexpected validation error for '{key}': {str(e)}")
    
    def _get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """Get value from nested configuration using dot notation"""
        keys = key.split('.')
        value = config
        
        try:
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return None
            return value
        except (KeyError, TypeError):
            return None
    
    def get_validation_summary(self) -> Dict[str, List[str]]:
        """Get a summary of all validation rules"""
        summary = {}
        
        for key, rules in self.rules.items():
            rule_descriptions = []
            for rule in rules:
                if rule.validation_type == ValidationType.TYPE:
                    if isinstance(rule.constraint, tuple):
                        types = " or ".join(t.__name__ for t in rule.constraint)
                    else:
                        types = rule.constraint.__name__
                    rule_descriptions.append(f"Must be of type: {types}")
                elif rule.validation_type == ValidationType.RANGE:
                    min_val, max_val = rule.constraint
                    rule_descriptions.append(f"Must be between {min_val} and {max_val}")
                elif rule.validation_type == ValidationType.CHOICE:
                    choices = ", ".join(map(str, rule.constraint))
                    rule_descriptions.append(f"Must be one of: {choices}")
                elif rule.validation_type == ValidationType.REGEX:
                    rule_descriptions.append(f"Must match pattern: {rule.constraint}")
                elif rule.validation_type == ValidationType.CUSTOM:
                    rule_descriptions.append("Must pass custom validation")
                
                if not rule.required:
                    rule_descriptions[-1] += " (optional)"
            
            summary[key] = rule_descriptions
        
        return summary


# Global validator instance
_validator: Optional[ConfigValidator] = None


def get_config_validator() -> ConfigValidator:
    """Get the global configuration validator"""
    global _validator
    if _validator is None:
        _validator = ConfigValidator()
    return _validator


def set_config_validator(validator: ConfigValidator):
    """Set the global configuration validator"""
    global _validator
    _validator = validator


def validate_config(config: Dict[str, Any]) -> bool:
    """Convenience function to validate configuration using global validator"""
    return get_config_validator().validate_config(config)