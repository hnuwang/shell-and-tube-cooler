from __future__ import annotations

import math
import unittest

from config import DesignConfig
from src.thermal_design import (
    calc_cold_mass_flow,
    calc_correction_factor,
    calc_heat_duty,
    calc_lmtd_countercurrent,
    calc_overall_u_from_resistances,
    run_thermal_design,
)


class ThermalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = DesignConfig()

    def test_calc_heat_duty_positive(self) -> None:
        duty = calc_heat_duty(3.0, 2200.0, 150.0, 50.0)
        self.assertGreater(duty, 0.0)

    def test_calc_cold_mass_flow_energy_balance(self) -> None:
        duty = calc_heat_duty(3.8888888889, 2385.75, 150.0, 50.0)
        mass_flow = calc_cold_mass_flow(duty, 4180.85, 20.0, 30.0)
        recovered = mass_flow * 4180.85 * 10.0
        self.assertAlmostEqual(duty, recovered, places=6)

    def test_calc_lmtd_countercurrent_positive_and_finite(self) -> None:
        lmtd = calc_lmtd_countercurrent(150.0, 50.0, 20.0, 30.0)
        self.assertGreater(lmtd, 0.0)
        self.assertTrue(math.isfinite(lmtd))

    def test_calc_lmtd_handles_equal_terminal_differences(self) -> None:
        lmtd = calc_lmtd_countercurrent(100.0, 60.0, 20.0, 60.0)
        self.assertAlmostEqual(lmtd, 40.0)

    def test_correction_factor_within_reasonable_range(self) -> None:
        factor = calc_correction_factor(1, 2, 150.0, 50.0, 20.0, 30.0)
        self.assertGreater(factor, 0.0)
        self.assertLessEqual(factor, 1.0)

    def test_required_area_increases_when_u_decreases(self) -> None:
        heat_duty = 900000.0
        dt_eff = 60.0
        area_high_u = heat_duty / (400.0 * dt_eff)
        area_low_u = heat_duty / (250.0 * dt_eff)
        self.assertGreater(area_low_u, area_high_u)

    def test_overall_u_from_resistances_positive(self) -> None:
        u_value = calc_overall_u_from_resistances(self.config, 800.0, 2500.0, 0.016, 0.019, 45.0)
        self.assertGreater(u_value, 0.0)

    def test_run_thermal_design_returns_complete_result(self) -> None:
        result = run_thermal_design(self.config)
        self.assertGreater(result.heat_duty_w, 0.0)
        self.assertGreater(result.cold_mass_flow_kg_s, 0.0)
        self.assertGreater(result.effective_temp_diff_k, 0.0)
        self.assertGreater(result.required_area_m2, 0.0)

    def test_invalid_temperature_span_raises(self) -> None:
        with self.assertRaises(ValueError):
            calc_lmtd_countercurrent(60.0, 30.0, 40.0, 70.0)


if __name__ == "__main__":
    unittest.main()
