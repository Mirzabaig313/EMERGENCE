# EMERGENCE – AI Ecosystem Simulator

EMERGENCE is a richly interactive, terminal-native artificial life simulation where digital creatures learn to survive in a lush 2D world. Each creature is powered by a neural network brain that learns during its lifetime via reinforcement learning and evolves across generations through a genetic algorithm. The result is an emergent ecosystem of plants and herbivores that grow, eat, learn, and reproduce in a colourful, emoji-powered world view.

The latest release upgrades EMERGENCE from a traditional CLI to a full-screen Textual-powered TUI complete with real-time animation, split panes, command palette, fuzzy autocomplete, mouse-ready widgets, and keyboard shortcuts — while keeping the original CLI available for power users.

## Features

- **Continuous 500×500 World** – Creatures roam a floating-point plane with realistic velocity, energy usage, and terrain constraints.
- **Neural Network Brains** – Each herbivore owns a fully differentiable feed-forward network (5 inputs → 8 hidden → 3 outputs) with tanh/linear activations.
- **Reinforcement Learning** – Creatures learn from their own experience using temporal-difference updates and an exploration vs. exploitation policy.
- **Genetic Algorithm Evolution** – Successful herbivores pass on their brains through crossover and mutation. Physical traits mutate too, nudging lineages toward efficiency.
- **Emergent Ecosystem** – Plants sprout, grow, and get consumed. Herbivores explore, graze, recover, and reproduce. Population dynamics emerge naturally.
- **Interactive TUI (New!)** – Full-screen Textual interface with tabs, command palette, fuzzy autocomplete, real-time animation, emoji creatures (🐰🌱), keyboard shortcuts, and live graphs.
- **Legacy CLI** – The original Rich-powered text interface remains available for scripting and advanced control.
- **Gameplay Modes & Progression** – Survival, challenge, sandbox, and speedrun modes with Evolution Points, unlocks, achievements, and random events.
- **Statistics & Analytics Suite** – Real-time dashboard, population graphs, heatmaps, lineage explorer, neural analysis, learning curves, and exports.
- **Beautiful Visualisation** – A live viewport renders the world with colour-coded agents, plus sidebar statistics and lineage tools.
- **Persistence** – The entire world state—including neural networks and evolutionary data—can be saved and restored.

## Getting Started

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch the Interactive TUI

```bash
python -m emergence
```

Or install as a package and use the console script:

```bash
pip install .
emergence
```

### 3. Prefer the Legacy CLI?

```bash
python -m emergence --cli
# or after installation
emergence-cli
```

## Tutorial: First Steps

1. **Launch the TUI**
   ```
   python -m emergence
   ```
   Press **ENTER** on the title screen to enter the split-pane interface.

2. **Create your first creature**
   - Move to the command palette at the bottom (it has focus by default).
   - Type `create herbivore Bloom` — use `Tab` for autocomplete.
   - Press **Enter** and watch the 🐰 appear in the world view.

3. **Let the world evolve**
   - Press `Ctrl+P` to start/stop the real-time simulation.
   - Watch plants 🌱 regrow and herbivores explore as stats update live.
   - Use `simulate 200` for a quick headless burst if you prefer.

4. **Inspect statistics**
   - The right pane shows generation, population, fitness, and energy bars.
   - Switch to the **📈 Graphs** tab for sparkline history.
   - Use the commands `stats` or `population` for textual summaries.

5. **Help or study a creature**
   - `feed Bloom` / `heal Bloom` to intervene.
   - `observe Bloom` for a Rich stats panel.
   - `show_brain Bloom` to inspect the neural network architecture.

6. **Save your world**
   - `save my_world.json` persists the simulation.
   - Load later with `load my_world.json`.

Prefer scripting? Launch with `python -m emergence --cli` for the original command-line workflow.

## Command Reference

### Core Commands
| Command | Description |
| --- | --- |
| `create [species] [name]` | Spawn a new plant or herbivore |
| `observe [name]` | Inspect creature state and statistics |
| `reward/punish [name] [amount]` | Reinforce or discourage recent actions |
| `teach [name] [strength]` | Provide a guidance boost |
| `feed/heal [name]` | Directly restore energy or health |
| `breed [name1] [name2]` | Genetically cross two herbivores |
| `simulate [ticks]` | Run the world without visualisation |
| `view [ticks]` | Live Rich visualisation of the ecosystem |
| `population` | List every living entity |

### Visualization & Analytics Commands
| Command | Description |
| --- | --- |
| `dashboard` | Show comprehensive statistics dashboard |
| `graph [type]` | Display graphs: population, fitness, age, energy |
| `heatmap [type]` | Show spatial heatmaps: births, deaths, food |
| `timeline` | Display evolution timeline across generations |
| `learning_curve [name]` | Show individual creature's learning progress |
| `compare_species` | Compare species statistics in table form |
| `events [count] [type]` | Show recent simulation events |
| `top [count]` | Display top performing creatures |
| `show_brain [name]` | Print detailed neural network analysis |
| `family_tree [name] [depth]` | Reveal detailed ancestry and lineage |

### Data Management Commands
| Command | Description |
| --- | --- |
| `save [file]` | Save world state to file |
| `load [file]` | Load world state from file |
| `snapshot [name]` | Create a named snapshot for comparison |
| `export_stats [file]` | Export statistics to JSON or CSV |

### Settings & Keyboard Shortcuts

#### TUI Keyboard Shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+P` | Play/Pause real-time simulation |
| `Ctrl+F` | Fast-forward (increase speed multiplier) |
| `Ctrl+S` | Quick save to autosave file |
| `Ctrl+Q` | Quit the application |
| `Tab` | Autocomplete commands |
| `↑ / ↓` | Navigate command history |
| `Esc` | Clear command input |

#### CLI Settings Commands

| Command | Description |
| --- | --- |
| `speed [multiplier]` | Adjust `view` refresh speed |
| `follow [name]` | Center the camera on a creature |
| `auto_mode on/off` | Toggle faster plant growth |
| `quit` | Exit the simulator |

### TUI Features

- **Fuzzy Command Matching**: Typos forgiven! `crete` → `create`, `obsrv` → `observe`
- **Command History**: Press ↑/↓ to cycle through previous commands
- **Tab Autocomplete**: Start typing and press Tab for suggestions
- **Real-Time Animation**: World updates 10 FPS when `Ctrl+P` is pressed
- **Live Graphs**: Sparkline population charts update every tick
- **Futuristic HUD**: Control Deck action bar, neon population graphs, and a live command center banner
- **Beautiful Emojis**: 🐰 herbivores, 🌱 plants, 🌲 trees, 🌾 grass

See **[TUI_GUIDE.md](TUI_GUIDE.md)** for a comprehensive interactive TUI guide.

## AI System Architecture

### Neural Network Engine
- Architecture: `5 → 8 → 3` fully connected layers.
- Hidden activation: `tanh`; output: linear.
- Inputs: hunger, health, distance to nearest plant, direction to plant, current speed.
- Outputs: desired acceleration vector (x, y) and an eat/rest signal.

### Reinforcement Learning
- TD(0) style update per action with exploration decay.
- Rewards: positive for eating and surviving; negative for starvation and death.
- Manual player rewards hook directly into network updates.

### Genetic Evolution
- Fitness: accumulated rewards across lifetime.
- Selection: top performers become parents when population dips.
- Crossover: per-weight mixing with random masks.
- Mutation: Gaussian noise on weights, biases, and physical traits.

### World Simulation Loop
- Tick-based update (default 1 unit per tick).
- Plant growth and seeding, herbivore perception & action, collision-free position clamping.
- Automatic reproduction when energy exceeds a threshold.

### Persistence
- Entire world serialised to JSON, including neural network weights, agent parameters, and lineage metadata.

## Example Experiments

- **Learning to Graze:** Run `simulate 2000` and watch herbivores discover efficient grazing patterns. Use `graph fitness` to visualize improvement.
- **Directed Evolution:** Use `reward` and `punish` to favour explorers over sedentary creatures, then observe offspring traits with `family_tree`.
- **Brain Analysis:** Use `show_brain [name]` before and after long simulations to inspect weight magnitude growth and strongest connections.
- **Lineage Tracking:** Combine `view` and `family_tree` to follow successful families across generations.
- **Population Dynamics:** Use `dashboard` and `graph population` to observe predator-prey style oscillations as resources vary.
- **Spatial Patterns:** Run `heatmap births` and `heatmap deaths` to identify safe zones and danger areas.
- **Learning Curves:** Track individual progress with `learning_curve [name]` to see fitness improvement over time.
- **Performance Analytics:** Use `top 10` and `compare_species` to identify and analyze the most successful strategies.

## Tips for Emergent Behaviour

- Keep the ecosystem in balance—too many plants lead to energy hoarding; too few cause collapse.
- Occasional manual rewards can push behaviour toward exploration or caution.
- Use `auto_mode on` during long visualisations to prevent starvation cascades.
- Saving snapshots periodically allows you to rewind evolution.

## New Gameplay Features

EMERGENCE now includes a comprehensive gameplay system with:

- **Game Modes:** Survival mode (reach Gen 100), Challenge mode (specific scenarios), Sandbox mode (creative freedom), and Speedrun mode (race the clock)
- **Evolution Points (EP):** Earn EP by reaching milestones and unlock new creatures, abilities, and challenges
- **Achievements:** Track your progress with 18+ achievements from "First Steps" to "Apex of Evolution"
- **Random Events:** Experience droughts, invasions, evolution boosts, and more that dynamically affect gameplay
- **Biome System:** Plains, forests, deserts, mountains, and water sources with unique properties
- **Creature Tiers:** From simple herbivores to mythical dragons and unicorns (defined in specifications)

See [GAMEPLAY_GUIDE.md](GAMEPLAY_GUIDE.md) for complete details on all gameplay features.

**Try the gameplay demo:**
```bash
python examples/gameplay_demo.py
```

**New CLI commands:**
- `start_mode [survival|challenge|sandbox|speedrun]` - Begin a game mode
- `gameplay` - Show current progress and timeline
- `achievements` - View achievement progress
- `unlock [name]` - Spend Evolution Points on unlocks

## Roadmap

- **Phase Two:** Full integration of multi-species system (carnivores, apex predators, scavengers, omnivores, mythical creatures)
- **Advanced Biomes:** Complete biome effects on movement, energy, and spawning
- **Challenge Scenarios:** Fully functional drought, invasion, ice age, and extinction challenges
- **Shared Wilderness:** Persistent multiplayer zones with leaderboards
- **Teaching Tools:** Scripted lessons, behaviour tagging, and curriculum learning

## License

EMERGENCE is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.
