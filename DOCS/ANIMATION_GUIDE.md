# EMERGENCE Animation Guide

This guide documents the animation system used in EMERGENCE, including frame sequences, timing, engine design, and integration points.

## Animation Architecture

- **Library Module**: `emergence.animations` defines animation frames and helper methods.
- **Animation Objects**: Instances of `Animation` store frames, FPS, type (loop, once, pingpong), and timing metadata.
- **Animation Engine**: `AnimationEngine` updates active animations, supports async operation, and scales for 100+ entities.
- **Entity Animator**: `EntityAnimator` attaches animations to specific entities (`herbivore`, `carnivore`, `plant`).
- **Asset Manager**: `ArtAssetManager` orchestrates animations, registers entity animators, and provides frame retrieval.

## Frame Timing

- Default FPS: **10 frames per second** (100 ms per frame)
- Frame duration calculated as `1.0 / fps`
- Engine uses high-resolution time to update frames precisely
- Tick-based rendering supported via `get_frame_by_tick(animation_id, tick)`

## Animation Types

| Type | Behavior |
|------|----------|
| `LOOP` | Continuous looping (default) |
| `ONCE` | Plays once, then stops at last frame |
| `PINGPONG` | Plays forward then backward repeatedly |

## Creature Animations

### Herbivores

| State | Frames |
|-------|--------|
| `idle` | `['🐰', '🐰', '🐇', '🐰', '🐰', '🐇', '🐰', '🐰', '🐰', '🐰']` |
| `walk` | `['🐰', '🐇', '🐰', '🐇', '🐰', '🐇', '🐰', '🐇', '🐰', '🐇']` |
| `run` | `['💨', '🐇', '💨', '🐇', '💨', '🐇', '💨', '🐇', '💨', '🐇']` |
| `eat` | `['🐰', '😋', '🐰', '🌱', '🐰', '😋', '🐰', '🌱', '🐰', '✅']` |
| `breed` | `['❤️', '🐰', '❤️', '🐰', '✨', '👶', '✨', '🐰', '🐰', '🐰']` |
| `flee` | `['💨', '🐇', '💨', '😨', '💨', '🐇', '💨', '😨', '💨', '🐇']` |

### Carnivores

| State | Frames |
|-------|--------|
| `idle` | `['🦊', '🦊', '👁️', '🦊', '🦊', '👁️', '🦊', '🦊', '🦊', '🦊']` |
| `hunt` | `['🦊', '👁️', '🏃', '💨', '⚡', '🦊', '👁️', '🏃', '💨', '⚡']` |
| `attack` | `['🦊', '💥', '🔴', '🦊', '💥', '🔴', '🦊', '😋', '✅', '🦊']` |
| `eat` | `['🦊', '🍖', '😋', '🦊', '🍖', '😋', '🦊', '✅', '🦊', '🦊']` |
| `prowl` | `['🦊', '🐾', '🦊', '🐾', '🦊', '🐾', '🦊', '🐾', '🦊', '🐾']` |

### Plants

| State | Frames |
|-------|--------|
| `grow` | `['·', "'", '¸', '🌱', '🌿', '🌿', '🌿', '🌿', '🌿', '🌿']` |
| `mature` | `['🌿'] * 10` |
| `die` | `['🌿', '🍂', '🍂', '·', '·', ' ', ' ', ' ', ' ', ' ']` |
| `rustle` | `['🌿', '🌾', '🌿', '🌾', '🌿', '🌾', '🌿', '🌾', '🌿', '🌿']` |

## Effect Animations

| Effect | Frames | Duration |
|--------|--------|----------|
| `birth_effect` | `['·', '✧', '✨', '⭐', '✨', '✧', '·', ' ', ' ', ' ']` | 1.0 s |
| `death_effect` | `['💀', '※', '※', '·', '·', '·', ' ', ' ', ' ', ' ']` | 1.0 s |
| `attack_impact` | `['💥', '⚡', '💢', '✨', '·', ' ', ' ', ' ', ' ', ' ']` | 0.5 s |
| `evolution_flash` | `['⚡', '🧬', '✨', '🌟', '✨', '🧬', '⚡', '·', ' ', ' ']` | 1.0 s |
| `heal_effect` | `['❤️', '💚', '✨', '💖', '✨', '💚', '❤️', '·', ' ', ' ']` | 0.8 s |
| `eat_effect` | `['🍃', '😋', '+20', '✅', '·', ' ', ' ', ' ', ' ', ' ']` | 0.5 s |
| `levelup_effect` | `['✨', '⭐', '🌟', '⭐', '✨', '⭐', '🌟', '⭐', '✨', ' ']` | 1.0 s |
| `chase_trail` | `['💨', '💨', '💨', '·', '·', ' ', ' ', ' ', ' ', ' ']` | 0.5 s |
| `scent_trail` | `['·', '·', '·', '·', ' ', ' ', ' ', ' ', ' ', ' ']` | 0.5 s |

Additional sequences for environment and UI include `water_ripple`, `fire_flicker`, `spinner`, and `dots` for loading indicators.

## Async Animation Loop

The animation engine can run asynchronously:

```python
import asyncio
from emergence.animations import AnimationEngine

engine = AnimationEngine(fps=10)
asyncio.create_task(engine.run_async())
```

## Entity Animation Workflow

1. Register an animator:

```python
from emergence.art_assets import get_asset_manager

assets = get_asset_manager()
animator = assets.register_entity_animator("bloom")
```

2. Set state:

```python
animator.set_state("walk", species="herbivore")
```

3. Retrieve frame (per tick):

```python
frame = animator.get_current_frame()
```

## Animation Engine Performance

- O(1) updates per animation due to direct indexing
- One-shot animations are auto-deactivated when completed
- `AnimationEngine.update()` can be called each game tick or through async loop
- Global `frame_duration` ensures consistent pacing

### Handling 100+ Animated Sprites

- Register single `Animation` instances per entity-state combination
- Use `EntityAnimator` to manage entity-specific states
- Cache state transitions to avoid re-registering identical animations
- Utilize `get_frame_by_tick` for deterministic frame selection across distributed simulations

## Integration with Textual

```python
from textual.app import ComposeResult
from textual.widget import Widget
from emergence.art_assets import get_asset_manager

class AnimatedSprite(Widget):
    def __init__(self, entity_id: str, species: str = "herbivore") -> None:
        super().__init__()
        self.entity_id = entity_id
        self.species = species
        self.assets = get_asset_manager()
        self.animator = self.assets.register_entity_animator(entity_id)

    def set_state(self, state: str) -> None:
        self.animator.set_state(state, self.species)

    def render(self) -> str:
        return self.animator.get_current_frame()

    def on_mount(self) -> None:
        self.set_interval(0.1, self.refresh)  # 10 FPS
```

## Animation Serialization

- All animation sequences are mirrored in `emergence/assets/animations.json`
- JSON entries include `frames`, `fps`, `loop`, and `duration`
- Useful for editor tools, procedural generation, or exporting to visualization software

## Extending Animations

1. Add frames to `AnimationLibrary` in `animations.py`
2. Update `animations.json` for serialized reference
3. Document the new sequence in this guide
4. Register new states in `EntityAnimator` if necessary

Example addition:

```python
AnimationLibrary.HERBIVORE_SLEEP = ['🐰', '💤', '🐰', '💤', '🐰', '💤', '🐰', '💤', '🐰', '💤']
```

## Debugging Tips

- Use `AnimationEngine.get_frame(animation_id)` to inspect current frames
- Enable logging around `update()` to verify frame progression
- For asynchronous loops, ensure `asyncio` task is active and not cancelled
- Validate frame lengths: mismatched lengths can cause index errors
- Keep frame sequences consistent (list of strings)

## Testing Animations

See `tests/test_art_assets.py` for automated validation. Tests cover:

- Animation registration and retrieval
- Frame progression over time
- One-shot animation cleanup
- Looping and ping-pong behavior

Run tests with:

```bash
pytest tests/test_art_assets.py
```

## Related Documentation

- [SPRITE_GUIDE.md](SPRITE_GUIDE.md)
- [COLOR_SCHEME.md](COLOR_SCHEME.md)
- [UI_COMPONENTS.md](UI_COMPONENTS.md)
- [ASSETS_README.md](ASSETS_README.md)
