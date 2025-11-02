"""Gameplay system for EMERGENCE tying together world, modes, progression, and events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from emergence.events import EventManager
from emergence.game_modes import (
    CHALLENGES,
    GAME_MODES,
    ChallengeScenario,
    ChallengeType,
    GameMode,
    GameModeType,
)
from emergence.progression import ProgressionTracker, UnlockType
from emergence.stats import StatisticsTracker
from emergence.world import World


@dataclass
class GameplayState:
    """Stores current session state."""
    
    mode: GameMode
    challenge: Optional[ChallengeScenario] = None
    generation: int = 1
    elapsed_ticks: int = 0
    victory: bool = False
    defeat: bool = False
    tutorial_completed: bool = False
    speedrun_start_tick: Optional[int] = None
    speedrun_completion_tick: Optional[int] = None
    timeline_messages: List[str] = field(default_factory=list)


class GameplaySystem:
    """Main gameplay orchestrator for EMERGENCE."""
    
    def __init__(self, world: World, console: Optional[Console] = None):
        self.world = world
        self.console = console or Console()
        self.progression = ProgressionTracker()
        self.event_manager = EventManager()
        self.state = GameplayState(mode=GAME_MODES[GameModeType.SURVIVAL])
        self.active = False
        self.speedrun_best_time: Optional[int] = None
        self.challenge_progress: Dict[ChallengeType, bool] = {challenge: False for challenge in CHALLENGES}
    
    def start_mode(self, mode_type: GameModeType, challenge: Optional[ChallengeType] = None) -> str:
        """Start a game mode (and optional challenge)."""
        mode = GAME_MODES[mode_type]
        challenge_scenario = CHALLENGES.get(challenge) if challenge else None
        self.state = GameplayState(mode=mode, challenge=challenge_scenario)
        self.active = True
        
        # Reset world with mode-specific starting conditions
        self._reset_world_for_mode(mode)
        self.event_manager.clear_all_events()
        
        if mode_type == GameModeType.SANDBOX:
            # In sandbox, unlock everything
            for unlock in self.progression.unlocks.values():
                unlock.unlocked = True
            self.progression.evolution_points = 9999
            self.progression.divine_saves_remaining = 999
            self.event_manager.enable_events(False)
        else:
            self.event_manager.enable_events(True)
        
        # For speedrun, record start tick
        if mode_type == GameModeType.SPEEDRUN:
            self.state.speedrun_start_tick = self.world.tick_count
        
        message = f"🎮 Started {mode.name}"
        if challenge_scenario:
            message += f" - Challenge: {challenge_scenario.name}"
        
        self.state.timeline_messages.append(message)
        return message
    
    def _reset_world_for_mode(self, mode: GameMode):
        """Reset world with starting creatures and plants for a mode."""
        # Clear existing creatures
        self.world.herbivores.clear()
        self.world.dead_herbivores.clear()
        self.world.plants.clear()
        
        # Spawn starting plants
        for _ in range(mode.start_plants):
            self.world.spawn_plant()
        
        # Spawn starting herbivores
        for _ in range(mode.start_population):
            self.world.spawn_herbivore()
    
    def apply_challenge_modifiers(self, challenge: ChallengeScenario):
        """Apply modifiers from challenge scenario."""
        # Keep track of active challenge modifiers locally
        # (Detailed integration can be implemented within world simulation later)
        self.state.timeline_messages.append(
            f"⚙️ Challenge modifiers applied: {challenge.modifiers}"
        )
    
    def update_generation(self, generation: int) -> List[str]:
        """Update gameplay systems when a new generation is reached."""
        messages = []
        self.state.generation = generation
        
        # Progression achievements
        messages.extend(self.progression.update_generation_achievements(generation))
        
        # Random events
        messages.extend(self.event_manager.check_random_events(generation, {}))
        messages.extend(self.event_manager.update_events(generation))
        
        # Check win/lose conditions
        messages.extend(self.check_victory_conditions())
        
        # Speedrun tracking
        if self.state.mode.id == GameModeType.SPEEDRUN and not self.state.speedrun_completion_tick:
            population = len([h for h in self.world.herbivores if h.alive])
            if generation >= self.state.mode.win_generation and population >= self.state.mode.min_population:
                self.state.speedrun_completion_tick = self.world.tick_count
                elapsed = self.state.speedrun_completion_tick - (self.state.speedrun_start_tick or 0)
                messages.append(f"⏱️ Speedrun complete in {elapsed} ticks!")
                if not self.speedrun_best_time or elapsed < self.speedrun_best_time:
                    self.speedrun_best_time = elapsed
                    messages.append("🥇 New personal best!")
        
        # Store timeline messages
        self.state.timeline_messages.extend(messages)
        return messages
    
    def check_victory_conditions(self) -> List[str]:
        """Check win/loss conditions based on mode."""
        messages = []
        mode = self.state.mode
        population = len([h for h in self.world.herbivores if h.alive])
        generation = self.world.stats.total_generations
        
        if mode.id == GameModeType.SURVIVAL:
            if generation >= mode.win_generation and population >= mode.min_population:
                if not self.state.victory:
                    self.state.victory = True
                    messages.append("🎉 Survival Victory! Generation 100 reached with thriving ecosystem!")
                    self.progression.earn_ep(100, "Survival victory")
        elif mode.id == GameModeType.CHALLENGE:
            if self.state.challenge and generation >= self.state.challenge.start_generation + self.state.challenge.duration_generations:
                if not self.state.victory:
                    self.state.victory = True
                    self.progression.earn_ep(100, "Challenge victory")
                    messages.append(f"🏆 Challenge Complete: {self.state.challenge.name}")
        
        # Defeat conditions: population collapse
        if population <= 0 and not self.state.victory:
            self.state.defeat = True
            messages.append("💀 Ecosystem collapse - all creatures perished.")
        
        return messages
    
    def award_ep_for_tick(self, generation: int) -> List[str]:
        """Award EP for progression per tick."""
        messages = []
        # +1 EP per generation survived
        messages.append(self.progression.earn_ep(1, f"Generation {generation} survived"))
        return messages
    
    def award_ep_for_mutation(self) -> List[str]:
        """Award EP for mutations."""
        messages = ["Mutation occurred!"]
        messages.extend(self.progression.record_mutation())
        messages.append(self.progression.earn_ep(20, "Mutation discovered"))
        return messages
    
    def consume_divine_save(self) -> bool:
        """Use a divine save if available."""
        if self.progression.divine_saves_remaining > 0:
            self.progression.divine_saves_remaining -= 1
            return True
        return False
    
    def purchase_unlock(self, unlock_type: UnlockType) -> str:
        """Purchase an unlock with EP."""
        success, message = self.progression.unlock_content(unlock_type)
        if success:
            # Apply unlock effects
            if unlock_type == UnlockType.WEATHER_CONTROL:
                self.event_manager.enable_events(False)
            # Note: Other unlock effects would require deeper integration with world simulation
        return message
    
    def display_status_panel(self) -> Panel:
        """Create rich panel showing gameplay status."""
        table = Table.grid(expand=True)
        table.add_column(justify="left")
        table.add_column(justify="right")
        
        # Mode information
        table.add_row(f"🎮 Mode: [cyan]{self.state.mode.name}[/cyan]", f"Difficulty: [magenta]{self.state.mode.difficulty.value.title()}[/magenta]")
        if self.state.challenge:
            table.add_row(f"⚔️ Challenge: [yellow]{self.state.challenge.name}[/yellow]", f"Gen {self.state.challenge.start_generation}-{self.state.challenge.start_generation + self.state.challenge.duration_generations}")
        
        # Progression
        generation = self.world.stats.total_generations
        population = len([h for h in self.world.herbivores if h.alive])
        table.add_row(f"🧬 Generation: [bold]{generation}[/bold]", f"Population: [bold green]{population}[/bold green]")
        
        summary = self.progression.get_achievements_summary()
        table.add_row(f"⭐ Evolution Points: [bold yellow]{self.progression.evolution_points}[/bold yellow]", f"Achievements: [bold]{summary['unlocked']}[/bold]/[bold]{summary['total']}[/bold]")
        
        # Active events
        active_events = self.event_manager.get_active_events_display()
        if active_events:
            table.add_row("🔥 Active Events:", ", ".join(active_events))
        
        # Victory/defeat status
        if self.state.victory:
            table.add_row("🎉", "[bold green]Victory achieved![/bold green]")
        elif self.state.defeat:
            table.add_row("💀", "[bold red]Ecosystem collapse[/bold red]")
        
        return Panel(table, title="Gameplay Status", border_style="cyan", padding=(1, 2))
    
    def display_timeline(self) -> Panel:
        """Create timeline panel showing recent messages."""
        timeline = self.state.timeline_messages[-8:]
        timeline_text = "\n".join(timeline) if timeline else "No major events yet."
        return Panel(timeline_text, title="Ecosystem Timeline", border_style="magenta")


# Convenience helper for CLI
_default_gameplay_system: Optional[GameplaySystem] = None


def get_gameplay_system(world: World, console: Optional[Console] = None) -> GameplaySystem:
    """Get or create the gameplay system for the given world."""
    global _default_gameplay_system
    if _default_gameplay_system is None or _default_gameplay_system.world is not world:
        _default_gameplay_system = GameplaySystem(world, console)
    return _default_gameplay_system
