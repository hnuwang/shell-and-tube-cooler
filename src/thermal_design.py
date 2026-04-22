from __future__ import annotations

import math

from src.models import MechanicalResult, ThermalResult
from src.properties import get_kerosene_props, get_water_props
from src.utils import DesignError, ensure_positive


def calc_heat_duty(
    hot_mass_flow_kg_s: float,
    cp_hot_j_kg_k: float,
    hot_in_c: float,
    hot_out_c: float,
) -> float:
    """Calculate heat duty released by the hot stream."""
    return hot_mass_flow_kg_s * cp_hot_j_kg_k * (hot_in_c - hot_out_c)


def calc_cold_mass_flow(
    heat_duty_w: float,
    cp_cold_j_kg_k: float,
    cold_in_c: float,
    cold_out_c: float,
) -> float:
    """Calculate cold-side mass flow needed to absorb the heat duty."""
    return heat_duty_w / (cp_cold_j_kg_k * (cold_out_c - cold_in_c))


def calc_lmtd_countercurrent(
    hot_in_c: float,
    hot_out_c: float,
    cold_in_c: float,
    cold_out_c: float,
) -> float:
    """Calculate counter-current logarithmic mean temperature difference."""
    delta_t1 = hot_in_c - cold_out_c
    delta_t2 = hot_out_c - cold_in_c
    ensure_positive(delta_t1, "delta_t1")
    ensure_positive(delta_t2, "delta_t2")
    if math.isclose(delta_t1, delta_t2, rel_tol=1e-9):
        return delta_t1
    return (delta_t1 - delta_t2) / math.log(delta_t1 / delta_t2)


def calc_correction_factor(
    shell_passes: int,
    tube_passes: int,
    hot_in_c: float,
    hot_out_c: float,
    cold_in_c: float,
    cold_out_c: float,
) -> float:
    """Calculate the LMTD correction factor for one shell pass and multiple tube passes."""
    if shell_passes != 1:
        raise ValueError("Course-design implementation currently supports one shell pass only.")
    if tube_passes == 1:
        return 1.0

    r_value = (hot_in_c - hot_out_c) / (cold_out_c - cold_in_c)
    p_value = (cold_out_c - cold_in_c) / (hot_in_c - cold_in_c)
    if math.isclose(r_value, 1.0, rel_tol=1e-6):
        numerator = math.sqrt(2.0) * p_value
        denominator = math.log((1.0 - p_value) / (1.0 - p_value / 2.0))
        return numerator / denominator

    sqrt_term = math.sqrt(r_value**2 + 1.0)
    numerator = (sqrt_term / (r_value - 1.0)) * math.log((1.0 - p_value) / (1.0 - p_value * r_value))
    denominator = math.log(
        (2.0 - p_value * (r_value + 1.0 - sqrt_term))
        / (2.0 - p_value * (r_value + 1.0 + sqrt_term))
    )
    correction_factor = numerator / denominator
    if not 0.0 < correction_factor <= 1.0:
        raise DesignError(f"Calculated correction factor is invalid: F = {correction_factor:.3f}")
    return correction_factor


def estimate_overall_u(config, hot_props, cold_props) -> float:
    """Return the assumed overall heat-transfer coefficient for initial sizing."""
    del hot_props, cold_props
    return config.initial_overall_u_w_m2_k


def calc_overall_u_from_resistances(
    config,
    hot_side_h: float,
    cold_side_h: float,
    tube_inner_diameter_m: float,
    tube_outer_diameter_m: float,
    tube_wall_k_w_m_k: float,
) -> float:
    """Calculate overall heat-transfer coefficient on the outer-area basis."""
    resistance_inner_conv = tube_outer_diameter_m / (tube_inner_diameter_m * cold_side_h)
    resistance_inner_fouling = (
        config.fouling_resistance_tube_m2_k_w * tube_outer_diameter_m / tube_inner_diameter_m
    )
    resistance_wall = (
        tube_outer_diameter_m
        * math.log(tube_outer_diameter_m / tube_inner_diameter_m)
        / (2.0 * tube_wall_k_w_m_k)
    )
    resistance_outer_fouling = config.fouling_resistance_shell_m2_k_w
    resistance_outer_conv = 1.0 / hot_side_h
    total_resistance = (
        resistance_inner_conv
        + resistance_inner_fouling
        + resistance_wall
        + resistance_outer_fouling
        + resistance_outer_conv
    )
    return 1.0 / total_resistance


def _calc_tube_side_coefficient(cold_mass_flow_kg_s: float, mech: MechanicalResult, cold_props) -> tuple[float, float]:
    area = mech.tube_geometry.tube_inner_flow_area_m2
    velocity = cold_mass_flow_kg_s / (cold_props.density_kg_m3 * area)
    re_value = cold_props.density_kg_m3 * velocity * mech.tube_geometry.tube_inner_diameter_m / cold_props.dynamic_viscosity_pa_s
    pr_value = cold_props.prandtl
    conductivity = cold_props.thermal_conductivity_w_m_k
    diameter = mech.tube_geometry.tube_inner_diameter_m

    if re_value < 2300.0:
        nusselt = 3.66
    else:
        nusselt = 0.023 * re_value**0.8 * pr_value**0.4
    return nusselt * conductivity / diameter, velocity


def _calc_shell_side_coefficient(hot_mass_flow_kg_s: float, mech: MechanicalResult, hot_props) -> tuple[float, float]:
    shell_area = mech.shell_geometry.shell_crossflow_area_m2
    velocity = hot_mass_flow_kg_s / (hot_props.density_kg_m3 * shell_area)
    re_value = hot_props.density_kg_m3 * velocity * mech.shell_geometry.shell_equivalent_diameter_m / hot_props.dynamic_viscosity_pa_s
    pr_value = hot_props.prandtl
    conductivity = hot_props.thermal_conductivity_w_m_k
    diameter = mech.shell_geometry.shell_equivalent_diameter_m

    if re_value < 100.0:
        nusselt = 0.9 * re_value**0.4 * pr_value**0.36
    else:
        nusselt = 0.36 * re_value**0.55 * pr_value ** (1.0 / 3.0)
    return nusselt * conductivity / diameter, velocity


def _build_base_thermal_result(config) -> ThermalResult:
    hot_bulk_temp_c = 0.5 * (config.hot_inlet_temp_c + config.hot_outlet_temp_c)
    cold_bulk_temp_c = 0.5 * (config.cold_inlet_temp_c + config.cold_outlet_temp_c)
    hot_props = get_kerosene_props(hot_bulk_temp_c)
    cold_props = get_water_props(cold_bulk_temp_c)

    heat_duty_w = calc_heat_duty(
        config.hot_mass_flow_kg_s,
        hot_props.specific_heat_j_kg_k,
        config.hot_inlet_temp_c,
        config.hot_outlet_temp_c,
    )
    cold_mass_flow_kg_s = calc_cold_mass_flow(
        heat_duty_w,
        cold_props.specific_heat_j_kg_k,
        config.cold_inlet_temp_c,
        config.cold_outlet_temp_c,
    )
    lmtd_k = calc_lmtd_countercurrent(
        config.hot_inlet_temp_c,
        config.hot_outlet_temp_c,
        config.cold_inlet_temp_c,
        config.cold_outlet_temp_c,
    )
    correction_factor = calc_correction_factor(
        config.shell_passes,
        config.tube_passes,
        config.hot_inlet_temp_c,
        config.hot_outlet_temp_c,
        config.cold_inlet_temp_c,
        config.cold_outlet_temp_c,
    )
    effective_temp_diff_k = correction_factor * lmtd_k
    overall_u_assumed = estimate_overall_u(config, hot_props, cold_props)
    required_area_m2 = heat_duty_w / (overall_u_assumed * effective_temp_diff_k)
    return ThermalResult(
        heat_duty_w=heat_duty_w,
        cold_mass_flow_kg_s=cold_mass_flow_kg_s,
        lmtd_k=lmtd_k,
        correction_factor=correction_factor,
        effective_temp_diff_k=effective_temp_diff_k,
        overall_u_assumed_w_m2_k=overall_u_assumed,
        overall_u_calculated_w_m2_k=overall_u_assumed,
        required_area_m2=required_area_m2,
        hot_bulk_temp_c=hot_bulk_temp_c,
        cold_bulk_temp_c=cold_bulk_temp_c,
        hot_film_coefficient_w_m2_k=0.0,
        cold_film_coefficient_w_m2_k=0.0,
    )


def run_thermal_design(config) -> ThermalResult:
    """Run the initial thermal sizing step with the assumed overall coefficient."""
    return _build_base_thermal_result(config)


def refine_thermal_design(config, mech: MechanicalResult) -> ThermalResult:
    """Recalculate film coefficients and required area after geometry selection."""
    thermal = _build_base_thermal_result(config)
    hot_props = get_kerosene_props(thermal.hot_bulk_temp_c)
    cold_props = get_water_props(thermal.cold_bulk_temp_c)
    cold_side_h, _ = _calc_tube_side_coefficient(thermal.cold_mass_flow_kg_s, mech, cold_props)
    hot_side_h, _ = _calc_shell_side_coefficient(config.hot_mass_flow_kg_s, mech, hot_props)
    overall_u = calc_overall_u_from_resistances(
        config,
        hot_side_h=hot_side_h,
        cold_side_h=cold_side_h,
        tube_inner_diameter_m=mech.tube_geometry.tube_inner_diameter_m,
        tube_outer_diameter_m=mech.tube_geometry.tube_outer_diameter_m,
        tube_wall_k_w_m_k=config.tube_wall_thermal_conductivity_w_m_k,
    )
    required_area_m2 = thermal.heat_duty_w / (overall_u * thermal.effective_temp_diff_k)
    return ThermalResult(
        heat_duty_w=thermal.heat_duty_w,
        cold_mass_flow_kg_s=thermal.cold_mass_flow_kg_s,
        lmtd_k=thermal.lmtd_k,
        correction_factor=thermal.correction_factor,
        effective_temp_diff_k=thermal.effective_temp_diff_k,
        overall_u_assumed_w_m2_k=thermal.overall_u_assumed_w_m2_k,
        overall_u_calculated_w_m2_k=overall_u,
        required_area_m2=required_area_m2,
        hot_bulk_temp_c=thermal.hot_bulk_temp_c,
        cold_bulk_temp_c=thermal.cold_bulk_temp_c,
        hot_film_coefficient_w_m2_k=hot_side_h,
        cold_film_coefficient_w_m2_k=cold_side_h,
    )
