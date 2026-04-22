from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from config import DesignConfig


class DesignConfigPayload(BaseModel):
    hot_mass_flow_kg_s: float = 14000.0 / 3600.0
    hot_inlet_temp_c: float = 150.0
    hot_outlet_temp_c: float = 50.0
    cold_inlet_temp_c: float = 20.0
    cold_outlet_temp_c: float = 30.0
    hot_pressure_mpa: float = 0.1
    cold_pressure_mpa: float = 0.3
    shell_passes: int = 1
    tube_passes: int = 2
    tube_outer_diameter_m: float = 0.019
    tube_inner_diameter_m: float = 0.016
    tube_length_candidates_m: list[float] = Field(default_factory=lambda: [1.5, 2.0, 3.0, 4.5, 6.0])
    pitch_ratio: float = 1.25
    layout_angle_deg: float = 30.0
    shell_clearance_m: float = 0.045
    baffle_spacing_ratio: float = 0.4
    baffle_spacing_min_m: float = 0.08
    baffle_spacing_max_m: float = 0.30
    baffle_cut_ratio: float = 0.25
    tube_wall_thermal_conductivity_w_m_k: float = 45.0
    fouling_resistance_tube_m2_k_w: float = 0.0002
    fouling_resistance_shell_m2_k_w: float = 0.00035
    initial_overall_u_w_m2_k: float = 300.0
    use_u_recalculation: bool = True
    tube_velocity_min_m_s: float = 0.5
    tube_velocity_max_m_s: float = 2.5
    shell_velocity_min_m_s: float = 0.3
    shell_velocity_max_m_s: float = 1.5
    allowable_tube_pressure_drop_pa: float = 50000.0
    allowable_shell_pressure_drop_pa: float = 40000.0
    area_margin_min: float = 0.05
    area_margin_max: float = 0.25
    max_iterations: int = 20
    strict_property_range: bool = True
    print_intermediate: bool = False
    export_markdown_tables: bool = True
    tube_inlet_loss_coefficient: float = 1.5
    tube_return_loss_coefficient_per_pass: float = 1.0
    tube_outlet_loss_coefficient: float = 1.0
    shell_friction_factor_constant: float = 0.24

    def to_design_config(self) -> DesignConfig:
        """Convert API payload to the internal DesignConfig object."""
        return DesignConfig.from_mapping(self.model_dump())


class ApiMessage(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    message: str


class ConfigResponse(BaseModel):
    config: dict[str, Any]


class DesignRunResponse(BaseModel):
    design: dict[str, Any]


class ImportConfigResponse(BaseModel):
    config: dict[str, Any]
    source: str
