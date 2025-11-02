"""Game modes and challenges for EMERGENCE."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class Difficulty(Enum):
    """Difficulty levels for game modes."""
    
    CREATIVE = "creative"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class GameModeType(Enum):
    """Types of game modes."""
    
    SURVIVAL = "survival"
    CHALLENGE = "challenge"
    SANDBOX = "sandbox"
    SPEEDRUN = "speedrun"


@dataclass
class GameMode:
    """Game mode definition."""
    
    id: GameModeType
    name: str
    description: str
    difficulty: Difficulty
    start_population: int
    start_plants: int
    win_generation: int
    min_population: int
    unlock_requirements: Optional[str] = None


GAME_MODES: Dict[GameModeType, GameMode] = {
    GameModeType.SURVIVAL: GameMode(
        id=GameModeType.SURVIVAL,
        name="Survival Mode",
        description="Keep ecosystem alive for 100 generations",
        difficulty=Difficulty.MEDIUM,
        start_population=10,
        start_plants=60,
        win_generation=100,
        min_population=20,
    ),
    GameModeType.CHALLENGE: GameMode(
        id=GameModeType.CHALLENGE,
        name="Challenge Mode",
        description="Face pre-set survival scenarios",
        difficulty=Difficulty.HARD,
        start_population=20,
        start_plants=40,
        win_generation=0,
        min_population=0,
    ),
    GameModeType.SANDBOX: GameMode(
        id=GameModeType.SANDBOX,
        name="Sandbox Mode",
        description="Unlimited creativity, no win condition",
        difficulty=Difficulty.CREATIVE,
        start_population=25,
        start_plants=100,
        win_generation=0,
        min_population=0,
    ),
    GameModeType.SPEEDRUN: GameMode(
        id=GameModeType.SPEEDRUN,
        name="Speedrun Mode",
        description="Reach Generation 100 as fast as possible",
        difficulty=Difficulty.EXPERT,
        start_population=15,
        start_plants=50,
        win_generation=100,
        min_population=20,
    ),
}


class ChallengeType(Enum):
    """Different challenge scenarios."""
    
    DROUGHT = "drought"
    PREDATOR_INVASION = "predator_invasion"
    ICE_AGE = "ice_age"
    EXTINCTION_EVENT = "extinction_event"


@dataclass
class ChallengeScenario:
    """Challenge scenario definition."""
    
    id: ChallengeType
    name: str
    description: str
    duration_generations: int
    modifiers: Dict[str, float]
    start_generation: int = 0
    win_condition: str = ""


CHALLENGES: Dict[ChallengeType, ChallengeScenario] = {
    ChallengeType.DROUGHT: ChallengeScenario(
        id=ChallengeType.DROUGHT,
        name="The Drought",
        description="90% reduced plant growth for 50 generations",
        duration_generations=50,
        modifiers={"plant_growth_multiplier": 0.1},
        start_generation=1,
        win_condition="Survive drought period",
    ),
    ChallengeType.PREDATOR_INVASION: ChallengeScenario(
        id=ChallengeType.PREDATOR_INVASION,
        name="Predator Invasion",
        description="Survive 20 carnivores spawning at Generation 30",
        duration_generations=30,
        modifiers={"carnivore_spawns": 20, "spawn_generation": 30},
        start_generation=30,
        win_condition="Eliminate invading predators",
    ),
    ChallengeType.ICE_AGE: ChallengeScenario(
        id=ChallengeType.ICE_AGE,
        name="Ice Age",
        description="50% slower reproduction, higher energy costs",
        duration_generations=40,
        modifiers={
            "reproduction_rate_multiplier": 0.5,
            "energy_cost_multiplier": 1.5,
        },
        start_generation=10,
        win_condition="Restore stable ecosystem",
    ),
    ChallengeType.EXTINCTION_EVENT: ChallengeScenario(
        id=ChallengeType.EXTINCTION_EVENT,
        name="Extinction Event",
        description="Recover from 90% population wipe",
        duration_generations=20,
        modifiers={"population_wipe": 0.9},
        start_generation=1,
        win_condition="Restore population to pre-event levels",
    ),
}
