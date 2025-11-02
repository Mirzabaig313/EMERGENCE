"""Demo of the new gameplay system with modes, progression, and events."""

from rich.console import Console

from emergence.gameplay import GameplaySystem
from emergence.game_modes import GameModeType
from emergence.progression import UnlockType
from emergence.world import World


def main():
    """Run a demo of the gameplay system."""
    console = Console()
    world = World()
    gameplay = GameplaySystem(world, console)
    
    console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║       EMERGENCE GAMEPLAY DEMO          ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]\n")
    
    # Start survival mode
    console.print("[yellow]Starting Survival Mode...[/yellow]\n")
    message = gameplay.start_mode(GameModeType.SURVIVAL)
    console.print(f"✓ {message}\n")
    
    # Show gameplay status
    console.print("[bold]Initial Gameplay Status:[/bold]")
    panel = gameplay.display_status_panel()
    console.print(panel)
    console.print()
    
    # Simulate some ticks
    console.print("[yellow]Simulating 100 ticks...[/yellow]\n")
    world.simulate(100, headless=True)
    
    # Check for events
    generation = world.stats.total_generations
    messages = gameplay.event_manager.check_random_events(generation, {})
    if messages:
        console.print("[bold green]Random Events:[/bold green]")
        for msg in messages:
            console.print(f"  • {msg}")
        console.print()
    
    # Update achievements
    population = len([h for h in world.herbivores if h.alive])
    achievement_messages = gameplay.progression.update_population_achievements(population, 1)
    if achievement_messages:
        console.print("[bold magenta]Achievements Unlocked:[/bold magenta]")
        for msg in achievement_messages:
            console.print(f"  • {msg}")
        console.print()
    
    # Award some EP
    ep_msg = gameplay.progression.earn_ep(10, "Demo bonus")
    console.print(f"[green]✓ {ep_msg}[/green]\n")
    
    # Show updated status
    console.print("[bold]Updated Gameplay Status:[/bold]")
    panel = gameplay.display_status_panel()
    console.print(panel)
    console.print()
    
    # Show timeline
    timeline = gameplay.display_timeline()
    console.print(timeline)
    console.print()
    
    # Show achievements
    console.print("[bold cyan]Achievement Progress:[/bold cyan]")
    from rich.table import Table
    
    table = Table(show_header=True)
    table.add_column("Achievement", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Progress", style="yellow")
    
    for achievement in list(gameplay.progression.achievements.values())[:5]:
        status = "✓ Unlocked" if achievement.unlocked else "Locked"
        progress = f"{min(achievement.progress, achievement.max_progress):.0f}/{achievement.max_progress}"
        table.add_row(achievement.name, status, progress)
    
    console.print(table)
    console.print()
    
    # Show available unlocks
    console.print(f"[bold cyan]Evolution Points:[/bold cyan] {gameplay.progression.evolution_points}")
    console.print("[dim]Use EP to unlock new creatures, abilities, and challenges![/dim]\n")
    
    # Show example unlocks
    console.print("[bold]Example Unlocks Available:[/bold]")
    example_unlocks = [
        UnlockType.CARNIVORES,
        UnlockType.MUTATION_BOOST,
        UnlockType.DIVINE_INTERVENTION,
    ]
    
    for unlock_type in example_unlocks:
        unlock = gameplay.progression.unlocks[unlock_type]
        status = "✓ Unlocked" if unlock.unlocked else f"({unlock.ep_cost} EP)"
        console.print(f"  • {unlock.name}: {unlock.description} {status}")
    
    console.print("\n[bold green]Demo complete! Try running 'python -m emergence' to play interactively.[/bold green]")


if __name__ == "__main__":
    main()
