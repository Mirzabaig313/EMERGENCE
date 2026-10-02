"""Brain types for EMERGENCE creatures, including connectome-seeded brains.

Every brain follows one duck-typed contract (no Protocol class):

    brain_type: str
    forward(inputs: (5,), commit: bool = True) -> (3,)
    backward(gradient: (3,), learning_rate: float) -> None   # gradient = dLoss/dOutput
    mutate(mutation_rate: float, mutation_scale: float) -> None
    clone(rng=None) -> brain
    crossover(a, b, rng=None) -> brain                         # staticmethod
    compatible(other) -> bool                                  # same class and topology
    to_dict() -> dict

Inputs (see Herbivore.perceive): hunger, health, food_distance, food_direction, speed.
Outputs (see Herbivore.apply_action): move_x, move_y, eat.

Brain types:
    random                - dense 5-8-3 MLP (the original brain)
    recurrent             - dense 8-node rate network with state carried across ticks
    connectome            - wiring + signs from a fly connectome circuit, settles from rest each tick
    connectome-recurrent  - same wiring, state carried across ticks
    generative            - sparse wiring sampled from MICrONS-style cell-type connection probabilities
"""

from __future__ import annotations

import functools
import json
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np

from emergence.neural import NeuralNetwork

SENSORS = ("hunger", "health", "food_distance", "food_direction", "speed")
ACTIONS = ("move_x", "move_y", "eat")
BRAIN_TYPES = ("random", "connectome", "recurrent", "connectome-recurrent", "generative")

CONNECTOME_PATH = Path(__file__).parent / "assets" / "connectome_fly.json"
CONNECTOME_GAIN = 1.5  # scales normalized synapse weights into a useful tanh range
STEPS = 4  # settle iterations for stateless graph brains
MAX_HOPS = STEPS - 1  # signal horizon of a stateless forward pass starting from rest

# Sign of each presynaptic transmitter (Dale's law).
# ponytail: monoamines/unknown treated as excitatory; real modulatory effects are receptor-dependent.
NT_SIGN = {"ACh": 1, "GABA": -1, "Glu": -1, "His": -1, "histamine": -1}

# MICrONS-inspired connection probabilities P[pre][post] for mouse V1 cell classes.
# Illustrative order-of-magnitude values, NOT extracted data; verify against source:
#   MICrONS Consortium, Nature 640 (2025), "Functional connectomics spanning multiple areas of mouse visual cortex"
#   Schneider-Mizell et al., Nature (2025), inhibitory connectomic census of mouse visual cortex
#   Campagnola et al., Science 375 (2022), local connectivity in mouse and human cortex
MICRONS_CONNECTION_PROB: Dict[str, Dict[str, float]] = {
    "E": {"E": 0.10, "PV": 0.40, "SST": 0.30, "VIP": 0.10},
    "PV": {"E": 0.50, "PV": 0.50, "SST": 0.05, "VIP": 0.05},
    "SST": {"E": 0.40, "PV": 0.30, "SST": 0.05, "VIP": 0.30},
    "VIP": {"E": 0.05, "PV": 0.05, "SST": 0.40, "VIP": 0.05},
}
GENERATIVE_CLASSES = ["E"] * 12 + ["PV"] * 2 + ["SST", "VIP"]


class GraphBrain:
    """Sparse, signed, rate-based brain over N graph nodes. Weight matrix is W[post, pre]."""

    def __init__(
        self,
        brain_type: str,
        W: np.ndarray,
        mask: np.ndarray,
        sign: Optional[np.ndarray],
        b: np.ndarray,
        U: np.ndarray,
        U_mask: np.ndarray,
        R: np.ndarray,
        R_mask: np.ndarray,
        b_out: np.ndarray,
        recurrent: bool,
        alpha: float = 0.5,
        steps: int = STEPS,
        rng: Optional[np.random.Generator] = None,
    ):
        self.brain_type = brain_type
        self.rng = rng if rng is not None else np.random.default_rng()
        self.W = np.array(W, dtype=float, copy=True)
        self.mask = np.array(mask, dtype=bool, copy=True)
        self.sign = None if sign is None else np.array(sign, dtype=float, copy=True)
        self.b = np.array(b, dtype=float, copy=True)
        self.U = np.array(U, dtype=float, copy=True)
        self.U_mask = np.array(U_mask, dtype=bool, copy=True)
        self.R = np.array(R, dtype=float, copy=True)
        self.R_mask = np.array(R_mask, dtype=bool, copy=True)
        self.b_out = np.array(b_out, dtype=float, copy=True)
        self.recurrent = bool(recurrent)
        self.alpha = float(alpha)
        self.steps = int(steps)
        self.n = self.W.shape[0]
        self.h = np.zeros(self.n)
        self._h_used = np.zeros(self.n)
        self.node_names: Optional[List[str]] = None
        self.node_neuropils: Optional[List[str]] = None
        self._apply_constraints()

    # -- core dynamics -----------------------------------------------------
    def forward(self, inputs: np.ndarray, commit: bool = True) -> np.ndarray:
        drive = self.U @ np.asarray(inputs, dtype=float) + self.b
        if self.recurrent:
            h = (1.0 - self.alpha) * self.h + self.alpha * np.tanh(self.W @ self.h + drive)
        else:
            h = np.zeros(self.n)
            for _ in range(self.steps):
                h = np.tanh(self.W @ h + drive)
        if commit:
            self.h = h
            self._h_used = h
        return self.R @ h + self.b_out

    def backward(self, gradient: np.ndarray, learning_rate: float) -> None:
        # ponytail: readout-only learning; lifetime RL can't reshape connectome weights (evolution does).
        # Upgrade path: truncated BPTT through W.
        gradient = np.asarray(gradient, dtype=float)
        self.R -= learning_rate * np.outer(gradient, self._h_used) * self.R_mask
        self.b_out -= learning_rate * gradient

    def _apply_constraints(self) -> None:
        """Fixed topology + Dale's law: weights may reach 0 but never flip sign."""
        self.W *= self.mask
        if self.sign is not None:
            self.W = np.where(self.sign[None, :] > 0, np.maximum(self.W, 0.0), np.minimum(self.W, 0.0))
        self.U *= self.U_mask
        self.R *= self.R_mask

    # -- evolution ---------------------------------------------------------
    def mutate(self, mutation_rate: float, mutation_scale: float) -> None:
        for name, mask in (("W", self.mask), ("U", self.U_mask), ("R", self.R_mask), ("b", None), ("b_out", None)):
            arr = getattr(self, name)
            hit = self.rng.random(arr.shape) < mutation_rate
            if mask is not None:
                hit &= mask
            arr += hit * self.rng.normal(0.0, mutation_scale, arr.shape)
        self._apply_constraints()

    def compatible(self, other: object) -> bool:
        if type(other) is not GraphBrain or other.brain_type != self.brain_type:
            return False
        same_sign = (self.sign is None and other.sign is None) or (
            self.sign is not None and other.sign is not None and np.array_equal(self.sign, other.sign)
        )
        return (
            same_sign
            and np.array_equal(self.mask, other.mask)
            and np.array_equal(self.U_mask, other.U_mask)
            and np.array_equal(self.R_mask, other.R_mask)
        )

    def clone(self, rng: Optional[np.random.Generator] = None) -> "GraphBrain":
        child = GraphBrain(
            self.brain_type, self.W, self.mask, self.sign, self.b, self.U, self.U_mask,
            self.R, self.R_mask, self.b_out, self.recurrent, self.alpha, self.steps, rng=rng,
        )
        child.node_names = list(self.node_names) if self.node_names else None
        child.node_neuropils = list(self.node_neuropils) if self.node_neuropils else None
        return child

    @staticmethod
    def crossover(a: "GraphBrain", b: "GraphBrain", rng: Optional[np.random.Generator] = None) -> "GraphBrain":
        if not a.compatible(b):
            raise ValueError("Parent brains must share brain type and topology for crossover")
        rng = rng if rng is not None else np.random.default_rng()
        child = a.clone(rng=rng)
        for name in ("W", "b", "U", "R", "b_out"):
            pa, pb = getattr(a, name), getattr(b, name)
            setattr(child, name, np.where(rng.random(pa.shape) < 0.5, pa, pb))
        child._apply_constraints()
        return child

    # -- serialization -----------------------------------------------------
    def to_dict(self) -> dict:
        post, pre = np.nonzero(self.mask)
        u_node, u_sensor = np.nonzero(self.U_mask)
        r_action, r_node = np.nonzero(self.R_mask)
        return {
            "type": "graph",
            "brain_type": self.brain_type,
            "n": self.n,
            "recurrent": self.recurrent,
            "alpha": self.alpha,
            "steps": self.steps,
            "sign": None if self.sign is None else [int(s) for s in self.sign],
            "edges": [[int(i), int(j), float(self.W[i, j])] for i, j in zip(post, pre)],
            "bias": self.b.tolist(),
            "input": [[int(i), int(s), float(self.U[i, s])] for i, s in zip(u_node, u_sensor)],
            "readout": [[int(a), int(i), float(self.R[a, i])] for a, i in zip(r_action, r_node)],
            "readout_bias": self.b_out.tolist(),
            "state": self.h.tolist(),
        }

    @classmethod
    def from_dict(cls, data: dict, rng: Optional[np.random.Generator] = None) -> "GraphBrain":
        n = int(data["n"])
        W, mask = np.zeros((n, n)), np.zeros((n, n), dtype=bool)
        for i, j, w in data["edges"]:
            W[i, j], mask[i, j] = w, True  # zero-weight edges keep their topology slot
        U, U_mask = np.zeros((n, len(SENSORS))), np.zeros((n, len(SENSORS)), dtype=bool)
        for i, s, w in data["input"]:
            U[i, s], U_mask[i, s] = w, True
        R, R_mask = np.zeros((len(ACTIONS), n)), np.zeros((len(ACTIONS), n), dtype=bool)
        for a, i, w in data["readout"]:
            R[a, i], R_mask[a, i] = w, True
        brain = cls(
            data["brain_type"], W, mask, None if data.get("sign") is None else np.array(data["sign"], dtype=float),
            np.array(data["bias"], dtype=float), U, U_mask, R, R_mask, np.array(data["readout_bias"], dtype=float),
            data["recurrent"], data.get("alpha", 0.5), data.get("steps", STEPS), rng=rng,
        )
        state = data.get("state")
        if state is not None and len(state) == n:
            brain.h = np.array(state, dtype=float)
        return brain


# -- connectome loading ------------------------------------------------------
@functools.lru_cache(maxsize=4)
def load_connectome(path: Union[str, Path, None] = None) -> dict:
    """Load and validate a connectome JSON (schema_version 1).

    The result is cached and shared: treat it as READ-ONLY. Copy anything you keep.
    """
    path = Path(path) if path is not None else CONNECTOME_PATH
    with open(path, "r", encoding="utf-8") as fh:
        conn = json.load(fh)
    _validate_connectome(conn)
    return conn


def _validate_connectome(conn: dict) -> None:
    def fail(msg: str) -> None:
        raise ValueError(f"Invalid connectome: {msg}")

    if conn.get("schema_version") != 1:
        fail(f"schema_version must be 1, got {conn.get('schema_version')!r}")
    nodes = conn.get("nodes") or []
    if not nodes:
        fail("no nodes")
    if [nd.get("id") for nd in nodes] != list(range(len(nodes))):
        fail("node ids must be unique, contiguous and ordered from 0")
    for nd in nodes:
        if nd.get("role") not in ("input", "hidden", "output"):
            fail(f"node {nd.get('id')} has invalid role {nd.get('role')!r}")
        if nd.get("sign") not in (-1, 1):
            fail(f"node {nd['id']} sign must be -1 or 1")
        if "neuropil" in nd and not (isinstance(nd["neuropil"], str) and nd["neuropil"]):
            fail(f"node {nd['id']} neuropil must be a non-empty string")
    n, seen = len(nodes), set()
    for e in conn.get("edges") or []:
        pre, post, w = e.get("pre"), e.get("post"), e.get("weight")
        if not (isinstance(pre, int) and isinstance(post, int) and 0 <= pre < n and 0 <= post < n):
            fail(f"edge {e} has out-of-range node index")
        if not (isinstance(w, (int, float)) and w > 0):
            fail(f"edge {e} weight must be > 0")
        if (pre, post) in seen:
            fail(f"duplicate edge ({pre}, {post})")
        seen.add((pre, post))
    sensor_map, motor_map = conn.get("sensor_map") or {}, conn.get("motor_map") or {}
    if not set(sensor_map) <= set(SENSORS):
        fail(f"unknown sensors {sorted(set(sensor_map) - set(SENSORS))}")
    if set(motor_map) != set(ACTIONS):
        fail(f"motor_map keys must be exactly {list(ACTIONS)}")
    for mapping in (sensor_map, motor_map):
        for key, entries in mapping.items():
            for entry in entries:
                if len(entry) != 2 or not (isinstance(entry[0], int) and 0 <= entry[0] < n):
                    fail(f"map entry {key}: {entry} is invalid")


def unreachable_outputs(source: Union[dict, GraphBrain], max_hops: int = MAX_HOPS) -> list:
    """Motor-readout nodes not reachable from any sensor node within `max_hops` edges.

    Returns node names for a connectome dict, node indices for a GraphBrain.
    """
    if isinstance(source, GraphBrain):
        n = source.n
        adj = [list(np.flatnonzero(source.mask[:, j])) for j in range(n)]  # pre -> posts
        sensors = set(np.flatnonzero(source.U_mask.any(axis=1)).tolist())
        motors = sorted(set(np.flatnonzero(source.R_mask.any(axis=0)).tolist()))
        label = lambda i: int(i)  # noqa: E731
    else:
        n = len(source["nodes"])
        adj = [[] for _ in range(n)]
        for e in source["edges"]:
            adj[e["pre"]].append(e["post"])
        sensors = {entry[0] for entries in source["sensor_map"].values() for entry in entries}
        motors = sorted({entry[0] for entries in source["motor_map"].values() for entry in entries})
        label = lambda i: source["nodes"][i]["name"]  # noqa: E731
    hops = {s: 0 for s in sensors}
    queue = deque(sensors)
    while queue:
        node = queue.popleft()
        if hops[node] >= max_hops:
            continue
        for nxt in adj[node]:
            if nxt not in hops:
                hops[nxt] = hops[node] + 1
                queue.append(nxt)
    return [label(m) for m in motors if m not in hops]


# -- factories -----------------------------------------------------------------
def _connectome_brain(kind: str, rng: np.random.Generator, conn: Optional[dict] = None) -> GraphBrain:
    conn = conn if conn is not None else load_connectome()
    n = len(conn["nodes"])
    sign = np.array([nd["sign"] for nd in conn["nodes"]], dtype=float)
    W, mask = np.zeros((n, n)), np.zeros((n, n), dtype=bool)
    for e in conn["edges"]:
        mask[e["post"], e["pre"]] = True
        W[e["post"], e["pre"]] = e["weight"]
    W = sign[None, :] * W * CONNECTOME_GAIN * (1.0 + 0.1 * rng.standard_normal((n, n)))
    U, U_mask = np.zeros((n, len(SENSORS))), np.zeros((n, len(SENSORS)), dtype=bool)
    for s_idx, sensor in enumerate(SENSORS):
        for node, gain in conn["sensor_map"].get(sensor, []):
            U[node, s_idx] = gain * (1.0 + 0.1 * rng.standard_normal())
            U_mask[node, s_idx] = True
    R, R_mask = np.zeros((len(ACTIONS), n)), np.zeros((len(ACTIONS), n), dtype=bool)
    for a_idx, action in enumerate(ACTIONS):
        for node, gain in conn["motor_map"][action]:
            R[a_idx, node] = gain * (1.0 + 0.1 * rng.standard_normal())
            R_mask[a_idx, node] = True
    recurrent = kind == "connectome-recurrent"
    brain = GraphBrain(
        kind, W, mask, sign, np.zeros(n), U, U_mask, R, R_mask, np.zeros(len(ACTIONS)),
        recurrent=recurrent, alpha=0.5, steps=1 if recurrent else STEPS, rng=rng,
    )
    brain.node_names = [nd["name"] for nd in conn["nodes"]]
    brain.node_neuropils = [nd.get("neuropil", "unknown") for nd in conn["nodes"]]
    return brain


def _recurrent_brain(rng: np.random.Generator, n: int = 8) -> GraphBrain:
    W = rng.normal(0.0, 0.9 / np.sqrt(n), (n, n))
    lim_u, lim_r = np.sqrt(6 / (len(SENSORS) + n)), np.sqrt(6 / (n + len(ACTIONS)))
    U = rng.uniform(-lim_u, lim_u, (n, len(SENSORS)))
    R = rng.uniform(-lim_r, lim_r, (len(ACTIONS), n))
    return GraphBrain(
        "recurrent", W, np.ones((n, n), dtype=bool), None, np.zeros(n), U, np.ones_like(U, dtype=bool),
        R, np.ones_like(R, dtype=bool), np.zeros(len(ACTIONS)), recurrent=True, alpha=0.5, steps=1, rng=rng,
    )


def _generative_weights(mask: np.ndarray, sign: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Lognormal synapse magnitudes on `mask`, signed by presynaptic class, scaled by 1/sqrt(mean in-degree)."""
    mean_in = max(1.0, mask.sum(axis=1).mean())
    mags = rng.lognormal(-1.0, 0.5, mask.shape) / np.sqrt(mean_in)
    return sign[None, :] * mags * mask


def generate_template(rng: np.random.Generator) -> GraphBrain:
    """Sample a MICrONS-style sparse circuit with every readout reachable from the sensors."""
    classes = GENERATIVE_CLASSES
    n = len(classes)
    sign = np.array([1.0 if c == "E" else -1.0 for c in classes])
    prob = np.array([[MICRONS_CONNECTION_PROB[classes[pre]][classes[post]] for pre in range(n)] for post in range(n)])
    U_mask = np.zeros((n, len(SENSORS)), dtype=bool)
    for s in range(len(SENSORS)):
        U_mask[s, s] = True  # sensors drive E0..E4
    R = np.zeros((len(ACTIONS), n))
    for a, node, gain in ((0, 9, 1.0), (0, 10, -1.0), (1, 11, 1.0), (1, 8, -1.0), (2, 7, 1.0)):
        R[a, node] = gain
    R_mask = R != 0

    def build(mask: np.ndarray) -> GraphBrain:
        return GraphBrain(
            "generative", np.zeros((n, n)), mask, sign, np.zeros(n), U_mask.astype(float), U_mask,
            R, R_mask, np.zeros(len(ACTIONS)), recurrent=False, steps=STEPS, rng=rng,
        )

    # ponytail: rejection sampling biases connectivity slightly above the table's probabilities.
    for _ in range(100):
        mask = rng.random((n, n)) < prob
        np.fill_diagonal(mask, False)
        template = build(mask)
        if not unreachable_outputs(template, MAX_HOPS):
            break
    else:
        for k in unreachable_outputs(template, MAX_HOPS):
            mask[k, k % len(SENSORS)] = True  # direct E->E edge from a sensor node
        template = build(mask)
    template.W = _generative_weights(template.mask, sign, rng)
    template._apply_constraints()
    return template


def make_brain(kind: str, rng: np.random.Generator, template: Optional[GraphBrain] = None):
    """Build a new brain of the given type. `template` is the shared generative topology."""
    if kind == "random":
        return NeuralNetwork((5, 8, 3), rng=rng)
    if kind == "recurrent":
        return _recurrent_brain(rng)
    if kind in ("connectome", "connectome-recurrent"):
        return _connectome_brain(kind, rng)
    if kind == "generative":
        if template is None:
            return generate_template(rng)
        brain = template.clone(rng=rng)
        brain.h = np.zeros(brain.n)
        brain.W = _generative_weights(brain.mask, brain.sign, rng)
        brain._apply_constraints()
        return brain
    raise ValueError(f"Unknown brain type {kind!r}; choose one of {', '.join(BRAIN_TYPES)}")


def brain_from_dict(data: dict, rng: Optional[np.random.Generator] = None):
    """Rebuild any brain from to_dict() output. Missing 'type' means an old-format MLP save."""
    if data.get("type", "mlp") == "mlp":
        return NeuralNetwork.from_dict(data, rng=rng)
    brain = GraphBrain.from_dict(data, rng=rng)
    if brain.brain_type.startswith("connectome"):
        try:
            conn = load_connectome()
        except (OSError, ValueError):
            conn = None
        if conn is not None and len(conn["nodes"]) == brain.n:
            brain.node_names = [nd["name"] for nd in conn["nodes"]]
            brain.node_neuropils = [nd.get("neuropil", "unknown") for nd in conn["nodes"]]
    return brain


def parameter_count(brain) -> int:
    if isinstance(brain, GraphBrain):
        return int(brain.mask.sum() + brain.U_mask.sum() + brain.R_mask.sum() + brain.n + len(ACTIONS))
    return int(sum(layer.weights.size + layer.biases.size for layer in brain.layers))


def brain_summary_lines(brain) -> List[str]:
    """Short human-readable description shared by the CLI and TUI."""
    lines = [f"Type: {getattr(brain, 'brain_type', 'random')}", f"Parameters: {parameter_count(brain)}"]
    if isinstance(brain, GraphBrain):
        edges = int(brain.mask.sum())
        inhib = int((brain.mask & (brain.W < 0)).sum()) if brain.sign is not None else int((brain.W < 0).sum())
        lines += [
            f"Nodes: {brain.n}  Edges: {edges}  Inhibitory: {100 * inhib / max(1, edges):.0f}%",
            f"Dynamics: {'recurrent, alpha=' + format(brain.alpha, '.2f') if brain.recurrent else f'settles in {brain.steps} steps'}",
            f"State norm: {float(np.linalg.norm(brain.h)):.3f}",
        ]
    else:
        lines.append("Layers: " + " -> ".join(str(s) for s in brain.layer_sizes))
    return lines


def neuropil_table(brain) -> List[tuple]:
    """(neuropil, nodes, within-neuropil edges) rows, FlyBrainLab-style LPU grouping. Empty if unknown."""
    if not isinstance(brain, GraphBrain) or not brain.node_neuropils:
        return []
    labels = brain.node_neuropils
    rows = []
    for np_name in sorted(set(labels)):
        idx = [i for i, lab in enumerate(labels) if lab == np_name]
        within = int(brain.mask[np.ix_(idx, idx)].sum())
        rows.append((np_name, len(idx), within))
    return rows


def top_readouts(brain, k: int = 3) -> Dict[str, List[tuple]]:
    """Strongest readout weights per action: {action: [(node label, weight), ...]}."""
    if not isinstance(brain, GraphBrain):
        return {}
    out: Dict[str, List[tuple]] = {}
    for a, action in enumerate(ACTIONS):
        nodes = np.flatnonzero(brain.R_mask[a])
        nodes = nodes[np.argsort(-np.abs(brain.R[a, nodes]))][:k]
        label = (lambda i: brain.node_names[i]) if brain.node_names else str
        out[action] = [(label(int(i)), float(brain.R[a, i])) for i in nodes]
    return out

