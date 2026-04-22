from __future__ import annotations

from pprint import pprint

from config import DesignConfig
from report_data import build_result_tables
from src.assumptions import build_assumption_set
from src.hydraulic_design import run_hydraulic_design
from src.mechanical_design import iterate_geometry
from src.models import DesignResult
from src.properties import configure_property_behavior, get_kerosene_props, get_water_props
from src.thermal_design import refine_thermal_design, run_thermal_design
from src.utils import DesignError


def run_design(config) -> DesignResult:
    """Run the complete course-design workflow."""
    configure_property_behavior(config.strict_property_range)
    thermal = run_thermal_design(config)
    mech = iterate_geometry(config, thermal)

    if config.use_u_recalculation:
        for _ in range(config.max_iterations):
            refined = refine_thermal_design(config, mech)
            margin = (mech.actual_area_m2 - refined.required_area_m2) / refined.required_area_m2
            thermal = refined
            if config.area_margin_min <= margin <= config.area_margin_max:
                break
            mech = iterate_geometry(config, thermal)

    hydraulic = run_hydraulic_design(config, thermal, mech)
    if not hydraulic.tube_pressure_drop_ok:
        raise DesignError(f"管程压降超限: {hydraulic.tube_pressure_drop_pa:.1f} Pa")
    if not hydraulic.shell_pressure_drop_ok:
        raise DesignError(f"壳程压降超限: {hydraulic.shell_pressure_drop_pa:.1f} Pa")

    hot_properties = get_kerosene_props(thermal.hot_bulk_temp_c)
    cold_properties = get_water_props(thermal.cold_bulk_temp_c)
    operating_condition = config.operating_condition
    assumptions = build_assumption_set(config)
    design = DesignResult(
        operating_condition=operating_condition,
        assumptions=assumptions,
        hot_properties=hot_properties,
        cold_properties=cold_properties,
        thermal_result=thermal,
        mechanical_result=mech,
        hydraulic_result=hydraulic,
        result_tables={},
    )
    design.result_tables = build_result_tables(design)
    return design


def main() -> None:
    """Execute the default design case and print traceable result tables."""
    config = DesignConfig()
    design = run_design(config)
    if config.print_intermediate:
        for table_name, rows in design.result_tables.items():
            print(f"\n[{table_name}]")
            pprint(rows, sort_dicts=False)


if __name__ == "__main__":
    main()
