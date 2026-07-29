import tempfile
import unittest
import json
from pathlib import Path

from prism_slm.collection import (
    channel_group,
    channel_unit,
    flatten_leaves,
    validate_run,
    verify_checksums,
    write_checksums,
)
from prism_slm.contracts import SemanticGroup


class CollectionTests(unittest.TestCase):
    def test_channel_semantics(self) -> None:
        self.assertEqual(
            channel_group("enriched.temp.cpu_temp_avg"),
            SemanticGroup.THERMAL_POWER,
        )
        self.assertEqual(
            channel_group("enriched.gpu_power"),
            SemanticGroup.ACCELERATOR,
        )
        self.assertEqual(channel_group("host.memory.available"), SemanticGroup.MEMORY)
        self.assertEqual(channel_group("host.network.bytes_sent_total"), SemanticGroup.IO)

    def test_channel_units(self) -> None:
        self.assertEqual(channel_unit("enriched.cpu_power"), "watts")
        self.assertEqual(channel_unit("enriched.temp.cpu_temp_avg"), "celsius")
        self.assertEqual(channel_unit("host.memory.available"), "bytes")
        self.assertEqual(channel_unit("enriched.pcpu_usage.0"), "megahertz")
        self.assertEqual(channel_unit("enriched.pcpu_usage.1"), "fraction")
        self.assertEqual(
            channel_unit("host.cpu_utilization_derived_percent"),
            "percent",
        )

    def test_flatten_and_checksum(self) -> None:
        self.assertEqual(
            flatten_leaves({"cpu": {"usage": [1000, 0.5]}}),
            {"cpu.usage.0": 1000, "cpu.usage.1": 0.5},
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "telemetry.jsonl").write_text('{"sample": 1}\n')
            write_checksums(root)
            self.assertEqual(verify_checksums(root), [])
            (root / "telemetry.jsonl").write_text('{"sample": 2}\n')
            self.assertIn("checksum mismatch", verify_checksums(root)[0])

    def test_validator_rejects_compressed_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "platform.json").write_text("{}\n")
            (root / "channels.json").write_text('{"channels": []}\n')
            (root / "collection.json").write_text(
                json.dumps(
                    {
                        "expected_samples": 3,
                        "sampling_hz": 1,
                        "scenario": "NOMINAL",
                        "status": "complete",
                    }
                )
                + "\n"
            )
            (root / "events.jsonl").write_text(
                '{"event": "workload_started"}\n'
            )
            (root / "telemetry.jsonl").write_text(
                "\n".join(
                    json.dumps(
                        {
                            "t_rel_seconds": value,
                            "enriched": None,
                        }
                    )
                    for value in (0.0, 0.01, 0.02)
                )
                + "\n"
            )
            result = validate_run(root, verify_hashes=False)
            self.assertFalse(result["valid"])
            self.assertTrue(
                any("observed sample span" in item for item in result["failures"])
            )


if __name__ == "__main__":
    unittest.main()
