from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from backend.schemas import ConfigResponse, DesignConfigPayload, DesignRunResponse, HealthResponse, ImportConfigResponse
from backend.services.design_service import (
    export_excel_bytes,
    export_word_bytes,
    get_default_config_dict,
    load_config_from_excel_bytes,
    load_config_from_json_bytes,
    run_design_from_mapping,
)
from src.utils import DesignError

router = APIRouter(tags=["design"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Simple health endpoint for frontend bootstrapping."""
    return HealthResponse(status="ok", message="Shell-and-tube cooler backend is running.")


@router.get("/design/default-config", response_model=ConfigResponse)
def get_default_config() -> ConfigResponse:
    """Return the default course-design configuration."""
    return ConfigResponse(config=get_default_config_dict())


@router.post("/design/run", response_model=DesignRunResponse)
def run_design_api(payload: DesignConfigPayload) -> DesignRunResponse:
    """Run the complete design workflow and return JSON results."""
    try:
        design = run_design_from_mapping(payload.model_dump())
    except DesignError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Design calculation failed: {exc}") from exc
    return DesignRunResponse(design=design)


@router.post("/design/import/json", response_model=ImportConfigResponse)
async def import_json_config(file: UploadFile = File(...)) -> ImportConfigResponse:
    """Parse an uploaded JSON config file into API config shape."""
    try:
        content = await file.read()
        config = load_config_from_json_bytes(content, file.filename or "config.json")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"JSON import failed: {exc}") from exc
    return ImportConfigResponse(config=config, source=file.filename or "config.json")


@router.post("/design/import/excel", response_model=ImportConfigResponse)
async def import_excel_config(file: UploadFile = File(...)) -> ImportConfigResponse:
    """Parse an uploaded Excel config template into API config shape."""
    try:
        content = await file.read()
        config = load_config_from_excel_bytes(content, file.filename or "config.xlsx")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Excel import failed: {exc}") from exc
    return ImportConfigResponse(config=config, source=file.filename or "config.xlsx")


@router.post("/design/export/excel")
def export_excel_api(payload: DesignConfigPayload) -> Response:
    """Run the design and return an Excel workbook."""
    try:
        content = export_excel_bytes(payload.model_dump())
    except DesignError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Excel export failed: {exc}") from exc
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="design_results.xlsx"'},
    )


@router.post("/design/export/word")
def export_word_api(payload: DesignConfigPayload) -> Response:
    """Run the design and return a Word report."""
    try:
        content = export_word_bytes(payload.model_dump())
    except DesignError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Word export failed: {exc}") from exc
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="design_results.docx"'},
    )
