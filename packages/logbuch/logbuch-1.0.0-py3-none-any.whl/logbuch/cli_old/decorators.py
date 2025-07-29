#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/cli/decorators.py

import time
import functools
from typing import Any, Callable, Optional, Dict, List
from rich import print as rprint

from logbuch.core.logger import get_logger
from logbuch.core.exceptions import LogbuchError, format_error_for_user, get_error_details
from logbuch.core.security import get_security_manager


def command_wrapper(
    name: str,
    short_help: str = "",
    aliases: Optional[List[str]] = None,
    require_auth: bool = False,
    rate_limit: bool = True
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            security = get_security_manager()
            
            # Log command start
            logger.log_user_action(name, **{
                k: str(v)[:100] for k, v in kwargs.items()  # Truncate long values
            })
            
            # Rate limiting check
            if rate_limit and not security.check_rate_limit(name):
                rprint("[red]⚠️ Rate limit exceeded. Please wait before trying again.[/red]")
                return
            
            # Authentication check (placeholder for future implementation)
            if require_auth:
                # TODO: Implement authentication system
                pass
            
            try:
                # Execute command
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log successful completion
                logger.info(f"Command '{name}' completed successfully", extra={
                    'command': name,
                    'duration_seconds': duration,
                    'success': True
                })
                
                return result
                
            except Exception as error:
                duration = time.time() - start_time
                
                # Log error
                logger.error(f"Command '{name}' failed", extra={
                    'command': name,
                    'duration_seconds': duration,
                    'success': False,
                    'error_details': get_error_details(error)
                })
                
                # Display user-friendly error
                user_message = format_error_for_user(error)
                rprint(f"[red]❌ {user_message}[/red]")
                
                # Re-raise for proper error handling
                raise
        
        # Add metadata to function
        wrapper._command_name = name
        wrapper._command_help = short_help
        wrapper._command_aliases = aliases or []
        wrapper._require_auth = require_auth
        wrapper._rate_limit = rate_limit
        
        return wrapper
    return decorator


def error_handler(
    show_traceback: bool = False,
    custom_messages: Optional[Dict[type, str]] = None
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            
            try:
                return func(*args, **kwargs)
                
            except KeyboardInterrupt:
                rprint("\n[yellow]Operation cancelled by user[/yellow]")
                return
                
            except LogbuchError as error:
                # Handle our custom exceptions
                logger.error(f"Logbuch error in {func.__name__}", extra=error.to_dict())
                rprint(f"[red]❌ {error.user_message}[/red]")
                
                if show_traceback and logger.logger.level <= 10:  # DEBUG level
                    logger.exception("Full traceback:")
                
            except Exception as error:
                # Handle unexpected exceptions
                error_type = type(error).__name__
                
                # Use custom message if available
                if custom_messages and type(error) in custom_messages:
                    message = custom_messages[type(error)]
                else:
                    message = f"An unexpected error occurred: {str(error)}"
                
                logger.exception(f"Unexpected error in {func.__name__}", extra={
                    'function': func.__name__,
                    'error_type': error_type,
                    'error_message': str(error)
                })
                
                rprint(f"[red]❌ {message}[/red]")
                
                if show_traceback and logger.logger.level <= 10:  # DEBUG level
                    import traceback
                    rprint(f"[dim]{traceback.format_exc()}[/dim]")
        
        return wrapper
    return decorator


def performance_monitor(
    threshold_seconds: float = 1.0,
    log_all: bool = False
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            
            start_time = time.time()
            start_memory = _get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
                
            except Exception as error:
                success = False
                raise
                
            finally:
                end_time = time.time()
                end_memory = _get_memory_usage()
                
                duration = end_time - start_time
                memory_delta = end_memory - start_memory if end_memory and start_memory else 0
                
                # Log performance metrics
                perf_data = {
                    'function': func.__name__,
                    'duration_seconds': duration,
                    'duration_ms': duration * 1000,
                    'memory_delta_mb': memory_delta / (1024 * 1024) if memory_delta else 0,
                    'success': success,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
                
                # Log based on conditions
                if log_all or duration > threshold_seconds:
                    if duration > threshold_seconds:
                        logger.warning(f"Slow execution: {func.__name__}", extra=perf_data)
                    else:
                        logger.info(f"Performance: {func.__name__}", extra=perf_data)
                
                # Display warning for very slow operations
                if duration > threshold_seconds * 2:
                    rprint(f"[yellow]⚠️ Operation took {duration:.2f} seconds[/yellow]")
        
        return wrapper
    return decorator


def validate_args(**validation_rules):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from logbuch.core.validators import get_validator
            validator = get_validator()
            
            # Validate kwargs based on rules
            for param_name, rules in validation_rules.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    validation_type = rules.get('type', 'string')
                    
                    try:
                        if validation_type == 'string':
                            kwargs[param_name] = validator.validate_string(
                                value, param_name, **{k: v for k, v in rules.items() if k != 'type'}
                            )
                        elif validation_type == 'integer':
                            kwargs[param_name] = validator.validate_integer(
                                value, param_name, **{k: v for k, v in rules.items() if k != 'type'}
                            )
                        elif validation_type == 'choice':
                            kwargs[param_name] = validator.validate_choice(
                                value, param_name, **{k: v for k, v in rules.items() if k != 'type'}
                            )
                        elif validation_type == 'tags':
                            kwargs[param_name] = validator.validate_tags(value, param_name)
                        elif validation_type == 'priority':
                            kwargs[param_name] = validator.validate_priority(value, param_name)
                        elif validation_type == 'file_path':
                            kwargs[param_name] = validator.validate_file_path(
                                value, param_name, **{k: v for k, v in rules.items() if k != 'type'}
                            )
                    except Exception as e:
                        rprint(f"[red]❌ Validation error for {param_name}: {str(e)}[/red]")
                        return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cache_result(
    ttl_seconds: int = 300,
    key_func: Optional[Callable] = None
):
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check cache
            current_time = time.time()
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return result
                else:
                    # Remove expired entry
                    del cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            return result
        
        # Add cache management methods
        wrapper.clear_cache = lambda: cache.clear()
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'keys': list(cache.keys())
        }
        
        return wrapper
    return decorator


def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    exceptions: tuple = (Exception,)
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as error:
                    if attempt == max_attempts - 1:
                        # Last attempt failed, re-raise
                        logger.error(f"All retry attempts failed for {func.__name__}", extra={
                            'function': func.__name__,
                            'attempts': max_attempts,
                            'final_error': str(error)
                        })
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = delay_seconds * (backoff_multiplier ** attempt)
                    
                    logger.warning(f"Retry attempt {attempt + 1} for {func.__name__}", extra={
                        'function': func.__name__,
                        'attempt': attempt + 1,
                        'max_attempts': max_attempts,
                        'delay_seconds': delay,
                        'error': str(error)
                    })
                    
                    time.sleep(delay)
        
        return wrapper
    return decorator


# Utility functions

def _get_memory_usage() -> Optional[int]:
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss
    except ImportError:
        return None


def combine_decorators(*decorators):
    def decorator(func):
        for dec in reversed(decorators):
            func = dec(func)
        return func
    return decorator


# Common decorator combinations

def standard_command(
    name: str,
    short_help: str = "",
    aliases: Optional[List[str]] = None,
    validation_rules: Optional[Dict] = None
):
    decorators = [
        command_wrapper(name, short_help, aliases),
        error_handler(show_traceback=True),
        performance_monitor(threshold_seconds=2.0)
    ]
    
    if validation_rules:
        decorators.append(validate_args(**validation_rules))
    
    return combine_decorators(*decorators)


def data_command(
    name: str,
    short_help: str = "",
    aliases: Optional[List[str]] = None,
    cache_ttl: int = 60
):
    return combine_decorators(
        command_wrapper(name, short_help, aliases),
        error_handler(),
        performance_monitor(),
        cache_result(ttl_seconds=cache_ttl)
    )


def file_command(
    name: str,
    short_help: str = "",
    aliases: Optional[List[str]] = None,
    max_retries: int = 3
):
    return combine_decorators(
        command_wrapper(name, short_help, aliases),
        error_handler(),
        performance_monitor(),
        retry(max_attempts=max_retries, exceptions=(IOError, OSError))
    )
