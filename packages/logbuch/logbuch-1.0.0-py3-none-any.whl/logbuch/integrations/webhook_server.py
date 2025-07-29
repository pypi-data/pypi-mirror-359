#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/integrations/webhook_server.py

import json
import hmac
import hashlib
import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from threading import Thread
import asyncio
from pathlib import Path

try:
    from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Create dummy classes for when FastAPI is not available
    class HTTPAuthorizationCredentials:
        def __init__(self):
            self.credentials = ""
    
    class Request:
        pass
    
    class BackgroundTasks:
        pass

from logbuch.core.logger import get_logger
from logbuch.core.config import get_config
from logbuch.core.exceptions import LogbuchError
from logbuch.core.security import get_security_manager


@dataclass
class WebhookEvent:
    id: str
    source: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime.datetime
    signature: Optional[str] = None
    processed: bool = False


class WebhookError(LogbuchError):
    pass


class WebhookServer:
    def __init__(self, port: int = 8080, host: str = "localhost"):
        self.logger = get_logger("webhook_server")
        self.security = get_security_manager()
        self.config = get_config()
        
        self.port = port
        self.host = host
        self.app = None
        self.server_thread = None
        self.is_running = False
        
        # Event handlers
        self.handlers: Dict[str, List[Callable]] = {}
        self.events: List[WebhookEvent] = []
        
        # Security
        self.webhook_secrets: Dict[str, str] = {}
        self.api_keys: List[str] = []
        
        if FASTAPI_AVAILABLE:
            self._setup_fastapi()
        else:
            self.logger.warning("FastAPI not available - webhook server disabled")
    
    def _setup_fastapi(self):
        self.app = FastAPI(
            title="Logbuch Webhook Server",
            description="Professional webhook server for Logbuch integrations",
            version="1.0.0"
        )
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Security
        security = HTTPBearer(auto_error=False)
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = datetime.datetime.now()
            response = await call_next(request)
            process_time = (datetime.datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Webhook request: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
            return response
        
        # Routes
        @self.app.get("/")
        async def root():
            return {
                "service": "Logbuch Webhook Server",
                "version": "1.0.0",
                "status": "running",
                "endpoints": [
                    "/webhook/{source}",
                    "/api/events",
                    "/api/health"
                ]
            }
        
        @self.app.get("/api/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat(),
                "events_processed": len([e for e in self.events if e.processed]),
                "events_pending": len([e for e in self.events if not e.processed])
            }
        
        @self.app.get("/api/events")
        async def list_events(credentials: HTTPAuthorizationCredentials = Depends(security)):
            if not self._verify_api_key(credentials):
                raise HTTPException(status_code=401, detail="Invalid API key")
            
            return {
                "events": [
                    {
                        "id": event.id,
                        "source": event.source,
                        "event_type": event.event_type,
                        "timestamp": event.timestamp.isoformat(),
                        "processed": event.processed
                    }
                    for event in self.events[-100:]  # Last 100 events
                ]
            }
        
        @self.app.post("/webhook/{source}")
        async def receive_webhook(
            source: str,
            request: Request,
            background_tasks: BackgroundTasks
        ):
            try:
                # Get request data
                body = await request.body()
                headers = dict(request.headers)
                
                # Verify signature if configured
                if source in self.webhook_secrets:
                    if not self._verify_signature(source, body, headers):
                        raise HTTPException(status_code=401, detail="Invalid signature")
                
                # Parse JSON data
                try:
                    data = json.loads(body.decode())
                except json.JSONDecodeError:
                    data = {"raw_body": body.decode()}
                
                # Create webhook event
                event = WebhookEvent(
                    id=self._generate_event_id(),
                    source=source,
                    event_type=self._detect_event_type(source, data, headers),
                    data=data,
                    timestamp=datetime.datetime.now(),
                    signature=headers.get("x-hub-signature-256") or headers.get("x-signature")
                )
                
                # Store event
                self.events.append(event)
                
                # Process event in background
                background_tasks.add_task(self._process_event, event)
                
                self.logger.info(f"Webhook received from {source}: {event.event_type}")
                
                return {
                    "status": "received",
                    "event_id": event.id,
                    "timestamp": event.timestamp.isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Webhook processing error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        # IFTTT specific endpoints
        @self.app.post("/ifttt/v1/triggers/new_task")
        async def ifttt_new_task_trigger(request: Request):
            return await self._handle_ifttt_trigger(request, "new_task")
        
        @self.app.post("/ifttt/v1/actions/add_task")
        async def ifttt_add_task_action(request: Request):
            return await self._handle_ifttt_action(request, "add_task")
    
    def start_server(self, background: bool = True):
        if not FASTAPI_AVAILABLE:
            raise WebhookError("FastAPI not available - cannot start webhook server")
        
        if self.is_running:
            self.logger.warning("Webhook server already running")
            return
        
        if background:
            self.server_thread = Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
        else:
            self._run_server()
        
        self.is_running = True
        self.logger.info(f"Webhook server started on {self.host}:{self.port}")
    
    def stop_server(self):
        self.is_running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)
        self.logger.info("Webhook server stopped")
    
    def _run_server(self):
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning"  # Reduce uvicorn logging
        )
    
    def add_webhook_secret(self, source: str, secret: str):
        self.webhook_secrets[source] = secret
        self.logger.info(f"Added webhook secret for {source}")
    
    def add_api_key(self, api_key: str):
        self.api_keys.append(api_key)
        self.logger.info("Added new API key")
    
    def register_handler(self, event_type: str, handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        self.logger.info(f"Registered handler for {event_type}")
    
    def _verify_signature(self, source: str, body: bytes, headers: Dict[str, str]) -> bool:
        secret = self.webhook_secrets.get(source)
        if not secret:
            return True  # No secret configured
        
        # GitHub style signature
        if "x-hub-signature-256" in headers:
            signature = headers["x-hub-signature-256"]
            expected = "sha256=" + hmac.new(
                secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected)
        
        # Generic signature
        if "x-signature" in headers:
            signature = headers["x-signature"]
            expected = hmac.new(
                secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected)
        
        return False
    
    def _verify_api_key(self, credentials: Optional[HTTPAuthorizationCredentials]) -> bool:
        if not credentials:
            return False
        
        return credentials.credentials in self.api_keys
    
    def _generate_event_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def _detect_event_type(self, source: str, data: Dict[str, Any], headers: Dict[str, str]) -> str:
        # GitHub events
        if source == "github":
            return headers.get("x-github-event", "unknown")
        
        # IFTTT events
        if source == "ifttt":
            return data.get("trigger", {}).get("event", "ifttt_trigger")
        
        # Zapier events
        if source == "zapier":
            return data.get("event_type", "zapier_trigger")
        
        # Generic events
        return data.get("event_type", f"{source}_event")
    
    async def _process_event(self, event: WebhookEvent):
        try:
            # Call registered handlers
            handlers = self.handlers.get(event.event_type, [])
            handlers.extend(self.handlers.get("*", []))  # Universal handlers
            
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    self.logger.error(f"Handler error for {event.event_type}: {e}")
            
            # Mark as processed
            event.processed = True
            
            self.logger.info(f"Processed event {event.id} from {event.source}")
            
        except Exception as e:
            self.logger.error(f"Event processing error: {e}")
    
    async def _handle_ifttt_trigger(self, request: Request, trigger_type: str):
        # IFTTT trigger implementation
        return {"data": []}
    
    async def _handle_ifttt_action(self, request: Request, action_type: str):
        # IFTTT action implementation
        return {"data": [{"id": "success"}]}


# Pre-built webhook handlers for common integrations

class LogbuchWebhookHandlers:
    def __init__(self, storage):
        self.storage = storage
        self.logger = get_logger("webhook_handlers")
    
    async def handle_github_push(self, event: WebhookEvent):
        if event.event_type == "push":
            commits = event.data.get("commits", [])
            repo_name = event.data.get("repository", {}).get("name", "Unknown")
            
            # Create task for code review
            task_content = f"Review {len(commits)} new commits in {repo_name}"
            self.storage.add_task(task_content, priority="medium", tags=["github", "code-review"])
            
            self.logger.info(f"Created task for GitHub push to {repo_name}")
    
    async def handle_ifttt_task(self, event: WebhookEvent):
        if event.source == "ifttt":
            task_content = event.data.get("task", {}).get("content")
            priority = event.data.get("task", {}).get("priority", "medium")
            
            if task_content:
                self.storage.add_task(task_content, priority=priority, tags=["ifttt"])
                self.logger.info(f"Created task from IFTTT: {task_content}")
    
    async def handle_zapier_journal(self, event: WebhookEvent):
        if event.source == "zapier":
            journal_text = event.data.get("journal", {}).get("text")
            
            if journal_text:
                self.storage.add_journal_entry(journal_text, tags=["zapier"])
                self.logger.info("Added journal entry from Zapier")
    
    async def handle_calendar_event(self, event: WebhookEvent):
        if "calendar" in event.source:
            event_data = event.data.get("event", {})
            title = event_data.get("title")
            start_time = event_data.get("start")
            
            if title and start_time:
                task_content = f"Prepare for: {title}"
                self.storage.add_task(
                    task_content,
                    priority="medium",
                    due_date=start_time,
                    tags=["calendar", "meeting"]
                )
                self.logger.info(f"Created task for calendar event: {title}")
    
    async def handle_email_task(self, event: WebhookEvent):
        if "email" in event.source:
            subject = event.data.get("subject", "")
            sender = event.data.get("from", "")
            
            if "TODO" in subject.upper() or "TASK" in subject.upper():
                task_content = f"Email task: {subject} (from {sender})"
                self.storage.add_task(task_content, priority="medium", tags=["email"])
                self.logger.info(f"Created task from email: {subject}")
    
    async def handle_smart_home(self, event: WebhookEvent):
        if event.source in ["homeassistant", "smartthings", "iot"]:
            device = event.data.get("device", "")
            action = event.data.get("action", "")
            
            if action == "low_battery":
                task_content = f"Replace battery in {device}"
                self.storage.add_task(task_content, priority="low", tags=["maintenance", "smart-home"])
                self.logger.info(f"Created maintenance task for {device}")
    
    def register_all_handlers(self, webhook_server: WebhookServer):
        webhook_server.register_handler("push", self.handle_github_push)
        webhook_server.register_handler("ifttt_trigger", self.handle_ifttt_task)
        webhook_server.register_handler("zapier_trigger", self.handle_zapier_journal)
        webhook_server.register_handler("calendar_event", self.handle_calendar_event)
        webhook_server.register_handler("email_received", self.handle_email_task)
        webhook_server.register_handler("device_alert", self.handle_smart_home)
