"""Custom Textual widgets for EMERGENCE TUI."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

from rich import box
from rich.cells import cell_len
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from thefuzz import process
from textual import events
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

if TYPE_CHECKING:
    from emergence.entities import Herbivore
    from emergence.world import World

from emergence.analyzer import SuggestionPriority


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

        # Compact single-row grid for space efficiency
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(justify="left", ratio=2)
        grid.add_column(justify="center", ratio=2)
        grid.add_column(justify="right", ratio=2)

        grid.add_row(
            Text.from_markup(f"[bold {status_color}]● {status_label}[/] │ [cyan]Tick[/]: [bold]{tick:,}[/] │ [yellow]🐰[/] [bold]{herbivores}[/] │ [bright_green]🌱[/] [bold]{plants}[/]"),
            Text.from_markup(f"[magenta]Gen[/]: [bold]{generation}[/] │ [blue]Fitness[/]: [bold]{best_fitness:.1f}[/] │ [green]Speed[/]: [bold]{self.speed_multiplier:.1f}×[/]"),
            Text.from_markup("[dim]Neural • RL • Genetic[/dim]"),
        )

        return Panel(
            grid,
            box=box.ROUNDED,
            border_style="cyan",
            title="[bold cyan]EMERGENCE PROTOCOL[/bold cyan]",
            subtitle=None,
            style="on #050a14",
            padding=(0, 1),
        )


class WorldViewWidget(Static):
    """Animated world view showing creatures and environment."""

    class CreatureSelected(Message):
        """Posted when a creature is clicked."""

        def __init__(self, creature_name: str, creature: "Herbivore") -> None:
            super().__init__()
            self.creature_name = creature_name
            self.creature = creature

    world: reactive[Optional["World"]] = reactive(None)
    selected_creature: reactive[Optional[str]] = reactive(None)
    hovered_creature: reactive[Optional[str]] = reactive(None)

    def __init__(self, world: Optional["World"] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = world
        self.viewport_width = 60
        self.viewport_height = 20
        # Performance optimization: cache render state
        self.last_render_tick: int = 0
        self.render_cache: Optional[Panel] = None

    def render(self) -> Panel:
        """Render the world view with caching for performance."""
        if not self.world:
            content = Text("Loading ecosystem...", style="dim cyan", justify="center")
            return Panel(content, box=box.SIMPLE)

        # Performance optimization: return cached render if tick hasn't changed
        # This prevents re-rendering the same state multiple times
        current_tick = self.world.tick_count
        self._fit_viewport()
        if self.render_cache and current_tick == self.last_render_tick:
            return self.render_cache

        self.last_render_tick = current_tick

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
        # Every grid cell is 2 terminal columns: emoji are double-width, so pad 1-wide glyphs to keep rows aligned.
        text = Text()
        for row in grid:
            for char in row:
                if cell_len(char) == 1:
                    char += " "
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
                elif char == "· ":
                    text.append(char, style="dim white")
                else:
                    text.append(char)
            text.append("\n")

        # Add game-like footer with instructions
        text.append("\n")
        text.append("═" * (self.viewport_width * self.CELL_W), style="dim cyan")
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

        # Add selection indicator if creature is selected
        if self.selected_creature and self.world:
            creature = self._find_creature(self.selected_creature)
            if creature:
                text.append(f"\n✨ Selected: {self.selected_creature} (Energy: {creature.energy:.0f}, Health: {creature.health:.0f})", style="bold yellow")

        subtitle_text = f"[bold cyan]⏱ Tick: {self.world.tick_count:,}[/bold cyan] │ [yellow]🌍 Size: {self.world.config.width:.0f}x{self.world.config.height:.0f}[/yellow]"

        if self.hovered_creature:
            subtitle_text += f" │ [dim yellow]Hover: {self.hovered_creature}[/dim yellow]"

        # Left-aligned (no Align.center) so _cell_at can map mouse offsets back to grid cells exactly.
        self.render_cache = Panel(
            text,
            title=None, 
            subtitle=subtitle_text,
            box=box.SIMPLE,  # invisible border; real borders handled by CSS
        )
        return self.render_cache

    def _find_creature(self, name: str) -> Optional["Herbivore"]:
        """Find a herbivore by name."""
        if not self.world:
            return None
        for herbivore in self.world.herbivores:
            if herbivore.name == name and herbivore.alive:
                return herbivore
        return None

    # Layout constants for the Rich Panel(box=SIMPLE) drawn in render():
    CELL_W = 2          # terminal columns per grid cell (emoji are double-width)
    PAD_X = 2           # left border + panel padding
    PAD_Y = 1           # top border
    CHROME_ROWS = 6     # top/bottom border + blank, rule, controls, selected line

    def _fit_viewport(self) -> None:
        """Size the grid to the widget so the whole panel is used."""
        w, h = self.content_size
        if w <= 0 or h <= 0:
            return  # not laid out yet; keep the defaults
        vw = max(10, (w - 2 * self.PAD_X) // self.CELL_W)
        vh = max(5, h - self.CHROME_ROWS)
        if (vw, vh) != (self.viewport_width, self.viewport_height):
            self.viewport_width, self.viewport_height = vw, vh
            self.render_cache = None

    def _cell_at(self, event: events.MouseEvent) -> Optional[tuple]:
        """Grid cell under the mouse, or None outside the grid."""
        offset = event.get_content_offset(self)
        if offset is None:
            return None
        cx, cy = (offset.x - self.PAD_X) // self.CELL_W, offset.y - self.PAD_Y
        if 0 <= cx < self.viewport_width and 0 <= cy < self.viewport_height:
            return cx, cy
        return None

    def _find_creature_at_position(self, viewport_x: int, viewport_y: int) -> Optional["Herbivore"]:
        """Find a creature at given viewport coordinates."""
        if not self.world:
            return None

        # Convert viewport coordinates to world coordinates
        scale_x = self.viewport_width / self.world.config.width
        scale_y = self.viewport_height / self.world.config.height

        # Check each herbivore
        for herbivore in self.world.herbivores:
            if not herbivore.alive:
                continue

            creature_x = int(herbivore.position[0] * scale_x)
            creature_y = int(herbivore.position[1] * scale_y)

            # Check if click is within creature position (with small tolerance)
            if abs(creature_x - viewport_x) <= 1 and abs(creature_y - viewport_y) <= 1:
                return herbivore

        return None

    def on_click(self, event: events.Click) -> None:
        """Handle mouse click on world view."""
        if not self.world:
            return

        cell = self._cell_at(event)
        creature = self._find_creature_at_position(*cell) if cell else None
        self.render_cache = None  # selection line changes without a tick

        if creature:
            self.selected_creature = creature.name
            # Post message to parent screen
            self.post_message(self.CreatureSelected(creature.name, creature))
            self.refresh()
        else:
            # Clicked empty space - deselect
            self.selected_creature = None
            self.refresh()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Handle mouse hover to show creature info."""
        if not self.world:
            return

        cell = self._cell_at(event)
        creature = self._find_creature_at_position(*cell) if cell else None
        name = creature.name if creature else None
        if name != self.hovered_creature:
            self.hovered_creature = name
            self.render_cache = None  # hover subtitle changes without a tick
            self.refresh()


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

        types_alive = len(self.world.brain_type_counts())
        grid.add_row(Text.from_markup("[cyan]🧠 Brain[/]"), Text(f"{self.world.config.brain_type} ({types_alive} types alive)"))
        if self.world.config.disease_enabled:
            grid.add_row(Text.from_markup("[red]🦠 Infected[/]"), Text(str(self.world.infected_count())))

        return Panel(
            grid,
            title=None,
            box=box.SIMPLE,
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
            "brain",
            "compare_brains",
            "disease",
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


class ControlButtonsWidget(Container):
    """Game control action bar with real clickable buttons."""

    class ButtonPressed(Message):
        """Posted when a control button is pressed."""

        def __init__(self, action: str) -> None:
            super().__init__()
            self.action = action

    is_playing: reactive[bool] = reactive(False)
    speed_multiplier: reactive[float] = reactive(1.0)

    def compose(self) -> ComposeResult:
        """Compose the control buttons."""
        with Horizontal(id="control_buttons_container"):
            play_btn = Button("▶️  Play", id="btn_play", variant="success")
            play_btn.tooltip = "Start real-time simulation (Ctrl+P)"
            yield play_btn

            pause_btn = Button("⏸️  Pause", id="btn_pause", variant="warning")
            pause_btn.tooltip = "Pause simulation (Ctrl+P)"
            yield pause_btn

            fast_btn = Button("⏩ Fast", id="btn_fast", variant="primary")
            fast_btn.tooltip = "Increase speed multiplier (Ctrl+F)"
            yield fast_btn

            save_btn = Button("💾 Save", id="btn_save")
            save_btn.tooltip = "Quick save to emergence_autosave.json (Ctrl+S)"
            yield save_btn

            stats_btn = Button("📊 Stats", id="btn_stats")
            stats_btn.tooltip = "Show ecosystem statistics"
            yield stats_btn

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id

        if button_id == "btn_play":
            self.post_message(self.ButtonPressed("play"))
        elif button_id == "btn_pause":
            self.post_message(self.ButtonPressed("pause"))
        elif button_id == "btn_fast":
            self.post_message(self.ButtonPressed("fast_forward"))
        elif button_id == "btn_save":
            self.post_message(self.ButtonPressed("save"))
        elif button_id == "btn_stats":
            self.post_message(self.ButtonPressed("stats"))

    def watch_is_playing(self, is_playing: bool) -> None:
        """Update button states when play state changes."""
        try:
            play_btn = self.query_one("#btn_play", Button)
            pause_btn = self.query_one("#btn_pause", Button)

            if is_playing:
                play_btn.disabled = True
                pause_btn.disabled = False
            else:
                play_btn.disabled = False
                pause_btn.disabled = True
        except Exception:
            pass


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


class CreatureContextMenu(Container):
    """Context menu popup for creature actions."""

    class ActionSelected(Message):
        """Posted when an action is selected from the menu."""

        def __init__(self, action: str, creature_name: str) -> None:
            super().__init__()
            self.action = action
            self.creature_name = creature_name

    def __init__(self, creature_name: str, creature: "Herbivore", **kwargs) -> None:
        super().__init__(**kwargs)
        self.creature_name = creature_name
        self.creature = creature

    def compose(self) -> ComposeResult:
        """Compose the context menu with action buttons."""
        with Vertical(id="context_menu_panel"):
            # Creature info header
            yield Static(
                f"🐰 {self.creature_name}\n"
                f"Energy: {self.creature.energy:.0f} │ Health: {self.creature.health:.0f}\n"
                f"Fitness: {self.creature.fitness:.0f} │ Age: {self.creature.age:.0f}",
                id="creature_info_header"
            )

            # Action buttons
            with Vertical(id="action_buttons"):
                feed_btn = Button("🍖 Feed (+30 energy)", id="btn_feed", variant="success")
                feed_btn.tooltip = "Restore 30 energy points to this creature"
                yield feed_btn

                heal_btn = Button("❤️ Heal (+40 health)", id="btn_heal", variant="success")
                heal_btn.tooltip = "Restore 40 health points to this creature"
                yield heal_btn

                observe_btn = Button("👁️ Observe (details)", id="btn_observe", variant="primary")
                observe_btn.tooltip = "View detailed stats and brain information"
                yield observe_btn

                teach_btn = Button("📚 Teach (guide)", id="btn_teach")
                teach_btn.tooltip = "Guide learning with reinforcement signal"
                yield teach_btn

                reward_btn = Button("💝 Reward (reinforce)", id="btn_reward")
                reward_btn.tooltip = "Reinforce current behavior positively"
                yield reward_btn

                punish_btn = Button("⚠️ Punish (discourage)", id="btn_punish", variant="warning")
                punish_btn.tooltip = "Discourage current behavior (negative signal)"
                yield punish_btn

                breed_btn = Button("🧬 Breed with...", id="btn_breed")
                breed_btn.tooltip = "Select this creature for breeding"
                yield breed_btn

                close_btn = Button("❌ Close", id="btn_close", variant="error")
                close_btn.tooltip = "Close this menu (ESC)"
                yield close_btn

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks in context menu."""
        button_id = event.button.id

        if button_id == "btn_close":
            # Just remove the menu
            self.remove()
            return

        # Map button IDs to action names
        action_map = {
            "btn_feed": "feed",
            "btn_heal": "heal",
            "btn_observe": "observe",
            "btn_teach": "teach",
            "btn_reward": "reward",
            "btn_punish": "punish",
            "btn_breed": "breed",
        }

        action = action_map.get(button_id)
        if action:
            self.post_message(self.ActionSelected(action, self.creature_name))
            self.remove()  # Close menu after selection


class SmartSuggestionsWidget(Container):
    """Proactive guidance system that suggests contextual actions."""

    class SuggestionClicked(Message):
        """Posted when a suggestion is clicked."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    world: reactive[Optional["World"]] = reactive(None)

    def __init__(self, world: Optional["World"] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = world
        self.last_update_tick: int = 0
        self.update_interval: int = 10  # Update every 10 ticks
        self.current_suggestions = []

        # Import analyzer here to avoid circular imports
        from emergence.analyzer import GameStateAnalyzer
        self.analyzer = GameStateAnalyzer()

    def compose(self) -> ComposeResult:
        """Compose the suggestions panel."""
        with Vertical(id="suggestions_panel"):
            yield Static("🧠 SMART SUGGESTIONS", id="suggestions_title")
            yield Static(id="suggestions_content")

    def on_mount(self) -> None:
        """Update suggestions when mounted."""
        self.set_interval(1.0, self._update_suggestions)

    def _update_suggestions(self) -> None:
        """Periodically update suggestions."""
        if not self.world:
            return

        current_tick = self.world.tick_count
        if current_tick - self.last_update_tick < self.update_interval:
            return

        self.last_update_tick = current_tick

        # Get suggestions from analyzer
        self.current_suggestions = self.analyzer.get_all_suggestions(self.world)
        self._render_suggestions()

    def _render_suggestions(self) -> None:
        """Render suggestions as text with clickable commands."""
        try:
            content_widget = self.query_one("#suggestions_content", Static)
        except Exception:
            return

        if not self.current_suggestions:
            content = Text("✨ All systems optimal!", style="green")
            content_widget.update(content)
            return

        content = Text()
        for i, suggestion in enumerate(self.current_suggestions):
            # Color coding based on priority
            if suggestion.priority == SuggestionPriority.CRITICAL:
                priority_style = "bold red"
            elif suggestion.priority == SuggestionPriority.WARNING:
                priority_style = "bold yellow"
            elif suggestion.priority == SuggestionPriority.INFO:
                priority_style = "bold blue"
            else:  # TIP
                priority_style = "bold green"

            # Icon and title
            content.append(f"{suggestion.icon} ", style=priority_style)
            content.append(f"{suggestion.title.upper()}: ", style=priority_style)
            content.append(f"{suggestion.description}\n", style="white")

            # Command hint if available - make it look clickable
            if suggestion.command:
                content.append(f"  → ", style="dim cyan")
                content.append(f"{suggestion.command}", style="cyan underline")
                content.append(f" (clickable)\n", style="dim")

            # Add spacing between suggestions (except last)
            if i < len(self.current_suggestions) - 1:
                content.append("\n")

        content_widget.update(content)

    def on_click(self, event) -> None:
        """Handle clicks on suggestions."""
        # For now, just show that suggestions exist
        # In a full implementation, we'd detect which suggestion was clicked
        if self.current_suggestions and self.current_suggestions[0].command:
            # Post message with first suggestion's command
            self.post_message(self.SuggestionClicked(self.current_suggestions[0].command))


class CommandBrowserWidget(Container):
    """F1 command discovery overlay with search functionality."""

    class CommandSelected(Message):
        """Posted when a command is selected from the browser."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    def __init__(self, available_commands: list, **kwargs) -> None:
        super().__init__(**kwargs)
        self.available_commands = available_commands
        self.all_commands = self._build_command_catalog()
        self.filtered_commands = self.all_commands

    def _build_command_catalog(self) -> dict:
        """Build complete command catalog with metadata."""
        return {
            "core": [
                ("help", "Show all commands and usage"),
                ("create", "Spawn plant or herbivore - create [species] [name]"),
                ("observe", "Inspect creature stats - observe [name]"),
                ("simulate", "Run headless simulation - simulate [ticks]"),
                ("view", "Watch simulation - view [ticks]"),
                ("stats", "Show ecosystem statistics"),
                ("population", "List all living creatures"),
                ("play", "Start simulation"),
                ("pause", "Pause simulation"),
                ("dashboard", "Show main statistics panel"),
                ("graph", "Display charts - graph [population|fitness|age|energy]"),
                ("heatmap", "Show heatmaps - heatmap [births|deaths|food]"),
                ("quit", "Exit the game"),
                ("exit", "Exit the game"),
            ],
            "creature_interaction": [
                ("feed", "Restore creature energy (+30) - feed [name]"),
                ("heal", "Restore creature health (+40) - heal [name]"),
                ("reward", "Reinforce learning - reward [name] [amount]"),
                ("punish", "Discourage behavior - punish [name] [amount]"),
                ("teach", "Guide learning - teach [name] [strength]"),
                ("breed", "Force reproduction - breed [name1] [name2]"),
                ("show_brain", "Display neural network - show_brain [name]"),
                ("show_lineage", "Show ancestry - show_lineage [name]"),
                ("family_tree", "Display family tree - family_tree [name] [depth]"),
                ("follow", "Highlight a creature - follow [name]"),
                ("brain", "Show/set brain type for new spawns - brain [type]"),
                ("compare_brains", "Compare brain types by fitness and lifespan"),
                ("disease", "Toggle the immune system mechanic - disease on/off"),
            ],
            "visualization": [
                ("timeline", "Show evolution timeline"),
                ("learning_curve", "Display learning progress - learning_curve [name]"),
                ("compare_species", "Compare species statistics"),
                ("events", "Show recent events - events [count] [type]"),
                ("top", "Show top performers - top [count]"),
            ],
            "persistence": [
                ("save", "Save world state - save [filename]"),
                ("load", "Load world state - load [filename]"),
                ("snapshot", "Create snapshot - snapshot [name]"),
                ("export_stats", "Export statistics - export_stats [filename]"),
            ],
            "controls": [
                ("speed", "Set simulation speed - speed [multiplier]"),
                ("auto_mode", "Toggle resource spawning - auto_mode [on|off]"),
            ],
            "gameplay": [
                ("start_mode", "Start game mode - start_mode [survival|challenge|sandbox|speedrun]"),
                ("gameplay", "Show gameplay status"),
                ("unlock", "Purchase unlock - unlock [name]"),
                ("achievements", "View achievements"),
            ],
        }

    def compose(self) -> ComposeResult:
        """Compose the command browser overlay."""
        with Vertical(id="browser_panel"):
            yield Static(
                "🔍 COMMAND BROWSER - Press F1 or ESC to Close",
                id="browser_title"
            )

            search_input = Input(
                placeholder="Search commands (type to filter)...",
                id="cmd_search"
            )
            search_input.tooltip = "Type to search commands with fuzzy matching"
            yield search_input

            with Vertical(id="cmd_list"):
                yield Static(self._render_command_list(), id="cmd_results")

            close_btn = Button("❌ Close", id="btn_browser_close", variant="error")
            close_btn.tooltip = "Close command browser (F1 or ESC)"
            yield close_btn

    def on_mount(self) -> None:
        """Focus search box when mounted."""
        try:
            search_input = self.query_one("#cmd_search", Input)
            search_input.focus()
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id != "cmd_search":
            return

        query = event.value.strip().lower()

        if query:
            # Fuzzy search through all commands
            all_cmd_names = []
            for category_cmds in self.all_commands.values():
                all_cmd_names.extend([cmd[0] for cmd in category_cmds])

            # Use thefuzz for fuzzy matching
            matches = process.extract(query, all_cmd_names, limit=15)
            matched_names = [cmd for cmd, score in matches if score >= 50]

            # Filter catalog to only matched commands
            self.filtered_commands = {}
            for category, commands in self.all_commands.items():
                filtered = [cmd for cmd in commands if cmd[0] in matched_names]
                if filtered:
                    self.filtered_commands[category] = filtered
        else:
            self.filtered_commands = self.all_commands

        # Update display
        try:
            results = self.query_one("#cmd_results", Static)
            results.update(self._render_command_list())
        except Exception:
            pass

    def _render_command_list(self) -> Text:
        """Render the filtered command list."""
        content = Text()

        # Count total commands
        total = sum(len(cmds) for cmds in self.filtered_commands.values())

        if total == 0:
            content.append("\n  No commands found.\n", style="dim")
            content.append("  Try a different search term.", style="dim")
            return content

        content.append(f"\n  {total} command(s) found\n\n", style="dim cyan")

        # Category icons and names
        category_display = {
            "core": ("📚", "CORE COMMANDS"),
            "creature_interaction": ("🎯", "CREATURE INTERACTION"),
            "visualization": ("📊", "VISUALIZATION & ANALYSIS"),
            "persistence": ("💾", "PERSISTENCE & DATA"),
            "controls": ("⚙️", "CONTROL & SETTINGS"),
            "gameplay": ("🎮", "GAMEPLAY SYSTEM"),
        }

        for category, commands in self.filtered_commands.items():
            if not commands:
                continue

            icon, name = category_display.get(category, ("", category.upper()))
            content.append(f"  {icon} {name}\n", style="bold cyan")

            for cmd_name, cmd_desc in commands:
                content.append(f"    → ", style="dim cyan")
                content.append(f"{cmd_name}", style="bold green")
                content.append(f"  {cmd_desc}\n", style="white")

            content.append("\n")

        return content

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn_browser_close":
            self.remove()

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape" or event.key == "f1":
            self.remove()
            event.prevent_default()
            event.stop()


class KeyboardShortcutsWidget(Container):
    """F2 keyboard shortcuts reference overlay."""

    def compose(self) -> ComposeResult:
        """Compose the shortcuts panel."""
        with Vertical(id="shortcuts_panel"):
            yield Static("⌨️  KEYBOARD SHORTCUTS", id="shortcuts_title")
            yield Static(id="shortcuts_content")

            close_btn = Button("Close (ESC / F2)", id="btn_shortcuts_close", variant="primary")
            close_btn.tooltip = "Close this shortcuts panel"
            yield close_btn

    def on_mount(self) -> None:
        """Populate shortcuts when mounted."""
        self._render_shortcuts()

    def _render_shortcuts(self) -> None:
        """Render the keyboard shortcuts reference."""
        try:
            content_widget = self.query_one("#shortcuts_content", Static)
        except Exception:
            return

        content = Text()

        shortcuts = {
            "🎮 Simulation Control": [
                ("Ctrl+P", "Play / Pause simulation"),
                ("Ctrl+F", "Fast forward (2x speed)"),
                ("Space", "Single step (when paused)"),
            ],
            "🗂️ Navigation": [
                ("F1", "Open command browser"),
                ("F2", "Show keyboard shortcuts (this panel)"),
                ("Ctrl+D", "Switch to dashboard view"),
                ("Tab", "Focus command input"),
            ],
            "💾 File Operations": [
                ("Ctrl+S", "Quick save game"),
                ("Ctrl+L", "Load saved game"),
            ],
            "🎯 Command Input": [
                ("Enter", "Execute command"),
                ("Tab", "Autocomplete command"),
                ("Escape", "Clear command input"),
                ("↑ / ↓", "Browse command history"),
            ],
            "🐰 Creature Interaction": [
                ("Click", "Select creature (opens context menu)"),
                ("Right Click", "Quick observe creature"),
            ],
            "⚙️ System": [
                ("Ctrl+Q", "Quit application"),
                ("Ctrl+C", "Force quit"),
            ],
        }

        for category, shortcuts_list in shortcuts.items():
            content.append(f"\n{category}\n", style="bold cyan")
            content.append("─" * 60, style="dim cyan")
            content.append("\n")

            for key, description in shortcuts_list:
                content.append(f"  ", style="dim")
                content.append(f"{key:15}", style="bold green")
                content.append(f" → {description}\n", style="white")

        content.append("\n")
        content.append("💡 Tip: ", style="bold yellow")
        content.append("Hover over any button for context-specific help!\n", style="dim white")

        content_widget.update(content)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn_shortcuts_close":
            self.remove()

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape" or event.key == "f2":
            self.remove()
            event.prevent_default()
            event.stop()


class DetailedCreaturePanel(Container):
    """Collapsible detailed creature information panel."""

    creature_name: reactive[Optional[str]] = reactive(None)
    world: reactive[Optional["World"]] = reactive(None)
    is_expanded: reactive[bool] = reactive(True)

    def __init__(self, world: Optional["World"] = None, creature_name: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.world = world
        self.creature_name = creature_name

    def compose(self) -> ComposeResult:
        """Compose the detailed panel."""
        with Vertical(id="detailed_creature_panel"):
            toggle_btn = Button("◀ Collapse", id="btn_toggle_sidebar", variant="primary")
            toggle_btn.tooltip = "Collapse/Expand creature details sidebar"
            yield toggle_btn
            yield Static(id="creature_details_content")

    def on_mount(self) -> None:
        """Update when mounted."""
        self._update_details()

    def watch_creature_name(self, new_name: Optional[str]) -> None:
        """Watch for creature name changes."""
        self._update_details()

    def _update_details(self) -> None:
        """Update the detailed creature information."""
        try:
            content_widget = self.query_one("#creature_details_content", Static)
        except Exception:
            return

        if not self.world or not self.creature_name:
            content = Text("No creature selected", style="dim")
            content_widget.update(content)
            return

        # Find the creature
        creature = None
        for h in self.world.herbivores:
            if h.name == self.creature_name and h.alive:
                creature = h
                break

        if not creature:
            content = Text(f"Creature '{self.creature_name}' not found", style="dim red")
            content_widget.update(content)
            return

        # Build detailed info
        content = Text()
        content.append(f"🐰 {creature.name}\n", style="bold green")
        content.append("─" * 30, style="dim")
        content.append("\n\n")

        # Core stats
        content.append("📊 Core Stats\n", style="bold cyan")
        content.append(f"Generation: ", style="white")
        content.append(f"{creature.generation}\n", style="bold yellow")
        content.append(f"Age: ", style="white")
        content.append(f"{creature.age:.0f} ticks\n", style="bold")
        content.append(f"Fitness: ", style="white")
        content.append(f"{creature.fitness:.1f}\n\n", style="bold green")

        # Health & Energy bars
        content.append("💪 Vitals\n", style="bold cyan")
        health_pct = (creature.health / creature.max_health) * 100
        energy_pct = (creature.energy / creature.max_energy) * 100

        health_color = "green" if health_pct >= 70 else "yellow" if health_pct >= 40 else "red"
        energy_color = "green" if energy_pct >= 70 else "yellow" if energy_pct >= 40 else "red"

        content.append(f"❤️  Health: ", style="white")
        content.append(f"{creature.health:.0f}/{creature.max_health:.0f} ", style=health_color)
        content.append(f"({health_pct:.0f}%)\n", style="dim")

        content.append(f"⚡ Energy: ", style="white")
        content.append(f"{creature.energy:.0f}/{creature.max_energy:.0f} ", style=energy_color)
        content.append(f"({energy_pct:.0f}%)\n\n", style="dim")

        # Neural network info
        content.append("🧠 Neural Network\n", style="bold cyan")
        if hasattr(creature, 'brain') and creature.brain:
            try:
                layers = creature.brain.layers if hasattr(creature.brain, 'layers') else []
                content.append(f"Type: {creature.brain_type}  Layers: {len(layers) or 'graph'}\n", style="white")
            except:
                content.append(f"Architecture: Hidden layers\n", style="dim")
        else:
            content.append("No brain data\n", style="dim")
        content.append("\n")

        # Lineage
        content.append("🌳 Lineage\n", style="bold cyan")
        if creature.parents:
            content.append(f"Parents: ", style="white")
            content.append(f"{', '.join(creature.parents[:2])}\n", style="yellow")
        else:
            content.append(f"Parents: Original\n", style="dim")

        if hasattr(creature, 'children_count'):
            content.append(f"Children: {creature.children_count}\n", style="white")
        content.append("\n")

        # Quick actions hint
        content.append("💡 Tip: ", style="bold yellow")
        content.append("Click creature in world view\nfor action menu", style="dim white")

        content_widget.update(content)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle toggle button."""
        if event.button.id == "btn_toggle_sidebar":
            self.is_expanded = not self.is_expanded
            self.post_message(self.SidebarToggled(self.is_expanded))
            # Update button text
            event.button.label = "▶ Expand" if not self.is_expanded else "◀ Collapse"

    class SidebarToggled(Message):
        """Posted when sidebar is toggled."""
        def __init__(self, is_expanded: bool) -> None:
            super().__init__()
            self.is_expanded = is_expanded


class WelcomeTutorialWidget(Container):
    """First-time user tutorial overlay with step-by-step guide."""

    current_step: reactive[int] = reactive(0)
    total_steps: int = 5

    def compose(self) -> ComposeResult:
        """Compose the tutorial overlay."""
        with Vertical(id="tutorial_overlay"):
            yield Static("🎓 Welcome to EMERGENCE", id="tutorial_title")
            yield Static(id="tutorial_content")

            with Horizontal(id="tutorial_buttons"):
                skip_btn = Button("Skip Tutorial", id="btn_skip_tutorial", variant="default")
                skip_btn.tooltip = "Skip the tutorial and start playing"
                yield skip_btn

                prev_btn = Button("◀ Previous", id="btn_prev_step", variant="default")
                prev_btn.tooltip = "Go to previous step"
                yield prev_btn

                next_btn = Button("Next ▶", id="btn_next_step", variant="primary")
                next_btn.tooltip = "Go to next step"
                yield next_btn

    def on_mount(self) -> None:
        """Initialize the tutorial."""
        self._update_content()

    def watch_current_step(self, new_step: int) -> None:
        """Watch for step changes."""
        self._update_content()

    def _update_content(self) -> None:
        """Update the tutorial content based on current step."""
        content_widget = self.query_one("#tutorial_content", Static)

        steps = [
            {
                "title": "🌍 What is EMERGENCE?",
                "content": [
                    "EMERGENCE is a neural evolution simulator where creatures learn",
                    "to survive through reinforcement learning and genetic algorithms.",
                    "",
                    "🐰 Herbivores have neural networks that evolve over generations",
                    "🌱 Plants provide food and regrow automatically",
                    "🧬 Genetics and learning combine to create emergent behavior",
                    "",
                    "Watch as simple creatures develop complex survival strategies!",
                ]
            },
            {
                "title": "🎮 Basic Controls",
                "content": [
                    "Control the simulation with these keyboard shortcuts:",
                    "",
                    "  Ctrl+P  → Play / Pause the simulation",
                    "  Ctrl+F  → Fast forward (2× speed)",
                    "  Space   → Step forward one tick (when paused)",
                    "  F1      → Open command browser",
                    "  F2      → Show all keyboard shortcuts",
                    "",
                    "You can also use the control buttons at the top!",
                ]
            },
            {
                "title": "💬 Command System",
                "content": [
                    "Type commands in the input field at the bottom:",
                    "",
                    "  create herbivore  → Add a new creature",
                    "  create plant      → Add a food source",
                    "  feed <name>       → Give energy to a creature",
                    "  breed <a> <b>     → Breed two creatures",
                    "  observe <name>    → Get detailed creature info",
                    "  auto_mode on      → Auto-spawn plants",
                    "",
                    "Press Tab for autocomplete, or F1 to browse all commands!",
                ]
            },
            {
                "title": "🎯 Smart Suggestions",
                "content": [
                    "The right sidebar shows AI-powered suggestions based on",
                    "the current state of your simulation:",
                    "",
                    "  ⚠️  Critical alerts (starvation, health issues)",
                    "  🔋  Energy and resource warnings",
                    "  🧬  Breeding opportunities",
                    "  🏆  Milestones and achievements",
                    "  📚  Teaching and learning tips",
                    "",
                    "Click on suggestions to execute them instantly!",
                ]
            },
            {
                "title": "🚀 Ready to Begin!",
                "content": [
                    "You're all set to start your evolution experiment!",
                    "",
                    "Quick tips:",
                    "  • Click creatures in the world view for detailed stats",
                    "  • Monitor the graphs to track population trends",
                    "  • Use auto_mode to maintain a stable ecosystem",
                    "  • Experiment with breeding high-fitness creatures",
                    "  • Save your simulation anytime with Ctrl+S",
                    "",
                    "Press 'Start Playing' to close this tutorial and begin!",
                ]
            },
        ]

        step_data = steps[self.current_step]

        content = Text()
        content.append(f"{step_data['title']}\n", style="bold cyan")
        content.append("─" * 60, style="dim")
        content.append("\n\n")

        for line in step_data["content"]:
            content.append(line + "\n")

        content.append("\n")
        content.append("─" * 60, style="dim")
        content.append(f"\nStep {self.current_step + 1} of {self.total_steps}", style="dim italic")

        content_widget.update(content)

        # Update button states
        try:
            prev_btn = self.query_one("#btn_prev_step", Button)
            next_btn = self.query_one("#btn_next_step", Button)

            prev_btn.disabled = (self.current_step == 0)

            if self.current_step == self.total_steps - 1:
                next_btn.label = "Start Playing!"
                next_btn.variant = "success"
            else:
                next_btn.label = "Next ▶"
                next_btn.variant = "primary"
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn_skip_tutorial":
            self.post_message(self.TutorialClosed())
            self.remove()
        elif event.button.id == "btn_prev_step":
            if self.current_step > 0:
                self.current_step -= 1
        elif event.button.id == "btn_next_step":
            if self.current_step < self.total_steps - 1:
                self.current_step += 1
            else:
                # Final step - close tutorial
                self.post_message(self.TutorialClosed())
                self.remove()

    class TutorialClosed(Message):
        """Posted when tutorial is closed."""
        pass
