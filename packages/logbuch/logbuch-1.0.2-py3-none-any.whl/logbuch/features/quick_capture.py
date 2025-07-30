#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/quick_capture.py

import datetime
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from logbuch.core.logger import get_logger


class CaptureType(Enum):
    IDEA = "idea"           # 💡 Random ideas and inspirations
    TASK = "task"           # ✅ Quick tasks to do
    NOTE = "note"           # 📝 Important information
    QUOTE = "quote"         # 💬 Memorable quotes
    LINK = "link"           # 🔗 Useful links and resources
    REMINDER = "reminder"   # ⏰ Things to remember
    GOAL = "goal"           # 🎯 Aspirations and objectives


@dataclass
class QuickCapture:
    id: str
    type: CaptureType
    content: str
    tags: List[str]
    priority: str
    created_at: datetime.datetime
    processed: bool = False
    converted_to: Optional[str] = None  # task_id, note_id, etc.


class QuickCaptureSystem:
    def __init__(self, storage):
        self.storage = storage
        self.logger = get_logger("quick_capture")
        self.captures = self._load_captures()
        
        self.logger.debug("Quick Capture System initialized")
    
    def _load_captures(self) -> List[QuickCapture]:
        try:
            from pathlib import Path
            captures_file = Path.home() / ".logbuch" / "quick_captures.json"
            
            if captures_file.exists():
                with open(captures_file, 'r') as f:
                    data = json.load(f)
                    captures = []
                    for item in data:
                        item['created_at'] = datetime.datetime.fromisoformat(item['created_at'])
                        item['type'] = CaptureType(item['type'])
                        captures.append(QuickCapture(**item))
                    return captures
        except Exception as e:
            self.logger.debug(f"Could not load captures: {e}")
        
        return []
    
    def _save_captures(self):
        try:
            from pathlib import Path
            captures_file = Path.home() / ".logbuch" / "quick_captures.json"
            captures_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = []
            for capture in self.captures:
                capture_dict = {
                    'id': capture.id,
                    'type': capture.type.value,
                    'content': capture.content,
                    'tags': capture.tags,
                    'priority': capture.priority,
                    'created_at': capture.created_at.isoformat(),
                    'processed': capture.processed,
                    'converted_to': capture.converted_to
                }
                data.append(capture_dict)
            
            with open(captures_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save captures: {e}")
    
    def quick_capture(self, content: str, capture_type: str = "auto", 
                     tags: List[str] = None, priority: str = "medium") -> str:
        # Auto-detect type if not specified
        if capture_type == "auto":
            capture_type = self._detect_type(content)
        
        # Generate ID
        capture_id = f"cap_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract tags from content if not provided
        if tags is None:
            tags = self._extract_tags(content)
        
        # Create capture
        capture = QuickCapture(
            id=capture_id,
            type=CaptureType(capture_type),
            content=content,
            tags=tags,
            priority=priority,
            created_at=datetime.datetime.now()
        )
        
        self.captures.append(capture)
        self._save_captures()
        
        self.logger.info(f"Quick capture created: {capture_type} - {content[:50]}...")
        return capture_id
    
    def _detect_type(self, content: str) -> str:
        content_lower = content.lower()
        
        # Task indicators
        if any(word in content_lower for word in ['todo', 'task', 'do ', 'finish', 'complete', 'work on']):
            return "task"
        
        # Idea indicators  
        if any(word in content_lower for word in ['idea', 'maybe', 'what if', 'could', 'might', 'brainstorm']):
            return "idea"
        
        # Reminder indicators
        if any(word in content_lower for word in ['remember', 'remind', 'don\'t forget', 'note to self']):
            return "reminder"
        
        # Goal indicators
        if any(word in content_lower for word in ['goal', 'want to', 'aspire', 'achieve', 'dream']):
            return "goal"
        
        # Quote indicators
        if content.startswith('"') and content.endswith('"'):
            return "quote"
        
        # Link indicators
        if 'http' in content_lower or 'www.' in content_lower:
            return "link"
        
        # Default to note
        return "note"
    
    def _extract_tags(self, content: str) -> List[str]:
        import re
        tags = re.findall(r'#(\w+)', content)
        return tags
    
    def list_captures(self, capture_type: Optional[str] = None, 
                     unprocessed_only: bool = False) -> List[QuickCapture]:
        captures = self.captures
        
        if capture_type:
            captures = [c for c in captures if c.type.value == capture_type]
        
        if unprocessed_only:
            captures = [c for c in captures if not c.processed]
        
        # Sort by creation date (newest first)
        captures.sort(key=lambda x: x.created_at, reverse=True)
        return captures
    
    def process_capture(self, capture_id: str, action: str = "convert") -> bool:
        capture = next((c for c in self.captures if c.id == capture_id), None)
        if not capture:
            return False
        
        try:
            if action == "convert":
                converted_id = self._convert_capture(capture)
                if converted_id:
                    capture.processed = True
                    capture.converted_to = converted_id
                    self._save_captures()
                    return True
            
            elif action == "delete":
                self.captures.remove(capture)
                self._save_captures()
                return True
            
            elif action == "archive":
                capture.processed = True
                self._save_captures()
                return True
        
        except Exception as e:
            self.logger.error(f"Error processing capture: {e}")
        
        return False
    
    def _convert_capture(self, capture: QuickCapture) -> Optional[str]:
        try:
            if capture.type == CaptureType.TASK:
                # Convert to task
                task_data = {
                    'title': capture.content,
                    'priority': capture.priority,
                    'tags': capture.tags,
                    'created_from_capture': capture.id
                }
                # Would integrate with task creation system
                return f"task_{capture.id}"
            
            elif capture.type == CaptureType.NOTE:
                # Convert to journal entry
                journal_data = {
                    'content': capture.content,
                    'tags': capture.tags,
                    'created_from_capture': capture.id
                }
                # Would integrate with journal system
                return f"journal_{capture.id}"
            
            elif capture.type == CaptureType.GOAL:
                # Convert to goal
                goal_data = {
                    'title': capture.content,
                    'priority': capture.priority,
                    'created_from_capture': capture.id
                }
                # Would integrate with goal system
                return f"goal_{capture.id}"
            
            elif capture.type == CaptureType.REMINDER:
                # Convert to task with due date
                task_data = {
                    'title': f"Reminder: {capture.content}",
                    'priority': 'high',
                    'due_date': (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
                    'created_from_capture': capture.id
                }
                return f"reminder_task_{capture.id}"
            
            # For ideas, quotes, links - keep as captures but mark processed
            return f"archived_{capture.id}"
            
        except Exception as e:
            self.logger.error(f"Error converting capture: {e}")
            return None
    
    def get_capture_stats(self) -> Dict[str, Any]:
        total = len(self.captures)
        processed = len([c for c in self.captures if c.processed])
        unprocessed = total - processed
        
        # Count by type
        type_counts = {}
        for capture in self.captures:
            type_name = capture.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Recent activity
        recent = [c for c in self.captures if 
                 c.created_at > datetime.datetime.now() - datetime.timedelta(days=7)]
        
        return {
            'total_captures': total,
            'processed': processed,
            'unprocessed': unprocessed,
            'processing_rate': processed / total if total > 0 else 0,
            'type_distribution': type_counts,
            'recent_captures': len(recent),
            'most_common_type': max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        }
    
    def search_captures(self, query: str) -> List[QuickCapture]:
        query_lower = query.lower()
        results = []
        
        for capture in self.captures:
            if (query_lower in capture.content.lower() or 
                any(query_lower in tag.lower() for tag in capture.tags)):
                results.append(capture)
        
        return results
    
    def get_daily_captures(self, date: Optional[datetime.date] = None) -> List[QuickCapture]:
        if date is None:
            date = datetime.date.today()
        
        return [c for c in self.captures if c.created_at.date() == date]


# Export for CLI integration
__all__ = ['QuickCaptureSystem', 'QuickCapture', 'CaptureType']
