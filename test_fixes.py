"""Test script to verify all bug fixes and improvements."""

from emergence.entities import Herbivore, Plant
from emergence.neural import NeuralNetwork
from emergence.reinforcement import RLAgent
from emergence.world import World
from emergence.genetics import GeneticAlgorithm
from emergence.stats import StatisticsTracker
from emergence.events import EventManager
import numpy as np

print("Testing Bug Fixes and Improvements")
print("=" * 50)

# Test Bug 1 fix: metabolism only in tick()
h = Herbivore(name='test', position=np.array([0.0, 0.0]), species='herbivore')
initial_energy = h.energy
h.apply_action(np.array([0.0, 0.0, 0.0]), dt=1.0)
# With no movement (speed=0), only move_cost * speed = 0 should be deducted
print(f'Bug 1 test - Energy after apply_action (no movement): {h.energy} (should be {initial_energy})')
assert h.energy == initial_energy, "Bug 1 FAILED: metabolism still deducted in apply_action"
print("✓ Bug 1 PASSED: Double metabolism deduction fixed")

# Test Bug 2 fix: clone creates new RNG
nn = NeuralNetwork((5, 8, 3))
clone = nn.clone()
assert nn.rng is not clone.rng, "Bug 2 FAILED: clone shares RNG with parent"
print("✓ Bug 2 PASSED: Clone creates new RNG instance")

# Test Bug 3 & 4 fix: RLAgent has rng parameter and last_q_value
agent = RLAgent(nn, rng=np.random.default_rng(42))
assert hasattr(agent, 'rng'), "Bug 4 FAILED: Agent missing rng attribute"
assert hasattr(agent, 'last_q_value'), "Bug 3 FAILED: Agent missing last_q_value attribute"
print("✓ Bug 3 PASSED: Q-value tracking added")
print("✓ Bug 4 PASSED: Seeded RNG for reproducibility")

# Test Bug 5 fix: World._update_plants accepts growth_multiplier
world = World()
world.spawn_plant()
# This should not raise an error
world._update_plants(growth_multiplier=2.0)
print("✓ Bug 5 PASSED: Event modifiers can be applied to plant growth")

# Test stats fix: deque uses history_window
tracker = StatisticsTracker(history_window=500)
assert tracker.population_history.maxlen == 500, f"Stats fix FAILED: maxlen is {tracker.population_history.maxlen}"
assert tracker.events.maxlen == 2500, f"Stats fix FAILED: events maxlen is {tracker.events.maxlen}"
print("✓ Stats fix PASSED: Deque uses history_window parameter")

# Test genetics docstring (just verify it loads)
ga = GeneticAlgorithm()
assert "Truncation" in ga.select_parents.__doc__, "Docstring fix FAILED"
print("✓ Docstring fix PASSED: select_parents describes truncation selection")

print("=" * 50)
print("All tests passed!")
