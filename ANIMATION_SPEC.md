# Grayscale Sprite Animation Specification

This document defines animation behavior, frame timing, state transitions, and integration guidelines for the grayscale creature sprites in EMERGENCE.

---

## 1. Animation States

Each creature supports the following core animation states:

| State       | Type         | Loop   | Description                              |
|-------------|--------------|--------|------------------------------------------|
| `idle`      | Loop         | ✓      | Default standing/resting pose            |
| `attack`    | Single-shot  | ✗      | Attack animation (transitions to idle)   |
| `damaged`   | Single-shot  | ✗      | Taking damage (recoil, transitions back) |
| `death`     | Single-shot  | ✗      | Death/collapse (ends at last frame)      |

### State Characteristics
- **Idle**: Continuous looping. Used when no other action is in progress.
- **Attack**: Triggers once, returns to idle. Duration ~0.3s.
- **Damaged**: Immediate response to damage event, returns to idle. Duration ~0.2s.
- **Death**: Final state, no loop, no return to idle.

---

## 2. Frame Timing & FPS

### Default Timing
```python
DEFAULT_TIMINGS = {
    'idle': 1.0,      # 1 second per frame
    'attack': 0.3,    # 0.3 seconds total
    'damaged': 0.2,   # 0.2 seconds total
    'death': 0.5,     # 0.5 seconds total
}
```

### Per-Creature Variations
Some creatures have custom FPS settings to match their perceived speed:

- **Fast Creatures** (Giant Rat, Giant Spider): 12 FPS
- **Standard Creatures**: 10 FPS
- **Slow Creatures** (Golem, Zombie): 8 FPS
- **Boss Creatures** (Dragon, Wyvern): 15 FPS

---

## 3. State Machine Architecture

The `CreatureAnimationStateMachine` manages automatic transitions:

```
       ┌──────────────┐
       │     IDLE     │ ◄───────┐
       └──────────────┘         │
              │                 │
              │ (on attack)     │ (on complete)
              ▼                 │
       ┌──────────────┐         │
       │   ATTACK     │─────────┘
       └──────────────┘
              │
              │ (on damage)
              ▼
       ┌──────────────┐         │
       │   DAMAGED    │─────────┘
       └──────────────┘
              │
              │ (on death event)
              ▼
       ┌──────────────┐
       │    DEATH     │ (terminal)
       └──────────────┘
```

### Transition Rules
1. **IDLE → ATTACK**: Triggered by `state_machine.attack()`
2. **IDLE → DAMAGED**: Triggered by `state_machine.take_damage()`
3. **IDLE → DEATH**: Triggered by `state_machine.die()`
4. **ATTACK → IDLE**: Automatic upon completion (non-looping)
5. **DAMAGED → IDLE**: Automatic upon completion (non-looping)
6. **DEATH → (none)**: Terminal state; no transitions

---

## 4. Usage Examples

### Basic Animation Setup
```python
from emergence.sprite_renderer import GrayscaleSpriteRenderer
from emergence.sprite_animator import CreatureAnimationStateMachine

# Initialize renderer and state machine
renderer = GrayscaleSpriteRenderer()
state_machine = CreatureAnimationStateMachine(renderer, 'dragon')

# Main game loop
while running:
    state_machine.update()  # Check for automatic transitions
    sprite = state_machine.get_current_sprite()
    
    # Render sprite
    for line in sprite:
        print(line)
    
    time.sleep(1.0 / 60)  # 60 FPS game loop
```

### Manual State Transitions
```python
# Trigger attack animation
state_machine.attack()

# Trigger damage response
state_machine.take_damage()

# Trigger death
state_machine.die()
```

### Custom Animation Sequences
```python
from emergence.sprite_animator import create_animation_timeline

# Create custom combo animation
timeline = [
    ('idle', 0.2),
    ('attack', 0.3),
    ('attack', 0.3),  # Double attack
    ('idle', 0.5),
]

animation = create_animation_timeline(renderer, 'werewolf', timeline)
```

---

## 5. Animation Frame Data

### Simple Animation (One Sprite Per State)
```python
animator.create_simple_animation(
    name='dragon_idle',
    sprite_renderer=renderer,
    creature_type='dragon',
    states=['idle'],          # Single state
    durations=[1.0],          # Duration per state
    loop=True
)
```

### Complex Animation (Multiple Frames Per State)
```python
animator.create_simple_animation(
    name='werewolf_attack_combo',
    sprite_renderer=renderer,
    creature_type='werewolf',
    states=['idle', 'attack', 'attack', 'idle'],
    durations=[0.2, 0.15, 0.15, 0.3],
    loop=False
)
```

---

## 6. State Callbacks

Register callbacks to trigger game events on state changes:

```python
def on_attack_start():
    print("Dragon attacks!")
    play_sound('dragon_roar.wav')

def on_death():
    print("Dragon has been defeated!")
    drop_loot()
    award_experience()

state_machine.register_state_callback('attack', on_attack_start)
state_machine.register_state_callback('death', on_death)
```

---

## 7. Directional Animation

Sprites face right by default. Use `facing` parameter for left-facing:

```python
# Right-facing (default)
sprite = renderer.render_sprite('dragon', 'idle', facing='right')

# Left-facing (flipped)
sprite = renderer.render_sprite('dragon', 'idle', facing='left')
```

The `sprite_flipper` module handles horizontal mirroring and character direction mapping.

---

## 8. Animation Effects

### Tinting
Apply dynamic shading for environmental effects:

```python
# Darken sprite (in shadow)
sprite = renderer.render_sprite('werewolf', 'idle', tint='darker')

# Lighten sprite (in bright light)
sprite = renderer.render_sprite('vampire', 'attack', tint='lighter')
```

### Tint Mapping
```
' ' → '░' → '▒' → '▓' → '█'  (darker)
'█' → '▓' → '▒' → '░' → ' '  (lighter)
```

---

## 9. Performance Considerations

### Optimization Strategies
- **Pre-calculate**: Render sprites once per state change, not per frame.
- **Batching**: Group sprites by state to reduce redundant render calls.
- **Culling**: Skip rendering off-screen sprites.

### Benchmarks
- **Sprite Render Time**: < 1ms per sprite
- **State Machine Update**: < 0.1ms per entity
- **Memory**: ~2KB per creature (all states loaded)

### Recommended Limits
- On-screen creatures: 50+
- Active animations: 100+
- State machine updates: 200+ per frame

---

## 10. Integration Points

### With World Simulation
```python
class Creature:
    def __init__(self, creature_type):
        self.sprite_renderer = GrayscaleSpriteRenderer()
        self.animator = CreatureAnimationStateMachine(
            self.sprite_renderer, creature_type
        )
    
    def update(self, delta_time):
        self.animator.update()
    
    def render(self):
        sprite = self.animator.get_current_sprite()
        # ... render sprite at creature position
```

### With Combat System
```python
def deal_damage(attacker, target):
    attacker.animator.attack()
    target.animator.take_damage()
    
    if target.health <= 0:
        target.animator.die()
```

---

## 11. Future Extensions

Planned animation features:

### Additional States
- `walk`: Movement animation
- `run`: Fast movement
- `cast`: Spellcasting
- `block`: Defensive stance
- `stun`: Status effect animation

### Advanced Features
- **Interpolation**: Smooth transitions between states
- **Layering**: Overlay status effects (burning, frozen)
- **Particles**: Dynamic effects (sparks, blood, dust)
- **Combo Chains**: Multi-state attack sequences

---

## 12. Testing & Validation

### Animation Preview Tool
```python
from emergence.sprite_renderer import render_animation_preview

# Preview all states cycling
render_animation_preview('dragon', delay=0.5)
```

### State Transition Testing
```python
def test_animation_lifecycle():
    state_machine = CreatureAnimationStateMachine(renderer, 'zombie')
    
    # Test idle → attack → idle
    assert state_machine.current_state == 'idle'
    state_machine.attack()
    assert state_machine.current_state == 'attack'
    
    # Wait for completion
    time.sleep(0.4)
    state_machine.update()
    assert state_machine.current_state == 'idle'
    
    # Test death (terminal state)
    state_machine.die()
    assert state_machine.current_state == 'death'
    state_machine.attack()  # Should have no effect
    assert state_machine.current_state == 'death'
```

---

## 13. Best Practices

1. **Always Update State Machine**: Call `state_machine.update()` each frame to handle auto-transitions.
2. **Validate State Completeness**: Ensure all 4 states exist before registering a creature.
3. **Consistent Anchor Points**: Keep anchor positions stable across states for smooth rendering.
4. **Test Both Directions**: Validate left-facing sprites render correctly after flipping.
5. **Profile Performance**: Use timers to measure animation overhead in production builds.

---

## 14. Troubleshooting

### Animation Not Transitioning
- Check if state is looping when it should be single-shot
- Ensure `update()` is called each frame
- Verify animation completion logic

### Sprite Flickering
- May indicate rendering called more frequently than FPS target
- Check for duplicate render calls

### Incorrect Facing Direction
- Verify `facing` parameter
- Check `sprite_flipper` mapping for directional characters

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: EMERGENCE Development Team
