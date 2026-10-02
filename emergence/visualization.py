import math
from typing import List, Optional, Tuple

import numpy as np
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from emergence.entities import Herbivore, Plant
from emergence.world import World


class Visualizer:
    """Rich-based colorful CLI visualization for the world."""

    def __init__(self, world: World, viewport_size: Tuple[int, int] = (50, 30)):
        self.world = world
        self.viewport_width, self.viewport_height = viewport_size
        self.focus_position: Optional[np.ndarray] = None
        self.follow_target: Optional[str] = None
        self.console = Console()

    def render(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=8),
        )
        layout["header"].update(self._render_header())
        layout["main"].split_row(Layout(self._render_world(), name="world"), Layout(self._render_sidebar(), name="sidebar", ratio=1))
        layout["footer"].update(self._render_footer())
        return layout

    def _render_header(self) -> Panel:
        title = Text("EMERGENCE - AI Ecosystem Simulator", style="bold cyan", justify="center")
        subtitle = Text(f"Tick: {self.world.tick_count} | Neural Networks + Reinforcement Learning + Genetic Evolution", justify="center")
        content = Text.assemble(title, "\n", subtitle)
        return Panel(content, style="cyan")

    def _render_world(self) -> Panel:
        if self.follow_target:
            creature = self._find_creature(self.follow_target)
            if creature:
                self.focus_position = creature.position.copy()

        if self.focus_position is None:
            # Default center view
            self.focus_position = np.array([self.world.config.width / 2, self.world.config.height / 2])

        viewport = self._create_viewport()
        return Panel(viewport, title="World View", border_style="green")

    def _create_viewport(self) -> Text:
        # Map continuous world to discrete viewport
        grid = [[" " for _ in range(self.viewport_width)] for _ in range(self.viewport_height)]

        for plant in self.world.plants:
            if not plant.alive:
                continue
            x, y = self._world_to_viewport(plant.position)
            if 0 <= x < self.viewport_width and 0 <= y < self.viewport_height:
                grid[y][x] = self._plant_char(plant)

        for herbivore in self.world.herbivores:
            if not herbivore.alive:
                continue
            x, y = self._world_to_viewport(herbivore.position)
            if 0 <= x < self.viewport_width and 0 <= y < self.viewport_height:
                # The whole world is always in view, so "follow" highlights the creature instead of panning.
                grid[y][x] = "@" if herbivore.name == self.follow_target else self._herbivore_char(herbivore)

        text = Text()
        for row in grid:
            for char in row:
                if char == "@":
                    text.append(char, style="bold yellow")
                elif char == "H":
                    text.append(char, style="bold red")
                elif char == "h":
                    text.append(char, style="red")
                elif char == "P":
                    text.append(char, style="bold green")
                elif char == "p":
                    text.append(char, style="green")
                elif char == ".":
                    text.append(char, style="dim green")
                else:
                    text.append(char, style="dim")
            text.append("\n")
        return text

    def _world_to_viewport(self, position: np.ndarray) -> Tuple[int, int]:
        scale_x = self.viewport_width / self.world.config.width
        scale_y = self.viewport_height / self.world.config.height
        x = int(position[0] * scale_x)
        y = int(position[1] * scale_y)
        return x, y

    def _plant_char(self, plant: Plant) -> str:
        if plant.growth_stage >= 4.0:
            return "P"
        elif plant.growth_stage >= 2.0:
            return "p"
        return "."

    def _herbivore_char(self, herbivore: Herbivore) -> str:
        if herbivore.energy >= 70:
            return "H"
        return "h"

    def _render_sidebar(self) -> Panel:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        pop = self.world.population_summary()
        table.add_row("Plants", str(pop["plants"]))
        table.add_row("Herbivores", str(pop["herbivores"]))

        metrics = self.world.ecosystem_metrics()
        table.add_row("", "")
        table.add_row("Avg Energy", f"{metrics['avg_energy']:.1f}")
        table.add_row("Avg Fitness", f"{metrics['avg_fitness']:.1f}")

        if self.world.herbivores:
            best = max(self.world.herbivores, key=lambda h: h.fitness)
            table.add_row("", "")
            table.add_row("Top Creature", best.name)
            table.add_row("  Fitness", f"{best.fitness:.1f}")
            table.add_row("  Generation", str(best.generation))

        return Panel(table, title="Statistics", border_style="yellow")

    def _render_footer(self) -> Panel:
        herbivore_table = Table(title="Living Herbivores", show_header=True, box=None)
        herbivore_table.add_column("Name", style="cyan")
        herbivore_table.add_column("Energy", style="yellow")
        herbivore_table.add_column("Health", style="green")
        herbivore_table.add_column("Age", style="magenta")
        herbivore_table.add_column("Fitness", style="blue")
        herbivore_table.add_column("Gen", style="white")

        for herbivore in sorted(self.world.herbivores, key=lambda h: h.fitness, reverse=True)[:5]:
            herbivore_table.add_row(
                herbivore.name[:15],
                f"{herbivore.energy:.0f}",
                f"{herbivore.health:.0f}",
                f"{herbivore.age:.0f}",
                f"{herbivore.fitness:.1f}",
                str(herbivore.generation),
            )

        return Panel(herbivore_table, border_style="blue")

    def _find_creature(self, name: str) -> Optional[Herbivore]:
        for herbivore in self.world.herbivores:
            if herbivore.name == name:
                return herbivore
        return None

    def print_brain(self, name: str) -> None:
        creature = self._find_creature(name)
        if not creature:
            self.console.print(f"[red]Creature {name} not found[/red]")
            return
        brain = creature.agent.brain
        from emergence.brains import GraphBrain

        if isinstance(brain, GraphBrain):
            self._print_graph_brain(name, brain)
            return

        text = Text()
        text.append(f"\n  Neural Network Architecture for {name}\n", style="bold cyan")
        text.append("  " + "=" * 50 + "\n\n", style="cyan")
        
        # Input layer labels
        input_labels = ["Hunger", "Health", "Distance", "Direction", "Speed"]
        output_labels = ["Move X", "Move Y", "Eat"]
        
        text.append("  INPUT LAYER:\n", style="bold green")
        for i, label in enumerate(input_labels):
            text.append(f"    [{i}] {label:12}", style="green")
            if i < len(input_labels):
                text.append(" ⬤\n", style="bold green")
        
        text.append("\n  HIDDEN LAYERS:\n", style="bold yellow")
        for idx, layer in enumerate(brain.layers[:-1]):
            text.append(f"    Layer {idx}: {layer.weights.shape[0]} neurons\n", style="yellow")
            text.append(f"      Weight range: [{layer.weights.min():.3f}, {layer.weights.max():.3f}]\n", style="dim")
            text.append(f"      Avg magnitude: {np.abs(layer.weights).mean():.3f}\n", style="dim")
        
        text.append("\n  OUTPUT LAYER:\n", style="bold magenta")
        final_layer = brain.layers[-1]
        for i, label in enumerate(output_labels):
            text.append(f"    [{i}] {label:12}", style="magenta")
            text.append(" ⬤\n", style="bold magenta")
        
        text.append(f"\n  Total parameters: {sum(layer.weights.size + layer.biases.size for layer in brain.layers)}\n", style="cyan")
        
        # Show strongest connections
        text.append("\n  STRONGEST INPUT CONNECTIONS:\n", style="bold white")
        first_layer = brain.layers[0]
        for out_idx in range(min(3, first_layer.weights.shape[0])):
            strongest_input = np.argmax(np.abs(first_layer.weights[out_idx]))
            weight = first_layer.weights[out_idx][strongest_input]
            text.append(f"    {input_labels[strongest_input]} → Hidden[{out_idx}]: ", style="white")
            text.append(f"{weight:+.3f}\n", style="green" if weight > 0 else "red")
        
        self.console.print(Panel(text, title=f"Brain Analysis", border_style="cyan"))

    def _print_graph_brain(self, name: str, brain) -> None:
        from emergence.brains import brain_summary_lines, neuropil_table, top_readouts

        text = Text()
        text.append(f"\n  Graph Brain for {name}\n", style="bold cyan")
        for line in brain_summary_lines(brain):
            text.append(f"  {line}\n", style="white")
        text.append("\n  STRONGEST READOUTS:\n", style="bold magenta")
        for action, entries in top_readouts(brain).items():
            joined = ", ".join(f"{label} {w:+.2f}" for label, w in entries)
            text.append(f"    {action:8} <- {joined}\n", style="magenta")
        self.console.print(Panel(text, title="Brain Analysis", border_style="cyan"))

        rows = neuropil_table(brain)
        if rows:
            table = Table(title="Neuropils (FlyBrainLab-style LPU view)")
            table.add_column("Neuropil", style="cyan")
            table.add_column("Nodes", justify="right")
            table.add_column("Internal edges", justify="right")
            for np_name, nodes, edges in rows:
                table.add_row(np_name, str(nodes), str(edges))
            self.console.print(table)

    def print_lineage(self, name: str) -> None:
        creature = self._find_creature(name)
        if not creature:
            self.console.print(f"[red]Creature {name} not found[/red]")
            return
        self.console.print(Panel(f"[cyan]Lineage for {name}[/cyan]", expand=False))
        self.console.print(f"Generation: {creature.generation}")
        self.console.print(f"Parents: {', '.join(creature.parents) if creature.parents else 'Original'}")
