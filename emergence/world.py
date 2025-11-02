from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING

import numpy as np

from emergence.entities import Herbivore, Plant
from emergence.genetics import GeneticAlgorithm
from emergence.stats import GenerationStats, StatisticsTracker

if TYPE_CHECKING:
    from emergence.gameplay import GameplaySystem


@dataclass
class WorldConfig:
    width: float = 500.0
    height: float = 500.0
    max_plants: int = 120
    plant_spawn_rate: float = 0.05
    plant_seed_energy: float = 15.0
    herbivore_spawn_energy: float = 60.0
    herbivore_reproduction_threshold: float = 90.0


@dataclass
class World:
    config: WorldConfig = field(default_factory=WorldConfig)
    rng: np.random.Generator = field(default_factory=np.random.default_rng)
    plants: List[Plant] = field(default_factory=list)
    herbivores: List[Herbivore] = field(default_factory=list)
    dead_herbivores: List[Herbivore] = field(default_factory=list)
    tick_count: int = 0
    next_id: int = 0
    genetics: GeneticAlgorithm = field(default_factory=GeneticAlgorithm)
    stats: StatisticsTracker = field(default_factory=StatisticsTracker)
    gameplay_system: Optional["GameplaySystem"] = field(default=None, init=False, repr=False, compare=False)

    def spawn_plant(self, name: Optional[str] = None, position: Optional[np.ndarray] = None) -> Plant:
        pos = position if position is not None else self._random_position(margin=20)
        plant = Plant(name=name or f"plant_{len(self.plants)}", position=pos, species="plant")
        self.plants.append(plant)
        return plant

    def spawn_herbivore(self, name: Optional[str] = None, position: Optional[np.ndarray] = None) -> Herbivore:
        pos = position if position is not None else self._random_position(margin=30)
        herbivore = Herbivore(name=name or f"herbivore_{self.next_id}", position=pos, species="herbivore", rng=self.rng)
        self.herbivores.append(herbivore)
        self.stats.record_birth(
            self.tick_count,
            herbivore.name,
            (float(herbivore.position[0]), float(herbivore.position[1])),
            herbivore.parents,
            herbivore.generation,
        )
        self.next_id += 1
        return herbivore

    def simulate(self, ticks: int, headless: bool = True) -> Dict[str, float]:
        stats = {"ticks": ticks, "plants_spawned": 0, "herbivores_dead": 0, "offspring": 0}
        for _ in range(ticks):
            self.tick_count += 1
            self._update_plants()
            newly_dead: List[Herbivore] = []
            rewards: Dict[str, float] = {}
            births_this_tick = 0
            deaths_this_tick = 0
            plants_eaten_tick = 0

            for herbivore in list(self.herbivores):
                if not herbivore.alive:
                    newly_dead.append(herbivore)
                    continue

                state = herbivore.perceive(self.plants)
                action = herbivore.decide(state, explore=headless)
                herbivore.apply_action(action)
                self._clamp_position(herbivore)

                # Eating behavior
                eat_reward = 0.0
                if action[2] > 0.4:
                    nearby_plants = [
                        plant for plant in self.plants if plant.alive and herbivore.distance_to(plant) <= herbivore.eat_radius
                    ]
                    for plant in nearby_plants:
                        eaten = herbivore.eat(plant)
                        if eaten > 0:
                            eat_reward += eaten * 0.5
                            plants_eaten_tick += 1
                            # Track food consumption
                            self.stats.record_food_consumption(self.tick_count, (float(herbivore.position[0]), float(herbivore.position[1])), eaten)
                # Survival reward
                survival_reward = 0.1
                reward = eat_reward + survival_reward
                rewards[herbivore.name] = reward

                next_state = herbivore.perceive(self.plants)
                herbivore.apply_reward(reward, next_state=next_state)
                
                # Track learning progress
                self.stats.record_learning_progress(herbivore.name, self.tick_count, herbivore.fitness)
                
                herbivore.tick()

                if herbivore.energy >= self.config.herbivore_reproduction_threshold:
                    partner = self._select_partner(herbivore)
                    if partner:
                        child_pos = self._random_position(margin=40)
                        child = self.genetics.reproduce(
                            herbivore,
                            partner,
                            name=f"herbivore_{self.next_id}",
                            position=child_pos,
                            rng=self.rng,
                        )
                        self.herbivores.append(child)
                        self.next_id += 1
                        herbivore.energy *= 0.6
                        partner.energy *= 0.6
                        stats["offspring"] += 1
                        births_this_tick += 1
                        # Track birth
                        self.stats.record_birth(
                            self.tick_count,
                            child.name,
                            (float(child_pos[0]), float(child_pos[1])),
                            child.parents,
                            child.generation,
                        )

                if herbivore.energy <= 0 or herbivore.health <= 0:
                    herbivore.alive = False
                    newly_dead.append(herbivore)

            # Remove dead herbivores
            for corpse in newly_dead:
                if corpse in self.herbivores:
                    self.herbivores.remove(corpse)
                    self.dead_herbivores.append(corpse)
                    stats["herbivores_dead"] += 1
                    deaths_this_tick += 1
                    # Track death
                    self.stats.record_death(
                        self.tick_count,
                        corpse.name,
                        (float(corpse.position[0]), float(corpse.position[1])),
                        corpse.age,
                        corpse.fitness,
                        corpse.generation,
                    )

            # Regrow plants and spawn new ones
            if len(self.plants) < self.config.max_plants and self.rng.random() < self.config.plant_spawn_rate:
                self.spawn_plant()
                stats["plants_spawned"] += 1

            # Evolution when population crashes
            if len(self.herbivores) < 5 and self.dead_herbivores:
                new_generation, self.next_id = self.genetics.evolve_generation(
                    self.dead_herbivores, self.next_id, (self.config.width, self.config.height), self.rng
                )
                self.herbivores.extend(new_generation)
                for child in new_generation:
                    self.stats.record_birth(
                        self.tick_count,
                        child.name,
                        (float(child.position[0]), float(child.position[1])),
                        child.parents,
                        child.generation,
                    )
                    births_this_tick += 1
                self.dead_herbivores.clear()

            # Record tick statistics
            if self.herbivores:
                avg_fitness = float(np.mean([h.fitness for h in self.herbivores]))
                best_fitness = float(max(h.fitness for h in self.herbivores))
                avg_energy = float(np.mean([h.energy for h in self.herbivores]))
                avg_age = float(np.mean([h.age for h in self.herbivores]))
                max_gen = max(h.generation for h in self.herbivores)
            else:
                avg_fitness = best_fitness = avg_energy = avg_age = 0.0
                max_gen = 0
            
            self.stats.record_tick(
                self.tick_count,
                len(self.herbivores),
                len([p for p in self.plants if p.alive]),
                avg_fitness,
                best_fitness,
                avg_energy,
                avg_age,
                max_gen,
            )

            if max_gen > self.stats.total_generations:
                generation_creatures = [h for h in self.herbivores if h.generation == max_gen]
                if generation_creatures:
                    gen_avg_fitness = float(np.mean([h.fitness for h in generation_creatures]))
                    gen_best_fitness = float(max([h.fitness for h in generation_creatures]))
                    gen_avg_age = float(np.mean([h.age for h in generation_creatures]))
                    gen_avg_energy = float(np.mean([h.energy for h in generation_creatures]))
                    gen_population = len(generation_creatures)
                else:
                    gen_avg_fitness = avg_fitness
                    gen_best_fitness = best_fitness
                    gen_avg_age = avg_age
                    gen_avg_energy = avg_energy
                    gen_population = len(self.herbivores)

                gen_stats = GenerationStats(
                    generation=max_gen,
                    tick=self.tick_count,
                    population=gen_population,
                    avg_fitness=gen_avg_fitness,
                    best_fitness=gen_best_fitness,
                    avg_age=gen_avg_age,
                    avg_energy=gen_avg_energy,
                    births=births_this_tick,
                    deaths=deaths_this_tick,
                    plants_eaten=plants_eaten_tick,
                )
                self.stats.record_generation(gen_stats)

        return stats

    def _update_plants(self) -> None:
        for plant in list(self.plants):
            plant.tick()
            if not plant.alive and plant.nutrients <= 0:
                self.plants.remove(plant)

    def _clamp_position(self, herbivore: Herbivore) -> None:
        herbivore.position[0] = float(np.clip(herbivore.position[0], 0, self.config.width))
        herbivore.position[1] = float(np.clip(herbivore.position[1], 0, self.config.height))

    def _select_partner(self, herbivore: Herbivore) -> Optional[Herbivore]:
        candidates = [h for h in self.herbivores if h is not herbivore and h.alive and h.energy > 50]
        if not candidates:
            return None
        return max(candidates, key=lambda h: h.fitness)

    def reward(self, name: str, amount: float) -> bool:
        creature = self._find_creature(name)
        if creature:
            creature.reward(amount)
            return True
        return False

    def punish(self, name: str, amount: float) -> bool:
        creature = self._find_creature(name)
        if creature:
            creature.reward(-abs(amount))
            return True
        return False

    def creature_stats(self, name: str) -> Optional[Dict[str, float]]:
        creature = self._find_creature(name)
        if not creature:
            return None
        return {
            "name": creature.name,
            "energy": creature.energy,
            "health": creature.health,
            "age": creature.age,
            "fitness": creature.fitness,
            "generation": creature.generation,
            "plants_eaten": creature.stats.get("plants_eaten", 0),
            "distance_travelled": creature.stats.get("distance_travelled", 0),
        }

    def population_summary(self) -> Dict[str, int]:
        return {
            "plants": len([p for p in self.plants if p.alive]),
            "herbivores": len([h for h in self.herbivores if h.alive]),
        }

    def ecosystem_metrics(self) -> Dict[str, float]:
        avg_energy = np.mean([h.energy for h in self.herbivores]) if self.herbivores else 0.0
        avg_fitness = np.mean([h.fitness for h in self.herbivores]) if self.herbivores else 0.0
        return {"avg_energy": float(avg_energy), "avg_fitness": float(avg_fitness), "tick": float(self.tick_count)}

    def to_dict(self) -> dict:
        return {
            "config": self.config.__dict__,
            "plants": [
                {
                    "name": plant.name,
                    "position": plant.position.tolist(),
                    "growth_stage": plant.growth_stage,
                    "nutrients": plant.nutrients,
                    "age": plant.age,
                    "alive": plant.alive,
                }
                for plant in self.plants
            ],
            "herbivores": [
                {
                    "name": herbivore.name,
                    "position": herbivore.position.tolist(),
                    "energy": herbivore.energy,
                    "health": herbivore.health,
                    "age": herbivore.age,
                    "fitness": herbivore.fitness,
                    "generation": herbivore.generation,
                    "alive": herbivore.alive,
                    "parents": herbivore.parents,
                    "agent": herbivore.agent.to_dict(),
                }
                for herbivore in self.herbivores
            ],
            "tick_count": self.tick_count,
            "next_id": self.next_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "World":
        world = cls(config=WorldConfig(**data["config"]))
        world.tick_count = data.get("tick_count", 0)
        world.next_id = data.get("next_id", 0)
        for plant_data in data.get("plants", []):
            plant = Plant(
                name=plant_data["name"],
                position=np.array(plant_data["position"], dtype=float),
                species="plant",
                growth_stage=plant_data["growth_stage"],
                nutrients=plant_data["nutrients"],
                age=plant_data["age"],
                alive=plant_data["alive"],
            )
            world.plants.append(plant)
        for herb_data in data.get("herbivores", []):
            herbivore = Herbivore(
                name=herb_data["name"],
                position=np.array(herb_data["position"], dtype=float),
                species="herbivore",
                energy=herb_data["energy"],
                health=herb_data["health"],
                age=herb_data["age"],
                fitness=herb_data["fitness"],
                generation=herb_data.get("generation", 0),
                parents=herb_data.get("parents", []),
                agent=None,  # type: ignore
                alive=herb_data.get("alive", True),
            )
            herbivore.agent = world._reconstruct_agent(herb_data["agent"])
            herbivore.rng = world.rng
            world.herbivores.append(herbivore)
        return world

    def save(self, path: str | Path) -> None:
        data = self.to_dict()
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "World":
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    def _find_creature(self, name: str) -> Optional[Herbivore]:
        for herbivore in self.herbivores:
            if herbivore.name == name:
                return herbivore
        return None

    def _random_position(self, margin: float = 0.0) -> np.ndarray:
        x = self.rng.uniform(margin, self.config.width - margin)
        y = self.rng.uniform(margin, self.config.height - margin)
        return np.array([x, y], dtype=float)

    def _reconstruct_agent(self, data: dict):
        from emergence.reinforcement import RLAgent

        agent = RLAgent.from_dict(data)
        return agent
