#!/usr/bin/env python3
"""
EMERGENCE Art Assets Demo

Demonstrates the terminal art asset system including sprites, animations,
colors, UI components, terrain, and effects.
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from emergence.art_assets import get_asset_manager
from emergence.sprites import SpriteLibrary, create_sparkline
from emergence.ui_elements import AsciiArt


def demo_sprites(console: Console, assets):
    """Demonstrate sprite rendering."""
    console.print("\n[bold cyan]═══ SPRITE DEMO ═══[/bold cyan]\n")
    
    # Herbivores
    console.print("[bold green]Herbivores:[/bold green]")
    console.print(f"  Standard: {SpriteLibrary.HERBIVORE_RABBIT}")
    console.print(f"  Fast:     {SpriteLibrary.HERBIVORE_RABBIT_FAST}")
    console.print(f"  Large:    {SpriteLibrary.HERBIVORE_DEER}")
    console.print(f"  Small:    {SpriteLibrary.HERBIVORE_MOUSE}")
    
    # Carnivores
    console.print("\n[bold red]Carnivores:[/bold red]")
    console.print(f"  Standard: {SpriteLibrary.CARNIVORE_FOX}")
    console.print(f"  Apex:     {SpriteLibrary.CARNIVORE_WOLF}")
    console.print(f"  Scavenger:{SpriteLibrary.CARNIVORE_EAGLE}")
    console.print(f"  Omnivore: {SpriteLibrary.CARNIVORE_BEAR}")
    
    # Plants
    console.print("\n[bold green]Plants:[/bold green]")
    console.print(f"  Sprout:   {SpriteLibrary.PLANT_SPROUT}")
    console.print(f"  Herb:     {SpriteLibrary.PLANT_HERB}")
    console.print(f"  Grass:    {SpriteLibrary.PLANT_GRASS}")
    console.print(f"  Tree:     {SpriteLibrary.PLANT_TREE}")
    
    # Status indicators
    console.print("\n[bold yellow]Status Indicators:[/bold yellow]")
    console.print(f"  {SpriteLibrary.STATUS_SLEEPING} Sleeping")
    console.print(f"  {SpriteLibrary.STATUS_EATING} Eating")
    console.print(f"  {SpriteLibrary.STATUS_BREEDING} Breeding")
    console.print(f"  {SpriteLibrary.STATUS_LEVELUP} Level Up")
    console.print(f"  {SpriteLibrary.STATUS_ELITE} Elite")
    
    time.sleep(2)


def demo_animations(console: Console, assets):
    """Demonstrate animation sequences."""
    console.print("\n[bold cyan]═══ ANIMATION DEMO ═══[/bold cyan]\n")
    
    # Register entity animators
    herbivore_animator = assets.register_entity_animator("demo_herbivore")
    carnivore_animator = assets.register_entity_animator("demo_carnivore")
    
    # Demonstrate herbivore animations
    console.print("[bold green]Herbivore Animations:[/bold green]")
    
    states = ['idle', 'walk', 'run', 'eat']
    for state in states:
        console.print(f"\n  State: {state}")
        herbivore_animator.set_state(state, species='herbivore')
        
        # Show a few frames
        for _ in range(5):
            frame = herbivore_animator.get_current_frame()
            console.print(f"    {frame}", end=" ")
            assets.update_animations()
            time.sleep(0.1)
        console.print()
    
    # Demonstrate carnivore animations
    console.print("\n[bold red]Carnivore Animations:[/bold red]")
    
    states = ['idle', 'hunt', 'attack']
    for state in states:
        console.print(f"\n  State: {state}")
        carnivore_animator.set_state(state, species='carnivore')
        
        # Show a few frames
        for _ in range(5):
            frame = carnivore_animator.get_current_frame()
            console.print(f"    {frame}", end=" ")
            assets.update_animations()
            time.sleep(0.1)
        console.print()
    
    time.sleep(2)


def demo_colors(console: Console, assets):
    """Demonstrate color schemes."""
    console.print("\n[bold cyan]═══ COLOR DEMO ═══[/bold cyan]\n")
    
    # Creature colors
    console.print("[bold]Creature Colors:[/bold]")
    
    sprite = assets.get_sprite('herbivore')
    
    # Healthy herbivore
    color = assets.get_creature_color('herbivore', age=100, health=100, energy=90)
    text = assets.render_colored_sprite(sprite, color)
    console.print(f"  Healthy herbivore: ", text)
    
    # Hungry herbivore
    color = assets.get_creature_color('herbivore', age=100, health=30, energy=20)
    text = assets.render_colored_sprite(sprite, color)
    console.print(f"  Hungry herbivore:  ", text)
    
    # Baby herbivore
    color = assets.get_creature_color('herbivore', age=50, health=100, energy=80)
    text = assets.render_colored_sprite(sprite, color)
    console.print(f"  Baby herbivore:    ", text)
    
    time.sleep(2)


def demo_ui_components(console: Console, assets):
    """Demonstrate UI components."""
    console.print("\n[bold cyan]═══ UI COMPONENTS DEMO ═══[/bold cyan]\n")
    
    # Menu
    console.print("[bold]Menu:[/bold]")
    menu = assets.create_menu(["New Game", "Load Game", "Settings", "Quit"], selected=0, width=30)
    for line in menu:
        console.print(line)
    
    # Progress bars
    console.print("\n[bold]Progress Bars:[/bold]")
    hp_bar = assets.create_progress_bar("HP", 75, 100, width=30, bar_width=10)
    en_bar = assets.create_progress_bar("EN", 60, 100, width=30, bar_width=10)
    console.print(f"  {hp_bar}")
    console.print(f"  {en_bar}")
    
    # Stat panel
    console.print("\n[bold]Stat Panel:[/bold]")
    stats = {
        "HP": "75/100",
        "EN": "60/100",
        "FIT": "847",
        "AGE": "234"
    }
    panel = assets.create_stat_panel("CREATURE STATS", stats, width=35)
    for line in panel:
        console.print(line)
    
    # Tabs
    console.print("\n[bold]Tabs:[/bold]")
    tabs = assets.create_tabs(["🌍 World", "📊 Dashboard", "📈 Graphs"], active=0, width=60)
    console.print(tabs)
    
    time.sleep(2)


def demo_terrain(console: Console, assets):
    """Demonstrate terrain rendering."""
    console.print("\n[bold cyan]═══ TERRAIN DEMO ═══[/bold cyan]\n")
    
    # Terrain textures
    console.print("[bold]Terrain Textures:[/bold]\n")
    
    plains = assets.get_terrain_texture('plains', width=20, height=3)
    console.print("[bold green]Plains:[/bold green]")
    for line in plains:
        console.print(f"  {line}")
    
    console.print()
    
    desert = assets.get_terrain_texture('desert', width=20, height=3)
    console.print("[bold yellow]Desert:[/bold yellow]")
    for line in desert:
        console.print(f"  {line}")
    
    # Sparkline
    console.print("\n[bold]Sparkline (Population):[/bold]")
    values = [10, 15, 20, 18, 25, 30, 28, 35, 40, 38, 45]
    sparkline = assets.create_sparkline(values, width=30)
    console.print(f"  Population: {sparkline}")
    
    time.sleep(2)


def demo_scenes(console: Console, assets):
    """Demonstrate predefined scenes."""
    console.print("\n[bold cyan]═══ SCENES DEMO ═══[/bold cyan]\n")
    
    # Campfire scene
    console.print("[bold]Campfire Scene:[/bold]")
    campfire = assets.render_scene('campfire')
    for line in campfire:
        console.print(line)
    
    console.print("\n[bold]Village Scene:[/bold]")
    village = assets.render_scene('village')
    for line in village:
        console.print(line)
    
    time.sleep(2)


def demo_effects(console: Console, assets):
    """Demonstrate visual effects."""
    console.print("\n[bold cyan]═══ EFFECTS DEMO ═══[/bold cyan]\n")
    
    console.print("[bold]Visual Effects:[/bold]")
    
    # Birth effect
    console.print("\n  Birth effect:")
    effect = assets.create_effect('birth', (100, 100), duration=1.0)
    for i in range(8):
        console.print(f"    {effect.get_current_sprite()}", end=" ")
        effect.update(effect.start_time + i * 0.125)
        time.sleep(0.125)
    console.print()
    
    # Attack effect
    console.print("\n  Attack effect:")
    effect = assets.create_effect('attack', (100, 100), duration=0.5)
    for i in range(5):
        console.print(f"    {effect.get_current_sprite()}", end=" ")
        effect.update(effect.start_time + i * 0.1)
        time.sleep(0.1)
    console.print()
    
    # Evolution effect
    console.print("\n  Evolution effect:")
    effect = assets.create_effect('evolution', (100, 100), duration=1.0)
    for i in range(8):
        console.print(f"    {effect.get_current_sprite()}", end=" ")
        effect.update(effect.start_time + i * 0.125)
        time.sleep(0.125)
    console.print()
    
    time.sleep(2)


def demo_logo(console: Console, assets):
    """Display EMERGENCE logo."""
    console.clear()
    console.print("\n")
    
    logo = assets.get_logo()
    for line in logo:
        console.print(f"[bold cyan]{line}[/bold cyan]")
    
    console.print("\n[bold]AI Ecosystem Simulator[/bold]")
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def main():
    """Run all demonstrations."""
    console = Console()
    assets = get_asset_manager()
    
    # Display logo
    demo_logo(console, assets)
    
    console.clear()
    
    # Run demos
    demo_sprites(console, assets)
    demo_animations(console, assets)
    demo_colors(console, assets)
    demo_ui_components(console, assets)
    demo_terrain(console, assets)
    demo_scenes(console, assets)
    demo_effects(console, assets)
    
    # Summary
    console.print("\n[bold cyan]═══ DEMO COMPLETE ═══[/bold cyan]\n")
    info = assets.get_info()
    console.print("[bold]Asset Manager Info:[/bold]")
    for key, value in info.items():
        console.print(f"  {key}: {value}")
    
    console.print("\n[bold green]✅ All art assets successfully demonstrated![/bold green]")
    console.print("\n[dim]For more information, see:[/dim]")
    console.print("  - ASSETS_README.md")
    console.print("  - SPRITE_GUIDE.md")
    console.print("  - ANIMATION_GUIDE.md")
    console.print("  - COLOR_SCHEME.md")
    console.print("  - UI_COMPONENTS.md")


if __name__ == '__main__':
    main()
