# EMERGENCE - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Neural Network Engine](#neural-network-engine)
3. [Reinforcement Learning System](#reinforcement-learning-system)
4. [Genetic Algorithm](#genetic-algorithm)
5. [World Simulation](#world-simulation)
6. [Entities and Behaviour](#entities-and-behaviour)
7. [Visualisation System](#visualisation-system)
8. [Persistence](#persistence)
9. [Extending the System](#extending-the-system)
10. [Statistics & Analytics](#statistics--analytics)

## Architecture Overview

EMERGENCE is built on a triple-hybrid AI architecture combining:
- **Neural networks** for creature decision-making
- **Reinforcement learning** for within-lifetime optimisation
- **Genetic algorithms** for multi-generational evolution

### Core Modules

```
emergence/
├── __init__.py         # Package metadata
├── __main__.py         # CLI entry point
├── cli.py              # Interactive command interface
├── neural.py           # Feed-forward neural networks
├── reinforcement.py    # RL agent with TD learning
├── genetics.py         # Genetic algorithm operations
├── entities.py         # Plants, herbivores, and entity logic
├── world.py            # World simulation and state management
├── visualization.py    # Rich-based rendering
├── stats.py            # Statistics tracking and data collection
├── graphs.py           # ASCII graph rendering utilities
└── dashboard.py        # Dashboard and analytics views
```

## Neural Network Engine

### Architecture: `emergence.neural.NeuralNetwork`

The MVP uses a simple but fully functional feed-forward network:
- Input layer: 5 neurons (hunger, health, distance_to_plant, direction_to_plant, speed)
- Hidden layer: 8 neurons with tanh activation
- Output layer: 3 neurons with linear activation (dx, dy, eat_signal)

### Key Features

**Xavier Initialization**: Weights are initialized from a uniform distribution:
```python
limit = sqrt(6 / (fan_in + fan_out))
weights ~ Uniform(-limit, limit)
```

**Backpropagation**: Implemented for gradient-based reinforcement learning updates:
```python
network.backward(gradient, learning_rate)
```

**Crossover**: Combine two parent networks by mixing weights per-parameter:
```python
child = NeuralNetwork.crossover(parent_a, parent_b)
```

**Mutation**: Apply Gaussian noise to weights and biases:
```python
network.mutate(mutation_rate=0.1, mutation_scale=0.3)
```

### Usage Example

```python
from emergence.neural import NeuralNetwork
import numpy as np

# Create a network
brain = NeuralNetwork((5, 8, 3))
state = np.array([0.8, 1.0, 0.5, 0.2, 0.1])
action = brain.forward(state)  # Returns [dx, dy, eat]

# Update with gradient
gradient = np.array([0.1, -0.2, 0.5])
brain.backward(gradient, learning_rate=0.01)
```

## Reinforcement Learning System

### TD Learning: `emergence.reinforcement.RLAgent`

Each creature owns an RL agent that wraps a neural network and manages learning.

**Temporal Difference Update**:
```
TD_error = reward + gamma * Q(next_state) - Q(current_state)
gradient = sign(action) * TD_error
```

**Exploration vs Exploitation**:
- Epsilon-greedy policy: with probability ε, choose random action
- Epsilon decays over time: `ε = max(0.01, ε * 0.999)`

**Reward Structure**:
- +0.5 per nutrient eaten from plants
- +0.1 per tick survived
- Manual rewards from player commands

### Key Methods

```python
# Choose an action
action = agent.choose_action(state, explore=True)

# Update based on reward
agent.update(reward, next_state)

# Manual reinforcement
agent.reinforce(strength=5.0)
```

## Genetic Algorithm

### Evolution: `emergence.genetics.GeneticAlgorithm`

When populations decline, the genetic algorithm creates a new generation from successful creatures.

**Selection**: Tournament selection based on fitness score (accumulated rewards).

**Crossover**: 
```python
if random() < crossover_rate:
    child_brain = crossover(parent_a.brain, parent_b.brain)
```

**Mutation**:
- Neural network weights: Gaussian noise on 10% of parameters
- Physical traits (metabolism, speed, vision): inherited with small mutations

**Fitness Function**:
```
fitness = sum(rewards) + survival_time * 0.1 + plants_eaten * 2
```

### Evolutionary Pressure

Creatures that:
- Find food efficiently
- Survive longer
- Reproduce successfully

...pass on their genes. Poor performers die without offspring.

## World Simulation

### Continuous Space: `emergence.world.World`

The world is a 500×500 continuous plane (not a grid).

**Tick-based Update Loop**:
1. Update plants (growth, decay)
2. For each herbivore:
   - Perceive environment
   - Decide action via neural network
   - Apply physics (velocity, position)
   - Eat nearby plants
   - Update energy and health
   - Apply RL reward
   - Check reproduction threshold
   - Check death conditions
3. Remove dead creatures
4. Spawn new plants
5. Trigger evolution if population crashes

**Energy System**:
- Creatures burn `metabolism * dt` per tick
- Movement costs `move_cost * speed`
- Eating restores energy
- Energy <= 0 causes health loss

**Reproduction**:
- Trigger when energy >= 90
- Select fittest available partner
- Create offspring via genetic crossover + mutation
- Parents lose 40% energy

## Entities and Behaviour

### Plants (`emergence.entities.Plant`)

- **Growth**: Increase size and nutrients over time
- **Consumption**: Herbivores eat nutrients, killing plant if depleted
- **Spawning**: World automatically seeds new plants

### Herbivores (`emergence.entities.Herbivore`)

**Perception**: 5-dimensional state vector
```python
state = [
    hunger,              # 1 - (energy / max_energy)
    health_ratio,        # health / max_health
    distance_to_plant,   # normalized by vision_range
    direction_to_plant,  # angle in radians / π
    current_speed,       # magnitude of velocity
]
```

**Action Space**: 3-dimensional continuous
```python
action = [
    acceleration_x,  # change in velocity x
    acceleration_y,  # change in velocity y
    eat_signal,      # > 0.4 triggers eating
]
```

**Physical Traits** (evolvable):
- metabolism: energy burn rate
- speed_limit: maximum velocity
- vision_range: how far creature can see
- eat_radius: distance at which eating is possible

**Memory**: Creatures remember last food location and recent rewards.

## Visualisation System

### Rich-based Rendering: `emergence.visualization.Visualizer`

**Viewport Mapping**: Maps continuous world coordinates to a 50×30 character grid.

**Color Coding**:
- `P` (bold green): Mature plant
- `p` (green): Young plant
- `.` (dim green): Sprouting plant
- `H` (bold red): High-energy herbivore
- `h` (red): Low-energy herbivore

**Live View Mode**:
```python
with Live(visualizer.render(), refresh_per_second=20) as live:
    for _ in range(ticks):
        world.simulate(1)
        live.update(visualizer.render())
```

**Sidebar Statistics**:
- Population counts
- Average energy and fitness
- Top creature details

**Footer Table**: Lists top 5 herbivores by fitness.

## Persistence

### Save/Load: JSON Serialization

The entire world state is serializable:

**Saved Data**:
- World configuration
- All plants (position, nutrients, growth, age)
- All herbivores (position, energy, health, age, fitness, generation, parents)
- Neural network weights and biases
- RL agent parameters (learning rate, epsilon)
- Tick count and ID counter

**Usage**:
```python
world.save("ecosystem_snapshot.json")
restored = World.load("ecosystem_snapshot.json")
```

This allows:
- Pausing and resuming evolution
- Sharing interesting ecosystems
- Debugging specific scenarios
- Time-travel experiments

## Extending the System

### Adding Carnivores (Phase 2)

1. **Create `Carnivore` class** in `entities.py`:
   - Similar structure to `Herbivore`
   - Perceive herbivores instead of plants
   - Attack action instead of eat
   - Higher metabolism

2. **Update perception**:
   - Add inputs for nearest prey distance/direction
   - Add health of target
   - Add escape vector (for fleeing)

3. **Implement hunting**:
   - Check proximity to herbivores
   - Deal damage on attack action
   - Consume corpse for energy

4. **Add to genetic system**:
   - Separate evolution pools
   - Tune mutation rates for predators

### Advanced Visualization

**Heatmaps**:
```python
def render_heatmap(self, resource: str) -> Text:
    # Aggregate resource density across world
    # Render as color-intensity map
```

**Family Trees**:
```python
def build_tree(self, creature: Herbivore) -> Tree:
    # Recursively construct ancestry graph
    # Use Rich Tree widget
```

### Teaching System

**Behaviour Templates**:
```python
def teach_behavior(self, creature: Herbivore, behavior: str):
    if behavior == "explore":
        # Reward high speed, distance travelled
    elif behavior == "graze":
        # Reward low movement, high eating
```

### Multi-Agent Communication

**Signal Passing**:
```python
# Emit signal (stored in herbivore state)
herbivore.emit_signal("danger", strength=0.8)

# Nearby creatures perceive signals
signals = herbivore.perceive_signals(nearby_creatures)
```

## Performance Considerations

**Current Capacity**: 50-100 creatures, 100-150 plants on standard hardware.

**Optimization Strategies**:
1. **Spatial Partitioning**: Use quadtree for O(log n) nearest-neighbor queries
2. **Vectorization**: Batch neural network forward passes
3. **Lazy Evaluation**: Only update creatures in view during visualisation
4. **Cython Extensions**: Compile hot paths (physics, perception) to C
5. **GPU Acceleration**: Port neural network to PyTorch for parallel inference

## Debugging Tips

**Track a specific creature**:
```
> follow herbivore_42
> view 500
```

**Inspect weights after learning**:
```
> show_brain herbivore_42
```

**Save checkpoints during long runs**:
```
> simulate 500
> save checkpoint_1.json
> simulate 500
> save checkpoint_2.json
```

**Compare generations**:
```python
# Load two saves and compare average fitness
world_gen1 = World.load("gen_1.json")
world_gen10 = World.load("gen_10.json")
```

## FAQ

**Q: Why do all herbivores die sometimes?**  
A: Population crashes happen when plants are over-consumed. Enable `auto_mode on` to increase plant spawning, or manually `create plant` repeatedly.

**Q: Creatures aren't learning—what's wrong?**  
A: Check exploration (epsilon) isn't too high, and that rewards are scaled appropriately. Try manually rewarding good behaviour.

**Q: How do I speed up evolution?**  
A: Run `simulate 5000` headless, then `view` the result. Increase mutation rate in `genetics.py` for faster change.

**Q: Can I train a "champion" creature?**  
A: Yes! Use `reward` extensively on one herbivore, then `breed` it with itself repeatedly (or clone via save/load).

## Conclusion

EMERGENCE MVP successfully demonstrates the convergence of neural networks, reinforcement learning, and genetic algorithms in an emergent simulation. The modular architecture makes expansion straightforward, and the persistence system ensures experiments can be shared and iterated upon.

Explore, evolve, and enjoy the beauty of artificial life!
