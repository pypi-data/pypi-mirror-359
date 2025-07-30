#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# tests/test_commuter_assistant.py


import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from tests.test_mocks import MockStorage, MockConfig
from logbuch.commands.task import add_task, list_tasks
from logbuch.commands.journal import add_journal_entry, list_journal_entries


class TestLocationBasedFeatures:
    def test_location_aware_task_creation(self, mock_storage):
        # Mock location data
        mock_location = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'address': 'San Francisco, CA',
            'context': 'work'
        }
        
        with patch('logbuch.features.location.get_current_location', return_value=mock_location):
            # Add task with location context
            task_id = add_task(
                mock_storage, 
                "Pick up coffee on the way to work",
                tags=["commute", "coffee"],
                location_context=True
            )
            
            assert task_id is not None
            
            # Verify task was created with location context
            tasks = list_tasks(mock_storage)
            task = next((t for t in tasks if t['id'] == task_id), None)
            assert task is not None
            assert "commute" in task['tags']
    
    def test_proximity_based_task_suggestions(self, mock_storage):
        # Add location-tagged tasks
        add_task(mock_storage, "Buy groceries", tags=["shopping", "grocery_store"])
        add_task(mock_storage, "Pick up dry cleaning", tags=["errands", "dry_cleaner"])
        add_task(mock_storage, "Get gas", tags=["car", "gas_station"])
        add_task(mock_storage, "Work meeting", tags=["work", "office"])
        
        # Mock current location near shopping area
        mock_location = {
            'latitude': 37.7849,
            'longitude': -122.4094,
            'nearby_places': ['grocery_store', 'gas_station']
        }
        
        with patch('logbuch.features.location.get_current_location', return_value=mock_location):
            with patch('logbuch.features.location.get_nearby_tasks') as mock_nearby:
                # Mock nearby tasks based on location
                nearby_tasks = [
                    {'id': 1, 'content': 'Buy groceries', 'tags': ['shopping', 'grocery_store']},
                    {'id': 3, 'content': 'Get gas', 'tags': ['car', 'gas_station']}
                ]
                mock_nearby.return_value = nearby_tasks
                
                # Get location-based suggestions
                suggestions = mock_nearby(mock_storage, mock_location)
                
                assert len(suggestions) == 2
                assert any('groceries' in task['content'] for task in suggestions)
                assert any('gas' in task['content'] for task in suggestions)
    
    def test_commute_route_optimization(self, mock_storage):
        # Add tasks with different locations
        tasks_with_locations = [
            ("Post office - mail package", ["errands"], "post_office"),
            ("Bank - deposit check", ["finance"], "bank"),
            ("Pharmacy - pick up prescription", ["health"], "pharmacy"),
            ("Home - start point", ["home"], "home"),
            ("Office - end point", ["work"], "office")
        ]
        
        task_ids = []
        for content, tags, location in tasks_with_locations:
            task_id = add_task(mock_storage, content, tags=tags)
            task_ids.append((task_id, location))
        
        # Mock route optimization
        with patch('logbuch.features.commuter.optimize_route') as mock_optimize:
            optimized_route = [
                {'task_id': task_ids[3][0], 'location': 'home', 'order': 1},
                {'task_id': task_ids[0][0], 'location': 'post_office', 'order': 2},
                {'task_id': task_ids[1][0], 'location': 'bank', 'order': 3},
                {'task_id': task_ids[2][0], 'location': 'pharmacy', 'order': 4},
                {'task_id': task_ids[4][0], 'location': 'office', 'order': 5}
            ]
            mock_optimize.return_value = optimized_route
            
            # Get optimized route
            route = mock_optimize(task_ids)
            
            assert len(route) == 5
            assert route[0]['location'] == 'home'  # Start at home
            assert route[-1]['location'] == 'office'  # End at office
            
            # Verify order is logical
            orders = [stop['order'] for stop in route]
            assert orders == sorted(orders)


class TestTravelTimeCalculations:
    def test_travel_time_estimation(self, mock_storage):
        # Mock travel time API
        with patch('logbuch.features.commuter.get_travel_time') as mock_travel_time:
            mock_travel_time.return_value = {
                'duration_minutes': 25,
                'distance_km': 15.2,
                'mode': 'driving',
                'traffic_factor': 1.3  # 30% slower due to traffic
            }
            
            # Calculate travel time
            travel_info = mock_travel_time('home', 'office')
            
            assert travel_info['duration_minutes'] == 25
            assert travel_info['distance_km'] == 15.2
            assert travel_info['traffic_factor'] > 1.0  # Traffic delay
    
    def test_commute_time_based_reminders(self, mock_storage):
        # Add time-sensitive task
        task_id = add_task(
            mock_storage,
            "Important 9 AM meeting",
            tags=["work", "meeting"],
            due_time="09:00"
        )
        
        # Mock current time and travel time
        mock_now = datetime(2024, 1, 15, 8, 10)  # 8:10 AM
        mock_travel_time = 35  # 35 minutes to get to work
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            
            with patch('logbuch.features.commuter.get_travel_time_to_work', return_value=mock_travel_time):
                with patch('logbuch.features.commuter.should_leave_now') as mock_should_leave:
                    # Should suggest leaving soon (meeting at 9, travel time 35 min, current time 8:10)
                    mock_should_leave.return_value = {
                        'should_leave': True,
                        'leave_time': '08:15',
                        'buffer_minutes': 10,
                        'reason': 'Meeting in 50 minutes, travel time 35 minutes'
                    }
                    
                    reminder = mock_should_leave(task_id, mock_now)
                    
                    assert reminder['should_leave'] is True
                    assert '08:15' in reminder['leave_time']
    
    def test_traffic_aware_scheduling(self, mock_storage):
        # Add tasks with different time sensitivities
        morning_task = add_task(mock_storage, "Morning meeting", tags=["work"], due_time="09:00")
        flexible_task = add_task(mock_storage, "Grocery shopping", tags=["errands"])
        evening_task = add_task(mock_storage, "Dinner reservation", tags=["personal"], due_time="19:30")
        
        # Mock traffic data
        traffic_data = {
            'morning_rush': {'start': '07:00', 'end': '09:30', 'delay_factor': 1.5},
            'evening_rush': {'start': '17:00', 'end': '19:00', 'delay_factor': 1.4},
            'off_peak': {'delay_factor': 1.0}
        }
        
        with patch('logbuch.features.commuter.get_traffic_data', return_value=traffic_data):
            with patch('logbuch.features.commuter.optimize_schedule') as mock_optimize:
                optimized_schedule = [
                    {'task_id': morning_task, 'suggested_time': '08:00', 'traffic_factor': 1.5},
                    {'task_id': flexible_task, 'suggested_time': '14:00', 'traffic_factor': 1.0},
                    {'task_id': evening_task, 'suggested_time': '18:30', 'traffic_factor': 1.4}
                ]
                mock_optimize.return_value = optimized_schedule
                
                schedule = mock_optimize([morning_task, flexible_task, evening_task])
                
                assert len(schedule) == 3
                # Flexible task should be scheduled during off-peak hours
                flexible_schedule = next(s for s in schedule if s['task_id'] == flexible_task)
                assert flexible_schedule['traffic_factor'] == 1.0


class TestPublicTransportIntegration:
    def test_transit_schedule_integration(self, mock_storage):
        # Add commute-related task
        task_id = add_task(
            mock_storage,
            "Catch 8:15 train to downtown",
            tags=["commute", "train"]
        )
        
        # Mock transit API
        with patch('logbuch.features.transit.get_next_departures') as mock_departures:
            mock_departures.return_value = [
                {'time': '08:15', 'line': 'Blue Line', 'platform': '2', 'delay': 0},
                {'time': '08:30', 'line': 'Blue Line', 'platform': '2', 'delay': 2},
                {'time': '08:45', 'line': 'Blue Line', 'platform': '2', 'delay': 0}
            ]
            
            departures = mock_departures('downtown_station')
            
            assert len(departures) == 3
            assert departures[0]['time'] == '08:15'
            assert departures[1]['delay'] == 2  # 2 minute delay
    
    def test_transit_disruption_notifications(self, mock_storage):
        # Add transit-dependent tasks
        add_task(mock_storage, "Morning commute", tags=["commute", "train"])
        add_task(mock_storage, "Client meeting downtown", tags=["work", "meeting"])
        
        # Mock transit disruption
        disruption_data = {
            'line': 'Blue Line',
            'status': 'delayed',
            'delay_minutes': 15,
            'reason': 'Signal problems',
            'alternative_routes': ['Red Line + Bus 42', 'Green Line']
        }
        
        with patch('logbuch.features.transit.get_service_alerts', return_value=[disruption_data]):
            with patch('logbuch.features.commuter.get_affected_tasks') as mock_affected:
                affected_tasks = [
                    {'id': 1, 'content': 'Morning commute', 'impact': 'high'},
                    {'id': 2, 'content': 'Client meeting downtown', 'impact': 'medium'}
                ]
                mock_affected.return_value = affected_tasks
                
                alerts = mock_affected(mock_storage, disruption_data)
                
                assert len(alerts) == 2
                assert any(task['impact'] == 'high' for task in alerts)
    
    def test_multimodal_journey_planning(self, mock_storage):
        # Add complex journey task
        task_id = add_task(
            mock_storage,
            "Get to airport for 2 PM flight",
            tags=["travel", "airport"],
            due_time="14:00"
        )
        
        # Mock multimodal journey
        with patch('logbuch.features.transit.plan_multimodal_journey') as mock_journey:
            journey_plan = {
                'total_duration': 75,  # 75 minutes
                'legs': [
                    {'mode': 'walk', 'duration': 5, 'from': 'home', 'to': 'metro_station'},
                    {'mode': 'metro', 'duration': 25, 'from': 'metro_station', 'to': 'central_station'},
                    {'mode': 'train', 'duration': 35, 'from': 'central_station', 'to': 'airport_station'},
                    {'mode': 'walk', 'duration': 10, 'from': 'airport_station', 'to': 'airport_terminal'}
                ],
                'departure_time': '12:15',
                'arrival_time': '13:30'
            }
            mock_journey.return_value = journey_plan
            
            plan = mock_journey('home', 'airport', '14:00')
            
            assert plan['total_duration'] == 75
            assert len(plan['legs']) == 4
            assert plan['departure_time'] == '12:15'
            assert plan['arrival_time'] == '13:30'


class TestWeatherIntegration:
    def test_weather_based_task_suggestions(self, mock_storage):
        # Add weather-dependent tasks
        add_task(mock_storage, "Wash car", tags=["car", "outdoor"])
        add_task(mock_storage, "Go for a run", tags=["exercise", "outdoor"])
        add_task(mock_storage, "Indoor workout", tags=["exercise", "indoor"])
        add_task(mock_storage, "Grocery shopping", tags=["errands", "indoor"])
        
        # Mock weather data
        weather_data = {
            'condition': 'rain',
            'temperature': 15,
            'precipitation_probability': 80,
            'wind_speed': 25,
            'visibility': 'poor'
        }
        
        with patch('logbuch.features.weather.get_current_weather', return_value=weather_data):
            with patch('logbuch.features.commuter.filter_tasks_by_weather') as mock_filter:
                # Should suggest indoor tasks during rain
                weather_appropriate_tasks = [
                    {'id': 3, 'content': 'Indoor workout', 'tags': ['exercise', 'indoor']},
                    {'id': 4, 'content': 'Grocery shopping', 'tags': ['errands', 'indoor']}
                ]
                mock_filter.return_value = weather_appropriate_tasks
                
                suggestions = mock_filter(mock_storage, weather_data)
                
                assert len(suggestions) == 2
                assert all('indoor' in task['tags'] for task in suggestions)
    
    def test_commute_mode_weather_adaptation(self, mock_storage):
        # Add commute task
        task_id = add_task(
            mock_storage,
            "Get to work",
            tags=["commute", "work"]
        )
        
        # Test different weather conditions
        weather_scenarios = [
            {
                'condition': 'sunny',
                'temperature': 22,
                'recommended_mode': 'bike',
                'reason': 'Perfect weather for cycling'
            },
            {
                'condition': 'rain',
                'temperature': 10,
                'recommended_mode': 'public_transport',
                'reason': 'Avoid getting wet'
            },
            {
                'condition': 'snow',
                'temperature': -5,
                'recommended_mode': 'car',
                'reason': 'Safer than walking or cycling'
            }
        ]
        
        for scenario in weather_scenarios:
            with patch('logbuch.features.weather.get_current_weather', return_value=scenario):
                with patch('logbuch.features.commuter.recommend_transport_mode') as mock_recommend:
                    mock_recommend.return_value = {
                        'mode': scenario['recommended_mode'],
                        'reason': scenario['reason'],
                        'confidence': 0.8
                    }
                    
                    recommendation = mock_recommend(scenario)
                    
                    assert recommendation['mode'] == scenario['recommended_mode']
                    assert recommendation['confidence'] > 0.5


class TestCommuterJournalIntegration:
    def test_commute_time_logging(self, mock_storage):
        # Mock commute tracking
        commute_data = {
            'start_time': '08:15',
            'end_time': '08:45',
            'duration_minutes': 30,
            'mode': 'public_transport',
            'route': 'Blue Line to Central, then Bus 42',
            'delays': 5,
            'weather': 'cloudy'
        }
        
        with patch('logbuch.features.commuter.track_commute', return_value=commute_data):
            # Simulate automatic journal entry creation
            journal_text = f"""
            Commute Log - {datetime.now().strftime('%Y-%m-%d')}
            Duration: {commute_data['duration_minutes']} minutes
            Mode: {commute_data['mode']}
            Route: {commute_data['route']}
            Delays: {commute_data['delays']} minutes
            Weather: {commute_data['weather']}
            """
            
            entry_id = add_journal_entry(
                mock_storage,
                journal_text.strip(),
                tags=["commute", "auto-generated"]
            )
            
            assert entry_id is not None
            
            entries = list_journal_entries(mock_storage, tag="commute")
            assert len(entries) == 1
            assert "30 minutes" in entries[0]['text']
            assert "public_transport" in entries[0]['text']
    
    def test_commute_pattern_analysis(self, mock_storage):
        # Add multiple commute journal entries
        commute_entries = [
            "Commute: 25 minutes by train, no delays",
            "Commute: 35 minutes by train, 10 minute delay due to signal issues",
            "Commute: 20 minutes by bike, perfect weather",
            "Commute: 40 minutes by car, heavy traffic",
            "Commute: 30 minutes by train, light rain"
        ]
        
        for entry_text in commute_entries:
            add_journal_entry(mock_storage, entry_text, tags=["commute"])
        
        # Mock pattern analysis
        with patch('logbuch.features.commuter.analyze_commute_patterns') as mock_analyze:
            analysis_result = {
                'average_duration': 30,
                'most_common_mode': 'train',
                'reliability_score': 0.7,
                'weather_impact': 'moderate',
                'recommendations': [
                    'Consider leaving 5 minutes earlier on rainy days',
                    'Train is most reliable option',
                    'Bike is fastest in good weather'
                ]
            }
            mock_analyze.return_value = analysis_result
            
            analysis = mock_analyze(mock_storage)
            
            assert analysis['average_duration'] == 30
            assert analysis['most_common_mode'] == 'train'
            assert len(analysis['recommendations']) == 3


class TestLocationPrivacyAndSecurity:
    def test_location_data_anonymization(self, mock_storage):
        # Mock location with sensitive data
        sensitive_location = {
            'latitude': 37.7749123456789,  # High precision
            'longitude': -122.4194987654321,
            'address': '123 Main St, Apt 4B, San Francisco, CA',
            'device_id': 'unique_device_identifier'
        }
        
        with patch('logbuch.features.location.anonymize_location') as mock_anonymize:
            anonymized_location = {
                'latitude': 37.775,  # Reduced precision
                'longitude': -122.419,
                'address': 'San Francisco, CA',  # General area only
                'device_id': None  # Removed
            }
            mock_anonymize.return_value = anonymized_location
            
            safe_location = mock_anonymize(sensitive_location)
            
            # Verify sensitive data is removed/reduced
            assert len(str(safe_location['latitude'])) < len(str(sensitive_location['latitude']))
            assert 'Apt 4B' not in safe_location['address']
            assert safe_location['device_id'] is None
    
    def test_location_data_encryption(self, mock_storage):
        location_data = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timestamp': datetime.now().isoformat()
        }
        
        with patch('logbuch.features.security.encrypt_location_data') as mock_encrypt:
            encrypted_data = "encrypted_location_string_12345"
            mock_encrypt.return_value = encrypted_data
            
            # Store encrypted location
            task_id = add_task(
                mock_storage,
                "Location-aware task",
                tags=["location"],
                encrypted_location=encrypted_data
            )
            
            assert task_id is not None
            
            # Verify raw location data is not stored in plain text
            tasks = list_tasks(mock_storage)
            task = next((t for t in tasks if t['id'] == task_id), None)
            assert task is not None
            # Location should not be visible in plain text
            assert '37.7749' not in str(task)
    
    def test_location_permission_handling(self, mock_storage):
        permission_scenarios = [
            {'granted': True, 'precision': 'high'},
            {'granted': True, 'precision': 'low'},
            {'granted': False, 'precision': None}
        ]
        
        for scenario in permission_scenarios:
            with patch('logbuch.features.location.check_permissions', return_value=scenario):
                with patch('logbuch.features.location.get_location_if_permitted') as mock_get_location:
                    if scenario['granted']:
                        mock_location = {
                            'available': True,
                            'precision': scenario['precision']
                        }
                    else:
                        mock_location = {
                            'available': False,
                            'error': 'Permission denied'
                        }
                    
                    mock_get_location.return_value = mock_location
                    
                    location = mock_get_location()
                    
                    if scenario['granted']:
                        assert location['available'] is True
                        assert location['precision'] == scenario['precision']
                    else:
                        assert location['available'] is False
                        assert 'Permission denied' in location['error']


class TestCommuterAssistantIntegration:
    def test_morning_commute_workflow(self, mock_storage):
        # Add morning tasks
        meeting_task = add_task(mock_storage, "9 AM client meeting", tags=["work", "meeting"], due_time="09:00")
        coffee_task = add_task(mock_storage, "Get coffee", tags=["personal", "coffee"])
        
        # Mock morning workflow
        with patch('logbuch.features.commuter.morning_commute_assistant') as mock_assistant:
            morning_plan = {
                'wake_up_time': '07:00',
                'leave_time': '08:15',
                'travel_duration': 35,
                'weather_alert': 'Light rain expected - bring umbrella',
                'transit_status': 'Normal service',
                'suggested_route': 'Blue Line to Central Station',
                'nearby_tasks': [coffee_task],
                'arrival_time': '08:50',
                'buffer_time': 10
            }
            mock_assistant.return_value = morning_plan
            
            plan = mock_assistant(mock_storage, meeting_task)
            
            assert plan['leave_time'] == '08:15'
            assert plan['travel_duration'] == 35
            assert len(plan['nearby_tasks']) == 1
            assert plan['buffer_time'] == 10
    
    def test_evening_commute_workflow(self, mock_storage):
        # Add evening tasks
        grocery_task = add_task(mock_storage, "Buy groceries", tags=["errands", "grocery"])
        gym_task = add_task(mock_storage, "Go to gym", tags=["fitness", "gym"])
        
        # Mock evening workflow
        with patch('logbuch.features.commuter.evening_commute_assistant') as mock_assistant:
            evening_plan = {
                'departure_time': '17:30',
                'avoid_rush_hour': True,
                'optimized_stops': [grocery_task, gym_task],
                'estimated_home_time': '19:15',
                'traffic_conditions': 'Heavy traffic on main routes',
                'alternative_route': 'Take Highway 101 instead of I-280'
            }
            mock_assistant.return_value = evening_plan
            
            plan = mock_assistant(mock_storage)
            
            assert plan['avoid_rush_hour'] is True
            assert len(plan['optimized_stops']) == 2
            assert 'Heavy traffic' in plan['traffic_conditions']
    
    def test_weekend_errand_optimization(self, mock_storage):
        # Add weekend errands
        errands = [
            ("Post office", ["mail"], "post_office"),
            ("Bank", ["finance"], "bank"),
            ("Grocery store", ["food"], "grocery"),
            ("Hardware store", ["home"], "hardware"),
            ("Pharmacy", ["health"], "pharmacy")
        ]
        
        for content, tags, location in errands:
            add_task(mock_storage, content, tags=tags + ["errands"])
        
        # Mock weekend optimization
        with patch('logbuch.features.commuter.optimize_weekend_errands') as mock_optimize:
            optimized_plan = {
                'total_time': 120,  # 2 hours
                'total_distance': 25,  # 25 km
                'route_order': [
                    {'task': 'Post office', 'time': '10:00', 'duration': 15},
                    {'task': 'Bank', 'time': '10:30', 'duration': 10},
                    {'task': 'Grocery store', 'time': '11:00', 'duration': 30},
                    {'task': 'Hardware store', 'time': '11:45', 'duration': 20},
                    {'task': 'Pharmacy', 'time': '12:15', 'duration': 10}
                ],
                'savings': {
                    'time_saved': 45,  # minutes
                    'distance_saved': 15  # km
                }
            }
            mock_optimize.return_value = optimized_plan
            
            plan = mock_optimize(mock_storage)
            
            assert plan['total_time'] == 120
            assert len(plan['route_order']) == 5
            assert plan['savings']['time_saved'] == 45
