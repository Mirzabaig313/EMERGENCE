"""
Color scheme definitions for EMERGENCE terminal art assets.

Provides ANSI color codes using rich.color for creatures, terrain, UI, and messages.
Supports theme switching and color customization.
"""

from rich.color import Color
from typing import Dict, Any


class ColorScheme:
    """Color scheme for EMERGENCE visual assets."""
    
    # Herbivores (green spectrum)
    HERBIVORE_HEALTHY = Color.from_rgb(0, 255, 0)      # bright green
    HERBIVORE_HUNGRY = Color.from_rgb(200, 200, 0)     # yellow
    HERBIVORE_BABY = Color.from_rgb(150, 255, 150)     # light green
    HERBIVORE_ELDERLY = Color.from_rgb(100, 150, 100)  # dark green
    
    # Carnivores (red spectrum)
    CARNIVORE_NORMAL = Color.from_rgb(255, 69, 0)      # red-orange
    CARNIVORE_HUNTING = Color.from_rgb(255, 0, 0)      # bright red
    CARNIVORE_APEX = Color.from_rgb(139, 0, 0)         # dark red
    CARNIVORE_BABY = Color.from_rgb(255, 150, 150)     # light red
    
    # Special creatures
    SCAVENGER = Color.from_rgb(128, 128, 128)          # gray
    OMNIVORE = Color.from_rgb(139, 69, 19)             # brown
    CAMOUFLAGE = Color.from_rgb(100, 100, 60)          # olive
    MYTHICAL = Color.from_rgb(138, 43, 226)            # purple
    MYTHICAL_DRAGON = Color.from_rgb(255, 0, 255)      # magenta
    MYTHICAL_UNICORN = Color.from_rgb(255, 192, 203)   # pink
    
    # Plants (green spectrum)
    PLANT_YOUNG = Color.from_rgb(50, 205, 50)          # lime green
    PLANT_MATURE = Color.from_rgb(34, 139, 34)         # forest green
    PLANT_DYING = Color.from_rgb(139, 69, 19)          # brown
    PLANT_SEED = Color.from_rgb(160, 82, 45)           # sienna
    
    # Terrain
    WATER = Color.from_rgb(0, 191, 255)                # deep sky blue
    WATER_DEEP = Color.from_rgb(0, 105, 148)           # dark blue
    DESERT = Color.from_rgb(255, 215, 0)               # gold/sand
    FOREST = Color.from_rgb(34, 139, 34)               # forest green
    MOUNTAIN = Color.from_rgb(169, 169, 169)           # gray
    MOUNTAIN_PEAK = Color.from_rgb(255, 255, 255)      # white
    PLAINS = Color.from_rgb(154, 205, 50)              # yellow-green
    ICE = Color.from_rgb(175, 238, 238)                # pale turquoise
    FIRE = Color.from_rgb(255, 69, 0)                  # red-orange
    
    # UI Colors (Neon/Futuristic)
    UI_BORDER = Color.from_rgb(0, 255, 255)            # cyan
    UI_HEADER = Color.from_rgb(0, 191, 255)            # deep sky blue
    UI_TEXT = Color.from_rgb(255, 255, 255)            # white
    UI_DIM = Color.from_rgb(128, 128, 128)             # gray
    UI_HIGHLIGHT = Color.from_rgb(255, 255, 0)         # yellow
    UI_SUCCESS = Color.from_rgb(0, 255, 0)             # green
    UI_ERROR = Color.from_rgb(255, 0, 0)               # red
    UI_WARNING = Color.from_rgb(255, 165, 0)           # orange
    UI_INFO = Color.from_rgb(0, 191, 255)              # cyan
    
    # Graph colors (vibrant)
    GRAPH_LINE1 = Color.from_rgb(0, 255, 127)          # spring green
    GRAPH_LINE2 = Color.from_rgb(255, 20, 147)         # deep pink
    GRAPH_LINE3 = Color.from_rgb(255, 215, 0)          # gold
    GRAPH_LINE4 = Color.from_rgb(138, 43, 226)         # blue violet
    GRAPH_LINE5 = Color.from_rgb(0, 255, 255)          # cyan
    GRAPH_GRID = Color.from_rgb(64, 64, 64)            # dark gray
    GRAPH_AXIS = Color.from_rgb(128, 128, 128)         # gray
    
    # Message Log Colors
    MSG_NORMAL = Color.from_rgb(200, 200, 200)         # light gray
    MSG_BIRTH = Color.from_rgb(0, 255, 0)              # green
    MSG_DEATH = Color.from_rgb(255, 0, 0)              # red
    MSG_EVOLUTION = Color.from_rgb(138, 43, 226)       # purple
    MSG_ACHIEVEMENT = Color.from_rgb(255, 215, 0)      # gold
    MSG_WARNING = Color.from_rgb(255, 165, 0)          # orange
    MSG_INFO = Color.from_rgb(0, 191, 255)             # cyan
    MSG_DEBUG = Color.from_rgb(128, 128, 128)          # gray
    
    # Status indicators
    STATUS_SLEEPING = Color.from_rgb(100, 100, 255)    # light blue
    STATUS_BREEDING = Color.from_rgb(255, 105, 180)    # hot pink
    STATUS_INJURED = Color.from_rgb(255, 0, 0)         # red
    STATUS_ENERGIZED = Color.from_rgb(255, 255, 0)     # yellow
    STATUS_TIRED = Color.from_rgb(128, 128, 128)       # gray
    STATUS_EATING = Color.from_rgb(0, 255, 0)          # green
    STATUS_SCARED = Color.from_rgb(255, 165, 0)        # orange
    STATUS_AGGRESSIVE = Color.from_rgb(255, 0, 0)      # red


class ThemeManager:
    """Manages color themes and allows theme switching."""
    
    THEMES: Dict[str, Dict[str, Any]] = {
        'default': {
            'name': 'Neon Terminal',
            'description': 'Bright neon colors on dark background',
            'scheme': ColorScheme
        },
        'dark': {
            'name': 'Dark Mode',
            'description': 'Muted colors for low-light environments',
            'scheme': ColorScheme  # Would have different colors
        },
        'light': {
            'name': 'Light Mode',
            'description': 'High contrast for bright environments',
            'scheme': ColorScheme  # Would have different colors
        },
        'retro': {
            'name': 'Retro Terminal',
            'description': 'Classic green phosphor terminal',
            'scheme': ColorScheme  # Would have different colors
        },
        'cyberpunk': {
            'name': 'Cyberpunk',
            'description': 'Pink and cyan neon aesthetic',
            'scheme': ColorScheme  # Would have different colors
        }
    }
    
    def __init__(self, theme: str = 'default'):
        self.current_theme = theme
        self.scheme = self.THEMES[theme]['scheme']
    
    def set_theme(self, theme: str) -> bool:
        """Switch to a different color theme."""
        if theme in self.THEMES:
            self.current_theme = theme
            self.scheme = self.THEMES[theme]['scheme']
            return True
        return False
    
    def get_theme_info(self, theme: str) -> Dict[str, str]:
        """Get information about a theme."""
        if theme in self.THEMES:
            return {
                'name': self.THEMES[theme]['name'],
                'description': self.THEMES[theme]['description']
            }
        return {}
    
    def list_themes(self) -> list:
        """List all available themes."""
        return list(self.THEMES.keys())


# Helper functions for color manipulation
def get_creature_color(species: str, age: float, health: float, energy: float) -> Color:
    """Get the appropriate color for a creature based on its state."""
    if species == 'herbivore':
        if age < 100:  # Baby
            return ColorScheme.HERBIVORE_BABY
        elif health < 30:
            return ColorScheme.HERBIVORE_HUNGRY
        elif age > 1000:  # Elderly
            return ColorScheme.HERBIVORE_ELDERLY
        else:
            return ColorScheme.HERBIVORE_HEALTHY
    
    elif species == 'carnivore':
        if age < 100:  # Baby
            return ColorScheme.CARNIVORE_BABY
        elif energy > 80:
            return ColorScheme.CARNIVORE_HUNTING
        else:
            return ColorScheme.CARNIVORE_NORMAL
    
    elif species == 'dragon':
        return ColorScheme.MYTHICAL_DRAGON
    
    elif species == 'unicorn':
        return ColorScheme.MYTHICAL_UNICORN
    
    else:
        return ColorScheme.UI_TEXT


def get_plant_color(age: float, health: float) -> Color:
    """Get the appropriate color for a plant based on its state."""
    if age < 50:  # Young
        return ColorScheme.PLANT_YOUNG
    elif health < 30:  # Dying
        return ColorScheme.PLANT_DYING
    else:  # Mature
        return ColorScheme.PLANT_MATURE


def get_terrain_color(terrain_type: str) -> Color:
    """Get the appropriate color for terrain."""
    terrain_colors = {
        'water': ColorScheme.WATER,
        'water_deep': ColorScheme.WATER_DEEP,
        'desert': ColorScheme.DESERT,
        'forest': ColorScheme.FOREST,
        'mountain': ColorScheme.MOUNTAIN,
        'plains': ColorScheme.PLAINS,
        'ice': ColorScheme.ICE,
        'fire': ColorScheme.FIRE
    }
    return terrain_colors.get(terrain_type, ColorScheme.PLAINS)


def get_message_color(message_type: str) -> Color:
    """Get the appropriate color for a message type."""
    message_colors = {
        'normal': ColorScheme.MSG_NORMAL,
        'birth': ColorScheme.MSG_BIRTH,
        'death': ColorScheme.MSG_DEATH,
        'evolution': ColorScheme.MSG_EVOLUTION,
        'achievement': ColorScheme.MSG_ACHIEVEMENT,
        'warning': ColorScheme.MSG_WARNING,
        'info': ColorScheme.MSG_INFO,
        'debug': ColorScheme.MSG_DEBUG
    }
    return message_colors.get(message_type, ColorScheme.MSG_NORMAL)


# Default theme manager instance
default_theme = ThemeManager()
