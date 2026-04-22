import { AlertTriangle, CheckCircle2, FlaskConical, Gauge, LayoutTemplate, ShieldCheck, Thermometer } from "lucide-react";

import type {
  DashboardViewModel,
  DesignResultDto,
  KpiCardViewModel,
  ProcessStepViewModel,
  ValidationItemViewModel,
} from "../types/design";

export function mapDesignResultToDashboard(result: DesignResultDto): DashboardViewModel {
  return {
    title: "固定管板式管壳式煤油冷却器",
    subtitle: "课程设计计算与答辩展示系统",
    designStatus: result.designStatus,
    statusTitle: getStatusTitle(result.designStatus),
    statusMessage: result.validation.summaryText,
    kpis: buildKpis(result),
    processSteps: buildProcessSteps(result),
    validationItems: buildValidationItems(result),
    defenseSummary: result.defenseSummary,
  };
}

export function getStatusTitle(status: DesignResultDto["designStatus"]) {
  if (status === "success") return "方案可行";
  if (status === "warning") return "方案部分满足";
  return "方案不可行";
}

export function getStatusIcon(status: DesignResultDto["designStatus"]) {
  if (status === "success") return CheckCircle2;
  if (status === "warning") return AlertTriangle;
  return AlertTriangle;
}

export function getProcessIcon(stepId: string) {
  switch (stepId) {
    case "input":
      return LayoutTemplate;
    case "thermal":
      return Thermometer;
    case "mechanical":
      return FlaskConical;
    case "hydraulic":
      return Gauge;
    default:
      return ShieldCheck;
  }
}

function buildKpis(result: DesignResultDto): KpiCardViewModel[] {
  return [
    {
      id: "heat-duty",
      title: "热负荷",
      value: formatNumber(result.thermalResult.heatDutyW / 1000, 2),
      unit: "kW",
      description: "基于热量衡算",
      tone: "primary",
    },
    {
      id: "cold-flow",
      title: "冷却水流量",
      value: formatNumber(result.thermalResult.coldMassFlowKgS, 2),
      unit: "kg/s",
      description: "满足冷端升温要求",
      tone: "primary",
    },
    {
      id: "overall-u",
      title: "总传热系数",
      value: formatNumber(result.thermalResult.overallUCalculatedWm2K, 2),
      unit: "W/(m²·K)",
      description: "采用校核后的综合值",
      tone: "success",
    },
    {
      id: "structure",
      title: "推荐结构方案",
      value: result.mechanicalResult.recommendedStructureText,
      description: `${result.mechanicalResult.shellPasses} 壳程 / ${result.mechanicalResult.tubePasses} 管程`,
      tone: "success",
    },
  ];
}

function buildProcessSteps(result: DesignResultDto): ProcessStepViewModel[] {
  return [
    {
      id: "input",
      title: "输入",
      metric: "工况已载入",
      description: `煤油 ${result.operatingCondition.hotInletTempC} → ${result.operatingCondition.hotOutletTempC} ℃`,
      state: "done",
    },
    {
      id: "thermal",
      title: "热工",
      metric: `Q = ${formatNumber(result.thermalResult.heatDutyW / 1000, 1)} kW`,
      description: `A = ${formatNumber(result.thermalResult.requiredAreaM2, 2)} m²`,
      state: "done",
    },
    {
      id: "mechanical",
      title: "结构",
      metric: `L = ${formatNumber(result.mechanicalResult.tubeLengthM, 1)} m`,
      description: `N = ${result.mechanicalResult.tubeCount} 根`,
      state: "done",
    },
    {
      id: "hydraulic",
      title: "阻力",
      metric: `管程 ${formatNumber(result.hydraulicResult.tubePressureDropPa / 1000, 2)} kPa`,
      description: `壳程 ${formatNumber(result.hydraulicResult.shellPressureDropPa / 1000, 2)} kPa`,
      state: result.hydraulicResult.tubePressureDropOk && result.hydraulicResult.shellPressureDropOk ? "done" : "warning",
    },
    {
      id: "conclusion",
      title: "结论",
      metric: getStatusTitle(result.designStatus),
      description: result.validation.summaryText,
      state: result.designStatus === "success" ? "active" : "warning",
    },
  ];
}

function buildValidationItems(result: DesignResultDto): ValidationItemViewModel[] {
  return [
    {
      id: "area",
      label: "传热面积",
      passed: result.validation.areaOk,
      detail: `${formatNumber(result.thermalResult.requiredAreaM2, 2)} / ${formatNumber(result.mechanicalResult.actualAreaM2, 2)} m²`,
    },
    {
      id: "tube-velocity",
      label: "管内流速",
      passed: result.validation.tubeVelocityOk,
      detail: `${formatNumber(result.hydraulicResult.tubeVelocityMS, 3)} m/s`,
    },
    {
      id: "shell-velocity",
      label: "壳程流速",
      passed: result.validation.shellVelocityOk,
      detail: `${formatNumber(result.hydraulicResult.shellVelocityMS, 3)} m/s`,
    },
    {
      id: "tube-drop",
      label: "管程压降",
      passed: result.validation.tubePressureDropOk,
      detail: `${formatNumber(result.hydraulicResult.tubePressureDropPa / 1000, 2)} kPa`,
    },
    {
      id: "shell-drop",
      label: "壳程压降",
      passed: result.validation.shellPressureDropOk,
      detail: `${formatNumber(result.hydraulicResult.shellPressureDropPa / 1000, 2)} kPa`,
    },
  ];
}

function formatNumber(value: number, digits = 2) {
  return new Intl.NumberFormat("zh-CN", {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  }).format(value);
}
