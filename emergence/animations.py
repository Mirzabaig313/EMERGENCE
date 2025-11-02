"""
Animation sequences for EMERGENCE terminal art assets.

Provides frame-based animations for creatures, plants, effects, and UI elements.
Supports 10 FPS animation system with looping and one-shot animations.
"""

import time
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class AnimationType(Enum):
    """Types of animations."""
    LOOP = "loop"
    ONCE = "once"
    PINGPONG = "pingpong"


@dataclass
class Animation:
    """Represents a single animation sequence."""
    name: str
    frames: List[str]
    fps: int = 10
    animation_type: AnimationType = AnimationType.LOOP
    current_frame: int = 0
    last_update: float = field(default_factory=time.time)
    direction: int = 1  # For pingpong animations
    
    def get_frame_duration(self) -> float:
        """Get duration of each frame in seconds."""
        return 1.0 / self.fps
    
    def update(self, current_time: float) -> bool:
        """Update animation frame. Returns True if frame changed."""
        if current_time - self.last_update >= self.get_frame_duration():
            if self.animation_type == AnimationType.LOOP:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            elif self.animation_type == AnimationType.ONCE:
                if self.current_frame < len(self.frames) - 1:
                    self.current_frame += 1
            elif self.animation_type == AnimationType.PINGPONG:
                self.current_frame += self.direction
                if self.current_frame >= len(self.frames) - 1:
                    self.direction = -1
                elif self.current_frame <= 0:
                    self.direction = 1
            
            self.last_update = current_time
            return True
        return False
    
    def get_current_frame(self) -> str:
        """Get the current frame sprite."""
        return self.frames[self.current_frame]
    
    def reset(self) -> None:
        """Reset animation to start."""
        self.current_frame = 0
        self.direction = 1
        self.last_update = time.time()


class AnimationLibrary:
    """Library of all predefined animations."""
    
    # Herbivore animations (10 frames each for smooth 10 FPS)
    HERBIVORE_IDLE = ['🐰', '🐰', '🐇', '🐰', '🐰', '🐇', '🐰', '🐰', '🐰', '🐰']
    HERBIVORE_WALK = ['🐰', '🐇', '🐰', '🐇', '🐰', '🐇', '🐰', '🐇', '🐰', '🐇']
    HERBIVORE_RUN = ['💨', '🐇', '💨', '🐇', '💨', '🐇', '💨', '🐇', '💨', '🐇']
    HERBIVORE_EAT = ['🐰', '😋', '🐰', '🌱', '🐰', '😋', '🐰', '🌱', '🐰', '✅']
    HERBIVORE_BREED = ['❤️', '🐰', '❤️', '🐰', '✨', '👶', '✨', '🐰', '🐰', '🐰']
    HERBIVORE_FLEE = ['💨', '🐇', '💨', '😨', '💨', '🐇', '💨', '😨', '💨', '🐇']
    
    # Carnivore animations
    CARNIVORE_IDLE = ['🦊', '🦊', '👁️', '🦊', '🦊', '👁️', '🦊', '🦊', '🦊', '🦊']
    CARNIVORE_HUNT = ['🦊', '👁️', '🏃', '💨', '⚡', '🦊', '👁️', '🏃', '💨', '⚡']
    CARNIVORE_ATTACK = ['🦊', '💥', '🔴', '🦊', '💥', '🔴', '🦊', '😋', '✅', '🦊']
    CARNIVORE_EAT = ['🦊', '🍖', '😋', '🦊', '🍖', '😋', '🦊', '✅', '🦊', '🦊']
    CARNIVORE_PROWL = ['🦊', '🐾', '🦊', '🐾', '🦊', '🐾', '🦊', '🐾', '🦊', '🐾']
    
    # Plant animations
    PLANT_GROW = ['·', '\'', '¸', '🌱', '🌿', '🌿', '🌿', '🌿', '🌿', '🌿']
    PLANT_MATURE = ['🌿', '🌿', '🌿', '🌿', '🌿', '🌿', '🌿', '🌿', '🌿', '🌿']
    PLANT_DIE = ['🌿', '🍂', '🍂', '·', '·', ' ', ' ', ' ', ' ', ' ']
    PLANT_RUSTLE = ['🌿', '🌾', '🌿', '🌾', '🌿', '🌾', '🌿', '🌾', '🌿', '🌿']
    
    # Effect animations (one-shot)
    BIRTH_EFFECT = ['·', '✧', '✨', '⭐', '✨', '✧', '·', ' ', ' ', ' ']
    DEATH_EFFECT = ['💀', '※', '※', '·', '·', '·', ' ', ' ', ' ', ' ']
    ATTACK_IMPACT = ['💥', '⚡', '💢', '✨', '·', ' ', ' ', ' ', ' ', ' ']
    EVOLUTION_FLASH = ['⚡', '🧬', '✨', '🌟', '✨', '🧬', '⚡', '·', ' ', ' ']
    HEAL_EFFECT = ['❤️', '💚', '✨', '💖', '✨', '💚', '❤️', '·', ' ', ' ']
    EAT_EFFECT = ['🍃', '😋', '+20', '✅', '·', ' ', ' ', ' ', ' ', ' ']
    LEVELUP_EFFECT = ['✨', '⭐', '🌟', '⭐', '✨', '⭐', '🌟', '⭐', '✨', ' ']
    
    # Trail effects
    CHASE_TRAIL = ['💨', '💨', '💨', '·', '·', ' ', ' ', ' ', ' ', ' ']
    SCENT_TRAIL = ['·', '·', '·', '·', ' ', ' ', ' ', ' ', ' ', ' ']
    
    # Water animation
    WATER_RIPPLE = ['💧', '≈', '≈', '💧', '≈', '≈', '💧', '≈', '≈', '💧']
    
    # Fire animation
    FIRE_FLICKER = ['🔥', '🔥', '✨', '🔥', '🔥', '✨', '🔥', '🔥', '✨', '🔥']
    
    # Loading/Spinner
    SPINNER = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    DOTS = ['.  ', '.. ', '...', '.. ', '.  ', '   ']
    
    # Breathing animation (for idle)
    BREATHING = ['○', '◯', '◯', '◯', '○', '○', '○', '○', '○', '○']
    
    @classmethod
    def create_animation(cls, name: str, animation_type: AnimationType = AnimationType.LOOP, 
                        fps: int = 10) -> Optional[Animation]:
        """Create an animation object from the library."""
        frames = getattr(cls, name.upper(), None)
        if frames:
            return Animation(name=name, frames=frames, fps=fps, animation_type=animation_type)
        return None
    
    @classmethod
    def get_herbivore_animation(cls, state: str) -> List[str]:
        """Get herbivore animation frames for a given state."""
        animations = {
            'idle': cls.HERBIVORE_IDLE,
            'walk': cls.HERBIVORE_WALK,
            'run': cls.HERBIVORE_RUN,
            'eat': cls.HERBIVORE_EAT,
            'breed': cls.HERBIVORE_BREED,
            'flee': cls.HERBIVORE_FLEE
        }
        return animations.get(state, cls.HERBIVORE_IDLE)
    
    @classmethod
    def get_carnivore_animation(cls, state: str) -> List[str]:
        """Get carnivore animation frames for a given state."""
        animations = {
            'idle': cls.CARNIVORE_IDLE,
            'hunt': cls.CARNIVORE_HUNT,
            'attack': cls.CARNIVORE_ATTACK,
            'eat': cls.CARNIVORE_EAT,
            'prowl': cls.CARNIVORE_PROWL
        }
        return animations.get(state, cls.CARNIVORE_IDLE)
    
    @classmethod
    def get_plant_animation(cls, state: str) -> List[str]:
        """Get plant animation frames for a given state."""
        animations = {
            'grow': cls.PLANT_GROW,
            'mature': cls.PLANT_MATURE,
            'die': cls.PLANT_DIE,
            'rustle': cls.PLANT_RUSTLE
        }
        return animations.get(state, cls.PLANT_MATURE)
    
    @classmethod
    def get_effect_animation(cls, effect: str) -> List[str]:
        """Get effect animation frames."""
        effects = {
            'birth': cls.BIRTH_EFFECT,
            'death': cls.DEATH_EFFECT,
            'attack': cls.ATTACK_IMPACT,
            'evolution': cls.EVOLUTION_FLASH,
            'heal': cls.HEAL_EFFECT,
            'eat': cls.EAT_EFFECT,
            'levelup': cls.LEVELUP_EFFECT,
            'chase': cls.CHASE_TRAIL,
            'scent': cls.SCENT_TRAIL
        }
        return effects.get(effect, ['·'])


class AnimationEngine:
    """Manages all active animations and updates them."""
    
    def __init__(self, fps: int = 10):
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.animations: Dict[str, Animation] = {}
        self.active_animations: List[str] = []
        self.tick_counter = 0
        
    def register_animation(self, animation_id: str, animation: Animation) -> None:
        """Register an animation with a unique ID."""
        self.animations[animation_id] = animation
        
    def activate_animation(self, animation_id: str) -> bool:
        """Activate a registered animation."""
        if animation_id in self.animations and animation_id not in self.active_animations:
            self.active_animations.append(animation_id)
            self.animations[animation_id].reset()
            return True
        return False
    
    def deactivate_animation(self, animation_id: str) -> None:
        """Deactivate an animation."""
        if animation_id in self.active_animations:
            self.active_animations.remove(animation_id)
    
    def update(self, current_time: Optional[float] = None) -> None:
        """Update all active animations."""
        if current_time is None:
            current_time = time.time()
        
        for anim_id in self.active_animations[:]:  # Copy list to allow modification
            animation = self.animations[anim_id]
            animation.update(current_time)
            
            # Remove one-shot animations that finished
            if (animation.animation_type == AnimationType.ONCE and 
                animation.current_frame >= len(animation.frames) - 1):
                self.deactivate_animation(anim_id)
    
    def get_frame(self, animation_id: str) -> Optional[str]:
        """Get current frame of an animation."""
        animation = self.animations.get(animation_id)
        if animation:
            return animation.get_current_frame()
        return None
    
    def get_frame_by_tick(self, animation_id: str, tick: int) -> Optional[str]:
        """Get animation frame based on game tick (for synchronized animations)."""
        animation = self.animations.get(animation_id)
        if animation:
            frame_index = (tick // (60 // self.fps)) % len(animation.frames)
            return animation.frames[frame_index]
        return None
    
    def clear_finished_animations(self) -> None:
        """Remove finished one-shot animations."""
        for anim_id in list(self.active_animations):
            animation = self.animations[anim_id]
            if (animation.animation_type == AnimationType.ONCE and 
                animation.current_frame >= len(animation.frames) - 1):
                self.deactivate_animation(anim_id)
    
    async def run_async(self) -> None:
        """Run animation engine in async loop."""
        while True:
            self.update()
            await asyncio.sleep(self.frame_duration)
    
    def tick(self) -> None:
        """Update animation tick counter."""
        self.tick_counter += 1
        self.update()


class EntityAnimator:
    """Manages animations for individual entities."""
    
    def __init__(self, entity_id: str, animation_engine: AnimationEngine):
        self.entity_id = entity_id
        self.engine = animation_engine
        self.current_state = 'idle'
        self.state_changed = False
        
    def set_state(self, state: str, species: str = 'herbivore') -> None:
        """Set entity animation state."""
        if state != self.current_state:
            self.current_state = state
            self.state_changed = True
            
            # Get appropriate animation frames
            if species == 'herbivore':
                frames = AnimationLibrary.get_herbivore_animation(state)
            elif species == 'carnivore':
                frames = AnimationLibrary.get_carnivore_animation(state)
            elif species == 'plant':
                frames = AnimationLibrary.get_plant_animation(state)
            else:
                frames = AnimationLibrary.HERBIVORE_IDLE
            
            # Create and register animation
            animation_id = f"{self.entity_id}_{state}"
            animation = Animation(
                name=animation_id,
                frames=frames,
                fps=10,
                animation_type=AnimationType.LOOP
            )
            
            # Deactivate old animations
            for anim_id in list(self.engine.active_animations):
                if anim_id.startswith(self.entity_id):
                    self.engine.deactivate_animation(anim_id)
            
            # Activate new animation
            self.engine.register_animation(animation_id, animation)
            self.engine.activate_animation(animation_id)
    
    def get_current_frame(self) -> str:
        """Get current animation frame for this entity."""
        animation_id = f"{self.entity_id}_{self.current_state}"
        frame = self.engine.get_frame(animation_id)
        return frame if frame else '🐰'
    
    def play_effect(self, effect: str, duration: Optional[int] = None) -> str:
        """Play a one-shot effect animation."""
        frames = AnimationLibrary.get_effect_animation(effect)
        effect_id = f"{self.entity_id}_effect_{effect}_{time.time()}"
        
        animation = Animation(
            name=effect_id,
            frames=frames,
            fps=10,
            animation_type=AnimationType.ONCE
        )
        
        self.engine.register_animation(effect_id, animation)
        self.engine.activate_animation(effect_id)
        
        return effect_id


def create_custom_animation(frames: List[str], fps: int = 10, 
                           animation_type: AnimationType = AnimationType.LOOP) -> Animation:
    """Create a custom animation from frame list."""
    return Animation(
        name="custom",
        frames=frames,
        fps=fps,
        animation_type=animation_type
    )


def interpolate_frames(start_frame: str, end_frame: str, steps: int = 5) -> List[str]:
    """Create interpolated frames between two frames (for smooth transitions)."""
    # Simple implementation that alternates between frames
    frames = []
    for i in range(steps):
        if i % 2 == 0:
            frames.append(start_frame)
        else:
            frames.append(end_frame)
    return frames
