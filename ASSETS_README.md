# EMERGENCE Terminal Art Asset System

This document describes the terminal art asset system for EMERGENCE. It outlines the architecture, file layout, asset categories, rendering requirements, and integration points with the simulator.

## Overview

EMERGENCE uses a hybrid visual language that blends retro terminal aesthetics with modern emoji expressiveness and ANSI color highlights. The art system is optimized for a 500×500 world simulation rendered in both CLI and full-screen Textual TUI modes. Assets are designed for 10 FPS real-time animation and high readability at 120+ character terminal width.

### Goals

- Professional-grade presentation using emoji characters, Unicode box-drawing glyphs, and ANSI color blocks
- Smooth animation at 10 FPS with support for 100+ concurrent animated sprites
- Futuristic HUD design with neon accents and intuitive overlays
- Consistent rendering across macOS, Linux, and Windows terminals
- Ready-to-use assets for Textual and Rich rendering pipelines

## File Layout

```
emergence/
  art_assets.py        # Asset manager
  sprites.py           # Sprite definitions and helpers
  animations.py        # Animation library and engine
  colors.py            # Color schemes and theme manager
  terrain.py           # Terrain textures and scenes
  effects.py           # Visual effect sequences
  ui_elements.py       # Box drawing and UI components
  assets/
    sprites.json       # Serialized sprite catalog
    animations.json    # Serialized animation sequences
    themes.json        # Serialized color themes
    ui_layouts.json    # Serialized UI layout definitions
```

Documentation:
```
ASSETS_README.md
SPRITE_GUIDE.md
ANIMATION_GUIDE.md
COLOR_SCHEME.md
UI_COMPONENTS.md
```

## Asset Categories

1. **Sprites** – Emoji and Unicode characters representing creatures, plants, terrain, overlays, and action effects. Accessible through `emergence.sprites` or `sprites.json`.
2. **Animations** – Frame-based sequences for herbivores, carnivores, plants, and particle effects. Managed by `AnimationEngine` in `emergence.animations` and defined in `animations.json`.
3. **Colors** – ANSI-safe color palettes defined with `rich.color.Color`. Multiple themes are available via `ThemeManager` and described in `COLOR_SCHEME.md`.
4. **UI Elements** – Modular components including box borders, menu panels, HUDs, command palette, tab bar, and dashboard layouts. Implemented in `ui_elements.py` and serialized in `ui_layouts.json`.
5. **Terrain & Scenes** – Textures, heatmaps, progress bars, and cinematic scenes (campfire, village, dashboard, population graph, animation reference). Implemented in `terrain.py`.
6. **Effects** – Particle-style visuals for births, deaths, attacks, evolutions, heals, etc. Managed by `EffectManager` in `effects.py`.

## ArtAssetManager

`ArtAssetManager` (in `art_assets.py`) provides unified access to all resources:

```python
from emergence.art_assets import get_asset_manager

assets = get_asset_manager()
frame = assets.animate_entity("bloom", state="walk", species="herbivore")
color = assets.get_creature_color("herbivore", age=50, health=90, energy=70)
scene = assets.render_scene("campfire")
menu = assets.create_menu(["New Game", "Settings", "Quit"], selected=0)
```

Key responsibilities:

- Manage sprite and animation retrieval
- Coordinate color schemes and theme switching
- Provide UI builders for menus, dashboards, HUD overlays, and command palette
- Render terrain textures, heatmaps, and progress bars
- Spawn and update visual effects with negligible overhead
- Supply ASCII art logos and cinematic scenes

## Performance Considerations

- `AnimationEngine` runs at configurable FPS (default 10) with frame caching to support 100+ animated entities.
- `EffectManager` caps active effects to maintain responsiveness and avoid terminal saturation.
- All rendering helpers produce pure strings for compatibility with Rich and Textual; color styling is applied via `rich.text.Text` when required.

## Integration with Textual

- Use `Textual` widgets to render strings from `ArtAssetManager` using `Rich` renderables.
- For colored sprites, wrap characters with `rich.text.Text` and apply styles using `ColorScheme`.
- UI layouts from `ui_layouts.json` map cleanly onto `Textual` layout containers (grid, vertical/horizontal splits).
- Animations are ticked inside Textual's update loop through `AnimationEngine.tick()` or `Animator` instances.

## Cross-Platform Rendering Tips

- Ensure the terminal uses a font with good emoji coverage (Apple Color Emoji, Noto Color Emoji, Segoe UI Emoji).
- On Windows, enable ANSI support using Rich's built-in detection or `colorama` init (Rich handles this automatically).
- Keep line width at ≥ 120 characters for full dashboard visibility. UI components gracefully degrade for narrower widths via string truncation.

## Testing

A dedicated test suite in `tests/test_art_assets.py` ensures:

- Sprites and animations load without errors
- Heatmap and progress bar rendering stays within expected dimensions
- UI components produce consistent borders and lengths
- Scene registry includes all required cinematic assets

Run tests with:

```bash
pytest
```

(Or use `python -m pytest` if pytest is installed.)

## Extending the Asset System

- Add new sprite definitions in `sprites.py` and `sprites.json` for serialization.
- Define new animation sequences in `animations.py` and `animations.json`.
- Create additional themes in `COLOR_SCHEME.md` and register them in `themes.json`.
- Extend UI layouts via `ui_elements.py` and `ui_layouts.json` for custom screens.
- Register new scenes in `terrain.py` and update documentation accordingly.

For further usage details, see the companion guides:

- [SPRITE_GUIDE.md](SPRITE_GUIDE.md)
- [ANIMATION_GUIDE.md](ANIMATION_GUIDE.md)
- [COLOR_SCHEME.md](COLOR_SCHEME.md)
- [UI_COMPONENTS.md](UI_COMPONENTS.md)
