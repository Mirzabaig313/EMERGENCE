"""Progression system with Evolution Points, achievements, and unlocks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class AchievementType(Enum):
    """Types of achievements."""
    
    # Survival achievements
    FIRST_STEPS = "first_steps"  # Generation 10
    SEASONED = "seasoned"  # Generation 50
    MASTER = "master"  # Generation 100
    IMMORTAL = "immortal"  # Generation 200
    
    # Population achievements
    THRIVING = "thriving"  # Population 50+
    ECOSYSTEM_BUILDER = "ecosystem_builder"  # 5 species coexisting
    HARMONY = "harmony"  # All species alive simultaneously
    
    # Evolution achievements
    NATURAL_SELECTION = "natural_selection"  # 10 successful mutations
    GUIDING_HAND = "guiding_hand"  # Teach 100 behaviors
    GENETIC_ENGINEER = "genetic_engineer"  # Breed 1000+ fitness creature
    APEX_CREATOR = "apex_creator"  # Evolve Dragon or Unicorn
    
    # Challenge achievements
    SURVIVOR = "survivor"  # Complete any challenge mode
    MASTER_STRATEGIST = "master_strategist"  # Complete all challenges
    IRON_ECOSYSTEM = "iron_ecosystem"  # Win on hard difficulty
    
    # Discovery achievements
    FIRST_BLOOD = "first_blood"  # First predator kill
    PACK_MENTALITY = "pack_mentality"  # Witness pack behavior
    RARE_FIND = "rare_find"  # Discover camouflage creature
    LEGENDARY = "legendary"  # Witness mythical creature
    APEX_OF_EVOLUTION = "apex_of_evolution"  # Avg fitness exceeds 1000


@dataclass
class Achievement:
    """Achievement definition."""
    
    id: AchievementType
    name: str
    description: str
    ep_reward: int
    unlocked: bool = False
    progress: float = 0.0
    max_progress: float = 1.0


# Achievement definitions
ACHIEVEMENT_DEFINITIONS = {
    AchievementType.FIRST_STEPS: Achievement(
        id=AchievementType.FIRST_STEPS,
        name="🥉 First Steps",
        description="Reach Generation 10",
        ep_reward=10,
        max_progress=10,
    ),
    AchievementType.SEASONED: Achievement(
        id=AchievementType.SEASONED,
        name="🥈 Seasoned",
        description="Reach Generation 50",
        ep_reward=25,
        max_progress=50,
    ),
    AchievementType.MASTER: Achievement(
        id=AchievementType.MASTER,
        name="🥇 Master",
        description="Reach Generation 100",
        ep_reward=50,
        max_progress=100,
    ),
    AchievementType.IMMORTAL: Achievement(
        id=AchievementType.IMMORTAL,
        name="💎 Immortal",
        description="Reach Generation 200",
        ep_reward=100,
        max_progress=200,
    ),
    AchievementType.THRIVING: Achievement(
        id=AchievementType.THRIVING,
        name="Thriving",
        description="Reach population of 50+",
        ep_reward=20,
        max_progress=50,
    ),
    AchievementType.ECOSYSTEM_BUILDER: Achievement(
        id=AchievementType.ECOSYSTEM_BUILDER,
        name="Ecosystem Builder",
        description="5 species coexisting",
        ep_reward=30,
        max_progress=5,
    ),
    AchievementType.HARMONY: Achievement(
        id=AchievementType.HARMONY,
        name="Harmony",
        description="All species alive simultaneously",
        ep_reward=50,
        max_progress=1,
    ),
    AchievementType.NATURAL_SELECTION: Achievement(
        id=AchievementType.NATURAL_SELECTION,
        name="Natural Selection",
        description="10 successful mutations",
        ep_reward=15,
        max_progress=10,
    ),
    AchievementType.GUIDING_HAND: Achievement(
        id=AchievementType.GUIDING_HAND,
        name="Guiding Hand",
        description="Teach 100 behaviors",
        ep_reward=25,
        max_progress=100,
    ),
    AchievementType.GENETIC_ENGINEER: Achievement(
        id=AchievementType.GENETIC_ENGINEER,
        name="Genetic Engineer",
        description="Breed creature with 1000+ fitness",
        ep_reward=40,
        max_progress=1000,
    ),
    AchievementType.APEX_CREATOR: Achievement(
        id=AchievementType.APEX_CREATOR,
        name="Apex Creator",
        description="Evolve Dragon or Unicorn",
        ep_reward=100,
    ),
    AchievementType.SURVIVOR: Achievement(
        id=AchievementType.SURVIVOR,
        name="Survivor",
        description="Complete any challenge mode",
        ep_reward=30,
    ),
    AchievementType.MASTER_STRATEGIST: Achievement(
        id=AchievementType.MASTER_STRATEGIST,
        name="Master Strategist",
        description="Complete all challenges",
        ep_reward=75,
        max_progress=4,
    ),
    AchievementType.IRON_ECOSYSTEM: Achievement(
        id=AchievementType.IRON_ECOSYSTEM,
        name="Iron Ecosystem",
        description="Win on hard difficulty",
        ep_reward=50,
    ),
    AchievementType.FIRST_BLOOD: Achievement(
        id=AchievementType.FIRST_BLOOD,
        name="First Blood",
        description="First predator kill",
        ep_reward=10,
    ),
    AchievementType.PACK_MENTALITY: Achievement(
        id=AchievementType.PACK_MENTALITY,
        name="Pack Mentality",
        description="Witness pack behavior",
        ep_reward=20,
    ),
    AchievementType.RARE_FIND: Achievement(
        id=AchievementType.RARE_FIND,
        name="Rare Find",
        description="Discover camouflage creature",
        ep_reward=30,
    ),
    AchievementType.LEGENDARY: Achievement(
        id=AchievementType.LEGENDARY,
        name="Legendary",
        description="Witness mythical creature",
        ep_reward=75,
    ),
    AchievementType.APEX_OF_EVOLUTION: Achievement(
        id=AchievementType.APEX_OF_EVOLUTION,
        name="Apex of Evolution",
        description="Average fitness exceeds 1000",
        ep_reward=60,
        max_progress=1000,
    ),
}


class UnlockType(Enum):
    """Types of unlockable content."""
    
    # Creatures
    CARNIVORES = "carnivores"
    APEX_PREDATORS = "apex_predators"
    SCAVENGERS = "scavengers"
    OMNIVORES = "omnivores"
    CAMOUFLAGE = "camouflage"
    
    # Abilities
    MUTATION_BOOST = "mutation_boost"
    ADVANCED_TEACHING = "advanced_teaching"
    DIVINE_INTERVENTION = "divine_intervention"
    WEATHER_CONTROL = "weather_control"
    TIME_WARP = "time_warp"
    
    # Challenges
    DROUGHT_CHALLENGE = "drought_challenge"
    ICE_AGE_CHALLENGE = "ice_age_challenge"
    INVASION_CHALLENGE = "invasion_challenge"
    EXTINCTION_CHALLENGE = "extinction_challenge"


@dataclass
class Unlock:
    """Unlockable content definition."""
    
    id: UnlockType
    name: str
    description: str
    ep_cost: int
    unlocked: bool = False


UNLOCK_DEFINITIONS = {
    UnlockType.CARNIVORES: Unlock(
        id=UnlockType.CARNIVORES,
        name="Carnivores",
        description="Unlock small predators",
        ep_cost=20,
    ),
    UnlockType.APEX_PREDATORS: Unlock(
        id=UnlockType.APEX_PREDATORS,
        name="Apex Predators",
        description="Unlock powerful apex predators",
        ep_cost=30,
    ),
    UnlockType.SCAVENGERS: Unlock(
        id=UnlockType.SCAVENGERS,
        name="Scavengers",
        description="Unlock efficient scavengers",
        ep_cost=25,
    ),
    UnlockType.OMNIVORES: Unlock(
        id=UnlockType.OMNIVORES,
        name="Omnivores",
        description="Unlock flexible omnivores",
        ep_cost=25,
    ),
    UnlockType.CAMOUFLAGE: Unlock(
        id=UnlockType.CAMOUFLAGE,
        name="Camouflage Creatures",
        description="Unlock stealth creatures",
        ep_cost=35,
    ),
    UnlockType.MUTATION_BOOST: Unlock(
        id=UnlockType.MUTATION_BOOST,
        name="Mutation Boost",
        description="Increase mutation rate by 50%",
        ep_cost=10,
    ),
    UnlockType.ADVANCED_TEACHING: Unlock(
        id=UnlockType.ADVANCED_TEACHING,
        name="Advanced Teaching",
        description="Creatures learn faster",
        ep_cost=15,
    ),
    UnlockType.DIVINE_INTERVENTION: Unlock(
        id=UnlockType.DIVINE_INTERVENTION,
        name="Divine Intervention",
        description="Save creatures from death (3 uses)",
        ep_cost=20,
    ),
    UnlockType.WEATHER_CONTROL: Unlock(
        id=UnlockType.WEATHER_CONTROL,
        name="Weather Control",
        description="Control weather events",
        ep_cost=25,
    ),
    UnlockType.TIME_WARP: Unlock(
        id=UnlockType.TIME_WARP,
        name="Time Warp",
        description="Skip 10 generations instantly",
        ep_cost=30,
    ),
    UnlockType.DROUGHT_CHALLENGE: Unlock(
        id=UnlockType.DROUGHT_CHALLENGE,
        name="Drought Challenge",
        description="Survive reduced plant growth",
        ep_cost=5,
    ),
    UnlockType.ICE_AGE_CHALLENGE: Unlock(
        id=UnlockType.ICE_AGE_CHALLENGE,
        name="Ice Age Challenge",
        description="Survive harsh conditions",
        ep_cost=10,
    ),
    UnlockType.INVASION_CHALLENGE: Unlock(
        id=UnlockType.INVASION_CHALLENGE,
        name="Invasion Challenge",
        description="Survive predator invasion",
        ep_cost=15,
    ),
    UnlockType.EXTINCTION_CHALLENGE: Unlock(
        id=UnlockType.EXTINCTION_CHALLENGE,
        name="Extinction Challenge",
        description="Recover from population wipe",
        ep_cost=15,
    ),
}


@dataclass
class ProgressionTracker:
    """Tracks player progression, achievements, and unlocks."""
    
    evolution_points: int = 0
    total_ep_earned: int = 0
    achievements: Dict[AchievementType, Achievement] = field(default_factory=dict)
    unlocks: Dict[UnlockType, Unlock] = field(default_factory=dict)
    
    # Statistics for achievements
    mutations_count: int = 0
    teachings_count: int = 0
    predator_kills: int = 0
    challenges_completed: Set[str] = field(default_factory=set)
    
    # Divine intervention uses
    divine_saves_remaining: int = 0
    
    def __post_init__(self):
        """Initialize achievements and unlocks."""
        if not self.achievements:
            self.achievements = {k: Achievement(**v.__dict__) for k, v in ACHIEVEMENT_DEFINITIONS.items()}
        if not self.unlocks:
            self.unlocks = {k: Unlock(**v.__dict__) for k, v in UNLOCK_DEFINITIONS.items()}
    
    def earn_ep(self, amount: int, reason: str = "") -> str:
        """Award Evolution Points."""
        self.evolution_points += amount
        self.total_ep_earned += amount
        return f"+{amount} EP earned! {reason}"
    
    def spend_ep(self, amount: int) -> bool:
        """Spend Evolution Points if available."""
        if self.evolution_points >= amount:
            self.evolution_points -= amount
            return True
        return False
    
    def unlock_content(self, unlock_type: UnlockType) -> tuple[bool, str]:
        """Unlock content with EP."""
        unlock = self.unlocks.get(unlock_type)
        if not unlock:
            return False, "Unknown unlock"
        
        if unlock.unlocked:
            return False, f"{unlock.name} already unlocked"
        
        if self.spend_ep(unlock.ep_cost):
            unlock.unlocked = True
            if unlock_type == UnlockType.DIVINE_INTERVENTION:
                self.divine_saves_remaining += 3
            return True, f"Unlocked: {unlock.name}! (-{unlock.ep_cost} EP)"
        
        return False, f"Need {unlock.ep_cost} EP (have {self.evolution_points})"
    
    def check_achievement(self, achievement_type: AchievementType, current_value: float = 1.0) -> tuple[bool, str]:
        """Check and unlock achievement if conditions met."""
        achievement = self.achievements.get(achievement_type)
        if not achievement or achievement.unlocked:
            return False, ""
        
        achievement.progress = current_value
        
        if current_value >= achievement.max_progress:
            achievement.unlocked = True
            reward = achievement.ep_reward
            self.earn_ep(reward, f"Achievement: {achievement.name}")
            return True, f"🏆 ACHIEVEMENT: {achievement.name} unlocked! +{reward} EP"
        
        return False, ""
    
    def update_generation_achievements(self, generation: int):
        """Update generation-based achievements."""
        messages = []
        
        unlocked, msg = self.check_achievement(AchievementType.FIRST_STEPS, generation)
        if unlocked:
            messages.append(msg)
        
        unlocked, msg = self.check_achievement(AchievementType.SEASONED, generation)
        if unlocked:
            messages.append(msg)
        
        unlocked, msg = self.check_achievement(AchievementType.MASTER, generation)
        if unlocked:
            messages.append(msg)
        
        unlocked, msg = self.check_achievement(AchievementType.IMMORTAL, generation)
        if unlocked:
            messages.append(msg)
        
        return messages
    
    def update_population_achievements(self, total_population: int, num_species: int):
        """Update population-based achievements."""
        messages = []
        
        unlocked, msg = self.check_achievement(AchievementType.THRIVING, total_population)
        if unlocked:
            messages.append(msg)
        
        unlocked, msg = self.check_achievement(AchievementType.ECOSYSTEM_BUILDER, num_species)
        if unlocked:
            messages.append(msg)
        
        return messages
    
    def update_fitness_achievement(self, avg_fitness: float):
        """Update fitness-based achievements."""
        messages = []
        
        unlocked, msg = self.check_achievement(AchievementType.APEX_OF_EVOLUTION, avg_fitness)
        if unlocked:
            messages.append(msg)
        
        return messages
    
    def record_mutation(self):
        """Record a mutation event."""
        self.mutations_count += 1
        messages = []
        unlocked, msg = self.check_achievement(AchievementType.NATURAL_SELECTION, self.mutations_count)
        if unlocked:
            messages.append(msg)
        return messages
    
    def record_teaching(self):
        """Record a teaching event."""
        self.teachings_count += 1
        messages = []
        unlocked, msg = self.check_achievement(AchievementType.GUIDING_HAND, self.teachings_count)
        if unlocked:
            messages.append(msg)
        return messages
    
    def record_predator_kill(self):
        """Record a predator kill."""
        self.predator_kills += 1
        messages = []
        if self.predator_kills == 1:
            unlocked, msg = self.check_achievement(AchievementType.FIRST_BLOOD, 1)
            if unlocked:
                messages.append(msg)
        return messages
    
    def record_mythical_creature(self):
        """Record witnessing a mythical creature."""
        messages = []
        unlocked, msg = self.check_achievement(AchievementType.LEGENDARY, 1)
        if unlocked:
            messages.append(msg)
        unlocked, msg = self.check_achievement(AchievementType.APEX_CREATOR, 1)
        if unlocked:
            messages.append(msg)
        return messages
    
    def is_unlocked(self, unlock_type: UnlockType) -> bool:
        """Check if content is unlocked."""
        unlock = self.unlocks.get(unlock_type)
        return unlock.unlocked if unlock else False
    
    def get_unlocked_list(self) -> List[str]:
        """Get list of unlocked content."""
        return [unlock.name for unlock in self.unlocks.values() if unlock.unlocked]
    
    def get_achievements_summary(self) -> Dict[str, int]:
        """Get summary of achievements."""
        total = len(self.achievements)
        unlocked = sum(1 for a in self.achievements.values() if a.unlocked)
        return {
            "total": total,
            "unlocked": unlocked,
            "percentage": int((unlocked / total * 100) if total > 0 else 0),
        }
