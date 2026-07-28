import unittest

from prism_slm.contracts import ChannelSpec, PlatformSpec, SemanticGroup


class ContractTests(unittest.TestCase):
    def test_platform_reports_available_semantic_groups(self) -> None:
        platform = PlatformSpec.from_channels(
            platform_id="EPYC_LINUX",
            architecture="x86_64",
            operating_system="Ubuntu",
            observability="host",
            channels=[
                ChannelSpec(
                    native_name="cpu_utilization",
                    unit="percent",
                    semantic_group=SemanticGroup.COMPUTE,
                    source="procfs",
                    sampling_period_seconds=1.0,
                ),
                ChannelSpec(
                    native_name="memory_available",
                    unit="bytes",
                    semantic_group=SemanticGroup.MEMORY,
                    source="procfs",
                    sampling_period_seconds=1.0,
                ),
            ],
        )
        self.assertEqual(
            platform.available_groups,
            {SemanticGroup.COMPUTE, SemanticGroup.MEMORY},
        )

    def test_duplicate_native_channels_are_rejected(self) -> None:
        channel = ChannelSpec(
            native_name="temperature",
            unit="celsius",
            semantic_group=SemanticGroup.THERMAL_POWER,
            source="lm_sensors",
            sampling_period_seconds=1.0,
        )
        with self.assertRaisesRegex(ValueError, "unique"):
            PlatformSpec.from_channels(
                platform_id="EPYC_LINUX",
                architecture="x86_64",
                operating_system="Ubuntu",
                observability="host",
                channels=[channel, channel],
            )

    def test_nonpositive_sampling_period_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            ChannelSpec(
                native_name="power",
                unit="watts",
                semantic_group=SemanticGroup.THERMAL_POWER,
                source="collector",
                sampling_period_seconds=0,
            )


if __name__ == "__main__":
    unittest.main()
