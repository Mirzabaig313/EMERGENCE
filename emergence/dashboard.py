"""Dashboard system for EMERGENCE statistics and visualizations."""

from typing import Optional

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from emergence.graphs import ASCIIGraph, DashboardRenderer
from emergence.stats import StatisticsTracker
from emergence.world import World


class Dashboard:
    """Main dashboard for displaying statistics and visualizations."""

    def __init__(self, world: World, console: Optional[Console] = None):
        self.world = world
        self.console = console or Console()
        self.graph = ASCIIGraph(width=70, height=20)
        self.renderer = DashboardRenderer(self.console)

    def show_main_dashboard(self) -> None:
        """Display the main statistics dashboard."""
        stats = self.world.stats
        summary = stats.get_summary()

        # Get current metrics
        current_pop = summary.get("current_population", {})
        current_fit = summary.get("current_fitness", {})

        panel = self.renderer.render_main_dashboard(
            tick=self.world.tick_count,
            population=current_pop.get("herbivores", 0),
            plants=current_pop.get("plants", 0),
            avg_fitness=current_fit.get("avg", 0.0),
            best_fitness=current_fit.get("best", 0.0),
            generation=current_pop.get("generation", 0),
            births=stats.total_births,
            deaths=stats.total_deaths,
            plants_consumed=stats.total_plants_consumed,
        )
        self.console.print(panel)

    def show_population_graph(self, last_n: int = 100) -> None:
        """Display population over time graph."""
        data = self.world.stats.get_population_data(last_n=last_n)
        if not data:
            self.console.print("[yellow]No population data available yet[/yellow]")
            return

        # Prepare data for line chart
        herbivore_data = [(d["tick"], d["herbivores"]) for d in data]
        plant_data = [(d["tick"], d["plants"]) for d in data]

        chart_data = {"Herbivores": herbivore_data, "Plants": plant_data}
        colors = {"Herbivores": "red", "Plants": "green"}

        panel = self.graph.render_line_chart(
            data=chart_data,
            title=f"Population Over Time (Last {len(data)} ticks)",
            x_label="Tick",
            y_label="Count",
            colors=colors,
        )
        self.console.print(panel)

    def show_fitness_graph(self, last_n: int = 100) -> None:
        """Display fitness evolution graph."""
        data = self.world.stats.get_fitness_data(last_n=last_n)
        if not data:
            self.console.print("[yellow]No fitness data available yet[/yellow]")
            return

        # Prepare data for line chart
        avg_fitness_data = [(d["tick"], d["avg"]) for d in data]
        best_fitness_data = [(d["tick"], d["best"]) for d in data]

        chart_data = {"Average Fitness": avg_fitness_data, "Best Fitness": best_fitness_data}
        colors = {"Average Fitness": "yellow", "Best Fitness": "green"}

        panel = self.graph.render_line_chart(
            data=chart_data,
            title=f"Fitness Evolution (Last {len(data)} ticks)",
            x_label="Tick",
            y_label="Fitness",
            colors=colors,
        )
        self.console.print(panel)

    def show_age_distribution(self) -> None:
        """Display age distribution histogram."""
        ages = [h.age for h in self.world.herbivores if h.alive]
        if not ages:
            self.console.print("[yellow]No creatures alive to analyze[/yellow]")
            return

        panel = self.graph.render_histogram(ages, bins=10, title="Age Distribution", color="cyan")
        self.console.print(panel)

    def show_fitness_distribution(self) -> None:
        """Display fitness distribution histogram."""
        fitnesses = [h.fitness for h in self.world.herbivores if h.alive]
        if not fitnesses:
            self.console.print("[yellow]No creatures alive to analyze[/yellow]")
            return

        panel = self.graph.render_histogram(fitnesses, bins=10, title="Fitness Distribution", color="green")
        self.console.print(panel)

    def show_energy_distribution(self) -> None:
        """Display energy distribution histogram."""
        energies = [h.energy for h in self.world.herbivores if h.alive]
        if not energies:
            self.console.print("[yellow]No creatures alive to analyze[/yellow]")
            return

        panel = self.graph.render_histogram(energies, bins=10, title="Energy Distribution", color="yellow")
        self.console.print(panel)

    def show_heatmap(self, heatmap_type: str) -> None:
        """Display spatial heatmap."""
        if heatmap_type not in {"births", "deaths", "food"}:
            self.console.print("[red]Unknown heatmap type. Use births, deaths, or food.[/red]")
            return

        resolution = 20
        world_size = (self.world.config.width, self.world.config.height)
        heatmap_data = self.world.stats.get_heatmap_data(heatmap_type, world_size, resolution)

        titles = {"births": "Birth Locations Heatmap", "deaths": "Death Locations Heatmap", "food": "Food Consumption Heatmap"}

        title = titles.get(heatmap_type, "Heatmap")
        panel = self.graph.render_heatmap(heatmap_data, title=title)
        self.console.print(panel)

    def show_timeline(self) -> None:
        """Display evolution timeline."""
        generations = self.world.stats.generation_history
        if not generations:
            self.console.print("[yellow]No generation data available yet[/yellow]")
            return

        text = Text()
        text.append("═" * 70 + "\n", style="cyan")
        text.append("EVOLUTION TIMELINE\n", style="bold cyan")
        text.append("═" * 70 + "\n", style="cyan")

        for gen in generations[-10:]:
            timeline = self.renderer.render_population_timeline(
                gen.tick, gen.generation, gen.avg_fitness, gen.best_fitness
            )
            text.append(timeline)

        self.console.print(Panel(text, title="Evolution Progress", border_style="cyan"))

    def show_species_comparison(self) -> None:
        """Display species comparison table."""
        herbivores = [h for h in self.world.herbivores if h.alive]

        if not herbivores:
            self.console.print("[yellow]No creatures alive to compare[/yellow]")
            return

        # Calculate statistics
        import numpy as np

        avg_fitness = float(np.mean([h.fitness for h in herbivores]))
        avg_energy = float(np.mean([h.energy for h in herbivores]))
        avg_age = float(np.mean([h.age for h in herbivores]))
        avg_health = float(np.mean([h.health for h in herbivores]))

        table = Table(title="Species Statistics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Herbivores", style="green")

        table.add_row("Population", str(len(herbivores)))
        table.add_row("Avg Fitness", f"{avg_fitness:.1f}")
        table.add_row("Avg Energy", f"{avg_energy:.1f}")
        table.add_row("Avg Age", f"{avg_age:.1f}")
        table.add_row("Avg Health", f"{avg_health:.1f}")
        table.add_row("Total Births", str(self.world.stats.total_births))
        table.add_row("Total Deaths", str(self.world.stats.total_deaths))

        self.console.print(table)

    def show_learning_curve(self, name: str) -> None:
        """Display learning curve for a specific creature."""
        if name not in self.world.stats.learning_curves:
            self.console.print(f"[red]No learning data for {name}[/red]")
            return

        curve_data = self.world.stats.learning_curves[name]
        if not curve_data:
            self.console.print(f"[yellow]No learning data for {name}[/yellow]")
            return

        chart_data = {name: curve_data}
        panel = self.graph.render_line_chart(
            data=chart_data,
            title=f"Learning Progress: {name}",
            x_label="Tick",
            y_label="Fitness",
            colors={name: "cyan"},
        )
        self.console.print(panel)

    def show_family_tree(self, name: str, depth: int = 5) -> None:
        """Display family tree for a creature."""
        lineage = self.world.stats.get_lineage(name, depth=depth)
        if not lineage:
            self.console.print(f"[red]{name} not found in family tree[/red]")
            return

        text = Text()
        text.append("╔" + "═" * 60 + "╗\n", style="cyan")
        text.append("║", style="cyan")
        text.append(f" LINEAGE FOR {name:^46} ", style="bold cyan")
        text.append("║\n", style="cyan")
        text.append("╚" + "═" * 60 + "╝\n", style="cyan")

        for i, ancestor in enumerate(lineage):
            indent = "  " * i
            arrow = "└─ " if i > 0 else ""
            
            text.append(f"{indent}{arrow}", style="dim")
            text.append(f"[{ancestor['name']}]\n", style="bold green" if i == 0 else "green")
            text.append(f"{indent}   ", style="dim")
            text.append(f"Gen {ancestor['generation']}", style="cyan")
            text.append(f" | Born: Tick {ancestor['birth_tick']}", style="yellow")
            
            if "final_fitness" in ancestor:
                text.append(f" | Fitness: {ancestor['final_fitness']:.1f}", style="magenta")
            
            text.append("\n")
            
            parents = ancestor.get("parents", [])
            if parents:
                text.append(f"{indent}   Parents: {', '.join(parents)}\n", style="dim")
            
            text.append("\n")

        self.console.print(Panel(text, title="Family Tree", border_style="cyan"))

    def show_recent_events(self, count: int = 10, event_type: Optional[str] = None) -> None:
        """Display recent events."""
        events = self.world.stats.get_recent_events(count=count, event_type=event_type)
        if not events:
            self.console.print("[yellow]No events recorded yet[/yellow]")
            return

        table = Table(title=f"Recent {'All ' if not event_type else event_type.title() + ' '}Events", show_header=True)
        table.add_column("Tick", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Details", style="white")

        for event in events:
            event_data = event.data
            details = f"{event_data.get('name', 'Unknown')}"
            if event.event_type == "death":
                details += f" (Age: {event_data.get('age', 0):.0f}, Fitness: {event_data.get('fitness', 0):.1f})"
            table.add_row(str(event.tick), event.event_type.title(), details)

        self.console.print(table)

    def show_top_performers(self, count: int = 10) -> None:
        """Display top performing creatures."""
        herbivores = sorted(self.world.herbivores, key=lambda h: h.fitness, reverse=True)[:count]
        if not herbivores:
            self.console.print("[yellow]No creatures available[/yellow]")
            return

        table = Table(title=f"Top {count} Performers", show_header=True)
        table.add_column("Rank", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Fitness", style="yellow")
        table.add_column("Generation", style="magenta")
        table.add_column("Age", style="blue")
        table.add_column("Energy", style="white")

        for i, creature in enumerate(herbivores, 1):
            table.add_row(
                str(i),
                creature.name,
                f"{creature.fitness:.1f}",
                str(creature.generation),
                f"{creature.age:.0f}",
                f"{creature.energy:.0f}",
            )

        self.console.print(table)
