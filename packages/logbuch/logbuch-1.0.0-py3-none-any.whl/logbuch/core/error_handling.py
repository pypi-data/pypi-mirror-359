#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import sys
import traceback
import functools
from typing import Any, Callable, Dict, Optional, Type, Union
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from logbuch.core.logger import get_logger

console = Console()
logger = get_logger(__name__)


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LogbuchError(Exception):
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 user_message: str = None, suggestions: list = None):
        super().__init__(message)
        self.severity = severity
        self.user_message = user_message or message
        self.suggestions = suggestions or []
        self.timestamp = None


class DatabaseError(LogbuchError):
    def __init__(self, message: str, query: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.query = query


class ValidationError(LogbuchError):
    def __init__(self, message: str, field: str = None, value: Any = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value


class ConfigurationError(LogbuchError):
    pass


class IntegrationError(LogbuchError):
    def __init__(self, message: str, service: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.service = service


class PerformanceError(LogbuchError):
    def __init__(self, message: str, operation: str = None, duration: float = None, **kwargs):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.duration = duration


class ErrorHandler:
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
        self.max_history = 100
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        context = context or {}
        error_info = self._analyze_error(error, context)
        
        # Log the error
        self._log_error(error_info)
        
        # Track error frequency
        self._track_error(error_info)
        
        # Display user-friendly message
        self._display_error(error_info)
        
        # Return whether the application should continue
        return error_info['severity'] != ErrorSeverity.CRITICAL
    
    def _analyze_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'severity': ErrorSeverity.MEDIUM,
            'user_message': None,
            'suggestions': [],
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        # Handle specific error types
        if isinstance(error, LogbuchError):
            error_info.update({
                'severity': error.severity,
                'user_message': error.user_message,
                'suggestions': error.suggestions
            })
        
        elif isinstance(error, FileNotFoundError):
            error_info.update({
                'severity': ErrorSeverity.HIGH,
                'user_message': f"File not found: {error.filename}",
                'suggestions': [
                    "Check if the file path is correct",
                    "Ensure the file exists and is accessible",
                    "Try running 'logbuch setup' to initialize"
                ]
            })
        
        elif isinstance(error, PermissionError):
            error_info.update({
                'severity': ErrorSeverity.HIGH,
                'user_message': "Permission denied - cannot access file or directory",
                'suggestions': [
                    "Check file permissions",
                    "Try running with appropriate privileges",
                    "Ensure the directory is writable"
                ]
            })
        
        elif isinstance(error, ImportError):
            error_info.update({
                'severity': ErrorSeverity.HIGH,
                'user_message': f"Missing dependency: {error.name if hasattr(error, 'name') else 'unknown'}",
                'suggestions': [
                    "Install missing dependencies with: pip install -r requirements.txt",
                    "Check if all required packages are installed",
                    "Try reinstalling Logbuch"
                ]
            })
        
        elif isinstance(error, KeyboardInterrupt):
            error_info.update({
                'severity': ErrorSeverity.LOW,
                'user_message': "Operation cancelled by user",
                'suggestions': []
            })
        
        else:
            # Generic error handling
            error_info['user_message'] = f"An unexpected error occurred: {str(error)}"
            error_info['suggestions'] = [
                "Try the operation again",
                "Check the logs for more details",
                "Report this issue if it persists"
            ]
        
        return error_info
    
    def _log_error(self, error_info: Dict[str, Any]):
        log_message = f"{error_info['type']}: {error_info['message']}"
        
        if error_info['context']:
            log_message += f" | Context: {error_info['context']}"
        
        if error_info['severity'] == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
            logger.critical(error_info['traceback'])
        elif error_info['severity'] == ErrorSeverity.HIGH:
            logger.error(log_message)
            logger.debug(error_info['traceback'])
        elif error_info['severity'] == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
            logger.debug(error_info['traceback'])
        else:
            logger.info(log_message)
    
    def _track_error(self, error_info: Dict[str, Any]):
        error_key = f"{error_info['type']}:{error_info['message'][:50]}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Add to history
        self.error_history.append({
            'timestamp': None,  # Would use datetime.now() in real implementation
            'type': error_info['type'],
            'message': error_info['message'],
            'severity': error_info['severity']
        })
        
        # Limit history size
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def _display_error(self, error_info: Dict[str, Any]):
        # Choose appropriate emoji and color based on severity
        severity_config = {
            ErrorSeverity.LOW: {'emoji': '💡', 'color': 'bright_blue', 'title': 'Info'},
            ErrorSeverity.MEDIUM: {'emoji': '⚠️', 'color': 'bright_yellow', 'title': 'Warning'},
            ErrorSeverity.HIGH: {'emoji': '❌', 'color': 'bright_red', 'title': 'Error'},
            ErrorSeverity.CRITICAL: {'emoji': '💥', 'color': 'red', 'title': 'Critical Error'}
        }
        
        config = severity_config[error_info['severity']]
        
        # Create error message
        error_text = Text()
        error_text.append(f"{config['emoji']} {error_info['user_message']}\n", style=f"bold {config['color']}")
        
        # Add suggestions if available
        if error_info['suggestions']:
            error_text.append("\n💡 Suggestions:\n", style="bold bright_cyan")
            for i, suggestion in enumerate(error_info['suggestions'], 1):
                error_text.append(f"  {i}. {suggestion}\n", style="dim")
        
        # Add context if in debug mode
        if logger.level <= 10 and error_info['context']:  # DEBUG level
            error_text.append(f"\n🔍 Context: {error_info['context']}", style="dim")
        
        # Display in panel
        panel = Panel(
            error_text,
            title=f"[bold {config['color']}]{config['title']}[/bold {config['color']}]",
            border_style=config['color']
        )
        
        console.print(panel)
    
    def get_error_stats(self) -> Dict[str, Any]:
        total_errors = sum(self.error_counts.values())
        most_common = sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_errors': total_errors,
            'unique_errors': len(self.error_counts),
            'most_common': most_common,
            'recent_errors': self.error_history[-10:]
        }


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 user_message: str = None, suggestions: list = None):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Convert to LogbuchError if not already
                if not isinstance(e, LogbuchError):
                    e = LogbuchError(
                        str(e),
                        severity=severity,
                        user_message=user_message,
                        suggestions=suggestions
                    )
                
                # Handle the error
                should_continue = error_handler.handle_error(e, {
                    'function': func.__name__,
                    'args': str(args)[:100],
                    'kwargs': str(kwargs)[:100]
                })
                
                if not should_continue:
                    sys.exit(1)
                
                return None
        
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default=None, **kwargs) -> Any:
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle_error(e, {
            'function': func.__name__ if hasattr(func, '__name__') else str(func),
            'args': str(args)[:100],
            'kwargs': str(kwargs)[:100]
        })
        return default


def validate_input(value: Any, validator: Callable, error_message: str = None) -> Any:
    try:
        if not validator(value):
            raise ValidationError(
                error_message or f"Invalid value: {value}",
                value=value,
                suggestions=["Check the input format", "Refer to the documentation"]
            )
        return value
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        else:
            raise ValidationError(
                f"Validation failed: {str(e)}",
                value=value
            )


def graceful_shutdown(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            console.print("\n👋 [dim]Goodbye! Thanks for using Logbuch![/dim]")
            sys.exit(0)
        except Exception as e:
            should_continue = error_handler.handle_error(e)
            if not should_continue:
                console.print("\n💥 [bold red]Critical error - shutting down safely[/bold red]")
                sys.exit(1)
            return None
    
    return wrapper


# Context managers for error handling
class ErrorContext:
    def __init__(self, context_name: str, ignore_errors: bool = False):
        self.context_name = context_name
        self.ignore_errors = ignore_errors
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            should_continue = error_handler.handle_error(exc_val, {
                'context': self.context_name
            })
            
            if self.ignore_errors or should_continue:
                return True  # Suppress the exception
            else:
                return False  # Let the exception propagate


# Export error handling utilities
__all__ = [
    'LogbuchError',
    'DatabaseError', 
    'ValidationError',
    'ConfigurationError',
    'IntegrationError',
    'PerformanceError',
    'ErrorSeverity',
    'ErrorHandler',
    'error_handler',
    'handle_errors',
    'safe_execute',
    'validate_input',
    'graceful_shutdown',
    'ErrorContext'
]
