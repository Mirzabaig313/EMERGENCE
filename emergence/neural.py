from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class LayerWeights:
    weights: np.ndarray
    biases: np.ndarray


class NeuralNetwork:
    """Simple feed-forward neural network with tanh hidden layers and a linear output.

    Implements the duck-typed brain contract documented in ``emergence.brains``.
    """

    brain_type = "random"

    def __init__(self, layer_sizes: Tuple[int, ...], rng: np.random.Generator | None = None):
        if len(layer_sizes) < 2:
            raise ValueError("layer_sizes must include at least input and output size")
        self.layer_sizes = tuple(layer_sizes)
        self.rng = rng if rng is not None else np.random.default_rng()
        self.layers: List[LayerWeights] = []
        for input_size, output_size in zip(self.layer_sizes[:-1], self.layer_sizes[1:]):
            # Xavier initialization
            limit = np.sqrt(6 / (input_size + output_size))
            weights = self.rng.uniform(-limit, limit, size=(output_size, input_size))
            biases = np.zeros(output_size)
            self.layers.append(LayerWeights(weights=weights, biases=biases))

    def clone(self, rng: np.random.Generator | None = None) -> "NeuralNetwork":
        # Fresh RNG unless one is given, so parent and clone never share state by accident.
        clone = NeuralNetwork.__new__(NeuralNetwork)
        clone.layer_sizes = self.layer_sizes
        clone.rng = rng if rng is not None else np.random.default_rng()
        clone.layers = [
            LayerWeights(weights=np.array(layer.weights, copy=True), biases=np.array(layer.biases, copy=True))
            for layer in self.layers
        ]
        return clone

    def compatible(self, other: object) -> bool:
        return type(other) is NeuralNetwork and tuple(other.layer_sizes) == self.layer_sizes

    def forward(self, inputs: np.ndarray, commit: bool = True) -> np.ndarray:
        # `commit` is ignored: the MLP is stateless.
        activation = inputs
        self._cache: List[np.ndarray] = [activation]
        for layer in self.layers[:-1]:
            z = np.dot(layer.weights, activation) + layer.biases
            activation = np.tanh(z)
            self._cache.append(activation)
        # Last layer is linear to allow continuous action values
        final_layer = self.layers[-1]
        output = np.dot(final_layer.weights, activation) + final_layer.biases
        self._cache.append(output)
        return output

    def backward(self, gradient: np.ndarray, learning_rate: float) -> None:
        """Backpropagate a gradient (dLoss/dOutput) through the network and update weights."""

        activations = self._cache
        delta = gradient
        # Update final layer (linear)
        last_activation = activations[-2]
        final_layer = self.layers[-1]
        grad_w = np.outer(delta, last_activation)
        grad_b = delta
        final_layer.weights -= learning_rate * grad_w
        final_layer.biases -= learning_rate * grad_b

        # Propagate backwards through hidden layers
        delta = np.dot(final_layer.weights.T, delta)
        for layer_index in range(len(self.layers) - 2, -1, -1):
            layer = self.layers[layer_index]
            activation = activations[layer_index + 1]
            prev_activation = activations[layer_index]
            # Derivative of tanh is (1 - tanh^2)
            activation_grad = (1 - np.square(activation)) * delta
            grad_w = np.outer(activation_grad, prev_activation)
            grad_b = activation_grad
            layer.weights -= learning_rate * grad_w
            layer.biases -= learning_rate * grad_b
            delta = np.dot(layer.weights.T, activation_grad)

    def mutate(self, mutation_rate: float, mutation_scale: float) -> None:
        for layer in self.layers:
            mask_w = self.rng.random(size=layer.weights.shape) < mutation_rate
            noise_w = self.rng.normal(scale=mutation_scale, size=layer.weights.shape)
            layer.weights += mask_w * noise_w

            mask_b = self.rng.random(size=layer.biases.shape) < mutation_rate
            noise_b = self.rng.normal(scale=mutation_scale, size=layer.biases.shape)
            layer.biases += mask_b * noise_b

    @staticmethod
    def crossover(parent_a: "NeuralNetwork", parent_b: "NeuralNetwork", rng: np.random.Generator | None = None) -> "NeuralNetwork":
        if not parent_a.compatible(parent_b):
            raise ValueError("Parent networks must have identical architectures for crossover")
        rng = rng if rng is not None else np.random.default_rng()
        child = NeuralNetwork(parent_a.layer_sizes, rng=rng)
        for layer_idx, (layer_a, layer_b) in enumerate(zip(parent_a.layers, parent_b.layers)):
            mix_mask = rng.random(size=layer_a.weights.shape) < 0.5
            child.layers[layer_idx].weights = np.where(mix_mask, layer_a.weights, layer_b.weights)

            mix_mask_b = rng.random(size=layer_a.biases.shape) < 0.5
            child.layers[layer_idx].biases = np.where(mix_mask_b, layer_a.biases, layer_b.biases)
        return child

    def to_dict(self) -> dict:
        return {
            "type": "mlp",
            "layer_sizes": list(self.layer_sizes),
            "layers": [
                {"weights": layer.weights.tolist(), "biases": layer.biases.tolist()} for layer in self.layers
            ],
        }

    @classmethod
    def from_dict(cls, data: dict, rng: np.random.Generator | None = None) -> "NeuralNetwork":
        # Build without Xavier init so loading never consumes draws from a shared rng.
        network = cls.__new__(cls)
        network.layer_sizes = tuple(data["layer_sizes"])
        network.rng = rng if rng is not None else np.random.default_rng()
        network.layers = [
            LayerWeights(
                weights=np.array(layer_data["weights"], dtype=float),
                biases=np.array(layer_data["biases"], dtype=float),
            )
            for layer_data in data["layers"]
        ]
        return network
