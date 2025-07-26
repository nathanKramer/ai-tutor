from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Protocol


class UIInterface(Protocol):
    """Interface for terminal/UI interactions"""
    
    def show_info(self, message: str) -> None:
        """Show an info message"""
        ...
    
    def show_error(self, message: str) -> None:
        """Show an error message"""
        ...
    
    def show_success(self, message: str) -> None:
        """Show a success message"""
        ...
    
    def get_user_input(self, prompt: str = "> ") -> str:
        """Get input from user"""
        ...


class ToolInterface(ABC):
    """Abstract interface for tools"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get tool name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get tool description"""
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get JSON schema for tool parameters"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def is_safe(self, **kwargs) -> bool:
        """Check if tool execution is safe with given parameters"""
        pass


class ConversationManagerInterface(ABC):
    """Interface for managing conversation history"""
    
    @abstractmethod
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history"""
        pass
    
    @abstractmethod
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent messages from conversation"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear conversation history"""
        pass
    
    @abstractmethod
    def get_summary(self) -> str:
        """Get conversation summary"""
        pass



class ProviderInterface(ABC):
    """Abstract interface for AI providers"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass
    
    @abstractmethod
    def get_response(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Get response from AI provider"""
        pass
    
    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if provider supports tool calls"""
        pass


class TutorInterface(ABC):
    """Abstract interface for AI tutors"""
    
    @abstractmethod
    def get_response(self, user_input: str, context: str = "") -> str:
        """Get tutor response to user input"""
        pass
    
    @abstractmethod
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to different AI provider"""
        pass
    
    @abstractmethod
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        pass
    
    @abstractmethod
    def set_system_prompt(self, prompt: str) -> None:
        """Update system prompt"""
        pass


class LoggerInterface(Protocol):
    """Interface for logging"""
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        ...
    
    def info(self, message: str) -> None:
        """Log info message"""
        ...
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        ...
    
    def error(self, message: str) -> None:
        """Log error message"""
        ...


class EventManagerInterface(ABC):
    """Interface for event management"""
    
    @abstractmethod
    def emit(self, event: str, **kwargs) -> None:
        """Emit an event"""
        pass
    
    @abstractmethod
    def subscribe(self, event: str, callback) -> None:
        """Subscribe to an event"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event: str, callback) -> None:
        """Unsubscribe from an event"""
        pass