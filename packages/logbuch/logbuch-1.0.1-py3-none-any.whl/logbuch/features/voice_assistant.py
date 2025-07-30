#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/voice_assistant.py

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

from logbuch.core.logger import get_logger
from logbuch.core.config import get_config


@dataclass
class VoiceCommand:
    text: str
    confidence: float
    timestamp: float
    action: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class VoiceAssistant:
    def __init__(self):
        self.logger = get_logger("voice_assistant")
        self.config = get_config()
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-speech
        self.tts_engine = pyttsx3.init()
        self._configure_voice()
        
        # Voice processing
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.wake_words = ["hey logbuch", "logbuch", "productivity assistant"]
        
        # Command patterns
        self.command_patterns = {
            # Task management
            r"add task (.+)": "add_task",
            r"create task (.+)": "add_task", 
            r"new task (.+)": "add_task",
            r"complete task (.+)": "complete_task",
            r"finish task (.+)": "complete_task",
            r"done with (.+)": "complete_task",
            
            # Journal entries
            r"add journal (.+)": "add_journal",
            r"journal entry (.+)": "add_journal",
            r"write in journal (.+)": "add_journal",
            
            # Mood tracking
            r"i feel (.+)": "add_mood",
            r"my mood is (.+)": "add_mood",
            r"feeling (.+)": "add_mood",
            
            # Information queries
            r"what tasks do i have": "list_tasks",
            r"show my tasks": "list_tasks",
            r"what's on my todo": "list_tasks",
            r"how am i doing": "show_dashboard",
            r"show dashboard": "show_dashboard",
            r"productivity summary": "show_dashboard",
            
            # Smart suggestions
            r"give me suggestions": "get_suggestions",
            r"how can i improve": "get_suggestions",
            r"productivity tips": "get_suggestions",
            
            # Time management
            r"what's due today": "due_today",
            r"upcoming deadlines": "due_soon",
            r"overdue tasks": "overdue_tasks",
        }
        
        self.logger.debug("Voice Assistant initialized")
    
    def _configure_voice(self):
        voices = self.tts_engine.getProperty('voices')
        
        # Try to find a pleasant voice
        preferred_voices = ['samantha', 'alex', 'victoria', 'karen']
        
        for voice in voices:
            voice_name = voice.name.lower()
            if any(pref in voice_name for pref in preferred_voices):
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 180)  # Slightly faster than default
        self.tts_engine.setProperty('volume', 0.8)
    
    def speak(self, text: str, interrupt: bool = False):
        if interrupt:
            self.tts_engine.stop()
        
        self.logger.info(f"Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_for_wake_word(self) -> bool:
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
            
            text = self.recognizer.recognize_google(audio).lower()
            
            for wake_word in self.wake_words:
                if wake_word in text:
                    return True
            
            return False
            
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return False
    
    def listen_for_command(self, timeout: int = 5) -> Optional[VoiceCommand]:
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Give user feedback
            self.speak("I'm listening", interrupt=False)
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            confidence = 0.8  # Google Speech API doesn't provide confidence
            
            command = VoiceCommand(
                text=text,
                confidence=confidence,
                timestamp=time.time()
            )
            
            self.logger.info(f"Voice command received: {text}")
            return command
            
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that. Could you repeat?")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition error: {e}")
            self.speak("Sorry, I'm having trouble with speech recognition.")
            return None
        except sr.WaitTimeoutError:
            self.speak("I didn't hear anything. Try again when you're ready.")
            return None
    
    def parse_command(self, command: VoiceCommand) -> Optional[VoiceCommand]:
        import re
        
        text = command.text.lower()
        
        for pattern, action in self.command_patterns.items():
            match = re.search(pattern, text)
            if match:
                command.action = action
                command.parameters = {"match_groups": match.groups()}
                return command
        
        # If no pattern matches, try general intent recognition
        command.action = "unknown"
        command.parameters = {"original_text": command.text}
        return command
    
    def start_voice_mode(self, storage, callback: Optional[Callable] = None):
        self.is_listening = True
        self.speak("Voice assistant activated. Say 'Hey Logbuch' to give commands.")
        
        def voice_loop():
            while self.is_listening:
                try:
                    # Listen for wake word
                    if self.listen_for_wake_word():
                        # Listen for command
                        command = self.listen_for_command()
                        
                        if command:
                            # Parse and execute command
                            parsed_command = self.parse_command(command)
                            if parsed_command:
                                self.execute_voice_command(parsed_command, storage)
                                
                                if callback:
                                    callback(parsed_command)
                    
                    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Voice loop error: {e}")
                    time.sleep(1)
        
        # Start voice processing in background thread
        voice_thread = threading.Thread(target=voice_loop, daemon=True)
        voice_thread.start()
        
        return voice_thread
    
    def stop_voice_mode(self):
        self.is_listening = False
        self.speak("Voice assistant deactivated. Goodbye!")
    
    def execute_voice_command(self, command: VoiceCommand, storage):
        action = command.action
        params = command.parameters or {}
        
        try:
            if action == "add_task":
                task_content = params["match_groups"][0]
                storage.add_task(task_content, priority="medium")
                self.speak(f"Added task: {task_content}")
            
            elif action == "complete_task":
                task_query = params["match_groups"][0]
                # Find matching task (simplified)
                tasks = storage.get_tasks()
                for task in tasks:
                    if task_query.lower() in task['content'].lower() and not task.get('done'):
                        storage.complete_task(task['id'])
                        self.speak(f"Completed task: {task['content']}")
                        return
                self.speak(f"Couldn't find task: {task_query}")
            
            elif action == "add_journal":
                journal_text = params["match_groups"][0]
                storage.add_journal_entry(journal_text)
                self.speak("Journal entry added successfully")
            
            elif action == "add_mood":
                mood = params["match_groups"][0]
                storage.add_mood_entry(mood)
                self.speak(f"Recorded your mood as {mood}")
            
            elif action == "list_tasks":
                tasks = storage.get_tasks()
                incomplete_tasks = [t for t in tasks if not t.get('done')][:5]
                
                if incomplete_tasks:
                    task_list = ", ".join([t['content'] for t in incomplete_tasks])
                    self.speak(f"You have {len(incomplete_tasks)} tasks: {task_list}")
                else:
                    self.speak("You have no pending tasks. Great job!")
            
            elif action == "show_dashboard":
                tasks = storage.get_tasks()
                total_tasks = len(tasks)
                completed_tasks = len([t for t in tasks if t.get('done')])
                completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                
                self.speak(f"You have {total_tasks} total tasks with {completion_rate:.0f}% completion rate. You're doing great!")
            
            elif action == "get_suggestions":
                from logbuch.integrations.smart_suggestions import SmartSuggestionEngine
                engine = SmartSuggestionEngine()
                suggestions = engine.analyze_and_suggest(storage)
                
                if suggestions:
                    top_suggestion = suggestions[0]
                    self.speak(f"Here's my top suggestion: {top_suggestion.title}. {top_suggestion.description}")
                else:
                    self.speak("Your productivity setup looks great! No suggestions at this time.")
            
            elif action == "due_today":
                import datetime
                today = datetime.date.today()
                tasks = storage.get_tasks()
                due_today = []
                
                for task in tasks:
                    if not task.get('done') and task.get('due_date'):
                        try:
                            due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                            if due_date == today:
                                due_today.append(task)
                        except:
                            continue
                
                if due_today:
                    task_list = ", ".join([t['content'] for t in due_today])
                    self.speak(f"You have {len(due_today)} tasks due today: {task_list}")
                else:
                    self.speak("No tasks are due today. You're all caught up!")
            
            elif action == "overdue_tasks":
                import datetime
                today = datetime.date.today()
                tasks = storage.get_tasks()
                overdue = []
                
                for task in tasks:
                    if not task.get('done') and task.get('due_date'):
                        try:
                            due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                            if due_date < today:
                                overdue.append(task)
                        except:
                            continue
                
                if overdue:
                    self.speak(f"You have {len(overdue)} overdue tasks that need attention.")
                else:
                    self.speak("No overdue tasks. You're staying on top of things!")
            
            else:
                self.speak("I'm not sure how to help with that. Try asking about tasks, journal, or mood.")
        
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            self.speak("Sorry, I encountered an error while processing that command.")
    
    def dictate_journal_entry(self, storage) -> str:
        self.speak("I'm ready to take your journal entry. Speak naturally, and I'll transcribe everything.")
        
        full_text = []
        
        while True:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                self.speak("Go ahead, I'm listening.")
                
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                
                text = self.recognizer.recognize_google(audio)
                
                if "stop dictation" in text.lower() or "end journal" in text.lower():
                    break
                
                full_text.append(text)
                self.speak("Got it. Continue, or say 'stop dictation' when finished.")
                
            except sr.WaitTimeoutError:
                if full_text:
                    self.speak("Should I save what you've dictated so far?")
                    # Simple yes/no recognition would go here
                    break
                else:
                    self.speak("I didn't hear anything. Let's try again.")
            except Exception as e:
                self.logger.error(f"Dictation error: {e}")
                break
        
        if full_text:
            journal_text = " ".join(full_text)
            storage.add_journal_entry(journal_text, tags=["voice-dictated"])
            self.speak(f"Journal entry saved with {len(journal_text)} characters.")
            return journal_text
        else:
            self.speak("No journal entry was recorded.")
            return ""
    
    def voice_mood_checkin(self, storage):
        self.speak("Let's do a quick mood check-in. How are you feeling right now?")
        
        command = self.listen_for_command(timeout=10)
        if command:
            mood_text = command.text.lower()
            
            # Extract mood from natural speech
            mood_keywords = {
                'happy': ['happy', 'good', 'great', 'wonderful', 'fantastic', 'amazing'],
                'sad': ['sad', 'down', 'blue', 'depressed', 'low'],
                'stressed': ['stressed', 'overwhelmed', 'anxious', 'worried', 'tense'],
                'excited': ['excited', 'pumped', 'energetic', 'enthusiastic'],
                'tired': ['tired', 'exhausted', 'sleepy', 'drained'],
                'focused': ['focused', 'concentrated', 'sharp', 'clear'],
                'calm': ['calm', 'peaceful', 'relaxed', 'serene']
            }
            
            detected_mood = None
            for mood, keywords in mood_keywords.items():
                if any(keyword in mood_text for keyword in keywords):
                    detected_mood = mood
                    break
            
            if detected_mood:
                storage.add_mood_entry(detected_mood, notes=f"Voice check-in: {command.text}")
                self.speak(f"Thanks for sharing. I've recorded that you're feeling {detected_mood}.")
                
                # Provide contextual response
                if detected_mood in ['sad', 'stressed', 'tired']:
                    self.speak("Remember to take care of yourself. Maybe try a short break or some deep breathing.")
                elif detected_mood in ['happy', 'excited', 'focused']:
                    self.speak("That's wonderful! You're in a great state to tackle your tasks.")
            else:
                # Record the raw text as mood
                storage.add_mood_entry(command.text, notes="Voice check-in")
                self.speak("Thanks for sharing how you're feeling. I've recorded that.")
        else:
            self.speak("No problem, we can check in on your mood later.")


# Voice command decorators and utilities

def voice_enabled(func):
    def wrapper(*args, **kwargs):
        # Check if voice mode is requested
        if '--voice' in kwargs or kwargs.get('voice'):
            assistant = VoiceAssistant()
            assistant.speak(f"Voice mode activated for {func.__name__}")
        
        return func(*args, **kwargs)
    return wrapper


class VoiceCommandProcessor:
    def __init__(self, storage):
        self.storage = storage
        self.assistant = VoiceAssistant()
    
    def process_natural_language(self, text: str) -> str:
        text = text.lower()
        
        # Task management
        if "add" in text and "task" in text:
            task_content = text.replace("add task", "").replace("add a task", "").strip()
            return f"logbuch task '{task_content}'"
        
        # Journal entries
        if "journal" in text and ("add" in text or "write" in text):
            journal_content = text.replace("add journal", "").replace("write journal", "").strip()
            return f"logbuch journal '{journal_content}'"
        
        # Mood tracking
        if "mood" in text or "feeling" in text:
            mood = text.replace("i'm feeling", "").replace("my mood is", "").replace("feeling", "").strip()
            return f"logbuch mood {mood}"
        
        # Information queries
        if "show" in text and "tasks" in text:
            return "logbuch task --list"
        
        if "dashboard" in text:
            return "logbuch dashboard"
        
        return f"# Unrecognized command: {text}"
