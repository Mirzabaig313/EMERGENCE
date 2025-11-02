"""
Sprite animation system for grayscale block art creatures.

Manages animation state machines, frame timing, and smooth transitions
between different creature states.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import time


@dataclass
class AnimationFrame:
    """Represents a single animation frame."""
    state: str
    duration: float  # Duration in seconds
    sprite_data: List[str]


@dataclass
class AnimationSequence:
    """Represents a sequence of animation frames."""
    frames: List[AnimationFrame]
    loop: bool = True
    
    def get_frame_at_time(self, elapsed_time: float) -> AnimationFrame:
        """Get the frame that should be displayed at given elapsed time."""
        if not self.frames:
            raise ValueError("Animation sequence has no frames")
        
        total_duration = sum(frame.duration for frame in self.frames)
        
        if self.loop:
            elapsed_time = elapsed_time % total_duration
        else:
            elapsed_time = min(elapsed_time, total_duration)
        
        cumulative_time = 0.0
        for frame in self.frames:
            cumulative_time += frame.duration
            if elapsed_time < cumulative_time:
                return frame
        
        return self.frames[-1]


class SpriteAnimator:
    """Manages sprite animations for creatures."""
    
    # Default animation timings (in seconds)
    DEFAULT_TIMINGS = {
        'idle': 1.0,
        'attack': 0.3,
        'damaged': 0.2,
        'death': 0.5,
    }
    
    def __init__(self):
        """Initialize the animator."""
        self.animations: Dict[str, AnimationSequence] = {}
        self.current_animation: Optional[str] = None
        self.animation_start_time: float = 0.0
        self.paused: bool = False
        self.pause_time: float = 0.0
        
    def create_animation_sequence(
        self,
        name: str,
        frames: List[AnimationFrame],
        loop: bool = True
    ) -> None:
        """
        Create and register an animation sequence.
        
        Args:
            name: Name of the animation
            frames: List of animation frames
            loop: Whether animation should loop
        """
        self.animations[name] = AnimationSequence(frames=frames, loop=loop)
    
    def create_simple_animation(
        self,
        name: str,
        sprite_renderer,
        creature_type: str,
        states: List[str],
        durations: Optional[List[float]] = None,
        loop: bool = True
    ) -> None:
        """
        Create a simple animation from a sequence of states.
        
        Args:
            name: Name of the animation
            sprite_renderer: Renderer to get sprite data from
            creature_type: Type of creature
            states: List of states to animate through
            durations: Duration for each state (uses defaults if None)
            loop: Whether animation should loop
        """
        if durations is None:
            durations = [self.DEFAULT_TIMINGS.get(state, 1.0) for state in states]
        
        if len(durations) != len(states):
            raise ValueError("Number of durations must match number of states")
        
        frames = []
        for state, duration in zip(states, durations):
            sprite_data = sprite_renderer.render_sprite(creature_type, state)
            if sprite_data:
                frames.append(AnimationFrame(
                    state=state,
                    duration=duration,
                    sprite_data=sprite_data
                ))
        
        self.create_animation_sequence(name, frames, loop)
    
    def play_animation(self, name: str) -> bool:
        """
        Start playing an animation.
        
        Args:
            name: Name of animation to play
        
        Returns:
            True if animation exists and started, False otherwise
        """
        if name not in self.animations:
            return False
        
        self.current_animation = name
        self.animation_start_time = time.time()
        self.paused = False
        return True
    
    def pause(self) -> None:
        """Pause the current animation."""
        if not self.paused:
            self.paused = True
            self.pause_time = time.time()
    
    def resume(self) -> None:
        """Resume the paused animation."""
        if self.paused:
            pause_duration = time.time() - self.pause_time
            self.animation_start_time += pause_duration
            self.paused = False
    
    def get_current_frame(self) -> Optional[AnimationFrame]:
        """
        Get the current frame of the active animation.
        
        Returns:
            Current animation frame or None if no animation is playing
        """
        if self.current_animation is None:
            return None
        
        if self.current_animation not in self.animations:
            return None
        
        animation = self.animations[self.current_animation]
        
        if self.paused:
            elapsed_time = self.pause_time - self.animation_start_time
        else:
            elapsed_time = time.time() - self.animation_start_time
        
        return animation.get_frame_at_time(elapsed_time)
    
    def is_animation_complete(self) -> bool:
        """
        Check if the current non-looping animation has completed.
        
        Returns:
            True if animation is complete (only for non-looping animations)
        """
        if self.current_animation is None:
            return True
        
        animation = self.animations.get(self.current_animation)
        if animation is None or animation.loop:
            return False
        
        elapsed_time = time.time() - self.animation_start_time
        total_duration = sum(frame.duration for frame in animation.frames)
        
        return elapsed_time >= total_duration


class CreatureAnimationStateMachine:
    """
    State machine for managing creature animation transitions.
    
    Handles automatic transitions between animation states based on
    creature behavior and game events.
    """
    
    def __init__(self, sprite_renderer, creature_type: str):
        """
        Initialize the state machine.
        
        Args:
            sprite_renderer: Renderer for getting sprite data
            creature_type: Type of creature this manages
        """
        self.sprite_renderer = sprite_renderer
        self.creature_type = creature_type
        self.animator = SpriteAnimator()
        self.current_state = 'idle'
        self.state_callbacks: Dict[str, List[Callable]] = {}
        
        # Create default animations
        self._create_default_animations()
    
    def _create_default_animations(self) -> None:
        """Create default animation sequences for all states."""
        # Idle animation (loop)
        self.animator.create_simple_animation(
            'idle',
            self.sprite_renderer,
            self.creature_type,
            ['idle'],
            [1.0],
            loop=True
        )
        
        # Attack animation (single shot)
        self.animator.create_simple_animation(
            'attack',
            self.sprite_renderer,
            self.creature_type,
            ['attack', 'idle'],
            [0.3, 0.1],
            loop=False
        )
        
        # Damaged animation (single shot)
        self.animator.create_simple_animation(
            'damaged',
            self.sprite_renderer,
            self.creature_type,
            ['damaged', 'idle'],
            [0.2, 0.1],
            loop=False
        )
        
        # Death animation (single shot, no loop)
        self.animator.create_simple_animation(
            'death',
            self.sprite_renderer,
            self.creature_type,
            ['death'],
            [1.0],
            loop=False
        )
    
    def register_state_callback(self, state: str, callback: Callable) -> None:
        """
        Register a callback to be called when entering a state.
        
        Args:
            state: State name
            callback: Function to call when state is entered
        """
        if state not in self.state_callbacks:
            self.state_callbacks[state] = []
        self.state_callbacks[state].append(callback)
    
    def transition_to(self, new_state: str) -> bool:
        """
        Transition to a new animation state.
        
        Args:
            new_state: Name of state to transition to
        
        Returns:
            True if transition was successful
        """
        if new_state == self.current_state:
            return False
        
        # Don't allow transitions out of death
        if self.current_state == 'death':
            return False
        
        # Start the new animation
        if self.animator.play_animation(new_state):
            self.current_state = new_state
            
            # Call state callbacks
            if new_state in self.state_callbacks:
                for callback in self.state_callbacks[new_state]:
                    callback()
            
            return True
        
        return False
    
    def update(self) -> None:
        """
        Update the state machine.
        
        Should be called each frame to handle automatic transitions.
        """
        # Auto-transition back to idle after non-looping animations complete
        if self.current_state in ['attack', 'damaged']:
            if self.animator.is_animation_complete():
                self.transition_to('idle')
    
    def get_current_sprite(self) -> Optional[List[str]]:
        """
        Get the sprite data for the current frame.
        
        Returns:
            Sprite lines for current frame
        """
        frame = self.animator.get_current_frame()
        if frame:
            return frame.sprite_data
        return None
    
    def attack(self) -> None:
        """Trigger attack animation."""
        self.transition_to('attack')
    
    def take_damage(self) -> None:
        """Trigger damaged animation."""
        self.transition_to('damaged')
    
    def die(self) -> None:
        """Trigger death animation."""
        self.transition_to('death')
    
    def idle(self) -> None:
        """Return to idle animation."""
        self.transition_to('idle')


def create_animation_timeline(
    sprite_renderer,
    creature_type: str,
    timeline: List[tuple]
) -> AnimationSequence:
    """
    Create a complex animation from a timeline specification.
    
    Args:
        sprite_renderer: Renderer for getting sprite data
        creature_type: Type of creature
        timeline: List of (state, duration) tuples
    
    Returns:
        AnimationSequence ready to play
    
    Example:
        timeline = [
            ('idle', 0.5),
            ('attack', 0.3),
            ('attack', 0.3),  # Double attack
            ('idle', 0.5),
        ]
    """
    frames = []
    for state, duration in timeline:
        sprite_data = sprite_renderer.render_sprite(creature_type, state)
        if sprite_data:
            frames.append(AnimationFrame(
                state=state,
                duration=duration,
                sprite_data=sprite_data
            ))
    
    return AnimationSequence(frames=frames, loop=False)


def interpolate_frame_count(duration: float, fps: int = 30) -> int:
    """
    Calculate number of frames for a given duration at target FPS.
    
    Args:
        duration: Duration in seconds
        fps: Target frames per second
    
    Returns:
        Number of frames
    """
    return max(1, int(duration * fps))
