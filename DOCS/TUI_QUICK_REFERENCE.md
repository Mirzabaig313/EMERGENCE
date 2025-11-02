# EMERGENCE TUI - Quick Reference Card

## 🚀 Getting Started
```bash
python -m emergence          # Launch TUI
python -m emergence --cli    # Launch classic CLI
```

Press **ENTER** on title screen to begin.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+P` | Play/Pause simulation |
| `Ctrl+F` | Fast forward (2x speed) |
| `Ctrl+S` | Quick save to autosave.json |
| `Ctrl+D` | Switch to dashboard view |
| `Ctrl+Q` | Quit application |
| `Tab` | Autocomplete current command |
| `↑` / `↓` | Navigate command history |
| `Esc` | Clear command input |

---

## 📝 Essential Commands

### Create & Observe
```bash
create herbivore Alice        # Spawn a creature
create plant                  # Spawn a plant (random name)
observe Alice                 # View creature stats
population                    # List all entities
stats                         # Ecosystem overview
```

### Control Simulation
```bash
play                          # Start async simulation
pause                         # Stop simulation
simulate 100                  # Run 100 ticks headless
speed 2.5                     # Set speed multiplier
auto_mode on                  # Enable auto resource spawn
```

### Train Creatures
```bash
reward Alice 10               # Reinforce learning
punish Alice 5                # Discourage behavior
teach Alice 3                 # Guide learning
feed Alice                    # Add +30 energy
heal Alice                    # Add +40 health
breed Alice Bob               # Create offspring
```

---

## 📊 Visualization Commands

### Graphs (output to console)
```bash
graph population              # Population over time
graph fitness                 # Fitness trends
graph age                     # Age distribution
graph energy                  # Energy distribution
```

### Heatmaps (output to console)
```bash
heatmap births                # Birth locations
heatmap deaths                # Death locations
heatmap food                  # Food consumption
```

### Analysis Tools
```bash
dashboard                     # Main statistics panel
timeline                      # Evolution timeline
show_brain Alice              # Neural network details
family_tree Alice 8           # Ancestry (8 generations)
learning_curve Alice          # Learning progress
compare_species               # Species comparison
top 10                        # Top 10 performers
events 20                     # Recent 20 events
```

---

## 💾 Save & Load

```bash
save my_world.json            # Save current state
load my_world.json            # Restore saved state
snapshot baseline             # Create named snapshot
snapshot list                 # View all snapshots
snapshot compare old new      # Compare snapshots
export_stats data.csv         # Export to CSV
export_stats data.json        # Export to JSON
```

---

## 🎮 Gameplay Modes

### Start a Mode
```bash
start_mode survival           # Keep alive 100 generations
start_mode sandbox            # Creative mode, no limits
start_mode speedrun           # Race to Gen 100
start_mode challenge drought  # Drought challenge
```

### Challenges Available
- `drought` - 90% reduced plant growth
- `invasion` - Survive 20 predator spawns
- `ice_age` - Slower reproduction, higher costs
- `extinction` - Recover from 90% population wipe

### Progression
```bash
gameplay                      # Show current status
achievements                  # View achievement progress
unlock carnivores             # Spend Evolution Points
```

### Available Unlocks
```
carnivores, apex, scavengers, omnivores, camouflage
mutation, teaching, divine, weather, timewarp
drought, ice_age, invasion, extinction
```

---

## 🎯 Common Workflows

### Beginner: Basic Simulation
```bash
create herbivore Alice
create herbivore Bob
simulate 100
stats
```

### Intermediate: Training & Breeding
```bash
create herbivore Alice
reward Alice 10
feed Alice
create herbivore Bob
breed Alice Bob
observe herbivore_3
```

### Advanced: Analysis & Optimization
```bash
snapshot before
simulate 500
snapshot after
snapshot compare before after
graph fitness
show_brain Alice
family_tree Alice 6
top 10
```

### Expert: Gameplay Mode
```bash
start_mode survival
gameplay
simulate 100
unlock carnivores
achievements
save survival_run.json
```

---

## 💡 Pro Tips

1. **Use Tab** for autocomplete - just type `cre<Tab>` → `create`
2. **Fuzzy matching** forgives typos - `obsrv` works for `observe`
3. **Console output** - Complex visualizations print to console for detail
4. **Background simulation** - Use Ctrl+P to run while you explore
5. **Quick iterations** - `simulate 100` → analyze → repeat
6. **Snapshots** - Take frequent snapshots to compare experiments
7. **Auto mode** - Enable during long simulations to prevent starvation
8. **Speed control** - Slow to 0.5x for observation, fast to 10x for evolution

---

## 🆘 Getting Help

```bash
help                          # Show all commands
```

Or consult the full documentation:
- [TUI_CLI_PARITY.md](TUI_CLI_PARITY.md) - Complete command reference
- [GAMEPLAY_GUIDE.md](GAMEPLAY_GUIDE.md) - Game modes and mechanics
- [README.md](README.md) - Main documentation

---

## 🐛 Troubleshooting

**Command not working?**
- Check spelling (or use Tab autocomplete)
- Try `help` to see syntax
- Fuzzy matching will suggest corrections

**Simulation too fast/slow?**
- Use `speed [0.1-10.0]` to adjust
- Or Ctrl+F to double current speed

**Want CLI instead?**
```bash
python -m emergence --cli
```

---

**Version:** TUI with full CLI parity
**Status:** ✅ All 39 commands implemented
**Last Updated:** 2025-11-02
