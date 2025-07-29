#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/core/exceptions.py

from typing import Optional, Dict, Any


class LogbuchError(Exception):
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.user_message = user_message or message
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'user_message': self.user_message,
            'details': self.details
        }


class ValidationError(LogbuchError):
    def __init__(self, field: str, value: Any, reason: str):
        message = f"Validation failed for field '{field}': {reason}"
        user_message = f"Invalid {field}: {reason}"
        details = {'field': field, 'value': str(value), 'reason': reason}
        super().__init__(message, 'VALIDATION_ERROR', details, user_message)


class StorageError(LogbuchError):
    def __init__(self, operation: str, reason: str, details: Optional[Dict] = None):
        message = f"Storage operation '{operation}' failed: {reason}"
        user_message = f"Failed to {operation.lower()}. Please try again."
        error_details = {'operation': operation, 'reason': reason}
        if details:
            error_details.update(details)
        super().__init__(message, 'STORAGE_ERROR', error_details, user_message)


class ConfigurationError(LogbuchError):
    def __init__(self, message: str, config_key: Optional[str] = None):
        user_message = "Configuration error. Please check your settings."
        details = {'config_key': config_key} if config_key else {}
        super().__init__(message, 'CONFIG_ERROR', details, user_message)


class SecurityError(LogbuchError):
    def __init__(self, violation_type: str, details: Optional[Dict] = None):
        message = f"Security violation: {violation_type}"
        user_message = "Operation blocked for security reasons."
        super().__init__(message, 'SECURITY_ERROR', details or {}, user_message)


class NotificationError(LogbuchError):
    def __init__(self, reason: str, platform: Optional[str] = None):
        message = f"Notification failed: {reason}"
        user_message = "Failed to send notification."
        details = {'platform': platform} if platform else {}
        super().__init__(message, 'NOTIFICATION_ERROR', details, user_message)


class ExportError(LogbuchError):
    def __init__(self, format_type: str, reason: str):
        message = f"Export to {format_type} failed: {reason}"
        user_message = f"Failed to export data as {format_type}."
        details = {'format': format_type, 'reason': reason}
        super().__init__(message, 'EXPORT_ERROR', details, user_message)


class ImportError(LogbuchError):
    def __init__(self, source: str, reason: str, line_number: Optional[int] = None):
        message = f"Import from {source} failed: {reason}"
        user_message = f"Failed to import data from {source}."
        details = {'source': source, 'reason': reason}
        if line_number:
            details['line_number'] = line_number
            message += f" (line {line_number})"
        super().__init__(message, 'IMPORT_ERROR', details, user_message)


class BackupError(LogbuchError):
    def __init__(self, operation: str, reason: str):
        message = f"Backup {operation} failed: {reason}"
        user_message = f"Backup operation failed. {reason}"
        details = {'operation': operation, 'reason': reason}
        super().__init__(message, 'BACKUP_ERROR', details, user_message)


class ProjectError(LogbuchError):
    def __init__(self, project_id: str, operation: str, reason: str):
        message = f"Project {project_id} {operation} failed: {reason}"
        user_message = f"Project operation failed: {reason}"
        details = {'project_id': project_id, 'operation': operation, 'reason': reason}
        super().__init__(message, 'PROJECT_ERROR', details, user_message)


# Exception handling utilities

def handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LogbuchError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert unexpected exceptions to LogbuchError
            raise LogbuchError(
                message=f"Unexpected error in {func.__name__}: {str(e)}",
                error_code='UNEXPECTED_ERROR',
                details={'function': func.__name__, 'original_error': str(e)},
                user_message="An unexpected error occurred. Please try again."
            )
    return wrapper


def format_error_for_user(error: Exception) -> str:
    if isinstance(error, LogbuchError):
        return error.user_message
    else:
        return "An unexpected error occurred. Please try again."


def get_error_details(error: Exception) -> Dict[str, Any]:
    if isinstance(error, LogbuchError):
        return error.to_dict()
    else:
        return {
            'error_type': type(error).__name__,
            'message': str(error),
            'error_code': 'UNKNOWN_ERROR'
        }
