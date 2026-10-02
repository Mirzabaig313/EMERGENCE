from __future__ import annotations

import dataclasses
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING

import numpy as np

from emergence.entities import Herbivore, Plant, plant_arrays, plant_distances
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
    brain_type: str = "random"  # see emergence.brains.BRAIN_TYPES
    # Disease / immune mechanic (off by default)
    disease_enabled: bool = False
    disease_seed_rate: float = 0.002  # per-tick chance one random susceptible gets infected
    disease_radius: float = 20.0
    disease_transmission: float = 0.05
    disease_damage: float = 2.0
    immune_cost: float = 0.05


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
    _brain_template: Optional[object] = field(default=None, init=False, repr=False, compare=False)
    _disease_event_prev: bool = field(default=False, init=False, repr=False, compare=False)
    _plant_seq: int = field(default=0, init=False, repr=False, compare=False)

    def spawn_plant(self, name: Optional[str] = None, position: Optional[np.ndarray] = None) -> Plant:
        pos = position if position is not None else self._random_position(margin=20)
        if name is None:
            # len(self.plants) shrinks after removals, so it repeats names; a monotonic counter doesn't.
            # ponytail: counter restarts on load, so loaded and new plants can share names (cosmetic only).
            name = f"plant_{self._plant_seq}"
            self._plant_seq += 1
        plant = Plant(name=name, position=pos, species="plant")
        self.plants.append(plant)
        return plant

    def spawn_herbivore(self, name: Optional[str] = None, position: Optional[np.ndarray] = None) -> Herbivore:
        pos = position if position is not None else self._random_position(margin=30)
        from emergence.reinforcement import RLAgent

        agent = RLAgent(self._new_brain(), rng=self.rng)
        herbivore = Herbivore(
            name=name or f"herbivore_{self.next_id}",
            position=pos,
            species="herbivore",
            agent=agent,
            rng=self.rng,
            energy=self.config.herbivore_spawn_energy,
        )
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

    def _new_brain(self):
        from emergence.brains import GraphBrain, generate_template, make_brain

        kind = self.config.brain_type
        if kind != "generative":
            return make_brain(kind, self.rng)
        if self._brain_template is None:
            # Share one topology across the population so crossover works; reuse a loaded one if present.
            existing = next((h.brain for h in self.herbivores if h.brain_type == "generative"), None)
            if isinstance(existing, GraphBrain):
                self._brain_template = existing.clone()
            else:
                self._brain_template = generate_template(self.rng)
        return make_brain(kind, self.rng, template=self._brain_template)

    def breed(self, parent_a: Herbivore, parent_b: Herbivore) -> Herbivore:
        """Player-forced reproduction. Records the birth and costs both parents 30% energy."""
        if parent_a is parent_b:
            raise ValueError("A creature can't breed with itself")
        if not (parent_a.alive and parent_b.alive):
            raise ValueError("Both parents must be alive")
        child = self.genetics.reproduce(
            parent_a, parent_b, name=f"herbivore_{self.next_id}", position=parent_a.position, rng=self.rng
        )
        self.herbivores.append(child)
        self.next_id += 1
        parent_a.energy *= 0.7
        parent_b.energy *= 0.7
        self.stats.record_birth(
            self.tick_count, child.name, (float(child.position[0]), float(child.position[1])), child.parents, child.generation
        )
        return child

    def brain_type_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for h in self.herbivores:
            if h.alive:
                counts[h.brain_type] = counts.get(h.brain_type, 0) + 1
        return counts

    def infected_count(self) -> int:
        return sum(1 for h in self.herbivores if h.alive and h.infection > 0)

    def _update_disease(self, modifiers: Dict[str, float], newly_dead: List[Herbivore]) -> None:
        """Infection progression, transmission and seeding (inspired by Allen Immunology's immune-health atlas).

        ponytail: single strain, boolean immune memory that never wanes, O(H^2) transmission
        (fine below ~500 herbivores; upgrade path is a spatial grid).
        """
        cfg = self.config
        alive = [h for h in self.herbivores if h.alive]
        # Constitutive immune cost and infection progression
        for h in alive:
            h.energy -= cfg.immune_cost * h.immune_strength
            if h.infection > 0:
                h.infection = float(np.clip(h.infection + 0.03 - 0.08 * h.immune_strength, 0.0, 1.0))
                h.health -= cfg.disease_damage * h.infection
                if h.infection == 0.0:
                    h.immune_memory = True
                    self.stats.record_disease(self.tick_count, h.name, "recovery")

        def susceptible(h: Herbivore) -> bool:
            return h.alive and h.infection == 0 and not h.immune_memory

        # Transmission from creatures infected at the start of this phase
        sources = [h for h in alive if h.infection > 0]
        if sources and alive:
            src_pos = np.array([h.position for h in sources], dtype=float)
            for h in alive:
                if not susceptible(h):
                    continue
                if plant_distances(src_pos, h.position).min() <= cfg.disease_radius:
                    if self.rng.random() < cfg.disease_transmission * (1.0 - h.immune_strength):
                        h.infection = 0.1
                        self.stats.record_disease(self.tick_count, h.name, "infection")

        # Baseline seeding
        if self.rng.random() < cfg.disease_seed_rate:
            pool = [h for h in alive if susceptible(h)]
            if pool:
                target = pool[int(self.rng.integers(len(pool)))]
                target.infection = 0.1
                self.stats.record_disease(self.tick_count, target.name, "infection")

        # Gameplay DISEASE event seeds on its rising edge only (events last whole generations)
        active = "health_reduction" in modifiers
        if active and not self._disease_event_prev:
            pool = [h for h in alive if susceptible(h)]
            if pool:
                for idx in self.rng.choice(len(pool), size=min(3, len(pool)), replace=False):
                    pool[int(idx)].infection = 0.1
                    self.stats.record_disease(self.tick_count, pool[int(idx)].name, "infection")
        self._disease_event_prev = active

        for h in alive:
            if h.alive and (h.health <= 0 or h.energy <= 0):
                h.alive = False
                newly_dead.append(h)

    def simulate(self, ticks: int, headless: bool = True) -> Dict[str, float]:
        stats = {"ticks": ticks, "plants_spawned": 0, "herbivores_dead": 0, "offspring": 0}
        for _ in range(ticks):
            self.tick_count += 1
            
            # Get active event modifiers from gameplay system
            modifiers: Dict[str, float] = {}
            if self.gameplay_system and hasattr(self.gameplay_system, 'event_manager'):
                modifiers = self.gameplay_system.event_manager.get_active_modifiers()
            
            # Apply plant growth modifier
            plant_growth_mult = modifiers.get("plant_growth_multiplier", 1.0)
            self._update_plants(growth_multiplier=plant_growth_mult)
            
            newly_dead: List[Herbivore] = []
            rewards: Dict[str, float] = {}
            births_this_tick = 0
            deaths_this_tick = 0
            plants_eaten_tick = 0
            
            # Get reproduction threshold modifier
            reproduction_mult = modifiers.get("reproduction_threshold_multiplier", 1.0)
            effective_reproduction_threshold = self.config.herbivore_reproduction_threshold * reproduction_mult

            # Plant list is fixed for the herbivore loop; snapshot once and keep `plant_alive` in sync.
            plant_pos, plant_alive = plant_arrays(self.plants)

            for herbivore in list(self.herbivores):
                if not herbivore.alive:
                    newly_dead.append(herbivore)
                    continue

                state = herbivore.perceive(self.plants, plant_pos, plant_alive)
                action = herbivore.decide(state, explore=headless)
                herbivore.apply_action(action)
                self._clamp_position(herbivore)

                # Eating behavior
                eat_reward = 0.0
                if action[2] > 0.4 and self.plants:
                    dist = plant_distances(plant_pos, herbivore.position)
                    nearby = np.flatnonzero(plant_alive & (dist <= herbivore.eat_radius))
                    for idx in nearby:
                        plant = self.plants[idx]
                        eaten = herbivore.eat(plant)
                        plant_alive[idx] = plant.alive
                        if eaten > 0:
                            eat_reward += eaten * 0.5
                            plants_eaten_tick += 1
                            # Track food consumption
                            self.stats.record_food_consumption(self.tick_count, (float(herbivore.position[0]), float(herbivore.position[1])), eaten)
                # Survival reward
                survival_reward = 0.1
                reward = eat_reward + survival_reward
                rewards[herbivore.name] = reward

                next_state = herbivore.perceive(self.plants, plant_pos, plant_alive)
                herbivore.apply_reward(reward, next_state=next_state)
                
                # Track learning progress
                self.stats.record_learning_progress(herbivore.name, self.tick_count, herbivore.fitness)
                
                herbivore.tick()

                if herbivore.alive and herbivore.energy >= effective_reproduction_threshold:
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

            if self.config.disease_enabled:
                self._update_disease(modifiers, newly_dead)

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
                        corpse.brain_type,
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
                    brain_fitness=self._brain_fitness(generation_creatures or self.herbivores),
                )
                self.stats.record_generation(gen_stats)
                # Must follow record_generation: victory checks read stats.total_generations.
                if self.gameplay_system and self.gameplay_system.active:
                    self.gameplay_system.update_generation(max_gen)

        return stats

    @staticmethod
    def _brain_fitness(creatures: List[Herbivore]) -> Dict[str, float]:
        groups: Dict[str, List[float]] = {}
        for h in creatures:
            groups.setdefault(h.brain_type, []).append(h.fitness)
        return {k: float(np.mean(v)) for k, v in groups.items()}

    def _update_plants(self, growth_multiplier: float = 1.0) -> None:
        for plant in self.plants:
            # Apply growth multiplier to plant's growth rate temporarily
            original_growth_rate = plant.growth_rate
            plant.growth_rate *= growth_multiplier
            plant.tick()
            plant.growth_rate = original_growth_rate  # Restore original rate
        # Filter by flags, not list.remove(): dataclass __eq__ compares numpy positions and raises
        # when two plants share a name (plant names can repeat after removals).
        self.plants = [p for p in self.plants if p.alive or p.nutrients > 0]

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
                    "metabolism": herbivore.metabolism,
                    "speed_limit": herbivore.speed_limit,
                    "vision_range": herbivore.vision_range,
                    "velocity": herbivore.velocity.tolist(),
                    "stats": dict(herbivore.stats),
                    "immune_strength": herbivore.immune_strength,
                    "infection": herbivore.infection,
                    "immune_memory": herbivore.immune_memory,
                }
                for herbivore in self.herbivores
            ],
            "tick_count": self.tick_count,
            "next_id": self.next_id,
            "stats": self.stats.to_save_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "World":
        known = {f.name for f in dataclasses.fields(WorldConfig)}
        world = cls(config=WorldConfig(**{k: v for k, v in data["config"].items() if k in known}))
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
                metabolism=herb_data.get("metabolism", 0.5),
                speed_limit=herb_data.get("speed_limit", 3.0),
                vision_range=herb_data.get("vision_range", 60.0),
                velocity=np.array(herb_data.get("velocity", [0.0, 0.0]), dtype=float),
                immune_strength=herb_data.get("immune_strength", 0.5),
                infection=herb_data.get("infection", 0.0),
                immune_memory=herb_data.get("immune_memory", False),
            )
            herbivore.stats.update(herb_data.get("stats", {}))
            herbivore.agent = world._reconstruct_agent(herb_data["agent"])
            herbivore.rng = world.rng
            world.herbivores.append(herbivore)
        if "stats" in data:
            world.stats.load_save_dict(data["stats"])
        return world

    def save(self, path: str | Path) -> None:
        # Atomic: write a sibling temp file, then replace, so a failed dump never truncates an existing save.
        path = Path(path)
        data = self.to_dict()
        tmp = path.with_suffix(path.suffix + ".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            os.replace(tmp, path)
        finally:
            if tmp.exists():
                tmp.unlink()

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

    def _reconstruct_agent(self, data: dict) -> "RLAgent":
        from emergence.reinforcement import RLAgent

        agent = RLAgent.from_dict(data, rng=self.rng)
        return agent
