import numpy as np

from emergence.neural import NeuralNetwork


class RLAgent:
    """Reinforcement Learning agent using temporal difference learning.

    `brain` is any object following the brain contract in emergence.brains.
    """

    def __init__(
        self,
        brain: NeuralNetwork,
        learning_rate: float = 0.01,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.999,
        min_epsilon: float = 0.01,
        rng: np.random.Generator | None = None,
    ):
        self.brain = brain
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.rng = rng if rng is not None else np.random.default_rng()
        self.last_state: np.ndarray | None = None
        self.last_action: np.ndarray | None = None
        self.last_q_value: float = 0.0  # Store Q-value from network output

    def choose_action(self, state: np.ndarray, explore: bool = True) -> np.ndarray:
        # Always run (and commit) the brain so recurrent state keeps evolving on explore ticks too.
        output = self.brain.forward(state)
        if explore and self.rng.random() < self.epsilon:
            # Random exploration using seeded RNG
            action = self.rng.standard_normal(3)
            self.last_q_value = 0.0  # No Q-value for random actions
        else:
            action = output
            # Use the max of network output as Q-value estimate
            self.last_q_value = float(np.max(action))
        self.last_state = state.copy()
        self.last_action = action.copy()
        return action

    def update(self, reward: float, next_state: np.ndarray | None = None) -> None:
        """TD learning update based on immediate reward."""
        if self.last_state is None or self.last_action is None:
            return

        if next_state is not None:
            next_q = np.max(self.brain.forward(next_state, commit=False))
            target = reward + self.discount_factor * next_q
        else:
            # Terminal state
            target = reward

        # Rebuild the backward cache for the last state without advancing recurrent state.
        self.brain.forward(self.last_state, commit=False)
        current_q = self.last_q_value
        td_error = target - current_q
        # backward() does W -= lr * grad, so the gradient is negated to move outputs
        # toward the taken action when the TD error is positive.
        gradient = -np.sign(self.last_action) * td_error
        self.brain.backward(gradient, self.learning_rate)

        # Decay exploration
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def reinforce(self, strength: float = 1.0) -> None:
        """Manual reinforcement from player: positive strength repeats the last action, negative avoids it."""
        if self.last_state is None or self.last_action is None:
            return
        self.brain.forward(self.last_state, commit=False)
        gradient = -np.sign(self.last_action) * strength
        self.brain.backward(gradient, self.learning_rate)

    def to_dict(self) -> dict:
        return {
            "brain": self.brain.to_dict(),
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "epsilon": self.epsilon,
        }

    @classmethod
    def from_dict(cls, data: dict, rng: np.random.Generator | None = None) -> "RLAgent":
        from emergence.brains import brain_from_dict

        return cls(
            brain=brain_from_dict(data["brain"], rng=rng),
            learning_rate=data["learning_rate"],
            discount_factor=data["discount_factor"],
            epsilon=data["epsilon"],
            rng=rng,
        )
