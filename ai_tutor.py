import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from config import Config
from providers import ProviderFactory, AIProvider
from core.prompt_manager import PromptManager
from core.interfaces import TutorInterface

load_dotenv()

class AITutor(TutorInterface):
    def __init__(self, config: Optional[Config] = None, ui=None):
        self.config = config or Config()
        self.ui = ui  # Terminal interface for tool feedback
        self.conversation_history: List[Dict[str, str]] = []
        
        # Initialize prompt manager and load system prompt
        self.prompt_manager = PromptManager()
        self.system_prompt = self.prompt_manager.get_default_system_prompt()
        
        # Initialize current provider
        self.current_provider: Optional[AIProvider] = None
        self._init_provider()
    
    def _init_provider(self):
        """Initialize the current AI provider"""
        provider_name = self.config.get_current_provider()
        self.current_provider = ProviderFactory.create_provider(provider_name, self.config, self.ui)
        
        if not self.current_provider or not self.current_provider.is_available():
            # Try to find an available fallback provider
            available_providers = ProviderFactory.get_available_providers(self.config)
            if available_providers:
                fallback_provider = available_providers[0]
                print(f"Warning: {provider_name} not available, falling back to {fallback_provider}")
                self.config.set_provider(fallback_provider)
                self.current_provider = ProviderFactory.create_provider(fallback_provider, self.config, self.ui)
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different provider"""
        new_provider = ProviderFactory.create_provider(provider_name, self.config, self.ui)
        if new_provider and new_provider.is_available():
            self.current_provider = new_provider
            self.config.set_provider(provider_name)
            return True
        return False
    
    def get_response(self, user_input: str, context: str = "") -> str:
        """
        Get AI tutor response to user input
        
        Args:
            user_input: What the user said
            context: Additional context about current code/situation
            
        Returns:
            AI tutor's response
        """
        if not self.current_provider:
            return "No AI provider available. Please check your API keys."
        
        # Add context to the message if provided
        message_content = user_input
        if context:
            message_content = f"Context: {context}\n\nUser: {user_input}"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user", 
            "content": message_content
        })
        
        # Prepare recent conversation history
        history_limit = self.config.get("conversation_history_limit", 10)
        recent_history = self.conversation_history[-history_limit:]
        
        # Get response from current provider
        ai_response = self.current_provider.get_response(recent_history, self.system_prompt)
        
        # Add AI response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        return ai_response
    
    def get_simple_response(self, user_input: str, context: str = "") -> str:
        """
        Get AI tutor response using simple tutor prompt (non-Socratic)
        
        Args:
            user_input: What the user said
            context: Additional context about current code/situation
            
        Returns:
            AI tutor's response using simple tutor prompt
        """
        if not self.current_provider:
            return "No AI provider available. Please check your API keys."
        
        # Add context to the message if provided
        message_content = user_input
        if context:
            message_content = f"Context: {context}\n\nUser: {user_input}"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user", 
            "content": message_content
        })
        
        # Prepare recent conversation history
        history_limit = self.config.get("conversation_history_limit", 10)
        recent_history = self.conversation_history[-history_limit:]
        
        # Get simple tutor prompt
        simple_prompt = self.prompt_manager.get_simple_tutor_prompt()
        
        # Get response from current provider using simple prompt
        ai_response = self.current_provider.get_response(recent_history, simple_prompt)
        
        # Add AI response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        return ai_response
    
    def get_raw_response(self, user_input: str, context: str = "") -> str:
        """
        Get AI response using no system prompt (completely raw)
        
        Args:
            user_input: What the user said
            context: Additional context about current code/situation
            
        Returns:
            AI response with no system prompt constraints
        """
        if not self.current_provider:
            return "No AI provider available. Please check your API keys."
        
        # Add context to the message if provided
        message_content = user_input
        if context:
            message_content = f"Context: {context}\n\nUser: {user_input}"
        
        # Create a minimal conversation history with just this message
        # Don't add to the main conversation history to avoid contamination
        raw_history = [{
            "role": "user", 
            "content": message_content
        }]
        
        # Get response from current provider with empty system prompt
        ai_response = self.current_provider.get_response(raw_history, "")
        
        # Don't add to conversation history since this is a raw query
        # Users can use regular mode for conversation continuity
        
        return ai_response
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt"""
        self.system_prompt = prompt
    
    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversation"""
        if not self.conversation_history:
            return "No conversation yet."
        
        recent_messages = self.conversation_history[-4:]
        summary = "Recent conversation:\n"
        for msg in recent_messages:
            role = "You" if msg["role"] == "user" else "AI Tutor"
            summary += f"{role}: {msg['content'][:100]}...\n"
        
        return summary