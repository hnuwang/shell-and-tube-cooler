from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OperatingCondition:
    hot_mass_flow_kg_s: float
    hot_inlet_temp_c: float
    hot_outlet_temp_c: float
    cold_inlet_temp_c: float
    cold_outlet_temp_c: float
    hot_pressure_mpa: float
    cold_pressure_mpa: float


@dataclass(slots=True)
class FluidProperties:
    temperature_k: float
    density_kg_m3: float
    dynamic_viscosity_pa_s: float
    specific_heat_j_kg_k: float
    thermal_conductivity_w_m_k: float
    prandtl: float
    kinematic_viscosity_m2_s: float
    thermal_diffusivity_m2_s: float


@dataclass(slots=True)
class ThermalResult:
    heat_duty_w: float
    cold_mass_flow_kg_s: float
    lmtd_k: float
    correction_factor: float
    effective_temp_diff_k: float
    overall_u_assumed_w_m2_k: float
    overall_u_calculated_w_m2_k: float
    required_area_m2: float
    hot_bulk_temp_c: float
    cold_bulk_temp_c: float
    hot_film_coefficient_w_m2_k: float
    cold_film_coefficient_w_m2_k: float


@dataclass(slots=True)
class TubeGeometry:
    tube_outer_diameter_m: float
    tube_inner_diameter_m: float
    tube_length_m: float
    tube_count: int
    tube_passes: int
    tubes_per_pass: int
    layout_angle_deg: float
    pitch_m: float
    area_per_tube_m2: float
    total_area_m2: float
    tube_inner_flow_area_m2: float


@dataclass(slots=True)
class ShellGeometry:
    shell_inner_diameter_m: float
    baffle_spacing_m: float
    baffle_cut_ratio: float
    bundle_diameter_m: float
    shell_crossflow_area_m2: float
    shell_equivalent_diameter_m: float


@dataclass(slots=True)
class MechanicalResult:
    tube_geometry: TubeGeometry
    shell_geometry: ShellGeometry
    actual_area_m2: float
    area_margin_ratio: float
    design_velocity_tube_m_s: float
    design_velocity_shell_m_s: float
    candidate_id: str
    constraints_ok: bool


@dataclass(slots=True)
class HydraulicResult:
    tube_reynolds: float
    shell_reynolds: float
    tube_friction_factor: float
    shell_friction_factor: float
    tube_velocity_m_s: float
    shell_velocity_m_s: float
    tube_pressure_drop_pa: float
    shell_pressure_drop_pa: float
    tube_pressure_drop_ok: bool
    shell_pressure_drop_ok: bool
    tube_details: dict[str, Any] = field(default_factory=dict)
    shell_details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AssumptionSet:
    flow_arrangement: str
    shell_passes: int
    tube_passes: int
    tube_outer_diameter_m: float
    tube_inner_diameter_m: float
    tube_length_candidates_m: list[float]
    pitch_ratio: float
    layout_angle_deg: float
    shell_clearance_m: float
    baffle_spacing_ratio: float
    baffle_spacing_limits_m: tuple[float, float]
    baffle_cut_ratio: float
    tube_wall_thermal_conductivity_w_m_k: float
    fouling_resistance_tube_m2_k_w: float
    fouling_resistance_shell_m2_k_w: float
    initial_overall_u_w_m2_k: float
    use_u_recalculation: bool
    tube_velocity_limits_m_s: tuple[float, float]
    shell_velocity_limits_m_s: tuple[float, float]
    allowable_tube_pressure_drop_pa: float
    allowable_shell_pressure_drop_pa: float
    area_margin_limits: tuple[float, float]
    max_iterations: int
    strict_property_range: bool


@dataclass(slots=True)
class DesignResult:
    operating_condition: OperatingCondition
    assumptions: AssumptionSet
    hot_properties: FluidProperties
    cold_properties: FluidProperties
    thermal_result: ThermalResult
    mechanical_result: MechanicalResult
    hydraulic_result: HydraulicResult
    result_tables: dict[str, list[dict[str, Any]]]
