"""Main TUI application for EMERGENCE using Textual."""

from __future__ import annotations

import asyncio
import shlex
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static, TabbedContent, TabPane
from thefuzz import process

from emergence.dashboard import Dashboard
from emergence.entities import Herbivore, Plant
from emergence.tui_widgets import (
    CommandInputWidget,
    ControlButtonsWidget,
    GameBannerWidget,
    LiveGraphWidget,
    StatsPanel,
    WorldViewWidget,
)
from emergence.world import World

try:
    from emergence.gameplay import GameplaySystem
    from emergence.game_modes import ChallengeType, GameModeType
    from emergence.progression import UnlockType

    GAMEPLAY_ENABLED = True
except ImportError:
    GAMEPLAY_ENABLED = False


class TitleScreen(Screen):
    """Beautiful title screen with ASCII art."""

    def compose(self) -> ComposeResult:
        """Compose the title screen."""
        yield Container(
            Static(self._get_title_art(), id="title_art"),
            id="title_container",
        )

    def _get_title_art(self) -> Text:
        """Generate beautiful ASCII art title."""
        text = Text()
        text.append("\n" * 1)

        # Game-style ASCII art logo
        logo_header = "╔" + "═" * 70 + "╗\n"
        text.append(logo_header, style="bold bright_cyan")

        title_line = "║" + " " * 70 + "║\n"
        text.append(title_line, style="bold bright_cyan")

        text.append("║     ", style="bold bright_cyan")
        text.append("███████╗███╗   ███╗███████╗██████╗  ██████╗ ███████╗", style="bold yellow")
        text.append("      ║\n", style="bold bright_cyan")

        text.append("║     ", style="bold bright_cyan")
        text.append("██╔════╝████╗ ████║██╔════╝██╔══██╗██╔════╝ ██╔════╝", style="bold yellow")
        text.append("      ║\n", style="bold bright_cyan")

        text.append("║     ", style="bold bright_cyan")
        text.append("█████╗  ██╔████╔██║█████╗  ██████╔╝██║  ███╗█████╗  ", style="bold bright_yellow")
        text.append("      ║\n", style="bold bright_cyan")

        text.append("║     ", style="bold bright_cyan")
        text.append("██╔══╝  ██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ", style="bold yellow")
        text.append("      ║\n", style="bold bright_cyan")

        text.append("║     ", style="bold bright_cyan")
        text.append("███████╗██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝███████╗", style="bold bright_yellow")
        text.append("      ║\n", style="bold bright_cyan")

        text.append("║     ", style="bold bright_cyan")
        text.append("╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝", style="bold yellow")
        text.append("      ║\n", style="bold bright_cyan")

        text.append(title_line, style="bold bright_cyan")

        text.append("║         ", style="bold bright_cyan")
        text.append("🧬✨ AI LIFE SIMULATION - TERMINAL GAME EDITION ✨🧬", style="bold bright_green")
        text.append("         ║\n", style="bold bright_cyan")

        text.append(title_line, style="bold bright_cyan")

        text.append("║                  ", style="bold bright_cyan")
        text.append("[🚀 FEATURES 🚀]", style="bold magenta on black")
        text.append("                              ║\n", style="bold bright_cyan")

        text.append("║    🧠 Neural Networks  │  🎮 Reinforcement Learning  │  🧬 Genetics    ║\n", style="cyan")
        text.append("║    🌍 Live World View  │  📊 Real-Time Stats  │  🎨 Rich Graphics    ║\n", style="cyan")

        text.append(title_line, style="bold bright_cyan")

        text.append("║                       ", style="bold bright_cyan")
        text.append("[⚡ START GAME ⚡]", style="bold black on bright_green")
        text.append("                          ║\n", style="bold bright_cyan")

        text.append(title_line, style="bold bright_cyan")

        text.append("║                  ", style="bold bright_cyan")
        text.append("Press ", style="white")
        text.append("ENTER", style="bold bright_green")
        text.append(" to Launch Simulation", style="white")
        text.append("                    ║\n", style="bold bright_cyan")

        text.append("║                  ", style="bold bright_cyan")
        text.append("Press ", style="white")
        text.append("Q", style="bold red")
        text.append(" to Quit                        ", style="white")
        text.append("           ║\n", style="bold bright_cyan")

        text.append(title_line, style="bold bright_cyan")

        logo_footer = "╚" + "═" * 70 + "╝\n"
        text.append(logo_footer, style="bold bright_cyan")

        text.append("\n")
        text.append("       🎮 ", style="yellow")
        text.append("Experience evolution in your terminal • Push CLI boundaries ", style="dim white")
        text.append("🎮\n", style="yellow")

        return text

    def on_key(self, event) -> None:
        """Handle key presses on title screen."""
        if event.key == "enter":
            self.app.push_screen("main")
        elif event.key == "q":
            self.app.exit()


class MainGameScreen(Screen):
    """Main game screen with split-pane layout."""

    BINDINGS = [
        Binding("ctrl+p", "toggle_play", "Play/Pause", show=True),
        Binding("ctrl+f", "fast_forward", "Fast Forward", show=True),
        Binding("ctrl+d", "dashboard_view", "Dashboard", show=True),
        Binding("ctrl+s", "save_game", "Save", show=True),
        Binding("ctrl+q", "quit_game", "Quit", show=True),
        Binding("escape", "clear_input", "Clear", show=False),
        Binding("tab", "autocomplete", "Autocomplete", show=False),
    ]

    is_playing: reactive[bool] = reactive(False)
    speed_multiplier: reactive[float] = reactive(1.0)

    def __init__(self, world: World, **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = world
        self.console = Console()
        self.dashboard = Dashboard(self.world, self.console)
        self.gameplay: Optional[GameplaySystem] = (
            GameplaySystem(self.world, self.console) if GAMEPLAY_ENABLED else None
        )
        self.simulation_task: Optional[asyncio.Task] = None
        self.available_commands: List[str] = [
            "help",
            "create",
            "observe",
            "reward",
            "punish",
            "teach",
            "feed",
            "heal",
            "breed",
            "show_brain",
            "show_lineage",
            "family_tree",
            "simulate",
            "view",
            "stats",
            "dashboard",
            "graph",
            "heatmap",
            "timeline",
            "learning_curve",
            "compare_species",
            "events",
            "top",
            "population",
            "save",
            "load",
            "speed",
            "auto_mode",
            "follow",
            "snapshot",
            "export_stats",
            "play",
            "pause",
            "quit",
            "exit",
        ]

        # Add gameplay commands if available
        if GAMEPLAY_ENABLED:
            self.available_commands.extend([
                "start_mode",
                "gameplay",
                "unlock",
                "achievements",
            ])

    def compose(self) -> ComposeResult:
        """Compose the main game screen."""
        yield Header(show_clock=True)
        yield GameBannerWidget(world=self.world, id="game_banner")

        # Main content with tabs
        with TabbedContent(initial="world"):
            with TabPane("🌍 World", id="world"):
                with Horizontal():
                    with Vertical(id="world_container"):
                        yield WorldViewWidget(world=self.world, id="world_view")
                        yield ControlButtonsWidget(id="controls")
                    with Vertical(id="stats_container"):
                        yield StatsPanel(world=self.world, id="stats_panel")
                        yield LiveGraphWidget(world=self.world, graph_type="population", id="graph_widget")

            with TabPane("📊 Dashboard", id="dashboard"):
                yield Static("Dashboard View - Coming Soon", id="dashboard_view")

            with TabPane("📈 Graphs", id="graphs"):
                yield Static("Graphs View - Coming Soon", id="graphs_view")

            with TabPane("🧬 Evolution", id="evolution"):
                yield Static("Evolution View - Coming Soon", id="evolution_view")

            with TabPane("⚙️ Settings", id="settings"):
                yield Static(self._get_settings_panel(), id="settings_view")

        # Command input at bottom
        yield CommandInputWidget(available_commands=self.available_commands, id="command_palette")
        yield Footer()

    def _get_settings_panel(self) -> Panel:
        """Generate settings panel."""
        text = Text()
        text.append("╔" + "═" * 60 + "╗\n", style="cyan")
        text.append("║", style="cyan")
        text.append(" " * 21 + "SETTINGS" + " " * 21, style="bold cyan")
        text.append("      ║\n", style="cyan")
        text.append("╚" + "═" * 60 + "╝\n", style="cyan")
        text.append("\n")

        text.append("🎨 Visual Settings\n", style="bold yellow")
        text.append("  Animation Speed:  ", style="white")
        text.append(f"[{'░' * 4}█{'░' * 3}] {self.speed_multiplier}x\n", style="cyan")
        text.append("  Particle Effects: ", style="white")
        text.append("[✓] Enabled\n", style="green")
        text.append("\n")

        text.append("🎮 Gameplay Settings\n", style="bold yellow")
        text.append("  Auto-save:        ", style="white")
        text.append("[✓] Every 10 generations\n", style="green")
        text.append("  Starting Pop:     ", style="white")
        text.append(f"[{'░' * 2}█{'░' * 5}] 10 creatures\n", style="cyan")
        text.append("\n")

        text.append("⌨️  Keyboard Shortcuts\n", style="bold yellow")
        text.append("  Ctrl+P: Play/Pause     Ctrl+F: Fast Forward\n", style="dim")
        text.append("  Ctrl+D: Dashboard      Ctrl+S: Save\n", style="dim")
        text.append("  Ctrl+Q: Quit           Tab: Autocomplete\n", style="dim")

        return Panel(text, border_style="cyan")

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        command_widget = self.query_one("#command_palette", CommandInputWidget)
        command_widget.set_available_commands(self.available_commands)
        command_widget.focus_input()

        game_banner = self.query_one("#game_banner", GameBannerWidget)
        game_banner.world = self.world
        game_banner.is_playing = self.is_playing
        game_banner.speed_multiplier = self.speed_multiplier

        controls = self.query_one("#controls", ControlButtonsWidget)
        controls.is_playing = self.is_playing
        controls.speed_multiplier = self.speed_multiplier

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission."""
        command_line = event.value.strip()
        if not command_line:
            return

        command_widget = self.query_one("#command_palette", CommandInputWidget)
        command_widget.record_command(command_line)
        command_widget.clear()
        command_widget.focus_input()

        # Parse and execute command
        self.execute_command(command_line)

    def execute_command(self, command_line: str) -> None:
        """Execute a command with fuzzy matching."""
        try:
            args = shlex.split(command_line)
        except ValueError:
            self.notify("Invalid command syntax", severity="error")
            return

        if not args:
            return

        command = args[0].lower()
        params = args[1:]

        # Fuzzy match command
        best_match, score = process.extractOne(command, self.available_commands)

        if score < 60:
            self.notify(f"Unknown command: {command}. Type 'help' for options.", severity="warning")
            return

        if score < 80:
            # Ask for confirmation
            self.notify(f"Did you mean: {best_match}? Running it anyway...", severity="information")

        matched_command = best_match

        # Execute the matched command
        if matched_command == "help":
            self.show_help()
        elif matched_command == "create":
            self.command_create(params)
        elif matched_command == "observe":
            self.command_observe(params)
        elif matched_command == "simulate":
            self.command_simulate(params)
        elif matched_command in ("play", "pause"):
            self.action_toggle_play()
        elif matched_command == "feed":
            self.command_feed(params)
        elif matched_command == "heal":
            self.command_heal(params)
        elif matched_command == "stats":
            self.show_stats()
        elif matched_command == "population":
            self.show_population()
        elif matched_command == "reward":
            self.command_reward(params)
        elif matched_command == "punish":
            self.command_punish(params)
        elif matched_command == "teach":
            self.command_teach(params)
        elif matched_command == "breed":
            self.command_breed(params)
        elif matched_command == "auto_mode":
            self.command_auto_mode(params)
        elif matched_command == "show_brain":
            self.command_show_brain(params)
        elif matched_command == "show_lineage":
            self.command_show_lineage(params)
        elif matched_command == "family_tree":
            self.command_family_tree(params)
        elif matched_command == "save":
            self.command_save(params)
        elif matched_command == "load":
            self.command_load(params)
        elif matched_command == "graph":
            self.command_graph(params)
        elif matched_command == "heatmap":
            self.command_heatmap(params)
        elif matched_command == "timeline":
            self.command_timeline(params)
        elif matched_command == "learning_curve":
            self.command_learning_curve(params)
        elif matched_command == "compare_species":
            self.command_compare_species(params)
        elif matched_command == "events":
            self.command_events(params)
        elif matched_command == "top":
            self.command_top(params)
        elif matched_command == "snapshot":
            self.command_snapshot(params)
        elif matched_command == "export_stats":
            self.command_export_stats(params)
        elif matched_command == "speed":
            self.command_speed(params)
        elif matched_command == "follow":
            self.command_follow(params)
        elif matched_command == "dashboard":
            self.command_dashboard(params)
        elif matched_command in ("quit", "exit"):
            self.app.exit()
        else:
            # Check for gameplay commands
            if GAMEPLAY_ENABLED and self.gameplay:
                if matched_command == "start_mode":
                    self.command_start_mode(params)
                elif matched_command == "gameplay":
                    self.command_gameplay_status(params)
                elif matched_command == "unlock":
                    self.command_unlock(params)
                elif matched_command == "achievements":
                    self.command_achievements(params)
                else:
                    self.notify(f"Command '{matched_command}' not yet implemented in TUI", severity="warning")
            else:
                self.notify(f"Command '{matched_command}' not yet implemented in TUI", severity="warning")

    def show_help(self) -> None:
        """Show help information."""
        help_text = """CORE COMMANDS:
  create [species] [name]     - Spawn plant/herbivore
  observe [name]              - Inspect creature stats
  simulate [ticks]            - Run N ticks headless
  stats/population            - Show ecosystem info

CREATURE INTERACTION:
  reward [name] [amount]      - Reinforce learning
  punish [name] [amount]      - Discourage behavior
  teach [name] [strength]     - Guide learning
  feed/heal [name]            - Help a creature
  breed [name1] [name2]       - Force reproduction

VISUALIZATION & ANALYSIS:
  dashboard                   - Main statistics panel
  graph [type]                - population/fitness/age/energy
  heatmap [type]              - births/deaths/food
  timeline                    - Evolution timeline
  show_brain [name]           - Neural network details
  family_tree [name] [depth]  - Ancestry visualization
  learning_curve [name]       - Learning progress
  compare_species             - Species comparison
  events [count] [type]       - Recent events
  top [count]                 - Top performers

PERSISTENCE:
  save/load [file]            - World state management
  snapshot [name]             - Create/list snapshots
  snapshot compare [n1] [n2]  - Compare snapshots
  export_stats [file]         - Export to JSON/CSV

CONTROLS:
  play/pause                  - Toggle simulation
  speed [multiplier]          - Set speed (0.1-10.0)
  auto_mode on/off            - Toggle resource spawning
  follow [name]               - Camera follow creature

KEYBOARD SHORTCUTS:
  Ctrl+P - Play/Pause  |  Ctrl+F - Fast Forward
  Ctrl+D - Dashboard   |  Ctrl+S - Quick Save
  Tab    - Autocomplete|  Esc    - Clear Input
"""

        if GAMEPLAY_ENABLED and self.gameplay:
            help_text += """
GAMEPLAY SYSTEM:
  start_mode [mode]           - survival/challenge/sandbox/speedrun
  gameplay                    - Show status & timeline
  unlock [name]               - Spend Evolution Points
  achievements                - View progress
"""

        self.notify(help_text, title="📚 Help", timeout=20, severity="information")

    def command_create(self, params: List[str]) -> None:
        """Create a new entity."""
        if len(params) < 1:
            self.notify("Usage: create [species] [name]", severity="error")
            return

        species = params[0].lower()
        name = params[1] if len(params) > 1 else None

        if species in {"plant", "plants"}:
            plant = self.world.spawn_plant(name=name)
            self.notify(f"✅ Spawned plant {plant.name}", severity="success")
            self.refresh_widgets()
        elif species in {"herbivore", "herbivores"}:
            herb = self.world.spawn_herbivore(name=name)
            self.notify(f"✅ Spawned herbivore {herb.name}", severity="success")
            self.refresh_widgets()
        else:
            self.notify(f"Unknown species: {species}", severity="error")

    def command_observe(self, params: List[str]) -> None:
        """Observe a creature."""
        if not params:
            self.notify("Usage: observe [name]", severity="error")
            return

        name = params[0]
        stats = self.world.creature_stats(name)
        if stats:
            info = f"""
Creature: {name}
Energy: {stats['energy']:.1f}
Health: {stats['health']:.1f}
Age: {stats['age']:.0f}
Fitness: {stats['fitness']:.1f}
Generation: {stats['generation']}
"""
            self.notify(info, title=f"🐰 {name}", timeout=10, severity="information")
        else:
            self.notify(f"Creature {name} not found", severity="error")

    def command_simulate(self, params: List[str]) -> None:
        """Simulate N ticks."""
        ticks = int(params[0]) if params else 10
        self.notify(f"Simulating {ticks} ticks...", severity="information")

        # Run simulation
        self.world.simulate(ticks, headless=True)
        self.refresh_widgets()

        self.notify(f"✅ Simulated {ticks} ticks", severity="success")

    def command_feed(self, params: List[str]) -> None:
        """Feed a creature."""
        if not params:
            self.notify("Usage: feed [name]", severity="error")
            return

        name = params[0]
        creature = self._find_herbivore(name)
        if not creature:
            self.notify(f"Creature {name} not found", severity="error")
            return

        creature.energy = min(creature.max_energy, creature.energy + 30)
        self.notify(f"✅ Fed {name}. Energy now {creature.energy:.1f}", severity="success")
        self.refresh_widgets()

    def command_heal(self, params: List[str]) -> None:
        """Heal a creature."""
        if not params:
            self.notify("Usage: heal [name]", severity="error")
            return

        name = params[0]
        creature = self._find_herbivore(name)
        if not creature:
            self.notify(f"Creature {name} not found", severity="error")
            return

        creature.health = min(creature.max_health, creature.health + 40)
        self.notify(f"✅ Healed {name}. Health now {creature.health:.1f}", severity="success")
        self.refresh_widgets()

    def show_stats(self) -> None:
        """Show statistics."""
        summary = self.world.stats.get_summary()
        current_pop = summary.get("current_population", {})

        stats_text = f"""
Tick: {self.world.tick_count}
Herbivores: {current_pop.get('herbivores', 0)}
Plants: {current_pop.get('plants', 0)}
Total Births: {self.world.stats.total_births}
Total Deaths: {self.world.stats.total_deaths}
"""
        self.notify(stats_text, title="📊 Stats", timeout=8, severity="information")

    def show_population(self) -> None:
        """Show population list."""
        herbivore_count = len([h for h in self.world.herbivores if h.alive])
        plant_count = len([p for p in self.world.plants if p.alive])

        pop_text = f"""
Living Entities:
🐰 Herbivores: {herbivore_count}
🌱 Plants: {plant_count}

Top 3 Creatures:
"""
        for i, h in enumerate(sorted(self.world.herbivores, key=lambda x: x.fitness, reverse=True)[:3], 1):
            pop_text += f"  {i}. {h.name} (Fitness: {h.fitness:.1f})\n"

        self.notify(pop_text, title="Population", timeout=10, severity="information")

    # Phase 1: Critical Core Commands
    def command_reward(self, params: List[str]) -> None:
        """Reward a creature."""
        if len(params) < 1:
            self.notify("Usage: reward [name] [amount]", severity="error")
            return

        name = params[0]
        amount = float(params[1]) if len(params) > 1 else 5.0

        if self.world.reward(name, amount):
            self.notify(f"✅ Rewarded {name} with {amount} points", severity="success")
            self.refresh_widgets()
        else:
            self.notify(f"Creature {name} not found", severity="error")

    def command_punish(self, params: List[str]) -> None:
        """Punish a creature."""
        if len(params) < 1:
            self.notify("Usage: punish [name] [amount]", severity="error")
            return

        name = params[0]
        amount = float(params[1]) if len(params) > 1 else 5.0

        if self.world.punish(name, amount):
            self.notify(f"⚠️ Punished {name} with {amount} points", severity="warning")
            self.refresh_widgets()
        else:
            self.notify(f"Creature {name} not found", severity="error")

    def command_teach(self, params: List[str]) -> None:
        """Teach a creature."""
        if len(params) < 1:
            self.notify("Usage: teach [name] [strength]", severity="error")
            return

        name = params[0]
        strength = float(params[1]) if len(params) > 1 else 2.0

        if self.world.reward(name, strength):
            self.notify(f"📚 Provided guidance to {name} (+{strength})", severity="information")
            self.refresh_widgets()
        else:
            self.notify(f"Creature {name} not found", severity="error")

    def command_breed(self, params: List[str]) -> None:
        """Breed two creatures."""
        if len(params) < 2:
            self.notify("Usage: breed [name1] [name2]", severity="error")
            return

        parent_a = self._find_herbivore(params[0])
        parent_b = self._find_herbivore(params[1])

        if not parent_a or not parent_b:
            self.notify("Both parents must be herbivores", severity="error")
            return

        child = self.world.genetics.reproduce(
            parent_a,
            parent_b,
            name=f"herbivore_{self.world.next_id}",
            position=parent_a.position,
            rng=self.world.rng,
        )
        self.world.herbivores.append(child)
        self.world.next_id += 1
        parent_a.energy *= 0.7
        parent_b.energy *= 0.7

        self.notify(f"✅ Bred {parent_a.name} + {parent_b.name} → {child.name}", severity="success")
        self.refresh_widgets()

    def command_auto_mode(self, params: List[str]) -> None:
        """Toggle auto mode."""
        if not hasattr(self, 'auto_mode'):
            self.auto_mode = False

        if not params:
            status = "on" if self.auto_mode else "off"
            self.notify(f"Auto mode is {status}", severity="information")
            return

        flag = params[0].lower()
        if flag == "on":
            self.auto_mode = True
            self.world.config.plant_spawn_rate = 0.1
            self.notify("✅ Auto mode enabled. Plants will spawn more frequently.", severity="success")
        elif flag == "off":
            self.auto_mode = False
            self.world.config.plant_spawn_rate = 0.05
            self.notify("⚠️ Auto mode disabled.", severity="warning")
        else:
            self.notify("Usage: auto_mode on/off", severity="error")

    # Phase 2: Persistence & Data Management
    def command_save(self, params: List[str]) -> None:
        """Save world state."""
        from pathlib import Path

        if not params:
            self.notify("Usage: save [filename]", severity="error")
            return

        try:
            path = Path(params[0]).expanduser()
            self.world.save(path)
            self.notify(f"✅ Saved world to {path}", severity="success")
        except Exception as e:
            self.notify(f"❌ Save failed: {e}", severity="error")

    def command_load(self, params: List[str]) -> None:
        """Load world state."""
        from pathlib import Path

        if not params:
            self.notify("Usage: load [filename]", severity="error")
            return

        try:
            path = Path(params[0]).expanduser()
            if not path.exists():
                self.notify(f"File not found: {path}", severity="error")
                return

            self.world = World.load(path)
            self.dashboard = Dashboard(self.world, self.console)
            if GAMEPLAY_ENABLED:
                self.gameplay = GameplaySystem(self.world, self.console)

            self.notify(f"✅ Loaded world from {path}", severity="success")
            self.refresh_widgets()
        except Exception as e:
            self.notify(f"❌ Load failed: {e}", severity="error")

    def command_snapshot(self, params: List[str]) -> None:
        """Create or manage snapshots."""
        if not params or params[0].lower() == "list":
            snapshots = self.world.stats.snapshots
            if not snapshots:
                self.notify("No snapshots saved yet.", severity="information")
                return

            snapshot_text = "Snapshots:\n"
            for name, data in snapshots.items():
                herd_count = len(data["state"].get("herbivores", []))
                tick = data.get("tick", 0)
                snapshot_text += f"  • {name} (Tick: {tick}, Herbivores: {herd_count})\n"

            self.notify(snapshot_text, title="Snapshots", timeout=10, severity="information")
            return

        if params[0].lower() == "compare" and len(params) >= 3:
            self._compare_snapshots(params[1], params[2])
            return

        snapshot_name = params[0]
        self.world.stats.create_snapshot(snapshot_name, self.world.to_dict())
        self.notify(f"✅ Created snapshot: {snapshot_name}", severity="success")

    def command_export_stats(self, params: List[str]) -> None:
        """Export statistics."""
        from pathlib import Path

        if not params:
            self.notify("Usage: export_stats [filename]", severity="error")
            return

        try:
            path = Path(params[0]).expanduser()
            if path.suffix.lower() == ".csv":
                self.world.stats.export_to_csv(path)
            else:
                self.world.stats.export_to_json(path)
            self.notify(f"✅ Exported statistics to {path}", severity="success")
        except Exception as e:
            self.notify(f"❌ Export failed: {e}", severity="error")

    # Phase 3: Visualization & Analysis Tools
    def command_show_brain(self, params: List[str]) -> None:
        """Show creature's brain."""
        if not params:
            self.notify("Usage: show_brain [name]", severity="error")
            return

        from emergence.visualization import Visualizer
        visualizer = Visualizer(self.world)

        # Capture the brain output
        creature = self._find_herbivore(params[0])
        if not creature:
            self.notify(f"Creature {params[0]} not found", severity="error")
            return

        brain_info = f"""
Brain: {params[0]}
Weights shape: {creature.brain.weights_ih.shape}
Hidden layer: {creature.brain.hidden_size}
Learning rate: {creature.brain.learning_rate:.3f}

See console for full brain visualization.
"""
        self.notify(brain_info, title=f"🧠 {params[0]} Brain", timeout=8, severity="information")

        # Print full visualization to console
        visualizer.print_brain(params[0])

    def command_show_lineage(self, params: List[str]) -> None:
        """Show creature lineage."""
        if not params:
            self.notify("Usage: show_lineage [name]", severity="error")
            return

        self.dashboard.show_family_tree(params[0], depth=5)
        self.notify(f"Lineage for {params[0]} shown in console", severity="information")

    def command_family_tree(self, params: List[str]) -> None:
        """Show family tree."""
        if not params:
            self.notify("Usage: family_tree [name] [depth]", severity="error")
            return

        name = params[0]
        depth = int(params[1]) if len(params) > 1 else 6

        self.dashboard.show_family_tree(name, depth=depth)
        self.notify(f"Family tree for {name} (depth {depth}) shown in console", severity="information")

    def command_graph(self, params: List[str]) -> None:
        """Show graphs."""
        if not params:
            self.notify("Usage: graph [type] where type is: population, fitness, age, energy", severity="error")
            return

        graph_type = params[0].lower()
        last_n = 100
        if len(params) > 1:
            try:
                last_n = int(params[1])
            except ValueError:
                pass

        if graph_type == "population":
            self.dashboard.show_population_graph(last_n=last_n)
        elif graph_type == "fitness":
            self.dashboard.show_fitness_graph(last_n=last_n)
        elif graph_type == "age":
            self.dashboard.show_age_distribution()
        elif graph_type == "energy":
            self.dashboard.show_energy_distribution()
        else:
            self.notify(f"Unknown graph type: {graph_type}", severity="error")
            return

        self.notify(f"{graph_type.title()} graph shown in console", severity="information")

    def command_heatmap(self, params: List[str]) -> None:
        """Show heatmap."""
        if not params:
            self.notify("Usage: heatmap [type] where type is: births, deaths, food", severity="error")
            return

        heatmap_type = params[0].lower()
        self.dashboard.show_heatmap(heatmap_type)
        self.notify(f"{heatmap_type.title()} heatmap shown in console", severity="information")

    def command_timeline(self, params: List[str]) -> None:
        """Show evolution timeline."""
        self.dashboard.show_timeline()
        self.notify("Evolution timeline shown in console", severity="information")

    def command_learning_curve(self, params: List[str]) -> None:
        """Show learning curve."""
        if not params:
            self.notify("Usage: learning_curve [name]", severity="error")
            return

        self.dashboard.show_learning_curve(params[0])
        self.notify(f"Learning curve for {params[0]} shown in console", severity="information")

    def command_compare_species(self, params: List[str]) -> None:
        """Compare species."""
        self.dashboard.show_species_comparison()
        self.notify("Species comparison shown in console", severity="information")

    def command_events(self, params: List[str]) -> None:
        """Show recent events."""
        count = 10
        event_type = None
        for param in params:
            if param.isdigit():
                count = int(param)
            else:
                event_type = param.lower()

        self.dashboard.show_recent_events(count=count, event_type=event_type)
        self.notify(f"Showing {count} recent events in console", severity="information")

    def command_top(self, params: List[str]) -> None:
        """Show top performers."""
        count = int(params[0]) if params else 10
        self.dashboard.show_top_performers(count=count)
        self.notify(f"Top {count} performers shown in console", severity="information")

    def command_dashboard(self, params: List[str]) -> None:
        """Show main dashboard."""
        self.dashboard.show_main_dashboard()
        self.notify("Dashboard shown in console", severity="information")

    # Phase 4: Advanced Controls
    def command_speed(self, params: List[str]) -> None:
        """Set speed multiplier."""
        if not params:
            self.notify(f"Current speed multiplier: {self.speed_multiplier}x", severity="information")
            return

        try:
            self.speed_multiplier = max(0.1, float(params[0]))
            self.notify(f"⚡ Speed multiplier set to {self.speed_multiplier}x", severity="success")
            self.refresh_widgets()
        except ValueError:
            self.notify("Speed must be a number", severity="error")

    def command_follow(self, params: List[str]) -> None:
        """Follow a creature."""
        from emergence.visualization import Visualizer

        if not hasattr(self, 'visualizer'):
            self.visualizer = Visualizer(self.world)

        if not params:
            self.visualizer.follow_target = None
            self.notify("⏹️ Stopped following any creature.", severity="information")
            return

        name = params[0]
        if self._find_herbivore(name):
            self.visualizer.follow_target = name
            self.notify(f"👁️ Now following {name}", severity="success")
        else:
            self.notify(f"Creature {name} not found", severity="error")

    # Phase 5: Gameplay System Commands
    def command_start_mode(self, params: List[str]) -> None:
        """Start a game mode."""
        if not self.gameplay:
            self.notify("Gameplay system not available", severity="error")
            return

        if not params:
            self.notify("Usage: start_mode [survival|challenge|sandbox|speedrun] [challenge_name]", severity="error")
            return

        mode_name = params[0].lower()
        mode_map = {
            "survival": GameModeType.SURVIVAL,
            "challenge": GameModeType.CHALLENGE,
            "sandbox": GameModeType.SANDBOX,
            "speedrun": GameModeType.SPEEDRUN,
        }

        mode_type = mode_map.get(mode_name)
        if not mode_type:
            self.notify(f"Unknown mode: {mode_name}", severity="error")
            return

        challenge = None
        if len(params) > 1:
            challenge_name = params[1].lower()
            challenge_map = {
                "drought": ChallengeType.DROUGHT,
                "invasion": ChallengeType.PREDATOR_INVASION,
                "ice_age": ChallengeType.ICE_AGE,
                "extinction": ChallengeType.EXTINCTION_EVENT,
            }
            challenge = challenge_map.get(challenge_name)
            if challenge is None:
                self.notify(f"Unknown challenge: {challenge_name}", severity="warning")

        message = self.gameplay.start_mode(mode_type, challenge)
        self.notify(message, title="Game Mode", timeout=8, severity="success")
        self.refresh_widgets()

    def command_gameplay_status(self, params: List[str]) -> None:
        """Show gameplay status."""
        if not self.gameplay:
            self.notify("Gameplay system not available", severity="error")
            return

        # Print to console
        panel = self.gameplay.display_status_panel()
        timeline = self.gameplay.display_timeline()
        self.console.print(panel)
        self.console.print(timeline)

        self.notify("Gameplay status shown in console", severity="information")

    def command_unlock(self, params: List[str]) -> None:
        """Purchase an unlock."""
        if not self.gameplay:
            self.notify("Gameplay system not available", severity="error")
            return

        if not params:
            self.notify("Usage: unlock [name]", severity="error")
            return

        unlock_map = {
            "carnivores": UnlockType.CARNIVORES,
            "apex": UnlockType.APEX_PREDATORS,
            "scavengers": UnlockType.SCAVENGERS,
            "omnivores": UnlockType.OMNIVORES,
            "camouflage": UnlockType.CAMOUFLAGE,
            "mutation": UnlockType.MUTATION_BOOST,
            "teaching": UnlockType.ADVANCED_TEACHING,
            "divine": UnlockType.DIVINE_INTERVENTION,
            "weather": UnlockType.WEATHER_CONTROL,
            "timewarp": UnlockType.TIME_WARP,
            "drought": UnlockType.DROUGHT_CHALLENGE,
            "ice_age": UnlockType.ICE_AGE_CHALLENGE,
            "invasion": UnlockType.INVASION_CHALLENGE,
            "extinction": UnlockType.EXTINCTION_CHALLENGE,
        }

        key = params[0].lower()
        unlock_type = unlock_map.get(key)
        if not unlock_type:
            self.notify(f"Unknown unlock: {key}", severity="error")
            return

        message = self.gameplay.purchase_unlock(unlock_type)
        self.notify(message, title="Unlock", timeout=6, severity="information")

    def command_achievements(self, params: List[str]) -> None:
        """Show achievements."""
        if not self.gameplay:
            self.notify("Gameplay system not available", severity="error")
            return

        summary = self.gameplay.progression.get_achievements_summary()

        achievements_text = f"Achievements ({summary['unlocked']}/{summary['total']}):\n\n"
        for achievement in self.gameplay.progression.achievements.values():
            status = "✅" if achievement.unlocked else "🔒"
            progress = f"{min(achievement.progress, achievement.max_progress):.0f}/{achievement.max_progress}"
            achievements_text += f"{status} {achievement.name}: {progress}\n"

        self.notify(achievements_text, title="Achievements", timeout=15, severity="information")

    # Helper methods
    def _compare_snapshots(self, name1: str, name2: str) -> None:
        """Compare two snapshots."""
        snapshots = self.world.stats.snapshots
        if name1 not in snapshots:
            self.notify(f"Snapshot {name1} not found", severity="error")
            return
        if name2 not in snapshots:
            self.notify(f"Snapshot {name2} not found", severity="error")
            return

        snap1 = snapshots[name1]
        snap2 = snapshots[name2]

        tick1 = snap1.get("tick", 0)
        tick2 = snap2.get("tick", 0)
        herd1 = len(snap1["state"].get("herbivores", []))
        herd2 = len(snap2["state"].get("herbivores", []))
        births1 = snap1.get("total_births", 0)
        births2 = snap2.get("total_births", 0)
        deaths1 = snap1.get("total_deaths", 0)
        deaths2 = snap2.get("total_deaths", 0)

        comparison_text = f"""
Snapshot Comparison: {name1} vs {name2}

Tick: {tick1} → {tick2} (Δ {tick2-tick1:+d})
Herbivores: {herd1} → {herd2} (Δ {herd2-herd1:+d})
Total Births: {births1} → {births2} (Δ {births2-births1:+d})
Total Deaths: {deaths1} → {deaths2} (Δ {deaths2-deaths1:+d})
"""
        self.notify(comparison_text, title="Snapshot Comparison", timeout=12, severity="information")

    def refresh_widgets(self) -> None:
        """Refresh all reactive widgets."""
        try:
            world_view = self.query_one("#world_view", WorldViewWidget)
            world_view.world = self.world
            world_view.refresh()

            stats_panel = self.query_one("#stats_panel", StatsPanel)
            stats_panel.world = self.world
            stats_panel.refresh()

            graph_widget = self.query_one("#graph_widget", LiveGraphWidget)
            graph_widget.world = self.world
            graph_widget.refresh()

            game_banner = self.query_one("#game_banner", GameBannerWidget)
            game_banner.world = self.world
            game_banner.is_playing = self.is_playing
            game_banner.speed_multiplier = self.speed_multiplier
            game_banner.refresh()

            controls = self.query_one("#controls", ControlButtonsWidget)
            controls.is_playing = self.is_playing
            controls.speed_multiplier = self.speed_multiplier
            controls.refresh()
        except Exception:
            pass

    def _find_herbivore(self, name: str) -> Optional[Herbivore]:
        """Find a herbivore by name."""
        for herbivore in self.world.herbivores:
            if herbivore.name == name:
                return herbivore
        return None

    def action_toggle_play(self) -> None:
        """Toggle play/pause."""
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.notify("▶️  Simulation started", severity="information")
            self.start_simulation()
        else:
            self.notify("⏸️  Simulation paused", severity="information")
            self.stop_simulation()

        self.refresh_widgets()

    def start_simulation(self) -> None:
        """Start the simulation loop."""
        if self.simulation_task is None or self.simulation_task.done():
            self.simulation_task = asyncio.create_task(self._simulation_loop())

    def stop_simulation(self) -> None:
        """Stop the simulation loop."""
        if self.simulation_task and not self.simulation_task.done():
            self.simulation_task.cancel()

    async def _simulation_loop(self) -> None:
        """Main simulation loop."""
        try:
            while self.is_playing:
                # Simulate one tick
                self.world.simulate(1, headless=False)

                # Refresh widgets
                self.refresh_widgets()

                # Control speed
                delay = 0.1 / max(0.1, self.speed_multiplier)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass

    def action_fast_forward(self) -> None:
        """Fast forward simulation."""
        self.speed_multiplier = min(10.0, self.speed_multiplier * 2)
        self.notify(f"⏩ Speed: {self.speed_multiplier}x", severity="information")
        self.refresh_widgets()

    def action_dashboard_view(self) -> None:
        """Switch to dashboard view."""
        self.notify("Switching to dashboard...", severity="information")

    def action_save_game(self) -> None:
        """Save the game."""
        try:
            from pathlib import Path

            save_path = Path("emergence_autosave.json")
            self.world.save(save_path)
            self.notify(f"✅ Game saved to {save_path}", severity="success")
        except Exception as e:
            self.notify(f"❌ Save failed: {e}", severity="error")

    def action_quit_game(self) -> None:
        """Quit the game."""
        self.app.exit()

    def action_clear_input(self) -> None:
        """Clear the command input."""
        try:
            command_widget = self.query_one("#command_palette", CommandInputWidget)
            command_widget.clear()
        except Exception:
            pass

    def action_autocomplete(self) -> None:
        """Autocomplete command."""
        try:
            command_widget = self.query_one("#command_palette", CommandInputWidget)
            current_text = command_widget.get_value()
            stripped = current_text.strip()

            if not stripped:
                suggestions = command_widget.current_suggestions
                if suggestions:
                    command_widget.set_value(f"{suggestions[0]} ")
                return

            parts = current_text.split()
            prefix = parts[0].lower()
            matches = [cmd for cmd in self.available_commands if cmd.startswith(prefix)]
            if matches:
                completion = matches[0]
                if len(parts) > 1:
                    rest = " ".join(parts[1:])
                    command_widget.set_value(f"{completion} {rest}")
                else:
                    command_widget.set_value(f"{completion} ")
        except Exception:
            pass


class EmergenceApp(App):
    """Main EMERGENCE TUI application."""

    CSS = """
    /* Global styling for game-like appearance */
    Screen {
        background: $surface;
    }

    #title_container {
        align: center middle;
        background: $surface;
    }

    #title_art {
        width: auto;
        height: auto;
        background: $panel;
        border: wide $primary;
        padding: 2;
    }

    /* World container - main gameplay area */
    #world_container {
        width: 3fr;
        height: 100%;
        background: $surface-darken-1;
        padding: 1;
        border-right: solid $primary;
    }

    /* Stats container - HUD-like sidebar */
    #stats_container {
        width: 1fr;
        height: 100%;
        background: $surface-darken-2;
        border-left: heavy $accent;
        padding: 1;
    }

    /* World view - the main game viewport */
    #world_view {
        height: 3fr;
        background: $background 10%;
        border: heavy $success;
        border-title-color: $success;
        border-subtitle-color: $text-muted;
        margin-bottom: 1;
    }

    /* Stats panel - game HUD */
    #stats_panel {
        height: 2fr;
        background: $panel;
        border: tall $accent;
        border-title-color: $accent;
        padding: 1;
    }

    /* Graph widget - metrics display */
    #graph_widget {
        height: 1fr;
        background: $panel;
        border: solid $warning;
        border-title-color: $warning;
        padding: 1;
    }

    /* Control buttons - action bar */
    #controls {
        height: 4;
        background: $boost;
        border: wide $primary;
        border-title-color: $primary;
    }

    /* Command palette - input console */
    #command_palette {
        dock: bottom;
        height: 5;
        background: $surface;
        border-top: heavy $accent;
    }

    #command_input {
        background: $surface-darken-2;
        border: tall $accent;
        padding: 0 1;
    }

    #command_suggestions {
        height: 2;
        background: $panel;
        padding: 0 1;
    }

    /* Tabbed content styling */
    TabbedContent {
        height: 1fr;
        background: $surface;
    }

    Tabs {
        background: $boost;
        border-bottom: wide $primary;
    }

    Tab {
        background: $panel;
        border: solid $primary;
        padding: 0 2;
    }

    Tab:hover {
        background: $accent 50%;
    }

    Tab.-active {
        background: $accent;
        border: wide $success;
        text-style: bold;
    }

    /* Tab panes */
    TabPane {
        background: $surface;
        padding: 1;
    }

    /* Settings view styling */
    #settings_view {
        background: $panel;
        border: heavy $primary;
        padding: 2;
    }

    #dashboard_view, #graphs_view, #evolution_view {
        align: center middle;
        background: $panel;
        border: heavy $accent;
        padding: 2;
    }

    /* Game Banner - Top status bar */
    #game_banner {
        height: 5;
        background: $boost;
        border-bottom: heavy $primary;
        dock: top;
    }

    /* Header and Footer styling */
    Header {
        background: $boost;
        color: $text;
        border-bottom: heavy $primary;
        text-style: bold;
    }

    Footer {
        background: $boost;
        color: $text;
        border-top: heavy $primary;
    }

    Footer .footer--key {
        background: $accent;
        color: $text;
        text-style: bold;
    }

    Footer .footer--description {
        background: $panel;
        color: $text-muted;
    }

    /* Input styling */
    Input {
        background: $surface-darken-2;
        border: tall $accent;
        padding: 0 1;
    }

    Input:focus {
        border: tall $success;
        background: $surface-darken-1;
    }

    /* Static text styling */
    Static {
        background: transparent;
        color: $text;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = World()
        self._bootstrap_ecosystem()

    def _bootstrap_ecosystem(self) -> None:
        """Create initial ecosystem."""
        for _ in range(40):
            self.world.spawn_plant()
        for _ in range(10):
            self.world.spawn_herbivore()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Install screens
        self.install_screen(TitleScreen(), name="title")
        self.install_screen(MainGameScreen(world=self.world), name="main")

        # Show title screen
        self.push_screen("title")


def run_tui() -> None:
    """Run the TUI application."""
    app = EmergenceApp()
    app.run()


if __name__ == "__main__":
    run_tui()
