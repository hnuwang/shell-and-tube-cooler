from __future__ import annotations

import math

from src.geometry import (
    calc_shell_crossflow_area,
    calc_shell_equivalent_diameter,
    calc_tube_heat_transfer_area,
    calc_tube_inner_flow_area,
    estimate_bundle_diameter,
    estimate_shell_diameter,
)
from src.models import MechanicalResult, ShellGeometry, ThermalResult, TubeGeometry
from src.properties import get_kerosene_props, get_water_props
from src.utils import DesignError, clamp


def check_area_match(required_area_m2: float, actual_area_m2: float, tolerance: float) -> bool:
    """Check whether actual area lies within an allowed positive margin."""
    if actual_area_m2 < required_area_m2:
        return False
    return (actual_area_m2 - required_area_m2) / required_area_m2 <= tolerance


def _build_candidate(config, thermal: ThermalResult, tube_length_m: float, tube_count: int) -> MechanicalResult:
    pitch_m = config.pitch_ratio * config.tube_outer_diameter_m
    tubes_per_pass = tube_count // config.tube_passes
    area_per_tube_m2 = calc_tube_heat_transfer_area(config.tube_outer_diameter_m, tube_length_m, 1)
    total_area_m2 = calc_tube_heat_transfer_area(config.tube_outer_diameter_m, tube_length_m, tube_count)
    tube_inner_flow_area_m2 = calc_tube_inner_flow_area(config.tube_inner_diameter_m, tubes_per_pass)
    bundle_diameter_m = estimate_bundle_diameter(tube_count, pitch_m, config.layout_angle_deg)
    shell_inner_diameter_m = estimate_shell_diameter(bundle_diameter_m, config.shell_clearance_m)
    baffle_spacing_m = clamp(
        config.baffle_spacing_ratio * shell_inner_diameter_m,
        config.baffle_spacing_min_m,
        config.baffle_spacing_max_m,
    )
    shell_crossflow_area_m2 = calc_shell_crossflow_area(
        shell_inner_diameter_m,
        baffle_spacing_m,
        pitch_m,
        config.tube_outer_diameter_m,
    )
    shell_equivalent_diameter_m = calc_shell_equivalent_diameter(
        pitch_m,
        config.tube_outer_diameter_m,
        config.layout_angle_deg,
    )

    hot_props = get_kerosene_props(thermal.hot_bulk_temp_c)
    cold_props = get_water_props(thermal.cold_bulk_temp_c)
    design_velocity_tube_m_s = thermal.cold_mass_flow_kg_s / (cold_props.density_kg_m3 * tube_inner_flow_area_m2)
    design_velocity_shell_m_s = config.hot_mass_flow_kg_s / (hot_props.density_kg_m3 * shell_crossflow_area_m2)
    area_margin_ratio = (total_area_m2 - thermal.required_area_m2) / thermal.required_area_m2
    constraints_ok = (
        config.area_margin_min <= area_margin_ratio <= config.area_margin_max
        and config.tube_velocity_min_m_s <= design_velocity_tube_m_s <= config.tube_velocity_max_m_s
        and config.shell_velocity_min_m_s <= design_velocity_shell_m_s <= config.shell_velocity_max_m_s
    )

    tube_geometry = TubeGeometry(
        tube_outer_diameter_m=config.tube_outer_diameter_m,
        tube_inner_diameter_m=config.tube_inner_diameter_m,
        tube_length_m=tube_length_m,
        tube_count=tube_count,
        tube_passes=config.tube_passes,
        tubes_per_pass=tubes_per_pass,
        layout_angle_deg=config.layout_angle_deg,
        pitch_m=pitch_m,
        area_per_tube_m2=area_per_tube_m2,
        total_area_m2=total_area_m2,
        tube_inner_flow_area_m2=tube_inner_flow_area_m2,
    )
    shell_geometry = ShellGeometry(
        shell_inner_diameter_m=shell_inner_diameter_m,
        baffle_spacing_m=baffle_spacing_m,
        baffle_cut_ratio=config.baffle_cut_ratio,
        bundle_diameter_m=bundle_diameter_m,
        shell_crossflow_area_m2=shell_crossflow_area_m2,
        shell_equivalent_diameter_m=shell_equivalent_diameter_m,
    )
    return MechanicalResult(
        tube_geometry=tube_geometry,
        shell_geometry=shell_geometry,
        actual_area_m2=total_area_m2,
        area_margin_ratio=area_margin_ratio,
        design_velocity_tube_m_s=design_velocity_tube_m_s,
        design_velocity_shell_m_s=design_velocity_shell_m_s,
        candidate_id=f"L{tube_length_m:.2f}_N{tube_count}",
        constraints_ok=constraints_ok,
    )


def select_initial_geometry(config, thermal: ThermalResult) -> MechanicalResult:
    """Generate the minimum-tube-count candidate for the shortest viable tube length."""
    tube_length_m = max(config.tube_length_candidates_m)
    area_per_tube = calc_tube_heat_transfer_area(config.tube_outer_diameter_m, tube_length_m, 1)
    tube_count = math.ceil(thermal.required_area_m2 / area_per_tube)
    remainder = tube_count % config.tube_passes
    if remainder:
        tube_count += config.tube_passes - remainder
    return _build_candidate(config, thermal, tube_length_m, tube_count)


def iterate_geometry(config, thermal: ThermalResult) -> MechanicalResult:
    """Iterate over tube lengths and counts until an acceptable course-design candidate is found."""
    best_candidate: MechanicalResult | None = None
    failure_reasons: list[str] = []

    for tube_length_m in sorted(config.tube_length_candidates_m):
        area_per_tube = calc_tube_heat_transfer_area(config.tube_outer_diameter_m, tube_length_m, 1)
        tube_count = math.ceil(thermal.required_area_m2 * (1.0 + config.area_margin_min) / area_per_tube)
        remainder = tube_count % config.tube_passes
        if remainder:
            tube_count += config.tube_passes - remainder

        for _ in range(config.max_iterations):
            candidate = _build_candidate(config, thermal, tube_length_m, tube_count)
            if best_candidate is None or candidate.area_margin_ratio < best_candidate.area_margin_ratio:
                best_candidate = candidate
            if candidate.constraints_ok:
                return candidate

            reasons = []
            if candidate.area_margin_ratio < config.area_margin_min:
                reasons.append("面积不足")
            if candidate.area_margin_ratio > config.area_margin_max:
                reasons.append("面积裕量过大")
            if candidate.design_velocity_tube_m_s > config.tube_velocity_max_m_s:
                reasons.append("管内流速过高")
            if candidate.design_velocity_tube_m_s < config.tube_velocity_min_m_s:
                reasons.append("管内流速过低")
            if candidate.design_velocity_shell_m_s > config.shell_velocity_max_m_s:
                reasons.append("壳程流速过高")
            if candidate.design_velocity_shell_m_s < config.shell_velocity_min_m_s:
                reasons.append("壳程流速过低")
            failure_reasons.append(f"{candidate.candidate_id}: {'/'.join(reasons)}")
            tube_count += config.tube_passes

    detail = failure_reasons[-5:] if failure_reasons else ["未生成候选方案"]
    raise DesignError("几何筛选失败: " + "; ".join(detail))
