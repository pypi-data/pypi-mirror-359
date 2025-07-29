#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/core/logger.py

import logging
import logging.handlers
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .config import get_config


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format: [TIMESTAMP] LEVEL: message (module:function:line)
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        location = f"{record.module}:{record.funcName}:{record.lineno}"
        
        formatted = f"[{timestamp}] {color}{record.levelname}{reset}: {record.getMessage()}"
        
        if record.levelname in ['DEBUG', 'ERROR', 'CRITICAL']:
            formatted += f" ({location})"
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class PerformanceLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._timers: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> None:
        self._timers[operation] = time.time()
    
    def end_timer(self, operation: str, **extra_data) -> float:
        if operation not in self._timers:
            self.logger.warning(f"Timer '{operation}' was not started")
            return 0.0
        
        duration = time.time() - self._timers[operation]
        del self._timers[operation]
        
        self.logger.info(
            f"Performance: {operation} completed",
            extra={
                'operation': operation,
                'duration_seconds': duration,
                'duration_ms': duration * 1000,
                **extra_data
            }
        )
        
        return duration
    
    def log_operation(self, operation: str, **metrics):
        self.logger.info(
            f"Metrics: {operation}",
            extra={
                'operation': operation,
                'metrics': metrics
            }
        )


class Logger:
    def __init__(self, name: str = "logbuch"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.performance = PerformanceLogger(self.logger)
        self._configured = False
    
    def configure(self, config=None) -> None:
        if self._configured:
            return
        
        if config is None:
            try:
                config = get_config()
            except:
                # Fallback configuration if config system fails
                config = type('Config', (), {
                    'log_level': 'INFO',
                    'debug': False,
                    'data_dir': str(Path.home() / ".logbuch")
                })()
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level - SILENT by default for clean user experience
        # Only show logs when explicitly requested via verbose flag or debug mode
        verbose_mode = os.environ.get('LOKBUCH_VERBOSE', '0') == '1'
        debug_mode = hasattr(config, 'debug') and config.debug
        
        if verbose_mode:
            default_level = 'INFO'
        elif debug_mode:
            default_level = 'DEBUG'
        else:
            default_level = 'CRITICAL'  # Essentially silent - only critical errors
            
        log_level_str = getattr(config, 'log_level', default_level)
        log_level = getattr(logging, log_level_str.upper(), logging.CRITICAL)
        self.logger.setLevel(log_level)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(ColoredConsoleFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        log_dir = Path(config.data_dir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "logbuch.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
        
        self._configured = True
        self.logger.debug("Logging system configured", extra={
            'log_level': config.log_level,
            'debug_mode': config.debug,
            'log_directory': str(log_dir)
        })
    
    def debug(self, message: str, **extra) -> None:
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, **extra) -> None:
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **extra) -> None:
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, **extra) -> None:
        self.logger.error(message, extra=extra)
    
    def critical(self, message: str, **extra) -> None:
        self.logger.critical(message, extra=extra)
    
    def exception(self, message: str, **extra) -> None:
        self.logger.exception(message, extra=extra)
    
    def log_user_action(self, action: str, **details) -> None:
        self.info(f"User action: {action}", extra={
            'action_type': 'user_action',
            'action': action,
            **details
        })
    
    def log_system_event(self, event: str, **details) -> None:
        self.info(f"System event: {event}", extra={
            'event_type': 'system_event',
            'event': event,
            **details
        })
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> None:
        self.error(f"Error occurred: {str(error)}", extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        })


# Global logger instance
_logger: Optional[Logger] = None


def get_logger(name: str = "logbuch") -> Logger:
    global _logger
    if _logger is None or _logger.name != name:
        _logger = Logger(name)
        _logger.configure()
    return _logger


def log_function_call(func):
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Calling {func.__name__}", extra={
            'function': func.__name__,
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys())
        })
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"Completed {func.__name__}", extra={
                'function': func.__name__,
                'duration_seconds': duration,
                'success': True
            })
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed {func.__name__}: {str(e)}", extra={
                'function': func.__name__,
                'duration_seconds': duration,
                'success': False,
                'error': str(e)
            })
            raise
    
    return wrapper
