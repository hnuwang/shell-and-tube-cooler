export type DesignStatus = "success" | "warning" | "error";
export type DataSource = "default" | "json" | "excel" | "api";

export interface OperatingConditionDto {
  hotMassFlowKgS: number;
  hotInletTempC: number;
  hotOutletTempC: number;
  coldInletTempC: number;
  coldOutletTempC: number;
  hotPressureMpa: number;
  coldPressureMpa: number;
}

export interface ConstraintSettingsDto {
  tubeVelocityMinMS: number;
  tubeVelocityMaxMS: number;
  shellVelocityMinMS: number;
  shellVelocityMaxMS: number;
  allowableTubePressureDropPa: number;
  allowableShellPressureDropPa: number;
  areaMarginMin: number;
  areaMarginMax: number;
}

export interface AssumptionsDto {
  shellPasses: number;
  tubePasses: number;
  tubeOuterDiameterM: number;
  tubeInnerDiameterM: number;
  tubeLengthCandidatesM: number[];
  pitchRatio: number;
  layoutAngleDeg: number;
  shellClearanceM: number;
  baffleSpacingRatio: number;
  foulingResistanceTubeM2KW: number;
  foulingResistanceShellM2KW: number;
  initialOverallUWm2K: number;
}

export interface ThermalResultDto {
  heatDutyW: number;
  coldMassFlowKgS: number;
  lmtdK: number;
  correctionFactor: number;
  effectiveTempDiffK: number;
  overallUAssumedWm2K: number;
  overallUCalculatedWm2K: number;
  requiredAreaM2: number;
  hotFilmCoefficientWm2K: number;
  coldFilmCoefficientWm2K: number;
}

export interface MechanicalResultDto {
  tubeLengthM: number;
  tubeCount: number;
  tubePasses: number;
  shellPasses: number;
  tubesPerPass: number;
  actualAreaM2: number;
  areaMarginRatio: number;
  shellInnerDiameterM: number;
  baffleSpacingM: number;
  recommendedStructureText: string;
}

export interface HydraulicResultDto {
  tubeVelocityMS: number;
  shellVelocityMS: number;
  tubeReynolds: number;
  shellReynolds: number;
  tubePressureDropPa: number;
  shellPressureDropPa: number;
  tubePressureDropOk: boolean;
  shellPressureDropOk: boolean;
}

export interface ValidationResultDto {
  areaOk: boolean;
  tubeVelocityOk: boolean;
  shellVelocityOk: boolean;
  tubePressureDropOk: boolean;
  shellPressureDropOk: boolean;
  summaryText: string;
}

export interface ExportStatusDto {
  markdownReady: boolean;
  excelReady: boolean;
  wordReady: boolean;
}

export interface ApiHealthDto {
  status: "ok" | "degraded" | "error";
  calculationService: "online" | "offline";
  exportService: "online" | "offline";
  latestRequestStatus: string;
}

export interface DesignResultDto {
  designStatus: DesignStatus;
  operatingCondition: OperatingConditionDto;
  constraints: ConstraintSettingsDto;
  assumptions: AssumptionsDto;
  thermalResult: ThermalResultDto;
  mechanicalResult: MechanicalResultDto;
  hydraulicResult: HydraulicResultDto;
  validation: ValidationResultDto;
  defenseSummary: string;
  defenseTips: string[];
  logs: string[];
  lastCalculatedAt: string;
  dataSource: DataSource;
  exportStatus: ExportStatusDto;
}

export interface KpiCardViewModel {
  id: string;
  title: string;
  value: string;
  unit?: string;
  description: string;
  tone?: "primary" | "success" | "warning" | "danger";
}

export interface ProcessStepViewModel {
  id: string;
  title: string;
  metric: string;
  description: string;
  state: "done" | "active" | "warning";
}

export interface ValidationItemViewModel {
  id: string;
  label: string;
  passed: boolean;
  detail: string;
}

export interface DashboardViewModel {
  title: string;
  subtitle: string;
  designStatus: DesignStatus;
  statusTitle: string;
  statusMessage: string;
  kpis: KpiCardViewModel[];
  processSteps: ProcessStepViewModel[];
  validationItems: ValidationItemViewModel[];
  defenseSummary: string;
}

export interface DesignFormValues {
  operatingCondition: OperatingConditionDto;
  constraints: ConstraintSettingsDto;
  assumptions: AssumptionsDto;
}

export type DesignFormErrors = Partial<Record<string, string>>;
