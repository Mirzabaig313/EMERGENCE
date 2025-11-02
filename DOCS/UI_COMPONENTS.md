# EMERGENCE UI Components Guide

Complete reference for UI building blocks in EMERGENCE, including box drawing, panels, menus, HUDs, command palettes, tabs, and pre-built layouts.

## Architecture

- **Box Drawing Module**: `emergence.ui_elements` provides Unicode box-drawing characters and builders.
- **Component Builders**: Static methods on `UIComponents` create menus, stat panels, tabs, command palettes, tooltips, and more.
- **Layout Presets**: `PanelLayout` includes split-pane, three-column, and dashboard templates.
- **Serialization**: `ui_layouts.json` defines reusable layouts for consistent UI construction.

## Box Drawing Styles

### Light Borders

```
┌────────────────┐
│   Content      │
├────────────────┤
│   More content │
└────────────────┘
```

### Heavy Borders

```
┏━━━━━━━━━━━━━━━┓
┃   Important   ┃
┣━━━━━━━━━━━━━━━┫
┃   Content     ┃
┗━━━━━━━━━━━━━━━┛
```

### Double Borders

```
╔════════════════╗
║   Special Box  ║
╠════════════════╣
║   Content      ║
╚════════════════╝
```

### Rounded Borders

```
╭────────────────╮
│   Soft Edges   │
├────────────────┤
│   Content      │
╰────────────────╯
```

## BoxDrawing API

### Draw a Box

```python
from emergence.ui_elements import BoxDrawing, BoxStyle

box = BoxDrawing.draw_box(
    width=40,
    height=10,
    style=BoxStyle.DOUBLE,
    title="STATS"
)
for line in box:
    print(line)
```

### Draw a Separator

```python
separator = BoxDrawing.draw_separator(
    width=80,
    style=BoxStyle.HEAVY,
    left_connect=True,
    right_connect=True
)
print(separator)
```

### Draw Borders

```python
top = BoxDrawing.draw_border_top(80, BoxStyle.LIGHT, title="World View")
bottom = BoxDrawing.draw_border_bottom(80, BoxStyle.LIGHT)
side = BoxDrawing.draw_border_sides(80, "Some content here")
```

## UI Components

### Menus

```python
from emergence.ui_elements import UIComponents

items = ["New Game", "Load Game", "Settings", "Quit"]
menu = UIComponents.create_menu(items, selected=0, width=30)
for line in menu:
    print(line)
```

Output:
```
┌───────────── MAIN MENU ─────────────┐
│ ▸ New Game                          │
│   Load Game                         │
│   Settings                          │
│   Quit                              │
└─────────────────────────────────────┘
```

### Progress Bars

```python
bar = UIComponents.create_progress_bar(
    label="HP",
    value=75,
    max_value=100,
    width=20,
    bar_width=10
)
print(bar)
```

Output:
```
HP: ███████░░░ 75/100
```

### Stat Panels

```python
stats = {
    "HP": "████████░░",
    "EN": "██████░░░░",
    "FIT": "847"
}
panel = UIComponents.create_stat_panel(
    title="STATS",
    stats=stats,
    width=30
)
for line in panel:
    print(line)
```

Output:
```
┏━━━━━━━ STATS ━━━━━━━┓
┃ HP: ████████░░       ┃
┃ EN: ██████░░░░       ┃
┃ FIT: 847             ┃
┗━━━━━━━━━━━━━━━━━━━━━┛
```

### Tabs

```python
tabs = ["🌍 World", "📊 Dashboard", "📈 Graphs", "🧬 Evolution", "⚙️ Settings"]
tab_bar = UIComponents.create_tabs(tabs, active=0, width=80)
print(tab_bar)
```

Output:
```
╔══[🌍 World]══ 📊 Dashboard ══ 📈 Graphs ══ 🧬 Evolution ══ ⚙️ Settings ═══╗
```

### Command Palette

```python
suggestions = ["create herbivore [name]", "create plant"]
palette = UIComponents.create_command_palette(
    width=80,
    prompt="> create her_",
    suggestions=suggestions
)
for line in palette:
    print(line)
```

Output:
```
╔══════════════════════════════════════════════════ [Ctrl+P to close] ═══╗
║ 💬 Command Palette                                                      ║
╠═════════════════════════════════════════════════════════════════════════╣
║ > create her_                                                           ║
║   ▸ create herbivore [name]   ← Press Enter                            ║
║   ▸ create plant                                                        ║
╚═════════════════════════════════════════════════════════════════════════╝
```

### HUD Panel

```python
content = [
    ("HP", "75/100"),
    ("EN", "60/100"),
    ("FIT", "847")
]
hud = UIComponents.create_hud_panel(
    title="STATS",
    content=content,
    width=30
)
for line in hud:
    print(line)
```

### Tooltip

```python
tooltip = UIComponents.create_tooltip(
    text="This is a helpful tooltip that provides context for a UI element or action.",
    width=40
)
for line in tooltip:
    print(line)
```

Output:
```
┌──────────────────────────────────────┐
│ This is a helpful tooltip that       │
│ provides context for a UI element    │
│ or action.                           │
└──────────────────────────────────────┘
```

## Layout Presets

### Split Horizontal (Left/Right)

```python
from emergence.ui_elements import PanelLayout

layout = PanelLayout.split_horizontal(
    width=120,
    height=40,
    left_width=80,
    style=BoxStyle.DOUBLE
)
for line in layout:
    print(line)
```

### Split Vertical (Top/Bottom)

```python
layout = PanelLayout.split_vertical(
    width=120,
    top_height=20,
    bottom_height=20,
    style=BoxStyle.DOUBLE
)
for line in layout:
    print(line)
```

### Three Columns

```python
layout = PanelLayout.three_column(
    width=120,
    height=40,
    col1_width=30,
    col2_width=60,
    style=BoxStyle.DOUBLE
)
for line in layout:
    print(line)
```

### Main Dashboard

The complete EMERGENCE interface layout with header, world view, status panel, message log, and command input:

```python
dashboard = PanelLayout.dashboard_layout(width=120, height=40)
print(dashboard)
```

Output:
```
╔══════════════════════════════════════════════════════════════════════════╗
║ EMERGENCE - Gen: 47 | Pop: 87 | Fit: 847 | EP: 234                      ║
╠════════════════════════════════════════╦═════════════════════════════════╣
║ 🌍 WORLD VIEW (70%)                   ║ 📊 STATUS PANEL (30%)          ║
║                                        ║                                 ║
║  [Main game area]                      ║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓   ║
║                                        ║ ┃ SELECTED: Bloom          ┃   ║
║                                        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛   ║
╠════════════════════════════════════════╩═════════════════════════════════╣
║ 📜 MESSAGE LOG                                                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║ 💬 Command: _                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝
```

## ASCII Art

### EMERGENCE Logo

```python
from emergence.ui_elements import AsciiArt

logo = AsciiArt.LOGO
for line in logo:
    print(line)
```

Output:
```
███████╗███╗   ███╗███████╗██████╗  ██████╗ ███████╗███╗   ██╗ ██████╗███████╗
██╔════╝████╗ ████║██╔════╝██╔══██╗██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔════╝
█████╗  ██╔████╔██║█████╗  ██████╔╝██║  ███╗█████╗  ██╔██╗ ██║██║     █████╗  
██╔══╝  ██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██║╚██╗██║██║     ██╔══╝  
███████╗██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝███████╗██║ ╚████║╚██████╗███████╗
╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
```

### Mini Logo

```python
mini = AsciiArt.MINI_LOGO
for line in mini:
    print(line)
```

Output:
```
╔═══════════════════════════╗
║   E M E R G E N C E      ║
║   AI Ecosystem Simulator  ║
╚═══════════════════════════╝
```

### Centering

```python
centered_text = AsciiArt.center_text("EMERGENCE", width=80)
centered_art = AsciiArt.center_art(AsciiArt.MINI_LOGO, width=80)
```

## Asset Manager Integration

Use the `ArtAssetManager` to access UI components:

```python
from emergence.art_assets import get_asset_manager

assets = get_asset_manager()

# Draw box
box = assets.draw_box(width=40, height=10, style="double", title="STATS")

# Create menu
menu = assets.create_menu(["New Game", "Load", "Quit"], selected=0, width=30)

# Create stat panel
stats = {"HP": "80", "EN": "65", "FIT": "847"}
panel = assets.create_stat_panel("STATS", stats, width=30)

# Create tabs
tabs = assets.create_tabs(["World", "Dashboard", "Graphs"], active=0, width=80)

# Create command palette
palette = assets.create_command_palette(
    width=80,
    prompt="> ",
    suggestions=["create herbivore", "simulate 100"]
)

# Create full dashboard
dashboard = assets.create_dashboard_layout(width=120, height=40)

# Get logo
logo = assets.get_logo()
mini_logo = assets.get_mini_logo()
```

## Textual Integration

UI components integrate seamlessly with Textual widgets:

```python
from textual.app import App, ComposeResult
from textual.widgets import Static
from emergence.art_assets import get_asset_manager

class DashboardWidget(Static):
    def __init__(self) -> None:
        super().__init__()
        self.assets = get_asset_manager()

    def compose(self) -> ComposeResult:
        dashboard = self.assets.create_dashboard_layout(120, 40)
        yield Static(dashboard)

class EmergenceApp(App):
    def compose(self) -> ComposeResult:
        yield DashboardWidget()
```

## Best Practices

1. **Consistent Widths**: Keep panel widths consistent with terminal size constraints
2. **Title Length**: Titles should fit within box width minus 4 characters for padding
3. **Nesting**: Use separators to divide content within boxes rather than nesting boxes
4. **Color**: Apply colors via Rich `Text` objects rather than modifying raw strings
5. **Responsiveness**: Test UI at multiple terminal sizes (80, 100, 120, 140 columns)

## Terminal Compatibility

- **Unicode Box Drawing**: Supported by all modern terminals
- **Emoji in Headers**: Optional, gracefully degrades to text
- **Width**: Minimum 80 columns recommended; 120+ optimal
- **Height**: Minimum 24 rows recommended; 40+ optimal for full dashboard

## Testing

Test UI components with:

```bash
pytest tests/test_ui_components.py
```

Or manually inspect output:

```python
from emergence.ui_elements import UIComponents

menu = UIComponents.create_menu(["Item 1", "Item 2", "Item 3"])
for line in menu:
    print(line)
```

## See Also

- [ASSETS_README.md](ASSETS_README.md)
- [SPRITE_GUIDE.md](SPRITE_GUIDE.md)
- [ANIMATION_GUIDE.md](ANIMATION_GUIDE.md)
- [COLOR_SCHEME.md](COLOR_SCHEME.md)
