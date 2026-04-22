from __future__ import annotations

import math
import unittest

from config import DesignConfig
from src.geometry import (
    calc_shell_crossflow_area,
    calc_shell_equivalent_diameter,
    calc_tube_heat_transfer_area,
    calc_tube_inner_flow_area,
    estimate_bundle_diameter,
    estimate_shell_diameter,
)
from src.mechanical_design import iterate_geometry
from src.thermal_design import run_thermal_design
from src.utils import DesignError


class GeometryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = DesignConfig()
        self.thermal = run_thermal_design(self.config)

    def test_calc_tube_heat_transfer_area_matches_formula(self) -> None:
        area = calc_tube_heat_transfer_area(0.019, 3.0, 100)
        self.assertAlmostEqual(area, math.pi * 0.019 * 3.0 * 100)

    def test_calc_tube_inner_flow_area_matches_formula(self) -> None:
        area = calc_tube_inner_flow_area(0.016, 50)
        self.assertAlmostEqual(area, 50 * math.pi * 0.016**2 / 4.0)

    def test_bundle_and_shell_diameter_are_positive(self) -> None:
        bundle = estimate_bundle_diameter(120, 0.02375, 30.0)
        shell = estimate_shell_diameter(bundle, 0.045)
        self.assertGreater(bundle, 0.0)
        self.assertGreater(shell, bundle)

    def test_shell_crossflow_area_positive(self) -> None:
        area = calc_shell_crossflow_area(0.35, 0.14, 0.02375, 0.019)
        self.assertGreater(area, 0.0)

    def test_shell_equivalent_diameter_positive(self) -> None:
        diameter = calc_shell_equivalent_diameter(0.02375, 0.019, 30.0)
        self.assertGreater(diameter, 0.0)

    def test_iterate_geometry_returns_valid_mechanical_result(self) -> None:
        result = iterate_geometry(self.config, self.thermal)
        self.assertTrue(result.constraints_ok)
        self.assertEqual(result.tube_geometry.tube_count % self.config.tube_passes, 0)
        self.assertGreater(result.actual_area_m2, 0.0)
        self.assertGreater(result.shell_geometry.shell_crossflow_area_m2, 0.0)

    def test_more_tubes_increase_area_and_reduce_velocity_capacity(self) -> None:
        area_small = calc_tube_heat_transfer_area(0.019, 3.0, 80)
        area_large = calc_tube_heat_transfer_area(0.019, 3.0, 120)
        flow_area_small = calc_tube_inner_flow_area(0.016, 40)
        flow_area_large = calc_tube_inner_flow_area(0.016, 60)
        self.assertGreater(area_large, area_small)
        self.assertGreater(flow_area_large, flow_area_small)

    def test_iterate_geometry_raises_when_constraints_impossible(self) -> None:
        bad_config = DesignConfig(shell_velocity_min_m_s=2.0)
        with self.assertRaises(DesignError):
            iterate_geometry(bad_config, self.thermal)


if __name__ == "__main__":
    unittest.main()
