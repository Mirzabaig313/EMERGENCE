#!/usr/bin/env python3
"""
Grayscale Sprite Gallery Demo

Demonstrates the grayscale block art creature sprites for EMERGENCE.
Displays all creatures in various states and provides interactive navigation.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from emergence.sprite_renderer import (
    GrayscaleSpriteRenderer,
    create_sprite_sheet,
    render_animation_preview
)
from emergence.sprites_grayscale import (
    get_all_creature_types,
    get_creatures_by_tier,
    get_creatures_by_category,
    get_creature_info
)


def clear_screen():
    """Clear the terminal screen."""
    import os
    os.system('clear' if os.name != 'nt' else 'cls')


def show_main_menu():
    """Display main menu."""
    print("\n" + "=" * 80)
    print(" " * 20 + "GRAYSCALE SPRITE GALLERY - EMERGENCE")
    print("=" * 80)
    print("\n1. View All Creatures (Full Gallery)")
    print("2. View by Tier")
    print("3. View by Category")
    print("4. View Single Creature")
    print("5. Sprite Sheet (All Creatures)")
    print("6. Animation Preview")
    print("7. Side-by-Side Comparison")
    print("8. Exit")
    print("\nEnter choice (1-8): ", end='')


def show_all_creatures():
    """Display all creatures with all states."""
    clear_screen()
    renderer = GrayscaleSpriteRenderer()
    print("\n" + "=" * 80)
    print(" " * 25 + "COMPLETE CREATURE GALLERY")
    print("=" * 80 + "\n")
    
    renderer.render_sprite_gallery()
    
    input("\n\nPress Enter to return to main menu...")


def show_by_tier():
    """Display creatures by tier."""
    clear_screen()
    print("\nSelect Tier:")
    print("1. Tier 1 - Basic Enemies")
    print("2. Tier 2 - Advanced Enemies")
    print("3. Tier 3 - Elite Enemies")
    print("4. Tier 4 - Boss Enemies")
    print("5. Back to Main Menu")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice in ['1', '2', '3', '4']:
        tier = int(choice)
        creatures = get_creatures_by_tier(tier)
        
        clear_screen()
        renderer = GrayscaleSpriteRenderer()
        print(f"\n{'=' * 80}")
        print(f" TIER {tier} CREATURES ".center(80))
        print("=" * 80 + "\n")
        
        renderer.render_sprite_gallery(creature_types=creatures)
        
        input("\n\nPress Enter to continue...")


def show_by_category():
    """Display creatures by category."""
    clear_screen()
    print("\nSelect Category:")
    print("1. Basic Enemies")
    print("2. Advanced Enemies")
    print("3. Elite Enemies")
    print("4. Boss Enemies")
    print("5. Special Creatures")
    print("6. Back to Main Menu")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    categories = {
        '1': 'basic',
        '2': 'advanced',
        '3': 'elite',
        '4': 'boss',
        '5': 'special'
    }
    
    if choice in categories:
        category = categories[choice]
        creatures = get_creatures_by_category(category)
        
        clear_screen()
        renderer = GrayscaleSpriteRenderer()
        print(f"\n{'=' * 80}")
        print(f" {category.upper()} CREATURES ".center(80))
        print("=" * 80 + "\n")
        
        renderer.render_sprite_gallery(creature_types=creatures)
        
        input("\n\nPress Enter to continue...")


def show_single_creature():
    """Display a single creature with all states."""
    all_creatures = get_all_creature_types()
    
    clear_screen()
    print("\nAvailable Creatures:")
    print("-" * 80)
    
    for i, creature in enumerate(sorted(all_creatures), 1):
        info = get_creature_info(creature)
        display_name = creature.replace('_', ' ').title()
        tier = info['tier']
        category = info['category']
        print(f"{i:2}. {display_name:20} (Tier {tier} - {category})")
    
    print("-" * 80)
    choice = input("\nEnter creature number (or 0 to go back): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(all_creatures):
            creature = sorted(all_creatures)[idx]
            
            clear_screen()
            renderer = GrayscaleSpriteRenderer()
            print(f"\n{'=' * 80}")
            print(f" {creature.replace('_', ' ').upper()} ".center(80))
            print("=" * 80 + "\n")
            
            renderer.render_sprite_gallery(
                creature_types=[creature],
                states=['idle', 'attack', 'damaged', 'death']
            )
            
            input("\n\nPress Enter to continue...")
    except (ValueError, IndexError):
        pass


def show_sprite_sheet():
    """Display sprite sheet with all creatures."""
    clear_screen()
    print("\n" + "=" * 80)
    print(" " * 28 + "SPRITE SHEET - IDLE STATE")
    print("=" * 80 + "\n")
    
    all_creatures = sorted(get_all_creature_types())
    
    # Create sprite sheet
    sprite_sheet = create_sprite_sheet(all_creatures, state='idle', columns=3)
    
    for line in sprite_sheet:
        print(line)
    
    input("\n\nPress Enter to return to main menu...")


def show_animation_preview():
    """Show animation preview for a creature."""
    all_creatures = get_all_creature_types()
    
    clear_screen()
    print("\nSelect Creature for Animation Preview:")
    print("-" * 80)
    
    for i, creature in enumerate(sorted(all_creatures), 1):
        display_name = creature.replace('_', ' ').title()
        print(f"{i:2}. {display_name}")
    
    print("-" * 80)
    choice = input("\nEnter creature number (or 0 to go back): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(all_creatures):
            creature = sorted(all_creatures)[idx]
            
            clear_screen()
            print(f"\nStarting animation preview for {creature.replace('_', ' ').title()}")
            print("Press Ctrl+C to stop...")
            time.sleep(2)
            
            render_animation_preview(
                creature,
                states=['idle', 'attack', 'damaged', 'idle', 'death'],
                delay=0.8
            )
    except (ValueError, IndexError):
        pass
    except KeyboardInterrupt:
        pass


def show_side_by_side():
    """Show side-by-side comparison of creature states."""
    all_creatures = get_all_creature_types()
    
    clear_screen()
    print("\nSelect Creature for Side-by-Side Comparison:")
    print("-" * 80)
    
    for i, creature in enumerate(sorted(all_creatures), 1):
        display_name = creature.replace('_', ' ').title()
        print(f"{i:2}. {display_name}")
    
    print("-" * 80)
    choice = input("\nEnter creature number (or 0 to go back): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(all_creatures):
            creature = sorted(all_creatures)[idx]
            
            clear_screen()
            renderer = GrayscaleSpriteRenderer()
            renderer.compare_sprites_side_by_side(
                creature,
                states=['idle', 'attack', 'damaged', 'death']
            )
            
            input("\n\nPress Enter to continue...")
    except (ValueError, IndexError):
        pass


def main():
    """Main program loop."""
    while True:
        clear_screen()
        show_main_menu()
        
        choice = input().strip()
        
        if choice == '1':
            show_all_creatures()
        elif choice == '2':
            show_by_tier()
        elif choice == '3':
            show_by_category()
        elif choice == '4':
            show_single_creature()
        elif choice == '5':
            show_sprite_sheet()
        elif choice == '6':
            show_animation_preview()
        elif choice == '7':
            show_side_by_side()
        elif choice == '8':
            clear_screen()
            print("\nThank you for viewing the EMERGENCE Sprite Gallery!")
            print("Visit GRAYSCALE_SPRITES.md for full documentation.\n")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\n\nExiting sprite gallery...\n")
        sys.exit(0)
