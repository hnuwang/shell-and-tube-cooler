from __future__ import annotations

import csv
import warnings
from functools import lru_cache
from pathlib import Path

from config import DesignConfig
from src.models import FluidProperties
from src.utils import celsius_to_kelvin, linear_interpolate

_STRICT_RANGE = True


def configure_property_behavior(strict: bool) -> None:
    """Configure out-of-range behavior for convenience wrapper functions."""
    global _STRICT_RANGE
    _STRICT_RANGE = strict


def load_property_table(csv_path: str) -> list[dict]:
    """Load a property table from CSV into a list of float dictionaries."""
    rows: list[dict] = []
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for raw_row in reader:
            row = {key: float(value) for key, value in raw_row.items()}
            rows.append(row)
    if not rows:
        raise ValueError(f"Property table is empty: {csv_path}")
    rows.sort(key=lambda item: item["temperature_k"])
    return rows


def _coerce_bounds(table: list[dict], temperature_k: float, strict: bool) -> float:
    minimum = table[0]["temperature_k"]
    maximum = table[-1]["temperature_k"]
    if minimum <= temperature_k <= maximum:
        return temperature_k
    if strict:
        raise ValueError(
            f"Temperature {temperature_k:.2f} K is outside property table range "
            f"{minimum:.2f} K to {maximum:.2f} K."
        )
    clipped = max(minimum, min(temperature_k, maximum))
    warnings.warn(
        f"Temperature {temperature_k:.2f} K exceeded property table range; clipped to {clipped:.2f} K.",
        RuntimeWarning,
        stacklevel=2,
    )
    return clipped


def interpolate_property(table: list[dict], temperature_k: float) -> FluidProperties:
    """Interpolate fluid properties at the requested temperature in Kelvin."""
    adjusted_temperature = _coerce_bounds(table, temperature_k, strict=_STRICT_RANGE)
    if adjusted_temperature <= table[0]["temperature_k"]:
        row = dict(table[0])
    elif adjusted_temperature >= table[-1]["temperature_k"]:
        row = dict(table[-1])
    else:
        lower = table[0]
        upper = table[-1]
        for index in range(len(table) - 1):
            current = table[index]
            nxt = table[index + 1]
            if current["temperature_k"] <= adjusted_temperature <= nxt["temperature_k"]:
                lower = current
                upper = nxt
                break
        row = {}
        for key in lower:
            if key == "temperature_k":
                row[key] = adjusted_temperature
                continue
            row[key] = linear_interpolate(
                lower["temperature_k"],
                lower[key],
                upper["temperature_k"],
                upper[key],
                adjusted_temperature,
            )

    density = row["density_kg_m3"]
    dynamic_viscosity = row["dynamic_viscosity_pa_s"]
    specific_heat = row["specific_heat_j_kg_k"]
    conductivity = row["thermal_conductivity_w_m_k"]
    kinematic_viscosity = row.get("kinematic_viscosity_m2_s", dynamic_viscosity / density)
    thermal_diffusivity = row.get(
        "thermal_diffusivity_m2_s",
        conductivity / (density * specific_heat),
    )
    prandtl = row.get("prandtl", specific_heat * dynamic_viscosity / conductivity)

    return FluidProperties(
        temperature_k=row["temperature_k"],
        density_kg_m3=density,
        dynamic_viscosity_pa_s=dynamic_viscosity,
        specific_heat_j_kg_k=specific_heat,
        thermal_conductivity_w_m_k=conductivity,
        prandtl=prandtl,
        kinematic_viscosity_m2_s=kinematic_viscosity,
        thermal_diffusivity_m2_s=thermal_diffusivity,
    )


@lru_cache(maxsize=1)
def _load_kerosene_table() -> tuple[dict, ...]:
    config = DesignConfig()
    return tuple(load_property_table(str(config.kerosene_csv_path)))


@lru_cache(maxsize=1)
def _load_water_table() -> tuple[dict, ...]:
    config = DesignConfig()
    return tuple(load_property_table(str(config.water_csv_path)))


def get_kerosene_props(temp_c: float) -> FluidProperties:
    """Get kerosene properties at the requested Celsius temperature."""
    return interpolate_property(list(_load_kerosene_table()), celsius_to_kelvin(temp_c))


def get_water_props(temp_c: float) -> FluidProperties:
    """Get water properties at the requested Celsius temperature."""
    return interpolate_property(list(_load_water_table()), celsius_to_kelvin(temp_c))
