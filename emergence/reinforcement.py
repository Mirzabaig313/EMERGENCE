from typing import Tuple

import numpy as np

from emergence.neural import NeuralNetwork


class RLAgent:
    """Reinforcement Learning agent using temporal difference learning."""

    def __init__(
        self,
        brain: NeuralNetwork,
        learning_rate: float = 0.01,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.999,
        min_epsilon: float = 0.01,
    ):
        self.brain = brain
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.last_state: np.ndarray | None = None
        self.last_action: np.ndarray | None = None

    def choose_action(self, state: np.ndarray, explore: bool = True) -> np.ndarray:
        if explore and np.random.random() < self.epsilon:
            # Random exploration
            action = np.random.randn(3)
        else:
            action = self.brain.forward(state)
        self.last_state = state.copy()
        self.last_action = action.copy()
        return action

    def update(self, reward: float, next_state: np.ndarray | None = None) -> None:
        """TD learning update based on immediate reward."""
        if self.last_state is None or self.last_action is None:
            return

        if next_state is not None:
            next_q = np.max(self.brain.forward(next_state))
            target = reward + self.discount_factor * next_q
        else:
            # Terminal state
            target = reward

        self.brain.forward(self.last_state)
        current_q = self.last_action.max()
        td_error = target - current_q
        # Simple gradient: encourage actions that led to positive TD error
        gradient = np.sign(self.last_action) * td_error
        self.brain.backward(gradient, self.learning_rate)

        # Decay exploration
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def reinforce(self, strength: float = 1.0) -> None:
        """Manual reinforcement from player."""
        if self.last_state is None or self.last_action is None:
            return
        self.brain.forward(self.last_state)
        gradient = np.sign(self.last_action) * strength
        self.brain.backward(gradient, self.learning_rate)

    def to_dict(self) -> dict:
        return {
            "brain": self.brain.to_dict(),
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "epsilon": self.epsilon,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RLAgent":
        brain = NeuralNetwork.from_dict(data["brain"])
        return cls(
            brain=brain,
            learning_rate=data["learning_rate"],
            discount_factor=data["discount_factor"],
            epsilon=data["epsilon"],
        )
