"""Random events system for EMERGENCE."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

import numpy as np


class EventType(Enum):
    """Types of random events."""
    
    # Positive events
    ABUNDANT_RAIN = "abundant_rain"
    FERTILE_SEASON = "fertile_season"
    PEACE_PERIOD = "peace_period"
    EVOLUTION_BOOST = "evolution_boost"
    DISCOVERY = "discovery"
    
    # Negative events
    DROUGHT = "drought"
    PREDATOR_INVASION = "predator_invasion"
    DISEASE = "disease"
    FOOD_CONTAMINATION = "food_contamination"
    NATURAL_DISASTER = "natural_disaster"
    
    # Neutral events
    MIGRATION = "migration"
    SEASON_CHANGE = "season_change"
    COMET_SIGHTING = "comet_sighting"
    ANCIENT_RUINS = "ancient_ruins"


@dataclass
class RandomEvent:
    """Random event definition."""
    
    id: EventType
    name: str
    description: str
    duration: int  # Duration in generations
    probability: float  # Chance of occurring per generation
    modifiers: Dict[str, float]  # Gameplay modifiers
    visual_symbol: str
    color: str
    
    # Event state
    active: bool = False
    remaining_duration: int = 0


# Event definitions
EVENT_DEFINITIONS: Dict[EventType, RandomEvent] = {
    # Positive events
    EventType.ABUNDANT_RAIN: RandomEvent(
        id=EventType.ABUNDANT_RAIN,
        name="Abundant Rain",
        description="Plant growth +100% for 10 generations",
        duration=10,
        probability=0.05,
        modifiers={"plant_growth_multiplier": 2.0},
        visual_symbol="🌧️",
        color="cyan",
    ),
    EventType.FERTILE_SEASON: RandomEvent(
        id=EventType.FERTILE_SEASON,
        name="Fertile Season",
        description="Reproduction success +50%",
        duration=15,
        probability=0.04,
        modifiers={"reproduction_threshold_multiplier": 0.8},
        visual_symbol="🌸",
        color="magenta",
    ),
    EventType.PEACE_PERIOD: RandomEvent(
        id=EventType.PEACE_PERIOD,
        name="Peace Period",
        description="No predator spawns for 5 generations",
        duration=5,
        probability=0.02,
        modifiers={"predator_spawn_blocked": 1.0},
        visual_symbol="🕊️",
        color="white",
    ),
    EventType.EVOLUTION_BOOST: RandomEvent(
        id=EventType.EVOLUTION_BOOST,
        name="Evolution Boost",
        description="Mutation chance +200%",
        duration=8,
        probability=0.03,
        modifiers={"mutation_rate_multiplier": 3.0},
        visual_symbol="⚡",
        color="yellow",
    ),
    EventType.DISCOVERY: RandomEvent(
        id=EventType.DISCOVERY,
        name="Discovery",
        description="New safe zone revealed",
        duration=1,
        probability=0.01,
        modifiers={"safe_zone_added": 1.0},
        visual_symbol="🗺️",
        color="green",
    ),
    
    # Negative events
    EventType.DROUGHT: RandomEvent(
        id=EventType.DROUGHT,
        name="Drought",
        description="Plant growth -70% for 20 generations",
        duration=20,
        probability=0.03,
        modifiers={"plant_growth_multiplier": 0.3},
        visual_symbol="☀️",
        color="bright_yellow",
    ),
    EventType.PREDATOR_INVASION: RandomEvent(
        id=EventType.PREDATOR_INVASION,
        name="Predator Invasion",
        description="5 extra predators spawn",
        duration=1,
        probability=0.02,
        modifiers={"extra_predator_spawns": 5},
        visual_symbol="⚠️",
        color="red",
    ),
    EventType.DISEASE: RandomEvent(
        id=EventType.DISEASE,
        name="Disease",
        description="Random creatures lose 50% health",
        duration=1,
        probability=0.02,
        modifiers={"health_reduction": 0.5},
        visual_symbol="🦠",
        color="bright_red",
    ),
    EventType.FOOD_CONTAMINATION: RandomEvent(
        id=EventType.FOOD_CONTAMINATION,
        name="Food Contamination",
        description="Plants give less energy",
        duration=12,
        probability=0.03,
        modifiers={"plant_energy_multiplier": 0.6},
        visual_symbol="☠️",
        color="purple",
    ),
    EventType.NATURAL_DISASTER: RandomEvent(
        id=EventType.NATURAL_DISASTER,
        name="Natural Disaster",
        description="20% population loss",
        duration=1,
        probability=0.01,
        modifiers={"population_kill_rate": 0.2},
        visual_symbol="💥",
        color="bright_red",
    ),
    
    # Neutral events
    EventType.MIGRATION: RandomEvent(
        id=EventType.MIGRATION,
        name="Migration",
        description="Creatures move to new areas",
        duration=5,
        probability=0.04,
        modifiers={"migration_force": 1.0},
        visual_symbol="🦋",
        color="blue",
    ),
    EventType.SEASON_CHANGE: RandomEvent(
        id=EventType.SEASON_CHANGE,
        name="Season Change",
        description="Biome properties shift",
        duration=20,
        probability=0.03,
        modifiers={"biome_shift": 1.0},
        visual_symbol="🍂",
        color="orange",
    ),
    EventType.COMET_SIGHTING: RandomEvent(
        id=EventType.COMET_SIGHTING,
        name="Comet Sighting",
        description="Mythical mutation chance +500%",
        duration=3,
        probability=0.005,
        modifiers={"mythical_mutation_multiplier": 6.0},
        visual_symbol="☄️",
        color="bright_magenta",
    ),
    EventType.ANCIENT_RUINS: RandomEvent(
        id=EventType.ANCIENT_RUINS,
        name="Ancient Ruins Found",
        description="New explorable area unlocked",
        duration=1,
        probability=0.01,
        modifiers={"new_area_unlocked": 1.0},
        visual_symbol="🏛️",
        color="bright_white",
    ),
}


class EventManager:
    """Manages random events in the simulation."""
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.default_rng(seed)
        self.active_events: Dict[EventType, RandomEvent] = {}
        self.event_history: list[tuple[int, EventType, str]] = []
        self.enabled = True
    
    def trigger_event(self, event_type: EventType, generation: int) -> str:
        """Manually trigger an event."""
        event_def = EVENT_DEFINITIONS[event_type]
        event = RandomEvent(**event_def.__dict__)
        event.active = True
        event.remaining_duration = event.duration
        
        self.active_events[event_type] = event
        self.event_history.append((generation, event_type, f"{event.name} started"))
        
        return f"{event.visual_symbol} {event.name}: {event.description}"
    
    def check_random_events(self, generation: int, current_conditions: Dict[str, float]) -> list[str]:
        """Check for and trigger random events based on probabilities."""
        if not self.enabled:
            return []
        
        messages = []
        
        # Roll for each possible event
        for event_type, event_def in EVENT_DEFINITIONS.items():
            # Don't trigger if already active
            if event_type in self.active_events:
                continue
            
            # Check if event should trigger
            if self.rng.random() < event_def.probability:
                msg = self.trigger_event(event_type, generation)
                messages.append(msg)
        
        return messages
    
    def update_events(self, generation: int) -> list[str]:
        """Update active events and expire finished ones."""
        messages = []
        expired = []
        
        for event_type, event in self.active_events.items():
            event.remaining_duration -= 1
            
            if event.remaining_duration <= 0:
                event.active = False
                expired.append(event_type)
                msg = f"{event.name} has ended"
                messages.append(msg)
                self.event_history.append((generation, event_type, f"{event.name} ended"))
        
        # Remove expired events
        for event_type in expired:
            del self.active_events[event_type]
        
        return messages
    
    def get_active_modifiers(self) -> Dict[str, float]:
        """Get all active gameplay modifiers from events."""
        modifiers: Dict[str, float] = {}
        
        for event in self.active_events.values():
            for key, value in event.modifiers.items():
                # Multiply multipliers, add others
                if "multiplier" in key:
                    modifiers[key] = modifiers.get(key, 1.0) * value
                else:
                    modifiers[key] = modifiers.get(key, 0.0) + value
        
        return modifiers
    
    def get_active_events_display(self) -> list[str]:
        """Get display strings for active events."""
        displays = []
        for event in self.active_events.values():
            display = f"{event.visual_symbol} {event.name} ({event.remaining_duration} gen remaining)"
            displays.append(display)
        return displays
    
    def clear_all_events(self) -> None:
        """Clear all active events."""
        self.active_events.clear()
    
    def enable_events(self, enabled: bool = True) -> None:
        """Enable or disable random events."""
        self.enabled = enabled
