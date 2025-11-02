# EMERGENCE Interactive TUI Guide

## 🎮 Welcome to the Interactive TUI!

EMERGENCE has been transformed into a stunning, interactive Terminal User Interface (TUI) that pushes the boundaries of what's possible in a terminal. This guide will help you get the most out of the new interface.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install the package
pip install -e .
```

### Launch the TUI

```bash
# New interactive TUI (default)
python -m emergence

# Or use the command after installation
emergence

# Legacy CLI (if needed)
python -m emergence --cli
# or
emergence-cli
```

## ✨ Key Features

### 1. Beautiful Title Screen

When you launch EMERGENCE, you'll be greeted with stunning ASCII art:

```
╔══════════════════════════════════════════════════════════════╗
║     ███████╗███╗   ███╗███████╗██████╗  ██████╗ ███████╗   ║
║     ██╔════╝████╗ ████║██╔════╝██╔══██╗██╔════╝ ██╔════╝   ║
║     █████╗  ██╔████╔██║█████╗  ██████╔╝██║  ███╗█████╗     ║
║     ██╔══╝  ██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║██╔══╝     ║
║     ███████╗██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝███████╗   ║
║                  🧬 An AI Life Simulation Experience 🧬       ║
╚══════════════════════════════════════════════════════════════╝
```

Press **ENTER** to start, **Q** to quit.

### 2. Split-Pane Layout

The main game screen features a split-pane layout:

```
┌────────────────────────────────┬─────────────────────────┐
│  🌍 World View (Interactive)   │  📊 Live Stats          │
│                                │                         │
│  🐰🌱🌲🌾🐇🌱🌾                │  Generation: 12         │
│  🌱🐰🌾🌲🌱🐇🌾                │  Population: 67         │
│  🌾🌱🌲🌲🐰🌱🌾                │  🐰 Herbivores: 42     │
│  🌲🌲🌱🐰🌾🌱🌾                │  🌱 Plants: 234        │
│                                │                         │
│  [Live updating every frame]   │  📈 Live Graph          │
│                                │  ▁▂▃▄▅▆▇█              │
├────────────────────────────────┴─────────────────────────┤
│  [▶️ Play] [⏸️ Pause] [⏩ Fast] [📊 Dashboard] [⚙️ Settings]│
├──────────────────────────────────────────────────────────┤
│  📋 Command Palette                                      │
│  > create herbivore Bloom                                │
│  Suggestions: create • observe • simulate • feed         │
└──────────────────────────────────────────────────────────┘
```

### 3. Interactive World View

The world view shows your ecosystem in real-time with beautiful emoji:

- 🐰 **Healthy Herbivore** (70%+ energy)
- 🐇 **Medium Herbivore** (40-70% energy)
- 🐁 **Low Energy Herbivore** (<40% energy)
- 🌲 **Mature Plant** (fully grown)
- 🌱 **Growing Plant**
- 🌾 **Grass/Seedling**

The view updates automatically when simulation is running!

### 4. Command Palette with Autocomplete

Type commands at the bottom of the screen:

#### Autocomplete Features

- **Tab Completion**: Press `Tab` to autocomplete commands
- **Fuzzy Matching**: Typos are forgiven! `crete` → suggests `create`
- **Command History**: Use `↑` and `↓` to navigate previous commands
- **Suggestions**: See available commands as you type

#### Example Commands

```bash
# Create entities
> create herbivore Bloom
> create plant

# Observe creatures
> observe Bloom

# Simulation control
> simulate 100
> play
> pause

# Help creatures
> feed Bloom
> heal Bloom

# Information
> stats
> population

# Save/Load
> save my_world.json
> load my_world.json
```

### 5. Keyboard Shortcuts

Master these shortcuts for maximum efficiency:

| Shortcut | Action |
|----------|--------|
| `Ctrl+P` | Play/Pause simulation |
| `Ctrl+F` | Fast forward (increase speed) |
| `Ctrl+D` | Switch to Dashboard view |
| `Ctrl+S` | Save game |
| `Ctrl+Q` | Quit application |
| `Tab` | Autocomplete command |
| `Esc` | Clear command input |
| `↑/↓` | Navigate command history |
| `Enter` | Execute command |

### 6. Tabbed Interface

Switch between different views using tabs:

1. **🌍 World** - Live animated world view
2. **📊 Dashboard** - Comprehensive statistics
3. **📈 Graphs** - Population and fitness over time
4. **🧬 Evolution** - Family trees and lineages
5. **⚙️ Settings** - Configure simulation parameters

### 7. Live Statistics Panel

The stats panel shows real-time information:

```
📊 Live Stats
━━━━━━━━━━━━━━━━━━━━━
Generation:        47
Total Population:  67

┏━━━━━━━━━━━━━━━━━━━┓
┃ 🐰 Herbivores:  42 ┃
┃ 🌱 Plants:     234 ┃
┗━━━━━━━━━━━━━━━━━━━┛

📈 Fitness Trend:
  Avg:  847.2
  Best: 1234.5

⚡ Avg Energy: ████████░░ 80%

🌸 Total Births: 156
💀 Total Deaths: 89
🍃 Plants Eaten: 523
```

### 8. Real-Time Graphs

Live population graphs update automatically:

```
📈 Population Graph
━━━━━━━━━━━━━━━━━━━━━

Population Over Time

🐰 Herbivores: ▁▂▃▄▅▆▇█▇▆▅▄▃▄▅▆▇█ (42)
🌱 Plants:     ▃▄▅▆▆▅▄▃▄▅▆▇█▇▆▅▄▃ (234)

[Updates every tick automatically]
```

### 9. Fuzzy Command Matching

The TUI forgives typos and suggests corrections:

```
> crete herbivore Bloom
Did you mean: create? Running it anyway...
✅ Spawned herbivore Bloom
```

```
> obsrv Bloom
Did you mean: observe? Running it anyway...
🐰 Bloom
Energy: 75.3
Health: 100.0
...
```

### 10. Notifications

Get instant feedback with beautiful notifications:

```
┌──────────────────────────────┐
│ ✅ Success                    │
│                              │
│ Spawned herbivore Bloom!     │
└──────────────────────────────┘
```

```
┌──────────────────────────────┐
│ 🔔 Event Notification        │
│                              │
│ Generation 10 reached!       │
│ New species abilities        │
│ unlocked.                    │
└──────────────────────────────┘
```

## 📋 Complete Command Reference

### Creation Commands

```bash
create herbivore [name]  # Spawn a herbivore
create plant [name]      # Spawn a plant
```

### Observation Commands

```bash
observe [name]           # View creature details
stats                    # Show ecosystem stats
population               # List all creatures
show_brain [name]        # Neural network details
show_lineage [name]      # Family tree
```

### Simulation Commands

```bash
simulate [ticks]         # Run N simulation ticks
play                     # Start auto-simulation
pause                    # Stop auto-simulation
speed [multiplier]       # Set simulation speed
```

### Interaction Commands

```bash
feed [name]              # Give energy to creature
heal [name]              # Restore health
reward [name] [amount]   # Positive reinforcement
punish [name] [amount]   # Negative reinforcement
teach [name] [strength]  # Guide learning
breed [name1] [name2]    # Force reproduction
```

### Visualization Commands

```bash
dashboard                # Main dashboard
graph [type]             # Show graphs (population, fitness, etc.)
heatmap [type]           # Spatial heatmaps (births, deaths, food)
timeline                 # Evolution timeline
```

### Data Management

```bash
save [filename]          # Save world state
load [filename]          # Load world state
snapshot [name]          # Create comparison snapshot
export_stats [filename]  # Export data (JSON/CSV)
```

### Help & Settings

```bash
help                     # Show command reference
quit / exit              # Exit simulator
```

## 🎯 Tips & Tricks

### 1. Auto-Simulation Mode

Press `Ctrl+P` to start auto-simulation:
- World updates in real-time
- All stats refresh automatically
- Watch evolution happen live!

Press `Ctrl+P` again to pause.

### 2. Speed Control

Use `Ctrl+F` repeatedly to increase simulation speed:
- 1x (normal) → 2x → 4x → 8x → 10x

### 3. Command History

Don't retype commands! Use:
- `↑` to go back through history
- `↓` to go forward
- Just like a real shell!

### 4. Tab Completion

Start typing and press `Tab`:
```bash
> cre[Tab] → create
> create her[Tab] → create herbivore
```

### 5. Fuzzy Search

Don't worry about exact spelling:
- `simulate` = `simulte` = `simualte`
- `observe` = `obsrve` = `obserb`
- System will figure it out!

### 6. Quick Stats

Want quick info without opening menus?
```bash
> stats        # Quick overview
> population   # See all creatures
```

### 7. Experiment Safely

Create a snapshot before experiments:
```bash
> snapshot before_experiment
> [do risky things]
> load before_experiment  # if needed
```

## 🎨 Customization

### Settings Panel

Access via **⚙️ Settings** tab or `Ctrl+Shift+S`:

- **Animation Speed**: Control how fast the simulation runs
- **Particle Effects**: Toggle visual effects (future)
- **Auto-save**: Configure automatic saving
- **Starting Population**: Set initial creature count

## 🐛 Troubleshooting

### Terminal Too Small

If the TUI looks cramped:
1. Maximize your terminal window
2. Recommended: at least 120x30 characters
3. Use a modern terminal (iTerm2, Windows Terminal, etc.)

### Emojis Not Showing

If you see `?` or boxes instead of emojis:
1. Use a modern terminal with Unicode support
2. Install a font with emoji support (Noto Color Emoji, etc.)
3. Update your terminal emulator

### Performance Issues

If simulation is slow:
1. Reduce population (`create` fewer creatures)
2. Decrease speed multiplier
3. Use `simulate [ticks]` for batch processing instead of live mode

## 🔮 Future Features

Coming soon to the TUI:

- 🖱️ **Full Mouse Support** - Click creatures, drag to pan
- 🎮 **Game Modes** - Survival, Challenge, Sandbox modes
- 🏆 **Achievements** - Track your progress
- 📊 **Advanced Graphs** - More visualization types
- 🎨 **Themes** - Customize colors and appearance
- 🔊 **Sound Effects** - Terminal beeps for events
- 📹 **Recording** - Save simulation replays

## 📚 Learn More

- `README.md` - Project overview
- `DOCUMENTATION.md` - Technical documentation
- `GAMEPLAY_GUIDE.md` - Gameplay mechanics
- `examples/` - Example scripts

## 🎉 Enjoy!

You're now ready to experience EMERGENCE in all its interactive glory! 

Start creating your ecosystem and watch evolution unfold before your eyes.

**Remember**: This is still a terminal, but we're pushing the boundaries of what's possible! 🚀

---

*Made with ❤️ using Python, Rich, and Textual*
