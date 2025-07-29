#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/commuter_commands.py

import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn

from logbuch.features.commuter_assistant import CommuterAssistant, TransportMode


class BaseCommand:
    def __init__(self, storage):
        self.storage = storage
        self.console = Console()
    
    def execute(self, **kwargs):
        return True


class CommuterCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.commuter = CommuterAssistant(storage)
    
    def execute(self, action: str = "check", **kwargs):
        try:
            if action == "check" or action == "late":
                return self._quick_check()
            elif action == "setup":
                return self._setup_route()
            elif action == "routes":
                return self._list_routes()
            elif action == "patterns":
                return self._show_patterns()
            elif action == "dashboard":
                return self._show_dashboard()
            else:
                return self._quick_check()  # Default to quick check
                
        except Exception as e:
            self.console.print(f"❌ Error in commuter assistant: {e}", style="red")
            return False
    
    def _quick_check(self):
        # Show loading animation
        with Progress(
            TextColumn("[bold blue]Checking your train delays..."),
            console=self.console
        ) as progress:
            task = progress.add_task("Checking", total=None)
            import time
            time.sleep(1)  # Simulate API call
        
        # Get the quick check result
        result = self.commuter.quick_check()
        
        # Parse the result for beautiful display
        if "ON TIME" in result:
            status_color = "bright_green"
            icon = "✅"
            title = "Great News!"
        elif "DELAYED" in result:
            status_color = "bright_yellow"
            icon = "⏰"
            title = "Heads Up!"
        elif "CANCELLED" in result:
            status_color = "bright_red"
            icon = "🚫"
            title = "Bad News!"
        else:
            status_color = "bright_cyan"
            icon = "ℹ️"
            title = "Status Update"
        
        # Create beautiful result display
        result_text = Text()
        result_text.append(f"{icon} {result}", style=f"bold {status_color}")
        
        self.console.print(Panel(
            Align.center(result_text),
            title=f"🚂 {title}",
            border_style=status_color
        ))
        
        # Show next steps if delayed
        if "DELAYED" in result or "CANCELLED" in result:
            tips_text = Text()
            tips_text.append("💡 Quick Tips:\n", style="bold bright_yellow")
            tips_text.append("• Check alternative routes\n", style="white")
            tips_text.append("• Notify your contacts about the delay\n", style="white")
            tips_text.append("• Use the extra time productively", style="white")
            
            self.console.print(Panel(tips_text, title="🎯 What to do next", border_style="bright_yellow"))
        
        return True
    
    def _setup_route(self):
        if not self.commuter.routes:
            # First-time setup
            setup_text = Text()
            setup_text.append("🚂 COMMUTER ASSISTANT SETUP\n", style="bold bright_cyan")
            setup_text.append("Let's set up your daily commute route!\n", style="white")
            setup_text.append("This will enable instant delay checking.", style="dim white")
            
            self.console.print(Panel(
                Align.center(setup_text),
                title="🛤️ First Time Setup",
                border_style="bright_cyan"
            ))
        
        # Show setup instructions
        instructions_text = Text()
        instructions_text.append("📝 TO SET UP YOUR ROUTE:\n", style="bold bright_yellow")
        instructions_text.append("logbuch commute add-route", style="cyan")
        instructions_text.append(" \\\n", style="dim white")
        instructions_text.append("  --name \"Work Commute\"", style="cyan")
        instructions_text.append(" \\\n", style="dim white")
        instructions_text.append("  --from \"Central Station\"", style="cyan")
        instructions_text.append(" \\\n", style="dim white")
        instructions_text.append("  --to \"Business District\"", style="cyan")
        instructions_text.append(" \\\n", style="dim white")
        instructions_text.append("  --mode train", style="cyan")
        instructions_text.append(" \\\n", style="dim white")
        instructions_text.append("  --departure \"08:15\"", style="cyan")
        instructions_text.append(" \\\n", style="dim white")
        instructions_text.append("  --duration 45", style="cyan")
        instructions_text.append(" \\\n", style="dim white")
        instructions_text.append("  --line \"S1\"", style="cyan")
        instructions_text.append(" \\\n", style="dim white")
        instructions_text.append("  --default", style="cyan")
        
        self.console.print(Panel(instructions_text, title="⚙️ Setup Instructions", border_style="bright_yellow"))
        
        # Show example
        example_text = Text()
        example_text.append("💡 EXAMPLE:\n", style="bold bright_green")
        example_text.append("logbuch commute add-route --name \"Daily Train\" --from \"Munich Hbf\" --to \"Frankfurt\" --mode train --departure \"07:30\" --duration 60 --line \"ICE 123\" --default", style="green")
        
        self.console.print(Panel(example_text, title="📋 Example Command", border_style="bright_green"))
        
        return True
    
    def _list_routes(self):
        if not self.commuter.routes:
            self.console.print("🚂 No commute routes configured yet!", style="yellow")
            self.console.print("Use 'logbuch commute setup' to get started.", style="dim white")
            return True
        
        # Header
        header_text = Text()
        header_text.append("🚂 YOUR COMMUTE ROUTES\n", style="bold bright_cyan")
        header_text.append("Saved routes for instant delay checking", style="dim bright_white")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="🛤️ Route Manager",
            border_style="bright_cyan"
        ))
        
        # Routes table
        routes_table = Table(title="🚂 Configured Routes", show_header=True, header_style="bold bright_yellow")
        routes_table.add_column("Name", style="cyan", width=20)
        routes_table.add_column("Route", style="white", width=30)
        routes_table.add_column("Mode", style="green", width=10)
        routes_table.add_column("Departure", style="yellow", width=10)
        routes_table.add_column("Duration", style="magenta", width=10)
        routes_table.add_column("Line", style="blue", width=10)
        routes_table.add_column("Default", style="red", width=8)
        
        transport_emojis = {
            'train': '🚂',
            'bus': '🚌',
            'subway': '🚇',
            'tram': '🚋',
            'ferry': '⛴️'
        }
        
        for route in self.commuter.routes:
            emoji = transport_emojis.get(route.transport_mode.value, '🚂')
            mode_display = f"{emoji} {route.transport_mode.value.title()}"
            
            routes_table.add_row(
                route.name,
                f"{route.from_station} → {route.to_station}",
                mode_display,
                route.usual_departure_time,
                f"{route.usual_duration}min",
                route.line_number or "N/A",
                "✅" if route.is_default else ""
            )
        
        self.console.print(routes_table)
        
        # Quick actions
        actions_text = Text()
        actions_text.append("🚀 Quick Actions:\n", style="bold bright_yellow")
        actions_text.append("logbuch commute check", style="cyan")
        actions_text.append("    # Check delays now\n", style="dim white")
        actions_text.append("logbuch commute patterns", style="cyan")
        actions_text.append("  # View delay patterns", style="dim white")
        
        self.console.print(Panel(actions_text, title="⚡ What's Next", border_style="bright_yellow"))
        
        return True
    
    def _show_patterns(self):
        patterns = self.commuter.get_delay_patterns()
        
        if 'error' in patterns:
            self.console.print(f"📊 {patterns['error']}", style="yellow")
            self.console.print("Start using delay checking to build pattern data!", style="dim white")
            return True
        
        # Header
        self.console.print("📊 Commute Delay Patterns", style="bold bright_cyan")
        
        # Main statistics
        stats_left = Text()
        stats_left.append("📈 RELIABILITY STATS\n", style="bold bright_yellow")
        stats_left.append(f"🚂 Total Journeys: {patterns['total_journeys']}\n", style="white")
        stats_left.append(f"✅ On-Time Rate: {patterns['on_time_rate']*100:.1f}%\n", style="green")
        stats_left.append(f"⏰ Delay Rate: {patterns['delay_rate']*100:.1f}%\n", style="red")
        stats_left.append(f"📊 Average Delay: {patterns['average_delay']:.1f} min", style="cyan")
        
        stats_right = Text()
        stats_right.append("📅 DAY PATTERNS\n", style="bold bright_green")
        if patterns['worst_day']:
            stats_right.append(f"😤 Worst Day: {patterns['worst_day'][0]} ({patterns['worst_day'][1]:.1f}min avg)\n", style="red")
        if patterns['best_day']:
            stats_right.append(f"😊 Best Day: {patterns['best_day'][0]} ({patterns['best_day'][1]:.1f}min avg)\n", style="green")
        if patterns['most_common_reason']:
            stats_right.append(f"🔧 Main Issue: {patterns['most_common_reason'][0]} ({patterns['most_common_reason'][1]}x)", style="yellow")
        
        self.console.print(Panel(
            Columns([stats_left, stats_right], equal=True),
            title="📊 Delay Analytics",
            border_style="bright_yellow"
        ))
        
        # Weekly pattern
        if patterns['day_averages']:
            weekly_table = Table(title="📅 Weekly Delay Pattern", show_header=True, header_style="bold bright_cyan")
            weekly_table.add_column("Day", style="cyan", width=12)
            weekly_table.add_column("Avg Delay", style="yellow", width=12)
            weekly_table.add_column("Reliability", style="green", width=15)
            
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day in days_order:
                if day in patterns['day_averages']:
                    avg_delay = patterns['day_averages'][day]
                    
                    # Reliability rating
                    if avg_delay <= 2:
                        reliability = "🟢 Excellent"
                    elif avg_delay <= 5:
                        reliability = "🟡 Good"
                    elif avg_delay <= 10:
                        reliability = "🟠 Fair"
                    else:
                        reliability = "🔴 Poor"
                    
                    weekly_table.add_row(
                        day,
                        f"{avg_delay:.1f} min",
                        reliability
                    )
            
            self.console.print(weekly_table)
        
        return True
    
    def _show_dashboard(self):
        dashboard = self.commuter.get_commute_dashboard()
        
        # Header
        header_text = Text()
        header_text.append("🚂 COMMUTER DASHBOARD\n", style="bold bright_cyan")
        header_text.append("Your complete commute intelligence system", style="dim bright_white")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="🛤️ Commute Command Center",
            border_style="bright_cyan"
        ))
        
        # Current status
        current = dashboard['current_status']
        if 'error' not in current:
            status_text = Text()
            status_text.append("🚨 CURRENT STATUS\n", style="bold bright_red")
            
            if current['status'] == 'on_time':
                status_text.append("✅ Your train is ON TIME!", style="bold green")
            elif current['status'] == 'cancelled':
                status_text.append("🚫 Your train is CANCELLED!", style="bold red")
            else:
                status_text.append(f"⏰ Your train is {current['delay_minutes']} minutes LATE", style="bold yellow")
                if current['reason']:
                    status_text.append(f"\nReason: {current['reason']}", style="dim white")
            
            self.console.print(Panel(status_text, title="🚂 Right Now", border_style="bright_red"))
        
        # Quick check result
        quick_result = dashboard['quick_check_result']
        result_text = Text()
        result_text.append(quick_result, style="bold white")
        
        self.console.print(Panel(result_text, title="⚡ Quick Check", border_style="bright_yellow"))
        
        # Routes summary
        routes = dashboard['routes']
        if routes:
            routes_text = Text()
            routes_text.append("🛤️ CONFIGURED ROUTES\n", style="bold bright_green")
            for route in routes:
                default_marker = " (Default)" if route['is_default'] else ""
                routes_text.append(f"• {route['name']}{default_marker}\n", style="white")
                routes_text.append(f"  {route['from']} → {route['to']} at {route['departure']}\n", style="dim white")
            
            self.console.print(Panel(routes_text, title="🚂 Your Routes", border_style="bright_green"))
        
        # Patterns summary
        patterns = dashboard['delay_patterns']
        if 'error' not in patterns:
            patterns_text = Text()
            patterns_text.append("📊 RELIABILITY OVERVIEW\n", style="bold bright_blue")
            patterns_text.append(f"On-time rate: {patterns['on_time_rate']*100:.1f}%\n", style="green")
            patterns_text.append(f"Average delay: {patterns['average_delay']:.1f} minutes\n", style="yellow")
            if patterns['worst_day']:
                patterns_text.append(f"Worst day: {patterns['worst_day'][0]}", style="red")
            
            self.console.print(Panel(patterns_text, title="📈 Your Patterns", border_style="bright_blue"))
        
        return True


class CommuteSetupCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.commuter = CommuterAssistant(storage)
    
    def execute(self, name: str, from_station: str, to_station: str,
               mode: str, departure: str, duration: int,
               line: str = None, operator: str = None, 
               set_default: bool = False, **kwargs):
        # Input validation
        if not name or len(name.strip()) == 0:
            self.console.print("❌ Route name is required", style="red")
            return False
            
        if not from_station or len(from_station.strip()) == 0:
            self.console.print("❌ From station is required", style="red")
            return False
            
        if not to_station or len(to_station.strip()) == 0:
            self.console.print("❌ To station is required", style="red")
            return False
            
        if mode not in ['train', 'bus', 'subway', 'tram', 'ferry']:
            self.console.print("❌ Invalid transport mode", style="red")
            return False
            
        # Validate departure time format
        try:
            time_parts = departure.split(':')
            if len(time_parts) != 2:
                raise ValueError("Invalid format")
            hour, minute = int(time_parts[0]), int(time_parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time")
        except ValueError:
            self.console.print("❌ Departure time must be in HH:MM format (e.g., '08:30')", style="red")
            return False
            
        if duration <= 0 or duration > 1440:  # Max 24 hours
            self.console.print("❌ Duration must be between 1 and 1440 minutes", style="red")
            return False
        
        try:
            route_id = self.commuter.add_route(
                name=name,
                from_station=from_station,
                to_station=to_station,
                transport_mode=mode,
                departure_time=departure,
                duration=duration,
                line_number=line,
                operator=operator,
                set_as_default=set_default
            )
            
            # Success message
            success_text = Text()
            success_text.append("🎉 Route Added Successfully!\n", style="bold bright_green")
            success_text.append(f"Name: {name}\n", style="cyan")
            success_text.append(f"Route: {from_station} → {to_station}\n", style="white")
            success_text.append(f"Departure: {departure} ({duration} min journey)\n", style="yellow")
            if line:
                success_text.append(f"Line: {line}\n", style="blue")
            if set_default:
                success_text.append("✅ Set as default route", style="green")
            
            self.console.print(Panel(success_text, title="🚂 Route Configuration", border_style="bright_green"))
            
            # Next steps
            next_steps = Text()
            next_steps.append("🚀 What's Next:\n", style="bold bright_yellow")
            next_steps.append("logbuch late", style="cyan")
            next_steps.append("           # Quick delay check\n", style="dim white")
            next_steps.append("logbuch commute check", style="cyan")
            next_steps.append("  # Detailed status\n", style="dim white")
            next_steps.append("logbuch commute dashboard", style="cyan")
            next_steps.append(" # Full overview", style="dim white")
            
            self.console.print(Panel(next_steps, title="⚡ Try It Now", border_style="bright_yellow"))
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error adding route: {e}", style="red")
            return False


# Export commands
__all__ = ['CommuterCommand', 'CommuteSetupCommand']
