#!/usr/bin/env python3
"""Evolution demonstration.

This script runs multiple generations and tracks how fitness improves
through genetic algorithms and reinforcement learning.
"""

from emergence.world import World


def main():
    print("=" * 60)
    print("EMERGENCE Evolution Demo")
    print("=" * 60)
    print("\nInitializing ecosystem with founding population...")
    world = World()
    for _ in range(60):
        world.spawn_plant()
    for _ in range(15):
        world.spawn_herbivore()
    print(f"Starting population: {world.population_summary()}\n")
    print("Running evolutionary simulation...")
    print("This will take a few moments...\n")
    generation_stats = []
    for gen in range(5):
        print(f"Generation {gen + 1}/5")
        stats = world.simulate(500, headless=True)
        metrics = world.ecosystem_metrics()
        generation_stats.append(
            {"generation": gen + 1, "avg_fitness": metrics["avg_fitness"], "avg_energy": metrics["avg_energy"], "population": len(world.herbivores)}
        )
        print(f"  Avg Fitness: {metrics['avg_fitness']:.2f}")
        print(f"  Avg Energy: {metrics['avg_energy']:.2f}")
        print(f"  Population: {len(world.herbivores)}")
        print()
    print("=" * 60)
    print("Evolution Summary")
    print("=" * 60)
    for stat in generation_stats:
        print(
            f"Gen {stat['generation']}: Fitness={stat['avg_fitness']:.2f}, "
            f"Energy={stat['avg_energy']:.2f}, Pop={stat['population']}"
        )
    if generation_stats:
        initial_fitness = generation_stats[0]["avg_fitness"]
        final_fitness = generation_stats[-1]["avg_fitness"]
        improvement = ((final_fitness - initial_fitness) / max(initial_fitness, 0.1)) * 100
        print(f"\nFitness improvement: {improvement:.1f}%")
    if world.herbivores:
        best = max(world.herbivores, key=lambda h: h.fitness)
        print(f"\nMost successful creature: {best.name}")
        print(f"  Generation: {best.generation}")
        print(f"  Fitness: {best.fitness:.2f}")
        print(f"  Parents: {', '.join(best.parents) if best.parents else 'Original'}")
        print(f"  Plants eaten: {best.stats.get('plants_eaten', 0):.0f}")
        print(f"  Distance travelled: {best.stats.get('distance_travelled', 0):.1f}")
    print("\nEvolution demonstrates:")
    print("  - Neural networks learning within lifetimes (RL)")
    print("  - Successful traits passing to offspring (GA)")
    print("  - Emergent grazing and survival behaviors")


if __name__ == "__main__":
    main()
