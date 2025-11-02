"""Custom Textual widgets for EMERGENCE TUI."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from thefuzz import process
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

if TYPE_CHECKING:
    from emergence.world import World


class GameBannerWidget(Static):
    """Futuristic control banner for the simulation."""

    world: reactive[Optional["World"]] = reactive(None)
    speed_multiplier: reactive[float] = reactive(1.0)
    is_playing: reactive[bool] = reactive(False)

    def __init__(self, world: Optional["World"] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = world

    def render(self) -> Panel:
        """Render the game banner with live diagnostics."""
        title = Text.from_markup("[bold cyan]🧬 EMERGENCE CONTROL CORE[/bold cyan]")

        if self.world:
            tick = self.world.tick_count
            generation = max((h.generation for h in self.world.herbivores), default=0)
            herbivores = len([h for h in self.world.herbivores if h.alive])
            plants = len([p for p in self.world.plants if p.alive])
            best_fitness = max((h.fitness for h in self.world.herbivores), default=0.0)
        else:
            tick = generation = herbivores = plants = 0
            best_fitness = 0.0

        status_color = "bright_green" if self.is_playing else "yellow"
        status_label = "LIVE" if self.is_playing else "PAUSED"

        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(justify="left")
        grid.add_column(justify="center")
        grid.add_column(justify="right")

        grid.add_row(
            Text.from_markup(f"[cyan]Tick[/]: [bold]{tick:,}[/]"),
            Text.from_markup(f"[magenta]Generation[/]: [bold]{generation}[/]"),
            Text.from_markup(f"[green]Speed[/]: [bold]{self.speed_multiplier:.1f}×[/]"),
        )
        grid.add_row(
            Text.from_markup(f"[yellow]🐰 Herbivores[/]: [bold]{herbivores}[/]"),
            Text.from_markup(f"[bright_green]🌱 Plants[/]: [bold]{plants}[/]"),
            Text.from_markup(f"[blue]Best Fitness[/]: [bold]{best_fitness:.1f}[/]"),
        )
        grid.add_row(
            Text.from_markup(f"[bold {status_color}]● {status_label}[/]"),
            Text.from_markup("[dim]Neural • RL • Genetic[/dim]"),
            Text.from_markup("[white]Ctrl+S to Save • Ctrl+Q to Quit[/white]"),
        )

        content = Table.grid(expand=True)
        content.add_column()
        content.add_row(Align.center(title))
        content.add_row(grid)

        return Panel(
            content,
            box=box.DOUBLE_EDGE,
            border_style="bright_cyan",
            subtitle="[bold cyan]Command Deck Online[/bold cyan]",
            style="on #041027",
        )


class WorldViewWidget(Static):
    """Animated world view showing creatures and environment."""

    world: reactive[Optional["World"]] = reactive(None)

    def __init__(self, world: Optional["World"] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = world
        self.viewport_width = 75
        self.viewport_height = 28

    def render(self) -> Panel:
        """Render the world view."""
        if not self.world:
            content = Text("Loading world...", style="dim yellow", justify="center")
            return Panel(
                content, 
                title="🌍 [bold yellow]GAME WORLD[/bold yellow] 🌍", 
                border_style="bold bright_green",
                subtitle="[dim]Initializing ecosystem...[/dim]"
            )

        # Create emoji-based visualization with background terrain
        grid = [[" " for _ in range(self.viewport_width)] for _ in range(self.viewport_height)]
        
        # Add subtle background pattern for terrain
        for y in range(self.viewport_height):
            for x in range(self.viewport_width):
                if (x + y) % 8 == 0:
                    grid[y][x] = "·"  # Subtle terrain dots

        # Scale world coordinates to viewport
        scale_x = self.viewport_width / self.world.config.width
        scale_y = self.viewport_height / self.world.config.height

        # Draw plants first (background layer)
        for plant in self.world.plants:
            if not plant.alive:
                continue
            x = int(plant.position[0] * scale_x)
            y = int(plant.position[1] * scale_y)
            if 0 <= x < self.viewport_width and 0 <= y < self.viewport_height:
                # Plant emoji based on growth stage
                if plant.growth_stage >= 4.0:
                    grid[y][x] = "🌲"  # Full grown tree
                elif plant.growth_stage >= 2.0:
                    grid[y][x] = "🌱"  # Growing plant
                else:
                    grid[y][x] = "🌾"  # Grass

        # Draw herbivores (foreground layer)
        for herbivore in self.world.herbivores:
            if not herbivore.alive:
                continue
            x = int(herbivore.position[0] * scale_x)
            y = int(herbivore.position[1] * scale_y)
            if 0 <= x < self.viewport_width and 0 <= y < self.viewport_height:
                # Different emoji based on energy level
                if herbivore.energy >= 70:
                    grid[y][x] = "🐰"  # Healthy herbivore
                elif herbivore.energy >= 40:
                    grid[y][x] = "🐇"  # Medium energy
                else:
                    grid[y][x] = "🐁"  # Low energy

        # Convert grid to rich text with colors
        text = Text()
        for row in grid:
            for char in row:
                if char == "🌲":
                    text.append(char, style="green")
                elif char == "🌱":
                    text.append(char, style="bright_green")
                elif char == "🌾":
                    text.append(char, style="yellow")
                elif char == "🐰":
                    text.append(char, style="cyan")
                elif char == "🐇":
                    text.append(char, style="blue")
                elif char == "🐁":
                    text.append(char, style="magenta")
                elif char == "·":
                    text.append(char, style="dim white")
                else:
                    text.append(char)
            text.append("\n")

        # Add game-like footer with instructions
        text.append("\n")
        text.append("═" * self.viewport_width, style="dim cyan")
        text.append("\n")
        text.append("🎮 ", style="bold yellow")
        text.append("CONTROLS: ", style="bold white")
        text.append("Ctrl+P", style="bold green")
        text.append("=Play/Pause ", style="white")
        text.append("│ ", style="dim")
        text.append("Tab", style="bold cyan")
        text.append("=Command ", style="white")
        text.append("│ ", style="dim")
        text.append("Click creatures for details", style="dim yellow")

        return Panel(
            Align.center(text, vertical="top"),
            title="🌍 [bold bright_green]═══ GAME WORLD ═══[/bold bright_green] 🌍",
            border_style="bold bright_green",
            subtitle=f"[bold cyan]⏱ Tick: {self.world.tick_count:,}[/bold cyan] │ [yellow]🌍 Size: {self.world.config.width:.0f}x{self.world.config.height:.0f}[/yellow]",
            box=box.HEAVY,
            style="on #02141f",
        )


class StatsPanel(Static):
    """Live statistics panel."""

    world: reactive[Optional["World"]] = reactive(None)

    def __init__(self, world: Optional["World"] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = world

    def render(self) -> Panel:
        """Render the statistics panel."""
        if not self.world:
            return Panel("Loading...", title="📊 Live Stats", border_style="cyan")

        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(justify="left")
        grid.add_column(justify="right")

        # Current generation
        max_gen = max((h.generation for h in self.world.herbivores), default=0)
        grid.add_row(Text.from_markup("[yellow]Generation[/]"), Text.from_markup(f"[bold]{max_gen}[/]"))

        # Population counts
        herbivore_count = len([h for h in self.world.herbivores if h.alive])
        plant_count = len([p for p in self.world.plants if p.alive])
        total_pop = herbivore_count + plant_count

        grid.add_row(Text.from_markup("[cyan]Total Population[/]"), Text.from_markup(f"[bold]{total_pop}[/]"))
        grid.add_row(Text(), Text())
        grid.add_row(Text.from_markup("[bright_magenta]🐰 Herbivores[/]"), Text.from_markup(f"[bold]{herbivore_count}[/]"))
        grid.add_row(Text.from_markup("[bright_green]🌱 Plants[/]"), Text.from_markup(f"[bold]{plant_count}[/]"))
        grid.add_row(Text(), Text())

        # Fitness metrics
        if self.world.herbivores:
            avg_fitness = sum(h.fitness for h in self.world.herbivores) / len(self.world.herbivores)
            best_fitness = max(h.fitness for h in self.world.herbivores)
            avg_energy = sum(h.energy for h in self.world.herbivores) / len(self.world.herbivores)

            grid.add_row(Text.from_markup("[cyan]📈 Avg Fitness[/]"), Text.from_markup(f"{avg_fitness:.1f}"))
            grid.add_row(Text.from_markup("[green]🏆 Best Fitness[/]"), Text.from_markup(f"{best_fitness:.1f}"))
            grid.add_row(Text.from_markup("[yellow]⚡ Avg Energy[/]"), Text.from_markup(self._energy_bar(avg_energy)))
        else:
            grid.add_row(Text.from_markup("[cyan]📈 Fitness[/]"), Text.from_markup("[dim]No creatures[/dim]"))

        grid.add_row(Text(), Text())

        # Lifecycle stats
        grid.add_row(Text.from_markup("[green]🌸 Total Births[/]"), Text.from_markup(f"{self.world.stats.total_births}"))
        grid.add_row(Text.from_markup("[red]💀 Total Deaths[/]"), Text.from_markup(f"{self.world.stats.total_deaths}"))
        grid.add_row(Text.from_markup("[bright_green]🍃 Plants Eaten[/]"), Text.from_markup(f"{self.world.stats.total_plants_consumed}"))

        if self.world.herbivores:
            best = max(self.world.herbivores, key=lambda h: h.fitness)
            grid.add_row(Text(), Text())
            grid.add_row(Text.from_markup("[magenta]⭐ Top Survivor[/]"), Text.from_markup(f"{best.name} ({best.fitness:.1f})"))

        return Panel(
            grid,
            title="[bold magenta]📊 LIVE HUD[/bold magenta]",
            border_style="bright_magenta",
            box=box.ROUNDED,
            style="on #180321",
        )

    def _energy_bar(self, energy: float, width: int = 10) -> str:
        """Create a visual energy bar."""
        filled = int((energy / 100.0) * width)
        bar = "█" * filled + "░" * (width - filled)
        percentage = f" {energy:.0f}%"

        if energy >= 70:
            return f"[green]{bar}[/green]{percentage}"
        elif energy >= 40:
            return f"[yellow]{bar}[/yellow]{percentage}"
        else:
            return f"[red]{bar}[/red]{percentage}"


class CommandInputWidget(Container):
    """Interactive command palette with autocomplete and history."""

    def __init__(self, available_commands: Optional[list[str]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.available_commands = available_commands or [
            "help",
            "create",
            "observe",
            "simulate",
            "feed",
            "heal",
            "stats",
            "population",
            "play",
            "pause",
            "reward",
            "punish",
            "teach",
            "breed",
            "show_brain",
            "show_lineage",
            "family_tree",
            "dashboard",
            "graph",
            "heatmap",
            "timeline",
            "save",
            "load",
            "speed",
            "auto_mode",
            "quit",
        ]
        self.command_history: list[str] = []
        self.history_index: Optional[int] = None
        self._input: Optional[Input] = None
        self._suggestions_panel: Optional[Static] = None
        self._current_suggestions: list[str] = []

    def compose(self) -> ComposeResult:
        """Compose the command input and suggestions display."""
        yield Input(
            placeholder="Type command… (Tab autocomplete • ↑/↓ history)",
            id="command_input",
        )
        yield Static(id="command_suggestions")

    def on_mount(self) -> None:
        """Initialize references after mounting."""
        self._input = self.query_one("#command_input", Input)
        self._suggestions_panel = self.query_one("#command_suggestions", Static)
        self._update_suggestions_display([])

    @property
    def current_suggestions(self) -> list[str]:
        """Return the current suggestion list."""
        return list(self._current_suggestions)

    def focus_input(self) -> None:
        """Give focus to the input widget."""
        if self._input:
            self._input.focus()

    def get_value(self) -> str:
        """Get the current input value."""
        if self._input:
            return self._input.value
        return ""

    def set_value(self, value: str) -> None:
        """Programmatically set the input value."""
        if self._input:
            self._input.value = value
            self._input.cursor_position = len(value)
            self.update_suggestions(value)

    def clear(self) -> None:
        """Clear the input field and suggestions."""
        if self._input:
            self._input.value = ""
            self._input.cursor_position = 0
        self.history_index = None
        self.update_suggestions("")

    def record_command(self, command: str) -> None:
        """Record a command in the history."""
        command = command.strip()
        if not command:
            return
        if not self.command_history or self.command_history[-1] != command:
            self.command_history.append(command)
        self.history_index = None

    def set_available_commands(self, commands: list[str]) -> None:
        """Update the list of available commands."""
        self.available_commands = commands
        self.update_suggestions(self.get_value())

    def update_suggestions(self, text: str) -> None:
        """Update suggestion list based on input text."""
        text = text.strip()
        suggestions: list[str] = []
        if text:
            matches = process.extract(text, self.available_commands, limit=5)
            suggestions = [match for match, score in matches if score >= 50]
        else:
            suggestions = self.available_commands[:5]

        self._current_suggestions = suggestions
        self._update_suggestions_display(suggestions)

    def _update_suggestions_display(self, suggestions: list[str]) -> None:
        """Render suggestion panel."""
        if not self._suggestions_panel:
            return

        display = Text()
        if suggestions:
            display.append("Suggestions: ", style="cyan")
            for idx, suggestion in enumerate(suggestions):
                if idx:
                    display.append(" • ", style="dim")
                display.append(suggestion, style="yellow")
            display.append("\n", style="dim")
            display.append("Enter to execute • Tab to autocomplete", style="dim")
        else:
            display.append(
                "Type commands • Tab autocomplete • ↑/↓ history • Ctrl+Space palette",
                style="dim",
            )

        panel = Panel(
            display,
            title="[bold magenta]📋 COMMAND CONSOLE[/bold magenta]",
            border_style="bright_magenta",
            box=box.ROUNDED,
            style="on #230032",
        )
        self._suggestions_panel.update(panel)

    def on_input_changed(self, event: Input.Changed) -> None:
        """React to user typing."""
        # Reset history browsing when user types
        self.history_index = None
        self.update_suggestions(event.value)

    def on_input_key(self, event: Input.Key) -> None:
        """Handle history navigation keys."""
        if event.key == "up":
            event.stop()
            self._show_history_previous()
        elif event.key == "down":
            event.stop()
            self._show_history_next()

    def _show_history_previous(self) -> None:
        """Move to previous command in history."""
        if not self.command_history or not self._input:
            return
        if self.history_index is None:
            self.history_index = len(self.command_history) - 1
        else:
            self.history_index = max(0, self.history_index - 1)
        value = self.command_history[self.history_index]
        self._input.value = value
        self._input.cursor_position = len(value)
        self.update_suggestions(value)

    def _show_history_next(self) -> None:
        """Move to next command in history."""
        if not self.command_history or not self._input:
            return
        if self.history_index is None:
            return
        if self.history_index >= len(self.command_history) - 1:
            self.history_index = None
            self._input.value = ""
            self._input.cursor_position = 0
            self.update_suggestions("")
        else:
            self.history_index += 1
            value = self.command_history[self.history_index]
            self._input.value = value
            self._input.cursor_position = len(value)
            self.update_suggestions(value)


class ControlButtonsWidget(Static):
    """Game control action bar with fancy buttons."""

    is_playing: reactive[bool] = reactive(False)
    speed_multiplier: reactive[float] = reactive(1.0)

    def render(self) -> Panel:
        """Render the control buttons in a game-like UI."""
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(justify="center")

        # First row - primary controls
        row1 = Text()
        if self.is_playing:
            row1.append("  ║ ", style="dim cyan")
            row1.append("⏸️  PAUSE", style="bold black on yellow")
            row1.append(" ║  ", style="dim cyan")
        else:
            row1.append("  ║ ", style="dim cyan")
            row1.append("▶️  PLAY", style="bold black on bright_green")
            row1.append(" ║  ", style="dim cyan")

        row1.append("⏩ FAST [", style="bold white on blue")
        row1.append(f"{self.speed_multiplier:.1f}×", style="bold yellow on blue")
        row1.append("]", style="bold white on blue")
        row1.append(" ║  ", style="dim cyan")

        row1.append("💾 SAVE", style="bold black on cyan")
        row1.append(" ║  ", style="dim cyan")
        row1.append("📊 STATS", style="bold white on magenta")
        row1.append(" ║", style="dim cyan")

        # Second row - secondary controls
        row2 = Text()
        row2.append("  ╚════ ", style="dim cyan")
        row2.append("Ctrl+P", style="bold green")
        row2.append("=Play/Pause │ ", style="white")
        row2.append("Ctrl+F", style="bold cyan")
        row2.append("=Fast │ ", style="white")
        row2.append("Ctrl+S", style="bold yellow")
        row2.append("=Save │ ", style="white")
        row2.append("Ctrl+Q", style="bold red")
        row2.append("=Quit ", style="white")
        row2.append("════╝", style="dim cyan")

        grid.add_row(row1)
        grid.add_row(row2)

        return Panel(
            grid,
            title="[bold cyan]⚡ CONTROL DECK ⚡[/bold cyan]",
            border_style="bold bright_cyan",
            box=box.DOUBLE,
            style="on #042030",
        )


class CreatureInspectorWidget(Static):
    """Popup inspector for creature details."""

    def __init__(self, creature_name: str, world: "World", **kwargs) -> None:
        super().__init__(**kwargs)
        self.creature_name = creature_name
        self.world = world

    def render(self) -> Panel:
        """Render the creature inspector."""
        # Find the creature
        creature = None
        for h in self.world.herbivores:
            if h.name == self.creature_name:
                creature = h
                break

        if not creature:
            return Panel("Creature not found", title="Error", border_style="red")

        # Build inspector panel
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Species:", "Herbivore")
        table.add_row("Generation:", str(creature.generation))
        table.add_row("Age:", f"{creature.age} ticks")
        table.add_row("")

        # Health and energy bars
        health_bar = self._status_bar(creature.health, creature.max_health, "❤️ ")
        energy_bar = self._status_bar(creature.energy, creature.max_energy, "⚡")

        table.add_row("Health:", health_bar)
        table.add_row("Energy:", energy_bar)
        table.add_row("Fitness:", f"[yellow]{creature.fitness:.1f}[/yellow]")
        table.add_row("")

        # Lineage
        table.add_row("🌳 Lineage:", "")
        if creature.parents:
            table.add_row("  Parents:", f"{', '.join(creature.parents)}")
        else:
            table.add_row("  Parents:", "[dim]Original[/dim]")
        table.add_row("  Generation:", f"{creature.generation}th")
        table.add_row("")

        # Actions
        table.add_row("[Actions]", "Feed • Heal • Breed • Follow • Close")

        return Panel(
            table,
            title=f"🐰 {creature.name}",
            border_style="green",
            subtitle="Press ESC to close",
        )

    def _status_bar(self, current: float, maximum: float, icon: str = "") -> str:
        """Create a status bar."""
        percentage = (current / maximum) * 100 if maximum > 0 else 0
        filled = int((percentage / 100) * 10)
        bar = "█" * filled + "░" * (10 - filled)

        color = "green" if percentage >= 70 else "yellow" if percentage >= 40 else "red"
        return f"{icon}[{color}]{bar}[/{color}] {current:.0f}/{maximum:.0f}"


class NotificationWidget(Static):
    """Notification popup."""

    def __init__(self, title: str, message: str, notification_type: str = "info", **kwargs) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.message = message
        self.notification_type = notification_type

    def render(self) -> Panel:
        """Render the notification."""
        icon_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "event": "🔔",
        }

        color_map = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "event": "magenta",
        }

        icon = icon_map.get(self.notification_type, "ℹ️")
        color = color_map.get(self.notification_type, "blue")

        text = Text()
        text.append(f"{icon} {self.title}\n\n", style=f"bold {color}")
        text.append(self.message, style="white")

        return Panel(text, border_style=color)


class LiveGraphWidget(Static):
    """Live updating graph widget."""

    world: reactive[Optional["World"]] = reactive(None)

    def __init__(self, world: Optional["World"] = None, graph_type: str = "population", **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = world
        self.graph_type = graph_type

    def render(self) -> Panel:
        """Render a live graph."""
        if not self.world:
            return Panel("Loading...", title="📈 Graph", border_style="yellow")

        # Get data
        data = self.world.stats.get_population_data(last_n=50)
        if not data:
            return Panel("No data yet", title="📈 Population", border_style="yellow")

        # Simple ASCII graph with a neon HUD look
        if self.graph_type == "population":
            herbivore_counts = [d["herbivores"] for d in data]
            plant_counts = [d["plants"] for d in data]

            text = Text()
            text.append("📈 BIOSPHERE TREND\n\n", style="bold cyan")

            spark_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
            max_val = max(max(herbivore_counts, default=1), max(plant_counts, default=1))

            if max_val > 0:
                text.append("🐰 ", style="bold bright_magenta")
                text.append("Herbivores: ", style="cyan")
                for count in herbivore_counts[-30:]:
                    bar_height = int((count / max_val) * 7)
                    text.append(spark_chars[min(bar_height, 7)], style="bright_magenta")
                text.append(f" ({herbivore_counts[-1]})\n", style="bright_magenta")

                text.append("🌱 ", style="bold bright_green")
                text.append("Plants:     ", style="cyan")
                for count in plant_counts[-30:]:
                    bar_height = int((count / max_val) * 7)
                    text.append(spark_chars[min(bar_height, 7)], style="bright_green")
                text.append(f" ({plant_counts[-1]})\n", style="bright_green")

            text.append("\nAuto-refreshing diagnostics", style="dim")

            return Panel(
                text,
                title="[bold yellow]🌿 ECOSYSTEM MONITOR[/bold yellow]",
                border_style="bright_yellow",
                box=box.ROUNDED,
                style="on #1b1405",
            )

        return Panel(
            "Graph type not implemented yet",
            title="[bold yellow]📈 Graph[/bold yellow]",
            border_style="bright_yellow",
            box=box.ROUNDED,
            style="on #1b1405",
        )
