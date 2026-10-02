"""Game state analyzer for smart suggestions system."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from emergence.world import World
    from emergence.entities import Herbivore, Plant


class SuggestionPriority(str, Enum):
    """Priority levels for suggestions."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    TIP = "tip"


class SuggestionCategory(str, Enum):
    """Categories for suggestions."""

    HEALTH = "health"
    BREEDING = "breeding"
    MILESTONE = "milestone"
    RESOURCE = "resource"
    LEARNING = "learning"


@dataclass
class Thresholds:
    """Configuration thresholds for suggestion analysis."""

    # Energy thresholds
    CRITICAL_ENERGY: float = 20.0
    LOW_ENERGY: float = 40.0
    REPRODUCTION_ENERGY: float = 90.0

    # Health thresholds
    CRITICAL_HEALTH: float = 30.0

    # Age thresholds
    OLD_AGE: float = 450.0
    YOUNG_AGE: float = 300.0
    YOUNG_AGE_HIGH_PERFORMER: float = 200.0

    # Fitness thresholds
    HIGH_FITNESS: float = 70.0
    ELITE_FITNESS: float = 100.0
    FITNESS_RECORD: float = 150.0
    LOW_FITNESS: float = 30.0
    HIGH_PERFORMER_FITNESS: float = 80.0

    # Resource thresholds
    MIN_PLANTS: int = 20
    CRITICAL_PLANTS: int = 10
    LOW_PLANTS: int = 30
    MIN_HERBIVORES_FOR_SHORTAGE: int = 5
    MIN_HERBIVORES_FOR_CRITICAL: int = 3
    MIN_HERBIVORES_FOR_AUTO_MODE: int = 10

    # Population thresholds
    POPULATION_CRISIS: int = 5
    POPULATION_MILESTONES: Tuple[int, ...] = (20, 30, 50, 75, 100)
    GENERATION_MILESTONES: Tuple[int, ...] = (10, 15, 20, 25, 30, 40, 50, 75, 100)

    # Scoring ranges by priority
    SCORE_CRITICAL_MIN: float = 85.0
    SCORE_CRITICAL_MAX: float = 100.0
    SCORE_WARNING_MIN: float = 50.0
    SCORE_WARNING_MAX: float = 84.0
    SCORE_INFO_MIN: float = 40.0
    SCORE_INFO_MAX: float = 69.0
    SCORE_TIP_MIN: float = 30.0
    SCORE_TIP_MAX: float = 39.0

    # Deduplication
    COOLDOWN_TICKS: int = 50


@dataclass
class Suggestion:
    """A gameplay suggestion with priority and actionable command."""

    priority: SuggestionPriority
    category: SuggestionCategory
    title: str
    description: str
    command: Optional[str]  # Executable command like "feed herbivore_5"
    icon: str  # Emoji icon
    score: float  # For ranking (higher = more important)
    tick: int = 0  # When suggestion was generated


class GameStateAnalyzer:
    """Analyzes world state and generates contextual suggestions."""

    def __init__(self, thresholds: Optional[Thresholds] = None) -> None:
        """Initialize the analyzer."""
        self.thresholds = thresholds or Thresholds()
        self.shown_suggestions: deque[Tuple[str, int]] = deque(maxlen=20)
        self.last_milestone_tick: int = 0
        self.last_generation_celebrated: int = 0
        self.reached_population_milestones: set[int] = set()

    def get_all_suggestions(self, world: "World") -> List[Suggestion]:
        """Analyze world state and return prioritized suggestions."""
        if world is None:
            return []

        # Cache filtered collections for performance
        alive_herbivores = [h for h in world.herbivores if h.alive]
        alive_plants = [p for p in world.plants if p.alive]

        suggestions: List[Suggestion] = []

        # Gather all possible suggestions
        suggestions.extend(self.analyze_creature_health(world, alive_herbivores))
        suggestions.extend(self.analyze_breeding_opportunities(world, alive_herbivores))
        suggestions.extend(self.analyze_milestones(world, alive_herbivores))
        suggestions.extend(self.analyze_resources(world, alive_plants, alive_herbivores))
        suggestions.extend(self.analyze_learning(world, alive_herbivores))
        suggestions.extend(self.analyze_brain_types(world))

        # Remove duplicates based on category + title
        unique_suggestions = self._deduplicate(suggestions, world.tick_count)

        # Sort by score (highest first)
        unique_suggestions.sort(key=lambda s: s.score, reverse=True)

        # Return top 5
        return unique_suggestions[:5]

    def _create_suggestion(
        self,
        priority: SuggestionPriority,
        category: SuggestionCategory,
        title: str,
        description: str,
        command: Optional[str],
        icon: str,
        score: float,
        tick: int,
    ) -> Suggestion:
        """Helper method to create suggestions with consistent structure."""
        return Suggestion(
            priority=priority,
            category=category,
            title=title,
            description=description,
            command=command,
            icon=icon,
            score=score,
            tick=tick,
        )

    def _calculate_score(
        self, priority: SuggestionPriority, base_score: float, modifier: float = 0.0
    ) -> float:
        """Calculate standardized score based on priority level."""
        score = base_score + modifier

        # Clamp score to priority-appropriate range
        if priority == SuggestionPriority.CRITICAL:
            return min(
                self.thresholds.SCORE_CRITICAL_MAX,
                max(self.thresholds.SCORE_CRITICAL_MIN, score),
            )
        elif priority == SuggestionPriority.WARNING:
            return min(
                self.thresholds.SCORE_WARNING_MAX,
                max(self.thresholds.SCORE_WARNING_MIN, score),
            )
        elif priority == SuggestionPriority.INFO:
            return min(
                self.thresholds.SCORE_INFO_MAX,
                max(self.thresholds.SCORE_INFO_MIN, score),
            )
        else:  # TIP
            return min(
                self.thresholds.SCORE_TIP_MAX,
                max(self.thresholds.SCORE_TIP_MIN, score),
            )

    def analyze_creature_health(
        self, world: "World", alive_herbivores: List["Herbivore"]
    ) -> List[Suggestion]:
        """Analyze creature health and energy levels."""
        suggestions: List[Suggestion] = []

        if not alive_herbivores:
            return suggestions

        critical_energy: List["Herbivore"] = []
        low_energy: List["Herbivore"] = []
        critical_health: List["Herbivore"] = []
        old_creatures: List["Herbivore"] = []

        for herbivore in alive_herbivores:
            # Critical energy
            if herbivore.energy < self.thresholds.CRITICAL_ENERGY:
                critical_energy.append(herbivore)
            # Low energy
            elif herbivore.energy < self.thresholds.LOW_ENERGY:
                low_energy.append(herbivore)

            # Critical health
            if herbivore.health < self.thresholds.CRITICAL_HEALTH:
                critical_health.append(herbivore)

            # Old age warning
            if herbivore.age > self.thresholds.OLD_AGE:
                old_creatures.append(herbivore)

        # Critical energy warnings
        for creature in critical_energy:
            score = self._calculate_score(
                SuggestionPriority.CRITICAL,
                self.thresholds.SCORE_CRITICAL_MIN,
                self.thresholds.CRITICAL_ENERGY - creature.energy,
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.CRITICAL,
                    category=SuggestionCategory.HEALTH,
                    title="Starvation Warning",
                    description=f"{creature.name} starving ({creature.energy:.0f} energy)",
                    command=f"feed {creature.name}",
                    icon="⚠️",
                    score=score,
                    tick=world.tick_count,
                )
            )

        # Low energy batch warning
        if len(low_energy) >= 2:
            score = self._calculate_score(
                SuggestionPriority.WARNING,
                self.thresholds.SCORE_WARNING_MIN,
                len(low_energy) * 5.0,
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.WARNING,
                    category=SuggestionCategory.HEALTH,
                    title="Low Energy Alert",
                    description=f"{len(low_energy)} creatures below {self.thresholds.LOW_ENERGY:.0f} energy",
                    command=None,
                    icon="🔋",
                    score=score,
                    tick=world.tick_count,
                )
            )

        # Critical health warnings
        for creature in critical_health:
            score = self._calculate_score(
                SuggestionPriority.CRITICAL,
                self.thresholds.SCORE_CRITICAL_MIN,
                self.thresholds.CRITICAL_HEALTH - creature.health,
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.CRITICAL,
                    category=SuggestionCategory.HEALTH,
                    title="Health Critical",
                    description=f"{creature.name} injured ({creature.health:.0f} health)",
                    command=f"heal {creature.name}",
                    icon="❤️",
                    score=score,
                    tick=world.tick_count,
                )
            )

        # Old age warnings
        for creature in old_creatures:
            score = self._calculate_score(
                SuggestionPriority.WARNING,
                self.thresholds.SCORE_WARNING_MIN,
                (creature.age - self.thresholds.OLD_AGE) / 5.0,
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.WARNING,
                    category=SuggestionCategory.HEALTH,
                    title="Old Age Warning",
                    description=f"{creature.name} nearing end of life (age {creature.age:.0f})",
                    command=f"observe {creature.name}",
                    icon="⏰",
                    score=score,
                    tick=world.tick_count,
                )
            )

        return suggestions

    def analyze_breeding_opportunities(
        self, world: "World", alive_herbivores: List["Herbivore"]
    ) -> List[Suggestion]:
        """Identify good breeding candidates."""
        suggestions: List[Suggestion] = []

        if not alive_herbivores:
            return suggestions

        # Find high-fitness creatures with reproduction energy
        candidates = [
            h
            for h in alive_herbivores
            if h.fitness > self.thresholds.HIGH_FITNESS
            and h.energy >= self.thresholds.REPRODUCTION_ENERGY
        ]

        if len(candidates) >= 2:
            # Sort by fitness
            candidates.sort(key=lambda h: h.fitness, reverse=True)
            best_pair = candidates[:2]

            score = self._calculate_score(
                SuggestionPriority.WARNING,
                self.thresholds.SCORE_WARNING_MIN,
                (best_pair[0].fitness + best_pair[1].fitness) / 4.0,
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.WARNING,
                    category=SuggestionCategory.BREEDING,
                    title="Breeding Opportunity",
                    description=f"High-fitness pair ready (fitness {best_pair[0].fitness:.0f}/{best_pair[1].fitness:.0f})",
                    command=f"breed {best_pair[0].name} {best_pair[1].name}",
                    icon="🧬",
                    score=score,
                    tick=world.tick_count,
                )
            )

        # Elite creature ready to breed
        elite = [
            h
            for h in alive_herbivores
            if h.fitness > self.thresholds.ELITE_FITNESS
            and h.energy >= self.thresholds.REPRODUCTION_ENERGY
        ]
        if elite:
            best = max(elite, key=lambda h: h.fitness)
            score = self._calculate_score(
                SuggestionPriority.INFO,
                self.thresholds.SCORE_INFO_MIN,
                best.fitness / 5.0,
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.INFO,
                    category=SuggestionCategory.BREEDING,
                    title="Elite Breeding",
                    description=f"{best.name} elite creature ready (fitness {best.fitness:.0f})",
                    command=None,
                    icon="🌟",
                    score=score,
                    tick=world.tick_count,
                )
            )

        return suggestions

    def analyze_milestones(
        self, world: "World", alive_herbivores: List["Herbivore"]
    ) -> List[Suggestion]:
        """Detect achievement milestones."""
        suggestions: List[Suggestion] = []

        if not alive_herbivores:
            return suggestions

        # Check generation milestones
        max_generation = max((h.generation for h in alive_herbivores), default=0)

        if (
            max_generation in self.thresholds.GENERATION_MILESTONES
            and max_generation > self.last_generation_celebrated
        ):
            self.last_generation_celebrated = max_generation
            score = self._calculate_score(
                SuggestionPriority.INFO, self.thresholds.SCORE_INFO_MIN, 5.0
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.INFO,
                    category=SuggestionCategory.MILESTONE,
                    title="Generation Milestone",
                    description=f"Generation {max_generation} achieved!",
                    command=None,
                    icon="🎉",
                    score=score,
                    tick=world.tick_count,
                )
            )

        # Population milestones - check if we've reached any new ones
        herbivore_count = len(alive_herbivores)
        for milestone in self.thresholds.POPULATION_MILESTONES:
            if (
                herbivore_count >= milestone
                and milestone not in self.reached_population_milestones
            ):
                self.reached_population_milestones.add(milestone)
                score = self._calculate_score(
                    SuggestionPriority.INFO, self.thresholds.SCORE_INFO_MIN, 0.0
                )
                suggestions.append(
                    self._create_suggestion(
                        priority=SuggestionPriority.INFO,
                        category=SuggestionCategory.MILESTONE,
                        title="Population Milestone",
                        description=f"Population reached {milestone} creatures!",
                        command=None,
                        icon="📈",
                        score=score,
                        tick=world.tick_count,
                    )
                )

        # Fitness record
        best_fitness = max((h.fitness for h in alive_herbivores), default=0)
        if best_fitness > self.thresholds.FITNESS_RECORD:
            best_creature = max(alive_herbivores, key=lambda h: h.fitness)
            score = self._calculate_score(
                SuggestionPriority.INFO, self.thresholds.SCORE_INFO_MIN, -5.0
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.INFO,
                    category=SuggestionCategory.MILESTONE,
                    title="Fitness Record",
                    description=f"New record: {best_fitness:.0f} ({best_creature.name})",
                    command=f"observe {best_creature.name}",
                    icon="🏆",
                    score=score,
                    tick=world.tick_count,
                )
            )

        # Population crisis
        if 0 < herbivore_count <= self.thresholds.POPULATION_CRISIS:
            score = self._calculate_score(
                SuggestionPriority.CRITICAL, self.thresholds.SCORE_CRITICAL_MIN, 5.0
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.CRITICAL,
                    category=SuggestionCategory.MILESTONE,
                    title="Population Crisis",
                    description=f"Only {herbivore_count} creatures remaining!",
                    command="create herbivore",
                    icon="💀",
                    score=score,
                    tick=world.tick_count,
                )
            )

        return suggestions

    def analyze_resources(
        self,
        world: "World",
        alive_plants: List["Plant"],
        alive_herbivores: List["Herbivore"],
    ) -> List[Suggestion]:
        """Monitor resource availability."""
        suggestions: List[Suggestion] = []

        plant_count = len(alive_plants)
        herbivore_count = len(alive_herbivores)

        # Use if-elif chain to avoid redundant suggestions
        # Check most critical first
        if (
            plant_count < self.thresholds.CRITICAL_PLANTS
            and herbivore_count > self.thresholds.MIN_HERBIVORES_FOR_CRITICAL
        ):
            score = self._calculate_score(
                SuggestionPriority.CRITICAL, self.thresholds.SCORE_CRITICAL_MIN, 0.0
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.CRITICAL,
                    category=SuggestionCategory.RESOURCE,
                    title="Critical Food Shortage",
                    description=f"Starvation imminent - only {plant_count} plants",
                    command="create plant",
                    icon="⚠️",
                    score=score,
                    tick=world.tick_count,
                )
            )
        elif (
            plant_count < self.thresholds.MIN_PLANTS
            and herbivore_count > self.thresholds.MIN_HERBIVORES_FOR_SHORTAGE
        ):
            score = self._calculate_score(
                SuggestionPriority.WARNING,
                self.thresholds.SCORE_WARNING_MIN,
                self.thresholds.MIN_PLANTS - plant_count,
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.WARNING,
                    category=SuggestionCategory.RESOURCE,
                    title="Food Shortage",
                    description=f"Only {plant_count} plants for {herbivore_count} creatures",
                    command="auto_mode on",
                    icon="🌱",
                    score=score,
                    tick=world.tick_count,
                )
            )
        elif (
            plant_count < self.thresholds.LOW_PLANTS
            and herbivore_count > self.thresholds.MIN_HERBIVORES_FOR_AUTO_MODE
        ):
            score = self._calculate_score(
                SuggestionPriority.TIP, self.thresholds.SCORE_TIP_MIN, 10.0
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.TIP,
                    category=SuggestionCategory.RESOURCE,
                    title="Resource Management",
                    description="Enable auto_mode for steady plant supply",
                    command="auto_mode on",
                    icon="💡",
                    score=score,
                    tick=world.tick_count,
                )
            )

        return suggestions

    def analyze_learning(
        self, world: "World", alive_herbivores: List["Herbivore"]
    ) -> List[Suggestion]:
        """Suggest teaching and learning opportunities."""
        suggestions: List[Suggestion] = []

        if not alive_herbivores:
            return suggestions

        low_fitness_creatures = [
            h
            for h in alive_herbivores
            if h.fitness < self.thresholds.LOW_FITNESS
            and h.age < self.thresholds.YOUNG_AGE
        ]

        if low_fitness_creatures:
            # Suggest teaching for struggling young creatures
            creature = low_fitness_creatures[0]
            score = self._calculate_score(
                SuggestionPriority.INFO, self.thresholds.SCORE_INFO_MIN, 5.0
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.INFO,
                    category=SuggestionCategory.LEARNING,
                    title="Teaching Opportunity",
                    description=f"{creature.name} struggling (fitness {creature.fitness:.0f})",
                    command=f"teach {creature.name}",
                    icon="📚",
                    score=score,
                    tick=world.tick_count,
                )
            )

        # Suggest rewarding high performers
        high_performers = [
            h
            for h in alive_herbivores
            if h.fitness > self.thresholds.HIGH_PERFORMER_FITNESS
            and h.age < self.thresholds.YOUNG_AGE_HIGH_PERFORMER
        ]

        if high_performers:
            creature = max(high_performers, key=lambda h: h.fitness)
            score = self._calculate_score(
                SuggestionPriority.TIP, self.thresholds.SCORE_TIP_MIN, 5.0
            )
            suggestions.append(
                self._create_suggestion(
                    priority=SuggestionPriority.TIP,
                    category=SuggestionCategory.LEARNING,
                    title="Reinforce Success",
                    description=f"{creature.name} performing well (fitness {creature.fitness:.0f})",
                    command=f"reward {creature.name}",
                    icon="⭐",
                    score=score,
                    tick=world.tick_count,
                )
            )

        return suggestions

    def analyze_brain_types(self, world: "World") -> List[Suggestion]:
        """Point at `compare_brains` once two brain types have enough deaths to compare."""
        summary = world.stats.get_brain_type_summary(world.brain_type_counts())
        ready = sorted(
            ((k, v) for k, v in summary.items() if v["deaths"] >= 5), key=lambda kv: -kv[1]["avg_fitness"]
        )
        if len(ready) < 2:
            return []
        (a, sa), (b, sb) = ready[0], ready[1]
        return [
            self._create_suggestion(
                priority=SuggestionPriority.INFO,
                category=SuggestionCategory.LEARNING,
                title="Brain Comparison",
                description=(
                    f"{a} avg fitness {sa['avg_fitness']:.1f} vs {b} {sb['avg_fitness']:.1f} "
                    f"(n={sa['deaths']}/{sb['deaths']})"
                ),
                command="compare_brains",
                icon="🧠",
                score=self._calculate_score(SuggestionPriority.INFO, self.thresholds.SCORE_INFO_MIN, 0.0),
                tick=world.tick_count,
            )
        ]

    def _deduplicate(
        self, suggestions: List[Suggestion], current_tick: int
    ) -> List[Suggestion]:
        """Remove duplicate and recently shown suggestions."""
        unique: List[Suggestion] = []
        cooldown_ticks = self.thresholds.COOLDOWN_TICKS

        for suggestion in suggestions:
            # Create a more robust deduplication key using category + title
            dedup_key = f"{suggestion.category.value}:{suggestion.title}"

            # Check if this suggestion was shown recently
            is_duplicate = False
            for shown_key, shown_tick in self.shown_suggestions:
                if (
                    dedup_key == shown_key
                    and current_tick - shown_tick < cooldown_ticks
                ):
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique.append(suggestion)
                # Track this suggestion with the new key format
                self.shown_suggestions.append((dedup_key, current_tick))

        return unique
