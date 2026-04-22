from __future__ import annotations

import math


def calc_tube_heat_transfer_area(
    tube_outer_diameter_m: float,
    tube_length_m: float,
    tube_count: int,
) -> float:
    """Calculate total outer heat-transfer area of the tube bundle."""
    return math.pi * tube_outer_diameter_m * tube_length_m * tube_count


def calc_tube_inner_flow_area(tube_inner_diameter_m: float, tubes_per_pass: int) -> float:
    """Calculate the total inner flow area for one tube pass."""
    return tubes_per_pass * math.pi * tube_inner_diameter_m**2 / 4.0


def estimate_bundle_diameter(tube_count: int, pitch_m: float, layout_angle_deg: float) -> float:
    """Estimate bundle diameter from packing density for common tube layouts."""
    if layout_angle_deg in (30.0, 60.0):
        packing_factor = 0.87
    elif layout_angle_deg == 45.0:
        packing_factor = 0.80
    else:
        packing_factor = 0.70
    return pitch_m * math.sqrt(tube_count / packing_factor)


def estimate_shell_diameter(bundle_diameter_m: float, clearance_m: float) -> float:
    """Estimate shell inner diameter from bundle diameter and assembly clearance."""
    return bundle_diameter_m + clearance_m


def calc_shell_crossflow_area(
    shell_inner_diameter_m: float,
    baffle_spacing_m: float,
    pitch_m: float,
    tube_outer_diameter_m: float,
) -> float:
    """Estimate shell-side crossflow area using a Kern-style free-area expression."""
    free_area_ratio = max((pitch_m - tube_outer_diameter_m) / pitch_m, 1e-6)
    return shell_inner_diameter_m * baffle_spacing_m * free_area_ratio


def calc_shell_equivalent_diameter(
    pitch_m: float,
    tube_outer_diameter_m: float,
    layout_angle_deg: float,
) -> float:
    """Calculate shell-side equivalent diameter for triangular or square layouts."""
    if layout_angle_deg in (30.0, 60.0):
        return 1.10 * (pitch_m**2 - 0.917 * tube_outer_diameter_m**2) / tube_outer_diameter_m
    return 1.27 * (pitch_m**2 - 0.785 * tube_outer_diameter_m**2) / tube_outer_diameter_m
