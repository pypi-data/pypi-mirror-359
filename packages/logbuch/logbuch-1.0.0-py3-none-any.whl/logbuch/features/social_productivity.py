#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/social_productivity.py

import datetime
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random

from logbuch.core.logger import get_logger


class SocialRole(Enum):
    BUDDY = "buddy"                    # Accountability partner
    MENTOR = "mentor"                  # Guides others
    MENTEE = "mentee"                  # Learning from others
    TEAMMATE = "teammate"              # Team member
    COMPETITOR = "competitor"          # Friendly competition
    COACH = "coach"                    # Professional coach


@dataclass
class ProductivityBuddy:
    user_id: str
    username: str
    role: SocialRole
    connection_date: datetime.datetime
    shared_goals: List[str]
    accountability_score: float
    last_interaction: datetime.datetime
    mutual_achievements: int
    support_given: int
    support_received: int


@dataclass
class TeamChallenge:
    challenge_id: str
    title: str
    description: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    participants: List[str]
    challenge_type: str  # daily, weekly, monthly
    target_metric: str   # tasks, xp, streak, etc.
    target_value: int
    current_progress: Dict[str, int]
    rewards: Dict[str, int]  # XP rewards
    status: str  # active, completed, cancelled


@dataclass
class SocialAchievement:
    achievement_id: str
    title: str
    description: str
    earned_date: datetime.datetime
    rarity: str
    category: str
    public: bool
    likes: int
    comments: List[Dict]
    shared_with: List[str]


class SocialProductivityNetwork:
    def __init__(self, storage, user_id: Optional[str] = None):
        self.storage = storage
        self.user_id = user_id or self._generate_user_id()
        self.logger = get_logger("social_productivity")
        
        # Social data
        self.buddies = self._load_buddies()
        self.team_challenges = self._load_team_challenges()
        self.social_achievements = self._load_social_achievements()
        
        # Social settings
        self.public_profile = True
        self.share_achievements = True
        self.allow_buddy_requests = True
        self.participate_in_challenges = True
        
        self.logger.debug("Social Productivity Network initialized")
    
    def _generate_user_id(self) -> str:
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _load_buddies(self) -> List[ProductivityBuddy]:
        try:
            from pathlib import Path
            buddies_file = Path.home() / ".logbuch" / "social_buddies.json"
            
            if buddies_file.exists():
                with open(buddies_file, 'r') as f:
                    data = json.load(f)
                    buddies = []
                    for item in data:
                        item['connection_date'] = datetime.datetime.fromisoformat(item['connection_date'])
                        item['last_interaction'] = datetime.datetime.fromisoformat(item['last_interaction'])
                        item['role'] = SocialRole(item['role'])
                        buddies.append(ProductivityBuddy(**item))
                    return buddies
        except Exception as e:
            self.logger.debug(f"Could not load buddies: {e}")
        
        return []
    
    def _save_buddies(self):
        try:
            from pathlib import Path
            buddies_file = Path.home() / ".logbuch" / "social_buddies.json"
            buddies_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = []
            for buddy in self.buddies:
                buddy_dict = asdict(buddy)
                buddy_dict['connection_date'] = buddy.connection_date.isoformat()
                buddy_dict['last_interaction'] = buddy.last_interaction.isoformat()
                buddy_dict['role'] = buddy.role.value
                data.append(buddy_dict)
            
            with open(buddies_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save buddies: {e}")
    
    def _load_team_challenges(self) -> List[TeamChallenge]:
        # Mock data for now - would connect to real social platform
        return [
            TeamChallenge(
                challenge_id="weekly_warrior_001",
                title="Weekly Warrior Challenge",
                description="Complete 25 tasks this week",
                start_date=datetime.datetime.now() - datetime.timedelta(days=2),
                end_date=datetime.datetime.now() + datetime.timedelta(days=5),
                participants=["user123", "user456", self.user_id],
                challenge_type="weekly",
                target_metric="tasks_completed",
                target_value=25,
                current_progress={
                    "user123": 18,
                    "user456": 22,
                    self.user_id: 15
                },
                rewards={"winner": 500, "participant": 100},
                status="active"
            )
        ]
    
    def _load_social_achievements(self) -> List[SocialAchievement]:
        # Mock data - would sync with real social platform
        return []
    
    def find_productivity_buddies(self, criteria: Dict[str, Any]) -> List[Dict]:
        # Mock buddy suggestions - would use real matching algorithm
        potential_buddies = [
            {
                "user_id": "prod_master_2024",
                "username": "ProductivityMaster",
                "compatibility_score": 0.92,
                "shared_interests": ["time_management", "goal_setting", "habit_formation"],
                "productivity_level": "advanced",
                "timezone": "UTC-8",
                "preferred_role": "mentor",
                "achievements": 47,
                "current_streak": 23
            },
            {
                "user_id": "focus_ninja_99",
                "username": "FocusNinja",
                "compatibility_score": 0.87,
                "shared_interests": ["deep_work", "pomodoro", "minimalism"],
                "productivity_level": "intermediate",
                "timezone": "UTC-5",
                "preferred_role": "buddy",
                "achievements": 31,
                "current_streak": 12
            },
            {
                "user_id": "goal_crusher_x",
                "username": "GoalCrusher",
                "compatibility_score": 0.84,
                "shared_interests": ["goal_achievement", "tracking", "analytics"],
                "productivity_level": "advanced",
                "timezone": "UTC+1",
                "preferred_role": "competitor",
                "achievements": 52,
                "current_streak": 31
            }
        ]
        
        return potential_buddies
    
    def send_buddy_request(self, target_user_id: str, message: str = "") -> bool:
        try:
            # Mock implementation - would send real request
            self.logger.info(f"Buddy request sent to {target_user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send buddy request: {e}")
            return False
    
    def accept_buddy_request(self, requester_id: str) -> bool:
        try:
            # Create new buddy relationship
            new_buddy = ProductivityBuddy(
                user_id=requester_id,
                username=f"User_{requester_id[:6]}",  # Would get real username
                role=SocialRole.BUDDY,
                connection_date=datetime.datetime.now(),
                shared_goals=[],
                accountability_score=0.0,
                last_interaction=datetime.datetime.now(),
                mutual_achievements=0,
                support_given=0,
                support_received=0
            )
            
            self.buddies.append(new_buddy)
            self._save_buddies()
            
            self.logger.info(f"Buddy request accepted from {requester_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to accept buddy request: {e}")
            return False
    
    def create_team_challenge(self, challenge_data: Dict) -> str:
        challenge_id = f"challenge_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        challenge = TeamChallenge(
            challenge_id=challenge_id,
            title=challenge_data['title'],
            description=challenge_data['description'],
            start_date=datetime.datetime.fromisoformat(challenge_data['start_date']),
            end_date=datetime.datetime.fromisoformat(challenge_data['end_date']),
            participants=challenge_data.get('participants', [self.user_id]),
            challenge_type=challenge_data['type'],
            target_metric=challenge_data['metric'],
            target_value=challenge_data['target'],
            current_progress={},
            rewards=challenge_data.get('rewards', {"winner": 200, "participant": 50}),
            status="active"
        )
        
        self.team_challenges.append(challenge)
        return challenge_id
    
    def join_team_challenge(self, challenge_id: str) -> bool:
        for challenge in self.team_challenges:
            if challenge.challenge_id == challenge_id:
                if self.user_id not in challenge.participants:
                    challenge.participants.append(self.user_id)
                    challenge.current_progress[self.user_id] = 0
                    return True
        return False
    
    def update_challenge_progress(self, challenge_id: str, progress: int) -> bool:
        for challenge in self.team_challenges:
            if challenge.challenge_id == challenge_id:
                challenge.current_progress[self.user_id] = progress
                return True
        return False
    
    def share_achievement(self, achievement_data: Dict) -> str:
        achievement_id = f"social_ach_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        social_achievement = SocialAchievement(
            achievement_id=achievement_id,
            title=achievement_data['title'],
            description=achievement_data['description'],
            earned_date=datetime.datetime.now(),
            rarity=achievement_data.get('rarity', 'common'),
            category=achievement_data.get('category', 'general'),
            public=achievement_data.get('public', True),
            likes=0,
            comments=[],
            shared_with=achievement_data.get('shared_with', [])
        )
        
        self.social_achievements.append(social_achievement)
        return achievement_id
    
    def get_social_feed(self) -> List[Dict]:
        feed_items = []
        
        # Buddy achievements
        for buddy in self.buddies:
            # Mock buddy activities
            feed_items.append({
                "type": "buddy_achievement",
                "user": buddy.username,
                "content": f"{buddy.username} completed their daily goal!",
                "timestamp": datetime.datetime.now() - datetime.timedelta(hours=2),
                "likes": random.randint(3, 15),
                "can_like": True,
                "can_comment": True
            })
        
        # Challenge updates
        for challenge in self.team_challenges:
            if challenge.status == "active":
                leader = max(challenge.current_progress.items(), key=lambda x: x[1])
                feed_items.append({
                    "type": "challenge_update",
                    "content": f"Challenge '{challenge.title}': {leader[0]} is leading with {leader[1]} points!",
                    "timestamp": datetime.datetime.now() - datetime.timedelta(hours=1),
                    "challenge_id": challenge.challenge_id,
                    "can_join": self.user_id not in challenge.participants
                })
        
        # Motivational content
        feed_items.append({
            "type": "motivation",
            "content": "💪 Remember: Progress, not perfection. Every small step counts!",
            "timestamp": datetime.datetime.now() - datetime.timedelta(minutes=30),
            "likes": random.randint(10, 50),
            "can_like": True
        })
        
        # Sort by timestamp
        feed_items.sort(key=lambda x: x['timestamp'], reverse=True)
        return feed_items[:10]  # Return latest 10 items
    
    def get_leaderboard(self, timeframe: str = "weekly") -> List[Dict]:
        # Mock leaderboard data
        leaderboard = [
            {
                "rank": 1,
                "user_id": "productivity_king",
                "username": "ProductivityKing",
                "score": 2847,
                "achievements": 67,
                "streak": 45,
                "is_buddy": False,
                "is_self": False
            },
            {
                "rank": 2,
                "user_id": "focus_master_pro",
                "username": "FocusMasterPro",
                "score": 2634,
                "achievements": 59,
                "streak": 32,
                "is_buddy": True,
                "is_self": False
            },
            {
                "rank": 3,
                "user_id": self.user_id,
                "username": "You",
                "score": 2456,
                "achievements": 45,
                "streak": 28,
                "is_buddy": False,
                "is_self": True
            },
            {
                "rank": 4,
                "user_id": "goal_ninja_2024",
                "username": "GoalNinja2024",
                "score": 2398,
                "achievements": 52,
                "streak": 19,
                "is_buddy": True,
                "is_self": False
            }
        ]
        
        return leaderboard
    
    def send_encouragement(self, buddy_id: str, message: str) -> bool:
        try:
            # Find the buddy
            buddy = next((b for b in self.buddies if b.user_id == buddy_id), None)
            if not buddy:
                return False
            
            # Update interaction data
            buddy.last_interaction = datetime.datetime.now()
            buddy.support_given += 1
            
            # Mock sending message
            self.logger.info(f"Encouragement sent to {buddy.username}: {message}")
            self._save_buddies()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to send encouragement: {e}")
            return False
    
    def request_accountability_check(self, buddy_id: str, goal: str) -> bool:
        try:
            buddy = next((b for b in self.buddies if b.user_id == buddy_id), None)
            if not buddy:
                return False
            
            # Mock accountability request
            self.logger.info(f"Accountability check requested from {buddy.username} for goal: {goal}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to request accountability check: {e}")
            return False
    
    def get_social_dashboard(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "buddies": len(self.buddies),
            "active_challenges": len([c for c in self.team_challenges if c.status == "active"]),
            "social_achievements": len(self.social_achievements),
            "social_feed": self.get_social_feed()[:5],
            "leaderboard_position": 3,  # Mock position
            "buddy_suggestions": self.find_productivity_buddies({})[:3],
            "settings": {
                "public_profile": self.public_profile,
                "share_achievements": self.share_achievements,
                "allow_buddy_requests": self.allow_buddy_requests,
                "participate_in_challenges": self.participate_in_challenges
            },
            "stats": {
                "total_encouragements_sent": sum(b.support_given for b in self.buddies),
                "total_encouragements_received": sum(b.support_received for b in self.buddies),
                "average_accountability_score": sum(b.accountability_score for b in self.buddies) / len(self.buddies) if self.buddies else 0
            }
        }


# Export for CLI integration
__all__ = ['SocialProductivityNetwork', 'ProductivityBuddy', 'TeamChallenge', 'SocialAchievement', 'SocialRole']
