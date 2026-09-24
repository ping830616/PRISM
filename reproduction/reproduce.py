#!/usr/bin/env python3
"""Offline reviewer reproduction of PRISM's saved numerical paper artifacts.

No collection, raw-data reanalysis, model fitting, or notebook execution.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.metadata
import json
import math
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inside(root, relative):
    name = PurePosixPath(relative)
    if name.is_absolute() or ".." in name.parts or "\\" in relative:
        raise ValueError(f"Unsafe manifest path: {relative}")
    path = (root / str(name)).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Manifest path escapes repository: {relative}")
    return path


def verify_inputs(root=ROOT):
    root = Path(root).resolve()
    manifest_path = root / "reproduction/reviewer-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not manifest.get("required_sha256"):
        raise ValueError("Unrecognized or empty reviewer input manifest")
    errors = []
    for relative, expected in manifest["required_sha256"].items():
        path = inside(root, relative)
        if not path.is_file():
            errors.append(f"missing: {relative}")
        elif digest(path) != expected:
            errors.append(f"checksum mismatch: {relative}")
    if errors:
        raise ValueError("Reviewer input verification failed:\n" + "\n".join(errors))
    return manifest


def verify_results(check, output, expected):
    """Check independently frozen paper values, not image-byte equality."""
    import pandas as pd
    for key, target in expected["headline"].items():
        value = check.get(key)
        if isinstance(target, bool):
            matches = value is target
        elif isinstance(target, int):
            matches = value == target
        else:
            matches = isinstance(value, (int, float)) and math.isclose(value, target, rel_tol=1e-10, abs_tol=1e-10)
        if not matches:
            raise ValueError(f"Headline mismatch for {key}: {value!r} versus {target!r}")
    table = pd.read_csv(output / "tables/table-viii-development-progression.csv")
    actual = [[f"{r['Benign hours']:.2f}", f"{r['FAH']:.3f}",
               f"{int(r['Detected'])}/{int(r['Event runs'])}", f"{r['DR (%)']:.1f}", r["Outcome"]]
              for r in table.to_dict("records")]
    if actual != expected["table_viii_display_rows"]:
        raise ValueError("Current manuscript Table VIII subgroup rows do not match")


def write_gallery(output, report):
    import pandas as pd
    pieces = ["<!doctype html><html lang='en'><meta charset='utf-8'>",
              "<meta name='viewport' content='width=device-width,initial-scale=1'>",
              "<title>PRISM reviewer reproduction</title>",
              "<style>body{font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin:40px auto;padding:0 24px;color:#17212b}"
              "h1,h2,h3{line-height:1.2}img{display:block;max-width:100%;max-height:850px;margin:20px auto}"
              "table{border-collapse:collapse;font-size:14px;width:100%}td,th{border:1px solid #ccd3da;padding:7px;text-align:left}"
              "th{background:#eef2f5}section{margin:40px 0}.scroll{overflow:auto}a{color:#174d87}</style>",
              "<h1>PRISM reviewer reproduction</h1>",
              "<p>Saved numerical reports and exported plotting values were verified and used to regenerate the result tables and Figures 4–7. "
              "This run did not collect telemetry, fit a model, or revalidate the original recordings.</p>",
              "<p>Exact manuscript assets are preserved separately. Their copying is not counted as numerical regeneration. "
              "Fonts and layout in regenerated plots may differ from the manuscript.</p>",
              "<p><a href='reproduction-report.json'>Machine-readable verification report</a></p>"]
    for record in report["manuscript_assets"]:
        if record["kind"] == "figure" and record["number"] <= 3:
            path = "manuscript/" + record["path"]
            pieces.append(f"<section><h2>Figure {record['number']} — authored diagram</h2><img alt='Manuscript Figure {record['number']}' src='{html.escape(path)}'></section>")
    for record in report["regenerated_figures"]:
        number = record["figure_number"]
        png = next(name for name in record["outputs"] if name.endswith(".png"))
        reference = next(x for x in report["manuscript_assets"] if x["kind"] == "figure" and x["number"] == number)
        pieces.append(f"<section><h2>Figure {number} — regenerated from numerical inputs</h2><img alt='Regenerated Figure {number}' src='{html.escape(png)}'>"
                      f"<details><summary>Exact manuscript reference image</summary><img alt='Exact Figure {number}' src='manuscript/{html.escape(reference['path'])}'></details></section>")
    pieces.append("<h2>All nine manuscript tables</h2><p>Tables I–V are authored descriptions, comparisons and configurations, not learned numerical outputs. "
                  "Their original editable LaTeX is preserved. Tables VI–IX are also regenerated below.</p><ul>")
    for record in report["manuscript_assets"]:
        if record["kind"] == "table":
            pieces.append(f"<li><a href='manuscript/{html.escape(record['path'])}'>Table {record['number']} original LaTeX</a> — {html.escape(record['role'])}</li>")
    pieces.append("</ul><p>For table compilation, use manuscript/table-preamble.tex and references.bib with your IEEEtran project.</p>")
    for path in sorted((output / "tables").glob("*.csv")):
        frame = pd.read_csv(path)
        pieces.append(f"<section><h3>{html.escape(path.stem)}</h3><p><a href='tables/{path.name}'>CSV</a></p><div class='scroll'>" + frame.to_html(index=False, border=0, float_format=lambda value: f"{value:.6g}", na_rep="—") + "</div></section>")
    pieces.append("</html>")
    (output / "index.html").write_text("\n".join(pieces), encoding="utf-8")


def reproduce(output, root=ROOT):
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest = verify_inputs(root)
    if output.exists():
        raise ValueError("Output already exists; choose a new --output directory to preserve earlier results")
    if output == root or root.is_relative_to(output):
        raise ValueError("Output must not be the repository or its parent")
    # Thread limits precede scientific imports. They affect only this process.
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"):
        os.environ[name] = "1"
    os.environ["MPLBACKEND"] = "Agg"
    with tempfile.TemporaryDirectory(prefix="prism-render-") as runtime:
        os.environ["MPLCONFIGDIR"] = runtime
        os.environ["XDG_CACHE_HOME"] = runtime
        from reviewer_tables import export_tables
        from reviewer_plots import render_figures
        output.parent.mkdir(parents=True, exist_ok=True)
        # Stage outputs; no PASS report or destination is left after a failed run.
        with tempfile.TemporaryDirectory(prefix=".prism-stage-", dir=output.parent) as stage:
            working = Path(stage) / "result"
            working.mkdir()
            check = export_tables(root, working / "tables")
            figures = render_figures(root, working / "figures", root / "reproduction/inputs")
            verify_results(check, working, manifest["expected_results"])
            static_manifest = json.loads((root / "reproduction/manuscript/manifest.json").read_text(encoding="utf-8"))
            shutil.copytree(root / "reproduction/manuscript", working / "manuscript")
            for figure in figures:
                figure["outputs"] = [Path(path).relative_to(working).as_posix() for path in figure["outputs"]]
            report = {"status": "PASS", "scope": "saved_artifact_reproduction_not_raw_reanalysis",
                      "collection_performed": False, "model_fitting_performed": False, "reserved_data_accessed": False,
                      "base_commit": manifest["base_commit"], "reviewer_manifest_sha256": digest(root / "reproduction/reviewer-manifest.json"),
                      "reproduction_code_sha256": {path.name: digest(path) for path in sorted((root / "reproduction").glob("*.py"))},
                      "verified_input_count": len(manifest["required_sha256"]), "headlines": check,
                      "regenerated_figures": figures, "manuscript_assets": static_manifest["artifacts"],
                      "environment": {"python": platform.python_version(), "system": platform.system(), "machine": platform.machine(),
                                      "packages": {name: importlib.metadata.version(name) for name in ("numpy", "pandas", "scipy", "matplotlib", "Jinja2")}},
                      "tolerances": {"numerical_relative": 1e-10, "numerical_absolute": 1e-10, "plot_bytes": "not compared across platforms"}}
            write_gallery(working, report)
            report["output_sha256"] = {path.relative_to(working).as_posix(): digest(path) for path in sorted(working.rglob("*")) if path.is_file()}
            (working / "reproduction-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            working.rename(output)
    print(f"PASS: {len(manifest['required_sha256'])} verified inputs; result tables and four numerical figures regenerated.")
    print(f"Open {output / 'index.html'}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reviewer-output"))
    parser.add_argument("--verify-only", action="store_true", help="Check packaged inputs without importing scientific libraries or writing output")
    args = parser.parse_args()
    try:
        if args.verify_only:
            manifest = verify_inputs()
            print(f"PASS: {len(manifest['required_sha256'])} packaged input checksums verified (no numerical execution).")
        else:
            reproduce(args.output)
    except (ValueError, FileNotFoundError, ModuleNotFoundError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
