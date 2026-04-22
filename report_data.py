from __future__ import annotations

from src.models import DesignResult, OperatingCondition


def build_input_table(config) -> list[dict]:
    """Build the input-condition summary table."""
    return [
        {"参数": "煤油质量流量", "值": config.hot_mass_flow_kg_s, "单位": "kg/s"},
        {"参数": "煤油入口温度", "值": config.hot_inlet_temp_c, "单位": "℃"},
        {"参数": "煤油出口温度", "值": config.hot_outlet_temp_c, "单位": "℃"},
        {"参数": "冷却水入口温度", "值": config.cold_inlet_temp_c, "单位": "℃"},
        {"参数": "冷却水出口温度", "值": config.cold_outlet_temp_c, "单位": "℃"},
        {"参数": "煤油压力", "值": config.hot_pressure_mpa, "单位": "MPa"},
        {"参数": "冷却水压力", "值": config.cold_pressure_mpa, "单位": "MPa"},
    ]


def _build_input_table_from_operating_condition(condition: OperatingCondition) -> list[dict]:
    return [
        {"参数": "煤油质量流量", "值": condition.hot_mass_flow_kg_s, "单位": "kg/s"},
        {"参数": "煤油入口温度", "值": condition.hot_inlet_temp_c, "单位": "℃"},
        {"参数": "煤油出口温度", "值": condition.hot_outlet_temp_c, "单位": "℃"},
        {"参数": "冷却水入口温度", "值": condition.cold_inlet_temp_c, "单位": "℃"},
        {"参数": "冷却水出口温度", "值": condition.cold_outlet_temp_c, "单位": "℃"},
        {"参数": "煤油压力", "值": condition.hot_pressure_mpa, "单位": "MPa"},
        {"参数": "冷却水压力", "值": condition.cold_pressure_mpa, "单位": "MPa"},
    ]


def build_property_table(hot_props, cold_props) -> list[dict]:
    """Build a compact hot/cold property comparison table."""
    return [
        {"物性": "密度", "煤油": hot_props.density_kg_m3, "冷却水": cold_props.density_kg_m3, "单位": "kg/m3"},
        {"物性": "动力黏度", "煤油": hot_props.dynamic_viscosity_pa_s, "冷却水": cold_props.dynamic_viscosity_pa_s, "单位": "Pa·s"},
        {"物性": "定压比热", "煤油": hot_props.specific_heat_j_kg_k, "冷却水": cold_props.specific_heat_j_kg_k, "单位": "J/(kg·K)"},
        {"物性": "导热系数", "煤油": hot_props.thermal_conductivity_w_m_k, "冷却水": cold_props.thermal_conductivity_w_m_k, "单位": "W/(m·K)"},
        {"物性": "Pr数", "煤油": hot_props.prandtl, "冷却水": cold_props.prandtl, "单位": "-"},
    ]


def build_result_tables(design: DesignResult) -> dict[str, list[dict]]:
    """Build markdown-friendly tables from the final design result."""
    thermal = design.thermal_result
    mech = design.mechanical_result
    hydraulic = design.hydraulic_result
    return {
        "input": _build_input_table_from_operating_condition(design.operating_condition),
        "properties": build_property_table(design.hot_properties, design.cold_properties),
        "thermal": [
            {"项目": "热负荷", "值": thermal.heat_duty_w, "单位": "W"},
            {"项目": "冷却水流量", "值": thermal.cold_mass_flow_kg_s, "单位": "kg/s"},
            {"项目": "LMTD", "值": thermal.lmtd_k, "单位": "K"},
            {"项目": "修正系数 F", "值": thermal.correction_factor, "单位": "-"},
            {"项目": "有效温差", "值": thermal.effective_temp_diff_k, "单位": "K"},
            {"项目": "U_assumed", "值": thermal.overall_u_assumed_w_m2_k, "单位": "W/(m2·K)"},
            {"项目": "U_calculated", "值": thermal.overall_u_calculated_w_m2_k, "单位": "W/(m2·K)"},
            {"项目": "煤油侧膜系数", "值": thermal.hot_film_coefficient_w_m2_k, "单位": "W/(m2·K)"},
            {"项目": "水侧膜系数", "值": thermal.cold_film_coefficient_w_m2_k, "单位": "W/(m2·K)"},
            {"项目": "所需面积", "值": thermal.required_area_m2, "单位": "m2"},
        ],
        "mechanical": [
            {"项目": "候选编号", "值": mech.candidate_id, "单位": "-"},
            {"项目": "管长", "值": mech.tube_geometry.tube_length_m, "单位": "m"},
            {"项目": "总管数", "值": mech.tube_geometry.tube_count, "单位": "根"},
            {"项目": "每程管数", "值": mech.tube_geometry.tubes_per_pass, "单位": "根"},
            {"项目": "实际面积", "值": mech.actual_area_m2, "单位": "m2"},
            {"项目": "面积裕量", "值": mech.area_margin_ratio, "单位": "-"},
            {"项目": "管束直径", "值": mech.shell_geometry.bundle_diameter_m, "单位": "m"},
            {"项目": "壳体内径", "值": mech.shell_geometry.shell_inner_diameter_m, "单位": "m"},
            {"项目": "挡板间距", "值": mech.shell_geometry.baffle_spacing_m, "单位": "m"},
            {"项目": "壳程横流面积", "值": mech.shell_geometry.shell_crossflow_area_m2, "单位": "m2"},
            {"项目": "壳程当量直径", "值": mech.shell_geometry.shell_equivalent_diameter_m, "单位": "m"},
            {"项目": "结构约束是否合格", "值": "是" if mech.constraints_ok else "否", "单位": "-"},
        ],
        "hydraulic": [
            {"项目": "管程速度", "值": hydraulic.tube_velocity_m_s, "单位": "m/s"},
            {"项目": "壳程速度", "值": hydraulic.shell_velocity_m_s, "单位": "m/s"},
            {"项目": "管程 Re", "值": hydraulic.tube_reynolds, "单位": "-"},
            {"项目": "壳程 Re", "值": hydraulic.shell_reynolds, "单位": "-"},
            {"项目": "管程摩擦因子", "值": hydraulic.tube_friction_factor, "单位": "-"},
            {"项目": "壳程摩擦因子", "值": hydraulic.shell_friction_factor, "单位": "-"},
            {"项目": "管程压降", "值": hydraulic.tube_pressure_drop_pa, "单位": "Pa"},
            {"项目": "壳程压降", "值": hydraulic.shell_pressure_drop_pa, "单位": "Pa"},
            {"项目": "管程压降是否合格", "值": "是" if hydraulic.tube_pressure_drop_ok else "否", "单位": "-"},
            {"项目": "壳程压降是否合格", "值": "是" if hydraulic.shell_pressure_drop_ok else "否", "单位": "-"},
        ],
    }
