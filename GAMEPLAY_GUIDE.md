# EMERGENCE Gameplay System Guide

This guide explains the complete gameplay system for EMERGENCE with clear objectives, creature tiers, biomes, progression, game modes, and engaging player interactions.

## 🎯 Game Purpose & Win Conditions

**Core Concept:** You are a wildlife manager/god guiding evolution in a digital ecosystem.

### Game Modes

#### 1. SURVIVAL MODE (Primary)
- **Goal:** Keep ecosystem alive for 100 generations
- **Start:** 10 herbivores, abundant plants
- **Difficulty:** Medium
- **Win Condition:** Reach Generation 100 with population > 20

#### 2. CHALLENGE MODE
Pre-set scenarios with specific objectives:
- **"The Drought"** - 90% reduced plant growth for 50 generations
- **"Predator Invasion"** - Survive 20 carnivores spawning at Gen 30
- **"Ice Age"** - 50% slower reproduction, higher energy costs
- **"Extinction Event"** - Recover from 90% population wipe
- **Win Condition:** Complete scenario objective
- **Difficulty:** Hard

#### 3. SANDBOX MODE
- No win condition, pure experimentation
- All creatures/biomes unlocked
- Unlimited evolution points
- Control all parameters
- **Difficulty:** Creative

#### 4. SPEEDRUN MODE
- **Goal:** Reach Generation 100 as fast as possible (real-time)
- Leaderboard integration
- Optimal strategies required
- **Difficulty:** Expert

## 🦎 Creature System

### TIER 1: STARTERS (Available from start)

#### 🌱 PLANTS (Autotrophs)
```
Stats:
- Growth rate: 1 plant per 10 ticks in fertile soil
- Lifespan: 500 ticks
- Energy provided: 20 per consumption
- Spread: Seeds within 10 unit radius
```
- Not AI-controlled (grow automatically)
- Foundation of food chain
- Dense growth = hiding spots
- Player can plant manually

#### 🐰 HERBIVORES (Player's first creatures)
```
Stats:
- Speed: 3.0 units/tick
- Vision range: 30 units
- Hunger rate: -1 energy/tick
- Max energy: 100
- Reproduction cost: 50 energy
- Learning rate: 0.3 (fast)
- Health: 50
```

**Behaviors to Learn:**
- Graze efficiently (find plant clusters)
- Avoid predators (flee from red creatures)
- Form herds (stay near kin)
- Find water sources
- Hide in forests when threatened

**Commands:**
```
> create herbivore bloom
> observe bloom
> teach bloom "find food"
> reward bloom 10
```

### TIER 2: PREDATORS (Unlock at Generation 20)

#### 🦊 CARNIVORES (Small Predators)
```
Stats:
- Speed: 4.5 units/tick (faster than herbivores)
- Vision range: 50 units
- Hunger rate: -2 energy/tick (high metabolism)
- Max energy: 150
- Attack damage: 25
- Reproduction cost: 75 energy
- Learning rate: 0.2
- Health: 75
```

**Behaviors:**
- Chase prey efficiently
- Ambush tactics
- Pack coordination
- Territory establishment

**Unlocks:** Predator-prey dynamics, population oscillation

#### 🐺 APEX PREDATORS (Unlock at Generation 50)
```
Stats:
- Speed: 5.5 units/tick
- Vision range: 70 units
- Hunger rate: -3 energy/tick
- Max energy: 200
- Attack damage: 50 (can kill other predators)
- Reproduction cost: 100 energy
- Health: 150
```

**Challenge:** Balance ecosystem or apex predators collapse population

### TIER 3: SPECIALISTS (Unlock via achievements)

#### 🦅 SCAVENGERS
```
Stats:
- Speed: 6.0 units/tick (fastest)
- Vision range: 80 units
- Hunger rate: -1 energy/tick
- Scavenge efficiency: 80% of corpse energy
```
**Unlock:** 50 creature deaths witnessed

#### 🐻 OMNIVORES
```
Stats:
- Speed: 3.5 units/tick
- Can eat: Plants OR meat (flexible)
- Max energy: 120
- Attack damage: 30
```
**Unlock:** Survive food scarcity event

#### 🦎 CAMOUFLAGE CREATURES
```
Stats:
- Speed: 2.0 units/tick (slow)
- Special ability: Invisible when stationary
- Invisibility cooldown: 50 ticks
```
**Unlock:** Rare mutation (5% chance in forest biome)

### TIER 4: MYTHICAL (Extremely rare)

#### 🐉 DRAGON
- All stats +200%
- Area attack (hits multiple targets)
- Requires 5x normal food
- 0.1% mutation chance from apex predator
- **Achievement:** "Apex of Evolution"

#### 🦄 UNICORN
- Healing aura (restores 5 HP/tick to nearby allies)
- Creates social bonds
- Attracts others
- 0.1% mutation chance from herbivore
- **Achievement:** "Harmony"

## 🌍 Biome System

### World Generation
- 500x500 continuous coordinate space
- Procedurally generated biomes
- Rivers connect biomes
- Mountains create barriers

### Biomes

#### 🌾 PLAINS (40% of world)
```
- Plant density: High (1 plant per 5 sq units)
- Movement speed: 1.0x (normal)
- Hiding spots: None
- Energy cost: Normal
- Purpose: Primary herbivore habitat
```

#### 🌲 FOREST (25% of world)
```
- Plant density: Medium (1 plant per 10 sq units)
- Movement speed: 0.7x (slower)
- Hiding spots: Dense (reduces predator vision by 50%)
- Purpose: Hiding, ambush tactics, camouflage spawns
```

#### 🏜️ DESERT (15% of world)
```
- Plant density: Very low (1 plant per 50 sq units)
- Movement speed: 1.2x (fast, open)
- Energy cost: +100% (harsh conditions)
- Purpose: Challenge zone, high risk/reward
```

#### 🏔️ MOUNTAINS (10% of world)
```
- Impassable terrain (creatures cannot cross)
- Creates natural borders
- No resources
- Purpose: Natural boundaries
```

#### 💧 LAKES/RIVERS (5% of world)
```
- Water source (creatures must drink every 200 ticks)
- Movement speed: 0.5x (swimming)
- Plant density near water: Very high
- Purpose: Essential resource, congregation points
```

## 🎮 Gameplay Loop

### Phase 1: Tutorial & Setup (Gen 1-5)
```
> start survival_mode

╔════════════════════════════════════════╗
║      WELCOME TO EMERGENCE!             ║
║  You are the guide of evolution.       ║
║  Your mission: Keep life thriving.     ║
╚════════════════════════════════════════╝

🐰 10 herbivores spawned
Tutorial: Type 'help' for commands
```

**Tutorial Steps:**
1. `observe all` - Watch creature behavior
2. `teach bloom "eat plants"` - Basic teaching
3. `reward bloom` - Reinforce learning
4. `simulate 10` - Run simulation
5. `stats` - View results

### Phase 2: Early Game (Gen 6-20)
**Focus:** Population growth, basic survival

**Player Activities:**
- Breed successful herbivores
- Teach optimal grazing patterns
- Guide to water regularly
- Watch population grow 10 → 40+

**Random Events:**
```
Gen 8:  MUTATION! Herb23 gained +10% speed
Gen 12: MILESTONE: Population reached 25!
Gen 15: WEATHER: Rain! Plant growth +50%
Gen 18: WARNING: Food running low
```

### Phase 3: Mid Game (Gen 21-50)
**Major Event: PREDATOR ARRIVAL**
```
╔════════════════════════════════════════╗
║        ⚠️  PREDATOR DETECTED!  ⚠️       ║
╚════════════════════════════════════════╝

🦊 Carnivore spawned at (300, 200)
Your herbivores are in DANGER!

> teach all "flee from red creatures"
> create safe_zone forest_north
> simulate 20
```

### Phase 4: Late Game (Gen 51-100)
**Full Ecosystem Complexity:**
```
╔════════════ ECOSYSTEM STATUS ═══════════╗
║ Generation: 67                          ║
║ 🐰 Herbivores: 58  (healthy)            ║
║ 🦊 Carnivores: 14  (stable)             ║
║ 🐺 Apex Pred:  3   (dangerous)          ║
║ Food Chain: ✅ BALANCED                 ║
╚═════════════════════════════════════════╝
```

**Victory:**
```
╔════════════════════════════════════════╗
║           GENERATION 100!              ║
║         🎉 VICTORY! 🎉                 ║
║  You have guided life through          ║
║  100 generations of evolution.         ║
║  Rank: MASTER OF EVOLUTION             ║
╚════════════════════════════════════════╝
```

## 🏆 Progression System

### Evolution Points (EP)

**Earn EP from:**
```
+1 EP   = Generation survived
+5 EP   = Creature reaches 500 fitness
+10 EP  = Complete challenge event
+20 EP  = Discover rare mutation
+50 EP  = Reach mythical creature
+100 EP = Complete game mode
```

**Spend EP on:**
```
Unlocks:
- 20 EP: Unlock Carnivores
- 30 EP: Unlock Apex Predators
- 25 EP: Unlock Scavengers

Abilities:
- 10 EP: Increase mutation rate (+50%)
- 15 EP: Advanced teaching (faster learning)
- 20 EP: Divine intervention (save from death 3x)
- 25 EP: Weather control
```

### Achievements

**Survival:**
- 🥉 "First Steps" - Generation 10
- 🥈 "Seasoned" - Generation 50
- 🥇 "Master" - Generation 100
- 💎 "Immortal" - Generation 200

**Population:**
- "Thriving" - Population 50+
- "Ecosystem Builder" - 5 species coexisting
- "Harmony" - All species alive simultaneously

**Evolution:**
- "Natural Selection" - 10 successful mutations
- "Guiding Hand" - Teach 100 behaviors
- "Genetic Engineer" - Breed 1000+ fitness creature
- "Apex Creator" - Evolve Dragon or Unicorn

## 🎮 Player Commands

### Basic Commands
```
create [species] [name]       # Spawn creature
observe [name/all]            # Watch behavior
teach [name] [behavior]       # Guide learning
reward [name]                 # Positive reinforcement
feed [name]                   # Give food directly
heal [name]                   # Restore health
simulate [ticks]              # Run X ticks
stats                         # Ecosystem statistics
```

### Game Mode Commands
```
start_mode [survival/challenge/sandbox/speedrun]
select_challenge [drought/invasion/ice_age/extinction]
show_progress                 # Current objectives
check_victory                 # Victory conditions
```

### Progression Commands
```
show_achievements             # Achievement list
spend_ep [unlock_name]        # Purchase unlocks
show_unlocks                  # Available unlocks
```

## 🎲 Random Events

### Positive Events
- **Abundant Rain** - Plant growth +100% for 10 gen
- **Fertile Season** - Reproduction success +50%
- **Peace Period** - No predator spawns for 5 gen
- **Evolution Boost** - Mutation chance +200%

### Negative Events
- **Drought** - Plant growth -70% for 20 gen
- **Predator Invasion** - 5+ predators spawn
- **Disease** - Random creatures lose 50% health
- **Natural Disaster** - 20% population loss

## 📊 Scoring System

**Final Score Calculation:**
```
base_score = generations_survived × 100
population_bonus = final_population × 10
fitness_bonus = avg_fitness × 5
species_bonus = num_species × 500

Ranks:
0-10,000:      Novice
10,000-25,000: Apprentice
25,000-50,000: Expert
50,000-100,000: Master
100,000+:      Legendary
```

## 💡 Strategy Tips

1. **Early game:** Focus on teaching efficient grazing patterns
2. **Mid game:** Prepare for predators by teaching flee behaviors
3. **Late game:** Balance the ecosystem - too many predators will crash
4. **Use rewards** strategically to reinforce desired behaviors
5. **Save frequently** before risky experiments
6. **Watch for mutations** - they can create powerful lineages

## 🎯 Quick Start Guide

```bash
# Start EMERGENCE
python -m emergence

# Basic tutorial
> create herbivore bloom
> observe bloom
> teach bloom 5
> simulate 100
> view 200
> stats
> save my_world.json

# Advanced gameplay
> start_mode survival
> show_progress
> show_achievements
> graph population
> dashboard
```

---

This complete gameplay system creates a clear, engaging, goal-driven experience with meaningful progression and replayability!
