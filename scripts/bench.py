"""Headless benchmark / determinism digest / brain-type comparison for EMERGENCE.

Usage (from repo root):
    PYTHONPATH=. python3 scripts/bench.py --ticks 2000 --seed 42 --brain random
    PYTHONPATH=. python3 scripts/bench.py --ticks 2000 --seed 42 --profile
    PYTHONPATH=. python3 scripts/bench.py --ticks 500 --seed 42 --digest-only
    PYTHONPATH=. python3 scripts/bench.py --compare --ticks 3000 --seed 42
"""

from __future__ import annotations

import argparse
import cProfile
import hashlib
import pstats
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from emergence.world import World, WorldConfig  # noqa: E402


def build_world(brain: str, seed: int, disease: bool = False) -> World:
    config = WorldConfig()
    if hasattr(config, "brain_type"):
        config.brain_type = brain
    if hasattr(config, "disease_enabled"):
        config.disease_enabled = disease
    world = World(config=config, rng=np.random.default_rng(seed))
    # Same bootstrap as the CLI/TUI.
    for _ in range(40):
        world.spawn_plant()
    for _ in range(10):
        world.spawn_herbivore()
    return world


def digest(world: World) -> str:
    rows = [
        (h.name, round(float(h.position[0]), 9), round(float(h.position[1]), 9), round(h.energy, 9), round(h.fitness, 9))
        for h in world.herbivores
    ]
    return hashlib.sha256(repr((world.tick_count, rows)).encode()).hexdigest()[:16]


def run(brain: str, ticks: int, seed: int, disease: bool = False) -> dict:
    world = build_world(brain, seed, disease)
    start = time.perf_counter()
    world.simulate(ticks, headless=True)
    seconds = time.perf_counter() - start
    deaths = [e.data for e in world.stats.events if e.event_type == "death"]
    lifespans = [d["age"] for d in deaths]
    fitness = [d["fitness"] for d in deaths]
    return {
        "brain": brain,
        "ticks": ticks,
        "seconds": seconds,
        "tps": ticks / seconds if seconds else float("inf"),
        "population": len(world.herbivores),
        "generations": world.stats.total_generations,
        "plants_eaten": world.stats.total_plants_consumed,
        "deaths": world.stats.total_deaths,
        "avg_lifespan": float(np.mean(lifespans)) if lifespans else 0.0,
        "avg_fitness": float(np.mean(fitness)) if fitness else 0.0,
        "best_fitness": float(max(fitness)) if fitness else 0.0,
        "digest": digest(world),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ticks", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--brain", default="random")
    parser.add_argument("--disease", action="store_true")
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("--digest-only", action="store_true")
    parser.add_argument("--compare", action="store_true", help="Run every brain type and print a table")
    args = parser.parse_args(argv)

    if args.compare:
        from emergence.brains import BRAIN_TYPES

        cols = ["brain", "tps", "population", "generations", "plants_eaten", "deaths", "avg_lifespan", "avg_fitness", "best_fitness"]
        print("  ".join(f"{c:>20}" for c in cols))
        for brain in BRAIN_TYPES:
            r = run(brain, args.ticks, args.seed, args.disease)
            print("  ".join(f"{r[c]:>20.2f}" if isinstance(r[c], float) else f"{r[c]:>20}" for c in cols))
        return 0

    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()
        result = run(args.brain, args.ticks, args.seed, args.disease)
        profiler.disable()
        pstats.Stats(profiler).sort_stats("tottime").print_stats(20)
    else:
        result = run(args.brain, args.ticks, args.seed, args.disease)

    if args.digest_only:
        print(result["digest"])
    else:
        for key, value in result.items():
            print(f"{key:>14}: {value:.2f}" if isinstance(value, float) else f"{key:>14}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
