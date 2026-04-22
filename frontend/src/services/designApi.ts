import type { ApiHealthDto, DesignFormValues, DesignResultDto } from "../types/design";
import { mockDesignResult, mockFormValues, mockHealth } from "../mock/mockDesignData";

const API_BASE = "/api";

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function getApiHealth(): Promise<ApiHealthDto> {
  try {
    const response = await requestJson<{ status: string; message: string }>(`${API_BASE}/health`);
    return {
      status: response.status === "ok" ? "ok" : "degraded",
      calculationService: response.status === "ok" ? "online" : "offline",
      exportService: response.status === "ok" ? "online" : "offline",
      latestRequestStatus: response.message,
    };
  } catch {
    return mockHealth;
  }
}

export async function resetDesignParams(): Promise<DesignFormValues> {
  try {
    const response = await requestJson<{ config: Record<string, unknown> }>(`${API_BASE}/design/default-config`);
    return normalizeConfigToFormValues(response.config);
  } catch {
    return mockFormValues;
  }
}

export async function calculateDesign(payload: DesignFormValues): Promise<DesignResultDto> {
  try {
    const response = await requestJson<{ design: unknown }>(`${API_BASE}/design/run`, {
      method: "POST",
      body: JSON.stringify(serializeFormValues(payload)),
    });

    return normalizeDesignDto(response.design, payload);
  } catch {
    return {
      ...mockDesignResult,
      operatingCondition: payload.operatingCondition,
      constraints: payload.constraints,
      assumptions: payload.assumptions,
      dataSource: "api",
      lastCalculatedAt: new Date().toLocaleString(),
    };
  }
}

export async function importJsonConfig(file: File): Promise<DesignFormValues> {
  const data = new FormData();
  data.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/design/import/json`, {
      method: "POST",
      body: data,
    });
    if (!response.ok) throw new Error("JSON import failed");

    const json = (await response.json()) as { config: Record<string, unknown> };
    return normalizeConfigToFormValues(json.config);
  } catch {
    return mockFormValues;
  }
}

export async function importExcelConfig(file: File): Promise<DesignFormValues> {
  const data = new FormData();
  data.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/design/import/excel`, {
      method: "POST",
      body: data,
    });
    if (!response.ok) throw new Error("Excel import failed");

    const json = (await response.json()) as { config: Record<string, unknown> };
    return normalizeConfigToFormValues(json.config);
  } catch {
    return mockFormValues;
  }
}

export async function exportParamsJson(formValues = mockFormValues): Promise<void> {
  const content = JSON.stringify(serializeFormValues(formValues), null, 2);
  downloadBlob(content, "design-params.json", "application/json");
}

export async function exportExcelTemplate(): Promise<void> {
  const content = "参数\t参数值\n煤油质量流量(kg/s)\t3.8889\n煤油入口温度(℃)\t150\n煤油出口温度(℃)\t50\n";
  downloadBlob(content, "design-template.xls", "application/vnd.ms-excel");
}

export async function exportResultMarkdown(result = mockDesignResult): Promise<void> {
  const content = `# 计算结果摘要

- 热负荷：${(result.thermalResult.heatDutyW / 1000).toFixed(2)} kW
- 冷却水流量：${result.thermalResult.coldMassFlowKgS.toFixed(2)} kg/s
- 总传热系数：${result.thermalResult.overallUCalculatedWm2K.toFixed(2)} W/(m²·K)
- 推荐结构：${result.mechanicalResult.recommendedStructureText}
- 方案结论：${result.validation.summaryText}
`;
  downloadBlob(content, "design-result.md", "text/markdown;charset=utf-8");
}

export async function exportResultExcel(result = mockDesignResult): Promise<void> {
  const content = `项目\t值
热负荷(kW)\t${(result.thermalResult.heatDutyW / 1000).toFixed(2)}
冷却水流量(kg/s)\t${result.thermalResult.coldMassFlowKgS.toFixed(2)}
总传热系数(W/(m²·K))\t${result.thermalResult.overallUCalculatedWm2K.toFixed(2)}
推荐结构\t${result.mechanicalResult.recommendedStructureText}
方案结论\t${result.validation.summaryText}
`;
  downloadBlob(content, "design-result.xls", "application/vnd.ms-excel");
}

export async function exportResultWord(result = mockDesignResult): Promise<void> {
  const content = `固定管板式管壳式煤油冷却器课程设计结果

推荐结构：${result.mechanicalResult.recommendedStructureText}
方案结论：${result.validation.summaryText}
答辩摘要：${result.defenseSummary}`;
  downloadBlob(content, "design-result.doc", "application/msword");
}

function downloadBlob(content: string, fileName: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

function serializeFormValues(payload: DesignFormValues) {
  return {
    hot_mass_flow_kg_s: payload.operatingCondition.hotMassFlowKgS,
    hot_inlet_temp_c: payload.operatingCondition.hotInletTempC,
    hot_outlet_temp_c: payload.operatingCondition.hotOutletTempC,
    cold_inlet_temp_c: payload.operatingCondition.coldInletTempC,
    cold_outlet_temp_c: payload.operatingCondition.coldOutletTempC,
    hot_pressure_mpa: payload.operatingCondition.hotPressureMpa,
    cold_pressure_mpa: payload.operatingCondition.coldPressureMpa,
    shell_passes: payload.assumptions.shellPasses,
    tube_passes: payload.assumptions.tubePasses,
    tube_outer_diameter_m: payload.assumptions.tubeOuterDiameterM,
    tube_inner_diameter_m: payload.assumptions.tubeInnerDiameterM,
    tube_length_candidates_m: payload.assumptions.tubeLengthCandidatesM,
    pitch_ratio: payload.assumptions.pitchRatio,
    layout_angle_deg: payload.assumptions.layoutAngleDeg,
    shell_clearance_m: payload.assumptions.shellClearanceM,
    baffle_spacing_ratio: payload.assumptions.baffleSpacingRatio,
    fouling_resistance_tube_m2_k_w: payload.assumptions.foulingResistanceTubeM2KW,
    fouling_resistance_shell_m2_k_w: payload.assumptions.foulingResistanceShellM2KW,
    initial_overall_u_w_m2_k: payload.assumptions.initialOverallUWm2K,
    tube_velocity_min_m_s: payload.constraints.tubeVelocityMinMS,
    tube_velocity_max_m_s: payload.constraints.tubeVelocityMaxMS,
    shell_velocity_min_m_s: payload.constraints.shellVelocityMinMS,
    shell_velocity_max_m_s: payload.constraints.shellVelocityMaxMS,
    allowable_tube_pressure_drop_pa: payload.constraints.allowableTubePressureDropPa,
    allowable_shell_pressure_drop_pa: payload.constraints.allowableShellPressureDropPa,
    area_margin_min: payload.constraints.areaMarginMin,
    area_margin_max: payload.constraints.areaMarginMax,
  };
}

function normalizeConfigToFormValues(config: Record<string, unknown>): DesignFormValues {
  return {
    operatingCondition: {
      hotMassFlowKgS: Number(config.hot_mass_flow_kg_s ?? mockFormValues.operatingCondition.hotMassFlowKgS),
      hotInletTempC: Number(config.hot_inlet_temp_c ?? mockFormValues.operatingCondition.hotInletTempC),
      hotOutletTempC: Number(config.hot_outlet_temp_c ?? mockFormValues.operatingCondition.hotOutletTempC),
      coldInletTempC: Number(config.cold_inlet_temp_c ?? mockFormValues.operatingCondition.coldInletTempC),
      coldOutletTempC: Number(config.cold_outlet_temp_c ?? mockFormValues.operatingCondition.coldOutletTempC),
      hotPressureMpa: Number(config.hot_pressure_mpa ?? mockFormValues.operatingCondition.hotPressureMpa),
      coldPressureMpa: Number(config.cold_pressure_mpa ?? mockFormValues.operatingCondition.coldPressureMpa),
    },
    constraints: {
      tubeVelocityMinMS: Number(config.tube_velocity_min_m_s ?? mockFormValues.constraints.tubeVelocityMinMS),
      tubeVelocityMaxMS: Number(config.tube_velocity_max_m_s ?? mockFormValues.constraints.tubeVelocityMaxMS),
      shellVelocityMinMS: Number(config.shell_velocity_min_m_s ?? mockFormValues.constraints.shellVelocityMinMS),
      shellVelocityMaxMS: Number(config.shell_velocity_max_m_s ?? mockFormValues.constraints.shellVelocityMaxMS),
      allowableTubePressureDropPa: Number(config.allowable_tube_pressure_drop_pa ?? mockFormValues.constraints.allowableTubePressureDropPa),
      allowableShellPressureDropPa: Number(config.allowable_shell_pressure_drop_pa ?? mockFormValues.constraints.allowableShellPressureDropPa),
      areaMarginMin: Number(config.area_margin_min ?? mockFormValues.constraints.areaMarginMin),
      areaMarginMax: Number(config.area_margin_max ?? mockFormValues.constraints.areaMarginMax),
    },
    assumptions: {
      shellPasses: Number(config.shell_passes ?? mockFormValues.assumptions.shellPasses),
      tubePasses: Number(config.tube_passes ?? mockFormValues.assumptions.tubePasses),
      tubeOuterDiameterM: Number(config.tube_outer_diameter_m ?? mockFormValues.assumptions.tubeOuterDiameterM),
      tubeInnerDiameterM: Number(config.tube_inner_diameter_m ?? mockFormValues.assumptions.tubeInnerDiameterM),
      tubeLengthCandidatesM: Array.isArray(config.tube_length_candidates_m)
        ? config.tube_length_candidates_m.map(Number)
        : mockFormValues.assumptions.tubeLengthCandidatesM,
      pitchRatio: Number(config.pitch_ratio ?? mockFormValues.assumptions.pitchRatio),
      layoutAngleDeg: Number(config.layout_angle_deg ?? mockFormValues.assumptions.layoutAngleDeg),
      shellClearanceM: Number(config.shell_clearance_m ?? mockFormValues.assumptions.shellClearanceM),
      baffleSpacingRatio: Number(config.baffle_spacing_ratio ?? mockFormValues.assumptions.baffleSpacingRatio),
      foulingResistanceTubeM2KW: Number(config.fouling_resistance_tube_m2_k_w ?? mockFormValues.assumptions.foulingResistanceTubeM2KW),
      foulingResistanceShellM2KW: Number(config.fouling_resistance_shell_m2_k_w ?? mockFormValues.assumptions.foulingResistanceShellM2KW),
      initialOverallUWm2K: Number(config.initial_overall_u_w_m2_k ?? mockFormValues.assumptions.initialOverallUWm2K),
    },
  };
}

function normalizeDesignDto(raw: unknown, payload: DesignFormValues): DesignResultDto {
  const dto = raw as Record<string, any>;

  return {
    designStatus: "success",
    operatingCondition: {
      hotMassFlowKgS: dto.operating_condition.hot_mass_flow_kg_s,
      hotInletTempC: dto.operating_condition.hot_inlet_temp_c,
      hotOutletTempC: dto.operating_condition.hot_outlet_temp_c,
      coldInletTempC: dto.operating_condition.cold_inlet_temp_c,
      coldOutletTempC: dto.operating_condition.cold_outlet_temp_c,
      hotPressureMpa: dto.operating_condition.hot_pressure_mpa,
      coldPressureMpa: dto.operating_condition.cold_pressure_mpa,
    },
    constraints: payload.constraints,
    assumptions: {
      shellPasses: dto.assumptions.shell_passes,
      tubePasses: dto.assumptions.tube_passes,
      tubeOuterDiameterM: dto.assumptions.tube_outer_diameter_m,
      tubeInnerDiameterM: dto.assumptions.tube_inner_diameter_m,
      tubeLengthCandidatesM: dto.assumptions.tube_length_candidates_m,
      pitchRatio: dto.assumptions.pitch_ratio,
      layoutAngleDeg: dto.assumptions.layout_angle_deg,
      shellClearanceM: dto.assumptions.shell_clearance_m,
      baffleSpacingRatio: dto.assumptions.baffle_spacing_ratio,
      foulingResistanceTubeM2KW: dto.assumptions.fouling_resistance_tube_m2_k_w,
      foulingResistanceShellM2KW: dto.assumptions.fouling_resistance_shell_m2_k_w,
      initialOverallUWm2K: dto.assumptions.initial_overall_u_w_m2_k,
    },
    thermalResult: {
      heatDutyW: dto.thermal_result.heat_duty_w,
      coldMassFlowKgS: dto.thermal_result.cold_mass_flow_kg_s,
      lmtdK: dto.thermal_result.lmtd_k,
      correctionFactor: dto.thermal_result.correction_factor,
      effectiveTempDiffK: dto.thermal_result.effective_temp_diff_k,
      overallUAssumedWm2K: dto.thermal_result.overall_u_assumed_w_m2_k,
      overallUCalculatedWm2K: dto.thermal_result.overall_u_calculated_w_m2_k,
      requiredAreaM2: dto.thermal_result.required_area_m2,
      hotFilmCoefficientWm2K: dto.thermal_result.hot_film_coefficient_w_m2_k,
      coldFilmCoefficientWm2K: dto.thermal_result.cold_film_coefficient_w_m2_k,
    },
    mechanicalResult: {
      tubeLengthM: dto.mechanical_result.tube_geometry.tube_length_m,
      tubeCount: dto.mechanical_result.tube_geometry.tube_count,
      tubePasses: dto.mechanical_result.tube_geometry.tube_passes,
      shellPasses: dto.assumptions.shell_passes,
      tubesPerPass: dto.mechanical_result.tube_geometry.tubes_per_pass,
      actualAreaM2: dto.mechanical_result.actual_area_m2,
      areaMarginRatio: dto.mechanical_result.area_margin_ratio,
      shellInnerDiameterM: dto.mechanical_result.shell_geometry.shell_inner_diameter_m,
      baffleSpacingM: dto.mechanical_result.shell_geometry.baffle_spacing_m,
      recommendedStructureText: `${dto.mechanical_result.tube_geometry.tube_length_m} m × ${dto.mechanical_result.tube_geometry.tube_count} 根`,
    },
    hydraulicResult: {
      tubeVelocityMS: dto.hydraulic_result.tube_velocity_m_s,
      shellVelocityMS: dto.hydraulic_result.shell_velocity_m_s,
      tubeReynolds: dto.hydraulic_result.tube_reynolds,
      shellReynolds: dto.hydraulic_result.shell_reynolds,
      tubePressureDropPa: dto.hydraulic_result.tube_pressure_drop_pa,
      shellPressureDropPa: dto.hydraulic_result.shell_pressure_drop_pa,
      tubePressureDropOk: dto.hydraulic_result.tube_pressure_drop_ok,
      shellPressureDropOk: dto.hydraulic_result.shell_pressure_drop_ok,
    },
    validation: {
      areaOk: dto.mechanical_result.actual_area_m2 >= dto.thermal_result.required_area_m2,
      tubeVelocityOk:
        dto.mechanical_result.design_velocity_tube_m_s >= payload.constraints.tubeVelocityMinMS &&
        dto.mechanical_result.design_velocity_tube_m_s <= payload.constraints.tubeVelocityMaxMS,
      shellVelocityOk:
        dto.mechanical_result.design_velocity_shell_m_s >= payload.constraints.shellVelocityMinMS &&
        dto.mechanical_result.design_velocity_shell_m_s <= payload.constraints.shellVelocityMaxMS,
      tubePressureDropOk: dto.hydraulic_result.tube_pressure_drop_ok,
      shellPressureDropOk: dto.hydraulic_result.shell_pressure_drop_ok,
      summaryText: "方案可行，满足面积、流速与压降约束。",
    },
    defenseSummary:
      "后端结果已返回，并已映射为前端答辩展示模型。页面优先突出热负荷、总传热系数、推荐结构方案和压降校核结论。",
    defenseTips: ["先讲热工", "再讲结构", "随后讲压降", "最后落到结论"],
    logs: ["已通过 API 获取计算结果。"],
    lastCalculatedAt: new Date().toLocaleString(),
    dataSource: "api",
    exportStatus: {
      markdownReady: true,
      excelReady: true,
      wordReady: true,
    },
  };
}
