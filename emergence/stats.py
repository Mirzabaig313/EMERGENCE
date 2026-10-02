"""Statistics tracking and historical data management for EMERGENCE."""

from __future__ import annotations

import dataclasses
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class EventRecord:
    """Record of a specific event in the simulation."""

    tick: int
    event_type: str
    data: Dict[str, Any]


@dataclass
class GenerationStats:
    """Statistics for a single generation."""

    generation: int
    tick: int
    population: int
    avg_fitness: float
    best_fitness: float
    avg_age: float
    avg_energy: float
    births: int
    deaths: int
    plants_eaten: int
    brain_fitness: Dict[str, float] = field(default_factory=dict)  # avg fitness per brain type


@dataclass
class StatisticsTracker:
    """Comprehensive statistics tracking for the EMERGENCE ecosystem."""

    # Configuration
    history_window: int = 1000
    spatial_resolution: int = 20

    # Historical data - initialized in __post_init__ to use history_window
    population_history: deque = field(default_factory=deque)
    fitness_history: deque = field(default_factory=deque)
    generation_history: List[GenerationStats] = field(default_factory=list)
    events: deque = field(default_factory=deque)
    
    def __post_init__(self):
        """Initialize deques with proper maxlen based on history_window."""
        # Re-create deques with correct maxlen if they were created without it
        if self.population_history.maxlen != self.history_window:
            self.population_history = deque(self.population_history, maxlen=self.history_window)
        if self.fitness_history.maxlen != self.history_window:
            self.fitness_history = deque(self.fitness_history, maxlen=self.history_window)
        if self.events.maxlen != self.history_window * 5:
            self.events = deque(self.events, maxlen=self.history_window * 5)

    # Spatial tracking (for heatmaps)
    birth_locations: List[Tuple[float, float]] = field(default_factory=list)
    death_locations: List[Tuple[float, float]] = field(default_factory=list)
    food_consumption_locations: List[Tuple[float, float]] = field(default_factory=list)

    # Cumulative statistics
    total_births: int = 0
    total_deaths: int = 0
    total_plants_consumed: int = 0
    total_generations: int = 0
    extinct_species: int = 0
    total_infections: int = 0
    total_recoveries: int = 0

    # Per brain type: {deaths, lifespan_sum, fitness_sum, best_fitness, max_generation}
    brain_type_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Learning statistics
    learning_curves: Dict[str, List[Tuple[int, float]]] = field(default_factory=dict)

    # Family tree data
    family_tree: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Snapshots for comparison
    snapshots: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def record_tick(
        self,
        tick: int,
        herbivore_count: int,
        plant_count: int,
        avg_fitness: float,
        best_fitness: float,
        avg_energy: float,
        avg_age: float,
        generation: int,
    ) -> None:
        """Record statistics for the current tick."""
        self.population_history.append(
            {"tick": tick, "herbivores": herbivore_count, "plants": plant_count, "generation": generation}
        )
        self.fitness_history.append({"tick": tick, "avg": avg_fitness, "best": best_fitness})

    def record_birth(self, tick: int, name: str, position: Tuple[float, float], parents: List[str], generation: int) -> None:
        """Record a birth event."""
        self.total_births += 1
        self.birth_locations.append(position)
        self.events.append(EventRecord(tick=tick, event_type="birth", data={"name": name, "position": position}))
        
        # Update family tree
        self.family_tree[name] = {
            "generation": generation,
            "parents": parents,
            "birth_tick": tick,
            "birth_position": position,
            "fitness_history": [],
        }

    def record_death(
        self,
        tick: int,
        name: str,
        position: Tuple[float, float],
        age: float,
        fitness: float,
        generation: int,
        brain_type: str = "random",
    ) -> None:
        """Record a death event."""
        self.total_deaths += 1
        self.death_locations.append(position)
        self.events.append(
            EventRecord(
                tick=tick,
                event_type="death",
                data={"name": name, "position": position, "age": age, "fitness": fitness, "generation": generation},
            )
        )
        
        bucket = self.brain_type_stats.setdefault(
            brain_type, {"deaths": 0, "lifespan_sum": 0.0, "fitness_sum": 0.0, "best_fitness": float("-inf"), "max_generation": 0}
        )
        bucket["deaths"] += 1
        bucket["lifespan_sum"] += age
        bucket["fitness_sum"] += fitness
        bucket["best_fitness"] = max(bucket["best_fitness"], fitness)
        bucket["max_generation"] = max(bucket["max_generation"], generation)

        # Update family tree; the per-tick fitness history is dropped since final values are kept.
        if name in self.family_tree:
            self.family_tree[name]["death_tick"] = tick
            self.family_tree[name]["final_fitness"] = fitness
            self.family_tree[name]["lifespan"] = age
            self.family_tree[name].pop("fitness_history", None)

    def record_disease(self, tick: int, name: str, event_type: str) -> None:
        """Record an 'infection' or 'recovery' event."""
        if event_type == "infection":
            self.total_infections += 1
        else:
            self.total_recoveries += 1
        self.events.append(EventRecord(tick=tick, event_type=event_type, data={"name": name}))

    def get_brain_type_summary(self, alive_counts: Optional[Dict[str, int]] = None) -> Dict[str, Dict[str, float]]:
        """Per brain type: alive, deaths, avg_lifespan, avg_fitness, best_fitness, max_generation."""
        alive_counts = alive_counts or {}
        summary = {}
        for brain_type in sorted(set(self.brain_type_stats) | set(alive_counts)):
            b = self.brain_type_stats.get(brain_type, {})
            deaths = int(b.get("deaths", 0))
            summary[brain_type] = {
                "alive": int(alive_counts.get(brain_type, 0)),
                "deaths": deaths,
                "avg_lifespan": b.get("lifespan_sum", 0.0) / deaths if deaths else 0.0,
                "avg_fitness": b.get("fitness_sum", 0.0) / deaths if deaths else 0.0,
                "best_fitness": b.get("best_fitness", 0.0) if deaths else 0.0,
                "max_generation": int(b.get("max_generation", 0)),
            }
        return summary

    _COUNTERS = (
        "total_births", "total_deaths", "total_plants_consumed", "total_generations",
        "extinct_species", "total_infections", "total_recoveries",
    )

    def to_save_dict(self) -> Dict[str, Any]:
        """Compact persistent block for World.save.

        ponytail: events, heatmaps, learning curves and family tree are not persisted (file size).
        """
        data: Dict[str, Any] = {key: getattr(self, key) for key in self._COUNTERS}
        data["generation_history"] = [dataclasses.asdict(g) for g in self.generation_history]
        data["brain_type_stats"] = self.brain_type_stats
        return data

    def load_save_dict(self, block: Dict[str, Any]) -> None:
        for key in self._COUNTERS:
            setattr(self, key, block.get(key, 0))
        fields = GenerationStats.__dataclass_fields__
        self.generation_history = [
            GenerationStats(**{k: v for k, v in g.items() if k in fields}) for g in block.get("generation_history", [])
        ]
        self.brain_type_stats = {k: dict(v) for k, v in block.get("brain_type_stats", {}).items()}

    def record_food_consumption(self, tick: int, position: Tuple[float, float], amount: float) -> None:
        """Record food consumption event."""
        self.total_plants_consumed += 1
        self.food_consumption_locations.append(position)

    def record_generation(self, stats: GenerationStats) -> None:
        """Record statistics for a completed generation."""
        self.generation_history.append(stats)
        self.total_generations = stats.generation
        self.clear_spatial_data()

    MAX_LEARNING_CURVES = 200

    def record_learning_progress(self, name: str, tick: int, fitness: float) -> None:
        """Record learning progress for an individual creature."""
        if name not in self.learning_curves:
            if len(self.learning_curves) >= self.MAX_LEARNING_CURVES:
                # ponytail: oldest creature's curve is evicted; long runs lose early curves.
                self.learning_curves.pop(next(iter(self.learning_curves)))
            self.learning_curves[name] = []
        self.learning_curves[name].append((tick, fitness))

        # Update family tree with fitness history (living creatures only; dropped on death)
        node = self.family_tree.get(name)
        if node is not None and "fitness_history" in node:
            node["fitness_history"].append((tick, fitness))

    def create_snapshot(self, name: str, world_state: Dict[str, Any]) -> None:
        """Create a snapshot of the current world state."""
        self.snapshots[name] = {
            "timestamp": len(self.population_history),
            "tick": world_state.get("tick_count", 0),
            "state": world_state,
            "total_births": self.total_births,
            "total_deaths": self.total_deaths,
        }

    def get_population_data(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get population history data."""
        data = list(self.population_history)
        if last_n:
            return data[-last_n:]
        return data

    def get_fitness_data(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get fitness history data."""
        data = list(self.fitness_history)
        if last_n:
            return data[-last_n:]
        return data

    def get_heatmap_data(
        self, data_type: str, world_size: Tuple[float, float], resolution: int = 20
    ) -> np.ndarray:
        """Generate heatmap data for visualization."""
        width, height = world_size
        heatmap = np.zeros((resolution, resolution))

        if data_type == "births":
            locations = self.birth_locations
        elif data_type == "deaths":
            locations = self.death_locations
        elif data_type == "food":
            locations = self.food_consumption_locations
        else:
            return heatmap

        for x, y in locations:
            grid_x = int((x / width) * resolution)
            grid_y = int((y / height) * resolution)
            grid_x = min(grid_x, resolution - 1)
            grid_y = min(grid_y, resolution - 1)
            heatmap[grid_y, grid_x] += 1

        return heatmap

    def get_lineage(self, name: str, depth: int = 5) -> List[Dict[str, Any]]:
        """Get lineage information for a creature."""
        lineage = []
        current = name

        for _ in range(depth):
            if current not in self.family_tree:
                break

            node = self.family_tree[current]
            lineage.append({"name": current, **node})

            parents = node.get("parents", [])
            if not parents:
                break
            current = parents[0]

        return lineage

    def get_descendants(self, name: str) -> List[str]:
        """Get all descendants of a creature."""
        descendants = []
        for creature_name, data in self.family_tree.items():
            if name in data.get("parents", []):
                descendants.append(creature_name)
                descendants.extend(self.get_descendants(creature_name))
        return descendants

    def get_recent_events(self, count: int = 10, event_type: Optional[str] = None) -> List[EventRecord]:
        """Get recent events, optionally filtered by type."""
        events = list(self.events)
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-count:]

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all statistics."""
        return {
            "total_births": self.total_births,
            "total_deaths": self.total_deaths,
            "total_plants_consumed": self.total_plants_consumed,
            "total_generations": self.total_generations,
            "extinct_species": self.extinct_species,
            "current_population": self.population_history[-1] if self.population_history else {},
            "current_fitness": self.fitness_history[-1] if self.fitness_history else {},
            "tracked_creatures": len(self.learning_curves),
            "snapshots": list(self.snapshots.keys()),
        }

    def export_to_json(self, path: Path) -> None:
        """Export statistics to JSON file."""
        data = {
            "summary": self.get_summary(),
            "population_history": list(self.population_history),
            "fitness_history": list(self.fitness_history),
            "generation_history": [dataclasses.asdict(g) for g in self.generation_history],
            "brain_types": self.get_brain_type_summary(),
            "events": [{"tick": e.tick, "type": e.event_type, "data": e.data} for e in self.events],
            "family_tree": self.family_tree,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def export_to_csv(self, path: Path) -> None:
        """Export population and fitness data to CSV."""
        import csv

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["tick", "herbivores", "plants", "avg_fitness", "best_fitness", "generation"])

            pop_data = list(self.population_history)
            fit_data = list(self.fitness_history)

            for i in range(min(len(pop_data), len(fit_data))):
                pop = pop_data[i]
                fit = fit_data[i]
                writer.writerow(
                    [
                        pop["tick"],
                        pop["herbivores"],
                        pop["plants"],
                        fit["avg"],
                        fit["best"],
                        pop.get("generation", 0),
                    ]
                )

    def clear_spatial_data(self) -> None:
        """Clear spatial data to save memory (keep only recent data)."""
        max_locations = 10000
        if len(self.birth_locations) > max_locations:
            self.birth_locations = self.birth_locations[-max_locations:]
        if len(self.death_locations) > max_locations:
            self.death_locations = self.death_locations[-max_locations:]
        if len(self.food_consumption_locations) > max_locations:
            self.food_consumption_locations = self.food_consumption_locations[-max_locations:]
