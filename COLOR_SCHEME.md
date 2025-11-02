# EMERGENCE Color Scheme Reference

This guide documents the ANSI color palettes used by EMERGENCE. Colors are defined using `rich.color.Color.from_rgb` for cross-platform compatibility and managed through `ThemeManager` in `emergence.colors`.

## Color Architecture

- **ColorScheme**: Base class containing RGB values for creatures, plants, terrain, UI, graphs, and message log entries.
- **ThemeManager**: Handles theme selection and switching. Serialized themes are stored in `emergence/assets/themes.json`.
- **Usage**: Colors can be accessed via `ColorScheme` attributes or helper functions like `get_creature_color()`.

## Core Colors

### Herbivores

| Name | RGB | Description |
|------|-----|-------------|
| `HERBIVORE_HEALTHY` | (0, 255, 0) | Bright green for healthy herbivores |
| `HERBIVORE_HUNGRY` | (200, 200, 0) | Yellow for hungry herbivores |
| `HERBIVORE_BABY` | (150, 255, 150) | Light green for juvenile herbivores |
| `HERBIVORE_ELDERLY` | (100, 150, 100) | Muted green for elderly herbivores |

### Carnivores

| Name | RGB | Description |
|------|-----|-------------|
| `CARNIVORE_NORMAL` | (255, 69, 0) | Red-orange for active predators |
| `CARNIVORE_HUNTING` | (255, 0, 0) | Bright red when chasing |
| `CARNIVORE_APEX` | (139, 0, 0) | Dark red for apex predators |
| `CARNIVORE_BABY` | (255, 150, 150) | Light red for juvenile carnivores |

### Special Creatures

| Name | RGB | Description |
|------|-----|-------------|
| `SCAVENGER` | (128, 128, 128) | Neutral gray |
| `OMNIVORE` | (139, 69, 19) | Earthy brown |
| `CAMOUFLAGE` | (100, 100, 60) | Olive green |
| `MYTHICAL` | (138, 43, 226) | Purple |
| `MYTHICAL_DRAGON` | (255, 0, 255) | Vivid magenta |
| `MYTHICAL_UNICORN` | (255, 192, 203) | Pastel pink |

### Plants

| Name | RGB | Description |
|------|-----|-------------|
| `PLANT_YOUNG` | (50, 205, 50) | Lime green |
| `PLANT_MATURE` | (34, 139, 34) | Forest green |
| `PLANT_DYING` | (139, 69, 19) | Brown |
| `PLANT_SEED` | (160, 82, 45) | Sienna |

### Terrain

| Name | RGB | Description |
|------|-----|-------------|
| `WATER` | (0, 191, 255) | Deep sky blue |
| `WATER_DEEP` | (0, 105, 148) | Dark blue |
| `DESERT` | (255, 215, 0) | Gold/sand |
| `FOREST` | (34, 139, 34) | Forest green |
| `MOUNTAIN` | (169, 169, 169) | Gray |
| `MOUNTAIN_PEAK` | (255, 255, 255) | Snowy peak |
| `PLAINS` | (154, 205, 50) | Yellow-green |
| `ICE` | (175, 238, 238) | Pale turquoise |
| `FIRE` | (255, 69, 0) | Fiery red |

### UI Colors

| Name | RGB | Description |
|------|-----|-------------|
| `UI_BORDER` | (0, 255, 255) | Neon cyan border |
| `UI_HEADER` | (0, 191, 255) | Header text |
| `UI_TEXT` | (255, 255, 255) | Primary text |
| `UI_DIM` | (128, 128, 128) | Muted text |
| `UI_HIGHLIGHT` | (255, 255, 0) | Highlight color |
| `UI_SUCCESS` | (0, 255, 0) | Success state |
| `UI_ERROR` | (255, 0, 0) | Error state |
| `UI_WARNING` | (255, 165, 0) | Warning state |
| `UI_INFO` | (0, 191, 255) | Informational element |

### Graph Colors

| Name | RGB | Description |
|------|-----|-------------|
| `GRAPH_LINE1` | (0, 255, 127) | Spring green line |
| `GRAPH_LINE2` | (255, 20, 147) | Deep pink line |
| `GRAPH_LINE3` | (255, 215, 0) | Gold line |
| `GRAPH_LINE4` | (138, 43, 226) | Blue violet line |
| `GRAPH_LINE5` | (0, 255, 255) | Cyan line |
| `GRAPH_GRID` | (64, 64, 64) | Grid lines |
| `GRAPH_AXIS` | (128, 128, 128) | Axis lines |

### Message Log

| Name | RGB | Description |
|------|-----|-------------|
| `MSG_NORMAL` | (200, 200, 200) | Neutral |
| `MSG_BIRTH` | (0, 255, 0) | Birth event |
| `MSG_DEATH` | (255, 0, 0) | Death event |
| `MSG_EVOLUTION` | (138, 43, 226) | Evolution |
| `MSG_ACHIEVEMENT` | (255, 215, 0) | Achievement |
| `MSG_WARNING` | (255, 165, 0) | Warning |
| `MSG_INFO` | (0, 191, 255) | Info |
| `MSG_DEBUG` | (128, 128, 128) | Debug |

## Themes

Themes are defined in `themes.json`. Each theme includes a subset of the full palette to simplify overrides. Example entry:

```json
{
  "id": "default",
  "name": "Neon Terminal",
  "description": "Bright neon colors on dark background",
  "colors": {
    "herbivore_healthy": [0, 255, 0],
    "carnivore_normal": [255, 69, 0],
    "ui_border": [0, 255, 255]
  }
}
```

### Available Themes

1. **default** – Neon Terminal (full color spectrum)
2. **dark** – Muted low-light palette
3. **light** – High-contrast light mode
4. **retro** – Green phosphor terminal homage
5. **cyberpunk** – Cyan/pink neon pairing

## Helper Functions

### Creature Colors

```python
from emergence.colors import get_creature_color

color = get_creature_color(
    species="herbivore",
    age=50,
    health=80,
    energy=90
)
```

### Plant Colors

```python
from emergence.colors import get_plant_color

color = get_plant_color(age=20, health=70)
```

### Terrain Colors

```python
from emergence.colors import get_terrain_color

water_color = get_terrain_color("water")
desert_color = get_terrain_color("desert")
```

### Message Colors

```python
from emergence.colors import get_message_color

warning_style = get_message_color("warning")
info_style = get_message_color("info")
```

## Theme Manager Usage

```python
from emergence.colors import ThemeManager

theme_manager = ThemeManager(theme="default")
current_scheme = theme_manager.scheme

# Switch themes at runtime
if theme_manager.set_theme("cyberpunk"):
    scheme = theme_manager.scheme
```

## Rendering with Rich

```python
from rich.console import Console
from rich.text import Text
from emergence.art_assets import get_asset_manager

console = Console()
assets = get_asset_manager()
sprite = assets.get_sprite("herbivore")
color = assets.get_creature_color("herbivore", age=100, health=90, energy=70)
text = Text(sprite, style=color)
console.print(text)
```

## Accessibility Considerations

- Ensure color contrast is sufficient for readability, especially in light mode
- Consider colorblind-friendly schemes (e.g., replace red/green conflicts)
- Provide descriptive overlays or text to complement color cues
- Allow users to switch themes via configuration or command palette

## Extending Colors

1. Add new colors to `ColorScheme`
2. Update `ThemeManager.THEMES` and `themes.json`
3. Document new entries in this guide if widely used
4. Ensure UI components reference new color keys as needed

## See Also

- [ASSETS_README.md](ASSETS_README.md)
- [SPRITE_GUIDE.md](SPRITE_GUIDE.md)
- [ANIMATION_GUIDE.md](ANIMATION_GUIDE.md)
- [UI_COMPONENTS.md](UI_COMPONENTS.md)
