#!/usr/bin/env python3
"""EMERGENCE quickstart script.

This demonstrates the basic usage of the ecosystem simulator:
- Creating a world with plants and herbivores
- Running a headless simulation
- Viewing ecosystem statistics
"""

from emergence.world import World


def main():
    print("=" * 60)
    print("EMERGENCE Quickstart")
    print("=" * 60 + "\n")
    world = World()
    for _ in range(40):
        world.spawn_plant()
    for _ in range(10):
        world.spawn_herbivore()
    print(f"Initial population: {world.population_summary()}")
    print(f"Simulating 1000 ticks...\n")
    stats = world.simulate(1000, headless=True)
    print("Simulation complete!")
    print(f"Stats: {stats}")
    print(f"\nFinal population: {world.population_summary()}")
    metrics = world.ecosystem_metrics()
    print(f"Ecosystem metrics: {metrics}")
    if world.herbivores:
        best = max(world.herbivores, key=lambda h: h.fitness)
        print(f"\nBest performer: {best.name}")
        print(f"  Generation: {best.generation}")
        print(f"  Fitness: {best.fitness:.2f}")
        print(f"  Energy: {best.energy:.2f}")
        print(f"  Age: {best.age:.1f}")
    print("\nTo launch the interactive CLI, run: python -m emergence")


if __name__ == "__main__":
    main()
