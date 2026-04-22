from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from config import DesignConfig
from main import run_design
from src.file_io import (
    export_excel_report,
    export_word_report,
    load_config_from_excel,
    load_config_from_json,
)


def get_default_config_dict() -> dict[str, Any]:
    """Return the default design configuration as a plain dictionary."""
    config = DesignConfig(print_intermediate=False)
    result = config.to_dict()
    result.pop("base_dir", None)
    return result


def run_design_from_mapping(values: dict[str, Any]) -> dict[str, Any]:
    """Run the design calculation and serialize the result as JSON-friendly data."""
    config = DesignConfig.from_mapping(values)
    design = run_design(config)
    return _to_jsonable(design)


def load_config_from_json_bytes(content: bytes, file_name: str = "config.json") -> dict[str, Any]:
    """Load a configuration dictionary from uploaded JSON content."""
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / file_name
        path.write_bytes(content)
        config = load_config_from_json(path)
        result = config.to_dict()
        result.pop("base_dir", None)
        return result


def load_config_from_excel_bytes(content: bytes, file_name: str = "config.xlsx") -> dict[str, Any]:
    """Load a configuration dictionary from uploaded Excel content."""
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / file_name
        path.write_bytes(content)
        config = load_config_from_excel(path)
        result = config.to_dict()
        result.pop("base_dir", None)
        return result


def export_excel_bytes(values: dict[str, Any]) -> bytes:
    """Run the design and return an Excel workbook as bytes."""
    config = DesignConfig.from_mapping(values)
    design = run_design(config)
    with TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "design_results.xlsx"
        export_excel_report(output_path, design, Path(__file__).resolve().parents[2])
        return output_path.read_bytes()


def export_word_bytes(values: dict[str, Any]) -> bytes:
    """Run the design and return a Word report as bytes."""
    config = DesignConfig.from_mapping(values)
    design = run_design(config)
    with TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "design_results.docx"
        export_word_report(output_path, design)
        return output_path.read_bytes()


def _to_jsonable(value: Any) -> Any:
    """Recursively convert dataclasses and paths to JSON-friendly objects."""
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value
