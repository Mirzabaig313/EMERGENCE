"""Biome system for EMERGENCE - different terrains that affect gameplay."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

import numpy as np


class BiomeType(Enum):
    """Different biome types in the world."""
    
    PLAINS = "plains"
    FOREST = "forest"
    DESERT = "desert"
    MOUNTAINS = "mountains"
    LAKE = "lake"
    RIVER = "river"
    OCEAN = "ocean"


@dataclass
class BiomeProperties:
    """Properties that define how a biome affects gameplay."""
    
    name: str
    plant_density: float  # Plants per square unit
    movement_speed_multiplier: float  # Movement speed modifier
    hiding_effectiveness: float  # Vision range reduction for predators (0-1)
    energy_cost_multiplier: float  # Energy consumption modifier
    has_water: bool  # Whether creatures can drink here
    passable: bool  # Whether creatures can move through
    color: str  # Display color for visualization
    symbol: str  # ASCII symbol for display


# Biome definitions based on the ticket specifications
BIOME_DEFINITIONS = {
    BiomeType.PLAINS: BiomeProperties(
        name="Plains",
        plant_density=0.20,  # High: 1 plant per 5 sq units
        movement_speed_multiplier=1.0,
        hiding_effectiveness=0.0,  # No hiding spots
        energy_cost_multiplier=1.0,
        has_water=False,
        passable=True,
        color="yellow",
        symbol="🌾",
    ),
    BiomeType.FOREST: BiomeProperties(
        name="Forest",
        plant_density=0.10,  # Medium: 1 plant per 10 sq units
        movement_speed_multiplier=0.7,  # Slower movement
        hiding_effectiveness=0.5,  # 50% vision reduction
        energy_cost_multiplier=1.0,
        has_water=False,
        passable=True,
        color="green",
        symbol="🌲",
    ),
    BiomeType.DESERT: BiomeProperties(
        name="Desert",
        plant_density=0.02,  # Very low: 1 plant per 50 sq units
        movement_speed_multiplier=1.2,  # Faster, open terrain
        hiding_effectiveness=0.0,
        energy_cost_multiplier=2.0,  # +100% energy cost
        has_water=False,
        passable=True,
        color="bright_yellow",
        symbol="🏜️",
    ),
    BiomeType.MOUNTAINS: BiomeProperties(
        name="Mountains",
        plant_density=0.0,  # No plants
        movement_speed_multiplier=0.0,  # Impassable
        hiding_effectiveness=0.0,
        energy_cost_multiplier=1.0,
        has_water=False,
        passable=False,  # Cannot cross
        color="white",
        symbol="🏔️",
    ),
    BiomeType.LAKE: BiomeProperties(
        name="Lake",
        plant_density=0.30,  # Very high near water
        movement_speed_multiplier=0.5,  # Slow swimming
        hiding_effectiveness=0.0,
        energy_cost_multiplier=1.0,
        has_water=True,
        passable=True,
        color="blue",
        symbol="💧",
    ),
    BiomeType.RIVER: BiomeProperties(
        name="River",
        plant_density=0.30,  # Very high near water
        movement_speed_multiplier=0.5,  # Slow swimming
        hiding_effectiveness=0.0,
        energy_cost_multiplier=1.0,
        has_water=True,
        passable=True,
        color="cyan",
        symbol="💧",
    ),
    BiomeType.OCEAN: BiomeProperties(
        name="Ocean",
        plant_density=0.0,
        movement_speed_multiplier=0.0,
        hiding_effectiveness=0.0,
        energy_cost_multiplier=1.0,
        has_water=True,
        passable=False,  # World boundary
        color="bright_blue",
        symbol="🌊",
    ),
}


class BiomeMap:
    """Manages the biome layout of the world."""
    
    def __init__(self, width: float = 500.0, height: float = 500.0, seed: int | None = None):
        self.width = width
        self.height = height
        self.rng = np.random.default_rng(seed)
        self.resolution = 50  # Grid resolution for biome map
        self.biome_grid = self._generate_biomes()
    
    def _generate_biomes(self) -> np.ndarray:
        """Generate biome map using Perlin-like noise and rules."""
        # Create a grid to store biome types
        grid = np.full((self.resolution, self.resolution), BiomeType.PLAINS)
        
        # Generate noise-like patterns for biome placement
        noise = self._generate_noise()
        
        # Assign biomes based on noise values
        for y in range(self.resolution):
            for x in range(self.resolution):
                # Ocean at edges (5% of world)
                if x < 2 or x >= self.resolution - 2 or y < 2 or y >= self.resolution - 2:
                    grid[y, x] = BiomeType.OCEAN
                    continue
                
                # Use noise to determine biome type
                value = noise[y, x]
                
                # Plains: 40% (noise -0.2 to 0.4)
                if -0.2 <= value < 0.4:
                    grid[y, x] = BiomeType.PLAINS
                # Forest: 25% (noise 0.4 to 0.7)
                elif 0.4 <= value < 0.7:
                    grid[y, x] = BiomeType.FOREST
                # Desert: 15% (noise 0.7 to 0.9)
                elif 0.7 <= value < 0.9:
                    grid[y, x] = BiomeType.DESERT
                # Mountains: 10% (noise >= 0.9)
                elif value >= 0.9:
                    grid[y, x] = BiomeType.MOUNTAINS
                # Lakes: 5% (noise < -0.7)
                elif value < -0.7:
                    grid[y, x] = BiomeType.LAKE
                # Rivers: Connect water sources
                elif -0.7 <= value < -0.2:
                    # Rivers between lakes
                    if self.rng.random() < 0.1:
                        grid[y, x] = BiomeType.RIVER
                    else:
                        grid[y, x] = BiomeType.PLAINS
        
        return grid
    
    def _generate_noise(self) -> np.ndarray:
        """Generate Perlin-like noise for terrain."""
        # Simple noise generation using random interpolation
        # For production, could use opensimplex or similar
        noise = np.zeros((self.resolution, self.resolution))
        
        # Generate noise at multiple scales
        for scale in [4, 8, 16]:
            scaled_noise = self._generate_scale_noise(scale)
            noise += scaled_noise / scale
        
        # Normalize to [-1, 1]
        noise = (noise - noise.min()) / (noise.max() - noise.min()) * 2 - 1
        return noise
    
    def _generate_scale_noise(self, scale: int) -> np.ndarray:
        """Generate noise at a specific scale."""
        small = self.rng.random((scale, scale))
        factor = max(1, int(np.ceil(self.resolution / scale)))
        large = np.kron(small, np.ones((factor, factor)))
        return large[: self.resolution, : self.resolution]
    
    def get_biome_at(self, x: float, y: float) -> BiomeType:
        """Get the biome type at a world position."""
        # Convert world coordinates to grid coordinates
        grid_x = int((x / self.width) * self.resolution)
        grid_y = int((y / self.height) * self.resolution)
        
        # Clamp to grid bounds
        grid_x = max(0, min(self.resolution - 1, grid_x))
        grid_y = max(0, min(self.resolution - 1, grid_y))
        
        return self.biome_grid[grid_y, grid_x]
    
    def get_biome_properties(self, x: float, y: float) -> BiomeProperties:
        """Get the biome properties at a world position."""
        biome_type = self.get_biome_at(x, y)
        return BIOME_DEFINITIONS[biome_type]
    
    def is_position_passable(self, x: float, y: float) -> bool:
        """Check if a position is passable (not mountains or ocean)."""
        properties = self.get_biome_properties(x, y)
        return properties.passable
    
    def get_movement_multiplier(self, x: float, y: float) -> float:
        """Get movement speed multiplier at a position."""
        properties = self.get_biome_properties(x, y)
        return properties.movement_speed_multiplier
    
    def get_energy_multiplier(self, x: float, y: float) -> float:
        """Get energy cost multiplier at a position."""
        properties = self.get_biome_properties(x, y)
        return properties.energy_cost_multiplier
    
    def get_plant_spawn_probability(self, x: float, y: float) -> float:
        """Get plant spawn probability at a position."""
        properties = self.get_biome_properties(x, y)
        return properties.plant_density
    
    def has_water_source(self, x: float, y: float) -> bool:
        """Check if position has water."""
        properties = self.get_biome_properties(x, y)
        return properties.has_water
    
    def get_hiding_effectiveness(self, x: float, y: float) -> float:
        """Get hiding effectiveness (vision reduction) at a position."""
        properties = self.get_biome_properties(x, y)
        return properties.hiding_effectiveness
