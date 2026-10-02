"""Extract a small fly sensorimotor circuit from the Janelia male CNS connectome (neuPrint).

Writes emergence/assets/connectome_fly.json (schema_version 1) for the `connectome` brain types.

    pip install -e '.[connectome]'               # neuprint-python==0.6.4
    NEUPRINT_TOKEN=... python scripts/extract_connectome.py --dry-run
    NEUPRINT_TOKEN=... python scripts/extract_connectome.py

Get a token at https://neuprint.janelia.org (Account > Auth Token). The token is read from the
environment only and is never written or printed.

Unverified without a token: exact neuPrint column names and whether the default descending
neuron types exist in male-cns:v1.0. The script reports what it can't find.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from emergence.brains import MAX_HOPS, NT_SIGN, SENSORS, load_connectome, unreachable_outputs  # noqa: E402

DEFAULT_OUT = REPO_ROOT / "emergence" / "assets" / "connectome_fly.json"
NT_COLUMNS = ("consensusNt", "predictedNt", "celltypePredictedNt")
NT_ALIASES = {"acetylcholine": "ACh", "gaba": "GABA", "glutamate": "Glu", "histamine": "His"}


def parse_motor_map(text: str) -> Dict[str, List[Tuple[str, float]]]:
    """'move_x=DNa01:-1,DNa02:1;move_y=P9:1;eat=DNg11:1' -> {'move_x': [('DNa01', -1.0), ...], ...}"""
    result: Dict[str, List[Tuple[str, float]]] = {}
    for part in filter(None, text.split(";")):
        action, _, entries = part.partition("=")
        result[action.strip()] = [
            (name.strip(), float(gain)) for name, _, gain in (e.partition(":") for e in entries.split(",") if e)
        ]
    return result


def normalize_nt(value) -> str:
    if not isinstance(value, str) or not value:
        return "unknown"
    return NT_ALIASES.get(value.lower(), value)


def build_connectome(
    types: Sequence[str],
    roles: Dict[str, str],
    edges: Dict[Tuple[str, str], int],
    nts: Dict[str, str],
    n_neurons: Dict[str, int],
    sensor_assign: Dict[str, List[Tuple[str, float]]],
    motor_map: Dict[str, List[Tuple[str, float]]],
    meta: Dict[str, object],
    neuropils: Dict[str, str] | None = None,
) -> dict:
    """Pure (stdlib-only) builder for the schema_version 1 connectome dict."""
    index = {t: i for i, t in enumerate(types)}
    kept = {k: v for k, v in edges.items() if k[0] in index and k[1] in index and v > 0}
    max_syn = max(kept.values(), default=1)
    neuropils = neuropils or {}
    nodes = []
    for t in types:
        nt = normalize_nt(nts.get(t))
        nodes.append(
            {
                "id": index[t],
                "name": t,
                "role": roles[t],
                "nt": nt,
                "sign": NT_SIGN.get(nt, 1),
                "n_neurons": int(n_neurons.get(t, 1)),
                "neuropil": neuropils.get(t) or "unknown",
            }
        )
    return {
        "schema_version": 1,
        "synthetic_placeholder": False,
        **meta,
        "weight_normalization": "synapses / max(synapses) over kept edges",
        "nodes": nodes,
        "edges": [
            {"pre": index[a], "post": index[b], "synapses": int(s), "weight": round(s / max_syn, 4)}
            for (a, b), s in sorted(kept.items(), key=lambda kv: (index[kv[0][0]], index[kv[0][1]]))
        ],
        "sensor_map": {s: [[index[t], g] for t, g in entries] for s, entries in sensor_assign.items()},
        "motor_map": {a: [[index[t], g] for t, g in entries] for a, entries in motor_map.items()},
    }


def _fail(code: int, msg: str) -> int:
    print(msg, file=sys.stderr)
    return code


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--server", default="https://neuprint.janelia.org")
    parser.add_argument("--dataset", default="male-cns:v1.0")
    parser.add_argument("--outputs", default="DNa01,DNa02,MDN,P9,DNg11", help="Descending neuron types (motor nodes)")
    parser.add_argument("--motor-map", default="move_x=DNa01:-1,DNa02:1;move_y=P9:1,MDN:-1;eat=DNg11:1")
    parser.add_argument("--hidden-k", type=int, default=14)
    parser.add_argument("--input-k", type=int, default=5)
    parser.add_argument("--min-synapses", type=int, default=5)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true", help="Print a summary without writing")
    parser.add_argument("--force", action="store_true", help="Write even if some motor nodes are unreachable")
    args = parser.parse_args(argv)

    token = os.environ.get("NEUPRINT_TOKEN")
    if not token:
        return _fail(2, "NEUPRINT_TOKEN not set; get a token at neuprint.janelia.org (Account > Auth Token)")
    try:
        from neuprint import Client, NeuronCriteria as NC, fetch_neurons, fetch_simple_connections
    except ImportError:
        return _fail(2, "neuprint-python is not installed: pip install 'neuprint-python==0.6.4' (or pip install -e '.[connectome]')")

    def redact(e: Exception) -> str:
        return f"{type(e).__name__}: {str(e).replace(token, '***')}"

    try:
        client = Client(args.server, dataset=args.dataset, token=token)
    except Exception as e:  # network, auth, or unknown dataset
        try:
            names = sorted(Client(args.server, token=token).fetch_datasets())
            print(f"Available datasets: {', '.join(names)}", file=sys.stderr)
        except Exception:
            pass
        return _fail(3, f"neuPrint unreachable: {redact(e)}")

    outputs = [t.strip() for t in args.outputs.split(",") if t.strip()]
    motor_map = parse_motor_map(args.motor_map)
    try:
        # Upstream of the descending neurons -> hidden layer
        up = fetch_simple_connections(None, NC(type=outputs), min_weight=args.min_synapses, client=client)
        found = sorted(set(up["type_post"].dropna()))
        missing = [t for t in outputs if t not in found]
        if missing:
            print(f"Output types not found: {', '.join(missing)}", file=sys.stderr)
        if len(found) < 2:
            return _fail(4, "Fewer than 2 output types found; adjust --outputs")
        by_pre: Counter = Counter()
        per_output: Dict[str, Counter] = defaultdict(Counter)
        for row in up.itertuples():
            if isinstance(row.type_pre, str) and row.type_pre not in found:
                by_pre[row.type_pre] += int(row.weight)
                per_output[row.type_post][row.type_pre] += int(row.weight)
        # Give every output its strongest inputs first, so one heavily innervated output
        # (e.g. a walking DN) can't crowd out the others; fill the rest by total weight.
        quota = max(1, args.hidden_k // (2 * len(found)))
        hidden: List[str] = []
        for t in found:
            for pre, _ in per_output[t].most_common(quota):
                if pre not in hidden:
                    hidden.append(pre)
        for pre, _ in by_pre.most_common():
            if len(hidden) >= args.hidden_k:
                break
            if pre not in hidden:
                hidden.append(pre)

        # Upstream of hidden -> inputs (prefer sensory classes when the column exists)
        up2 = fetch_simple_connections(
            None, NC(type=hidden), min_weight=args.min_synapses, properties=["type", "superclass"], client=client
        )
        sensory_col = next((c for c in ("superclass_pre", "class_pre") if c in up2.columns), None)
        score: Counter = Counter()
        per_hidden: Dict[str, Counter] = defaultdict(Counter)
        for row in up2.itertuples():
            t = row.type_pre
            if not isinstance(t, str) or t in hidden or t in found:
                continue
            bonus = 10 if sensory_col and "sensory" in str(getattr(row, sensory_col, "")).lower() else 1
            score[t] += int(row.weight) * bonus
            per_hidden[row.type_post][t] += int(row.weight) * bonus
        # Same idea one layer up: every output first gets the strongest input into its own hidden feeders,
        # so it has a sensor -> hidden -> output path; the rest is filled by total (sensory-weighted) synapses.
        inputs: List[str] = []
        for t in found:
            feeders = [h for h in hidden if per_output[t][h] > 0]
            pool: Counter = sum((per_hidden[h] for h in feeders), Counter())
            for pre, _ in pool.most_common():
                if pre not in inputs:
                    inputs.append(pre)
                    break
        for pre, _ in score.most_common():
            if len(inputs) >= args.input_k:
                break
            if pre not in inputs:
                inputs.append(pre)
        types = inputs + hidden + found
        roles = {**{t: "input" for t in inputs}, **{t: "hidden" for t in hidden}, **{t: "output" for t in found}}

        conns = fetch_simple_connections(NC(type=types), NC(type=types), min_weight=args.min_synapses, client=client)
        edges: Dict[Tuple[str, str], int] = defaultdict(int)
        for row in conns.itertuples():
            if isinstance(row.type_pre, str) and isinstance(row.type_post, str):
                edges[(row.type_pre, row.type_post)] += int(row.weight)

        neuron_df, _roi_counts = fetch_neurons(NC(type=types), client=client)
    except Exception as e:
        return _fail(3, f"neuPrint query failed: {redact(e)}")

    nt_col = next((c for c in NT_COLUMNS if c in neuron_df.columns), None)
    if nt_col is None:
        print("Warning: no neurotransmitter column found; signs default to excitatory", file=sys.stderr)
    nts: Dict[str, str] = {}
    n_neurons: Dict[str, int] = Counter()
    neuropils: Dict[str, str] = {}
    by_type_nt: Dict[str, Counter] = defaultdict(Counter)
    for row in neuron_df.itertuples():
        n_neurons[row.type] += 1
        if nt_col:
            by_type_nt[row.type][normalize_nt(getattr(row, nt_col))] += 1
        rois = getattr(row, "inputRois", None) or getattr(row, "outputRois", None)
        if isinstance(rois, list) and rois and row.type not in neuropils:
            neuropils[row.type] = str(rois[0])
    for t, counter in by_type_nt.items():
        nts[t] = counter.most_common(1)[0][0]

    gains = {s: (-1.0 if s == "food_distance" else 1.0) for s in SENSORS}
    sensor_assign = {s: [] for s in SENSORS}
    for i, t in enumerate(inputs):  # round-robin inputs onto the 5 sensors
        sensor = SENSORS[i % len(SENSORS)]
        sensor_assign[sensor].append((t, gains[sensor]))
    sensor_assign = {k: v for k, v in sensor_assign.items() if v}
    for action, entries in motor_map.items():
        dropped = [t for t, _ in entries if t not in found]
        if dropped:
            print(f"Warning: {action} loses {', '.join(dropped)} (not found); fix --outputs/--motor-map", file=sys.stderr)
    motor_map = {a: [(t, g) for t, g in entries if t in found] for a, entries in motor_map.items()}
    empty = [a for a, entries in motor_map.items() if not entries]
    if empty:
        return _fail(4, f"No motor neurons left for: {', '.join(empty)}")

    meta = {
        "source": "Janelia FlyEM male CNS connectome via neuPrint",
        "dataset": args.dataset,
        "server": args.server,
        "citation": "Janelia FlyEM male CNS connectome (https://male-cns.janelia.org); Cell (2026) S0092-8674(26)00942-6",
        "license": "See dataset terms at https://male-cns.janelia.org/download/ (verify before redistribution)",
        "attribution": "Data: Janelia FlyEM / neuPrint.",
        "generated_by": "scripts/extract_connectome.py",
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
    }
    conn = build_connectome(types, roles, edges, nts, n_neurons, sensor_assign, motor_map, meta, neuropils)

    # Validate before writing
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(conn, fh)
        tmp = Path(fh.name)
    try:
        load_connectome(tmp)
    except ValueError as e:
        tmp.unlink()
        return _fail(4, str(e))
    tmp.unlink()
    unreachable = unreachable_outputs(conn, MAX_HOPS)
    print(f"{len(conn['nodes'])} nodes, {len(conn['edges'])} edges; unreachable motors: {unreachable or 'none'}")
    for name in unreachable:  # show what feeds each stranded motor neuron, to guide --outputs choices
        feeders = sorted({a for (a, b) in edges if b == name and a in roles}, key=lambda a: -edges[(a, name)])
        print(f"  {name} inputs in circuit: {', '.join(f'{a}({roles[a]})' for a in feeders) or 'none'}", file=sys.stderr)
    if unreachable and not args.force:
        return _fail(4, "Some motor nodes are unreachable within 3 hops; use --force or change --outputs")
    if args.dry_run:
        return 0

    out_tmp = args.out.with_suffix(args.out.suffix + ".tmp")
    out_tmp.write_text(json.dumps(conn, indent=1), encoding="utf-8")
    os.replace(out_tmp, args.out)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
