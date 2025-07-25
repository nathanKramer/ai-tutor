from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import openai
import anthropic
import json
from config import Config
from tools import ToolRegistry, process_tool_calls


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: Config, ui=None):
        self.config = config
        self.client = None
        self.tool_registry = ToolRegistry()
        self.ui = ui  # Terminal interface for showing tool feedback
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the AI provider client"""
        pass
    
    @abstractmethod
    def _make_api_call(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Make the actual API call and return the response text"""
        pass
    
    @abstractmethod
    def _supports_tools(self) -> bool:
        """Check if this provider supports tool calls"""
        pass
    
    @abstractmethod
    def _get_provider_name(self) -> str:
        """Get the provider name for error messages"""
        pass
    
    @abstractmethod
    def _handle_auth_error(self) -> str:
        """Handle authentication errors with provider-specific message"""
        pass
    
    def is_available(self) -> bool:
        """Check if the provider is available"""
        return self.client is not None
    
    def _show_tool_feedback(self, tool_name: str, arguments: dict):
        """Show user-visible feedback about tool execution"""
        if self.ui:
            if tool_name == "read_file":
                file_path = arguments.get("file_path", "unknown")
                max_lines = arguments.get("max_lines")
                if max_lines:
                    self.ui.show_info(f"🔍 Reading first {max_lines} lines of {file_path}...")
                else:
                    self.ui.show_info(f"🔍 Reading {file_path}...")
            elif tool_name == "list_files":
                directory = arguments.get("directory", ".")
                pattern = arguments.get("pattern", "*")
                self.ui.show_info(f"📁 Listing files in {directory} (pattern: {pattern})...")
            elif tool_name == "get_file_info":
                file_path = arguments.get("file_path", "unknown")
                self.ui.show_info(f"ℹ️  Getting info for {file_path}...")
    
    def get_response(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """
        Get response from the AI provider
        
        Args:
            messages: List of conversation messages
            system_prompt: System prompt for the AI
            
        Returns:
            AI response text
        """
        if not self.is_available():
            return f"{self._get_provider_name()} client not available. Please check your API key."
        
        try:
            return self._make_api_call(messages, system_prompt)
            
        except Exception as e:
            # Handle specific error types
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                return self._handle_auth_error()
            elif "rate limit" in str(e).lower():
                return "I'm getting rate limited. Please wait a moment before trying again."
            else:
                return f"{self._get_provider_name()} error: {str(e)}"


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        api_key = self.config.get_api_key("openai")
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def _make_api_call(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Make OpenAI API call with tool support"""
        # Prepare messages for OpenAI format (system message first)
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend(messages)
        
        model = self.config.get_model_for_provider("openai")
        
        # Prepare API call parameters
        call_params = {
            "model": model,
            "messages": api_messages,
            "max_tokens": self.config.get("max_tokens", 1000),
            "temperature": self.config.get("temperature", 0.7)
        }
        
        # Add tool definitions if supported
        if self._supports_tools():
            call_params["tools"] = self.tool_registry.get_tool_definitions()
            call_params["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**call_params)
        message = response.choices[0].message
        
        # Handle tool calls
        if message.tool_calls:
            # Show tool execution feedback to user
            for tc in message.tool_calls:
                try:
                    arguments = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                    self._show_tool_feedback(tc.function.name, arguments)
                except:
                    pass  # Don't break if feedback fails
            
            # Process tool calls
            tool_results = process_tool_calls(
                [{"id": tc.id, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} 
                 for tc in message.tool_calls],
                self.tool_registry
            )
            
            # Add tool call results to conversation and get final response
            api_messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in message.tool_calls]
            })
            
            for result in tool_results:
                api_messages.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["output"]
                })
            
            # Get final response
            final_response = self.client.chat.completions.create(
                model=model,
                messages=api_messages,
                max_tokens=self.config.get("max_tokens", 1000),
                temperature=self.config.get("temperature", 0.7)
            )
            
            return final_response.choices[0].message.content.strip()
        
        return message.content.strip() if message.content else ""
    
    def _supports_tools(self) -> bool:
        """OpenAI supports tool calls"""
        return True
    
    def _get_provider_name(self) -> str:
        return "OpenAI"
    
    def _handle_auth_error(self) -> str:
        return "I need a valid OpenAI API key. Please check your OPENAI_API_KEY environment variable."


class ClaudeProvider(AIProvider):
    """Claude provider implementation"""
    
    def _initialize_client(self):
        """Initialize Claude client"""
        api_key = self.config.get_api_key("claude")
        if api_key:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Claude client: {e}")
    
    def _make_api_call(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Make Claude API call with tool support"""
        model = self.config.get_model_for_provider("claude")
        
        # Prepare API call parameters
        call_params = {
            "model": model,
            "max_tokens": self.config.get("max_tokens", 1000),
            "temperature": self.config.get("temperature", 0.7),
            "system": system_prompt,
            "messages": messages
        }
        
        # Add tool definitions if supported
        if self._supports_tools():
            # Convert tool definitions to Claude format
            claude_tools = []
            for tool_def in self.tool_registry.get_tool_definitions():
                claude_tools.append({
                    "name": tool_def["function"]["name"],
                    "description": tool_def["function"]["description"],
                    "input_schema": tool_def["function"]["parameters"]
                })
            call_params["tools"] = claude_tools
        
        response = self.client.messages.create(**call_params)
        
        # Handle tool calls
        if any(block.type == "tool_use" for block in response.content):
            # Process tool calls
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            
            # Show tool execution feedback to user
            for tool_call in tool_calls:
                self._show_tool_feedback(tool_call.name, tool_call.input)
            
            tool_results = []
            
            for tool_call in tool_calls:
                result = self.tool_registry.execute_tool(tool_call.name, tool_call.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result
                })
            
            # Add tool results to conversation and get final response
            messages_with_tools = messages + [
                {
                    "role": "assistant",
                    "content": response.content
                },
                {
                    "role": "user", 
                    "content": tool_results
                }
            ]
            
            # Get final response
            final_response = self.client.messages.create(
                model=model,
                max_tokens=self.config.get("max_tokens", 1000),
                temperature=self.config.get("temperature", 0.7),
                system=system_prompt,
                messages=messages_with_tools
            )
            
            return final_response.content[0].text.strip()
        
        # Extract text from response
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content += block.text
        
        return text_content.strip()
    
    def _supports_tools(self) -> bool:
        """Claude supports tool calls"""
        return True
    
    def _get_provider_name(self) -> str:
        return "Claude"
    
    def _handle_auth_error(self) -> str:
        return "I need a valid Anthropic API key. Please check your ANTHROPIC_API_KEY environment variable."


class ProviderFactory:
    """Factory for creating AI providers"""
    
    @staticmethod
    def create_provider(provider_name: str, config: Config, ui=None) -> Optional[AIProvider]:
        """Create a provider instance"""
        if provider_name == "openai":
            return OpenAIProvider(config, ui)
        elif provider_name == "claude":
            return ClaudeProvider(config, ui)
        else:
            return None
    
    @staticmethod
    def get_available_providers(config: Config) -> List[str]:
        """Get list of available providers"""
        available = []
        
        for provider_name in ["openai", "claude"]:
            provider = ProviderFactory.create_provider(provider_name, config, ui=None)
            if provider and provider.is_available():
                available.append(provider_name)
        
        return available