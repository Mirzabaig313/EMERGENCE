"""
Art Asset Manager for EMERGENCE.

Central hub for managing all terminal art assets including sprites, animations,
colors, UI elements, terrain, and effects. Provides unified interface for
accessing all visual resources in the game.
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from rich.console import Console
from rich.style import Style
from rich.text import Text

from emergence.sprites import (
    SpriteLibrary,
    create_sparkline
)
from emergence.animations import (
    AnimationLibrary,
    AnimationEngine,
    EntityAnimator,
    Animation,
    AnimationType
)
from emergence.colors import (
    ColorScheme,
    ThemeManager,
    get_creature_color,
    get_plant_color,
    get_terrain_color,
    get_message_color
)
from emergence.ui_elements import (
    BoxDrawing,
    BoxStyle,
    PanelLayout,
    UIComponents,
    AsciiArt
)
from emergence.terrain import (
    TerrainTextures,
    TerrainPalette,
    render_heatmap,
    render_progress_bar,
    render_scene,
    list_scenes
)
from emergence.effects import (
    EffectLibrary,
    EffectManager,
    EffectType,
    Effect,
    create_birth_effect,
    create_death_effect,
    create_attack_effect,
    create_evolution_effect,
    create_heal_effect,
    create_levelup_effect
)


@dataclass
class AssetConfig:
    """Configuration for the asset manager."""
    fps: int = 10
    theme: str = 'default'
    enable_animations: bool = True
    enable_effects: bool = True
    max_effects: int = 100


class ArtAssetManager:
    """
    Central manager for all EMERGENCE art assets.
    
    Provides unified access to:
    - Sprites (emoji and Unicode characters)
    - Animations (10 FPS frame-based)
    - Colors (ANSI color schemes)
    - UI Elements (box drawing and layouts)
    - Terrain (textures and patterns)
    - Effects (visual effects and particles)
    """
    
    def __init__(self, config: Optional[AssetConfig] = None):
        self.config = config or AssetConfig()
        
        # Initialize subsystems
        self.sprites = SpriteLibrary()
        self.animation_engine = AnimationEngine(fps=self.config.fps)
        self.theme_manager = ThemeManager(theme=self.config.theme)
        self.effect_manager = EffectManager()
        
        # Entity animators
        self.entity_animators: Dict[str, EntityAnimator] = {}
        
        # Performance tracking
        self.frame_count = 0
        self.last_update_time = time.time()
        
        # Load default assets
        self._load_default_assets()
    
    def _load_default_assets(self) -> None:
        """Load default sprites and animations."""
        # Register default animations
        for anim_name in ['herbivore_idle', 'herbivore_walk', 'herbivore_eat', 
                         'carnivore_idle', 'carnivore_hunt']:
            animation = AnimationLibrary.create_animation(anim_name)
            if animation:
                self.animation_engine.register_animation(anim_name, animation)
    
    # Sprite Methods
    def get_sprite(self, entity_type: str, variant: str = 'standard', **kwargs) -> str:
        """Get a sprite for an entity type."""
        if entity_type == 'herbivore':
            return self.sprites.get_herbivore_sprite(variant)
        elif entity_type == 'carnivore':
            return self.sprites.get_carnivore_sprite(variant)
        elif entity_type == 'plant':
            growth = kwargs.get('growth_stage', 1.0)
            return self.sprites.get_plant_sprite(growth)
        elif entity_type == 'terrain':
            terrain_type = kwargs.get('terrain_type', 'grass')
            return self.sprites.get_terrain_sprite(terrain_type)
        else:
            return ' '
    
    def get_status_sprite(self, status: str) -> str:
        """Get a status indicator sprite."""
        return self.sprites.get_status_sprite(status)
    
    # Animation Methods
    def register_entity_animator(self, entity_id: str) -> EntityAnimator:
        """Register an animator for an entity."""
        animator = EntityAnimator(entity_id, self.animation_engine)
        self.entity_animators[entity_id] = animator
        return animator
    
    def get_entity_animator(self, entity_id: str) -> Optional[EntityAnimator]:
        """Get animator for an entity."""
        return self.entity_animators.get(entity_id)
    
    def animate_entity(self, entity_id: str, state: str, species: str = 'herbivore') -> str:
        """Get current animation frame for an entity."""
        animator = self.entity_animators.get(entity_id)
        if not animator:
            animator = self.register_entity_animator(entity_id)
        
        animator.set_state(state, species)
        return animator.get_current_frame()
    
    def update_animations(self) -> None:
        """Update all active animations."""
        if self.config.enable_animations:
            self.animation_engine.update()
    
    # Color Methods
    def get_color(self, color_name: str, **kwargs) -> Any:
        """Get a color from the current theme."""
        return getattr(self.theme_manager.scheme, color_name.upper(), ColorScheme.UI_TEXT)
    
    def set_theme(self, theme: str) -> bool:
        """Change the color theme."""
        return self.theme_manager.set_theme(theme)
    
    def get_creature_color(self, species: str, age: float = 100, 
                          health: float = 100, energy: float = 50) -> Any:
        """Get appropriate color for a creature."""
        return get_creature_color(species, age, health, energy)
    
    def render_colored_sprite(self, sprite: str, color: Any) -> Text:
        """Render a sprite with color using Rich."""
        return Text(sprite, style=Style(color=color))
    
    # UI Methods
    def draw_box(self, width: int, height: int, style: str = 'light', 
                title: Optional[str] = None) -> List[str]:
        """Draw a box with the specified style."""
        box_style = BoxStyle[style.upper()] if style.upper() in BoxStyle.__members__ else BoxStyle.LIGHT
        return BoxDrawing.draw_box(width, height, box_style, title)
    
    def draw_separator(self, width: int, style: str = 'light') -> str:
        """Draw a horizontal separator."""
        box_style = BoxStyle[style.upper()] if style.upper() in BoxStyle.__members__ else BoxStyle.LIGHT
        return BoxDrawing.draw_separator(width, box_style)
    
    def create_menu(self, items: List[str], selected: int = 0, width: int = 25) -> List[str]:
        """Create a menu UI."""
        return UIComponents.create_menu(items, selected, width)
    
    def create_stat_panel(self, title: str, stats: Dict[str, str], width: int = 30) -> List[str]:
        """Create a statistics panel."""
        return UIComponents.create_stat_panel(title, stats, width)
    
    def create_tabs(self, tabs: List[str], active: int = 0, width: int = 80) -> str:
        """Create a tab bar."""
        return UIComponents.create_tabs(tabs, active, width)
    
    def create_command_palette(self, width: int = 80, prompt: str = "> ",
                              suggestions: Optional[List[str]] = None) -> List[str]:
        """Create a command palette."""
        return UIComponents.create_command_palette(width, prompt, suggestions)
    
    def create_dashboard_layout(self, width: int = 120, height: int = 40) -> str:
        """Create the full dashboard layout."""
        return PanelLayout.dashboard_layout(width, height)
    
    # Terrain Methods
    def get_terrain_texture(self, terrain_type: str, width: int = 10, height: int = 5) -> List[str]:
        """Get a terrain texture."""
        return TerrainTextures.render_texture(terrain_type, width, height)
    
    def render_heatmap(self, grid: List[List[float]], max_value: float = 1.0) -> List[str]:
        """Render a heatmap."""
        return render_heatmap(grid, max_value)
    
    def create_progress_bar(self, label: str, value: float, max_value: float = 100,
                           width: int = 10) -> str:
        """Create a progress bar."""
        return render_progress_bar(label, value, max_value, width)
    
    def create_sparkline(self, values: List[float], width: int = 20) -> str:
        """Create a sparkline chart."""
        return create_sparkline(values, width)
    
    # Effect Methods
    def create_effect(self, effect_type: str, position: Tuple[float, float],
                     duration: float = 1.0) -> Optional[Effect]:
        """Create a visual effect."""
        if not self.config.enable_effects:
            return None
        
        try:
            effect_enum = EffectType[effect_type.upper()]
            return self.effect_manager.create_effect(effect_enum, position, duration)
        except KeyError:
            return None
    
    def update_effects(self) -> None:
        """Update all active effects."""
        if self.config.enable_effects:
            self.effect_manager.update()
    
    def get_effects_at(self, position: Tuple[float, float], radius: float = 5.0) -> List[Effect]:
        """Get effects near a position."""
        return self.effect_manager.get_effects_at(position, radius)
    
    def clear_effects(self) -> None:
        """Clear all effects."""
        self.effect_manager.clear_effects()
    
    # Scene Methods
    def render_scene(self, scene_name: str) -> List[str]:
        """Render a predefined scene."""
        return render_scene(scene_name)
    
    def list_scenes(self) -> List[str]:
        """List available scenes."""
        return list_scenes()
    
    # Update Methods
    def update(self, dt: float = 0.1) -> None:
        """Update all animated assets."""
        current_time = time.time()
        
        if self.config.enable_animations:
            self.update_animations()
        
        if self.config.enable_effects:
            self.update_effects()
        
        self.frame_count += 1
        self.last_update_time = current_time
    
    # Utility Methods
    def get_fps(self) -> float:
        """Get current FPS."""
        return self.config.fps
    
    def get_info(self) -> Dict[str, Any]:
        """Get asset manager information."""
        return {
            'fps': self.config.fps,
            'theme': self.config.theme,
            'animations_enabled': self.config.enable_animations,
            'effects_enabled': self.config.enable_effects,
            'active_effects': self.effect_manager.count_effects(),
            'registered_animators': len(self.entity_animators),
            'frame_count': self.frame_count
        }
    
    def get_all_sprites(self) -> Dict[str, str]:
        """Get dictionary of all available sprites."""
        return self.sprites.get_all_sprites()
    
    def get_logo(self) -> List[str]:
        """Get the EMERGENCE ASCII art logo."""
        return AsciiArt.LOGO
    
    def get_mini_logo(self) -> List[str]:
        """Get the mini EMERGENCE logo."""
        return AsciiArt.MINI_LOGO


# Global asset manager instance
_global_asset_manager: Optional[ArtAssetManager] = None


def get_asset_manager() -> ArtAssetManager:
    """Get the global asset manager instance."""
    global _global_asset_manager
    if _global_asset_manager is None:
        _global_asset_manager = ArtAssetManager()
    return _global_asset_manager


def set_asset_manager(manager: ArtAssetManager) -> None:
    """Set the global asset manager instance."""
    global _global_asset_manager
    _global_asset_manager = manager


# Convenience functions
def get_sprite(entity_type: str, **kwargs) -> str:
    """Convenience function to get a sprite."""
    return get_asset_manager().get_sprite(entity_type, **kwargs)


def animate(entity_id: str, state: str, species: str = 'herbivore') -> str:
    """Convenience function to animate an entity."""
    return get_asset_manager().animate_entity(entity_id, state, species)


def create_effect(effect_type: str, position: Tuple[float, float]) -> Optional[Effect]:
    """Convenience function to create an effect."""
    return get_asset_manager().create_effect(effect_type, position)
