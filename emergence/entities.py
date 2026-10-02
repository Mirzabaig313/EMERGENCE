from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from emergence.neural import NeuralNetwork
from emergence.reinforcement import RLAgent


# eq=False on every entity class: identity equality. Field equality compares numpy positions and raises
# ValueError inside list.remove / `in` when two entities share a name.
@dataclass(eq=False)
class Entity:
    name: str
    position: np.ndarray
    species: str
    alive: bool = True

    def distance_to(self, other: "Entity") -> float:
        return float(np.linalg.norm(self.position - other.position))


def plant_distances(positions: np.ndarray, origin: np.ndarray) -> np.ndarray:
    """Euclidean distances from origin to each row of positions (P, 2).

    ponytail: batched matmul reproduces np.linalg.norm's BLAS dot bit-for-bit on numpy 2.x;
    elementwise (d*d).sum() does not (~8% differ by 1 ulp, which breaks run digests).
    tests/test_world.py guards this.
    """
    d = positions - origin
    return np.sqrt(np.matmul(d[:, None, :], d[:, :, None]).ravel())


def plant_arrays(plants: List["Plant"]) -> "tuple[np.ndarray, np.ndarray]":
    """Snapshot plant positions (P, 2) and alive flags (P,) for vectorized queries."""
    if not plants:
        return np.zeros((0, 2)), np.zeros(0, dtype=bool)
    return np.array([p.position for p in plants], dtype=float), np.array([p.alive for p in plants], dtype=bool)


@dataclass(eq=False)
class Plant(Entity):
    growth_stage: float = 1.0
    nutrients: float = 20.0
    age: float = 0.0
    growth_rate: float = 0.01

    def tick(self, dt: float = 1.0) -> None:
        if not self.alive:
            return
        self.age += dt
        self.growth_stage = min(5.0, self.growth_stage + self.growth_rate * dt)
        self.nutrients = min(30.0, self.nutrients + 0.2 * dt)

    def consume(self, amount: float) -> float:
        if not self.alive:
            return 0.0
        eaten = min(self.nutrients, amount)
        self.nutrients -= eaten
        if self.nutrients <= 0:
            self.alive = False
        return eaten


@dataclass
class Memory:
    last_food_position: Optional[np.ndarray] = None
    last_reward: float = 0.0


@dataclass(eq=False)
class Herbivore(Entity):
    energy: float = 50.0
    health: float = 100.0
    age: float = 0.0
    fitness: float = 0.0
    agent: RLAgent = field(default_factory=lambda: RLAgent(NeuralNetwork((5, 8, 3))))
    memory: Memory = field(default_factory=Memory)
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(2))
    parents: List[str] = field(default_factory=list)
    generation: int = 0
    rng: np.random.Generator = field(default_factory=np.random.default_rng)

    max_energy: float = 100.0
    max_health: float = 100.0
    metabolism: float = 0.5
    move_cost: float = 0.2
    vision_range: float = 60.0
    eat_radius: float = 5.0
    speed_limit: float = 3.0

    stats: Dict[str, float] = field(default_factory=lambda: {"plants_eaten": 0.0, "distance_travelled": 0.0})

    # Immune system (used only when WorldConfig.disease_enabled). immune_strength is heritable.
    immune_strength: float = 0.5
    infection: float = 0.0
    immune_memory: bool = False

    @property
    def brain(self):
        return self.agent.brain

    @property
    def brain_type(self) -> str:
        return getattr(self.agent.brain, "brain_type", "random")

    def perceive(
        self, plants: List[Plant], positions: Optional[np.ndarray] = None, alive: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Build the 5-d sensor vector. `positions`/`alive` are optional per-tick plant arrays (see World)."""
        hunger = 1.0 - (self.energy / self.max_energy)
        health_ratio = self.health / self.max_health
        nearest_plant = self._nearest_plant(plants, positions, alive)
        if nearest_plant:
            delta = nearest_plant.position - self.position
            distance = np.linalg.norm(delta)
            direction = math.atan2(delta[1], delta[0]) / math.pi
            distance_norm = min(1.0, distance / self.vision_range)
            self.memory.last_food_position = nearest_plant.position.copy()
        else:
            distance_norm = 1.0
            direction = 0.0
        speed = np.linalg.norm(self.velocity) / self.speed_limit
        return np.array([hunger, health_ratio, distance_norm, direction, speed], dtype=float)

    def decide(self, state: np.ndarray, explore: bool = True) -> np.ndarray:
        return self.agent.choose_action(state, explore=explore)

    def apply_action(self, action: np.ndarray, dt: float = 1.0) -> None:
        # Action components: delta_x, delta_y, eat_signal
        move_vector = action[:2]
        eat_signal = action[2]
        acceleration = np.clip(move_vector, -1.0, 1.0)
        self.velocity += acceleration
        speed = np.linalg.norm(self.velocity)
        if speed > self.speed_limit:
            self.velocity = (self.velocity / speed) * self.speed_limit
        self.position += self.velocity * dt
        # Only deduct movement cost here; metabolism is handled in tick()
        self.energy -= self.move_cost * speed
        self.stats["distance_travelled"] += float(speed * dt)
        # Clamp position to world boundaries (handled in world update)
        self.memory.last_reward = eat_signal

    def eat(self, plant: Plant) -> float:
        eaten = plant.consume(10.0)
        if eaten > 0:
            self.energy = min(self.max_energy, self.energy + eaten)
            self.stats["plants_eaten"] += 1
        return eaten

    def tick(self, dt: float = 1.0) -> None:
        self.age += dt
        self.energy -= self.metabolism * dt
        if self.energy <= 0:
            self.health -= 5 * dt
        else:
            self.health = min(self.max_health, self.health + 0.1 * dt)
        if self.health <= 0 or self.age > 500:
            self.alive = False

    def reward(self, amount: float) -> None:
        self.agent.reinforce(amount)
        self.fitness += amount

    def apply_reward(self, reward: float, next_state: Optional[np.ndarray] = None) -> None:
        self.agent.update(reward, next_state)
        self.fitness += reward

    def _nearest_plant(
        self, plants: List[Plant], positions: Optional[np.ndarray] = None, alive: Optional[np.ndarray] = None
    ) -> Optional[Plant]:
        if not plants:
            return None
        if positions is None or alive is None:
            positions, alive = plant_arrays(plants)
        # ponytail: O(H*P) vectorized scan, fine for P up to a few thousand; upgrade path is a spatial grid.
        dist = plant_distances(positions, self.position)
        candidates = np.flatnonzero(alive & (dist <= self.vision_range))
        if candidates.size == 0:
            return None
        # argmin keeps the first minimum, same tie-break as the old min(key=...).
        return plants[int(candidates[np.argmin(dist[candidates])])]

    def copy_brain(self) -> NeuralNetwork:
        return self.agent.brain.clone()
