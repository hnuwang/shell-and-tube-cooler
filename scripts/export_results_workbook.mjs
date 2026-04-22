import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [, , payloadPath, outputPath] = process.argv;

if (!payloadPath || !outputPath) {
  console.error("Usage: node export_results_workbook.mjs <payload.json> <output.xlsx>");
  process.exit(1);
}

const payload = JSON.parse(await fs.readFile(payloadPath, "utf8"));
const workbook = Workbook.create();

function addTableSheet(workbookRef, sheetName, rows) {
  const sheet = workbookRef.worksheets.add(sheetName);
  if (!rows.length) {
    sheet.getRange("A1").values = [["No data"]];
    return;
  }

  const headers = Object.keys(rows[0]);
  const matrix = [headers, ...rows.map((row) => headers.map((header) => row[header]))];
  const endColumn = String.fromCharCode(64 + headers.length);
  sheet.getRange(`A1:${endColumn}${matrix.length}`).values = matrix;
  sheet.getRange(`A1:${endColumn}1`).format = {
    fill: "#0F766E",
    font: { bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
  };
  const bodyRange = sheet.getRange(`A2:${endColumn}${matrix.length}`);
  bodyRange.format.wrapText = true;
  bodyRange.format.autofitColumns();
  sheet.freezePanes.freezeRows(1);
}

const summarySheet = workbook.worksheets.add("Summary");
summarySheet.getRange("A1:D1").merge();
summarySheet.getRange("A1").values = [["固定管板式管壳式煤油冷却器结果总览"]];
summarySheet.getRange("A1").format = {
  fill: "#1D4ED8",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
};

summarySheet.getRange("A3:B9").values = [
  ["项目", "数值"],
  ["热负荷 (W)", payload.summary.heat_duty_w],
  ["冷却水流量 (kg/s)", payload.summary.cold_mass_flow_kg_s],
  ["所需面积 (m2)", payload.summary.required_area_m2],
  ["实际面积 (m2)", payload.summary.actual_area_m2],
  ["管程压降 (Pa)", payload.summary.tube_pressure_drop_pa],
  ["壳程压降 (Pa)", payload.summary.shell_pressure_drop_pa],
];
summarySheet.getRange("A3:B3").format = {
  fill: "#2563EB",
  font: { bold: true, color: "#FFFFFF" },
};
summarySheet.getRange("A3:B9").format.autofitColumns();
summarySheet.getRange("D3:E4").values = [
  ["方案状态", payload.summary.design_state],
  ["说明", payload.summary.design_state === "可行" ? "满足面积与压降约束" : "需调整参数"],
];
summarySheet.getRange("D3:E3").format = {
  fill: payload.summary.design_state === "可行" ? "#16A34A" : "#DC2626",
  font: { bold: true, color: "#FFFFFF" },
};
summarySheet.getRange("D3:E4").format.autofitColumns();

addTableSheet(workbook, "Inputs", payload.result_tables.input);
addTableSheet(workbook, "Properties", payload.result_tables.properties);
addTableSheet(workbook, "Thermal", payload.result_tables.thermal);
addTableSheet(workbook, "Mechanical", payload.result_tables.mechanical);
addTableSheet(workbook, "Hydraulic", payload.result_tables.hydraulic);

await fs.mkdir(path.dirname(outputPath), { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);
