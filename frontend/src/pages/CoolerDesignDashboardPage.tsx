import { useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  AlertTriangle,
  ArrowDownToLine,
  Bolt,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Database,
  Download,
  FileJson,
  FileSpreadsheet,
  FileText,
  FlaskConical,
  Gauge,
  Layers3,
  LoaderCircle,
  Play,
  RefreshCw,
  Server,
  Settings2,
  Sparkles,
  Thermometer,
  Upload,
} from "lucide-react";
import { Toaster, toast } from "sonner";

import { useDesignCalculation } from "../hooks/useDesignCalculation";
import { getProcessIcon } from "../mappers/designMappers";
import {
  exportExcelTemplate,
  exportParamsJson,
  exportResultExcel,
  exportResultMarkdown,
  exportResultWord,
} from "../services/designApi";
import type { DashboardViewModel, DesignFormValues, DesignResultDto } from "../types/design";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export default function CoolerDesignDashboardPage() {
  const {
    health,
    formValues,
    result,
    dashboard,
    errors,
    isLoading,
    progress,
    canExport,
    updateField,
    runCalculation,
    resetForm,
    importJson,
    importExcel,
  } = useDesignCalculation();

  const [activeTab, setActiveTab] = useState("overview");

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-[linear-gradient(180deg,#eef3fb_0%,#e9eef8_100%)] text-text-primary">
        <Toaster richColors position="top-right" />

        <div className="mx-auto max-w-[1680px] px-4 py-4 xl:px-6">
          <div className="grid gap-4 xl:grid-cols-[72px_360px_minmax(0,1fr)]">
            <DesktopRail />

            <aside className="xl:sticky xl:top-4">
              <div className="overflow-hidden rounded-[28px] border border-slate-800/80 bg-[linear-gradient(180deg,#131c30_0%,#0f1727_100%)] text-white shadow-[0_28px_56px_rgba(15,23,42,0.26)]">
                <SidebarBrand />

                <div className="space-y-4 px-4 pb-4">
                  <SidebarSection title="文件与接口" icon={Server}>
                    <div className="grid gap-3">
                      <FileInputButton
                        label="导入 JSON 参数"
                        accept=".json"
                        icon={FileJson}
                        onFile={async (file) => {
                          await importJson(file);
                          toast.success("JSON 参数已导入");
                        }}
                      />
                      <FileInputButton
                        label="导入 Excel 参数表"
                        accept=".xlsx,.xls"
                        icon={FileSpreadsheet}
                        onFile={async (file) => {
                          await importExcel(file);
                          toast.success("Excel 参数表已导入");
                        }}
                      />
                      <DarkActionButton
                        icon={Download}
                        label="导出参数 JSON"
                        onClick={async () => {
                          await exportParamsJson(formValues);
                          toast.success("参数 JSON 已导出");
                        }}
                      />
                      <DarkActionButton
                        icon={ArrowDownToLine}
                        label="导出 Excel 模板"
                        onClick={async () => {
                          await exportExcelTemplate();
                          toast.success("Excel 模板已导出");
                        }}
                      />
                    </div>

                    <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-3">
                      <div className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">服务状态</div>
                      <div className="space-y-2.5">
                        <SidebarHealthRow label="计算服务" online={health.calculationService === "online"} />
                        <SidebarHealthRow label="导出服务" online={health.exportService === "online"} />
                        <SidebarHealthRow label="最近请求" online={health.status !== "error"} statusText={health.latestRequestStatus} />
                      </div>
                    </div>
                  </SidebarSection>

                  <SidebarSection title="工况参数" icon={Thermometer}>
                    <InputSections formValues={formValues} onUpdateField={updateField} errors={errors} />
                  </SidebarSection>

                  <SidebarSection title="结果导出" icon={FileText}>
                    <div className="grid gap-3">
                      <ExportButton
                        label="导出 Markdown 摘要"
                        icon={FileText}
                        disabled={!canExport}
                        tip="请先完成一次计算。"
                        onClick={async () => {
                          await exportResultMarkdown(result ?? undefined);
                          toast.success("Markdown 摘要已导出");
                        }}
                      />
                      <ExportButton
                        label="导出 Excel 结果表"
                        icon={FileSpreadsheet}
                        disabled={!canExport}
                        tip="请先完成一次计算。"
                        onClick={async () => {
                          await exportResultExcel(result ?? undefined);
                          toast.success("Excel 结果表已导出");
                        }}
                      />
                      <ExportButton
                        label="导出 Word 结果表"
                        icon={FileText}
                        disabled={!canExport}
                        tip="请先完成一次计算。"
                        onClick={async () => {
                          await exportResultWord(result ?? undefined);
                          toast.success("Word 结果表已导出");
                        }}
                      />
                    </div>
                  </SidebarSection>

                  <div className="rounded-[22px] border border-blue-400/20 bg-[linear-gradient(180deg,rgba(24,48,92,0.92),rgba(11,22,45,0.96))] p-3 shadow-[0_18px_34px_rgba(37,99,235,0.18)]">
                    <Button
                      className="h-12 w-full rounded-2xl bg-[linear-gradient(180deg,#2d8cff_0%,#2563eb_100%)] text-[15px] font-semibold text-white shadow-[0_14px_28px_rgba(37,99,235,0.32)] hover:opacity-95"
                      onClick={async () => {
                        const ok = await runCalculation();
                        if (ok) {
                          toast.success("计算完成，结果已刷新");
                        } else {
                          toast.error("请先修正输入参数");
                        }
                      }}
                      disabled={isLoading}
                    >
                      {isLoading ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Bolt className="mr-2 h-4 w-4" />}
                      {isLoading ? "正在计算方案" : "开始计算方案"}
                    </Button>

                    <Button
                      variant="ghost"
                      className="mt-2 h-10 w-full rounded-2xl text-slate-300 hover:bg-white/6 hover:text-white"
                      onClick={async () => {
                        await resetForm();
                        toast.info("已恢复默认参数");
                      }}
                    >
                      <RefreshCw className="mr-2 h-4 w-4" />
                      恢复默认参数
                    </Button>
                  </div>
                </div>
              </div>
            </aside>

            <main className="min-w-0 rounded-[30px] border border-white/80 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] p-4 shadow-[0_30px_60px_rgba(15,23,42,0.08)] xl:p-5">
              <div className="space-y-3">
                <PageHeader result={result} />
                <StatusBanner dashboard={dashboard} isLoading={isLoading} progress={progress} />
                <KpiCards dashboard={dashboard} isLoading={isLoading} />
                <ProcessStepper dashboard={dashboard} />

                <div className="grid gap-3 xl:grid-cols-[1.06fr_0.94fr]">
                  <div className="space-y-3">
                    <ResultCardShell title="题目工况" subtitle="输入边界条件与热端、冷端工况">
                      <InfoGrid
                        isLoading={isLoading}
                        items={
                          result
                            ? [
                                ["煤油进出口", `${result.operatingCondition.hotInletTempC} → ${result.operatingCondition.hotOutletTempC} ℃`],
                                ["煤油流量", `${result.operatingCondition.hotMassFlowKgS} kg/s`],
                                ["冷却水进出口", `${result.operatingCondition.coldInletTempC} → ${result.operatingCondition.coldOutletTempC} ℃`],
                                ["工作压力", `热侧 ${result.operatingCondition.hotPressureMpa} / 冷侧 ${result.operatingCondition.coldPressureMpa} MPa`],
                              ]
                            : []
                        }
                      />
                    </ResultCardShell>

                    <ResultCardShell title="结构参数" subtitle="推荐方案与主要结构尺寸">
                      <InfoGrid
                        isLoading={isLoading}
                        items={
                          result
                            ? [
                                ["推荐结构方案", result.mechanicalResult.recommendedStructureText],
                                ["壳程 / 管程", `${result.mechanicalResult.shellPasses} / ${result.mechanicalResult.tubePasses}`],
                                ["实际面积 / 裕量", `${result.mechanicalResult.actualAreaM2.toFixed(2)} m² / ${(result.mechanicalResult.areaMarginRatio * 100).toFixed(2)}%`],
                                ["壳体内径 / 挡板间距", `${result.mechanicalResult.shellInnerDiameterM.toFixed(4)} m / ${result.mechanicalResult.baffleSpacingM.toFixed(4)} m`],
                              ]
                            : []
                        }
                      />
                    </ResultCardShell>

                    <DetailTabs dashboard={dashboard} result={result} activeTab={activeTab} onTabChange={setActiveTab} isLoading={isLoading} />
                  </div>

                  <div className="space-y-3">
                    <ResultCardShell title="阻力计算" subtitle="流速、Re 与压降校核">
                      <InfoGrid
                        isLoading={isLoading}
                        items={
                          result
                            ? [
                                ["管程流速 / Re", `${result.hydraulicResult.tubeVelocityMS.toFixed(3)} m/s / ${result.hydraulicResult.tubeReynolds}`],
                                ["壳程流速 / Re", `${result.hydraulicResult.shellVelocityMS.toFixed(3)} m/s / ${result.hydraulicResult.shellReynolds}`],
                                ["管程压降", `${(result.hydraulicResult.tubePressureDropPa / 1000).toFixed(2)} kPa`],
                                ["壳程压降", `${(result.hydraulicResult.shellPressureDropPa / 1000).toFixed(2)} kPa`],
                              ]
                            : []
                        }
                      />
                    </ResultCardShell>

                    <ValidationCard dashboard={dashboard} isLoading={isLoading} />
                    <PigIpCard />
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

function DesktopRail() {
  const icons = [FlaskConical, Layers3, FileText, Settings2];

  return (
    <div className="hidden xl:block">
      <div className="flex h-full min-h-[calc(100vh-2rem)] flex-col items-center rounded-[24px] border border-slate-800/80 bg-[linear-gradient(180deg,#131c30_0%,#0f1727_100%)] py-4 shadow-[0_22px_46px_rgba(15,23,42,0.24)]">
        <div className="mb-6 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#1da1ff_0%,#2d63ff_100%)] shadow-[0_10px_24px_rgba(45,99,255,0.34)]">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <div className="flex flex-1 flex-col items-center gap-3">
          {icons.map((Icon, index) => (
            <div
              key={index}
              className={`flex h-11 w-11 items-center justify-center rounded-2xl border text-slate-300 ${
                index === 0 ? "border-blue-400/30 bg-blue-500/12 text-white" : "border-white/6 bg-white/4"
              }`}
            >
              <Icon className="h-4.5 w-4.5" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SidebarBrand() {
  return (
    <div className="border-b border-white/8 px-4 py-4">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#1da1ff_0%,#2d63ff_100%)] shadow-[0_12px_24px_rgba(45,99,255,0.34)]">
          <FlaskConical className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="text-[20px] font-bold tracking-tight text-white">换热器辅助设计系统</div>
          <div className="text-sm text-slate-400">Shell-and-Tube Course Design</div>
        </div>
      </div>
    </div>
  );
}

function SidebarSection({ title, icon: Icon, children }: { title: string; icon: typeof Server; children: ReactNode }) {
  return (
    <div className="rounded-[22px] border border-white/8 bg-white/5 p-3.5 backdrop-blur">
      <div className="mb-3 flex items-center gap-2">
        <div className="flex h-6 w-6 items-center justify-center rounded-full border border-blue-400/25 bg-blue-500/14 text-blue-300">
          <Icon className="h-3.5 w-3.5" />
        </div>
        <div className="text-[15px] font-semibold text-white">{title}</div>
      </div>
      {children}
    </div>
  );
}

function SidebarHealthRow({
  label,
  online,
  statusText,
}: {
  label: string;
  online: boolean;
  statusText?: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/6 bg-slate-950/20 px-3 py-2.5">
      <div className="min-w-0">
        <div className="text-sm font-medium text-slate-200">{label}</div>
        {statusText ? <div className="truncate text-xs text-slate-400">{statusText}</div> : null}
      </div>
      <Badge className={online ? "bg-success text-white hover:bg-success" : "bg-danger text-white hover:bg-danger"}>
        {online ? "在线" : "异常"}
      </Badge>
    </div>
  );
}

function DarkActionButton({
  icon: Icon,
  label,
  onClick,
}: {
  icon: typeof Download;
  label: string;
  onClick: () => Promise<void>;
}) {
  return (
    <Button
      variant="ghost"
      className="h-11 justify-start rounded-2xl border border-white/8 bg-white/4 px-4 text-slate-200 hover:bg-white/8 hover:text-white"
      onClick={() => void onClick()}
    >
      <Icon className="mr-2 h-4 w-4 text-blue-300" />
      {label}
    </Button>
  );
}

function PageHeader({ result }: { result: DesignResultDto | null }) {
  return (
    <div className="flex flex-col gap-4 rounded-[24px] border border-slate-200 bg-white px-5 py-4 shadow-[0_12px_30px_rgba(15,23,42,0.05)] lg:flex-row lg:items-center lg:justify-between">
      <div>
        <div className="text-[34px] font-bold tracking-tight text-slate-950">固定管板式煤油冷却器设计项目</div>
        <div className="mt-1 text-[14px] text-text-secondary">HNU 课程设计项目 / 结构校核 / 计算结果展示</div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Button className="h-11 rounded-2xl bg-[linear-gradient(180deg,#4ea2ff_0%,#2563eb_100%)] px-5 text-sm font-semibold text-white shadow-[0_12px_24px_rgba(37,99,235,0.26)] hover:opacity-95">
          生成设计书(PDF)
        </Button>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-text-secondary">
          <div>数据来源：{result?.dataSource ?? "default"}</div>
          <div className="mt-1 flex items-center gap-1 text-slate-500">
            <Clock3 className="h-3.5 w-3.5" />
            时间：{result?.lastCalculatedAt ?? "尚未计算"}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBanner({
  dashboard,
  isLoading,
  progress,
}: {
  dashboard: DashboardViewModel;
  isLoading: boolean;
  progress: number;
}) {
  const passedCount = dashboard.validationItems.filter((item) => item.passed).length;
  const totalCount = dashboard.validationItems.length;
  const Icon = dashboard.designStatus === "success" ? CheckCircle2 : AlertTriangle;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="overflow-hidden rounded-[24px] border border-emerald-300 bg-[linear-gradient(180deg,#10b154_0%,#139c4d_100%)] px-6 py-5 text-white shadow-[0_16px_36px_rgba(22,163,74,0.24)]"
    >
      <div className="grid gap-4 lg:grid-cols-[1.4fr_1.2fr_0.9fr] lg:items-center">
        <div className="flex items-start gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-white/18">
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[28px] font-bold tracking-tight">{dashboard.statusTitle}</div>
            <div className="text-[15px] text-emerald-50/90">
              {dashboard.designStatus === "success" ? "Feasibility: Qualified" : dashboard.statusTitle}
            </div>
          </div>
        </div>

        <div>
          <div className="text-[22px] font-semibold">方案执行：通过</div>
          <div className="mt-1 text-[15px] text-emerald-50/90">{dashboard.statusMessage}</div>
          {isLoading ? (
            <div className="mt-3 rounded-2xl bg-white/12 px-4 py-3">
              <div className="mb-2 flex items-center justify-between text-xs">
                <span>正在进行计算</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-2 bg-white/20" />
            </div>
          ) : null}
        </div>

        <div className="rounded-[20px] border border-white/14 bg-white/12 px-4 py-4 text-right">
          <div className="text-[16px] font-semibold uppercase tracking-wide text-emerald-50/80">Checks Passed</div>
          <div className="mt-1 text-[34px] font-bold leading-none">
            {passedCount} / {totalCount}
          </div>
          <div className="mt-1 text-sm text-emerald-50/90">关键校核项全部通过</div>
        </div>
      </div>
    </motion.div>
  );
}

function KpiCards({ dashboard, isLoading }: { dashboard: DashboardViewModel; isLoading: boolean }) {
  const items = dashboard.kpis;

  return (
    <div className="grid gap-4 xl:grid-cols-4">
      {items.map((kpi, index) => {
        const isRecommendation = kpi.id === "structure";

        return (
          <motion.div key={kpi.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}>
            <Card className={`h-full rounded-[22px] border bg-white shadow-[0_10px_26px_rgba(15,23,42,0.05)] ${isRecommendation ? "border-blue-300 ring-1 ring-blue-100" : "border-slate-200"}`}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-[15px] font-semibold text-slate-900">
                      {index + 1}. {kpi.title}
                    </div>
                    <div className="mt-1 text-xs text-slate-500">{kpi.description}</div>
                  </div>
                  {isRecommendation ? (
                    <Badge className="bg-emerald-100 text-success hover:bg-emerald-100">Qualified</Badge>
                  ) : null}
                </div>

                <div className="mt-5 min-h-[72px]">
                  {isLoading ? (
                    <Skeleton className="h-12 w-40 rounded-xl" />
                  ) : (
                    <>
                      <div className={`font-bold leading-none text-slate-950 ${isRecommendation ? "text-[30px]" : "text-[50px]"}`}>
                        {kpi.value}
                      </div>
                      {kpi.unit ? <div className="mt-2 text-[18px] font-medium text-slate-700">{kpi.unit}</div> : null}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
}

function ProcessStepper({ dashboard }: { dashboard: DashboardViewModel }) {
  return (
    <Card className="rounded-[24px] border border-slate-200 bg-white shadow-[0_10px_26px_rgba(15,23,42,0.05)]">
      <CardContent className="p-4">
        <div className="flex flex-wrap gap-3">
          {dashboard.processSteps.map((step) => {
            const Icon = getProcessIcon(step.id);
            const isActive = step.state === "active";

            return (
              <div
                key={step.id}
                className={`flex min-w-[180px] flex-1 items-center gap-3 rounded-[18px] border px-4 py-3 ${
                  isActive
                    ? "border-blue-300 bg-blue-50 shadow-[0_8px_20px_rgba(37,99,235,0.08)]"
                    : "border-slate-200 bg-slate-50/80"
                }`}
              >
                <div className={`flex h-10 w-10 items-center justify-center rounded-2xl ${isActive ? "bg-primary text-white" : "bg-white text-primary"}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <div className="text-[14px] font-semibold text-slate-900">{step.title}</div>
                  <div className="truncate text-[13px] text-slate-600">{step.metric}</div>
                </div>
                <ChevronRight className="ml-auto hidden h-4 w-4 text-slate-300 xl:block" />
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

function ResultCardShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <Card className="rounded-[22px] border border-slate-200 bg-white shadow-[0_10px_26px_rgba(15,23,42,0.05)]">
      <CardContent className="p-5">
        <div className="mb-4">
          <div className="text-[18px] font-bold text-slate-950">{title}</div>
          <div className="mt-1 text-[13px] text-slate-500">{subtitle}</div>
        </div>
        {children}
      </CardContent>
    </Card>
  );
}

function InfoGrid({
  items,
  isLoading,
}: {
  items: [string, string][];
  isLoading: boolean;
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {isLoading
        ? Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-24 rounded-2xl" />)
        : items.map(([label, value]) => (
            <div key={label} className="rounded-[18px] bg-[linear-gradient(180deg,#f6f8fc_0%,#f1f5fb_100%)] px-4 py-4">
              <div className="text-[12px] font-medium text-slate-500">{label}</div>
              <div className="mt-3 text-[15px] font-semibold leading-7 text-slate-950">{value}</div>
            </div>
          ))}
    </div>
  );
}

function ValidationCard({ dashboard, isLoading }: { dashboard: DashboardViewModel; isLoading: boolean }) {
  return (
    <ResultCardShell title="工程校核" subtitle="ENGINEERING CHECKS">
      <div className="space-y-3">
        {isLoading
          ? Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="h-14 rounded-2xl" />)
          : dashboard.validationItems.map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-[18px] border border-slate-200 bg-slate-50/70 px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className={`flex h-7 w-7 items-center justify-center rounded-full ${item.passed ? "bg-emerald-100 text-success" : "bg-red-100 text-danger"}`}>
                    {item.passed ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                  </div>
                  <div>
                    <div className="text-[15px] font-medium text-slate-900">{item.label}</div>
                    <div className="text-[13px] text-slate-600">{item.detail}</div>
                  </div>
                </div>
                <div className={`text-sm font-semibold ${item.passed ? "text-success" : "text-danger"}`}>
                  {item.passed ? "(Pass)" : "(Fail)"}
                </div>
              </div>
            ))}
      </div>
    </ResultCardShell>
  );
}

function PigIpCard() {
  return (
    <Card className="overflow-hidden rounded-[24px] border border-slate-200 bg-[linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] shadow-[0_10px_26px_rgba(15,23,42,0.05)]">
      <CardContent className="p-5">
        <div className="grid items-center gap-4 md:grid-cols-[220px_1fr]">
          <div className="flex items-center justify-center">
            <div className="relative rotate-[-5deg] rounded-[28px] border-2 border-white bg-[linear-gradient(180deg,#ffe6ef_0%,#fff5f8_100%)] p-3 shadow-[0_18px_34px_rgba(244,114,182,0.22)]">
              <div className="absolute -right-3 -top-3 rotate-[12deg] rounded-full bg-[#ff7ab6] px-3 py-1 text-[11px] font-bold tracking-wide text-white shadow-[0_8px_18px_rgba(255,122,182,0.34)]">
                OINK!
              </div>
              <div className="absolute -left-2 -top-2 h-5 w-5 rounded-full bg-[#93c5fd] opacity-80" />
              <div className="absolute -bottom-2 right-5 h-4 w-4 rounded-full bg-[#fde68a] opacity-90" />
              <div className="rounded-[22px] bg-white/72 p-3 backdrop-blur">
                <img
                  src="/pig-ip.jpg"
                  alt="小猪 IP 形象"
                  className="h-[180px] w-auto max-w-full object-contain drop-shadow-[0_14px_24px_rgba(244,114,182,0.16)]"
                />
              </div>
            </div>
          </div>

          <div className="flex flex-col justify-center">
            <div className="inline-flex w-fit rounded-full bg-pink-100 px-3 py-1 text-xs font-semibold text-[#db2777]">
              贴纸徽章 IP
            </div>
            <div
              className="mt-3 text-[24px] font-semibold tracking-[0.04em] text-slate-950"
              style={{ fontFamily: '"Georgia", "Times New Roman", "Palatino Linotype", serif', fontStyle: "italic" }}
            >
              manggoopiggg
              2023030505
            </div>
            <div className="mt-2 text-[14px] leading-7 text-slate-600">
              欢迎来到芒果🐖的换热器辅助设计系统！
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function DetailTabs({
  dashboard,
  result,
  activeTab,
  onTabChange,
  isLoading,
}: {
  dashboard: DashboardViewModel;
  result: DesignResultDto | null;
  activeTab: string;
  onTabChange: (tab: string) => void;
  isLoading: boolean;
}) {
  const tabs = [
    ["overview", "传热计算"],
    ["thermal", "结构参数"],
    ["mechanical", "阻力计算详解"],
    ["hydraulic", "计算日志"],
  ];

  return (
    <Tabs value={activeTab} onValueChange={onTabChange} className="space-y-0">
      <Card className="rounded-[24px] border border-slate-200 bg-white shadow-[0_10px_26px_rgba(15,23,42,0.05)]">
        <CardContent className="p-0">
          <div className="border-b border-slate-200 px-4 py-3">
            <TabsList className="h-auto flex-wrap rounded-full bg-slate-100/90 p-1">
              {tabs.map(([value, label]) => (
                <TabsTrigger
                  key={value}
                  value={value}
                  className="rounded-full px-4 py-2.5 text-sm font-medium text-slate-600 data-[state=active]:bg-white data-[state=active]:text-primary data-[state=active]:shadow-sm"
                >
                  {label}
                </TabsTrigger>
              ))}
            </TabsList>
          </div>

          <div className="p-5">
            <AnimatePresence mode="wait">
              <motion.div key={activeTab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.18 }}>
                <TabsContent value="overview" className="mt-0">
                  <ResultTableCard
                    title="传热计算"
                    rows={
                      result
                        ? [
                            ["热负荷 Q", `${(result.thermalResult.heatDutyW / 1000).toFixed(2)} kW`],
                            ["冷却水流量 Wc", `${result.thermalResult.coldMassFlowKgS.toFixed(2)} kg/s`],
                            ["LMTD", `${result.thermalResult.lmtdK.toFixed(2)} K`],
                            ["总传热系数 K", `${result.thermalResult.overallUCalculatedWm2K.toFixed(2)} W/(m²·K)`],
                          ]
                        : []
                    }
                    isLoading={isLoading}
                  />
                </TabsContent>

                <TabsContent value="thermal" className="mt-0">
                  <ResultTableCard
                    title="结构参数"
                    rows={
                      result
                        ? [
                            ["推荐结构", result.mechanicalResult.recommendedStructureText],
                            ["壳程 / 管程", `${result.mechanicalResult.shellPasses} / ${result.mechanicalResult.tubePasses}`],
                            ["每程管数", `${result.mechanicalResult.tubesPerPass} 根`],
                            ["挡板间距", `${result.mechanicalResult.baffleSpacingM.toFixed(4)} m`],
                          ]
                        : []
                    }
                    isLoading={isLoading}
                  />
                </TabsContent>

                <TabsContent value="mechanical" className="mt-0">
                  <ResultTableCard
                    title="阻力计算详解"
                    rows={
                      result
                        ? [
                            ["管程流速", `${result.hydraulicResult.tubeVelocityMS.toFixed(3)} m/s`],
                            ["壳程流速", `${result.hydraulicResult.shellVelocityMS.toFixed(3)} m/s`],
                            ["管程压降", `${(result.hydraulicResult.tubePressureDropPa / 1000).toFixed(2)} kPa`],
                            ["壳程压降", `${(result.hydraulicResult.shellPressureDropPa / 1000).toFixed(2)} kPa`],
                          ]
                        : []
                    }
                    isLoading={isLoading}
                  />
                </TabsContent>

                <TabsContent value="hydraulic" className="mt-0">
                  <ResultTableCard
                    title="计算日志"
                    rows={(result?.logs ?? []).map((log, index) => [`日志 ${index + 1}`, log])}
                    isLoading={isLoading}
                  />
                </TabsContent>
              </motion.div>
            </AnimatePresence>
          </div>
        </CardContent>
      </Card>
    </Tabs>
  );
}

function InputSections({
  formValues,
  onUpdateField,
  errors,
}: {
  formValues: DesignFormValues;
  onUpdateField: ReturnType<typeof useDesignCalculation>["updateField"];
  errors: ReturnType<typeof useDesignCalculation>["errors"];
}) {
  return (
    <ScrollArea className="max-h-[520px] pr-1">
      <Accordion type="multiple" defaultValue={["condition", "structure", "constraints", "assumptions"]} className="space-y-3">
        <InputSectionCard title="工况参数" subtitle="热工边界与进出口条件" value="condition">
          <FieldRow label="煤油质量流量" unit="kg/s" value={String(formValues.operatingCondition.hotMassFlowKgS)} onChange={(value) => onUpdateField("operatingCondition", "hotMassFlowKgS", Number(value))} error={errors["operatingCondition.hotMassFlowKgS"]} />
          <FieldRow label="煤油入口温度" unit="℃" value={String(formValues.operatingCondition.hotInletTempC)} onChange={(value) => onUpdateField("operatingCondition", "hotInletTempC", Number(value))} />
          <FieldRow label="煤油出口温度" unit="℃" value={String(formValues.operatingCondition.hotOutletTempC)} onChange={(value) => onUpdateField("operatingCondition", "hotOutletTempC", Number(value))} error={errors["operatingCondition.hotOutletTempC"]} />
          <FieldRow label="冷却水入口温度" unit="℃" value={String(formValues.operatingCondition.coldInletTempC)} onChange={(value) => onUpdateField("operatingCondition", "coldInletTempC", Number(value))} />
          <FieldRow label="冷却水出口温度" unit="℃" value={String(formValues.operatingCondition.coldOutletTempC)} onChange={(value) => onUpdateField("operatingCondition", "coldOutletTempC", Number(value))} error={errors["operatingCondition.coldOutletTempC"]} />
        </InputSectionCard>

        <InputSectionCard title="结构预设" subtitle="几何尺寸与流程配置" value="structure">
          <FieldRow label="管外径" unit="m" value={String(formValues.assumptions.tubeOuterDiameterM)} onChange={(value) => onUpdateField("assumptions", "tubeOuterDiameterM", Number(value))} />
          <FieldRow label="管内径" unit="m" value={String(formValues.assumptions.tubeInnerDiameterM)} onChange={(value) => onUpdateField("assumptions", "tubeInnerDiameterM", Number(value))} error={errors["assumptions.tubeInnerDiameterM"]} />
          <FieldRow label="管程数" unit="-" value={String(formValues.assumptions.tubePasses)} onChange={(value) => onUpdateField("assumptions", "tubePasses", Number(value))} error={errors["assumptions.tubePasses"]} />
          <FieldRow label="壳程数" unit="-" value={String(formValues.assumptions.shellPasses)} onChange={(value) => onUpdateField("assumptions", "shellPasses", Number(value))} />
          <FieldRow
            label="管长候选"
            unit="m"
            value={formValues.assumptions.tubeLengthCandidatesM.join(", ")}
            onChange={(value) =>
              onUpdateField(
                "assumptions",
                "tubeLengthCandidatesM",
                value
                  .split(",")
                  .map((item) => Number(item.trim()))
                  .filter((item) => !Number.isNaN(item) && item > 0),
              )
            }
            error={errors["assumptions.tubeLengthCandidatesM"]}
          />
        </InputSectionCard>

        <InputSectionCard title="约束与假设" subtitle="流速、压降与初算参数" value="constraints">
          <FieldRow label="管程最小流速" unit="m/s" value={String(formValues.constraints.tubeVelocityMinMS)} onChange={(value) => onUpdateField("constraints", "tubeVelocityMinMS", Number(value))} />
          <FieldRow label="管程最大流速" unit="m/s" value={String(formValues.constraints.tubeVelocityMaxMS)} onChange={(value) => onUpdateField("constraints", "tubeVelocityMaxMS", Number(value))} />
          <FieldRow label="许用管程压降" unit="Pa" value={String(formValues.constraints.allowableTubePressureDropPa)} onChange={(value) => onUpdateField("constraints", "allowableTubePressureDropPa", Number(value))} />
          <FieldRow label="许用壳程压降" unit="Pa" value={String(formValues.constraints.allowableShellPressureDropPa)} onChange={(value) => onUpdateField("constraints", "allowableShellPressureDropPa", Number(value))} />
          <FieldRow label="初选总传热系数 U" unit="W/(m²·K)" value={String(formValues.assumptions.initialOverallUWm2K)} onChange={(value) => onUpdateField("assumptions", "initialOverallUWm2K", Number(value))} />
        </InputSectionCard>

        <InputSectionCard title="工程附加参数" subtitle="节距、布管角与挡板经验值" value="assumptions">
          <FieldRow label="管间距比" unit="-" value={String(formValues.assumptions.pitchRatio)} onChange={(value) => onUpdateField("assumptions", "pitchRatio", Number(value))} />
          <FieldRow label="布管角" unit="deg" value={String(formValues.assumptions.layoutAngleDeg)} onChange={(value) => onUpdateField("assumptions", "layoutAngleDeg", Number(value))} />
          <FieldRow label="挡板间距比" unit="-" value={String(formValues.assumptions.baffleSpacingRatio)} onChange={(value) => onUpdateField("assumptions", "baffleSpacingRatio", Number(value))} />
          <FieldRow label="壳体间隙" unit="m" value={String(formValues.assumptions.shellClearanceM)} onChange={(value) => onUpdateField("assumptions", "shellClearanceM", Number(value))} />
        </InputSectionCard>
      </Accordion>
    </ScrollArea>
  );
}

function InputSectionCard({
  title,
  subtitle,
  value,
  children,
}: {
  title: string;
  subtitle: string;
  value: string;
  children: ReactNode;
}) {
  return (
    <AccordionItem value={value} className="rounded-[18px] border border-white/8 bg-slate-900/18 px-3">
      <AccordionTrigger className="py-3 text-left no-underline hover:no-underline">
        <div>
          <div className="text-[15px] font-semibold text-white">{title}</div>
          <div className="mt-1 text-xs text-slate-400">{subtitle}</div>
        </div>
      </AccordionTrigger>
      <AccordionContent className="space-y-3 pb-3">{children}</AccordionContent>
    </AccordionItem>
  );
}

function FileInputButton({
  label,
  accept,
  icon: Icon,
  onFile,
}: {
  label: string;
  accept: string;
  icon: typeof Upload;
  onFile: (file: File) => Promise<void>;
}) {
  return (
    <label className="block cursor-pointer">
      <input
        type="file"
        accept={accept}
        className="hidden"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void onFile(file);
          event.currentTarget.value = "";
        }}
      />
      <div className="flex h-11 items-center rounded-2xl border border-white/8 bg-white/6 px-4 text-sm text-slate-100 transition hover:bg-white/10">
        <Icon className="mr-2 h-4 w-4 text-blue-300" />
        {label}
        <Upload className="ml-auto h-4 w-4 text-slate-400" />
      </div>
    </label>
  );
}

function ExportButton({
  label,
  icon: Icon,
  disabled,
  tip,
  onClick,
}: {
  label: string;
  icon: typeof FileText;
  disabled: boolean;
  tip: string;
  onClick: () => Promise<void>;
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div>
          <Button
            disabled={disabled}
            variant="ghost"
            className="h-11 w-full justify-start rounded-2xl border border-white/8 bg-white/4 text-slate-100 hover:bg-white/8 disabled:border-white/6 disabled:bg-white/[0.03] disabled:text-slate-500"
            onClick={() => void onClick()}
          >
            <Icon className="mr-2 h-4 w-4 text-blue-300" />
            {label}
          </Button>
        </div>
      </TooltipTrigger>
      <TooltipContent>{disabled ? tip : "导出当前结果"}</TooltipContent>
    </Tooltip>
  );
}

function FieldRow({
  label,
  unit,
  value,
  onChange,
  error,
}: {
  label: string;
  unit: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-[12px]">
        <Label className="font-medium text-slate-200">{label}</Label>
        <span className="text-slate-400">{unit}</span>
      </div>
      <Input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-10 rounded-xl border-white/10 bg-white px-3 text-slate-950 placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
      />
      {error ? <p className="text-[12px] text-red-300">{error}</p> : null}
    </div>
  );
}

function ResultTableCard({
  title,
  rows,
  isLoading,
}: {
  title: string;
  rows: [string, string][];
  isLoading: boolean;
}) {
  return (
    <Card className="border-slate-200 bg-white shadow-none">
      <CardContent className="p-0">
        <div className="border-b border-slate-200 px-4 py-3">
          <div className="text-[16px] font-semibold text-slate-950">{title}</div>
        </div>
        <div className="space-y-2 p-4">
          {isLoading
            ? Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-14 rounded-2xl" />)
            : rows.map(([label, value]) => (
                <div key={label} className="flex items-center justify-between rounded-[16px] bg-slate-50 px-4 py-3">
                  <span className="text-sm text-slate-600">{label}</span>
                  <span className="text-sm font-semibold text-slate-950">{value}</span>
                </div>
              ))}
        </div>
      </CardContent>
    </Card>
  );
}

function SummaryLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-slate-600">{label}</span>
      <span className="text-right font-semibold text-slate-950">{value}</span>
    </div>
  );
}
