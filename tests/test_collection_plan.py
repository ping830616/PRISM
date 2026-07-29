import importlib.util
import tomllib
import unittest
from collections import Counter
from pathlib import Path

from prism_slm.workload_harness import SCENARIOS


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "make_collection_plan",
    ROOT / "scripts/make_collection_plan.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CollectionPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (ROOT / "configs/experiment-matrix.toml").open("rb") as stream:
            cls.config = tomllib.load(stream)
        cls.rows = MODULE.build_rows(cls.config)

    def test_extension_plan_inventory(self) -> None:
        self.assertEqual(len(self.rows), 252)
        self.assertEqual(
            Counter(row["run_kind"] for row in self.rows),
            {
                "required_matrix": 192,
                "targeted_extension": 36,
                "long_benign": 24,
            },
        )
        total_hours = sum(int(row["duration_seconds"]) for row in self.rows) / 3600
        self.assertAlmostEqual(total_hours, 64.8)

    def test_each_platform_has_twelve_planned_benign_hours(self) -> None:
        for platform_id in ("M2_MACOS", "EPYC_LINUX"):
            hours = (
                sum(
                    int(row["duration_seconds"])
                    for row in self.rows
                    if row["platform_id"] == platform_id
                    and row["scenario"] == "NOMINAL"
                )
                / 3600
            )
            self.assertAlmostEqual(hours, 12.0)

    def test_targeted_extension_scenarios_are_repeated(self) -> None:
        targeted = {
            row["scenario"]
            for row in self.rows
            if row["run_kind"] == "targeted_extension"
        }
        self.assertEqual(
            targeted,
            {"THERMAL_SHIFT", "POWER_SHIFT", "DEGRADATION_PROXY"},
        )
        planned_scenarios = {row["scenario"] for row in self.rows}
        self.assertTrue(planned_scenarios.issubset(set(SCENARIOS)))


if __name__ == "__main__":
    unittest.main()
