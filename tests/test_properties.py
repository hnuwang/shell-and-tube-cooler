from __future__ import annotations

import math
import warnings
import unittest

from config import DesignConfig
from src.properties import (
    configure_property_behavior,
    interpolate_property,
    load_property_table,
)
from src.utils import celsius_to_kelvin


class PropertyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = DesignConfig()
        self.kerosene_table = load_property_table(str(self.config.kerosene_csv_path))
        self.water_table = load_property_table(str(self.config.water_csv_path))
        configure_property_behavior(True)

    def test_exact_table_point_returns_exact_value(self) -> None:
        props = interpolate_property(self.kerosene_table, 320.0)
        self.assertAlmostEqual(props.density_kg_m3, 803.0)
        self.assertAlmostEqual(props.dynamic_viscosity_pa_s, 0.000993)

    def test_midpoint_interpolation_is_linear(self) -> None:
        props = interpolate_property(self.water_table, 310.0)
        self.assertAlmostEqual(props.density_kg_m3, (996.62 + 989.43) / 2.0)
        self.assertAlmostEqual(props.specific_heat_j_kg_k, (4179.0 + 4180.0) / 2.0)

    def test_out_of_range_strict_raises(self) -> None:
        configure_property_behavior(True)
        with self.assertRaises(ValueError):
            interpolate_property(self.water_table, 270.0)

    def test_out_of_range_non_strict_clips_with_warning(self) -> None:
        configure_property_behavior(False)
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            props = interpolate_property(self.water_table, 270.0)
        self.assertEqual(props.temperature_k, 280.0)
        self.assertTrue(captured)

    def test_unit_consistency_for_csv_values(self) -> None:
        props = interpolate_property(self.water_table, celsius_to_kelvin(26.85))
        self.assertTrue(math.isclose(props.dynamic_viscosity_pa_s, 0.0008544, rel_tol=1e-6))
        self.assertTrue(math.isclose(props.kinematic_viscosity_m2_s, props.dynamic_viscosity_pa_s / props.density_kg_m3, rel_tol=1e-4))


if __name__ == "__main__":
    unittest.main()
