from __future__ import annotations

import unittest

from config import DesignConfig
from src.hydraulic_design import calc_shell_pressure_drop, calc_tube_pressure_drop, run_hydraulic_design
from src.properties import get_kerosene_props, get_water_props
from src.mechanical_design import iterate_geometry
from src.thermal_design import run_thermal_design


class HydraulicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = DesignConfig()
        self.thermal = run_thermal_design(self.config)
        self.mech = iterate_geometry(self.config, self.thermal)
        self.hot_props = get_kerosene_props(self.thermal.hot_bulk_temp_c)
        self.cold_props = get_water_props(self.thermal.cold_bulk_temp_c)

    def test_reynolds_and_pressure_drop_are_positive(self) -> None:
        result = run_hydraulic_design(self.config, self.thermal, self.mech)
        self.assertGreater(result.tube_reynolds, 0.0)
        self.assertGreater(result.shell_reynolds, 0.0)
        self.assertGreater(result.tube_pressure_drop_pa, 0.0)
        self.assertGreater(result.shell_pressure_drop_pa, 0.0)

    def test_higher_flow_increases_tube_pressure_drop(self) -> None:
        base_drop, _ = calc_tube_pressure_drop(self.config, self.mech, self.cold_props, self.thermal.cold_mass_flow_kg_s)
        higher_drop, _ = calc_tube_pressure_drop(self.config, self.mech, self.cold_props, self.thermal.cold_mass_flow_kg_s * 1.2)
        self.assertGreater(higher_drop, base_drop)

    def test_longer_tube_length_increases_tube_pressure_drop(self) -> None:
        short_mech = self.mech
        long_config = DesignConfig(tube_length_candidates_m=[6.0])
        long_thermal = run_thermal_design(long_config)
        long_mech = iterate_geometry(long_config, long_thermal)
        short_drop, _ = calc_tube_pressure_drop(self.config, short_mech, self.cold_props, self.thermal.cold_mass_flow_kg_s)
        long_drop, _ = calc_tube_pressure_drop(long_config, long_mech, self.cold_props, long_thermal.cold_mass_flow_kg_s)
        self.assertGreater(long_drop, short_drop)

    def test_higher_flow_increases_shell_pressure_drop(self) -> None:
        base_drop, _ = calc_shell_pressure_drop(self.config, self.mech, self.hot_props, self.config.hot_mass_flow_kg_s)
        higher_drop, _ = calc_shell_pressure_drop(self.config, self.mech, self.hot_props, self.config.hot_mass_flow_kg_s * 1.2)
        self.assertGreater(higher_drop, base_drop)


if __name__ == "__main__":
    unittest.main()
