#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/commuter_assistant.py

import datetime
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from logbuch.core.logger import get_logger


class TransportMode(Enum):
    TRAIN = "train"
    BUS = "bus"
    SUBWAY = "subway"
    TRAM = "tram"
    FERRY = "ferry"


class DelayStatus(Enum):
    ON_TIME = "on_time"
    MINOR_DELAY = "minor_delay"      # 1-5 minutes
    MODERATE_DELAY = "moderate_delay" # 6-15 minutes
    MAJOR_DELAY = "major_delay"      # 16-30 minutes
    SEVERE_DELAY = "severe_delay"    # 30+ minutes
    CANCELLED = "cancelled"


@dataclass
class CommuteRoute:
    route_id: str
    name: str
    from_station: str
    to_station: str
    transport_mode: TransportMode
    usual_departure_time: str  # HH:MM format
    usual_duration: int        # minutes
    line_number: Optional[str] = None
    operator: Optional[str] = None
    is_default: bool = False


@dataclass
class DelayInfo:
    route_id: str
    current_delay: int         # minutes
    status: DelayStatus
    reason: Optional[str]
    next_departure: Optional[datetime.datetime]
    alternative_routes: List[str]
    last_updated: datetime.datetime
    confidence: float          # 0.0 to 1.0


@dataclass
class CommuteAlert:
    alert_id: str
    route_id: str
    message: str
    severity: str
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime]


class CommuterAssistant:
    def __init__(self, storage):
        self.storage = storage
        self.logger = get_logger("commuter_assistant")
        
        # Load user's commute data
        self.routes = self._load_routes()
        self.delay_history = self._load_delay_history()
        self.preferences = self._load_preferences()
        
        # API configurations (would be configurable)
        self.api_configs = {
            'deutsche_bahn': {
                'base_url': 'https://api.deutschebahn.com/timetables/v1',
                'api_key': None  # User would configure
            },
            'transport_api': {
                'base_url': 'https://transportapi.com/v3',
                'api_key': None
            },
            'gtfs_realtime': {
                'feed_url': None  # Local transit feed
            }
        }
        
        self.logger.debug("Commuter Assistant initialized")
    
    def _load_routes(self) -> List[CommuteRoute]:
        try:
            from pathlib import Path
            routes_file = Path.home() / ".logbuch" / "commute_routes.json"
            
            if routes_file.exists():
                with open(routes_file, 'r') as f:
                    data = json.load(f)
                    routes = []
                    for item in data:
                        item['transport_mode'] = TransportMode(item['transport_mode'])
                        routes.append(CommuteRoute(**item))
                    return routes
        except Exception as e:
            self.logger.debug(f"Could not load routes: {e}")
        
        return []
    
    def _save_routes(self):
        try:
            from pathlib import Path
            routes_file = Path.home() / ".logbuch" / "commute_routes.json"
            routes_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = []
            for route in self.routes:
                route_dict = asdict(route)
                route_dict['transport_mode'] = route.transport_mode.value
                data.append(route_dict)
            
            with open(routes_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save routes: {e}")
    
    def _load_delay_history(self) -> List[Dict]:
        try:
            from pathlib import Path
            history_file = Path.home() / ".logbuch" / "delay_history.json"
            
            if history_file.exists():
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.debug(f"Could not load delay history: {e}")
        
        return []
    
    def _load_preferences(self) -> Dict:
        return {
            'notification_threshold': 5,  # minutes
            'check_frequency': 15,        # minutes before departure
            'preferred_alternatives': True,
            'include_weather_impact': True,
            'alert_for_cancellations': True
        }
    
    def add_route(self, name: str, from_station: str, to_station: str,
                  transport_mode: str, departure_time: str, duration: int,
                  line_number: str = None, operator: str = None,
                  set_as_default: bool = False) -> str:
        route_id = f"route_{len(self.routes) + 1}_{datetime.datetime.now().strftime('%Y%m%d')}"
        
        # If this is the first route or explicitly set as default
        is_default = set_as_default or len(self.routes) == 0
        
        # If setting as default, unset other defaults
        if is_default:
            for route in self.routes:
                route.is_default = False
        
        new_route = CommuteRoute(
            route_id=route_id,
            name=name,
            from_station=from_station,
            to_station=to_station,
            transport_mode=TransportMode(transport_mode),
            usual_departure_time=departure_time,
            usual_duration=duration,
            line_number=line_number,
            operator=operator,
            is_default=is_default
        )
        
        self.routes.append(new_route)
        self._save_routes()
        
        self.logger.info(f"Added commute route: {name}")
        return route_id
    
    def check_delays(self, route_id: Optional[str] = None) -> DelayInfo:
        # Use default route if none specified
        if route_id is None:
            default_routes = [r for r in self.routes if r.is_default]
            if not default_routes:
                raise ValueError("No default route set. Add a route first!")
            route = default_routes[0]
        else:
            route = next((r for r in self.routes if r.route_id == route_id), None)
            if not route:
                raise ValueError(f"Route {route_id} not found")
        
        # Get real-time delay information
        delay_info = self._fetch_delay_info(route)
        
        # Save to history for pattern analysis
        self._save_delay_to_history(route, delay_info)
        
        return delay_info
    
    def _fetch_delay_info(self, route: CommuteRoute) -> DelayInfo:
        # Mock implementation - in reality would call transport APIs
        import random
        
        # Simulate realistic delay patterns
        delay_minutes = self._simulate_realistic_delay()
        
        # Determine status based on delay
        if delay_minutes == -1:  # Cancelled
            status = DelayStatus.CANCELLED
        elif delay_minutes <= 2:
            status = DelayStatus.ON_TIME
        elif delay_minutes <= 5:
            status = DelayStatus.MINOR_DELAY
        elif delay_minutes <= 15:
            status = DelayStatus.MODERATE_DELAY
        elif delay_minutes <= 30:
            status = DelayStatus.MAJOR_DELAY
        else:
            status = DelayStatus.SEVERE_DELAY
        
        # Generate realistic delay reasons
        delay_reasons = [
            "Signal failure",
            "Technical difficulties",
            "Staff shortage",
            "Weather conditions",
            "Track maintenance",
            "Previous train delays",
            "Passenger incident",
            "Infrastructure issues"
        ]
        
        reason = random.choice(delay_reasons) if delay_minutes > 2 else None
        
        # Calculate next departure
        now = datetime.datetime.now()
        departure_time = datetime.datetime.strptime(route.usual_departure_time, "%H:%M").time()
        next_departure = datetime.datetime.combine(now.date(), departure_time)
        
        if next_departure < now:
            next_departure += datetime.timedelta(days=1)
        
        if delay_minutes > 0:
            next_departure += datetime.timedelta(minutes=delay_minutes)
        
        return DelayInfo(
            route_id=route.route_id,
            current_delay=max(0, delay_minutes),  # Don't show negative delays
            status=status,
            reason=reason,
            next_departure=next_departure if status != DelayStatus.CANCELLED else None,
            alternative_routes=[],  # Would be populated with real alternatives
            last_updated=datetime.datetime.now(),
            confidence=random.uniform(0.8, 0.95)
        )
    
    def _simulate_realistic_delay(self) -> int:
        import random
        
        # Realistic delay distribution based on real train data
        delay_probabilities = [
            (0, 0.6),    # 60% on time
            (2, 0.15),   # 15% minor delay
            (5, 0.10),   # 10% moderate delay
            (10, 0.08),  # 8% significant delay
            (20, 0.04),  # 4% major delay
            (45, 0.02),  # 2% severe delay
            (-1, 0.01),  # 1% cancelled
        ]
        
        rand = random.random()
        cumulative = 0
        
        for delay, probability in delay_probabilities:
            cumulative += probability
            if rand <= cumulative:
                if delay == -1:
                    return -1  # Cancelled
                return delay + random.randint(0, 3)  # Add some variance
        
        return 0  # Default to on time
    
    def _save_delay_to_history(self, route: CommuteRoute, delay_info: DelayInfo):
        history_entry = {
            'route_id': route.route_id,
            'date': datetime.datetime.now().date().isoformat(),
            'time': datetime.datetime.now().time().isoformat(),
            'delay_minutes': delay_info.current_delay,
            'status': delay_info.status.value,
            'reason': delay_info.reason,
            'day_of_week': datetime.datetime.now().strftime('%A'),
            'weather': None  # Could integrate with weather API
        }
        
        self.delay_history.append(history_entry)
        
        # Keep only last 90 days of history
        cutoff_date = datetime.date.today() - datetime.timedelta(days=90)
        self.delay_history = [
            h for h in self.delay_history 
            if datetime.date.fromisoformat(h['date']) >= cutoff_date
        ]
        
        # Save to file
        try:
            from pathlib import Path
            history_file = Path.home() / ".logbuch" / "delay_history.json"
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(history_file, 'w') as f:
                json.dump(self.delay_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save delay history: {e}")
    
    def quick_check(self) -> str:
        try:
            delay_info = self.check_delays()
            
            if not delay_info:
                return "❌ No route configured. Set up your commute first!"
            
            # Get the route info
            route = next((r for r in self.routes if r.route_id == delay_info.route_id), None)
            
            if delay_info.status == DelayStatus.CANCELLED:
                return f"🚫 CANCELLED: Your {route.name if route else 'train'} is cancelled! Reason: {delay_info.reason}"
            
            elif delay_info.status == DelayStatus.ON_TIME:
                return f"✅ ON TIME: Your {route.name if route else 'train'} is running on schedule!"
            
            else:
                delay_emoji = {
                    DelayStatus.MINOR_DELAY: "⏰",
                    DelayStatus.MODERATE_DELAY: "🕐", 
                    DelayStatus.MAJOR_DELAY: "⏳",
                    DelayStatus.SEVERE_DELAY: "🚨"
                }.get(delay_info.status, "⏰")
                
                return f"{delay_emoji} DELAYED: Your {route.name if route else 'train'} is {delay_info.current_delay} minutes late! Reason: {delay_info.reason or 'Unknown'}"
        
        except Exception as e:
            return f"❌ Error checking delays: {e}"
    
    def get_delay_patterns(self, route_id: Optional[str] = None) -> Dict[str, Any]:
        # Filter history for specific route or all routes
        if route_id:
            history = [h for h in self.delay_history if h['route_id'] == route_id]
        else:
            history = self.delay_history
        
        if not history:
            return {"error": "No delay history available"}
        
        # Analyze patterns
        total_delays = len(history)
        on_time_count = len([h for h in history if h['delay_minutes'] <= 2])
        delayed_count = total_delays - on_time_count
        
        # Average delay
        avg_delay = sum(h['delay_minutes'] for h in history) / total_delays
        
        # Worst days of week
        day_delays = {}
        for entry in history:
            day = entry['day_of_week']
            if day not in day_delays:
                day_delays[day] = []
            day_delays[day].append(entry['delay_minutes'])
        
        day_averages = {
            day: sum(delays) / len(delays) 
            for day, delays in day_delays.items()
        }
        
        worst_day = max(day_averages.items(), key=lambda x: x[1]) if day_averages else None
        best_day = min(day_averages.items(), key=lambda x: x[1]) if day_averages else None
        
        # Most common delay reasons
        reasons = [h['reason'] for h in history if h['reason']]
        reason_counts = {}
        for reason in reasons:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        most_common_reason = max(reason_counts.items(), key=lambda x: x[1]) if reason_counts else None
        
        return {
            'total_journeys': total_delays,
            'on_time_rate': on_time_count / total_delays if total_delays > 0 else 0,
            'delay_rate': delayed_count / total_delays if total_delays > 0 else 0,
            'average_delay': avg_delay,
            'worst_day': worst_day,
            'best_day': best_day,
            'most_common_reason': most_common_reason,
            'day_averages': day_averages
        }
    
    def get_commute_dashboard(self) -> Dict[str, Any]:
        # Current delay status
        current_status = None
        try:
            delay_info = self.check_delays()
            current_status = {
                'delay_minutes': delay_info.current_delay,
                'status': delay_info.status.value,
                'reason': delay_info.reason,
                'next_departure': delay_info.next_departure.isoformat() if delay_info.next_departure else None
            }
        except Exception as e:
            current_status = {'error': str(e)}
        
        # Delay patterns
        patterns = self.get_delay_patterns()
        
        # Route information
        routes_info = []
        for route in self.routes:
            routes_info.append({
                'id': route.route_id,
                'name': route.name,
                'from': route.from_station,
                'to': route.to_station,
                'mode': route.transport_mode.value,
                'departure': route.usual_departure_time,
                'duration': route.usual_duration,
                'is_default': route.is_default
            })
        
        return {
            'current_status': current_status,
            'delay_patterns': patterns,
            'routes': routes_info,
            'quick_check_result': self.quick_check(),
            'last_updated': datetime.datetime.now().isoformat()
        }


# Export for CLI integration
__all__ = ['CommuterAssistant', 'CommuteRoute', 'DelayInfo', 'TransportMode', 'DelayStatus']
