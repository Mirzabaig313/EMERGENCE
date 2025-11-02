"""
Sprite definitions for EMERGENCE terminal art assets.

Provides emoji-based and Unicode character sprites for all entities,
creatures, plants, terrain features, and UI indicators.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Sprite:
    """Represents a single sprite."""
    char: str
    description: str
    category: str


class SpriteLibrary:
    """Library of all available sprites for EMERGENCE."""
    
    # Primary Herbivores
    HERBIVORE_RABBIT = '🐰'
    HERBIVORE_RABBIT_FAST = '🐇'
    HERBIVORE_DEER = '🦌'
    HERBIVORE_MOUSE = '🐁'
    
    # Primary Carnivores
    CARNIVORE_FOX = '🦊'
    CARNIVORE_WOLF = '🐺'
    CARNIVORE_EAGLE = '🦅'
    CARNIVORE_BEAR = '🐻'
    
    # Special Creatures
    CREATURE_LIZARD = '🦎'
    CREATURE_DRAGON = '🐉'
    CREATURE_UNICORN = '🦄'
    CREATURE_BAT = '🦇'
    CREATURE_LARVA = '🐛'
    CREATURE_EGG = '🥚'
    
    # Plants & Environment
    PLANT_SPROUT = '🌱'
    PLANT_HERB = '🌿'
    PLANT_GRASS = '🌾'
    PLANT_TREE = '🌲'
    PLANT_TREE_DECIDUOUS = '🌳'
    PLANT_CACTUS = '🌵'
    PLANT_MUSHROOM = '🍄'
    PLANT_LEAF = '🍃'
    PLANT_FALLEN_LEAF = '🍂'
    
    # Terrain Features
    TERRAIN_WATER = '💧'
    TERRAIN_OCEAN = '🌊'
    TERRAIN_MOUNTAIN = '🏔️'
    TERRAIN_DESERT = '🏜️'
    TERRAIN_ICE = '❄️'
    TERRAIN_FIRE = '🔥'
    TERRAIN_DEATH = '💀'
    
    # State Indicators (Overlays)
    STATUS_SLEEPING = '💤'
    STATUS_BREEDING = '❤️'
    STATUS_INJURED = '💔'
    STATUS_ENERGIZED = '⚡'
    STATUS_TIRED = '😴'
    STATUS_EATING = '😋'
    STATUS_SCARED = '😨'
    STATUS_ANGRY = '😡'
    STATUS_THINKING = '💭'
    STATUS_LEARNED = '💡'
    STATUS_LEVELUP = '✨'
    STATUS_ELITE = '⭐'
    STATUS_MUTATION = '💫'
    STATUS_SELECTED = '🎯'
    STATUS_OBSERVED = '👁️'
    
    # Action Effects
    EFFECT_SPARKLE = '✨'
    EFFECT_STAR = '⭐'
    EFFECT_STARBURST = '🌟'
    EFFECT_DEATH_SKULL = '💀'
    EFFECT_EXPLOSION = '💥'
    EFFECT_ZAP = '⚡'
    EFFECT_IMPACT = '💢'
    EFFECT_HEART = '❤️'
    EFFECT_GREEN_HEART = '💚'
    EFFECT_PINK_HEART = '💖'
    EFFECT_SMOKE = '💨'
    EFFECT_DNA = '🧬'
    EFFECT_MEAT = '🍖'
    EFFECT_TARGET = '🎯'
    
    # Unicode Block Elements
    BLOCK_SOLID = '█'
    BLOCK_DARK = '▓'
    BLOCK_MEDIUM = '▒'
    BLOCK_LIGHT = '░'
    BLOCK_EMPTY = ' '
    
    # Partial Blocks
    BLOCK_UPPER = '▀'
    BLOCK_LOWER = '▄'
    BLOCK_LEFT = '▌'
    BLOCK_RIGHT = '▐'
    
    # Small Blocks
    BLOCK_SMALL_BLACK = '■'
    BLOCK_SMALL_WHITE = '□'
    BLOCK_SMALL_BLACK_SQ = '▪'
    BLOCK_SMALL_WHITE_SQ = '▫'
    
    # UI Elements
    UI_ARROW_RIGHT = '▸'
    UI_ARROW_UP = '▴'
    UI_ARROW_DOWN = '▾'
    UI_CHECKMARK = '✅'
    UI_CROSS = '❌'
    UI_WARNING = '⚠️'
    UI_INFO = 'ℹ️'
    UI_QUEST = '❓'
    
    # Emoji Indicators for UI
    EMOJI_WORLD = '🌍'
    EMOJI_STATS = '📊'
    EMOJI_CHART = '📈'
    EMOJI_DNA = '🧬'
    EMOJI_SETTINGS = '⚙️'
    EMOJI_MESSAGE = '💬'
    EMOJI_SCROLL = '📜'
    EMOJI_COMMAND = '⌨️'
    
    # Trending indicators
    TREND_UP = '↑'
    TREND_DOWN = '↓'
    TREND_FLAT = '→'
    
    # Special Unicode characters
    CHAR_DOT = '·'
    CHAR_BULLET = '•'
    CHAR_TILDE = '≈'
    CHAR_SPARKLE = '※'
    CHAR_PLUS = '+'
    CHAR_MINUS = '−'
    CHAR_MULTIPLICATION = '×'
    
    # Colored squares for heatmaps
    HEAT_HIGH = '🟥'
    HEAT_MED_HIGH = '🟧'
    HEAT_MED = '🟨'
    HEAT_MED_LOW = '🟩'
    HEAT_LOW = '⬜'
    
    # Additional emoji
    EMOJI_HOUSE = '🏠'
    EMOJI_VILLAGE = '🏘️'
    EMOJI_WOOD = '🪵'
    EMOJI_CAMPFIRE = '🔥'
    
    @classmethod
    def get_herbivore_sprite(cls, variant: str = 'standard') -> str:
        """Get herbivore sprite based on variant."""
        sprites = {
            'standard': cls.HERBIVORE_RABBIT,
            'fast': cls.HERBIVORE_RABBIT_FAST,
            'large': cls.HERBIVORE_DEER,
            'small': cls.HERBIVORE_MOUSE
        }
        return sprites.get(variant, cls.HERBIVORE_RABBIT)
    
    @classmethod
    def get_carnivore_sprite(cls, variant: str = 'standard') -> str:
        """Get carnivore sprite based on variant."""
        sprites = {
            'standard': cls.CARNIVORE_FOX,
            'apex': cls.CARNIVORE_WOLF,
            'scavenger': cls.CARNIVORE_EAGLE,
            'omnivore': cls.CARNIVORE_BEAR
        }
        return sprites.get(variant, cls.CARNIVORE_FOX)
    
    @classmethod
    def get_plant_sprite(cls, growth_stage: float = 1.0) -> str:
        """Get plant sprite based on growth stage."""
        if growth_stage < 1.0:
            return cls.CHAR_DOT
        elif growth_stage < 2.0:
            return cls.PLANT_SPROUT
        elif growth_stage < 4.0:
            return cls.PLANT_HERB
        else:
            return cls.PLANT_GRASS
    
    @classmethod
    def get_terrain_sprite(cls, terrain_type: str) -> str:
        """Get terrain sprite based on type."""
        sprites = {
            'water': cls.TERRAIN_WATER,
            'ocean': cls.TERRAIN_OCEAN,
            'mountain': cls.TERRAIN_MOUNTAIN,
            'desert': cls.TERRAIN_DESERT,
            'ice': cls.TERRAIN_ICE,
            'fire': cls.TERRAIN_FIRE,
            'death': cls.TERRAIN_DEATH,
            'tree': cls.PLANT_TREE,
            'grass': cls.PLANT_GRASS
        }
        return sprites.get(terrain_type, cls.BLOCK_LIGHT)
    
    @classmethod
    def get_status_sprite(cls, status: str) -> str:
        """Get status indicator sprite."""
        sprites = {
            'sleeping': cls.STATUS_SLEEPING,
            'breeding': cls.STATUS_BREEDING,
            'injured': cls.STATUS_INJURED,
            'energized': cls.STATUS_ENERGIZED,
            'tired': cls.STATUS_TIRED,
            'eating': cls.STATUS_EATING,
            'scared': cls.STATUS_SCARED,
            'angry': cls.STATUS_ANGRY,
            'thinking': cls.STATUS_THINKING,
            'learned': cls.STATUS_LEARNED,
            'levelup': cls.STATUS_LEVELUP,
            'elite': cls.STATUS_ELITE,
            'mutation': cls.STATUS_MUTATION,
            'selected': cls.STATUS_SELECTED,
            'observed': cls.STATUS_OBSERVED
        }
        return sprites.get(status, '')
    
    @classmethod
    def get_all_sprites(cls) -> Dict[str, str]:
        """Get dictionary of all sprites."""
        return {
            name: getattr(cls, name)
            for name in dir(cls)
            if not name.startswith('_') and not callable(getattr(cls, name))
            and isinstance(getattr(cls, name), str)
        }


class SpritePatterns:
    """Pre-defined sprite patterns for terrain and effects."""
    
    # Terrain textures
    PLAINS = [
        "🌾🌾🌾🌾🌾",
        "🌾░🌾░🌾",
        "🌾🌾🌾🌾🌾"
    ]
    
    FOREST_DENSE = [
        "🌲🌲🌳🌲🌲",
        "🌳▓▓▓🌲",
        "🌲▓▓▓🌳"
    ]
    
    DESERT = [
        "🏜️░░░🏜️",
        "░▒░▒░",
        "░░▒░░"
    ]
    
    WATER = [
        "💧≈≈≈💧",
        "≈░≈░≈",
        "💧≈≈≈💧"
    ]
    
    MOUNTAIN = [
        "  🏔️  ",
        " /▓▓\\ ",
        "/▒▒▒▒\\"
    ]
    
    # Campfire scene
    CAMPFIRE = [
        "    ✨    ",
        "   🔥🔥   ",
        "  🔥🔥🔥  ",
        " ▓▓▓▓▓▓ ",
        "▒▒▒▒▒▒▒▒",
        "░░░░░░░░░░",
        "",
        "🪵══════🪵"
    ]
    
    # Village scene
    VILLAGE = [
        "  🏠  🏠  🏠  ",
        "  🏘️  🏘️  🏘️  ",
        "              ",
        "     🌲  🌲   "
    ]
    
    # Animal sprite (block art)
    ANIMAL_BLOCK = [
        "     ▄▄▄     ",
        "   ▄█████▄   ",
        "  ████▓████  ",
        "  ██▓▒▓▒▓██  ",
        "  ████████   ",
        "   ▀█████▀   ",
        "    ▀▀▀▀     "
    ]
    
    @classmethod
    def get_pattern(cls, name: str) -> List[str]:
        """Get a pattern by name."""
        return getattr(cls, name.upper(), [])


def create_progress_bar(value: float, max_value: float, width: int = 10, 
                       filled_char: str = '█', empty_char: str = '░') -> str:
    """Create a progress bar string."""
    ratio = min(1.0, max(0.0, value / max_value))
    filled_width = int(ratio * width)
    empty_width = width - filled_width
    return filled_char * filled_width + empty_char * empty_width


def create_health_bar(health: float, max_health: float = 100.0, width: int = 10) -> str:
    """Create a health bar with appropriate characters."""
    return create_progress_bar(health, max_health, width, '█', '░')


def create_energy_bar(energy: float, max_energy: float = 100.0, width: int = 10) -> str:
    """Create an energy bar with appropriate characters."""
    return create_progress_bar(energy, max_energy, width, '▓', '▒')


def create_sparkline(values: List[float], width: int = 20, height: int = 8) -> str:
    """Create a sparkline chart from values."""
    if not values:
        return ''
    
    # Sparkline characters (8 levels)
    chars = ' ▁▂▃▄▅▆▇█'
    
    # Normalize values
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val if max_val > min_val else 1.0
    
    # Create sparkline
    normalized = [(v - min_val) / range_val for v in values]
    sparkline = ''
    for val in normalized[-width:]:  # Take last 'width' values
        index = int(val * (len(chars) - 1))
        sparkline += chars[index]
    
    return sparkline


def create_heatmap_cell(value: float, max_value: float = 1.0) -> str:
    """Create a heatmap cell color based on value."""
    ratio = min(1.0, max(0.0, value / max_value))
    
    if ratio >= 0.8:
        return SpriteLibrary.HEAT_HIGH
    elif ratio >= 0.6:
        return SpriteLibrary.HEAT_MED_HIGH
    elif ratio >= 0.4:
        return SpriteLibrary.HEAT_MED
    elif ratio >= 0.2:
        return SpriteLibrary.HEAT_MED_LOW
    else:
        return SpriteLibrary.HEAT_LOW
