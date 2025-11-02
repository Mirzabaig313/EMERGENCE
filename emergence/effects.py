"""
Visual effects for EMERGENCE terminal art assets.

Provides particle effects, explosions, trails, and other visual effects
for births, deaths, attacks, evolutions, and other game events.
"""

import time
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class EffectType(Enum):
    """Types of visual effects."""
    BIRTH = "birth"
    DEATH = "death"
    ATTACK = "attack"
    EVOLUTION = "evolution"
    HEAL = "heal"
    EAT = "eat"
    LEVELUP = "levelup"
    CHASE = "chase"
    SCENT = "scent"
    EXPLOSION = "explosion"
    SPARKLE = "sparkle"
    SMOKE = "smoke"


@dataclass
class Effect:
    """Represents a single visual effect."""
    effect_type: EffectType
    position: Tuple[float, float]
    frames: List[str]
    current_frame: int = 0
    duration: float = 1.0  # Duration in seconds
    start_time: float = field(default_factory=time.time)
    active: bool = True
    
    def update(self, current_time: float) -> bool:
        """Update effect. Returns True if still active."""
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            self.active = False
            return False
        
        # Calculate current frame based on elapsed time
        progress = elapsed / self.duration
        frame_index = int(progress * len(self.frames))
        self.current_frame = min(frame_index, len(self.frames) - 1)
        return True
    
    def get_current_sprite(self) -> str:
        """Get current effect sprite."""
        if self.active and self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return ' '
    
    def is_finished(self) -> bool:
        """Check if effect has finished."""
        return not self.active or self.current_frame >= len(self.frames) - 1


class EffectLibrary:
    """Library of all visual effect sequences."""
    
    # Birth effects
    BIRTH = ['·', '✧', '✨', '⭐', '✨', '✧', '·', ' ']
    BIRTH_SPARKLE = ['✨', '🌟', '✨', '⭐', '✨', '·', ' ', ' ']
    BIRTH_HEARTS = ['💕', '💖', '💕', '💗', '💕', '·', ' ', ' ']
    
    # Death effects
    DEATH = ['💀', '※', '※', '·', '·', '·', ' ', ' ']
    DEATH_FADE = ['😵', '💀', '·', '·', ' ', ' ', ' ', ' ']
    DEATH_SMOKE = ['💨', '💨', '·', '·', ' ', ' ', ' ', ' ']
    
    # Attack effects
    ATTACK_IMPACT = ['💥', '⚡', '💢', '✨', '·', ' ', ' ', ' ']
    ATTACK_SLASH = ['⚔️', '✨', '💥', '·', ' ', ' ', ' ', ' ']
    ATTACK_BITE = ['🦷', '💥', '🔴', '·', ' ', ' ', ' ', ' ']
    
    # Evolution effects
    EVOLUTION = ['⚡', '🧬', '✨', '🌟', '✨', '🧬', '⚡', '·']
    EVOLUTION_DNA = ['🧬', '✨', '🧬', '💫', '🧬', '✨', '🧬', ' ']
    MUTATION = ['💫', '✨', '⚡', '🌟', '⚡', '✨', '💫', ' ']
    
    # Heal effects
    HEAL = ['❤️', '💚', '✨', '💖', '✨', '💚', '❤️', '·']
    HEAL_SPARKLE = ['✨', '💚', '✨', '💚', '✨', '💚', '✨', ' ']
    REGENERATE = ['💚', '💛', '💚', '💛', '💚', '💛', '💚', ' ']
    
    # Eating effects
    EAT = ['🍃', '😋', '+20', '✅', '·', ' ', ' ', ' ']
    EAT_PLANT = ['🌱', '😋', '✅', '·', ' ', ' ', ' ', ' ']
    EAT_MEAT = ['🍖', '😋', '✅', '·', ' ', ' ', ' ', ' ']
    
    # Level up effects
    LEVELUP = ['✨', '⭐', '🌟', '⭐', '✨', '⭐', '🌟', ' ']
    LEVELUP_BURST = ['🌟', '✨', '⭐', '💫', '⭐', '✨', '🌟', ' ']
    STAR_BURST = ['⭐', '✨', '⭐', '✨', '⭐', '✨', '⭐', ' ']
    
    # Trail effects
    CHASE_TRAIL = ['💨', '💨', '💨', '·', '·', ' ', ' ', ' ']
    SCENT_TRAIL = ['·', '·', '·', '·', ' ', ' ', ' ', ' ']
    FOOTPRINTS = ['🐾', '🐾', '·', '·', ' ', ' ', ' ', ' ']
    
    # Explosions
    EXPLOSION = ['💥', '💥', '💥', '💨', '💨', '·', ' ', ' ']
    BIG_EXPLOSION = ['💥', '🔥', '💥', '🔥', '💨', '💨', '·', ' ']
    
    # Sparkles
    SPARKLE = ['✨', '✨', '✨', '·', ' ', ' ', ' ', ' ']
    MAGIC_SPARKLE = ['✨', '💫', '✨', '💫', '✨', '·', ' ', ' ']
    TWINKLE = ['✧', '✦', '✧', '✦', '✧', '·', ' ', ' ']
    
    # Smoke
    SMOKE = ['💨', '💨', '💨', '·', '·', ' ', ' ', ' ']
    PUFF = ['💨', '·', ' ', ' ', ' ', ' ', ' ', ' ']
    
    # Status effects
    CONFUSED = ['💫', '😵', '💫', '😵', '💫', '·', ' ', ' ']
    POISONED = ['☠️', '💀', '☠️', '💀', '☠️', '·', ' ', ' ']
    STUNNED = ['⭐', '💫', '⭐', '💫', '⭐', '·', ' ', ' ']
    
    # Environmental effects
    RAIN = ['💧', '💧', '💧', '💧', '💧', '💧', '💧', '💧']
    SNOW = ['❄️', '❄️', '❄️', '❄️', '❄️', '❄️', '❄️', '❄️']
    WIND = ['💨', '💨', '💨', '💨', '💨', '💨', '💨', '💨']
    
    @classmethod
    def get_effect_frames(cls, effect_type: EffectType) -> List[str]:
        """Get effect frames by type."""
        effect_map = {
            EffectType.BIRTH: cls.BIRTH,
            EffectType.DEATH: cls.DEATH,
            EffectType.ATTACK: cls.ATTACK_IMPACT,
            EffectType.EVOLUTION: cls.EVOLUTION,
            EffectType.HEAL: cls.HEAL,
            EffectType.EAT: cls.EAT,
            EffectType.LEVELUP: cls.LEVELUP,
            EffectType.CHASE: cls.CHASE_TRAIL,
            EffectType.SCENT: cls.SCENT_TRAIL,
            EffectType.EXPLOSION: cls.EXPLOSION,
            EffectType.SPARKLE: cls.SPARKLE,
            EffectType.SMOKE: cls.SMOKE
        }
        return effect_map.get(effect_type, cls.SPARKLE)
    
    @classmethod
    def create_effect(cls, effect_type: EffectType, position: Tuple[float, float],
                     duration: float = 1.0) -> Effect:
        """Create a new effect instance."""
        frames = cls.get_effect_frames(effect_type)
        return Effect(
            effect_type=effect_type,
            position=position,
            frames=frames,
            duration=duration
        )


class EffectManager:
    """Manages all active visual effects."""
    
    def __init__(self):
        self.effects: List[Effect] = []
        self.max_effects = 100  # Limit for performance
        
    def add_effect(self, effect: Effect) -> None:
        """Add a new effect."""
        if len(self.effects) < self.max_effects:
            self.effects.append(effect)
    
    def create_effect(self, effect_type: EffectType, position: Tuple[float, float],
                     duration: float = 1.0) -> Effect:
        """Create and add a new effect."""
        effect = EffectLibrary.create_effect(effect_type, position, duration)
        self.add_effect(effect)
        return effect
    
    def update(self, current_time: Optional[float] = None) -> None:
        """Update all effects and remove finished ones."""
        if current_time is None:
            current_time = time.time()
        
        # Update and filter effects
        self.effects = [
            effect for effect in self.effects
            if effect.update(current_time)
        ]
    
    def get_effects_at(self, position: Tuple[float, float], radius: float = 5.0) -> List[Effect]:
        """Get all effects within radius of a position."""
        px, py = position
        effects = []
        for effect in self.effects:
            ex, ey = effect.position
            distance = ((px - ex) ** 2 + (py - ey) ** 2) ** 0.5
            if distance <= radius:
                effects.append(effect)
        return effects
    
    def clear_effects(self) -> None:
        """Clear all effects."""
        self.effects.clear()
    
    def clear_finished_effects(self) -> None:
        """Remove only finished effects."""
        self.effects = [effect for effect in self.effects if not effect.is_finished()]
    
    def get_all_active_effects(self) -> List[Effect]:
        """Get all active effects."""
        return [effect for effect in self.effects if effect.active]
    
    def count_effects(self) -> int:
        """Get count of active effects."""
        return len(self.effects)


class ParticleEffect:
    """More complex particle-based effect."""
    
    def __init__(self, position: Tuple[float, float], particle_count: int = 5,
                 duration: float = 1.0, spread: float = 10.0):
        self.position = position
        self.particles: List[Tuple[float, float, str]] = []
        self.duration = duration
        self.start_time = time.time()
        self.active = True
        
        # Create particles with random spread
        import random
        for _ in range(particle_count):
            px = position[0] + random.uniform(-spread, spread)
            py = position[1] + random.uniform(-spread, spread)
            sprite = random.choice(['·', '✨', '✧', '⭐', '💫'])
            self.particles.append((px, py, sprite))
    
    def update(self, current_time: float) -> bool:
        """Update particle effect."""
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            self.active = False
            return False
        return True
    
    def get_particles(self) -> List[Tuple[float, float, str]]:
        """Get all particle positions and sprites."""
        return self.particles if self.active else []


def create_birth_effect(position: Tuple[float, float]) -> Effect:
    """Create a birth effect at position."""
    return EffectLibrary.create_effect(EffectType.BIRTH, position, duration=0.8)


def create_death_effect(position: Tuple[float, float]) -> Effect:
    """Create a death effect at position."""
    return EffectLibrary.create_effect(EffectType.DEATH, position, duration=1.0)


def create_attack_effect(position: Tuple[float, float]) -> Effect:
    """Create an attack effect at position."""
    return EffectLibrary.create_effect(EffectType.ATTACK, position, duration=0.5)


def create_evolution_effect(position: Tuple[float, float]) -> Effect:
    """Create an evolution effect at position."""
    return EffectLibrary.create_effect(EffectType.EVOLUTION, position, duration=1.2)


def create_heal_effect(position: Tuple[float, float]) -> Effect:
    """Create a heal effect at position."""
    return EffectLibrary.create_effect(EffectType.HEAL, position, duration=0.8)


def create_levelup_effect(position: Tuple[float, float]) -> Effect:
    """Create a level up effect at position."""
    return EffectLibrary.create_effect(EffectType.LEVELUP, position, duration=1.0)


def create_trail_effect(start_pos: Tuple[float, float], end_pos: Tuple[float, float],
                       steps: int = 5) -> List[Effect]:
    """Create a trail of effects from start to end position."""
    effects = []
    sx, sy = start_pos
    ex, ey = end_pos
    
    for i in range(steps):
        t = i / steps
        px = sx + t * (ex - sx)
        py = sy + t * (ey - sy)
        effect = EffectLibrary.create_effect(EffectType.SMOKE, (px, py), duration=0.5)
        effects.append(effect)
    
    return effects
