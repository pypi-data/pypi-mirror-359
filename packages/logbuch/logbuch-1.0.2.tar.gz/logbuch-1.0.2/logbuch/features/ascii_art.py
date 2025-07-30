#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/ascii_art.py

import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from logbuch.core.logger import get_logger


class ASCIIFont(Enum):
    STANDARD = "standard"
    BIG = "big"
    BLOCK = "block"
    BUBBLE = "bubble"
    DIGITAL = "digital"
    GRAFFITI = "graffiti"
    SHADOW = "shadow"
    SLANT = "slant"
    SMALL = "small"
    MINI = "mini"
    SPEED = "speed"  # NEW: Racing-style speed font
    METAL = "metal"  # NEW: Metal effect


class ASCIIArtGenerator:
    def __init__(self):
        self.logger = get_logger("ascii_art")
        
        # Define ASCII art fonts
        self.fonts = {
            ASCIIFont.STANDARD: self._get_standard_font(),
            ASCIIFont.BIG: self._get_big_font(),
            ASCIIFont.BLOCK: self._get_block_font(),
            ASCIIFont.BUBBLE: self._get_bubble_font(),
            ASCIIFont.DIGITAL: self._get_digital_font(),
            ASCIIFont.GRAFFITI: self._get_graffiti_font(),
            ASCIIFont.SHADOW: self._get_shadow_font(),
            ASCIIFont.SLANT: self._get_slant_font(),
            ASCIIFont.SMALL: self._get_small_font(),
            ASCIIFont.MINI: self._get_mini_font(),
            ASCIIFont.SPEED: self._get_speed_font(),
            ASCIIFont.METAL: self._get_metal_font(),
        }
        
        self.logger.debug("ASCII Art Generator initialized")
    
    def generate_ascii_art(self, text: str, font: str = "standard", 
                          width: Optional[int] = None, 
                          justify: str = "left",
                          border: bool = False,
                          color: Optional[str] = None) -> str:
        if not text or len(text.strip()) == 0:
            return "❌ Text cannot be empty"
        
        # Convert font string to enum
        try:
            font_enum = ASCIIFont(font.lower())
        except ValueError:
            font_enum = ASCIIFont.STANDARD
        
        # Get font data
        font_data = self.fonts.get(font_enum, self.fonts[ASCIIFont.STANDARD])
        
        # Generate the ASCII art
        ascii_lines = self._render_text(text.upper(), font_data)
        
        # Apply justification
        if justify == "center":
            ascii_lines = self._center_text(ascii_lines, width)
        elif justify == "right":
            ascii_lines = self._right_align_text(ascii_lines, width)
        
        # Add border if requested
        if border:
            ascii_lines = self._add_border(ascii_lines)
        
        # Join lines
        result = "\n".join(ascii_lines)
        
        # Add color if specified (using rich markup)
        if color:
            result = f"[{color}]{result}[/{color}]"
        
        return result
    
    def _render_text(self, text: str, font_data: Dict) -> List[str]:
        if not text:
            return [""]
        
        # Get character height
        char_height = font_data.get('height', 5)
        
        # Initialize result lines
        result_lines = [""] * char_height
        
        # Process each character
        for char in text:
            if char == ' ':
                # Add space
                for i in range(char_height):
                    result_lines[i] += "  "
            elif char in font_data['chars']:
                # Add character
                char_lines = font_data['chars'][char]
                for i in range(char_height):
                    if i < len(char_lines):
                        result_lines[i] += char_lines[i]
                    else:
                        result_lines[i] += " " * len(char_lines[0]) if char_lines else " "
            else:
                # Unknown character, use placeholder
                for i in range(char_height):
                    result_lines[i] += "? "
        
        return result_lines
    
    def _center_text(self, lines: List[str], width: Optional[int] = None) -> List[str]:
        if not width:
            width = 80  # Default terminal width
        
        centered_lines = []
        for line in lines:
            line_width = len(line)
            if line_width < width:
                padding = (width - line_width) // 2
                centered_lines.append(" " * padding + line)
            else:
                centered_lines.append(line)
        
        return centered_lines
    
    def _right_align_text(self, lines: List[str], width: Optional[int] = None) -> List[str]:
        if not width:
            width = 80
        
        aligned_lines = []
        for line in lines:
            line_width = len(line)
            if line_width < width:
                padding = width - line_width
                aligned_lines.append(" " * padding + line)
            else:
                aligned_lines.append(line)
        
        return aligned_lines
    
    def _add_border(self, lines: List[str]) -> List[str]:
        if not lines:
            return lines
        
        # Find max width
        max_width = max(len(line) for line in lines) if lines else 0
        
        # Create border
        border_line = "+" + "-" * (max_width + 2) + "+"
        
        # Add border
        bordered_lines = [border_line]
        for line in lines:
            padded_line = line.ljust(max_width)
            bordered_lines.append(f"| {padded_line} |")
        bordered_lines.append(border_line)
        
        return bordered_lines
    
    def _get_standard_font(self) -> Dict:
        return {
            'height': 5,
            'chars': {
                'A': [
                    "  ██  ",
                    " ████ ",
                    "██  ██",
                    "██████",
                    "██  ██"
                ],
                'B': [
                    "██████",
                    "██  ██",
                    "██████",
                    "██  ██",
                    "██████"
                ],
                'C': [
                    " █████",
                    "██    ",
                    "██    ",
                    "██    ",
                    " █████"
                ],
                'D': [
                    "██████",
                    "██  ██",
                    "██  ██",
                    "██  ██",
                    "██████"
                ],
                'E': [
                    "██████",
                    "██    ",
                    "██████",
                    "██    ",
                    "██████"
                ],
                'F': [
                    "██████",
                    "██    ",
                    "██████",
                    "██    ",
                    "██    "
                ],
                'G': [
                    " █████",
                    "██    ",
                    "██ ███",
                    "██  ██",
                    " █████"
                ],
                'H': [
                    "██  ██",
                    "██  ██",
                    "██████",
                    "██  ██",
                    "██  ██"
                ],
                'I': [
                    "██████",
                    "  ██  ",
                    "  ██  ",
                    "  ██  ",
                    "██████"
                ],
                'J': [
                    "██████",
                    "    ██",
                    "    ██",
                    "██  ██",
                    " █████"
                ],
                'K': [
                    "██  ██",
                    "██ ██ ",
                    "████  ",
                    "██ ██ ",
                    "██  ██"
                ],
                'L': [
                    "██    ",
                    "██    ",
                    "██    ",
                    "██    ",
                    "██████"
                ],
                'M': [
                    "██  ██",
                    "██████",
                    "██████",
                    "██  ██",
                    "██  ██"
                ],
                'N': [
                    "██  ██",
                    "███ ██",
                    "██████",
                    "██ ███",
                    "██  ██"
                ],
                'O': [
                    " █████",
                    "██  ██",
                    "██  ██",
                    "██  ██",
                    " █████"
                ],
                'P': [
                    "██████",
                    "██  ██",
                    "██████",
                    "██    ",
                    "██    "
                ],
                'Q': [
                    " █████",
                    "██  ██",
                    "██  ██",
                    "██ ███",
                    " ██████"
                ],
                'R': [
                    "██████",
                    "██  ██",
                    "██████",
                    "██ ██ ",
                    "██  ██"
                ],
                'S': [
                    " █████",
                    "██    ",
                    " █████",
                    "    ██",
                    " █████"
                ],
                'T': [
                    "██████",
                    "  ██  ",
                    "  ██  ",
                    "  ██  ",
                    "  ██  "
                ],
                'U': [
                    "██  ██",
                    "██  ██",
                    "██  ██",
                    "██  ██",
                    " █████"
                ],
                'V': [
                    "██  ██",
                    "██  ██",
                    "██  ██",
                    " ████ ",
                    "  ██  "
                ],
                'W': [
                    "██  ██",
                    "██  ██",
                    "██████",
                    "██████",
                    "██  ██"
                ],
                'X': [
                    "██  ██",
                    " ████ ",
                    "  ██  ",
                    " ████ ",
                    "██  ██"
                ],
                'Y': [
                    "██  ██",
                    " ████ ",
                    "  ██  ",
                    "  ██  ",
                    "  ██  "
                ],
                'Z': [
                    "██████",
                    "   ██ ",
                    "  ██  ",
                    " ██   ",
                    "██████"
                ],
                '0': [
                    " █████",
                    "██  ██",
                    "██  ██",
                    "██  ██",
                    " █████"
                ],
                '1': [
                    "  ██  ",
                    " ███  ",
                    "  ██  ",
                    "  ██  ",
                    "██████"
                ],
                '2': [
                    " █████",
                    "    ██",
                    " █████",
                    "██    ",
                    "██████"
                ],
                '3': [
                    " █████",
                    "    ██",
                    " █████",
                    "    ██",
                    " █████"
                ],
                '4': [
                    "██  ██",
                    "██  ██",
                    "██████",
                    "    ██",
                    "    ██"
                ],
                '5': [
                    "██████",
                    "██    ",
                    "██████",
                    "    ██",
                    "██████"
                ],
                '6': [
                    " █████",
                    "██    ",
                    "██████",
                    "██  ██",
                    " █████"
                ],
                '7': [
                    "██████",
                    "    ██",
                    "   ██ ",
                    "  ██  ",
                    " ██   "
                ],
                '8': [
                    " █████",
                    "██  ██",
                    " █████",
                    "██  ██",
                    " █████"
                ],
                '9': [
                    " █████",
                    "██  ██",
                    " ██████",
                    "    ██",
                    " █████"
                ],
                '!': [
                    "  ██  ",
                    "  ██  ",
                    "  ██  ",
                    "      ",
                    "  ██  "
                ],
                '?': [
                    " █████",
                    "    ██",
                    "  ███ ",
                    "      ",
                    "  ██  "
                ],
                '.': [
                    "      ",
                    "      ",
                    "      ",
                    "      ",
                    "  ██  "
                ],
                ',': [
                    "      ",
                    "      ",
                    "      ",
                    "  ██  ",
                    " ██   "
                ],
                ':': [
                    "      ",
                    "  ██  ",
                    "      ",
                    "  ██  ",
                    "      "
                ],
                ';': [
                    "      ",
                    "  ██  ",
                    "      ",
                    "  ██  ",
                    " ██   "
                ],
                '-': [
                    "      ",
                    "      ",
                    "██████",
                    "      ",
                    "      "
                ],
                '_': [
                    "      ",
                    "      ",
                    "      ",
                    "      ",
                    "██████"
                ],
                '=': [
                    "      ",
                    "██████",
                    "      ",
                    "██████",
                    "      "
                ],
                '+': [
                    "      ",
                    "  ██  ",
                    "██████",
                    "  ██  ",
                    "      "
                ],
                '*': [
                    "      ",
                    "██ ██ ",
                    " ███  ",
                    "██ ██ ",
                    "      "
                ],
                '/': [
                    "    ██",
                    "   ██ ",
                    "  ██  ",
                    " ██   ",
                    "██    "
                ],
                '\\': [
                    "██    ",
                    " ██   ",
                    "  ██  ",
                    "   ██ ",
                    "    ██"
                ],
                '|': [
                    "  ██  ",
                    "  ██  ",
                    "  ██  ",
                    "  ██  ",
                    "  ██  "
                ],
                '(': [
                    "   ██ ",
                    "  ██  ",
                    "  ██  ",
                    "  ██  ",
                    "   ██ "
                ],
                ')': [
                    " ██   ",
                    "  ██  ",
                    "  ██  ",
                    "  ██  ",
                    " ██   "
                ],
                '[': [
                    " ████ ",
                    " ██   ",
                    " ██   ",
                    " ██   ",
                    " ████ "
                ],
                ']': [
                    " ████ ",
                    "   ██ ",
                    "   ██ ",
                    "   ██ ",
                    " ████ "
                ],
                '{': [
                    "   ███",
                    "  ██  ",
                    " ██   ",
                    "  ██  ",
                    "   ███"
                ],
                '}': [
                    "███   ",
                    "  ██  ",
                    "   ██ ",
                    "  ██  ",
                    "███   "
                ],
                '<': [
                    "   ██ ",
                    "  ██  ",
                    " ██   ",
                    "  ██  ",
                    "   ██ "
                ],
                '>': [
                    " ██   ",
                    "  ██  ",
                    "   ██ ",
                    "  ██  ",
                    " ██   "
                ],
                '@': [
                    " █████",
                    "██ ███",
                    "██████",
                    "██    ",
                    " █████"
                ],
                '#': [
                    " ██ ██",
                    "██████",
                    " ██ ██",
                    "██████",
                    " ██ ██"
                ],
                '$': [
                    "  ██  ",
                    " █████",
                    "██    ",
                    " █████",
                    "  ██  "
                ],
                '%': [
                    "██  ██",
                    "   ██ ",
                    "  ██  ",
                    " ██   ",
                    "██  ██"
                ],
                '^': [
                    "  ██  ",
                    " ████ ",
                    "██  ██",
                    "      ",
                    "      "
                ],
                '&': [
                    " ████ ",
                    "██  ██",
                    " ████ ",
                    "██ ███",
                    " ██ ██"
                ]
            }
        }
    
    def _get_big_font(self) -> Dict:
        return {
            'height': 7,
            'chars': {
                'A': [
                    "   ████   ",
                    "  ██  ██  ",
                    " ██    ██ ",
                    "██████████",
                    "██      ██",
                    "██      ██",
                    "██      ██"
                ],
                'B': [
                    "████████  ",
                    "██      ██",
                    "██      ██",
                    "████████  ",
                    "██      ██",
                    "██      ██",
                    "████████  "
                ],
                # Add more characters as needed...
            }
        }
    
    def _get_block_font(self) -> Dict:
        return {
            'height': 3,
            'chars': {
                'A': ["███", "█ █", "███"],
                'B': ["██ ", "██ ", "███"],
                'C': ["███", "█  ", "███"],
                'D': ["██ ", "█ █", "██ "],
                'E': ["███", "██ ", "███"],
                'F': ["███", "██ ", "█  "],
                'G': ["███", "█ █", "███"],
                'H': ["█ █", "███", "█ █"],
                'I': ["███", " █ ", "███"],
                'J': ["███", "  █", "██ "],
                'K': ["█ █", "██ ", "█ █"],
                'L': ["█  ", "█  ", "███"],
                'M': ["█ █", "███", "█ █"],
                'N': ["█ █", "███", "█ █"],
                'O': ["███", "█ █", "███"],
                'P': ["███", "███", "█  "],
                'Q': ["███", "█ █", "███"],
                'R': ["███", "██ ", "█ █"],
                'S': ["███", " ██", "███"],
                'T': ["███", " █ ", " █ "],
                'U': ["█ █", "█ █", "███"],
                'V': ["█ █", "█ █", " █ "],
                'W': ["█ █", "███", "█ █"],
                'X': ["█ █", " █ ", "█ █"],
                'Y': ["█ █", " █ ", " █ "],
                'Z': ["███", " █ ", "███"],
                '0': ["███", "█ █", "███"],
                '1': [" █ ", " █ ", " █ "],
                '2': ["███", " ██", "███"],
                '3': ["███", " ██", "███"],
                '4': ["█ █", "███", "  █"],
                '5': ["███", "██ ", "███"],
                '6': ["███", "██ ", "███"],
                '7': ["███", "  █", "  █"],
                '8': ["███", "███", "███"],
                '9': ["███", " ██", "███"],
                '!': [" █ ", " █ ", " █ "],
                '?': ["███", " ██", " █ "],
                '.': ["   ", "   ", " █ "],
                ' ': ["   ", "   ", "   "]
            }
        }
    
    def _get_bubble_font(self) -> Dict:
        return {
            'height': 5,
            'chars': {
                'A': [
                    " ╭─╮ ",
                    "╭┴─┴╮",
                    "│╭─╮│",
                    "││ ││",
                    "╰╯ ╰╯"
                ],
                'B': [
                    "╭───╮",
                    "│╭─╮│",
                    "│╰─╯│",
                    "│╭─╮│",
                    "╰╯ ╰╯"
                ],
                # Simplified bubble font
            }
        }
    
    def _get_digital_font(self) -> Dict:
        return {
            'height': 5,
            'chars': {
                'A': [
                    " ▄▄▄ ",
                    "▐   ▌",
                    "▐▄▄▄▌",
                    "▐   ▌",
                    "▐   ▌"
                ],
                # Add more digital characters...
            }
        }
    
    def _get_graffiti_font(self) -> Dict:
        return {
            'height': 6,
            'chars': {
                'A': [
                    "    ▄▄    ",
                    "   ████   ",
                    "  ██  ██  ",
                    " ████████ ",
                    "██      ██",
                    "██      ██"
                ],
                # Add more graffiti characters...
            }
        }
    
    def _get_shadow_font(self) -> Dict:
        return {
            'height': 5,
            'chars': {
                'A': [
                    " ██▄ ",
                    "██▀██",
                    "█████",
                    "██ ██",
                    "▀▀ ▀▀"
                ],
                # Add more shadow characters...
            }
        }
    
    def _get_slant_font(self) -> Dict:
        return {
            'height': 5,
            'chars': {
                'A': [
                    "   ██  ",
                    "  ████ ",
                    " ██  ██",
                    "████████",
                    "██    ██"
                ],
                # Add more slanted characters...
            }
        }
    
    def _get_small_font(self) -> Dict:
        return {
            'height': 3,
            'chars': {
                'A': ["▄█▄", "█▀█", "▀ ▀"],
                'B': ["██▄", "██▄", "██▀"],
                'C': ["▄██", "█  ", "▀██"],
                'D': ["██▄", "█ █", "██▀"],
                'E': ["███", "██▄", "███"],
                'F': ["███", "██▄", "█  "],
                'G': ["▄██", "█▄█", "▀██"],
                'H': ["█ █", "███", "█ █"],
                'I': ["███", " █ ", "███"],
                'J': ["███", "  █", "██▀"],
                'K': ["█▄█", "██▄", "█ █"],
                'L': ["█  ", "█  ", "███"],
                'M': ["█▄█", "███", "█ █"],
                'N': ["█▄█", "███", "█▀█"],
                'O': ["▄█▄", "█ █", "▀█▀"],
                'P': ["██▄", "██▀", "█  "],
                'Q': ["▄█▄", "█▄█", "▀██"],
                'R': ["██▄", "██▄", "█ █"],
                'S': ["▄██", "▀█▄", "██▀"],
                'T': ["███", " █ ", " █ "],
                'U': ["█ █", "█ █", "▀█▀"],
                'V': ["█ █", "█ █", " █ "],
                'W': ["█ █", "███", "▀▄▀"],
                'X': ["█▄█", " █ ", "█▀█"],
                'Y': ["█ █", " █ ", " █ "],
                'Z': ["███", "▄█▄", "███"],
                '0': ["▄█▄", "█ █", "▀█▀"],
                '1': [" █ ", " █ ", " █ "],
                '2': ["██▄", "▄█▀", "███"],
                '3': ["██▄", " █▄", "██▀"],
                '4': ["█ █", "▀█▀", "  █"],
                '5': ["███", "██▄", "██▀"],
                '6': ["▄█▄", "██▄", "▀█▀"],
                '7': ["███", "  █", "  █"],
                '8': ["▄█▄", "▄█▄", "▀█▀"],
                '9': ["▄█▄", "▀██", "▀█▀"],
                '!': [" █ ", " █ ", " ▄ "],
                '?': ["██▄", " █▀", " ▄ "],
                '.': ["   ", "   ", " ▄ "],
                ' ': ["   ", "   ", "   "]
            }
        }
    
    def _get_mini_font(self) -> Dict:
        return {
            'height': 1,
            'chars': {
                'A': ["▲"],
                'B': ["■"],
                'C': ["◐"],
                'D': ["◗"],
                'E': ["≡"],
                'F': ["⌐"],
                'G': ["◑"],
                'H': ["╫"],
                'I': ["│"],
                'J': ["⌐"],
                'K': ["╫"],
                'L': ["└"],
                'M': ["╫"],
                'N': ["╫"],
                'O': ["●"],
                'P': ["⌐"],
                'Q': ["◎"],
                'R': ["⌐"],
                'S': ["§"],
                'T': ["┬"],
                'U': ["∪"],
                'V': ["∨"],
                'W': ["╫"],
                'X': ["×"],
                'Y': ["¥"],
                'Z': ["≈"],
                '0': ["●"],
                '1': ["│"],
                '2': ["≈"],
                '3': ["≈"],
                '4': ["╫"],
                '5': ["§"],
                '6': ["◐"],
                '7': ["⌐"],
                '8': ["●"],
                '9': ["◎"],
                '!': ["!"],
                '?': ["?"],
                '.': ["."],
                ' ': [" "]
            }
        }
    
    def list_fonts(self) -> List[str]:
        return [font.value for font in ASCIIFont]
    
    def get_productivity_celebration(self, achievement: str) -> str:
        celebrations = [
            f"🎉 {achievement.upper()} 🎉",
            f"⭐ {achievement.upper()} ⭐",
            f"🚀 {achievement.upper()} 🚀",
            f"💪 {achievement.upper()} 💪",
            f"🏆 {achievement.upper()} 🏆"
        ]
        
        import random
        celebration_text = random.choice(celebrations)
        
        return self.generate_ascii_art(
            celebration_text,
            font="standard",
            justify="center",
            border=True,
            color="bright_green"
        )



    def _get_speed_font(self) -> Dict[str, List[str]]:
        return {
            'L': [
                '██      ',
                '██      ',
                '██      ',
                '██      ',
                '████████'
            ],
            'O': [
                ' ██████ ',
                '██    ██',
                '██    ██',
                '██    ██',
                ' ██████ '
            ],
            'G': [
                ' ██████ ',
                '██      ',
                '██  ████',
                '██    ██',
                ' ██████ '
            ],
            'B': [
                '███████ ',
                '██    ██',
                '███████ ',
                '██    ██',
                '███████ '
            ],
            'U': [
                '██    ██',
                '██    ██',
                '██    ██',
                '██    ██',
                ' ██████ '
            ],
            'C': [
                ' ██████ ',
                '██      ',
                '██      ',
                '██      ',
                ' ██████ '
            ],
            'H': [
                '██    ██',
                '██    ██',
                '████████',
                '██    ██',
                '██    ██'
            ],
            ' ': [
                '        ',
                '        ',
                '        ',
                '        ',
                '        '
            ],
            '!': [
                '██',
                '██',
                '██',
                '  ',
                '██'
            ],
        }
    
    def _get_metal_font(self) -> Dict[str, List[str]]:
        return {
            'L': [
                '██      ',
                '██      ',
                '██      ',
                '██      ',
                '████████'
            ],
            'O': [
                '████████',
                '██    ██',
                '██    ██',
                '██    ██',
                '████████'
            ],
            'G': [
                '████████',
                '██      ',
                '██  ████',
                '██    ██',
                '████████'
            ],
            'B': [
                '███████ ',
                '██    ██',
                '███████ ',
                '██    ██',
                '███████ '
            ],
            'U': [
                '██    ██',
                '██    ██',
                '██    ██',
                '██    ██',
                '████████'
            ],
            'C': [
                '████████',
                '██      ',
                '██      ',
                '██      ',
                '████████'
            ],
            'H': [
                '██    ██',
                '██    ██',
                '████████',
                '██    ██',
                '██    ██'
            ],
            ' ': [
                '        ',
                '        ',
                '        ',
                '        ',
                '        '
            ],
            '!': [
                '██',
                '██',
                '██',
                '  ',
                '██'
            ],
        }


# Export for CLI integration
__all__ = ['ASCIIArtGenerator', 'ASCIIFont']
