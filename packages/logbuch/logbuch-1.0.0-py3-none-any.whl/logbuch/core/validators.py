#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/core/validators.py

import re
import os
from pathlib import Path
from typing import Any, List, Optional, Union, Dict
from datetime import datetime
from .exceptions import ValidationError, SecurityError
from .config import get_config


class InputValidator:
    def __init__(self):
        self.config = get_config()
    
    def validate_string(
        self, 
        value: Any, 
        field_name: str,
        min_length: int = 0,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allow_empty: bool = True
    ) -> str:
        # Type check
        if not isinstance(value, str):
            if value is None and allow_empty:
                return ""
            raise ValidationError(field_name, value, "must be a string")
        
        # Length checks
        if not allow_empty and len(value.strip()) == 0:
            raise ValidationError(field_name, value, "cannot be empty")
        
        if len(value) < min_length:
            raise ValidationError(field_name, value, f"must be at least {min_length} characters")
        
        max_len = max_length or self.config.security.max_input_length
        if len(value) > max_len:
            raise ValidationError(field_name, value, f"must be no more than {max_len} characters")
        
        # Pattern validation
        if pattern and not re.match(pattern, value):
            raise ValidationError(field_name, value, "format is invalid")
        
        # Security checks
        if self.config.security.input_validation:
            self._check_for_malicious_content(value, field_name)
        
        return value.strip()
    
    def validate_integer(
        self,
        value: Any,
        field_name: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> int:
        # Type conversion
        try:
            if isinstance(value, str):
                int_value = int(value.strip())
            elif isinstance(value, (int, float)):
                int_value = int(value)
            else:
                raise ValueError("Invalid type")
        except (ValueError, TypeError):
            raise ValidationError(field_name, value, "must be a valid integer")
        
        # Range checks
        if min_value is not None and int_value < min_value:
            raise ValidationError(field_name, value, f"must be at least {min_value}")
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(field_name, value, f"must be no more than {max_value}")
        
        return int_value
    
    def validate_float(
        self,
        value: Any,
        field_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> float:
        # Type conversion
        try:
            if isinstance(value, str):
                float_value = float(value.strip())
            elif isinstance(value, (int, float)):
                float_value = float(value)
            else:
                raise ValueError("Invalid type")
        except (ValueError, TypeError):
            raise ValidationError(field_name, value, "must be a valid number")
        
        # Range checks
        if min_value is not None and float_value < min_value:
            raise ValidationError(field_name, value, f"must be at least {min_value}")
        
        if max_value is not None and float_value > max_value:
            raise ValidationError(field_name, value, f"must be no more than {max_value}")
        
        return float_value
    
    def validate_choice(
        self,
        value: Any,
        field_name: str,
        choices: List[str],
        case_sensitive: bool = True
    ) -> str:
        if not isinstance(value, str):
            raise ValidationError(field_name, value, "must be a string")
        
        value = value.strip()
        
        if case_sensitive:
            valid_choices = choices
            check_value = value
        else:
            valid_choices = [choice.lower() for choice in choices]
            check_value = value.lower()
        
        if check_value not in valid_choices:
            choices_str = ", ".join(choices)
            raise ValidationError(field_name, value, f"must be one of: {choices_str}")
        
        # Return original case from choices if case insensitive
        if not case_sensitive:
            for i, choice in enumerate(valid_choices):
                if choice == check_value:
                    return choices[i]
        
        return value
    
    def validate_date(
        self,
        value: Any,
        field_name: str,
        format_string: str = "%Y-%m-%d"
    ) -> datetime:
        if isinstance(value, datetime):
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, value, "must be a date string or datetime object")
        
        try:
            return datetime.strptime(value.strip(), format_string)
        except ValueError:
            raise ValidationError(field_name, value, f"must be in format {format_string}")
    
    def validate_file_path(
        self,
        value: Any,
        field_name: str,
        must_exist: bool = False,
        allowed_extensions: Optional[List[str]] = None
    ) -> Path:
        if not isinstance(value, (str, Path)):
            raise ValidationError(field_name, value, "must be a valid file path")
        
        path = Path(str(value).strip())
        
        # Security checks
        if self.config.security.sanitize_paths:
            self._validate_path_security(path, field_name)
        
        # Extension check
        extensions = allowed_extensions or self.config.security.allowed_file_extensions
        if extensions and path.suffix.lower() not in extensions:
            ext_str = ", ".join(extensions)
            raise ValidationError(field_name, value, f"file extension must be one of: {ext_str}")
        
        # Existence check
        if must_exist and not path.exists():
            raise ValidationError(field_name, value, "file does not exist")
        
        return path
    
    def validate_email(self, value: Any, field_name: str) -> str:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return self.validate_string(
            value, 
            field_name, 
            min_length=5, 
            max_length=254, 
            pattern=email_pattern
        )
    
    def validate_url(self, value: Any, field_name: str) -> str:
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return self.validate_string(
            value,
            field_name,
            min_length=10,
            max_length=2048,
            pattern=url_pattern
        )
    
    def validate_tags(self, value: Any, field_name: str) -> List[str]:
        if value is None:
            return []
        
        if isinstance(value, str):
            # Split comma-separated tags
            tags = [tag.strip() for tag in value.split(',') if tag.strip()]
        elif isinstance(value, list):
            tags = [str(tag).strip() for tag in value if str(tag).strip()]
        else:
            raise ValidationError(field_name, value, "must be a list or comma-separated string")
        
        # Validate each tag
        validated_tags = []
        for tag in tags:
            validated_tag = self.validate_string(
                tag, 
                f"{field_name}_tag", 
                min_length=1, 
                max_length=50,
                pattern=r'^[a-zA-Z0-9_-]+$'
            )
            if validated_tag not in validated_tags:  # Remove duplicates
                validated_tags.append(validated_tag)
        
        return validated_tags
    
    def validate_priority(self, value: Any, field_name: str) -> str:
        return self.validate_choice(
            value, 
            field_name, 
            ['low', 'medium', 'high'], 
            case_sensitive=False
        )
    
    def validate_mood(self, value: Any, field_name: str) -> str:
        return self.validate_string(
            value,
            field_name,
            min_length=1,
            max_length=50,
            pattern=r'^[a-zA-Z0-9_\-\s]+$'
        )
    
    def _check_for_malicious_content(self, value: str, field_name: str) -> None:
        # SQL injection patterns
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)\b)',
            r'(--|#|/\*|\*/)',
            r'(\bUNION\b.*\bSELECT\b)',
            r'(\bOR\b.*=.*\bOR\b)',
            r'(\'.*\'.*=.*\'.*\')'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityError(f"Potential SQL injection in {field_name}")
        
        # Script injection patterns
        script_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityError(f"Potential script injection in {field_name}")
        
        # Path traversal patterns
        if '../' in value or '..\\' in value:
            raise SecurityError(f"Potential path traversal in {field_name}")
    
    def _validate_path_security(self, path: Path, field_name: str) -> None:
        path_str = str(path)
        
        # Check for path traversal
        if '..' in path.parts:
            raise SecurityError(f"Path traversal detected in {field_name}")
        
        # Check for absolute paths outside allowed directories
        if path.is_absolute():
            allowed_roots = [
                Path.home(),
                Path.cwd(),
                Path(self.config.data_dir)
            ]
            
            if not any(str(path).startswith(str(root)) for root in allowed_roots):
                raise SecurityError(f"Path outside allowed directories in {field_name}")
        
        # Check for special files/devices on Unix systems
        if os.name == 'posix':
            dangerous_paths = ['/dev/', '/proc/', '/sys/']
            if any(path_str.startswith(dangerous) for dangerous in dangerous_paths):
                raise SecurityError(f"Access to system path denied in {field_name}")


# Validation decorators

def validate_input(**validation_rules):
    def decorator(func):
        def wrapper(*args, **kwargs):
            validator = InputValidator()
            
            # Validate kwargs based on rules
            for param_name, rules in validation_rules.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    validation_type = rules.get('type', 'string')
                    
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
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global validator instance
_validator: Optional[InputValidator] = None


def get_validator() -> InputValidator:
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator
