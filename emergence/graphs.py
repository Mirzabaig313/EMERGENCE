"""ASCII graph rendering utilities for EMERGENCE."""

from typing import Dict, List, Optional, Tuple

import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ASCIIGraph:
    """Render ASCII-based graphs and charts."""

    def __init__(self, width: int = 60, height: int = 15):
        self.width = width
        self.height = height
        self.console = Console()

    def render_line_chart(
        self,
        data: Dict[str, List[Tuple[int, float]]],
        title: str = "Chart",
        x_label: str = "X",
        y_label: str = "Y",
        colors: Optional[Dict[str, str]] = None,
    ) -> Panel:
        """Render a line chart with multiple series."""
        if not data or not any(data.values()):
            return Panel("[yellow]No data to display[/yellow]", title=title)

        # Determine data ranges
        all_x = []
        all_y = []
        for series in data.values():
            if series:
                all_x.extend([point[0] for point in series])
                all_y.extend([point[1] for point in series])

        if not all_x or not all_y:
            return Panel("[yellow]No data to display[/yellow]", title=title)

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        # Avoid division by zero
        if max_x == min_x:
            max_x = min_x + 1
        if max_y == min_y:
            max_y = min_y + 1

        # Create grid
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        # Plot each series
        symbols = ["█", "▓", "▒", "░", "●", "○", "■", "□"]
        default_colors = ["cyan", "green", "yellow", "magenta", "blue", "red"]
        colors = colors or {}

        for idx, (name, series) in enumerate(data.items()):
            if not series:
                continue

            symbol = symbols[idx % len(symbols)]
            color = colors.get(name, default_colors[idx % len(default_colors)])

            for i in range(len(series) - 1):
                x1, y1 = series[i]
                x2, y2 = series[i + 1]

                # Normalize to grid coordinates
                gx1 = int((x1 - min_x) / (max_x - min_x) * (self.width - 1))
                gy1 = int((1 - (y1 - min_y) / (max_y - min_y)) * (self.height - 1))
                gx2 = int((x2 - min_x) / (max_x - min_x) * (self.width - 1))
                gy2 = int((1 - (y2 - min_y) / (max_y - min_y)) * (self.height - 1))

                # Bresenham's line algorithm (simplified)
                dx = abs(gx2 - gx1)
                dy = abs(gy2 - gy1)
                sx = 1 if gx1 < gx2 else -1
                sy = 1 if gy1 < gy2 else -1
                err = dx - dy

                x, y = gx1, gy1
                while True:
                    if 0 <= x < self.width and 0 <= y < self.height:
                        grid[y][x] = (symbol, color)

                    if x == gx2 and y == gy2:
                        break

                    e2 = 2 * err
                    if e2 > -dy:
                        err -= dy
                        x += sx
                    if e2 < dx:
                        err += dx
                        y += sy

        # Render grid
        text = Text()
        for row in grid:
            for cell in row:
                if isinstance(cell, tuple):
                    symbol, color = cell
                    text.append(symbol, style=color)
                else:
                    text.append(cell, style="dim")
            text.append("\n")

        # Add axis labels
        y_axis = Text()
        y_axis.append(f"{y_label}\n", style="bold")
        y_axis.append(f"{max_y:.1f}│\n", style="dim")
        for _ in range(self.height - 2):
            y_axis.append("     │\n", style="dim")
        y_axis.append(f"{min_y:.1f}└", style="dim")
        y_axis.append("─" * (self.width + 1) + f" {x_label}\n", style="dim")
        y_axis.append(f"     {min_x:.0f}" + " " * (self.width - 10) + f"{max_x:.0f}", style="dim")

        # Legend
        legend = Text("\n\nLegend: ", style="bold")
        for idx, name in enumerate(data.keys()):
            symbol = symbols[idx % len(symbols)]
            color = colors.get(name, default_colors[idx % len(default_colors)])
            legend.append(f"{symbol} {name}  ", style=color)

        full_text = Text.assemble(text, y_axis, legend)
        return Panel(full_text, title=title, border_style="cyan")

    def render_histogram(
        self, data: List[float], bins: int = 10, title: str = "Histogram", color: str = "green"
    ) -> Panel:
        """Render a histogram."""
        if not data:
            return Panel("[yellow]No data to display[/yellow]", title=title)

        # Calculate histogram
        counts, edges = np.histogram(data, bins=bins)
        max_count = max(counts) if len(counts) > 0 else 1

        # Render bars
        text = Text()
        for i, count in enumerate(counts):
            bar_height = int((count / max_count) * self.height)
            label = f"{edges[i]:.1f}-{edges[i+1]:.1f}"
            text.append(f"{label:>12} │", style="dim")
            text.append("█" * bar_height, style=color)
            text.append(f" ({int(count)})\n")

        return Panel(text, title=title, border_style="cyan")

    def render_bar_chart(
        self, data: Dict[str, float], title: str = "Bar Chart", color: str = "blue"
    ) -> Panel:
        """Render a bar chart."""
        if not data:
            return Panel("[yellow]No data to display[/yellow]", title=title)

        max_value = max(data.values()) if data else 1
        max_label_len = max(len(k) for k in data.keys()) if data else 10

        text = Text()
        for name, value in data.items():
            bar_width = int((value / max_value) * (self.width - max_label_len - 10))
            text.append(f"{name:>{max_label_len}} │", style="dim")
            text.append("█" * bar_width, style=color)
            text.append(f" {value:.1f}\n")

        return Panel(text, title=title, border_style="cyan")

    def render_heatmap(
        self,
        data: np.ndarray,
        title: str = "Heatmap",
        gradient: Optional[List[str]] = None,
    ) -> Panel:
        """Render a heatmap using Unicode blocks and colors."""
        if data.size == 0:
            return Panel("[yellow]No data to display[/yellow]", title=title)

        gradient = gradient or ["⬜", "🟦", "🟩", "🟨", "🟧", "🟥"]
        max_val = data.max() if data.max() > 0 else 1

        text = Text()
        for row in data:
            for value in row:
                intensity = min(int((value / max_val) * (len(gradient) - 1)), len(gradient) - 1)
                text.append(gradient[intensity])
            text.append("\n")

        return Panel(text, title=title, border_style="cyan")


class DashboardRenderer:
    """Render comprehensive dashboard views."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.graph = ASCIIGraph()

    def render_main_dashboard(
        self,
        tick: int,
        population: int,
        plants: int,
        avg_fitness: float,
        best_fitness: float,
        generation: int,
        births: int,
        deaths: int,
        plants_consumed: int,
    ) -> Panel:
        """Render the main statistics dashboard."""
        text = Text()
        text.append("╔" + "═" * 48 + "╗\n", style="cyan")
        text.append("║", style="cyan")
        text.append(" " * 15 + "EMERGENCE STATS" + " " * 18, style="bold cyan")
        text.append("║\n", style="cyan")
        text.append("╠" + "═" * 48 + "╣\n", style="cyan")

        stats = [
            ("Generation", generation, "cyan"),
            ("Simulation Ticks", tick, "white"),
            ("Population", population, "green"),
            ("Plants Available", plants, "green"),
            ("Avg Fitness", f"{avg_fitness:.1f}", "yellow"),
            ("Best Fitness", f"{best_fitness:.1f}", "bold yellow"),
            ("Total Births", births, "cyan"),
            ("Total Deaths", deaths, "red"),
            ("Plants Consumed", plants_consumed, "green"),
        ]

        for label, value, color in stats:
            text.append("║ ", style="cyan")
            text.append(f"{label:20}", style="white")
            text.append(f"{value:>26}", style=color)
            text.append(" ║\n", style="cyan")

        text.append("╚" + "═" * 48 + "╝", style="cyan")

        return Panel(text, title="[bold cyan]Dashboard[/bold cyan]", border_style="cyan")

    def render_population_timeline(
        self, tick: int, generation: int, avg_fitness: float, best_fitness: float
    ) -> Text:
        """Render evolution timeline ASCII art."""
        # Calculate progress bar
        fitness_ratio = min(avg_fitness / (best_fitness or 1), 1.0)
        bar_length = 10
        filled = int(fitness_ratio * bar_length)

        text = Text()
        text.append(f"Gen {generation:3d}  ", style="cyan")
        text.append("█" * filled, style="green")
        text.append("░" * (bar_length - filled), style="dim")
        text.append(f"  (Avg: {avg_fitness:.0f})\n", style="white")

        return text
