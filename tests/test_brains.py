"""Brain types: contract, Dale's law, topology, serialization, connectome asset, old saves."""

import importlib.resources
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from emergence.brains import (
    BRAIN_TYPES,
    GraphBrain,
    brain_from_dict,
    generate_template,
    load_connectome,
    make_brain,
    unreachable_outputs,
)
from emergence.neural import NeuralNetwork
from emergence.reinforcement import RLAgent

ROOT = Path(__file__).resolve().parent.parent
X = np.array([0.5, 0.9, 0.3, 0.1, 0.2])


def rng(seed=0):
    return np.random.default_rng(seed)


@pytest.mark.parametrize("kind", BRAIN_TYPES)
def test_every_type_maps_5_to_3_and_roundtrips(kind):
    brain = make_brain(kind, rng())
    for _ in range(3):
        out = brain.forward(X)
    assert out.shape == (3,)
    clone = brain_from_dict(json.loads(json.dumps(brain.to_dict())), rng(1))
    assert type(clone) is type(brain) and clone.brain_type == brain.brain_type
    assert brain.compatible(clone)
    # Same weights (+ restored recurrent state) -> same next output
    assert np.allclose(clone.forward(X, commit=False), brain.forward(X, commit=False))


@pytest.mark.parametrize("kind", ["connectome", "generative"])
def test_dale_law_and_fixed_topology_survive_mutation_and_crossover(kind):
    r = rng(3)
    template = generate_template(r) if kind == "generative" else None
    a, b = make_brain(kind, r, template), make_brain(kind, r, template)
    mask = a.mask.copy()
    for _ in range(50):
        a.mutate(0.5, 1.0)
    child = GraphBrain.crossover(a, b, r)
    for brain in (a, child):
        assert not (brain.W[~mask] != 0).any(), "mutation/crossover created an edge"
        assert np.array_equal(brain.mask, mask)
        exc = brain.sign[None, :] > 0
        assert (brain.W[np.broadcast_to(exc, brain.W.shape)] >= 0).all()
        assert (brain.W[np.broadcast_to(~exc, brain.W.shape)] <= 0).all()


def test_recurrent_state_persists_only_on_commit():
    brain = make_brain("connectome-recurrent", rng())
    brain.forward(X)
    h1 = brain.h.copy()
    brain.forward(X, commit=False)
    assert np.array_equal(brain.h, h1)
    brain.forward(X)
    assert not np.array_equal(brain.h, h1)


def test_compatible_rules():
    r = rng()
    rec_a, rec_b = make_brain("recurrent", r), make_brain("recurrent", r)
    assert rec_a.compatible(rec_b)  # both sign=None, same dense mask
    assert not rec_a.compatible(make_brain("connectome", r))
    assert not make_brain("random", r).compatible(rec_a)


def test_placeholder_connectome_is_valid_reachable_and_packaged():
    conn = load_connectome()  # placeholder or a real extraction; both must validate
    assert isinstance(conn["synthetic_placeholder"], bool)
    assert all(nd["neuropil"] for nd in conn["nodes"])
    assert unreachable_outputs(conn, 3) == []
    packaged = importlib.resources.files("emergence") / "assets" / "connectome_fly.json"
    assert packaged.is_file()


def test_loader_rejects_duplicate_edge_accepts_self_loop(tmp_path):
    conn = json.loads((ROOT / "emergence/assets/connectome_fly.json").read_text())
    conn["edges"].append({"pre": 5, "post": 5, "synapses": 10, "weight": 0.1})
    ok = tmp_path / "ok.json"
    ok.write_text(json.dumps(conn))
    load_connectome(ok)
    conn["edges"].append(dict(conn["edges"][0]))
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(conn))
    with pytest.raises(ValueError, match="duplicate"):
        load_connectome(bad)


def test_brain_arrays_do_not_alias_cached_connectome():
    brain = make_brain("connectome", rng())
    brain.W[:] = 99.0
    assert load_connectome()["edges"][0]["weight"] <= 1.0


def test_generative_templates_always_reachable():
    assert all(unreachable_outputs(generate_template(rng(s)), 3) == [] for s in range(200))


def test_mixed_brain_parents_fall_back_to_clone():
    from emergence.world import World

    world = World(rng=rng(5))
    a = world.spawn_herbivore()
    world.config.brain_type = "connectome"
    b = world.spawn_herbivore()
    world.genetics.crossover_rate = 1.0
    child = world.genetics.reproduce(a, b, "kid", np.zeros(2), world.rng)
    assert type(child.brain) is NeuralNetwork


def test_reward_moves_output_toward_last_action():
    agent = RLAgent(NeuralNetwork((5, 8, 3), rng=rng()), learning_rate=0.05, epsilon=0.0, rng=rng())
    action = agent.choose_action(X, explore=False)
    before = agent.brain.forward(X)
    agent.reinforce(5.0)
    after = agent.brain.forward(X)
    assert float(np.dot(after - before, np.sign(action))) > 0
    agent.reinforce(-5.0)
    assert float(np.dot(agent.brain.forward(X) - after, np.sign(action))) < 0


def test_build_connectome_on_toy_tuples():
    sys.path.insert(0, str(ROOT / "scripts"))
    from extract_connectome import build_connectome

    types = ["S1", "H1", "M1", "M2", "M3"]
    roles = {"S1": "input", "H1": "hidden", "M1": "output", "M2": "output", "M3": "output"}
    edges = {("S1", "H1"): 50, ("H1", "M1"): 20, ("H1", "M2"): 10, ("H1", "M3"): 5, ("X", "H1"): 9}
    conn = build_connectome(
        types, roles, edges, {"S1": "acetylcholine", "H1": "gaba"}, {}, {"hunger": [("S1", 1.0)]},
        {"move_x": [("M1", 1.0)], "move_y": [("M2", 1.0)], "eat": [("M3", 1.0)]}, {"source": "toy"},
    )
    assert [nd["sign"] for nd in conn["nodes"]][:2] == [1, -1]
    assert len(conn["edges"]) == 4 and conn["edges"][0]["weight"] == 1.0
    assert unreachable_outputs(conn, 3) == []


def test_old_autosave_loads_with_identical_forward(tmp_path):
    from emergence.world import World

    src = ROOT / "emergence_autosave.json"
    if not src.exists():
        pytest.skip("no autosave fixture")
    path = tmp_path / "old.json"
    shutil.copy(src, path)
    raw = json.loads(path.read_text())
    world = World.load(path)
    assert world.config.brain_type == "random"
    assert len(world.herbivores) == len(raw["herbivores"])
    for herb, data in zip(world.herbivores, raw["herbivores"]):
        assert type(herb.brain) is NeuralNetwork
        layers = data["agent"]["brain"]["layers"]
        hidden = np.tanh(np.array(layers[0]["weights"]) @ X + np.array(layers[0]["biases"]))
        ref = np.array(layers[1]["weights"]) @ hidden + np.array(layers[1]["biases"])
        assert np.allclose(herb.brain.forward(X), ref)
