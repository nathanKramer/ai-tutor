import traceback
from typing import Type, Optional, Callable, Any
from core.interfaces import LoggerInterface


class AITutorError(Exception):
    """Base exception for AI Tutor application"""
    pass


class ConfigurationError(AITutorError):
    """Configuration-related errors"""
    pass


class ProviderError(AITutorError):
    """AI provider-related errors"""
    pass


class ToolError(AITutorError):
    """Tool execution errors"""
    pass


class APIError(AITutorError):
    """API-related errors"""
    pass


class ValidationError(AITutorError):
    """Input validation errors"""
    pass


class ErrorHandler:
    """Central error handling and recovery system"""
    
    def __init__(self, logger: Optional[LoggerInterface] = None):
        self.logger = logger
        self._error_handlers = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default error handlers"""
        self.register_handler(ConfigurationError, self._handle_config_error)
        self.register_handler(ProviderError, self._handle_provider_error)
        self.register_handler(ToolError, self._handle_tool_error)
        self.register_handler(APIError, self._handle_api_error)
        self.register_handler(ValidationError, self._handle_validation_error)
    
    def register_handler(self, error_type: Type[Exception], 
                        handler: Callable[[Exception], Optional[str]]):
        """Register a custom error handler"""
        self._error_handlers[error_type] = handler
    
    def handle_error(self, error: Exception, context: str = "") -> Optional[str]:
        """Handle an error and return user-friendly message"""
        error_type = type(error)
        
        # Log the error
        if self.logger:
            self.logger.error(f"Error in {context}: {error}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Try to find a specific handler
        for exc_type, handler in self._error_handlers.items():
            if isinstance(error, exc_type):
                return handler(error)
        
        # Fall back to generic handler
        return self._handle_generic_error(error)
    
    def _handle_config_error(self, error: ConfigurationError) -> str:
        """Handle configuration errors"""
        return f"Configuration error: {str(error)}. Please check your settings."
    
    def _handle_provider_error(self, error: ProviderError) -> str:
        """Handle AI provider errors"""
        return f"AI provider error: {str(error)}. Please check your API keys and try again."
    
    def _handle_tool_error(self, error: ToolError) -> str:
        """Handle tool execution errors"""
        return f"Tool error: {str(error)}. Please check the file path or parameters."
    
    def _handle_api_error(self, error: APIError) -> str:
        """Handle API errors"""
        error_msg = str(error).lower()
        
        if "rate limit" in error_msg:
            return "API rate limit exceeded. Please wait a moment before trying again."
        elif "authentication" in error_msg or "api key" in error_msg:
            return "Authentication failed. Please check your API key."
        elif "quota" in error_msg:
            return "API quota exceeded. Please check your account limits."
        else:
            return f"API error: {str(error)}. Please try again later."
    
    def _handle_validation_error(self, error: ValidationError) -> str:
        """Handle validation errors"""
        return f"Input validation error: {str(error)}"
    
    def _handle_generic_error(self, error: Exception) -> str:
        """Handle generic errors"""
        return f"An unexpected error occurred: {str(error)}"
    
    def safe_execute(self, func: Callable, *args, context: str = "", 
                    default_return: Any = None, **kwargs) -> Any:
        """Safely execute a function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = self.handle_error(e, context)
            if self.logger:
                self.logger.error(f"Safe execution failed in {context}: {error_msg}")
            return default_return


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def set_error_handler(handler: ErrorHandler):
    """Set the global error handler"""
    global _error_handler
    _error_handler = handler


def handle_error(error: Exception, context: str = "") -> Optional[str]:
    """Convenience function to handle errors using global handler"""
    return get_error_handler().handle_error(error, context)


def safe_execute(func: Callable, *args, context: str = "", 
                default_return: Any = None, **kwargs) -> Any:
    """Convenience function for safe execution using global handler"""
    return get_error_handler().safe_execute(func, *args, context=context, 
                                          default_return=default_return, **kwargs)