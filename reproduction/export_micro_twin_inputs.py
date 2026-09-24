"""Author-only recovery of the fixed Figure 4 diagnostic illustration.

This command is deliberately separate from the reviewer workflow. It performs
one fixed benign VAR fit to recover the plotted values from the existing
semantic cache. It does not fit the selected v3 monitor, search candidates,
collect data, or read confirmation/reserved arrays. Reviewer figure generation
uses the resulting CSV/JSON and never invokes this command.

Only the hash-pinned, explicitly named numerical definitions and the numerical
prefix of the illustration function are extracted from the canonical notebook.
The notebook, its cells, and its collection code are never executed wholesale.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PINNED_CACHE_SHA256 = "230725c240b2ebec0b4dcaa4ff199ff52585e4d4b8ed72030bc445896ba6777a"
PINNED_NUMERICAL_CODE_SHA256 = (
    "e137217e6d390ea4a964c80d147086eb4390be25c0b4bda7b73e089879cc5257"
)
DEMO_RUN_ID = "m2_macos__py_stats__membw__r01"
EXPECTED_FIT_RUN_IDS = {
    "m2_macos__py_stats__development_benign_supplement__f0",
    "m2_macos__py_stats__development_benign_supplement__f1",
    "m2_macos__py_stats__long_benign__s01",
    "m2_macos__py_stats__nominal__r01",
    "m2_macos__py_stats__nominal__r02",
}
CONSTANTS_BY_CELL = {
    66: {"BASE_FEATURES", "BLOCK_FEATURES"},
    74: {"COMPACT_STATE_NAMES"},
}
FUNCTIONS_BY_CELL = {
    68: {
        "robust_location_scale",
        "normalize_sequence",
        "lagged_design",
        "residual_matrix",
    },
    74: {
        "_feature_columns",
        "_row_median",
        "compact_semantic_sequence",
        "fit_compact_var",
        "compact_benign_segment",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _assigned(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Assign) and any(
        isinstance(target, ast.Name) and target.id == name for target in node.targets
    )


def _numerical_namespace(notebook_path: Path) -> tuple[dict[str, Any], dict]:
    notebook_bytes = notebook_path.read_bytes()
    notebook = json.loads(notebook_bytes)
    definitions = []
    definition_sources = []
    for cell_index in (66, 68, 74):
        cell_source = "".join(notebook["cells"][cell_index]["source"])
        tree = ast.parse(cell_source)
        seen_functions = set()
        seen_constants = set()
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS_BY_CELL.get(
                cell_index, set()
            ):
                definitions.append(node)
                definition_sources.append(ast.get_source_segment(cell_source, node))
                seen_functions.add(node.name)
            elif isinstance(node, ast.Assign):
                names = {
                    target.id for target in node.targets if isinstance(target, ast.Name)
                }
                selected = names & CONSTANTS_BY_CELL.get(cell_index, set())
                if selected:
                    definitions.append(node)
                    definition_sources.append(ast.get_source_segment(cell_source, node))
                    seen_constants.update(selected)
        if seen_functions != FUNCTIONS_BY_CELL.get(cell_index, set()):
            raise ValueError(
                f"Numerical function whitelist differs in cell {cell_index}."
            )
        if seen_constants != CONSTANTS_BY_CELL.get(cell_index, set()):
            raise ValueError(
                f"Numerical constant whitelist differs in cell {cell_index}."
            )

    illustration_source = "".join(notebook["cells"][132]["source"])
    illustration_tree = ast.parse(illustration_source)
    illustration = next(
        node
        for node in illustration_tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "generate_digital_micro_twin_figure"
    )
    start = next(
        index
        for index, node in enumerate(illustration.body)
        if _assigned(node, "TWIN_FIGURE_CONFIG")
    )
    end = next(
        index
        for index, node in enumerate(illustration.body)
        if _assigned(node, "BLACK")
    )
    numerical_prefix = illustration.body[start:end]
    canonical = json.dumps(
        {
            "definitions": definition_sources,
            "illustration": [
                ast.get_source_segment(illustration_source, node)
                for node in numerical_prefix
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    code_hash = sha256(canonical.encode("utf-8"))
    if code_hash != PINNED_NUMERICAL_CODE_SHA256:
        raise ValueError(
            "Numerical source differs from the pinned canonical illustration; "
            "refusing to execute the supplied notebook definitions."
        )

    # This local wrapper returns only the arrays used by the original plot.
    wrapper = ast.parse("def reconstruct(SEMANTIC_CACHE):\n    pass").body[0]
    wrapper.body = (
        numerical_prefix
        + ast.parse(
            "return dict(config=TWIN_FIGURE_CONFIG, model=micro_twin, "
            "fit_sequences=fit_sequences, time_seconds=time_seconds, onset=onset, "
            "observed=observed_normalized, expected=expected_normalized, "
            "standardized_residual=standardized_residual, "
            "aggregate_evidence=aggregate_evidence, "
            "diagnostic_threshold=diagnostic_threshold, state_lookup=state_lookup)"
        ).body
    )
    module = ast.fix_missing_locations(
        ast.Module(body=definitions + [wrapper], type_ignores=[])
    )
    namespace = {"np": np, "Iterable": Iterable, "Any": Any}
    exec(compile(module, "<pinned-micro-twin-numerics>", "exec"), namespace)
    return namespace, {
        "source_notebook_name": notebook_path.name,
        "source_notebook_sha256": sha256(notebook_bytes),
        "source_code_ast_selected_sha256": code_hash,
        "source_code_hash_algorithm": "SHA-256 of canonical JSON containing exact AST-selected source segments.",
        "canonical_source_commit": "6289c4d",
        "definition_cell_indices": [66, 68, 74],
        "illustration_cell_index": 132,
        "source_execution": "Whitelisted numerical definitions and illustration prefix only.",
    }


def _load_allowed_runs(cache_path: Path) -> tuple[dict[str, Any], list[str], dict]:
    cache_hash = sha256(cache_path.read_bytes())
    if cache_hash != PINNED_CACHE_SHA256:
        raise ValueError("Semantic cache differs from the pinned source cache.")
    array_records = []
    with np.load(cache_path, allow_pickle=False) as archive:
        metadata_text = str(archive["metadata"].item())
        metadata = json.loads(metadata_text)
        demo_record = metadata["runs"].get(DEMO_RUN_ID)
        if not demo_record or (
            demo_record["platform_id"],
            demo_record["workload"],
            demo_record["scenario"],
            demo_record["planned_split"],
        ) != ("M2_MACOS", "PY_STATS", "MEMBW", "development"):
            raise ValueError("The fixed illustrated development run is unavailable.")
        # Preserve the cache's ordering, exactly as the notebook comprehension.
        fitting_ids = [
            run_id
            for run_id, record in metadata["runs"].items()
            if record["platform_id"] == "M2_MACOS"
            and record["workload"] == "PY_STATS"
            and record["scenario"] == "NOMINAL"
            and record["planned_split"] in {"calibration", "development"}
        ]
        if set(fitting_ids) != EXPECTED_FIT_RUN_IDS or len(fitting_ids) != 5:
            raise ValueError("The fixed five-run benign fitting set differs.")
        wanted_ids = set(fitting_ids) | {DEMO_RUN_ID}
        runs = {}
        for run_id, record in metadata["runs"].items():
            if run_id not in wanted_ids:
                continue
            if record["planned_split"] not in {"calibration", "development"}:
                raise ValueError("Only calibration/development arrays may be read.")
            arrays = {}
            for suffix in ("x", "t", "fault"):
                array = np.asarray(archive[f"{run_id}__{suffix}"])
                arrays[suffix] = array
                array_records.append(
                    {
                        "run_id": run_id,
                        "array": suffix,
                        "shape": list(array.shape),
                        "dtype": array.dtype.str,
                        "sha256_c_order_bytes": sha256(
                            np.ascontiguousarray(array).tobytes()
                        ),
                    }
                )
            runs[run_id] = {**record, **arrays}
    return (
        {"metadata": metadata, "runs": runs},
        fitting_ids,
        {
            "semantic_cache_name": cache_path.name,
            "semantic_cache_sha256": cache_hash,
            "cache_metadata_sha256": sha256(metadata_text.encode("utf-8")),
            "dataset_fingerprint": metadata["dataset_fingerprint"],
            "analysis_revision": metadata["analysis_revision"],
            "block_seconds": metadata["block_seconds"],
            "opened_run_arrays": array_records,
            "opened_run_count": len(runs),
            "confirmation_arrays_read": 0,
            "reserved_arrays_read": 0,
        },
    )


def _json_model(model: dict) -> dict:
    return {
        key: value.tolist() if isinstance(value, np.ndarray) else value
        for key, value in model.items()
    }


def export_inputs(notebook_path: Path, cache_path: Path, output_dir: Path) -> dict:
    namespace, source_provenance = _numerical_namespace(notebook_path)
    cache, fitting_ids, cache_provenance = _load_allowed_runs(cache_path)
    if list(namespace["BLOCK_FEATURES"]) != cache["metadata"]["block_features"]:
        raise ValueError(
            "Cache diagnostic columns differ from the pinned feature definitions."
        )
    reconstructed = namespace["reconstruct"](cache)
    state_lookup = reconstructed["state_lookup"]
    state_index = state_lookup["compute_activity"]
    columns = {
        "time_seconds": reconstructed["time_seconds"],
        "observed_compute_activity": reconstructed["observed"][:, state_index],
        "expected_compute_activity": reconstructed["expected"][:, state_index],
    }
    for state in ("compute_activity", "memory_pressure", "io_variability"):
        values = np.abs(reconstructed["standardized_residual"][:, state_lookup[state]])
        columns[f"residual_{state}"] = (
            pd.Series(values).rolling(3, center=True, min_periods=1).median().to_numpy()
        )
    columns["aggregate_evidence"] = reconstructed["aggregate_evidence"]
    trace = pd.DataFrame(columns)
    csv_bytes = trace.to_csv(index=False, float_format="%.17g").encode("utf-8")
    metadata = {
        "schema_version": 1,
        "figure_number": 4,
        "run_id": DEMO_RUN_ID,
        "state": "compute_activity",
        "onset_seconds": float(reconstructed["onset"]),
        "diagnostic_threshold": float(reconstructed["diagnostic_threshold"]),
        "diagnostic_reference_quantile": 0.99,
        "diagnostic_reference_role": "Descriptive benign reference; not the v3 alert threshold.",
        "scope": (
            "Numerical reconstruction of the existing fixed development illustration. "
            "One benign diagnostic compact VAR fit, lags=1 and ridge penalty=100; "
            "not selected-v3 training, a candidate search, or a performance evaluation. "
            "This export does not assert byte identity with the manuscript PNG."
        ),
        "config": reconstructed["config"],
        "fitting_run_ids_in_original_order": fitting_ids,
        "fitting_runs": [
            {
                key: cache["runs"][run_id][key]
                for key in (
                    "run_id",
                    "platform_id",
                    "workload",
                    "scenario",
                    "planned_split",
                )
            }
            for run_id in fitting_ids
        ],
        "fitting_benign_blocks": [
            len(sequence) for sequence in reconstructed["fit_sequences"]
        ],
        "plotted_blocks": len(trace),
        "plotted_columns": list(trace.columns),
        "localized_residual_transform": {
            "input": "absolute standardized residual",
            "rolling_window_blocks": 3,
            "center": True,
            "min_periods": 1,
            "aggregation": "median",
        },
        "missing_values": "Empty CSV fields preserve undefined leading-lag residual/expected values.",
        "trace_csv_sha256": sha256(csv_bytes),
        "normalized_diagnostic_model": _json_model(reconstructed["model"]),
        "provenance": {
            **source_provenance,
            **cache_provenance,
            "exporter_sha256": sha256(Path(__file__).read_bytes()),
            "versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "pandas": pd.__version__,
            },
        },
    }
    json_bytes = (
        json.dumps(metadata, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        output_dir / "figure-4-micro-twin.csv": csv_bytes,
        output_dir / "figure-4-micro-twin.json": json_bytes,
    }
    for path, content in outputs.items():
        if path.exists() and path.read_bytes() != content:
            raise FileExistsError(
                f"Refusing to replace a different existing export: {path}"
            )
    for path, content in outputs.items():
        if not path.exists():
            path.write_bytes(content)
    return {
        "run_id": DEMO_RUN_ID,
        "plotted_blocks": len(trace),
        "fitting_run_count": len(fitting_ids),
        "diagnostic_threshold": metadata["diagnostic_threshold"],
        "trace_csv_sha256": metadata["trace_csv_sha256"],
        "outputs": [str(path) for path in outputs],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--notebook", required=True, type=Path, help="Canonical source notebook."
    )
    parser.add_argument(
        "--cache", required=True, type=Path, help="Pinned author semantic-block cache."
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Directory for the two exported figure inputs.",
    )
    args = parser.parse_args()
    print(json.dumps(export_inputs(args.notebook, args.cache, args.output), indent=2))


if __name__ == "__main__":
    main()
