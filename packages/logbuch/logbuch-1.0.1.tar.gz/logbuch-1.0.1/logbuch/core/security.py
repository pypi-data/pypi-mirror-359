#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/core/security.py

import time
import hashlib
import secrets
from collections import defaultdict, deque
from typing import Dict, Optional, Any, List
from pathlib import Path
from .config import get_config
from .logger import get_logger
from .exceptions import SecurityError


class RateLimiter:
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        window_start = now - self.time_window
        
        # Clean old requests
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, identifier: str) -> int:
        now = time.time()
        window_start = now - self.time_window
        
        # Clean old requests
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()
        
        return max(0, self.max_requests - len(self.requests[identifier]))
    
    def reset(self, identifier: str) -> None:
        if identifier in self.requests:
            del self.requests[identifier]


class InputSanitizer:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        # Remove or replace dangerous characters
        dangerous_chars = '<>:"/\\|?*'
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = Path(sanitized).stem, Path(sanitized).suffix
            max_name_len = 255 - len(ext)
            sanitized = name[:max_name_len] + ext
        
        # Ensure not empty
        if not sanitized:
            sanitized = "untitled"
        
        return sanitized
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        # Normalize path separators
        sanitized = path.replace('\\', '/')
        
        # Remove path traversal attempts
        parts = []
        for part in sanitized.split('/'):
            if part == '..':
                continue  # Skip parent directory references
            if part and part != '.':
                parts.append(InputSanitizer.sanitize_filename(part))
        
        return '/'.join(parts)
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        if not isinstance(text, str):
            return str(text)
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove null bytes and control characters (except newlines and tabs)
        sanitized = ''.join(char for char in text 
                           if ord(char) >= 32 or char in '\n\t\r')
        
        return sanitized.strip()


class SecurityAuditor:
    def __init__(self):
        self.logger = get_logger("security")
        self.suspicious_events: List[Dict[str, Any]] = []
        self.blocked_attempts: Dict[str, int] = defaultdict(int)
    
    def log_security_event(
        self, 
        event_type: str, 
        severity: str, 
        details: Dict[str, Any]
    ) -> None:
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        
        self.suspicious_events.append(event)
        
        # Log based on severity
        if severity == 'critical':
            self.logger.critical(f"Security event: {event_type}", extra=details)
        elif severity == 'high':
            self.logger.error(f"Security event: {event_type}", extra=details)
        elif severity == 'medium':
            self.logger.warning(f"Security event: {event_type}", extra=details)
        else:
            self.logger.info(f"Security event: {event_type}", extra=details)
    
    def log_blocked_attempt(self, attempt_type: str, identifier: str) -> None:
        self.blocked_attempts[f"{attempt_type}:{identifier}"] += 1
        
        self.log_security_event(
            'blocked_attempt',
            'medium',
            {
                'attempt_type': attempt_type,
                'identifier': identifier,
                'total_attempts': self.blocked_attempts[f"{attempt_type}:{identifier}"]
            }
        )
    
    def get_security_summary(self) -> Dict[str, Any]:
        recent_events = [
            event for event in self.suspicious_events
            if time.time() - event['timestamp'] < 3600  # Last hour
        ]
        
        return {
            'total_events': len(self.suspicious_events),
            'recent_events': len(recent_events),
            'blocked_attempts': dict(self.blocked_attempts),
            'severity_counts': {
                'critical': len([e for e in recent_events if e['severity'] == 'critical']),
                'high': len([e for e in recent_events if e['severity'] == 'high']),
                'medium': len([e for e in recent_events if e['severity'] == 'medium']),
                'low': len([e for e in recent_events if e['severity'] == 'low'])
            }
        }


class SecurityManager:
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("security")
        self.rate_limiter = RateLimiter(
            self.config.security.max_requests_per_minute,
            60  # 1 minute window
        )
        self.sanitizer = InputSanitizer()
        self.auditor = SecurityAuditor()
        self._session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        return secrets.token_hex(16)
    
    def check_rate_limit(self, operation: str, identifier: Optional[str] = None) -> bool:
        if not self.config.security.rate_limit_enabled:
            return True
        
        check_id = identifier or self._session_id
        rate_key = f"{operation}:{check_id}"
        
        if not self.rate_limiter.is_allowed(rate_key):
            self.auditor.log_blocked_attempt('rate_limit', rate_key)
            return False
        
        return True
    
    def validate_file_operation(self, file_path: str, operation: str) -> Path:
        # Sanitize path
        sanitized_path = self.sanitizer.sanitize_path(file_path)
        path = Path(sanitized_path)
        
        # Check if path is within allowed directories
        allowed_dirs = [
            Path(self.config.data_dir),
            Path.home() / "Downloads",
            Path.home() / "Documents",
            Path.cwd()
        ]
        
        # Convert to absolute path for checking
        abs_path = path.resolve()
        
        # Check if within allowed directories
        allowed = False
        for allowed_dir in allowed_dirs:
            try:
                abs_path.relative_to(allowed_dir.resolve())
                allowed = True
                break
            except ValueError:
                continue
        
        if not allowed:
            self.auditor.log_security_event(
                'unauthorized_file_access',
                'high',
                {
                    'operation': operation,
                    'requested_path': file_path,
                    'sanitized_path': str(path),
                    'absolute_path': str(abs_path)
                }
            )
            raise SecurityError(f"File access denied: {file_path}")
        
        return path
    
    def sanitize_user_input(self, input_data: Any, input_type: str = "text") -> Any:
        if input_type == "text":
            return self.sanitizer.sanitize_text(str(input_data))
        elif input_type == "filename":
            return self.sanitizer.sanitize_filename(str(input_data))
        elif input_type == "path":
            return self.sanitizer.sanitize_path(str(input_data))
        else:
            return self.sanitizer.sanitize_text(str(input_data))
    
    def log_user_action(self, action: str, **details) -> None:
        self.auditor.log_security_event(
            'user_action',
            'low',
            {
                'action': action,
                'session_id': self._session_id,
                **details
            }
        )
    
    def check_input_size(self, data: str, max_size: Optional[int] = None) -> bool:
        max_allowed = max_size or self.config.security.max_input_length
        
        if len(data) > max_allowed:
            self.auditor.log_security_event(
                'oversized_input',
                'medium',
                {
                    'input_size': len(data),
                    'max_allowed': max_allowed,
                    'session_id': self._session_id
                }
            )
            return False
        
        return True
    
    def generate_secure_filename(self, base_name: str, extension: str = "") -> str:
        timestamp = int(time.time())
        hash_part = hashlib.md5(f"{base_name}{timestamp}".encode()).hexdigest()[:8]
        safe_name = self.sanitizer.sanitize_filename(base_name)
        
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
        
        return f"{safe_name}_{timestamp}_{hash_part}{extension}"
    
    def get_security_status(self) -> Dict[str, Any]:
        return {
            'session_id': self._session_id,
            'rate_limiting_enabled': self.config.security.rate_limit_enabled,
            'input_validation_enabled': self.config.security.input_validation,
            'path_sanitization_enabled': self.config.security.sanitize_paths,
            'audit_summary': self.auditor.get_security_summary(),
            'remaining_requests': self.rate_limiter.get_remaining_requests(self._session_id)
        }


# Security decorators

def require_rate_limit(operation: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            security_manager = SecurityManager()
            
            if not security_manager.check_rate_limit(operation):
                raise SecurityError(f"Rate limit exceeded for operation: {operation}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def sanitize_inputs(**sanitization_rules):
    def decorator(func):
        def wrapper(*args, **kwargs):
            security_manager = SecurityManager()
            
            # Sanitize kwargs based on rules
            for param_name, input_type in sanitization_rules.items():
                if param_name in kwargs:
                    kwargs[param_name] = security_manager.sanitize_user_input(
                        kwargs[param_name], 
                        input_type
                    )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def audit_action(action_name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            security_manager = SecurityManager()
            
            # Log the action
            security_manager.log_user_action(
                action_name,
                function=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager
