"""
Terrain textures and background patterns for EMERGENCE.

Provides block character palettes, terrain textures, heatmap rendering,
progress bars, and pre-built scenes for campfire, village, dashboard HUD,
and population graphs.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass

from emergence.sprites import SpriteLibrary, SpritePatterns, create_heatmap_cell


@dataclass
class TerrainPalette:
    """Palette of block characters used for terrain rendering."""
    solid: str = '█'
    dark: str = '▓'
    medium: str = '▒'
    light: str = '░'
    empty: str = ' '
    upper: str = '▀'
    lower: str = '▄'
    left: str = '▌'
    right: str = '▐'
    square_black: str = '■'
    square_white: str = '□'
    small_black: str = '▪'
    small_white: str = '▫'


class TerrainTextures:
    """Predefined terrain textures using emoji and block characters."""
    TEXTURES: Dict[str, List[str]] = {
        'plains': [
            "🌾🌾🌾🌾🌾",
            "🌾░🌾░🌾",
            "🌾🌾🌾🌾🌾"
        ],
        'forest_dense': [
            "🌲🌲🌳🌲🌲",
            "🌳▓▓▓🌲",
            "🌲▓▓▓🌳"
        ],
        'desert': [
            "🏜️░░░🏜️",
            "░▒░▒░",
            "░░▒░░"
        ],
        'water': [
            "💧≈≈≈💧",
            "≈░≈░≈",
            "💧≈≈≈💧"
        ],
        'mountain': [
            "  🏔️  ",
            " /▓▓\\ ",
            "/▒▒▒▒\\"
        ],
        'ice': [
            "❄️░❄️░❄️",
            "░❄️░❄️░",
            "❄️░❄️░❄️"
        ],
        'volcano': [
            "  🔥  ",
            " ▓▓▓ ",
            " ▒▒▒ ",
            " ░░░ "
        ]
    }
    
    @classmethod
    def get_texture(cls, name: str) -> List[str]:
        """Get a texture by name."""
        return cls.TEXTURES.get(name, [])

    @classmethod
    def render_texture(cls, name: str, width: int, height: int) -> List[str]:
        """Render a texture to the desired width and height by tiling."""
        texture = cls.get_texture(name)
        if not texture:
            return [' ' * width for _ in range(height)]
        
        rendered = []
        texture_height = len(texture)
        texture_width = len(texture[0]) if texture else 0
        
        for row in range(height):
            base_row = texture[row % texture_height]
            tiled_row = ''.join(base_row[(col % texture_width)] for col in range(width))
            rendered.append(tiled_row)
        
        return rendered


def render_heatmap(grid: List[List[float]], max_value: float = 1.0) -> List[str]:
    """Render a heatmap using colored square emojis."""
    if not grid:
        return []
    
    rendered = []
    for row in grid:
        rendered_row = ''.join(create_heatmap_cell(value, max_value) for value in row)
        rendered.append(rendered_row)
    return rendered


def render_progress_bar(label: str, current: float, maximum: float, width: int = 10) -> str:
    """Render a progress bar using block characters."""
    ratio = min(1.0, max(0.0, current / maximum))
    filled = int(ratio * width)
    empty = width - filled
    bar = '█' * filled + '░' * empty
    return f"{label}: {bar} {current:.0f}/{maximum:.0f}"


def render_energy_bar(current: float, maximum: float, width: int = 10) -> str:
    """Render energy bar with darker blocks."""
    ratio = min(1.0, max(0.0, current / maximum))
    filled = int(ratio * width)
    empty = width - filled
    bar = '▓' * filled + '▒' * empty
    return f"EN: {bar} {current:.0f}/{maximum:.0f}"


def render_fitness_indicator(value: float, width: int = 20) -> str:
    """Render fitness indicator bar."""
    ratio = min(1.0, max(0.0, value / 1000.0))
    filled = int(ratio * width)
    empty = width - filled
    bar = '▓' * filled + '░' * empty
    return f"FIT: {bar} {value:.0f}"


SCENES: Dict[str, List[str]] = {
    'campfire': [
        "        ✨        ",
        "       🔥🔥       ",
        "      🔥🔥🔥      ",
        "     ▓▓▓▓▓▓     ",
        "    ▒▒▒▒▒▒▒▒    ",
        "   ░░░░░░░░░░   ",
        "",  # Blank line
        "  🪵══════🪵  ",
        "",  # Blank line
        "  🐰   🔥   🦊  "
    ],
    'village': [
        "╔══════ SETTLEMENT ══════╗",
        "║                        ║",
        "║  🏠  🏠  🏠           ║",
        "║  🏘️  🏘️  🏘️           ║",
        "║                        ║",
        "║     🌲  🌲            ║",
        "║  🐰 🐰 🐰  🦊         ║",
        "║                        ║",
        "╚════════════════════════╝"
    ],
    'animal_sprite': [
        "     ▄▄▄     ",
        "   ▄█████▄   ",
        "  ████▓████  ",
        "  ██▓▒▓▒▓██  ",
        "  ████████   ",
        "   ▀█████▀   ",
        "    ▀▀▀▀     "
    ],
    'dashboard_hud': [
        "╔══════════════ DASHBOARD ═══════════════╗",
        "║                                         ║",
        "║  ┏━━━━ POPULATION ━━━━┓               ║",
        "║  ┃ 🐰 Herbivores: 42  ┃  📈 Trending ↑ ║",
        "║  ┃ 🦊 Carnivores: 15  ┃  📉 Stable  → ║",
        "║  ┃ 🌱 Plants: 234     ┃  📊 Growing ↑ ║",
        "║  ┗━━━━━━━━━━━━━━━━━━━┛               ║",
        "║                                         ║",
        "║  ┏━━━━ ECOSYSTEM ━━━━━┓               ║",
        "║  ┃ Balance: ████████  ┃  ✅ Healthy   ║",
        "║  ┃ Food:    ██████░░  ┃  ⚠️ Low      ║",
        "║  ┃ Energy:  █████████ ┃  ✅ High     ║",
        "║  ┗━━━━━━━━━━━━━━━━━━━┛               ║",
        "║                                         ║",
        "║  ┏━━━ FITNESS TREND ━━━┓              ║",
        "║  ┃ Avg: 847 (+23)      ┃              ║",
        "║  ┃ ▁▂▃▄▅▆▇█             ┃              ║",
        "║  ┗━━━━━━━━━━━━━━━━━━━━┛              ║",
        "╚═════════════════════════════════════════╝"
    ],
    'population_graph': [
        "Population (Last 50 generations)",
        "200│         ╱╲     ╱╲",
        "   │       ╱  ╲   ╱  ╲    🐰 ████████",
        "150│     ╱    ╲ ╱    ╲   🦊 ████",
        "   │   ╱      ╲╱      ╲",
        "100│ ╱                 ╲",
        "   └─────────────────────",
        "    0   10   20   30   40   50",
        "",
        "█▇▆▅▆▇█▇▆▅▄▅▆▇█ Herbivores",
        "▂▃▄▅▄▃▂▃▄▅▆▅▄▃▂ Carnivores"
    ],
    'real_time_animation': [
        "Herbivore Animation (10 FPS):",
        " idle:  ['🐰', '🐰', '🐇', '🐰', '🐰', '🐇', '🐰', '🐰', '🐰', '🐰']",
        " walk:  ['🐰', '🐇', '🐰', '🐇', '🐰', '🐇', '🐰', '🐇', '🐰', '🐇']",
        " run:   ['💨', '🐇', '💨', '🐇', '💨', '🐇', '💨', '🐇', '💨', '🐇']",
        " eat:   ['🐰', '😋', '🐰', '🌱', '🐰', '😋', '🐰', '🌱', '🐰', '✅']",
        " breed: ['❤️', '🐰', '❤️', '🐰', '✨', '👶', '✨', '🐰', '🐰', '🐰']",
        "",
        "Carnivore Animation:",
        " idle:   ['🦊', '🦊', '👁️', '🦊', '🦊', '👁️', '🦊', '🦊', '🦊', '🦊']",
        " hunt:   ['🦊', '👁️', '🏃', '💨', '⚡', '🦊', '👁️', '🏃', '💨', '⚡']",
        " attack: ['🦊', '💥', '🔴', '🦊', '💥', '🔴', '🦊', '😋', '✅', '🦊']",
        " eat:    ['🦊', '🍖', '😋', '🦊', '🍖', '😋', '🦊', '✅', '🦊', '🦊']",
        "",
        "Plant Animation:",
        " grow:   ['·', '\'', '¸', '🌱', '🌿', '🌿', '🌿', '🌿', '🌿', '🌿']",
        " die:    ['🌿', '🍂', '🍂', '·', '·', ' ', ' ', ' ', ' ', ' ']"
    ]
}


def render_scene(name: str) -> List[str]:
    """Render a specific scene."""
    return SCENES.get(name, [])


def list_scenes() -> List[str]:
    """List available predefined scenes."""
    return list(SCENES.keys())
