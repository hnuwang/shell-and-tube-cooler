from __future__ import annotations

from src.models import AssumptionSet


def build_assumption_set(config) -> AssumptionSet:
    """Build a grouped assumption summary from the design configuration."""
    return AssumptionSet(
        flow_arrangement="tube side water, shell side kerosene",
        shell_passes=config.shell_passes,
        tube_passes=config.tube_passes,
        tube_outer_diameter_m=config.tube_outer_diameter_m,
        tube_inner_diameter_m=config.tube_inner_diameter_m,
        tube_length_candidates_m=list(config.tube_length_candidates_m),
        pitch_ratio=config.pitch_ratio,
        layout_angle_deg=config.layout_angle_deg,
        shell_clearance_m=config.shell_clearance_m,
        baffle_spacing_ratio=config.baffle_spacing_ratio,
        baffle_spacing_limits_m=(config.baffle_spacing_min_m, config.baffle_spacing_max_m),
        baffle_cut_ratio=config.baffle_cut_ratio,
        tube_wall_thermal_conductivity_w_m_k=config.tube_wall_thermal_conductivity_w_m_k,
        fouling_resistance_tube_m2_k_w=config.fouling_resistance_tube_m2_k_w,
        fouling_resistance_shell_m2_k_w=config.fouling_resistance_shell_m2_k_w,
        initial_overall_u_w_m2_k=config.initial_overall_u_w_m2_k,
        use_u_recalculation=config.use_u_recalculation,
        tube_velocity_limits_m_s=(config.tube_velocity_min_m_s, config.tube_velocity_max_m_s),
        shell_velocity_limits_m_s=(config.shell_velocity_min_m_s, config.shell_velocity_max_m_s),
        allowable_tube_pressure_drop_pa=config.allowable_tube_pressure_drop_pa,
        allowable_shell_pressure_drop_pa=config.allowable_shell_pressure_drop_pa,
        area_margin_limits=(config.area_margin_min, config.area_margin_max),
        max_iterations=config.max_iterations,
        strict_property_range=config.strict_property_range,
    )
