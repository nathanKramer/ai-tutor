import os
import sys
from typing import Dict, List, Optional
from pathlib import Path


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in normal Python environment
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class PromptManager:
    """Manages loading and combining system prompts from files"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(get_resource_path(prompts_dir))
        self._prompt_cache: Dict[str, str] = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """Load a single prompt from file"""
        if prompt_name in self._prompt_cache:
            return self._prompt_cache[prompt_name]
        
        prompt_path = self.prompts_dir / f"{prompt_name}.md"
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            self._prompt_cache[prompt_name] = content
            return content
        
        except Exception as e:
            raise RuntimeError(f"Failed to load prompt {prompt_name}: {e}")
    
    def combine_prompts(self, prompt_names: List[str], separator: str = "\n\n") -> str:
        """Combine multiple prompts into a single system prompt"""
        prompts = []
        
        for prompt_name in prompt_names:
            try:
                prompt_content = self.load_prompt(prompt_name)
                prompts.append(prompt_content)
            except Exception as e:
                print(f"Warning: Could not load prompt '{prompt_name}': {e}")
        
        return separator.join(prompts)
    
    def get_default_system_prompt(self) -> str:
        """Get the default combined system prompt"""
        default_prompts = [
            "socratic_tutor",
            "problem_progression", 
            "tool_usage"
        ]
        
        return self.combine_prompts(default_prompts)
    
    def get_simple_tutor_prompt(self) -> str:
        """Get the simple tutor prompt (more direct, less Socratic)"""
        simple_prompts = [
            "simple_tutor",
            "tool_usage"
        ]
        
        return self.combine_prompts(simple_prompts)
    
    def reload_prompts(self):
        """Clear cache and reload all prompts"""
        self._prompt_cache.clear()
    
    def list_available_prompts(self) -> List[str]:
        """List all available prompt files"""
        if not self.prompts_dir.exists():
            return []
        
        return [
            f.stem for f in self.prompts_dir.glob("*.md")
            if f.is_file()
        ]
    
    def create_custom_prompt(self, base_prompts: List[str], custom_additions: str) -> str:
        """Create a custom prompt by combining base prompts with additions"""
        base_prompt = self.combine_prompts(base_prompts)
        return f"{base_prompt}\n\n{custom_additions}"
