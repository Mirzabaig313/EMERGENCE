"""Statistics tracking and historical data management for EMERGENCE."""

from __future__ import annotations

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


@dataclass
class StatisticsTracker:
    """Comprehensive statistics tracking for the EMERGENCE ecosystem."""

    # Configuration
    history_window: int = 1000
    spatial_resolution: int = 20

    # Historical data
    population_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    fitness_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    generation_history: List[GenerationStats] = field(default_factory=list)
    events: deque = field(default_factory=lambda: deque(maxlen=5000))

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
        self, tick: int, name: str, position: Tuple[float, float], age: float, fitness: float, generation: int
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
        
        # Update family tree
        if name in self.family_tree:
            self.family_tree[name]["death_tick"] = tick
            self.family_tree[name]["final_fitness"] = fitness
            self.family_tree[name]["lifespan"] = age

    def record_food_consumption(self, tick: int, position: Tuple[float, float], amount: float) -> None:
        """Record food consumption event."""
        self.total_plants_consumed += 1
        self.food_consumption_locations.append(position)

    def record_generation(self, stats: GenerationStats) -> None:
        """Record statistics for a completed generation."""
        self.generation_history.append(stats)
        self.total_generations = stats.generation

    def record_learning_progress(self, name: str, tick: int, fitness: float) -> None:
        """Record learning progress for an individual creature."""
        if name not in self.learning_curves:
            self.learning_curves[name] = []
        self.learning_curves[name].append((tick, fitness))
        
        # Update family tree with fitness history
        if name in self.family_tree:
            self.family_tree[name]["fitness_history"].append((tick, fitness))

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
            "generation_history": [
                {
                    "generation": g.generation,
                    "tick": g.tick,
                    "population": g.population,
                    "avg_fitness": g.avg_fitness,
                    "best_fitness": g.best_fitness,
                    "avg_age": g.avg_age,
                    "avg_energy": g.avg_energy,
                    "births": g.births,
                    "deaths": g.deaths,
                    "plants_eaten": g.plants_eaten,
                }
                for g in self.generation_history
            ],
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
