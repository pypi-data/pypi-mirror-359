#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/toilet_command.py

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from logbuch.features.ascii_art import ASCIIArtGenerator


class BaseCommand:
    def __init__(self, storage):
        self.storage = storage
        self.console = Console()
    
    def execute(self, **kwargs):
        return True


class ToiletCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.ascii_generator = ASCIIArtGenerator()
    
    def execute(self, text: str = None, font: str = "standard", 
               width: int = None, justify: str = "left",
               border: bool = False, color: str = None,
               list_fonts: bool = False, celebrate: str = None, 
               metal: bool = False, speed: bool = False, **kwargs):
        try:
            if list_fonts:
                return self._list_fonts()
            elif celebrate:
                return self._celebrate_achievement(celebrate)
            elif text:
                # Check for special effects that require real toilet command
                if metal or speed:
                    return self._use_real_toilet(text, metal, speed)
                else:
                    return self._generate_ascii_art(text, font, width, justify, border, color)
            else:
                return self._show_help()
                
        except Exception as e:
            self.console.print(f"❌ Error in toilet command: {e}", style="red")
            return False
    
    def _use_real_toilet(self, text: str, metal: bool = False, speed: bool = False):
        import subprocess
        import shutil
        
        # Check if toilet command is available
        if not shutil.which('toilet'):
            self.console.print("❌ 'toilet' command not found. Install with: brew install toilet", style="red")
            self.console.print("Falling back to built-in ASCII art...", style="yellow")
            return self._generate_ascii_art(text)
        
        # Build toilet command
        cmd = ['toilet']
        
        if speed:
            # Try to use speed font with figlet-fonts
            cmd.extend(['--directory', 'figlet-fonts', '-f', 'speed.flf'])
        
        if metal:
            cmd.append('--metal')
        
        cmd.extend(['-W', text])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.console.print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ Error running toilet command: {e}", style="red")
            self.console.print("Falling back to built-in ASCII art...", style="yellow")
            return self._generate_ascii_art(text)
        except FileNotFoundError:
            self.console.print("❌ 'toilet' command not found. Install with: brew install toilet", style="red")
            self.console.print("Falling back to built-in ASCII art...", style="yellow")
            return self._generate_ascii_art(text)
    
    def _generate_ascii_art(self, text: str, font: str, width: int, 
                           justify: str, border: bool, color: str):
        # Generate the ASCII art
        ascii_art = self.ascii_generator.generate_ascii_art(
            text=text,
            font=font,
            width=width,
            justify=justify,
            border=border,
            color=color
        )
        
        # Display the result
        if color:
            # Rich markup is already applied
            self.console.print(ascii_art)
        else:
            # Plain ASCII art
            self.console.print(ascii_art, style="bright_cyan")
        
        return True
    
    def _list_fonts(self):
        # Header
        header_text = Text()
        header_text.append("🎨 AVAILABLE ASCII FONTS\n", style="bold bright_cyan")
        header_text.append("Choose your style for epic ASCII art", style="dim bright_white")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="🚽 Toilet Fonts",
            border_style="bright_cyan"
        ))
        
        # Get available fonts
        fonts = self.ascii_generator.list_fonts()
        
        # Create font examples
        font_examples = []
        
        for font in fonts:
            try:
                # Generate small example
                example = self.ascii_generator.generate_ascii_art("ABC", font=font)
                
                # Create font info
                font_info = Text()
                font_info.append(f"{font.upper()}\n", style="bold bright_yellow")
                font_info.append(example, style="bright_white")
                
                font_examples.append(Panel(
                    font_info,
                    title=f"Font: {font}",
                    border_style="bright_blue",
                    width=20
                ))
            except Exception:
                # Skip fonts that have issues
                continue
        
        # Display fonts in columns
        if font_examples:
            # Show 3 fonts per row
            for i in range(0, len(font_examples), 3):
                row_fonts = font_examples[i:i+3]
                self.console.print(Columns(row_fonts, equal=True))
                self.console.print()  # Add spacing
        
        # Usage examples
        usage_text = Text()
        usage_text.append("💡 Usage Examples:\n", style="bold bright_yellow")
        usage_text.append("logbuch toilet \"HELLO\" --font big\n", style="cyan")
        usage_text.append("logbuch toilet \"SUCCESS\" --font block --border\n", style="cyan")
        usage_text.append("logbuch toilet \"DONE\" --font standard --color green\n", style="cyan")
        usage_text.append("logbuch toilet \"EPIC\" --font graffiti --justify center", style="cyan")
        
        self.console.print(Panel(usage_text, title="🎯 How to Use", border_style="bright_yellow"))
        
        return True
    
    def _celebrate_achievement(self, achievement: str):
        celebration_art = self.ascii_generator.get_productivity_celebration(achievement)
        
        # Display with fanfare
        self.console.print()
        self.console.print(celebration_art)
        self.console.print()
        
        # Add motivational message
        motivational_messages = [
            "🎉 Outstanding work! Keep crushing those goals!",
            "⭐ You're on fire! This is what success looks like!",
            "🚀 Incredible achievement! You're unstoppable!",
            "💪 Phenomenal progress! You're a productivity machine!",
            "🏆 Epic accomplishment! You deserve this celebration!"
        ]
        
        import random
        message = random.choice(motivational_messages)
        
        self.console.print(Panel(
            Align.center(Text(message, style="bold bright_green")),
            title="🎊 Celebration",
            border_style="bright_green"
        ))
        
        return True
    
    def _show_help(self):
        help_text = Text()
        help_text.append("🚽 TOILET - ASCII ART GENERATOR\n", style="bold bright_cyan")
        help_text.append("Create epic ASCII art for your productivity celebrations!\n\n", style="dim white")
        
        help_text.append("📝 Basic Usage:\n", style="bold bright_yellow")
        help_text.append("logbuch toilet \"YOUR TEXT\"", style="cyan")
        help_text.append("                    # Basic ASCII art\n", style="dim white")
        
        help_text.append("\n🎨 Font Options:\n", style="bold bright_green")
        help_text.append("logbuch toilet \"TEXT\" --font big", style="cyan")
        help_text.append("        # Use big font\n", style="dim white")
        help_text.append("logbuch toilet \"TEXT\" --font block", style="cyan")
        help_text.append("      # Use block font\n", style="dim white")
        help_text.append("logbuch toilet \"TEXT\" --font small", style="cyan")
        help_text.append("      # Use small font\n", style="dim white")
        
        help_text.append("\n🎯 Styling Options:\n", style="bold bright_blue")
        help_text.append("logbuch toilet \"TEXT\" --border", style="cyan")
        help_text.append("           # Add border\n", style="dim white")
        help_text.append("logbuch toilet \"TEXT\" --color green", style="cyan")
        help_text.append("      # Add color\n", style="dim white")
        help_text.append("logbuch toilet \"TEXT\" --justify center", style="cyan")
        help_text.append("   # Center align\n", style="dim white")
        
        help_text.append("\n🎉 Special Features:\n", style="bold bright_magenta")
        help_text.append("logbuch toilet --list-fonts", style="cyan")
        help_text.append("              # Show all fonts\n", style="dim white")
        help_text.append("logbuch toilet --celebrate \"TASK DONE\"", style="cyan")
        help_text.append("   # Celebration mode\n", style="dim white")
        
        help_text.append("\n💡 Pro Tips:\n", style="bold bright_yellow")
        help_text.append("• Use quotes around text with spaces\n", style="white")
        help_text.append("• Combine --border and --color for epic results\n", style="white")
        help_text.append("• Use --celebrate for productivity achievements\n", style="white")
        help_text.append("• Try different fonts to find your favorite style", style="white")
        
        self.console.print(Panel(help_text, title="🚽 Toilet Help", border_style="bright_cyan"))
        
        return True


# Export command
__all__ = ['ToiletCommand']
