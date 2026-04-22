import { useEffect, useMemo, useState } from "react";

import { mapDesignResultToDashboard } from "../mappers/designMappers";
import { mockDesignResult, mockFormValues, mockHealth } from "../mock/mockDesignData";
import { calculateDesign, getApiHealth, importExcelConfig, importJsonConfig, resetDesignParams } from "../services/designApi";
import type { ApiHealthDto, DashboardViewModel, DesignFormErrors, DesignFormValues, DesignResultDto } from "../types/design";

export function useDesignCalculation() {
  const [health, setHealth] = useState<ApiHealthDto>(mockHealth);
  const [formValues, setFormValues] = useState<DesignFormValues>(mockFormValues);
  const [result, setResult] = useState<DesignResultDto | null>(mockDesignResult);
  const [dashboard, setDashboard] = useState<DashboardViewModel>(() => mapDesignResultToDashboard(mockDesignResult));
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [errors, setErrors] = useState<DesignFormErrors>({});

  useEffect(() => {
    void getApiHealth().then(setHealth);
    void resetDesignParams().then(setFormValues);
  }, []);

  const hasResult = Boolean(result);

  const canExport = useMemo(
    () => Boolean(result?.exportStatus.markdownReady || result?.exportStatus.excelReady || result?.exportStatus.wordReady),
    [result],
  );

  const updateField = (section: keyof DesignFormValues, key: string, value: string | number | number[]) => {
    setFormValues((previous) => ({
      ...previous,
      [section]: {
        ...previous[section],
        [key]: value,
      },
    }));
  };

  const runCalculation = async () => {
    const nextErrors = validateForm(formValues);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return false;

    setIsLoading(true);
    setProgress(8);
    const timer = window.setInterval(() => {
      setProgress((current) => (current >= 88 ? current : current + 12));
    }, 260);

    try {
      const nextResult = await calculateDesign(formValues);
      setResult(nextResult);
      setDashboard(mapDesignResultToDashboard(nextResult));
      setProgress(100);
      return true;
    } finally {
      window.clearInterval(timer);
      window.setTimeout(() => {
        setIsLoading(false);
        setProgress(0);
      }, 360);
    }
  };

  const resetForm = async () => {
    const defaults = await resetDesignParams();
    setFormValues(defaults);
    setErrors({});
    setResult(null);
  };

  const importJson = async (file: File) => {
    const imported = await importJsonConfig(file);
    setFormValues(imported);
    setErrors({});
  };

  const importExcel = async (file: File) => {
    const imported = await importExcelConfig(file);
    setFormValues(imported);
    setErrors({});
  };

  return {
    health,
    formValues,
    result,
    dashboard,
    isLoading,
    progress,
    errors,
    hasResult,
    canExport,
    updateField,
    runCalculation,
    resetForm,
    importJson,
    importExcel,
  };
}

function validateForm(values: DesignFormValues): DesignFormErrors {
  const nextErrors: DesignFormErrors = {};

  if (values.assumptions.tubeInnerDiameterM >= values.assumptions.tubeOuterDiameterM) {
    nextErrors["assumptions.tubeInnerDiameterM"] = "管内径必须小于管外径";
  }

  if (values.operatingCondition.hotInletTempC <= values.operatingCondition.hotOutletTempC) {
    nextErrors["operatingCondition.hotOutletTempC"] = "热流体出口温度应低于入口温度";
  }

  if (values.operatingCondition.coldOutletTempC <= values.operatingCondition.coldInletTempC) {
    nextErrors["operatingCondition.coldOutletTempC"] = "冷流体出口温度应高于入口温度";
  }

  if (!values.assumptions.tubeLengthCandidatesM.length) {
    nextErrors["assumptions.tubeLengthCandidatesM"] = "管长候选不能为空";
  }

  if (values.assumptions.tubePasses <= 0) {
    nextErrors["assumptions.tubePasses"] = "管程数必须为正整数";
  }

  return nextErrors;
}
