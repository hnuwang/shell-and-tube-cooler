from __future__ import annotations

import math

from src.models import FluidProperties, HydraulicResult, MechanicalResult, ThermalResult
from src.properties import get_kerosene_props, get_water_props


def calc_reynolds(rho: float, velocity: float, diameter_m: float, mu: float) -> float:
    """Calculate Reynolds number."""
    return rho * velocity * diameter_m / mu


def calc_tube_friction_factor(re: float) -> float:
    """Calculate Darcy friction factor for smooth tubes."""
    if re < 2300.0:
        return 64.0 / re
    return 0.3164 / re**0.25


def _calc_shell_friction_factor(re: float, constant: float) -> float:
    if re < 100.0:
        return 2.0
    return constant / re**0.15


def calc_tube_pressure_drop(
    config,
    mech: MechanicalResult,
    cold_props: FluidProperties,
    cold_mass_flow_kg_s: float,
) -> tuple[float, dict]:
    """Calculate tube-side pressure drop including simple local losses."""
    tube_area = mech.tube_geometry.tube_inner_flow_area_m2
    velocity = cold_mass_flow_kg_s / (cold_props.density_kg_m3 * tube_area)
    re_value = calc_reynolds(
        cold_props.density_kg_m3,
        velocity,
        mech.tube_geometry.tube_inner_diameter_m,
        cold_props.dynamic_viscosity_pa_s,
    )
    friction_factor = calc_tube_friction_factor(re_value)
    total_length_m = mech.tube_geometry.tube_length_m * mech.tube_geometry.tube_passes
    dynamic_head = cold_props.density_kg_m3 * velocity**2 / 2.0
    major_loss = friction_factor * (total_length_m / mech.tube_geometry.tube_inner_diameter_m) * dynamic_head
    local_zeta = (
        config.tube_inlet_loss_coefficient
        + config.tube_outlet_loss_coefficient
        + max(mech.tube_geometry.tube_passes - 1, 0) * config.tube_return_loss_coefficient_per_pass
    )
    minor_loss = local_zeta * dynamic_head
    total_drop = major_loss + minor_loss
    details = {
        "tube_area_m2": tube_area,
        "tube_total_length_m": total_length_m,
        "tube_dynamic_head_pa": dynamic_head,
        "tube_major_drop_pa": major_loss,
        "tube_minor_drop_pa": minor_loss,
        "tube_local_zeta": local_zeta,
        "tube_reynolds": re_value,
        "tube_friction_factor": friction_factor,
    }
    return total_drop, details


def calc_shell_pressure_drop(
    config,
    mech: MechanicalResult,
    hot_props: FluidProperties,
    hot_mass_flow_kg_s: float,
) -> tuple[float, dict]:
    """Calculate shell-side pressure drop using a simplified Kern-style model."""
    shell_area = mech.shell_geometry.shell_crossflow_area_m2
    velocity = hot_mass_flow_kg_s / (hot_props.density_kg_m3 * shell_area)
    re_value = calc_reynolds(
        hot_props.density_kg_m3,
        velocity,
        mech.shell_geometry.shell_equivalent_diameter_m,
        hot_props.dynamic_viscosity_pa_s,
    )
    friction_factor = _calc_shell_friction_factor(re_value, config.shell_friction_factor_constant)
    baffle_count = max(int(mech.tube_geometry.tube_length_m / mech.shell_geometry.baffle_spacing_m) - 1, 1)
    dynamic_head = hot_props.density_kg_m3 * velocity**2 / 2.0
    crossflow_factor = mech.shell_geometry.shell_inner_diameter_m / mech.shell_geometry.shell_equivalent_diameter_m
    total_drop = friction_factor * (baffle_count + 1) * crossflow_factor * dynamic_head
    details = {
        "shell_area_m2": shell_area,
        "shell_dynamic_head_pa": dynamic_head,
        "shell_baffle_count": baffle_count,
        "shell_crossflow_factor": crossflow_factor,
        "shell_reynolds": re_value,
        "shell_friction_factor": friction_factor,
    }
    return total_drop, details


def run_hydraulic_design(config, thermal: ThermalResult, mech: MechanicalResult) -> HydraulicResult:
    """Run tube-side and shell-side hydraulic calculations."""
    hot_props = get_kerosene_props(thermal.hot_bulk_temp_c)
    cold_props = get_water_props(thermal.cold_bulk_temp_c)
    tube_pressure_drop_pa, tube_details = calc_tube_pressure_drop(
        config,
        mech,
        cold_props,
        thermal.cold_mass_flow_kg_s,
    )
    shell_pressure_drop_pa, shell_details = calc_shell_pressure_drop(
        config,
        mech,
        hot_props,
        config.hot_mass_flow_kg_s,
    )
    return HydraulicResult(
        tube_reynolds=tube_details["tube_reynolds"],
        shell_reynolds=shell_details["shell_reynolds"],
        tube_friction_factor=tube_details["tube_friction_factor"],
        shell_friction_factor=shell_details["shell_friction_factor"],
        tube_velocity_m_s=mech.design_velocity_tube_m_s,
        shell_velocity_m_s=mech.design_velocity_shell_m_s,
        tube_pressure_drop_pa=tube_pressure_drop_pa,
        shell_pressure_drop_pa=shell_pressure_drop_pa,
        tube_pressure_drop_ok=tube_pressure_drop_pa <= config.allowable_tube_pressure_drop_pa,
        shell_pressure_drop_ok=shell_pressure_drop_pa <= config.allowable_shell_pressure_drop_pa,
        tube_details=tube_details,
        shell_details=shell_details,
    )
