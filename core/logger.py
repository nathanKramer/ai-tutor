import logging
import sys
from typing import Optional
from pathlib import Path
from core.interfaces import LoggerInterface


class FileLogger(LoggerInterface):
    """File-based logger implementation"""
    
    def __init__(self, name: str = "ai_tutor", log_file: Optional[str] = None, 
                 level: int = logging.INFO, console_output: bool = True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add file handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Add console handler if requested
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def set_level(self, level: int) -> None:
        """Set logging level"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


class NoOpLogger(LoggerInterface):
    """No-operation logger for when logging is disabled"""
    
    def debug(self, message: str) -> None:
        pass
    
    def info(self, message: str) -> None:
        pass
    
    def warning(self, message: str) -> None:
        pass
    
    def error(self, message: str) -> None:
        pass


class StructuredLogger(LoggerInterface):
    """Structured logger that adds context to log messages"""
    
    def __init__(self, base_logger: LoggerInterface, context: dict = None):
        self.base_logger = base_logger
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Format message with context"""
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            return f"[{context_str}] {message}"
        return message
    
    def debug(self, message: str) -> None:
        self.base_logger.debug(self._format_message(message))
    
    def info(self, message: str) -> None:
        self.base_logger.info(self._format_message(message))
    
    def warning(self, message: str) -> None:
        self.base_logger.warning(self._format_message(message))
    
    def error(self, message: str) -> None:
        self.base_logger.error(self._format_message(message))
    
    def with_context(self, **context) -> 'StructuredLogger':
        """Create a new logger with additional context"""
        new_context = {**self.context, **context}
        return StructuredLogger(self.base_logger, new_context)


def create_logger(name: str = "ai_tutor", debug: bool = False, 
                 log_file: Optional[str] = None) -> LoggerInterface:
    """Factory function to create appropriate logger"""
    level = logging.DEBUG if debug else logging.INFO
    
    if log_file or debug:
        return FileLogger(name, log_file, level, console_output=debug)
    else:
        return NoOpLogger()