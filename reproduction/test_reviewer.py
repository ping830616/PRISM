"""Focused checks for the offline reviewer path; never collect or fit a model.

Run: python -m unittest discover -s reproduction -p 'test_reviewer.py' -v
Set PRISM_REVIEWER_FULL_TEST=1 to additionally render the complete output bundle.
Scientific checks skip when the reviewer extras are absent; integrity and CLI
verification use only the standard library and must still pass.
"""
from __future__ import annotations

import contextlib
import copy
import csv
import hashlib
import importlib.abc
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


REPRODUCTION = Path(__file__).resolve().parent
ROOT = REPRODUCTION.parent
if str(REPRODUCTION) not in sys.path:
    sys.path.insert(0, str(REPRODUCTION))
import reproduce

SCIENTIFIC_AVAILABLE = all(
    importlib.util.find_spec(name) is not None
    for name in ("numpy", "pandas", "scipy", "matplotlib", "jinja2")
)
RESEARCH_IMPORTS = {"prism_slm", "experiments", "psutil", "sklearn", "nbclient", "nbformat"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class BlockResearchImports(importlib.abc.MetaPathFinder):
    """Fail if saved-result routines try to import collection/fitting machinery."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in RESEARCH_IMPORTS:
            raise AssertionError(f"Reviewer path imported research machinery: {fullname}")
        return None


@contextlib.contextmanager
def without_research_imports():
    blocker = BlockResearchImports()
    sys.meta_path.insert(0, blocker)
    try:
        yield
    finally:
        sys.meta_path.remove(blocker)


class InputIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="prism-reviewer-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "fixture"
        (self.root / "reproduction").mkdir(parents=True)
        self.payload = self.root / "inputs/evidence.json"
        self.payload.parent.mkdir()
        self.payload.write_text('{"events": 71}\n', encoding="utf-8")
        self.manifest = {
            "schema_version": 1,
            "required_sha256": {"inputs/evidence.json": sha256(self.payload)},
        }
        self.save_manifest()

    def save_manifest(self):
        (self.root / "reproduction/reviewer-manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )

    def test_valid_input_is_verified_without_output(self):
        before = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        self.assertEqual(reproduce.verify_inputs(self.root), self.manifest)
        self.assertEqual(before, sorted(p.relative_to(self.root) for p in self.root.rglob("*")))

    def test_tampering_fails_before_creating_output_or_parent(self):
        self.payload.write_text('{"events": 120}\n', encoding="utf-8")
        output = self.base / "new-parent/result"
        with self.assertRaisesRegex(ValueError, "checksum mismatch: inputs/evidence.json"):
            reproduce.reproduce(output, self.root)
        self.assertFalse(output.parent.exists())

    def test_missing_input_fails_before_creating_output(self):
        self.payload.unlink()
        output = self.base / "result"
        with self.assertRaisesRegex(ValueError, "missing: inputs/evidence.json"):
            reproduce.reproduce(output, self.root)
        self.assertFalse(output.exists())

    def test_unsupported_or_empty_manifest_is_rejected(self):
        for manifest in (
            {"schema_version": 2, "required_sha256": self.manifest["required_sha256"]},
            {"schema_version": 1, "required_sha256": {}},
        ):
            with self.subTest(manifest=manifest):
                self.manifest = manifest
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "Unrecognized or empty"):
                    reproduce.verify_inputs(self.root)

    def test_manifest_path_traversal_absolute_and_backslash_are_rejected(self):
        for relative in ("../outside.json", "inputs/../../outside.json", "/tmp/outside.json", "inputs\\evidence.json"):
            with self.subTest(relative=relative):
                self.manifest["required_sha256"] = {relative: "0" * 64}
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "Unsafe manifest path"):
                    reproduce.verify_inputs(self.root)

    def test_manifest_symlink_cannot_escape_repository(self):
        outside = self.base / "outside.json"
        outside.write_text("private fixture", encoding="utf-8")
        try:
            (self.root / "inputs/outside.json").symlink_to(outside)
        except OSError:
            if os.name == "nt":
                self.skipTest("This Windows account cannot create symbolic links")
            raise
        self.manifest["required_sha256"] = {"inputs/outside.json": sha256(outside)}
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "escapes repository"):
            reproduce.verify_inputs(self.root)

    def test_existing_output_is_preserved(self):
        output = self.base / "previous-result"
        output.mkdir()
        marker = output / "keep.txt"
        marker.write_text("previous evidence", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Output already exists"):
            reproduce.reproduce(output, self.root)
        self.assertEqual(marker.read_text(), "previous evidence")
        self.assertEqual(list(output.iterdir()), [marker])

    def test_failed_export_discards_partial_stage(self):
        tables = types.ModuleType("reviewer_tables")
        plots = types.ModuleType("reviewer_plots")

        def broken_export(root, output):
            output.mkdir()
            (output / "partial.csv").write_text("unfinished\n", encoding="utf-8")
            raise RuntimeError("synthetic export failure")

        tables.export_tables = broken_export
        plots.render_figures = mock.Mock(side_effect=AssertionError("Rendering must not start"))
        output = self.base / "output/result"
        with mock.patch.dict(sys.modules, {"reviewer_tables": tables, "reviewer_plots": plots}), mock.patch.dict(os.environ):
            with self.assertRaisesRegex(RuntimeError, "synthetic export failure"):
                reproduce.reproduce(output, self.root)
        self.assertFalse(output.exists())
        self.assertEqual(list(output.parent.iterdir()), [])
        plots.render_figures.assert_not_called()


class PackagedEvidenceTests(unittest.TestCase):
    def test_frozen_manifest_covers_numerical_inputs_and_manuscript_assets(self):
        manifest = reproduce.verify_inputs(ROOT)
        required = manifest["required_sha256"]
        for relative in (
            "reproduction/inputs/figure-4-micro-twin.csv",
            "reproduction/inputs/figure-4-micro-twin.json", "reproduction/manuscript/manifest.json",
        ):
            self.assertIn(relative, required)
        static = json.loads((REPRODUCTION / "manuscript/manifest.json").read_text())
        for artifact in static["artifacts"]:
            with self.subTest(path=artifact["path"]):
                self.assertIn("reproduction/manuscript/" + artifact["path"], required)
        self.assertEqual(len(manifest["expected_results"]["table_viii_display_rows"]), 12)

    def test_exact_manuscript_has_seven_figures_and_nine_tables(self):
        static_root = REPRODUCTION / "manuscript"
        manifest = json.loads((static_root / "manifest.json").read_text())
        figures = [row for row in manifest["artifacts"] if row["kind"] == "figure"]
        tables = [row for row in manifest["artifacts"] if row["kind"] == "table"]
        self.assertEqual([row["number"] for row in figures], list(range(1, 8)))
        self.assertEqual([row["number"] for row in tables], ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"])
        self.assertEqual([row["role"] for row in figures[:3]], ["authored_diagram"] * 3)
        for artifact in manifest["artifacts"]:
            with self.subTest(path=artifact["path"]):
                path = reproduce.inside(static_root, artifact["path"])
                self.assertEqual(sha256(path), artifact["sha256"])

    def test_verify_cli_works_from_foreign_cwd_without_site_packages(self):
        with tempfile.TemporaryDirectory(prefix="prism-foreign-cwd-") as directory:
            result = subprocess.run(
                [sys.executable, "-S", str(REPRODUCTION / "reproduce.py"), "--verify-only"],
                cwd=directory, capture_output=True, text=True, timeout=60,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("packaged input checksums verified", result.stdout)
            self.assertIn("no numerical execution", result.stdout)
            self.assertEqual(list(Path(directory).iterdir()), [])


@unittest.skipUnless(SCIENTIFIC_AVAILABLE, "Install reproduction/requirements-reviewer.txt for numerical checks")
class NumericalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="prism-reviewer-numerical-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.base = Path(cls.temporary.name)
        cls.environment = mock.patch.dict(os.environ, {
            "MPLCONFIGDIR": str(cls.base / "matplotlib"),
            "XDG_CACHE_HOME": str(cls.base / "cache"),
            "MPLBACKEND": "Agg",
        })
        cls.environment.start()
        cls.addClassCleanup(cls.environment.stop)
        with without_research_imports():
            import reviewer_tables
            import reviewer_plots
            cls.plots = reviewer_plots
            with contextlib.redirect_stdout(io.StringIO()):
                cls.check = reviewer_tables.export_tables(ROOT, cls.base / "tables")

    def table_rows(self, name):
        with (self.base / "tables" / name).open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

    def test_recorded_headlines_preserve_counts_and_failed_confirmation(self):
        self.assertEqual(self.check["validated_runs"], 208)
        self.assertEqual(self.check["development_runs_including_calibration"], 192)
        self.assertEqual(self.check["confirmation_runs"], 16)
        self.assertEqual(self.check["reserved_runs_planned"], 92)
        self.assertEqual(self.check["reserved_runs_accessed_by_this_cell"], 0)
        self.assertEqual(self.check["detected_controlled_event_runs"], 71)
        self.assertEqual(self.check["eligible_controlled_event_runs"], 120)
        self.assertAlmostEqual(self.check["confirmation_fah"], 6 / 16.8, places=12)
        self.assertIs(self.check["development_g3_passed"], True)
        self.assertIs(self.check["independent_confirmation_passed"], False)

    def test_table_viii_retains_all_twelve_pooled_and_subgroup_rows(self):
        rows = self.table_rows("table-viii-development-progression.csv")
        self.assertEqual(len(rows), 12)
        self.assertEqual([row["Section"][0] for row in rows], list("AAAABBBBCCCC"))
        self.assertEqual((int(rows[3]["Detected"]), int(rows[3]["Event runs"])), (71, 120))
        self.assertEqual(rows[3]["Outcome"], "Advance")
        self.assertEqual([row["Outcome"] for row in rows[4:8]], ["Fail", "Fail", "Pass", "Fail"])
        self.assertEqual([int(row["Detected"]) for row in rows[8:]], [37, 34, 33, 38])
        self.assertEqual([row["Outcome"] for row in rows[8:]], ["Pass"] * 4)

    def test_revision_and_replay_exposure_are_separate_from_event_detection(self):
        revisions = self.table_rows("table-vii-revision-history.csv")
        v3 = next(row for row in revisions if row["Revision"] == "v3")
        self.assertEqual(int(v3["Episodes"]), 6)
        self.assertAlmostEqual(float(v3["Benign h"]), 16.8, places=12)
        replay = next(row for row in self.table_rows("table-replay-accounting.csv") if row["Scope"] == "Pooled")
        self.assertEqual((int(replay["Rich blocks"]), int(replay["Valid blocks"])), (37, 12096))
        self.assertEqual((int(replay["Rich seconds"]), int(replay["Valid seconds"])), (185, 60480))

    def test_frozen_result_checks_reject_changed_headline_and_subgroup(self):
        expected = reproduce.verify_inputs(ROOT)["expected_results"]
        reproduce.verify_results(self.check, self.base, expected)
        wrong = copy.deepcopy(self.check)
        wrong["detected_controlled_event_runs"] = 72
        with self.assertRaisesRegex(ValueError, "Headline mismatch"):
            reproduce.verify_results(wrong, self.base, expected)
        changed = copy.deepcopy(expected)
        changed["table_viii_display_rows"] = changed["table_viii_display_rows"][:-1]
        with self.assertRaisesRegex(ValueError, "Table VIII subgroup rows"):
            reproduce.verify_results(self.check, self.base, changed)

    def test_saved_result_imports_exclude_collection_and_model_fitting(self):
        self.assertFalse(RESEARCH_IMPORTS.intersection(name.split(".")[0] for name in sys.modules))

    def test_missing_plot_values_fail_before_output_despite_archived_image(self):
        with tempfile.TemporaryDirectory(prefix="prism-missing-plot-") as directory:
            root = Path(directory)
            archive = root / "reproduction/manuscript/figures"
            archive.mkdir(parents=True)
            (archive / "figure-4-digital.png").write_bytes(b"preserved image is not numerical evidence")
            output = root / "new-figures"
            with without_research_imports(), self.assertRaisesRegex(FileNotFoundError, "Missing numerical figure inputs"):
                self.plots.render_figures(root, output)
            self.assertFalse(output.exists())

    def test_micro_twin_rejects_invalid_times_values_and_identity(self):
        import pandas as pd
        frame = pd.DataFrame({name: [1.0, 2.0, 3.0] for name in self.plots._TRACE_COLUMNS})
        frame["time_seconds"] = [2.5, 7.5, 12.5]
        metadata = {"run_id": "m2_macos__py_stats__membw__r01", "state": "compute_activity", "onset_seconds": 7.5, "diagnostic_threshold": 2.0}
        self.plots._validate_trace(frame, metadata)
        cases = []
        invalid = frame.copy()
        invalid["time_seconds"] = [2.5, 7.5, 7.5]
        cases.append((invalid, metadata, "strictly increasing"))
        invalid = frame.copy()
        invalid.loc[1, "aggregate_evidence"] = float("inf")
        cases.append((invalid, metadata, "infinity"))
        invalid = frame.copy()
        invalid["aggregate_evidence"] = float("nan")
        cases.append((invalid, metadata, "no finite values"))
        cases.append((frame.drop(columns=["residual_compute_activity"]), metadata, "lacks columns"))
        cases.append((frame, {**metadata, "onset_seconds": 1000}, "outside the plotted time range"))
        cases.append((frame, {**metadata, "run_id": "substituted_run"}, "fixed manuscript run"))
        for trace, info, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.plots._validate_trace(trace, info)


@unittest.skipUnless(
    SCIENTIFIC_AVAILABLE and os.environ.get("PRISM_REVIEWER_FULL_TEST") == "1",
    "Set PRISM_REVIEWER_FULL_TEST=1 with reviewer dependencies for the full rendering test",
)
class FullRenderingTests(unittest.TestCase):
    def test_complete_bundle_has_four_regenerated_png_pdf_pairs_and_verified_files(self):
        with tempfile.TemporaryDirectory(prefix="prism-reviewer-full-") as directory, mock.patch.dict(os.environ):
            output = Path(directory) / "result"
            with without_research_imports(), contextlib.redirect_stdout(io.StringIO()):
                report = reproduce.reproduce(output, ROOT)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["scope"], "saved_artifact_reproduction_not_raw_reanalysis")
            for field in ("collection_performed", "model_fitting_performed", "reserved_data_accessed"):
                self.assertIs(report[field], False)
            self.assertEqual([row["figure_number"] for row in report["regenerated_figures"]], [4, 5, 6, 7])
            for figure in report["regenerated_figures"]:
                self.assertEqual(figure["status"], "regenerated")
                self.assertEqual({Path(path).suffix for path in figure["outputs"]}, {".png", ".pdf"})
                for relative in figure["outputs"]:
                    path = reproduce.inside(output, relative)
                    self.assertGreater(path.stat().st_size, 100)
                    signature = b"\x89PNG\r\n\x1a\n" if path.suffix == ".png" else b"%PDF-"
                    self.assertTrue(path.read_bytes().startswith(signature))
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "reproduction-report.json").is_file())
            for relative, expected in report["output_sha256"].items():
                with self.subTest(path=relative):
                    self.assertEqual(sha256(reproduce.inside(output, relative)), expected)


if __name__ == "__main__":
    unittest.main()
