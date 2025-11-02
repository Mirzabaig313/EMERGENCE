# EMERGENCE Sprite Guide

Complete reference for all available sprites in the EMERGENCE terminal art asset system.

## Table of Contents

- [Primary Creatures](#primary-creatures)
- [Plants & Vegetation](#plants--vegetation)
- [Terrain Features](#terrain-features)
- [State Indicators](#state-indicators)
- [Action Effects](#action-effects)
- [UI Elements](#ui-elements)
- [Block Characters](#block-characters)
- [Usage Examples](#usage-examples)

## Primary Creatures

### Herbivores

| Sprite | Code | Description | Usage |
|--------|------|-------------|-------|
| 🐰 | `HERBIVORE_RABBIT` | Standard herbivore | Default creature sprite |
| 🐇 | `HERBIVORE_RABBIT_FAST` | Fast herbivore variant | Running animation frame |
| 🦌 | `HERBIVORE_DEER` | Large herbivore | Elite/evolved herbivore |
| 🐁 | `HERBIVORE_MOUSE` | Small herbivore | Baby/juvenile creature |

### Carnivores

| Sprite | Code | Description | Usage |
|--------|------|-------------|-------|
| 🦊 | `CARNIVORE_FOX` | Standard carnivore | Default predator sprite |
| 🐺 | `CARNIVORE_WOLF` | Apex predator | Pack hunter / elite |
| 🦅 | `CARNIVORE_EAGLE` | Scavenger | Flying predator |
| 🐻 | `CARNIVORE_BEAR` | Omnivore | Large territorial predator |

### Special Creatures

| Sprite | Code | Description | Usage |
|--------|------|-------------|-------|
| 🦎 | `CREATURE_LIZARD` | Camouflage creature | Adaptive species |
| 🐉 | `CREATURE_DRAGON` | Mythical dragon | Unlockable/rare creature |
| 🦄 | `CREATURE_UNICORN` | Mythical unicorn | Unlockable/rare creature |
| 🦇 | `CREATURE_BAT` | Night creature | Nocturnal species |
| 🐛 | `CREATURE_LARVA` | Larva/baby | Pre-evolution stage |
| 🥚 | `CREATURE_EGG` | Egg | Pre-birth stage |

## Plants & Vegetation

| Sprite | Code | Description | Usage |
|--------|------|-------------|-------|
| 🌱 | `PLANT_SPROUT` | Young plant/sprout | Growth stage 1-2 |
| 🌿 | `PLANT_HERB` | Mature plant/herb | Growth stage 2-4 |
| 🌾 | `PLANT_GRASS` | Grass/grain | Growth stage 4+ |
| 🌲 | `PLANT_TREE` | Tree/forest | Forest terrain |
| 🌳 | `PLANT_TREE_DECIDUOUS` | Deciduous tree | Alternative forest |
| 🌵 | `PLANT_CACTUS` | Desert plant/cactus | Desert biome |
| 🍄 | `PLANT_MUSHROOM` | Mushroom/fungus | Special vegetation |
| 🍃 | `PLANT_LEAF` | Leaf | Eating animation |
| 🍂 | `PLANT_FALLEN_LEAF` | Fallen leaf | Death animation |

## Terrain Features

| Sprite | Code | Description | Usage |
|--------|------|-------------|-------|
| 💧 | `TERRAIN_WATER` | Water/lake | Shallow water |
| 🌊 | `TERRAIN_OCEAN` | Ocean/deep water | Deep water biome |
| 🏔️ | `TERRAIN_MOUNTAIN` | Mountain/peak | Mountain biome |
| 🏜️ | `TERRAIN_DESERT` | Desert/sand | Desert biome |
| ❄️ | `TERRAIN_ICE` | Ice/snow | Ice biome |
| 🔥 | `TERRAIN_FIRE` | Fire/danger | Danger zone |
| 💀 | `TERRAIN_DEATH` | Death/graveyard | Death marker |

## State Indicators

Status overlays that appear with creatures:

| Sprite | Code | Description | Usage |
|--------|------|-------------|-------|
| 💤 | `STATUS_SLEEPING` | Sleeping/resting | Idle state overlay |
| ❤️ | `STATUS_BREEDING` | Breeding/mating | Reproduction state |
| 💔 | `STATUS_INJURED` | Injured/hurt | Low health warning |
| ⚡ | `STATUS_ENERGIZED` | Energized/powered | High energy state |
| 😴 | `STATUS_TIRED` | Tired/low energy | Low energy warning |
| 😋 | `STATUS_EATING` | Eating/satisfied | Feeding state |
| 😨 | `STATUS_SCARED` | Scared/fleeing | Fear response |
| 😡 | `STATUS_ANGRY` | Aggressive/angry | Attack mode |
| 💭 | `STATUS_THINKING` | Thinking/learning | Neural processing |
| 💡 | `STATUS_LEARNED` | Learned something | Learning event |
| ✨ | `STATUS_LEVELUP` | Leveled up/evolved | Evolution event |
| ⭐ | `STATUS_ELITE` | High fitness/elite | Top performer |
| 💫 | `STATUS_MUTATION` | Mutation happening | Genetic change |
| 🎯 | `STATUS_SELECTED` | Target/selected | Player selection |
| 👁️ | `STATUS_OBSERVED` | Being watched | Observer mode |

## Action Effects

Visual effects for actions and events:

### Birth
```
['·', '✧', '✨', '⭐', '✨']
```

### Death
```
['💀', '※', '·', '·', ' ']
```

### Attack
```
['💥', '⚡', '💢', '✨']
```

### Evolution
```
['⚡', '🧬', '✨', '🌟', '✨']
```

### Heal
```
['❤️', '💚', '✨', '💖']
```

### Eat
```
['🍃', '😋', '+20']
```

### Chase Trail
```
['💨', '💨', '💨']
```

## UI Elements

| Sprite | Code | Description |
|--------|------|-------------|
| ▸ | `UI_ARROW_RIGHT` | Menu selection arrow |
| ✅ | `UI_CHECKMARK` | Success indicator |
| ❌ | `UI_CROSS` | Error indicator |
| ⚠️ | `UI_WARNING` | Warning indicator |
| ℹ️ | `UI_INFO` | Info indicator |
| 💬 | `EMOJI_COMMAND` | Command/chat icon |
| 🌍 | `EMOJI_WORLD` | World view icon |
| 📊 | `EMOJI_STATS` | Statistics icon |
| 📈 | `EMOJI_CHART` | Graph icon |
| 🧬 | `EMOJI_DNA` | Evolution icon |
| ⚙️ | `EMOJI_SETTINGS` | Settings icon |

## Block Characters

Used for progress bars, textures, and backgrounds:

### Density Blocks
```
█  BLOCK_SOLID (100%)
▓  BLOCK_DARK (75%)
▒  BLOCK_MEDIUM (50%)
░  BLOCK_LIGHT (25%)
   BLOCK_EMPTY (0%)
```

### Partial Blocks
```
▀  BLOCK_UPPER (upper half)
▄  BLOCK_LOWER (lower half)
▌  BLOCK_LEFT (left half)
▐  BLOCK_RIGHT (right half)
```

### Small Blocks
```
■  BLOCK_SMALL_BLACK
□  BLOCK_SMALL_WHITE
▪  BLOCK_SMALL_BLACK_SQ
▫  BLOCK_SMALL_WHITE_SQ
```

### Heatmap Colors
```
🟥  HEAT_HIGH
🟧  HEAT_MED_HIGH
🟨  HEAT_MED
🟩  HEAT_MED_LOW
⬜  HEAT_LOW
```

## Usage Examples

### Getting Sprites

```python
from emergence.sprites import SpriteLibrary

# Get creature sprites
rabbit = SpriteLibrary.get_herbivore_sprite('standard')  # 🐰
fox = SpriteLibrary.get_carnivore_sprite('standard')     # 🦊

# Get plant sprites by growth stage
seed = SpriteLibrary.get_plant_sprite(0.5)    # ·
sprout = SpriteLibrary.get_plant_sprite(1.5)  # 🌱
mature = SpriteLibrary.get_plant_sprite(4.0)  # 🌾

# Get status indicators
sleeping = SpriteLibrary.get_status_sprite('sleeping')  # 💤
eating = SpriteLibrary.get_status_sprite('eating')      # 😋
```

### Creating Progress Bars

```python
from emergence.sprites import create_health_bar, create_energy_bar

health_bar = create_health_bar(75, 100, width=10)  # ████████░░
energy_bar = create_energy_bar(60, 100, width=10)  # ▓▓▓▓▓▓▒▒▒▒
```

### Creating Heatmaps

```python
from emergence.sprites import create_heatmap_cell

# Create a single heatmap cell
cell = create_heatmap_cell(0.8, 1.0)  # 🟧 (high activity)
```

### Creating Sparklines

```python
from emergence.sprites import create_sparkline

values = [10, 20, 30, 25, 35, 40, 38, 45]
sparkline = create_sparkline(values, width=20)
# Output: ▁▂▄▃▅▆▅▇
```

## Asset Manager Integration

The recommended way to access sprites is through the `ArtAssetManager`:

```python
from emergence.art_assets import get_asset_manager

assets = get_asset_manager()

# Get sprites
sprite = assets.get_sprite('herbivore', variant='fast')
status = assets.get_status_sprite('eating')

# Create UI components
bar = assets.create_progress_bar("HP", 75, 100, width=10)
sparkline = assets.create_sparkline([10, 20, 30, 40], width=15)
```

## Rendering with Color

```python
from emergence.art_assets import get_asset_manager
from rich.console import Console

assets = get_asset_manager()
console = Console()

# Get sprite with color
sprite = assets.get_sprite('herbivore')
color = assets.get_creature_color('herbivore', age=100, health=80, energy=60)
colored_sprite = assets.render_colored_sprite(sprite, color)

# Print to console
console.print(colored_sprite)
```

## Best Practices

1. **Use the Asset Manager**: Always access sprites through `get_asset_manager()` for consistency
2. **Cache frequently used sprites**: Store commonly used sprites in variables to avoid lookups
3. **Test emoji rendering**: Verify your terminal font supports the emoji set
4. **Consider fallbacks**: For terminals without emoji support, provide ASCII fallbacks
5. **Performance**: Use static sprites when animation isn't needed

## Terminal Compatibility

- **macOS Terminal**: Full emoji support with Apple Color Emoji font
- **iTerm2**: Excellent emoji rendering
- **Windows Terminal**: Good emoji support with Segoe UI Emoji
- **Linux terminals**: Requires Noto Color Emoji or similar font
- **VSCode integrated terminal**: Good support on all platforms

## See Also

- [ANIMATION_GUIDE.md](ANIMATION_GUIDE.md) - Animation sequences and frame timing
- [COLOR_SCHEME.md](COLOR_SCHEME.md) - Color palettes and themes
- [UI_COMPONENTS.md](UI_COMPONENTS.md) - UI building blocks
- [ASSETS_README.md](ASSETS_README.md) - Asset system overview
