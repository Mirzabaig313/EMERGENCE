"""
Sprite flipping utilities for grayscale block art sprites.

Provides horizontal flipping that respects directional Unicode block
characters to ensure mirrored sprites maintain correct silhouettes.
"""

from typing import List

# Mapping for characters that need to change when flipped horizontally
FLIP_CHAR_MAP = {
    '▌': '▐',
    '▐': '▌',
    '/': '\\',
    '\\': '/',
    '(': ')',
    ')': '(',
    '<': '>',
    '>': '<',
    '[': ']',
    ']': '[',
    '{': '}',
    '}': '{',
}


def flip_line_horizontal(line: str) -> str:
    """
    Flip a single line of sprite art horizontally.
    
    Args:
        line: Line to flip
    
    Returns:
        Flipped line with directional characters mapped appropriately
    """
    flipped_chars = []
    for char in reversed(line):
        flipped_chars.append(FLIP_CHAR_MAP.get(char, char))
    return ''.join(flipped_chars)


def flip_sprite_horizontal(sprite_lines: List[str]) -> List[str]:
    """
    Flip an entire sprite horizontally.
    
    Args:
        sprite_lines: Sprite represented as list of strings
    
    Returns:
        Horizontally flipped sprite
    """
    return [flip_line_horizontal(line) for line in sprite_lines]
