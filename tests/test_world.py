"""World: determinism, persistence, gameplay wiring, disease, validation, perf invariants."""

import json

import numpy as np
import pytest

from emergence.brains import BRAIN_TYPES
from emergence.cli import EmergenceCLI, bootstrap_world, parse_args, parse_finite_float
from emergence.entities import plant_distances
from emergence.world import World, WorldConfig


def make_world(seed=42, **config):
    world = World(config=WorldConfig(**config), rng=np.random.default_rng(seed))
    bootstrap_world(world)
    return world


def snapshot(world):
    return [(h.name, h.position.round(9).tolist(), round(h.energy, 9)) for h in world.herbivores]


@pytest.mark.parametrize("kind", BRAIN_TYPES)
def test_same_seed_is_deterministic(kind):
    a, b = make_world(brain_type=kind), make_world(brain_type=kind)
    a.simulate(200)
    b.simulate(200)
    assert snapshot(a) == snapshot(b)


def test_vectorized_distances_match_linalg_norm_exactly():
    v = np.random.default_rng(1).uniform(-500, 500, (10_000, 2))
    assert np.array_equal(plant_distances(v, np.zeros(2)), np.array([np.linalg.norm(x) for x in v]))


def test_traits_and_stats_survive_save_load(tmp_path):
    world = make_world(brain_type="connectome-recurrent", disease_enabled=True)
    world.simulate(300)
    h = world.herbivores[0]
    h.metabolism, h.vision_range, h.immune_strength = 0.37, 71.0, 0.8
    path = tmp_path / "w.json"
    world.save(path)
    loaded = World.load(path)
    lh = loaded.herbivores[0]
    assert (lh.metabolism, lh.vision_range, lh.immune_strength) == (0.37, 71.0, 0.8)
    assert lh.brain_type == "connectome-recurrent"
    assert np.allclose(lh.brain.h, h.brain.h)
    assert loaded.stats.total_births == world.stats.total_births
    assert loaded.config.disease_enabled
    assert [g.generation for g in loaded.stats.generation_history] == [g.generation for g in world.stats.generation_history]


def test_stats_block_without_new_fields_loads(tmp_path):
    world = make_world()
    world.simulate(300)
    data = world.to_dict()
    for g in data["stats"]["generation_history"]:
        g.pop("brain_fitness")
    loaded = World.from_dict(json.loads(json.dumps(data)))
    assert all(g.brain_fitness == {} for g in loaded.stats.generation_history)


def test_atomic_save_keeps_original_on_failure(tmp_path, monkeypatch):
    world = make_world()
    path = tmp_path / "w.json"
    world.save(path)
    original = path.read_text()
    monkeypatch.setattr(json, "dump", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("disk full")))
    with pytest.raises(RuntimeError):
        world.save(path)
    assert path.read_text() == original
    assert not list(tmp_path.glob("*.tmp"))


def test_breed_records_birth_and_rejects_self():
    world = make_world()
    a, b = world.herbivores[:2]
    births = world.stats.total_births
    child = world.breed(a, b)
    assert world.stats.total_births == births + 1 and child.name in world.stats.family_tree
    with pytest.raises(ValueError):
        world.breed(a, a)


def test_gameplay_updates_after_generation_record():
    from emergence.game_modes import GameModeType
    from emergence.gameplay import GameplaySystem

    world = make_world()
    gp = GameplaySystem(world)
    gp.start_mode(GameModeType.SURVIVAL)
    world.simulate(1500)
    assert world.stats.total_generations > 1
    assert gp.state.generation == world.stats.total_generations


def test_challenge_config_restored_on_next_mode():
    from emergence.game_modes import ChallengeType, GameModeType
    from emergence.gameplay import GameplaySystem

    world = make_world()
    original = world.config.plant_spawn_rate
    gp = GameplaySystem(world)
    gp.start_mode(GameModeType.CHALLENGE, ChallengeType.DROUGHT)
    assert world.config.plant_spawn_rate != original
    gp.start_mode(GameModeType.SURVIVAL)
    assert world.config.plant_spawn_rate == original


def test_one_generation_event_is_active_for_one_pass(monkeypatch):
    from emergence import events
    from emergence.gameplay import GameplaySystem

    world = make_world()
    gp = GameplaySystem(world)
    gp.active = True
    for etype, ev in events.EVENT_DEFINITIONS.items():
        monkeypatch.setattr(ev, "probability", 1.0 if etype is events.EventType.DISEASE else 0.0)
    gp.update_generation(2)
    assert "health_reduction" in gp.event_manager.get_active_modifiers()
    monkeypatch.setattr(events.EVENT_DEFINITIONS[events.EventType.DISEASE], "probability", 0.0)
    gp.update_generation(3)
    assert "health_reduction" not in gp.event_manager.get_active_modifiers()


def _disease_world(**cfg):
    return make_world(disease_enabled=True, disease_seed_rate=0.0, disease_transmission=0.0, immune_cost=0.0, **cfg)


def test_strong_immunity_recovers_with_memory():
    world = _disease_world()
    h = world.herbivores[0]
    h.immune_strength, h.infection, h.energy, h.health = 0.5, 0.1, 100.0, 100.0
    for _ in range(15):
        world._update_disease({}, [])
    assert h.infection == 0.0 and h.immune_memory and world.stats.total_recoveries == 1


def test_weak_immunity_worsens():
    world = _disease_world()
    h = world.herbivores[0]
    h.immune_strength, h.infection, h.health = 0.2, 0.1, 1e9
    seen = []
    for _ in range(10):
        world._update_disease({}, [])
        seen.append(h.infection)
    assert seen == sorted(seen) and seen[-1] > 0.1


def test_disease_event_seeds_on_rising_edge_only():
    world = _disease_world()
    for _ in range(50):
        world._update_disease({"health_reduction": 0.5}, [])
    assert world.stats.total_infections <= 3


def test_disease_death_is_recorded():
    world = _disease_world()
    h = world.herbivores[0]
    h.infection, h.health, h.immune_strength = 1.0, 0.5, 0.0
    deaths = world.stats.total_deaths
    world.simulate(1)
    assert not h.alive and h not in world.herbivores
    assert world.stats.total_deaths > deaths


def test_learning_curves_bounded():
    world = make_world()
    world.simulate(3000)
    assert len(world.stats.learning_curves) <= 200
    dead = [n for n, d in world.stats.family_tree.items() if "death_tick" in d]
    assert dead and all("fitness_history" not in world.stats.family_tree[n] for n in dead)


def test_parse_finite_float_rejects_nan_inf():
    for bad in ("nan", "inf", "-inf"):
        with pytest.raises(ValueError):
            parse_finite_float(bad, 1.0)
    assert parse_finite_float("2.5", 1.0) == 2.5


def test_cli_args_and_world_injection():
    args = parse_args(["--brain", "connectome", "--seed", "3", "--disease"])
    assert (args.brain, args.seed, args.disease) == ("connectome", 3, True)
    with pytest.raises(SystemExit):
        parse_args(["--seed", "-1"])
    with pytest.raises(SystemExit):
        parse_args(["--brain", "nope"])
    world = make_world()
    world.simulate(5)
    count = len(world.herbivores)
    cli = EmergenceCLI(world)
    assert len(cli.world.herbivores) == count  # no re-bootstrap


def test_analyzer_brain_comparison_names_both_types():
    from emergence.analyzer import GameStateAnalyzer

    world = make_world()
    for i in range(6):
        world.stats.record_death(1, f"a{i}", (0, 0), 50, 10.0, 1, "connectome")
        world.stats.record_death(1, f"b{i}", (0, 0), 40, 5.0, 1, "random")
    [s] = GameStateAnalyzer().analyze_brain_types(world)
    assert "connectome" in s.description and "random" in s.description and s.command == "compare_brains"


def test_duplicate_entity_names_do_not_crash_removal():
    # Field equality used to compare numpy positions inside list.remove and raise ValueError.
    from emergence.entities import Plant

    world = make_world()
    a = Plant(name="dup", position=np.array([1.0, 1.0]), species="plant")
    b = Plant(name="dup", position=np.array([2.0, 2.0]), species="plant", alive=False, nutrients=0.0)
    world.plants[:0] = [a, b]
    world.simulate(1)
    assert a in world.plants and b not in world.plants
    h = world.herbivores[0]
    world.spawn_herbivore(name=h.name)
    h.health = 0.0
    world.simulate(1)


def test_spawned_plant_names_are_unique_after_removals():
    world = make_world()
    world.simulate(500)
    names = [p.name for p in world.plants]
    assert len(names) == len(set(names))
