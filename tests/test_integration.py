from __future__ import annotations

import unittest

from config import DesignConfig
from main import run_design
from src.utils import DesignError


class IntegrationTests(unittest.TestCase):
    def test_default_config_runs(self) -> None:
        result = run_design(DesignConfig(print_intermediate=False))
        self.assertGreater(result.thermal_result.heat_duty_w, 0.0)
        self.assertIn("thermal", result.result_tables)
        self.assertIn("mechanical", result.result_tables)
        self.assertIn("hydraulic", result.result_tables)

    def test_hot_and_cold_duty_are_close(self) -> None:
        result = run_design(DesignConfig(print_intermediate=False))
        q_hot = result.thermal_result.heat_duty_w
        q_cold = (
            result.thermal_result.cold_mass_flow_kg_s
            * result.cold_properties.specific_heat_j_kg_k
            * (result.operating_condition.cold_outlet_temp_c - result.operating_condition.cold_inlet_temp_c)
        )
        self.assertAlmostEqual(q_hot, q_cold, delta=0.01 * q_hot)

    def test_low_allowable_pressure_drop_raises(self) -> None:
        config = DesignConfig(
            allowable_tube_pressure_drop_pa=1000.0,
            allowable_shell_pressure_drop_pa=1000.0,
            print_intermediate=False,
        )
        with self.assertRaises(DesignError):
            run_design(config)


if __name__ == "__main__":
    unittest.main()
