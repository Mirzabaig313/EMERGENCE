#!/usr/bin/env python3
"""Demonstration of EMERGENCE's statistics dashboard and visualizations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from emergence.world import World
from emergence.dashboard import Dashboard
from rich.console import Console


def main():
    """Run a demo simulation and show various dashboard views."""
    console = Console()
    console.print("\n[bold cyan]EMERGENCE Statistics Dashboard Demo[/bold cyan]\n")
    
    # Create world and bootstrap ecosystem
    world = World()
    for _ in range(40):
        world.spawn_plant()
    for _ in range(10):
        world.spawn_herbivore()
    
    # Create dashboard
    dashboard = Dashboard(world, console)
    
    # Run simulation for a bit
    console.print("[yellow]Running initial simulation (500 ticks)...[/yellow]\n")
    world.simulate(500, headless=True)
    
    # Show main dashboard
    console.print("\n[bold green]═══ MAIN DASHBOARD ═══[/bold green]\n")
    dashboard.show_main_dashboard()
    
    # Show population graph
    console.print("\n\n[bold green]═══ POPULATION GRAPH ═══[/bold green]\n")
    dashboard.show_population_graph(last_n=100)
    
    # Show fitness graph
    console.print("\n\n[bold green]═══ FITNESS EVOLUTION ═══[/bold green]\n")
    dashboard.show_fitness_graph(last_n=100)
    
    # Show distributions
    console.print("\n\n[bold green]═══ AGE DISTRIBUTION ═══[/bold green]\n")
    dashboard.show_age_distribution()
    
    console.print("\n\n[bold green]═══ ENERGY DISTRIBUTION ═══[/bold green]\n")
    dashboard.show_energy_distribution()
    
    # Show top performers
    console.print("\n\n[bold green]═══ TOP PERFORMERS ═══[/bold green]\n")
    dashboard.show_top_performers(count=5)
    
    # Show heatmaps
    console.print("\n\n[bold green]═══ BIRTH LOCATIONS HEATMAP ═══[/bold green]\n")
    dashboard.show_heatmap("births")
    
    console.print("\n\n[bold green]═══ FOOD CONSUMPTION HEATMAP ═══[/bold green]\n")
    dashboard.show_heatmap("food")
    
    # Show recent events
    console.print("\n\n[bold green]═══ RECENT EVENTS ═══[/bold green]\n")
    dashboard.show_recent_events(count=10)
    
    # Show species comparison
    console.print("\n\n[bold green]═══ SPECIES STATISTICS ═══[/bold green]\n")
    dashboard.show_species_comparison()
    
    # Show learning curve for a creature (if any exist)
    if world.herbivores:
        top_creature = max(world.herbivores, key=lambda h: h.fitness)
        console.print(f"\n\n[bold green]═══ LEARNING CURVE FOR {top_creature.name} ═══[/bold green]\n")
        dashboard.show_learning_curve(top_creature.name)
        
        # Show family tree
        console.print(f"\n\n[bold green]═══ FAMILY TREE FOR {top_creature.name} ═══[/bold green]\n")
        dashboard.show_family_tree(top_creature.name, depth=5)
    
    # Export statistics
    console.print("\n\n[bold green]Exporting statistics...[/bold green]")
    world.stats.export_to_json(Path("demo_stats.json"))
    world.stats.export_to_csv(Path("demo_stats.csv"))
    console.print("[green]✓ Exported to demo_stats.json and demo_stats.csv[/green]")
    
    console.print("\n[bold cyan]Demo complete![/bold cyan]\n")


if __name__ == "__main__":
    main()
