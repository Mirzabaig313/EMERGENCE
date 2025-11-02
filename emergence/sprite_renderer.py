"""
Grayscale Sprite Renderer for EMERGENCE.

Provides rendering capabilities for grayscale block art creature sprites
with support for positioning, flipping, and tinting effects.
"""

from typing import List, Optional, Tuple, Callable
from .sprites_grayscale import (
    CREATURE_SPRITES,
    get_creature_sprite,
    get_creature_info,
    SpriteData
)


class GrayscaleSpriteRenderer:
    """Renderer for grayscale block art creature sprites."""
    
    # Grayscale character progression (darkest to lightest)
    GRAYSCALE_CHARS = [' ', '░', '▒', '▓', '█']
    
    # Character mapping for shading adjustments
    CHAR_TO_INDEX = {
        ' ': 0,
        '░': 1,
        '▒': 2,
        '▓': 3,
        '█': 4,
        '▀': 3,  # Treat half blocks as dark
        '▄': 3,
        '▌': 3,
        '▐': 3,
        '■': 4,  # Small filled as solid
        '□': 1,  # Small empty as light
        '▪': 4,
        '▫': 1,
    }
    
    def __init__(self, output_handler: Optional[Callable] = None):
        """
        Initialize the sprite renderer.
        
        Args:
            output_handler: Optional function to handle output.
                          If None, uses print().
        """
        self.output_handler = output_handler or print
        self.sprites = CREATURE_SPRITES
    
    def render_sprite(
        self,
        creature_type: str,
        state: str = 'idle',
        x: int = 0,
        y: int = 0,
        facing: str = 'right',
        tint: Optional[str] = None
    ) -> List[str]:
        """
        Render a sprite and return the lines.
        
        Args:
            creature_type: Type of creature to render
            state: Animation state ('idle', 'attack', 'damaged', 'death')
            x: X position (for offset in output)
            y: Y position (for offset in output)
            facing: Direction ('left' or 'right')
            tint: Optional tint ('lighter', 'darker', None)
        
        Returns:
            List of sprite lines ready for rendering
        """
        sprite_lines = get_creature_sprite(creature_type, state, facing)
        
        if sprite_lines is None:
            return []
        
        # Apply tinting if requested
        if tint:
            sprite_lines = self.apply_tint(sprite_lines, tint)
        
        return sprite_lines
    
    def render_sprite_to_console(
        self,
        creature_type: str,
        state: str = 'idle',
        x: int = 0,
        y: int = 0,
        facing: str = 'right',
        tint: Optional[str] = None
    ) -> None:
        """
        Render a sprite directly to console at given position.
        
        Args:
            creature_type: Type of creature to render
            state: Animation state ('idle', 'attack', 'damaged', 'death')
            x: X position (column)
            y: Y position (row)
            facing: Direction ('left' or 'right')
            tint: Optional tint ('lighter', 'darker', None)
        """
        sprite_lines = self.render_sprite(
            creature_type, state, x, y, facing, tint
        )
        
        for i, line in enumerate(sprite_lines):
            # Add positioning prefix (ANSI escape codes could be used here)
            positioned_line = ' ' * x + line
            self.output_handler(positioned_line)
    
    def apply_tint(
        self,
        sprite_lines: SpriteData,
        tint_level: str
    ) -> SpriteData:
        """
        Apply a tint effect to darken or lighten sprite.
        
        Args:
            sprite_lines: Original sprite lines
            tint_level: 'lighter' or 'darker'
        
        Returns:
            Modified sprite lines with tint applied
        """
        if tint_level == 'lighter':
            shift = -1
        elif tint_level == 'darker':
            shift = 1
        else:
            return sprite_lines
        
        tinted_lines = []
        for line in sprite_lines:
            tinted_line = ''
            for char in line:
                if char in self.CHAR_TO_INDEX:
                    current_index = self.CHAR_TO_INDEX[char]
                    new_index = max(0, min(4, current_index + shift))
                    tinted_line += self.GRAYSCALE_CHARS[new_index]
                else:
                    # Preserve special characters
                    tinted_line += char
            tinted_lines.append(tinted_line)
        
        return tinted_lines
    
    def get_sprite_dimensions(
        self,
        creature_type: str
    ) -> Optional[Tuple[int, int]]:
        """
        Get the dimensions of a sprite.
        
        Args:
            creature_type: Type of creature
        
        Returns:
            Tuple of (width, height) or None if not found
        """
        info = get_creature_info(creature_type)
        if info:
            return (info['width'], info['height'])
        return None
    
    def get_sprite_anchor(
        self,
        creature_type: str
    ) -> Optional[Tuple[int, int]]:
        """
        Get the anchor point (ground position) of a sprite.
        
        Args:
            creature_type: Type of creature
        
        Returns:
            Tuple of (anchor_x, anchor_y) or None if not found
        """
        info = get_creature_info(creature_type)
        if info:
            return (info['anchor_x'], info['anchor_y'])
        return None
    
    def render_sprite_gallery(
        self,
        creature_types: Optional[List[str]] = None,
        states: Optional[List[str]] = None
    ) -> None:
        """
        Render a gallery of sprites for visual reference.
        
        Args:
            creature_types: List of creature types to show (None = all)
            states: List of states to show (None = all)
        """
        if creature_types is None:
            creature_types = list(self.sprites.keys())
        
        if states is None:
            states = ['idle', 'attack', 'damaged', 'death']
        
        for creature_type in creature_types:
            self.output_handler(f"\n{'=' * 80}")
            self.output_handler(f"CREATURE: {creature_type.upper()}")
            
            info = get_creature_info(creature_type)
            if info:
                self.output_handler(
                    f"Tier: {info['tier']} | "
                    f"Category: {info['category']} | "
                    f"Size: {info['width']}x{info['height']}"
                )
            
            self.output_handler(f"{'=' * 80}\n")
            
            for state in states:
                sprite_lines = self.render_sprite(creature_type, state)
                if sprite_lines:
                    self.output_handler(f"--- {state.upper()} ---")
                    for line in sprite_lines:
                        self.output_handler(line)
                    self.output_handler("")
    
    def compare_sprites_side_by_side(
        self,
        creature_type: str,
        states: Optional[List[str]] = None
    ) -> None:
        """
        Display multiple states of a creature side by side.
        
        Args:
            creature_type: Type of creature to compare
            states: List of states to compare (None = all)
        """
        if states is None:
            states = ['idle', 'attack', 'damaged', 'death']
        
        # Get all sprite data
        sprite_sets = []
        max_height = 0
        
        for state in states:
            sprite_lines = self.render_sprite(creature_type, state)
            if sprite_lines:
                sprite_sets.append((state, sprite_lines))
                max_height = max(max_height, len(sprite_lines))
        
        if not sprite_sets:
            self.output_handler(f"No sprites found for {creature_type}")
            return
        
        # Print header
        self.output_handler(f"\n{creature_type.upper()} - Side by Side Comparison")
        self.output_handler("=" * 120)
        
        # Print state labels
        header = ""
        for state, _ in sprite_sets:
            header += f"{state.upper():^40}"
        self.output_handler(header)
        self.output_handler("-" * 120)
        
        # Print sprites line by line
        for line_idx in range(max_height):
            line_output = ""
            for state, sprite_lines in sprite_sets:
                if line_idx < len(sprite_lines):
                    # Pad to 40 characters for alignment
                    line_output += f"{sprite_lines[line_idx]:40}"
                else:
                    line_output += " " * 40
            self.output_handler(line_output)
        
        self.output_handler("")
    
    def render_sprite_with_border(
        self,
        creature_type: str,
        state: str = 'idle',
        facing: str = 'right'
    ) -> None:
        """
        Render a sprite with a decorative border.
        
        Args:
            creature_type: Type of creature to render
            state: Animation state
            facing: Direction
        """
        sprite_lines = self.render_sprite(creature_type, state, facing=facing)
        
        if not sprite_lines:
            return
        
        info = get_creature_info(creature_type)
        width = info['width'] if info else max(len(line) for line in sprite_lines)
        
        # Top border
        self.output_handler("┌" + "─" * (width + 2) + "┐")
        
        # Sprite with side borders
        for line in sprite_lines:
            padded_line = line + " " * (width - len(line))
            self.output_handler(f"│ {padded_line} │")
        
        # Bottom border
        self.output_handler("└" + "─" * (width + 2) + "┘")
        
        # Info
        if info:
            self.output_handler(
                f"  {creature_type} - {state} - "
                f"Tier {info['tier']} {info['category']}"
            )


def create_sprite_sheet(
    creature_types: List[str],
    state: str = 'idle',
    columns: int = 3
) -> List[str]:
    """
    Create a sprite sheet with multiple creatures arranged in a grid.
    
    Args:
        creature_types: List of creatures to include
        state: Animation state to use
        columns: Number of columns in grid
    
    Returns:
        List of lines representing the sprite sheet
    """
    renderer = GrayscaleSpriteRenderer()
    rows = []
    current_row = []
    max_height_in_row = 0
    
    for i, creature_type in enumerate(creature_types):
        sprite_lines = renderer.render_sprite(creature_type, state)
        if not sprite_lines:
            continue
        
        current_row.append((creature_type, sprite_lines))
        max_height_in_row = max(max_height_in_row, len(sprite_lines))
        
        # Start new row if we've reached column limit
        if len(current_row) == columns or i == len(creature_types) - 1:
            rows.append((current_row, max_height_in_row))
            current_row = []
            max_height_in_row = 0
    
    # Build output
    output_lines = []
    for row_data, max_height in rows:
        # Create lines for this row
        for line_idx in range(max_height):
            line = ""
            for creature_type, sprite_lines in row_data:
                if line_idx < len(sprite_lines):
                    line += sprite_lines[line_idx] + "  "  # Add spacing
                else:
                    # Pad with spaces
                    info = get_creature_info(creature_type)
                    width = info['width'] if info else 20
                    line += " " * (width + 2)
            output_lines.append(line)
        
        # Add labels below each sprite
        label_line = ""
        for creature_type, _ in row_data:
            info = get_creature_info(creature_type)
            width = info['width'] if info else 20
            label = creature_type.replace('_', ' ').title()
            label_line += f"{label:^{width}}  "
        output_lines.append(label_line)
        output_lines.append("")  # Blank line between rows
    
    return output_lines


def render_animation_preview(
    creature_type: str,
    states: Optional[List[str]] = None,
    delay: float = 0.5
) -> None:
    """
    Render an animation preview cycling through states.
    
    Args:
        creature_type: Type of creature to animate
        states: List of states to cycle through
        delay: Delay between frames in seconds
    """
    import time
    import os
    
    if states is None:
        states = ['idle', 'attack', 'damaged', 'death', 'idle']
    
    renderer = GrayscaleSpriteRenderer()
    
    print(f"\nAnimation Preview: {creature_type.upper()}")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            for state in states:
                # Clear screen (works on Unix-like systems)
                if os.name != 'nt':
                    os.system('clear')
                else:
                    os.system('cls')
                
                print(f"\nState: {state.upper()}")
                print("-" * 40)
                
                sprite_lines = renderer.render_sprite(creature_type, state)
                for line in sprite_lines:
                    print(line)
                
                time.sleep(delay)
    except KeyboardInterrupt:
        print("\n\nAnimation stopped.")
