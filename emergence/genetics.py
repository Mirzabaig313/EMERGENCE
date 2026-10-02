from typing import List, Tuple

import numpy as np

from emergence.entities import Herbivore
from emergence.reinforcement import RLAgent


class GeneticAlgorithm:
    """Manages evolution of creatures via genetic algorithms."""

    def __init__(
        self,
        mutation_rate: float = 0.1,
        mutation_scale: float = 0.3,
        crossover_rate: float = 0.7,
        elite_fraction: float = 0.2,
    ):
        self.mutation_rate = mutation_rate
        self.mutation_scale = mutation_scale
        self.crossover_rate = crossover_rate
        self.elite_fraction = elite_fraction

    def select_parents(self, population: List[Herbivore], num_parents: int) -> List[Herbivore]:
        """Truncation selection - selects top N individuals by fitness."""
        if not population:
            return []
        sorted_pop = sorted(population, key=lambda h: h.fitness, reverse=True)
        return sorted_pop[:num_parents]

    def reproduce(
        self, parent_a: Herbivore, parent_b: Herbivore, name: str, position: np.ndarray, rng: np.random.Generator
    ) -> Herbivore:
        """Create offspring from two parents via crossover and mutation."""
        brain_a, brain_b = parent_a.agent.brain, parent_b.agent.brain
        # Mismatched brain types/topologies (e.g. after switching `brain` mid-run) fall back to cloning.
        if rng.random() < self.crossover_rate and brain_a.compatible(brain_b):
            child_brain = type(brain_a).crossover(brain_a, brain_b, rng=rng)
        else:
            child_brain = brain_a.clone(rng=rng)

        child_brain.mutate(self.mutation_rate, self.mutation_scale)
        child_agent = RLAgent(
            brain=child_brain,
            learning_rate=parent_a.agent.learning_rate,
            discount_factor=parent_a.agent.discount_factor,
            epsilon=0.3,
            rng=rng,
        )

        child = Herbivore(
            name=name,
            position=position.copy(),
            species="herbivore",
            agent=child_agent,
            parents=[parent_a.name, parent_b.name],
            generation=max(parent_a.generation, parent_b.generation) + 1,
            rng=rng,
            # Inherit physical traits with mutation
            metabolism=self._mutate_trait(np.mean([parent_a.metabolism, parent_b.metabolism]), 0.05, rng),
            speed_limit=self._mutate_trait(np.mean([parent_a.speed_limit, parent_b.speed_limit]), 0.2, rng),
            vision_range=self._mutate_trait(np.mean([parent_a.vision_range, parent_b.vision_range]), 2.0, rng),
            immune_strength=self._mutate_immunity((parent_a.immune_strength + parent_b.immune_strength) / 2, rng),
        )
        return child

    def _mutate_immunity(self, value: float, rng: np.random.Generator) -> float:
        # Same draw pattern as _mutate_trait, but clipped to [0, 1] instead of floored at 0.1.
        if rng.random() < self.mutation_rate:
            return float(np.clip(value + rng.normal(0, 0.05), 0.0, 1.0))
        return float(value)

    def _mutate_trait(self, value: float, scale: float, rng: np.random.Generator) -> float:
        if rng.random() < self.mutation_rate:
            return max(0.1, value + rng.normal(0, scale))
        return value

    def evolve_generation(
        self, dead_population: List[Herbivore], next_id: int, world_size: Tuple[float, float], rng: np.random.Generator
    ) -> Tuple[List[Herbivore], int]:
        """Create a new generation from dead creatures."""
        if len(dead_population) < 2:
            return [], next_id

        num_elite = max(2, int(len(dead_population) * self.elite_fraction))
        parents = self.select_parents(dead_population, num_elite)
        new_generation = []
        offspring_count = len(dead_population)

        for idx in range(offspring_count):
            parent_a = parents[idx % len(parents)]
            parent_b = parents[(idx + 1) % len(parents)]
            spawn_pos = np.array([rng.uniform(50, world_size[0] - 50), rng.uniform(50, world_size[1] - 50)])
            child = self.reproduce(parent_a, parent_b, f"herbivore_{next_id}", spawn_pos, rng)
            new_generation.append(child)
            next_id += 1

        return new_generation, next_id
