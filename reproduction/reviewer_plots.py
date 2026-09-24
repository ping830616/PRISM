"""Regenerate the four data figures in the current PRISM manuscript.

The plotting routines are adapted from Section 17D of
notebooks/PRISM_Complete_Experiment.ipynb at commit 6289c4d.  Only rendering
code is included here: there is no notebook execution, collection, cache
access, model fitting, candidate search, or locked-data access.

Figures 1–3 are conceptual manuscript diagrams and are not generated here.
The micro-twin illustration requires its exported plotting values; an
existing PNG is never substituted for numerical regeneration.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


_CANDIDATE_FILES = {
    "Static VAR": (
        "development-method-selection.json",
        "development-method-selection.csv",
    ),
    "Guarded adaptive VAR": (
        "development-guarded-method-selection.json",
        "development-guarded-method-selection.csv",
    ),
    "Robust residual fusion": (
        "development-robust-normalization-selection.json",
        "development-robust-normalization-candidates.csv",
    ),
}
_TRACE_COLUMNS = (
    "time_seconds",
    "observed_compute_activity",
    "expected_compute_activity",
    "residual_compute_activity",
    "residual_memory_pressure",
    "residual_io_variability",
    "aggregate_evidence",
)


def _require_files(paths):
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing numerical figure inputs:\n"
            + "\n".join(missing)
            + "\nThe micro-twin figure requires its exported plotted values; "
            "a bundled image cannot replace those inputs."
        )


def _input_record(path, repo_root):
    try:
        name = str(path.relative_to(repo_root))
    except ValueError:
        name = str(path)
    return {
        "path": name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _validate_trace(trace, metadata):
    missing = set(_TRACE_COLUMNS) - set(trace.columns)
    if missing:
        raise ValueError(f"Micro-twin trace lacks columns: {sorted(missing)}")
    if len(trace) < 2:
        raise ValueError("Micro-twin trace must contain at least two plotted times.")
    for column in _TRACE_COLUMNS:
        values = pd.to_numeric(trace[column], errors="raise").to_numpy(dtype=float)
        if np.isinf(values).any():
            raise ValueError(f"Micro-twin trace contains infinity in {column}.")
        if not np.isfinite(values).any():
            raise ValueError(f"Micro-twin trace has no finite values in {column}.")
    times = trace["time_seconds"].to_numpy(dtype=float)
    if not np.isfinite(times).all() or np.any(np.diff(times) <= 0):
        raise ValueError("Micro-twin times must be finite and strictly increasing.")
    for key in ("onset_seconds", "diagnostic_threshold"):
        if not np.isfinite(float(metadata[key])):
            raise ValueError(f"Micro-twin metadata {key} must be finite.")
    if not times[0] <= float(metadata["onset_seconds"]) <= times[-1]:
        raise ValueError("Micro-twin event onset is outside the plotted time range.")
    if metadata.get("run_id") != "m2_macos__py_stats__membw__r01":
        raise ValueError("Micro-twin data does not identify the fixed manuscript run.")
    if metadata.get("state", "compute_activity") != "compute_activity":
        raise ValueError("Micro-twin metadata does not identify compute_activity.")


def render_figures(
    repo_root: Path,
    output_dir: Path,
    inputs_dir: Path | None = None,
) -> list[dict]:
    """Render manuscript Figures 4–7 as PNG and PDF from saved numerical inputs.

    `inputs_dir` contains figure-4-micro-twin.csv and its matching JSON metadata
    (default: repo_root/reproduction/inputs).  The CSV holds the actual plotted
    curves; residual_* columns already include the notebook's absolute-value
    and centered three-block median transformation.  Other figures read the
    committed reports and CSVs in paper/results/development.

    All required files are checked before output is created.  Missing inputs
    raise FileNotFoundError rather than silently copying archived graphics.
    The returned records identify the input hashes, output files, and evidence
    role of each figure.  Callers should put output_dir outside source folders.
    """
    repo_root = Path(repo_root).resolve()
    output_dir = Path(output_dir).resolve()
    inputs_dir = (
        Path(inputs_dir).resolve()
        if inputs_dir is not None
        else repo_root / "reproduction" / "inputs"
    )
    data_dir = repo_root / "paper" / "results" / "development"
    trace_csv = inputs_dir / "figure-4-micro-twin.csv"
    trace_json = inputs_dir / "figure-4-micro-twin.json"
    audit_path = data_dir / "table-5-guarded-update-audit.csv"
    operational_path = data_dir / "table-9-operational-evidence-scorecard.csv"
    scenario_path = data_dir / "table-10-scenario-detection-coverage.csv"
    run_scores_path = data_dir / "supporting-dice-comparable-complete-run-scores.csv"
    candidate_paths = [
        data_dir / name for pair in _CANDIDATE_FILES.values() for name in pair
    ]
    _require_files(
        [
            trace_csv,
            trace_json,
            audit_path,
            operational_path,
            scenario_path,
            run_scores_path,
            *candidate_paths,
        ]
    )

    trace = pd.read_csv(trace_csv, float_precision="round_trip")
    trace_metadata = json.loads(trace_json.read_text(encoding="utf-8"))
    _validate_trace(trace, trace_metadata)
    reports = {}
    candidates = {}
    for label, (report_name, candidate_name) in _CANDIDATE_FILES.items():
        reports[label] = json.loads(
            (data_dir / report_name).read_text(encoding="utf-8")
        )
        candidates[label] = pd.read_csv(data_dir / candidate_name)
        if candidates[label].empty:
            raise ValueError(f"No saved candidates for {label}.")
    fingerprints = {report["dataset_fingerprint"] for report in reports.values()}
    if len(fingerprints) != 1:
        raise ValueError(
            "Initial-development figure reports have different dataset fingerprints."
        )

    audit = pd.read_csv(audit_path)
    actual_audit = audit.set_index("Audit event")["Count"].astype(int).to_dict()
    expected_audit = {
        key.replace("_", " "): int(value)
        for key, value in reports["Guarded adaptive VAR"][
            "guarded_update_audit_totals"
        ].items()
    }
    if actual_audit != expected_audit:
        raise ValueError("Guarded audit table differs from the saved guarded report.")

    operational = pd.read_csv(operational_path).set_index("Metric")
    scenario = pd.read_csv(scenario_path)
    run_scores = pd.read_csv(run_scores_path)
    if not np.allclose(
        scenario["Coverage %"].to_numpy(dtype=float),
        100.0
        * scenario["Detected"].to_numpy(dtype=float)
        / scenario["Runs"].to_numpy(dtype=float),
    ):
        raise ValueError(
            "Scenario coverage percentages differ from the saved run counts."
        )

    specifications = [
        {
            "figure_number": 4,
            "stem": "figure-4-micro-twin",
            "title": "Representative behavioral micro-twin residual construction",
            "evidence_role": "Fixed development illustration; descriptive benign reference, not the v3 decision threshold.",
            "inputs": [trace_csv, trace_json],
            "render": lambda: _plot_micro_twin(trace, trace_metadata),
            "data_summary": {
                "run_id": trace_metadata["run_id"],
                "plotted_blocks": len(trace),
            },
        },
        {
            "figure_number": 5,
            "stem": "figure-5-development-operating-points",
            "title": "Initial development candidate families",
            "evidence_role": "Initial development search; method exposures differ; separate from the selected v3 result.",
            "inputs": candidate_paths,
            "render": lambda: _plot_operating_points(candidates),
            "data_summary": {
                "dataset_fingerprint": next(iter(fingerprints)),
                "candidate_counts": {
                    label: len(frame) for label, frame in candidates.items()
                },
            },
        },
        {
            "figure_number": 6,
            "stem": "figure-6-guarded-update-audit",
            "title": "Development audit of guarded adaptive VAR actions",
            "evidence_role": "Earlier guarded VAR controller audit; not selected v3 residual-offset adaptation.",
            "inputs": [
                audit_path,
                data_dir / _CANDIDATE_FILES["Guarded adaptive VAR"][0],
            ],
            "render": lambda: _plot_guarded_audit(audit),
            "data_summary": actual_audit,
        },
        {
            "figure_number": 7,
            "stem": "figure-7-operational-reliability",
            "title": "PRISM operational evidence",
            "evidence_role": "Development scenario/delay evidence, independent benign confirmation, and replay accounting.",
            "inputs": [operational_path, scenario_path, run_scores_path],
            "render": lambda: _plot_operational_reliability(
                operational, scenario, run_scores
            ),
            "data_summary": {
                "scenario_count": len(scenario),
                "saved_run_count": len(run_scores),
                "development_fah": float(
                    operational.loc["FAH (development)", "Pooled"]
                ),
                "confirmation_fah": float(
                    operational.loc["FAH (confirmation)", "Pooled"]
                ),
            },
        },
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    result = []
    with plt.rc_context(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "figure.dpi": 100,
            "savefig.dpi": 300,
            "text.usetex": False,
        }
    ):
        for specification in specifications:
            figure = specification["render"]()
            png_path = output_dir / (specification["stem"] + ".png")
            pdf_path = png_path.with_suffix(".pdf")
            try:
                figure.savefig(
                    png_path, dpi=300, bbox_inches="tight", facecolor="white"
                )
                figure.savefig(
                    pdf_path,
                    bbox_inches="tight",
                    facecolor="white",
                    metadata={"CreationDate": None, "ModDate": None},
                )
            finally:
                plt.close(figure)
            result.append(
                {
                    key: value
                    for key, value in specification.items()
                    if key not in {"render", "inputs"}
                }
                | {
                    "status": "regenerated",
                    "inputs": [
                        _input_record(path, repo_root)
                        for path in specification["inputs"]
                    ],
                    "outputs": [str(png_path), str(pdf_path)],
                }
            )
    return result


def _plot_micro_twin(trace, metadata):
    """Rendering code adapted from canonical notebook Section 17D."""
    time_seconds = trace["time_seconds"].to_numpy(dtype=float)
    onset = float(metadata["onset_seconds"])
    diagnostic_threshold = float(metadata["diagnostic_threshold"])
    aggregate_evidence = trace["aggregate_evidence"].to_numpy(dtype=float)
    contributor_specs = (
        ("compute_activity", "Compute activity", "#0072B2", "-"),
        ("memory_pressure", "Memory pressure", "#009E73", "--"),
        ("io_variability", "I/O variability", "#E69F00", "-."),
    )
    BLACK = "#000000"
    GRID = "#D5D9DE"
    figure, axes = plt.subplots(
        3,
        1,
        figsize=(7.2, 11.0),
        sharex=True,
        gridspec_kw={"height_ratios": [1.1, 1.0, 1.0]},
    )
    figure.patch.set_facecolor("white")
    axes[0].plot(
        time_seconds,
        trace["observed_compute_activity"].to_numpy(dtype=float),
        color="#0072B2",
        linewidth=2.6,
        label="Observed",
    )
    axes[0].plot(
        time_seconds,
        trace["expected_compute_activity"].to_numpy(dtype=float),
        color="#D55E00",
        linewidth=2.6,
        linestyle="--",
        label="Micro-twin expected",
    )
    axes[0].axvline(
        onset, color=BLACK, linestyle=":", linewidth=2.0, label="Event onset"
    )
    axes[0].set_ylabel(
        "Normalized state", fontsize=14.5, fontweight="bold", color=BLACK
    )
    axes[0].set_title(
        "(a) Observed and expected state",
        loc="left",
        fontsize=17,
        fontweight="bold",
        color=BLACK,
        pad=9,
    )
    axes[0].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.29),
        ncol=3,
        frameon=False,
        fontsize=11.7,
        borderaxespad=0.0,
        handlelength=2.8,
        columnspacing=1.25,
        handletextpad=0.6,
    )
    for state_name, display_name, color, linestyle in contributor_specs:
        smoothed = trace["residual_" + state_name].to_numpy(dtype=float)
        axes[1].plot(
            time_seconds,
            smoothed,
            color=color,
            linewidth=2.4,
            linestyle=linestyle,
            label=display_name,
        )
    axes[1].set_ylabel(
        "Residual magnitude", fontsize=14.5, fontweight="bold", color=BLACK
    )
    axes[1].set_title(
        "(b) Localized residual evidence",
        loc="left",
        fontsize=17,
        fontweight="bold",
        color=BLACK,
        pad=9,
    )
    axes[1].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.29),
        ncol=3,
        frameon=False,
        fontsize=11.5,
        borderaxespad=0.0,
        handlelength=2.8,
        columnspacing=1.15,
        handletextpad=0.6,
    )
    axes[2].plot(
        time_seconds,
        aggregate_evidence,
        color="#7B2CBF",
        linewidth=2.6,
        label="Aggregate evidence",
    )
    axes[2].axhline(
        diagnostic_threshold,
        color="#C62828",
        linestyle="--",
        linewidth=2.3,
        label="99th-percentile benign reference",
    )
    axes[2].fill_between(
        time_seconds,
        diagnostic_threshold,
        aggregate_evidence,
        where=aggregate_evidence >= diagnostic_threshold,
        color="#C62828",
        alpha=0.16,
    )
    axes[2].set_ylabel(
        "Residual evidence", fontsize=14.5, fontweight="bold", color=BLACK
    )
    axes[2].set_title(
        "(c) Aggregated residual evidence",
        loc="left",
        fontsize=17,
        fontweight="bold",
        color=BLACK,
        pad=9,
    )
    axes[2].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.31),
        ncol=2,
        frameon=False,
        fontsize=11.5,
        borderaxespad=0.0,
        handlelength=2.8,
        columnspacing=1.25,
        handletextpad=0.6,
    )
    for axis in axes[1:]:
        axis.axvline(
            onset, color=BLACK, linestyle=":", linewidth=2.0, label="_nolegend_"
        )
    for axis in axes:
        axis.set_facecolor("white")
        axis.grid(axis="y", color=GRID, linewidth=0.9, alpha=0.85)
        axis.set_xlabel(
            "Run time (s)", fontsize=14.5, fontweight="bold", color=BLACK, labelpad=7
        )
        axis.yaxis.set_label_coords(-0.15, 0.5)
        axis.tick_params(
            axis="both",
            labelsize=12.5,
            colors=BLACK,
            width=1.1,
            length=4,
            labelbottom=True,
        )
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color(BLACK)
        axis.spines["bottom"].set_color(BLACK)
        axis.spines["left"].set_linewidth(1.1)
        axis.spines["bottom"].set_linewidth(1.1)
    axes[2].set_xlim(float(time_seconds.min()), float(time_seconds.max()))
    figure.subplots_adjust(left=0.22, right=0.97, bottom=0.09, top=0.97, hspace=1.05)
    return figure


def _plot_operating_points(PAPER_CANDIDATES):
    """Rendering code adapted from canonical notebook Section 17D."""
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.gridspec import GridSpec
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import FuncFormatter

    OPERATING_POINT_FONTS = {
        "figure_title": 28,
        "panel_title": 24,
        "axis_label": 22,
        "tick_number": 18,
    }
    G3_FALSE_ALERT_BUDGET = 0.25
    G3_DETECTION_REQUIREMENT = 50.0
    colors = {
        "Static VAR": "#0072B2",
        "Guarded adaptive VAR": "#D55E00",
        "Robust residual fusion": "#009E73",
        "Shared quantile fusion": "#7B2CBF",
    }
    light_colors = {
        "Static VAR": "#DCEEF8",
        "Guarded adaptive VAR": "#FBE5D2",
        "Robust residual fusion": "#D9F2EA",
        "Shared quantile fusion": "#EADDF6",
    }
    method_count = len(PAPER_CANDIDATES)
    figure = plt.figure(figsize=(12.0, 4.2 * method_count + 1.0), facecolor="white")
    grid = GridSpec(method_count, 12, figure=figure, hspace=0.95, wspace=1.8)
    for row_index, (label, candidates) in enumerate(PAPER_CANDIDATES.items()):
        if {"fah", "detection"}.issubset(candidates.columns):
            false_alert_rate = pd.to_numeric(
                candidates["fah"], errors="coerce"
            ).to_numpy(dtype=float)
            detection_rate = 100.0 * pd.to_numeric(
                candidates["detection"], errors="coerce"
            ).to_numpy(dtype=float)
        else:
            false_alert_rate = pd.to_numeric(
                candidates["false_alerts_per_hour"], errors="coerce"
            ).to_numpy(dtype=float)
            detection_rate = 100.0 * pd.to_numeric(
                candidates["anomaly_run_detection_rate"], errors="coerce"
            ).to_numpy(dtype=float)
        finite = np.isfinite(false_alert_rate) & np.isfinite(detection_rate)
        false_alert_rate = false_alert_rate[finite]
        detection_rate = detection_rate[finite]
        budget_multiple = false_alert_rate / G3_FALSE_ALERT_BUDGET
        positive_multiple = budget_multiple[budget_multiple > 0]
        if len(positive_multiple):
            plot_floor = min(0.2, max(0.02, positive_multiple.min() * 0.6))
        else:
            plot_floor = 0.2
        plotted_multiple = np.where(budget_multiple > 0, budget_multiple, plot_floor)
        zero_alert = budget_multiple <= 0
        if (
            label in {"Static VAR", "Guarded adaptive VAR"}
            and zero_alert.any()
            and len(positive_multiple)
        ):
            overview_axis = figure.add_subplot(grid[row_index, :4])
            focus_axis = figure.add_subplot(grid[row_index, 4:])
            overview_axis.set_facecolor("white")
            focus_axis.set_facecolor("white")
            method_color = colors[label]
            overview_x_min, overview_x_max = (-0.08, 1.12)
            overview_y_min, overview_y_max = (0.0, 102.0)
            overview_axis.axvspan(
                0.0,
                1.0,
                ymin=G3_DETECTION_REQUIREMENT / overview_y_max,
                ymax=1.0,
                color="#2E7D32",
                alpha=0.12,
                zorder=0,
            )
            overview_axis.scatter(
                [0.0],
                [float(np.median(detection_rate[zero_alert]))],
                marker="o",
                s=155 + 18 * zero_alert.sum(),
                facecolor=method_color,
                edgecolor=method_color,
                linewidth=2.2,
                zorder=5,
            )
            overview_axis.axvline(1.0, color="#C62828", linestyle="--", linewidth=2.0)
            overview_axis.axhline(
                G3_DETECTION_REQUIREMENT, color="#2E7D32", linestyle="--", linewidth=2.0
            )
            overview_axis.annotate(
                f"{zero_alert.sum()} candidates\n0 FAH / 0% detected",
                xy=(0.0, float(np.median(detection_rate[zero_alert]))),
                xytext=(0.12, 18.0),
                fontsize=13.5,
                fontweight="bold",
                color="#000000",
                arrowprops={"color": "#000000", "linewidth": 1.2},
            )
            overview_axis.set_xlim(overview_x_min, overview_x_max)
            overview_axis.set_ylim(overview_y_min, overview_y_max)
            overview_axis.set_xticks([0.0, 1.0])
            overview_axis.set_xticklabels(["0×", "1×"])
            display_label = "Guarded VAR" if label == "Guarded adaptive VAR" else label
            overview_axis.set_title(
                f"{display_label}\n{len(candidates)} candidates",
                loc="left",
                fontsize=OPERATING_POINT_FONTS["panel_title"],
                fontweight="bold",
                color="#000000",
                pad=10,
            )
            overview_axis.set_xlabel(
                "G3 operating window",
                fontsize=OPERATING_POINT_FONTS["axis_label"],
                color="#000000",
            )
            overview_axis.set_ylabel(
                "Detection (%)",
                fontsize=OPERATING_POINT_FONTS["axis_label"],
                color="#000000",
            )
            positive = budget_multiple > 0
            focus_x = budget_multiple[positive]
            focus_y = detection_rate[positive]
            focus_axis.scatter(
                focus_x,
                focus_y,
                s=62,
                alpha=0.84,
                color=method_color,
                edgecolor="white",
                linewidth=0.65,
                zorder=3,
            )
            frontier_order = np.argsort(focus_x, kind="mergesort")
            frontier_x = focus_x[frontier_order]
            frontier_y = focus_y[frontier_order]
            running_best = np.maximum.accumulate(frontier_y)
            frontier_change = np.r_[True, running_best[1:] > running_best[:-1] + 1e-09]
            focus_axis.step(
                frontier_x[frontier_change],
                running_best[frontier_change],
                where="post",
                color="#000000",
                linewidth=2.4,
                zorder=4,
            )
            focus_padding = max(8.0, 0.045 * (focus_x.max() - focus_x.min()))
            focus_axis.set_xlim(
                max(0.0, focus_x.min() - focus_padding), focus_x.max() + focus_padding
            )
            focus_axis.set_ylim(
                max(0.0, focus_y.min() - 3.0), min(102.0, focus_y.max() + 2.0)
            )
            focus_axis.xaxis.set_major_formatter(
                FuncFormatter(lambda value, _: f"{value:g}×")
            )
            if label == "Guarded adaptive VAR":
                focus_axis.set_xticks([20.0, 40.0, 60.0, 80.0, 100.0])
            focus_axis.set_title(
                f"Positive FAH\n{positive.sum()} candidates",
                loc="left",
                fontsize=OPERATING_POINT_FONTS["panel_title"],
                fontweight="bold",
                color="#000000",
                pad=10,
            )
            focus_axis.set_xlabel(
                "FAH relative to the 0.25 limit",
                fontsize=OPERATING_POINT_FONTS["axis_label"],
                color="#000000",
            )
            focus_axis.set_ylabel("")
            for split_axis in (overview_axis, focus_axis):
                split_axis.tick_params(
                    axis="both",
                    labelsize=OPERATING_POINT_FONTS["tick_number"],
                    colors="#000000",
                )
                split_axis.grid(axis="y", color="#D5D9DE", linewidth=0.8, alpha=0.7)
                split_axis.grid(axis="x", color="#E3E6E9", linewidth=0.7, alpha=0.55)
                split_axis.spines["top"].set_visible(False)
                split_axis.spines["right"].set_visible(False)
            continue
        axis = figure.add_subplot(grid[row_index, :])
        axis.set_facecolor("white")
        x_min = max(0.01, plot_floor * 0.75)
        x_max = max(2.0, np.nanmax(plotted_multiple) * 1.25)
        y_min = max(0.0, np.nanmin(detection_rate) - 6.0)
        y_max = min(102.0, max(58.0, np.nanmax(detection_rate) + 5.0))
        feasible_fraction_start = np.clip(
            (G3_DETECTION_REQUIREMENT - y_min) / (y_max - y_min), 0.0, 1.0
        )
        axis.axvspan(
            x_min,
            1.0,
            ymin=feasible_fraction_start,
            ymax=1.0,
            color="#2E7D32",
            alpha=0.12,
            zorder=0,
        )
        method_color = colors.get(label, "#0072B2")
        if len(candidates) >= 300:
            density_map = LinearSegmentedColormap.from_list(
                f"{label}-density", [light_colors.get(label, "#DCEEF8"), method_color]
            )
            axis.hexbin(
                plotted_multiple,
                detection_rate,
                xscale="log",
                gridsize=(58, 16),
                mincnt=1,
                bins="log",
                cmap=density_map,
                linewidths=0.25,
                edgecolors="white",
                alpha=0.92,
                zorder=2,
            )
        else:
            axis.scatter(
                plotted_multiple,
                detection_rate,
                s=48,
                alpha=0.8,
                color=method_color,
                edgecolor="white",
                linewidth=0.55,
                zorder=3,
            )
        if zero_alert.any():
            axis.scatter(
                np.full(zero_alert.sum(), plot_floor),
                detection_rate[zero_alert],
                marker="<",
                s=72,
                facecolor="white",
                edgecolor=method_color,
                linewidth=1.8,
                zorder=5,
            )
        frontier_order = np.argsort(plotted_multiple, kind="mergesort")
        frontier_x = plotted_multiple[frontier_order]
        frontier_y = detection_rate[frontier_order]
        running_best = np.maximum.accumulate(frontier_y)
        frontier_change = np.r_[True, running_best[1:] > running_best[:-1] + 1e-09]
        axis.step(
            frontier_x[frontier_change],
            running_best[frontier_change],
            where="post",
            color="#000000",
            linewidth=2.2,
            zorder=4,
        )
        axis.axvline(1.0, color="#C62828", linestyle="--", linewidth=1.8, zorder=1)
        axis.axhline(
            G3_DETECTION_REQUIREMENT,
            color="#2E7D32",
            linestyle="--",
            linewidth=1.8,
            zorder=1,
        )
        axis.set_xscale("log")
        axis.set_xlim(x_min, x_max)
        axis.set_ylim(y_min, y_max)
        axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}×"))
        axis.set_title(
            f"{label} | {len(candidates):,} candidates",
            loc="left",
            fontsize=OPERATING_POINT_FONTS["panel_title"],
            fontweight="bold",
            color="#000000",
            pad=10,
        )
        axis.set_xlabel(
            "FAH relative to the 0.25 limit",
            fontsize=OPERATING_POINT_FONTS["axis_label"],
            color="#000000",
            labelpad=8,
        )
        axis.set_ylabel(
            "Detection (%)",
            fontsize=OPERATING_POINT_FONTS["axis_label"],
            color="#000000",
        )
        axis.tick_params(
            axis="both",
            labelsize=OPERATING_POINT_FONTS["tick_number"],
            colors="#000000",
        )
        axis.grid(axis="y", color="#D5D9DE", linewidth=0.8, alpha=0.7)
        axis.grid(axis="x", color="#E3E6E9", linewidth=0.7, alpha=0.55)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#5B6770",
            markeredgecolor="white",
            markersize=9,
            label="Evaluated candidates",
        ),
        Line2D([0], [0], color="#000000", linewidth=2.2, label="Pareto frontier"),
        Patch(
            facecolor="#C8E6C9",
            edgecolor="#2E7D32",
            linewidth=1.0,
            label="G3 feasible region",
        ),
    ]
    figure.suptitle(
        "PRISM operational readiness map",
        fontsize=OPERATING_POINT_FONTS["figure_title"],
        fontweight="bold",
        color="#000000",
        y=0.995,
    )
    figure.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.965),
        ncol=3,
        frameon=False,
        fontsize=13,
    )
    grid.update(
        left=0.12, right=0.985, bottom=0.085, top=1.0 - 2.0 / figure.get_figheight()
    )
    return figure


def _plot_guarded_audit(GUARDED_AUDIT_TABLE):
    """Rendering code adapted from canonical notebook Section 17D."""
    from matplotlib.ticker import FuncFormatter, LogLocator
    import numpy as np
    import matplotlib.pyplot as plt

    audit_counts = GUARDED_AUDIT_TABLE.set_index("Audit event")["Count"].astype(int)
    accepted_updates = int(audit_counts["accepted updates"])
    rejected_updates = int(audit_counts["rejected updates"])
    promotions = int(audit_counts["promotions"])
    fault_freezes = int(audit_counts["fault freezes"])
    rollbacks = int(audit_counts["rollbacks"])
    screened_updates = accepted_updates + rejected_updates

    def audit_percent(numerator: int, denominator: int) -> float:
        return 100.0 * numerator / denominator if denominator else np.nan

    accepted_share = audit_percent(accepted_updates, screened_updates)
    rejected_share = audit_percent(rejected_updates, screened_updates)
    promotion_share = audit_percent(promotions, accepted_updates)
    freeze_share = audit_percent(fault_freezes, screened_updates)
    rollback_share = audit_percent(rollbacks, promotions)
    audit_palette = {
        "accepted updates": "#00796B",
        "rejected updates": "#F4B183",
        "promotions": "#0072B2",
        "fault freezes": "#A23B72",
        "rollbacks": "#D55E00",
    }
    BLACK = "#000000"
    GRID = "#D5D9DE"
    figure = plt.figure(figsize=(7.6, 8.6), facecolor="white")
    grid = figure.add_gridspec(nrows=2, ncols=1, height_ratios=[0.86, 1.0], hspace=0.5)
    decision_axis = figure.add_subplot(grid[0, 0])
    safeguard_axis = figure.add_subplot(grid[1, 0])
    bar_height = 0.34
    decision_axis.barh(
        [0],
        [accepted_share],
        height=bar_height,
        color=audit_palette["accepted updates"],
        edgecolor="white",
        linewidth=1.5,
        zorder=3,
    )
    decision_axis.barh(
        [0],
        [rejected_share],
        left=[accepted_share],
        height=bar_height,
        color=audit_palette["rejected updates"],
        edgecolor="white",
        linewidth=1.5,
        zorder=3,
    )
    decision_axis.text(
        accepted_share / 2.0,
        0,
        f"Accepted\n{accepted_updates:,} | {accepted_share:.1f}%",
        ha="center",
        va="center",
        multialignment="center",
        fontsize=15,
        fontweight="bold",
        color="white",
        linespacing=1.08,
        zorder=4,
    )
    decision_axis.text(
        accepted_share + rejected_share / 2.0,
        0,
        f"Rejected\n{rejected_updates:,} | {rejected_share:.1f}%",
        ha="center",
        va="center",
        multialignment="center",
        fontsize=15,
        fontweight="bold",
        color=BLACK,
        linespacing=1.08,
        zorder=4,
    )
    decision_axis.set_xlim(0.0, 100.0)
    decision_axis.set_ylim(-0.25, 0.25)
    decision_axis.set_yticks([])
    decision_axis.set_xticks([0, 25, 50, 75, 100])
    decision_axis.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"{value:g}%")
    )
    decision_axis.set_xlabel(
        "Share of update decisions",
        fontsize=16,
        fontweight="bold",
        color=BLACK,
        labelpad=8,
    )
    decision_axis.set_title(
        f"(a) Update screening  |  {screened_updates:,} decisions",
        loc="left",
        fontsize=19,
        fontweight="bold",
        color=BLACK,
        pad=10,
    )
    decision_axis.grid(axis="x", color=GRID, linewidth=0.9)
    decision_axis.set_axisbelow(True)
    safeguard_labels = ["Promotions", "Fault freezes", "Rollbacks"]
    safeguard_keys = ["promotions", "fault freezes", "rollbacks"]
    safeguard_counts = np.array([promotions, fault_freezes, rollbacks], dtype=float)
    safeguard_context = [
        f"{promotion_share:.1f}% of accepted",
        f"{freeze_share:.2f}% of screened",
        f"{rollback_share:.2f}% of promotions",
    ]
    safeguard_markers = ["o", "s", "D"]
    safeguard_positions = np.array([0.42, 0.21, 0.0])
    line_start = 6.5
    for position, key, count, context, marker in zip(
        safeguard_positions,
        safeguard_keys,
        safeguard_counts,
        safeguard_context,
        safeguard_markers,
    ):
        color = audit_palette[key]
        safeguard_axis.hlines(
            y=position,
            xmin=line_start,
            xmax=count,
            color=color,
            linewidth=5.5,
            alpha=0.82,
            zorder=2,
        )
        safeguard_axis.scatter(
            count,
            position,
            s=210,
            marker=marker,
            color=color,
            edgecolor=BLACK,
            linewidth=1.2,
            zorder=3,
        )
        if key == "promotions":
            safeguard_axis.annotate(
                f"{int(count):,} | {context}",
                xy=(count, position),
                xytext=(-8, 10),
                textcoords="offset points",
                ha="right",
                va="bottom",
                fontsize=14,
                fontweight="bold",
                color=BLACK,
                annotation_clip=False,
            )
        else:
            safeguard_axis.annotate(
                f"{int(count):,} | {context}",
                xy=(count, position),
                xytext=(12, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=14,
                fontweight="bold",
                color=BLACK,
                annotation_clip=False,
            )
    safeguard_axis.set_xscale("log")
    safeguard_axis.set_xlim(6.0, 2200.0)
    safeguard_axis.set_ylim(-0.1, 0.62)
    safeguard_axis.set_yticks(safeguard_positions)
    safeguard_axis.set_yticklabels(
        safeguard_labels, fontsize=15, fontweight="bold", color=BLACK
    )
    safeguard_axis.xaxis.set_major_locator(LogLocator(base=10.0, numticks=4))
    safeguard_axis.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"{int(value):,}" if value >= 1 else "")
    )
    safeguard_axis.set_xlabel(
        "Audit event count (log scale)",
        fontsize=16,
        fontweight="bold",
        color=BLACK,
        labelpad=8,
    )
    safeguard_axis.set_title(
        "(b) Promotion and safeguard actions",
        loc="left",
        fontsize=19,
        fontweight="bold",
        color=BLACK,
        pad=10,
    )
    safeguard_axis.grid(axis="x", color=GRID, linewidth=0.9, which="major")
    safeguard_axis.grid(axis="x", which="minor", visible=False)
    safeguard_axis.set_axisbelow(True)
    for axis in (decision_axis, safeguard_axis):
        axis.set_facecolor("white")
        axis.tick_params(axis="both", labelsize=14, colors=BLACK, width=1.1, length=5)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color(BLACK)
        axis.spines["bottom"].set_color(BLACK)
        axis.spines["left"].set_linewidth(1.1)
        axis.spines["bottom"].set_linewidth(1.1)
    figure.subplots_adjust(left=0.24, right=0.96, bottom=0.085, top=0.95, hspace=0.5)
    return figure


def _plot_operational_reliability(operational, scenario, run_scores):
    """Rendering code adapted from canonical notebook Section 17D."""
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch, FancyBboxPatch

    BLUE = "#0072B2"
    GREEN = "#009E73"
    ORANGE = "#E69F00"
    LIGHT_ORANGE = "#F4B183"
    VERMILLION = "#D55E00"
    PURPLE = "#7B2CBF"
    RED = "#C62828"
    BLACK = "#000000"
    GRID = "#D5D9DE"
    TRACK = "#AFC4D1"
    LIGHT_GREEN_CARD = "#E9F7F2"
    LIGHT_BLUE_CARD = "#EAF4FA"
    LIGHT_PURPLE_CARD = "#F3ECFA"
    figure, axes = plt.subplots(
        4, 1, figsize=(8.2, 18.6), gridspec_kw={"height_ratios": [1.8, 1.25, 1.25, 0.9]}
    )
    figure.patch.set_facecolor("white")
    scenario_plot = scenario.sort_values("Coverage %", ascending=True).copy()
    scenario_name_map = {
        "ATOMIC": "Atomic",
        "BRANCH": "Branch",
        "CACHE": "Cache",
        "CONTROLLED_CRASH": "Controlled crash",
        "DEGRADATION_PROXY": "Degradation proxy",
        "MEMBW": "Memory bandwidth",
        "POWER_SHIFT": "Power shift",
        "THERMAL_SHIFT": "Thermal shift",
        "TLB": "Address translation",
    }
    scenario_y = np.arange(len(scenario_plot))
    scenario_values = scenario_plot["Coverage %"].to_numpy(dtype=float)
    scenario_margins = scenario_values - 50.0
    scenario_colors = [
        BLUE if value >= 50.0 else LIGHT_ORANGE for value in scenario_values
    ]
    axes[0].barh(
        scenario_y,
        scenario_margins,
        color=scenario_colors,
        height=0.58,
        edgecolor="white",
        linewidth=0.9,
        zorder=3,
    )
    axes[0].axvline(0.0, color=BLACK, linestyle="--", linewidth=2.0, zorder=2)
    for y_value, coverage, margin in zip(scenario_y, scenario_values, scenario_margins):
        bar_right_edge = max(margin, 0.0)
        axes[0].text(
            bar_right_edge + 1.0,
            y_value,
            f"{coverage:.1f}% ({margin:+.1f})",
            va="center",
            ha="left",
            fontsize=12.0,
            fontweight="bold",
            color=BLACK,
            zorder=4,
            clip_on=False,
        )
    axes[0].set_yticks(
        scenario_y, [scenario_name_map[value] for value in scenario_plot["Scenario"]]
    )
    axes[0].set_xlim(-38, 33)
    axes[0].set_xlabel("Coverage margin (percentage points)", fontsize=14, labelpad=9)
    axes[0].set_title(
        "(a) Scenario coverage margin",
        loc="left",
        fontsize=17,
        fontweight="bold",
        color=BLACK,
        pad=10,
    )
    axes[0].legend(
        handles=[
            Patch(facecolor=BLUE, edgecolor=BLUE, label="Above reference"),
            Patch(
                facecolor=LIGHT_ORANGE, edgecolor=LIGHT_ORANGE, label="Below reference"
            ),
            Line2D(
                [0],
                [0],
                color=BLACK,
                linestyle="--",
                linewidth=2.0,
                label="50% reference",
            ),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=3,
        frameon=False,
        fontsize=12.0,
        columnspacing=1.4,
        handletextpad=0.6,
    )
    scopes = ["Apple M2", "AMD EPYC", "Pooled"]
    development_fah = operational.loc["FAH (development)", scopes].to_numpy(dtype=float)
    confirmation_fah = operational.loc["FAH (confirmation)", scopes].to_numpy(
        dtype=float
    )
    reliability_y = np.array([2.0, 1.0, 0.0])
    reliability_xmin = 0.085
    reliability_xmax = 0.385
    reliability_limit = 0.25
    axes[1].axvspan(
        reliability_xmin, reliability_limit, color="#E0F2EC", alpha=0.9, zorder=0
    )
    axes[1].axvspan(
        reliability_limit, reliability_xmax, color="#FBE6DE", alpha=0.9, zorder=0
    )
    axes[1].axvline(
        reliability_limit, color=RED, linestyle="--", linewidth=2.2, zorder=2
    )
    delta_label_layout = {
        "Apple M2": {"x": 0.238, "y_offset": -0.22, "ha": "right", "va": "top"},
        "AMD EPYC": {"x": 0.292, "y_offset": -0.22, "ha": "center", "va": "top"},
        "Pooled": {"x": 0.292, "y_offset": -0.22, "ha": "center", "va": "top"},
    }
    for scope_label, y_value, development_value, confirmation_value in zip(
        scopes, reliability_y, development_fah, confirmation_fah
    ):
        axes[1].annotate(
            "",
            xy=(confirmation_value, y_value),
            xytext=(development_value, y_value),
            arrowprops={
                "arrowstyle": "-|>",
                "color": TRACK,
                "linewidth": 3.2,
                "mutation_scale": 17,
                "shrinkA": 8,
                "shrinkB": 8,
            },
            zorder=2,
        )
        axes[1].scatter(
            development_value,
            y_value,
            s=175,
            marker="o",
            color=BLUE,
            edgecolor="white",
            linewidth=1.2,
            zorder=4,
        )
        axes[1].scatter(
            confirmation_value,
            y_value,
            s=185,
            marker="D",
            color=ORANGE,
            edgecolor="white",
            linewidth=1.2,
            zorder=4,
        )
        axes[1].text(
            development_value,
            y_value + 0.19,
            f"{development_value:.3f}",
            ha="center",
            va="bottom",
            fontsize=13,
            fontweight="bold",
            color=BLACK,
            zorder=5,
        )
        axes[1].text(
            confirmation_value,
            y_value + 0.19,
            f"{confirmation_value:.3f}",
            ha="center",
            va="bottom",
            fontsize=13,
            fontweight="bold",
            color=BLACK,
            zorder=5,
        )
        change = confirmation_value - development_value
        label_layout = delta_label_layout[scope_label]
        axes[1].text(
            label_layout["x"],
            y_value + label_layout["y_offset"],
            f"$\\Delta$ {change:+.3f}",
            ha=label_layout["ha"],
            va=label_layout["va"],
            fontsize=11.5,
            fontweight="bold",
            color=VERMILLION,
            zorder=5,
        )
    axes[1].set_xlim(reliability_xmin, reliability_xmax)
    axes[1].set_ylim(-0.42, 2.42)
    axes[1].set_yticks(reliability_y, scopes)
    axes[1].set_xticks([0.1, 0.15, 0.2, 0.25, 0.3, 0.35])
    axes[1].set_xlabel(
        "False alerts per benign hour (lower is better)", fontsize=14, labelpad=9
    )
    axes[1].set_title(
        "(b) Independent confirmation shift",
        loc="left",
        fontsize=17,
        fontweight="bold",
        color=BLACK,
        pad=10,
    )
    axes[1].legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="o",
                linestyle="none",
                markerfacecolor=BLUE,
                markeredgecolor="white",
                markersize=10,
                label="Development",
            ),
            Line2D(
                [0],
                [0],
                marker="D",
                linestyle="none",
                markerfacecolor=ORANGE,
                markeredgecolor="white",
                markersize=9,
                label="Independent confirmation",
            ),
            Line2D(
                [0],
                [0],
                color=RED,
                linestyle="--",
                linewidth=2.2,
                label="0.25 FAH limit",
            ),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.3),
        ncol=2,
        frameon=False,
        fontsize=12.0,
        columnspacing=1.5,
        handletextpad=0.6,
    )
    platform_specs = [
        ("M2_MACOS", "Apple M2", BLUE),
        ("EPYC_LINUX", "AMD EPYC", VERMILLION),
    ]
    delay_groups = []
    for platform_id, _, _ in platform_specs:
        delays = (
            run_scores.loc[
                (run_scores["platform_id"] == platform_id)
                & run_scores["detection_delay_seconds"].notna(),
                "detection_delay_seconds",
            ]
            .sort_values()
            .to_numpy(dtype=float)
        )
        delay_groups.append(delays)
    delay_positions = np.asarray([1.0, 0.0])
    violin = axes[2].violinplot(
        delay_groups,
        positions=delay_positions,
        vert=False,
        widths=0.72,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )
    for body, (_, _, color) in zip(violin["bodies"], platform_specs):
        body.set_facecolor(color)
        body.set_edgecolor(color)
        body.set_linewidth(1.5)
        body.set_alpha(0.24)
    axes[2].boxplot(
        delay_groups,
        positions=delay_positions,
        vert=False,
        widths=0.17,
        patch_artist=True,
        showfliers=False,
        boxprops={"facecolor": "white", "edgecolor": BLACK, "linewidth": 1.5},
        whiskerprops={"color": BLACK, "linewidth": 1.3},
        capprops={"color": BLACK, "linewidth": 1.3},
        medianprops={"color": BLACK, "linewidth": 2.0},
    )
    rng = np.random.default_rng(20260825)
    for position, delays, (_, _, color) in zip(
        delay_positions, delay_groups, platform_specs
    ):
        jitter = rng.normal(position, 0.045, size=len(delays))
        axes[2].scatter(
            delays,
            jitter,
            s=30,
            color=color,
            alpha=0.72,
            edgecolor="white",
            linewidth=0.5,
            zorder=3,
        )
        median_delay = float(np.median(delays))
        axes[2].scatter(
            [median_delay],
            [position],
            marker="D",
            s=105,
            color=BLACK,
            edgecolor="white",
            linewidth=0.9,
            zorder=5,
        )
        axes[2].annotate(
            f"median {median_delay:.1f} s",
            (median_delay, position),
            xytext=(0, 16),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
            color=BLACK,
            zorder=6,
        )
    all_delays = np.concatenate(delay_groups)
    axes[2].set_xlim(float(all_delays.min()) - 10, float(all_delays.max()) + 10)
    axes[2].set_yticks(delay_positions, [label for _, label, _ in platform_specs])
    axes[2].set_xlabel("Detection delay (s)", fontsize=14, labelpad=9)
    axes[2].set_title(
        "(c) Detection delay distribution",
        loc="left",
        fontsize=17,
        fontweight="bold",
        color=BLACK,
        pad=10,
    )
    axes[2].tick_params(axis="both", labelsize=12, colors=BLACK)
    axes[2].grid(axis="x", alpha=0.18)
    axes[2].legend(
        handles=[
            Patch(facecolor="#DCECF5", edgecolor=BLUE, label="Distribution"),
            Line2D(
                [0],
                [0],
                marker="o",
                linestyle="none",
                color=BLACK,
                markersize=7,
                label="Detected run",
            ),
            Line2D(
                [0],
                [0],
                marker="D",
                linestyle="none",
                color=BLACK,
                markersize=8,
                label="Median",
            ),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.29),
        ncol=3,
        frameon=False,
        fontsize=12.0,
        columnspacing=1.4,
        handletextpad=0.6,
    )

    def boolean_mask(series):
        """Convert boolean-like CSV values into a reliable mask."""
        return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})

    fault_case_mask = boolean_mask(run_scores["telemetry_fault_case"])
    fault_identified_mask = boolean_mask(run_scores["telemetry_fault_identified"])
    total_fault_runs = int(fault_case_mask.sum())
    identified_fault_runs = int((fault_case_mask & fault_identified_mask).sum())
    if total_fault_runs == 0:
        raise RuntimeError("No telemetry fault runs were found for panel (d).")
    fault_identification_rate = 100.0 * identified_fault_runs / total_fault_runs
    confirmation_hours = float(
        operational.loc["Independent benign monitoring", "Pooled"]
    )
    confirmation_seconds = int(round(confirmation_hours * 3600.0))
    valid_confirmation_rate = float(
        operational.loc["Valid confirmation time", "Pooled"]
    )
    valid_confirmation_seconds = int(
        round(confirmation_seconds * valid_confirmation_rate / 100.0)
    )
    rich_telemetry_avoided_rate = float(
        operational.loc["Rich telemetry avoided (replay)", "Pooled"]
    )
    rich_telemetry_retained_rate = 100.0 - rich_telemetry_avoided_rate
    rich_telemetry_retained_seconds = int(
        round(confirmation_seconds * rich_telemetry_retained_rate / 100.0)
    )
    accounting_cards = [
        {
            "title": "Telemetry faults\nidentified",
            "accounting": f"{identified_fault_runs:,} / {total_fault_runs:,} runs",
            "rate": f"{fault_identification_rate:.0f}%",
            "color": GREEN,
            "facecolor": LIGHT_GREEN_CARD,
        },
        {
            "title": "Valid confirmation\nmonitoring",
            "accounting": f"{valid_confirmation_seconds:,} / {confirmation_seconds:,} s",
            "rate": f"{valid_confirmation_rate:.0f}%",
            "color": BLUE,
            "facecolor": LIGHT_BLUE_CARD,
        },
        {
            "title": "Rich telemetry retained\nin replay",
            "accounting": f"{rich_telemetry_retained_seconds:,} / {confirmation_seconds:,} s",
            "rate": f"{rich_telemetry_retained_rate:.2f}%",
            "color": PURPLE,
            "facecolor": LIGHT_PURPLE_CARD,
        },
    ]
    axes[3].set_xlim(0.0, 1.0)
    axes[3].set_ylim(0.0, 1.0)
    axes[3].set_axis_off()
    axes[3].text(
        0.0,
        0.98,
        "(d) Integrity and replay accounting",
        transform=axes[3].transAxes,
        ha="left",
        va="top",
        fontsize=17,
        fontweight="bold",
        color=BLACK,
    )
    card_x_positions = [0.0, 0.345, 0.69]
    card_width = 0.31
    card_y = 0.1
    card_height = 0.68
    for x_position, card in zip(card_x_positions, accounting_cards):
        card_patch = FancyBboxPatch(
            (x_position, card_y),
            card_width,
            card_height,
            boxstyle="round,pad=0.012,rounding_size=0.025",
            transform=axes[3].transAxes,
            facecolor=card["facecolor"],
            edgecolor=card["color"],
            linewidth=1.8,
            clip_on=False,
            zorder=2,
        )
        axes[3].add_patch(card_patch)
        axes[3].plot(
            [x_position + 0.025, x_position + card_width - 0.025],
            [card_y + card_height - 0.045, card_y + card_height - 0.045],
            transform=axes[3].transAxes,
            color=card["color"],
            linewidth=5.0,
            solid_capstyle="round",
            clip_on=False,
            zorder=3,
        )
        # Smaller card typography avoids label overlap at one-column scale.
        axes[3].text(
            x_position + card_width / 2.0,
            card_y + 0.49,
            card["title"],
            transform=axes[3].transAxes,
            ha="center",
            va="center",
            fontsize=11.0,
            fontweight="bold",
            color=BLACK,
            linespacing=1.15,
            zorder=4,
        )
        axes[3].text(
            x_position + card_width / 2.0,
            card_y + 0.27,
            card["accounting"],
            transform=axes[3].transAxes,
            ha="center",
            va="center",
            fontsize=11.2,
            fontweight="bold",
            color=BLACK,
            zorder=4,
        )
        axes[3].text(
            x_position + card_width / 2.0,
            card_y + 0.105,
            card["rate"],
            transform=axes[3].transAxes,
            ha="center",
            va="center",
            fontsize=15.0,
            fontweight="bold",
            color=card["color"],
            zorder=4,
        )
    for axis in axes[:3]:
        axis.set_facecolor("white")
        axis.tick_params(axis="both", labelsize=12.5, colors=BLACK, width=1.0, length=4)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color(BLACK)
        axis.spines["bottom"].set_color(BLACK)
        axis.xaxis.label.set_color(BLACK)
        axis.yaxis.label.set_color(BLACK)
    axes[0].grid(axis="x", color=GRID, linewidth=0.9, alpha=0.85, zorder=0)
    axes[1].grid(axis="x", color=GRID, linewidth=0.9, alpha=0.85, zorder=0)
    axes[1].tick_params(axis="x", length=4)
    axes[1].tick_params(axis="y", length=0)
    axes[2].grid(axis="x", color=GRID, linewidth=0.9, alpha=0.85, zorder=0)
    figure.suptitle(
        "PRISM operational reliability profile",
        x=0.24,
        y=0.985,
        ha="left",
        fontsize=21,
        fontweight="bold",
        color=BLACK,
    )
    figure.subplots_adjust(left=0.24, right=0.97, bottom=0.045, top=0.95, hspace=1.12)
    return figure
