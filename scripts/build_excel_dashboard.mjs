import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const ROOT = new URL('../', import.meta.url);
const outDir = new URL('../excel/', import.meta.url);

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(',');
  return lines.slice(1).map((line) => {
    const values = line.split(',');
    return Object.fromEntries(headers.map((h, i) => [h, values[i] ?? '']));
  });
}

function number(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function pct(value) {
  return number(value);
}

async function loadCsv(relativePath) {
  const text = await fs.readFile(new URL(relativePath, ROOT), 'utf8');
  return parseCsv(text);
}

function writeTable(sheet, startCell, headers, rows) {
  const range = sheet.getRange(startCell).resize(rows.length + 1, headers.length);
  range.values = [headers, ...rows];
  range.format = {
    font: { name: 'Aptos', size: 10 },
    borders: { insideHorizontal: { style: 'Continuous', color: '#E5E7EB' } },
  };
  const headerRange = sheet.getRange(startCell).resize(1, headers.length);
  headerRange.format = {
    fill: '#111827',
    font: { bold: true, color: '#FFFFFF' },
  };
  return range;
}

function styleSheet(sheet) {
  sheet.showGridLines = false;
  sheet.getRange('A:Z').format = { font: { name: 'Aptos', size: 10 } };
}

const monthly = await loadCsv('data/processed/monthly_summary.csv');
const suppliers = await loadCsv('data/processed/supplier_scorecard.csv');
const categories = await loadCsv('data/processed/category_summary.csv');
const shipping = await loadCsv('data/processed/shipping_summary.csv');
const disruptions = await loadCsv('data/processed/disruption_summary.csv');
const kpis = await loadCsv('data/processed/executive_kpis.csv');

const wb = Workbook.create();
const dashboard = wb.worksheets.add('Executive Dashboard');
const supplierSheet = wb.worksheets.add('Supplier Scorecard');
const monthlySheet = wb.worksheets.add('Monthly Trends');
const categorySheet = wb.worksheets.add('Category Logistics');
const dataDict = wb.worksheets.add('Data Dictionary');

for (const sheet of [dashboard, supplierSheet, monthlySheet, categorySheet, dataDict]) {
  styleSheet(sheet);
}

dashboard.getRange('A1:H1').merge();
dashboard.getRange('A1').values = [['Supply Chain Risk & Performance Command Center']];
dashboard.getRange('A1').format = {
  fill: '#0F172A',
  font: { bold: true, color: '#FFFFFF', size: 18 },
};
dashboard.getRange('A2:H2').merge();
dashboard.getRange('A2').values = [['Executive view of delay exposure, supplier risk, disruption impact, and logistics performance.']];
dashboard.getRange('A2').format = { fill: '#E0F2FE', font: { color: '#075985', size: 11 } };

const kpiMap = Object.fromEntries(kpis.map((r) => [r.metric, number(r.value)]));
const kpiCards = [
  ['Total Orders', kpiMap['Total Orders'], '0'],
  ['Total Order Value', kpiMap['Total Order Value'], '$#,##0'],
  ['Delay Rate', kpiMap['Delay Rate'], '0.0%'],
  ['Risk Rate', kpiMap['Risk Rate'], '0.0%'],
  ['Avg Delay Days', kpiMap['Average Delay Days'], '0.0'],
  ['High Risk Orders', kpiMap['High Risk Orders'], '0'],
];

let col = 1;
for (const [label, value, fmt] of kpiCards) {
  const cell = dashboard.getCell(3, col - 1);
  const valueCell = dashboard.getCell(4, col - 1);
  cell.values = [[label]];
  valueCell.values = [[value]];
  dashboard.getRangeByIndexes(3, col - 1, 2, 1).format = {
    fill: '#F8FAFC',
    borders: { outline: { style: 'Continuous', color: '#CBD5E1' } },
  };
  cell.format = { font: { bold: true, color: '#475569' } };
  valueCell.format = { font: { bold: true, color: '#0F172A', size: 14 } };
  valueCell.format.numberFormat = fmt;
  col += 1;
}

const monthlyRows = monthly.map((r) => [
  r.order_month,
  number(r.orders),
  number(r.order_value_usd),
  pct(r.delay_rate),
  pct(r.risk_rate),
  number(r.avg_risk_score),
]);
writeTable(dashboard, 'A8', ['Month', 'Orders', 'Order Value', 'Delay Rate', 'Risk Rate', 'Avg Risk Score'], monthlyRows);
dashboard.getRange('C9:C25').format.numberFormat = '$#,##0';
dashboard.getRange('D9:E25').format.numberFormat = '0.0%';
dashboard.getRange('F9:F25').format.numberFormat = '0.0';

const categoryRows = categories.map((r) => [
  r.product_category,
  number(r.orders),
  number(r.order_value_usd),
  pct(r.delay_rate),
  pct(r.risk_rate),
  number(r.avg_risk_score),
]);
writeTable(dashboard, 'H8', ['Category', 'Orders', 'Order Value', 'Delay Rate', 'Risk Rate', 'Risk Score'], categoryRows);
dashboard.getRange('J9:J20').format.numberFormat = '$#,##0';
dashboard.getRange('K9:L20').format.numberFormat = '0.0%';

const chart1 = dashboard.charts.add('line', dashboard.getRange('A8:F21'));
chart1.title = 'Monthly Risk and Delay Trend';
chart1.hasLegend = true;
chart1.xAxis = { axisType: 'textAxis' };
chart1.yAxis = { numberFormatCode: '0.0%' };
chart1.setPosition('A25', 'G42');

const chart2 = dashboard.charts.add('bar', dashboard.getRange('H8:J13'));
chart2.title = 'Order Value by Product Category';
chart2.hasLegend = false;
chart2.yAxis = { numberFormatCode: '$#,##0' };
chart2.setPosition('H25', 'N42');

const topSuppliers = suppliers.slice(0, 15).map((r) => [
  r.supplier_id,
  number(r.orders),
  number(r.order_value_usd),
  pct(r.delay_rate),
  pct(r.risk_rate),
  number(r.supplier_reliability_score),
  number(r.avg_risk_score),
]);
writeTable(
  supplierSheet,
  'A1',
  ['Supplier', 'Orders', 'Order Value', 'Delay Rate', 'Risk Rate', 'Reliability', 'Risk Score'],
  topSuppliers
);
supplierSheet.getRange('C2:C16').format.numberFormat = '$#,##0';
supplierSheet.getRange('D2:E16').format.numberFormat = '0.0%';
supplierSheet.getRange('F2:G16').format.numberFormat = '0.0';
supplierSheet.freezePanes.freezeRows(1);
const chart3 = supplierSheet.charts.add('bar', supplierSheet.getRange('A1:G16'));
chart3.title = 'Top Supplier Risk Watchlist';
chart3.setPosition('I2', 'Q22');

writeTable(monthlySheet, 'A1', ['Month', 'Orders', 'Order Value', 'Delay Rate', 'Risk Rate', 'Avg Risk Score'], monthlyRows);
monthlySheet.getRange('C2:C25').format.numberFormat = '$#,##0';
monthlySheet.getRange('D2:E25').format.numberFormat = '0.0%';
const chart4 = monthlySheet.charts.add('line', monthlySheet.getRange('A1:F14'));
chart4.title = 'Monthly Orders, Value, Delay Rate, and Risk Rate';
chart4.setPosition('H2', 'P22');

const shippingRows = shipping.map((r) => [
  r.shipping_mode,
  number(r.orders),
  number(r.order_value_usd),
  pct(r.delay_rate),
  pct(r.risk_rate),
  number(r.avg_energy_joules),
  number(r.avg_comm_cost_mb),
  number(r.avg_risk_score),
]);
writeTable(
  categorySheet,
  'A1',
  ['Shipping Mode', 'Orders', 'Order Value', 'Delay Rate', 'Risk Rate', 'Avg Energy', 'Avg Comm MB', 'Risk Score'],
  shippingRows
);
categorySheet.getRange('C2:C10').format.numberFormat = '$#,##0';
categorySheet.getRange('D2:E10').format.numberFormat = '0.0%';

const disruptionRows = disruptions.slice(0, 12).map((r) => [
  r.disruption_type,
  r.disruption_severity,
  number(r.orders),
  number(r.order_value_usd),
  number(r.avg_delay_days),
  number(r.avg_risk_score),
]);
writeTable(categorySheet, 'J1', ['Disruption', 'Severity', 'Orders', 'Order Value', 'Avg Delay', 'Risk Score'], disruptionRows);
categorySheet.getRange('M2:M20').format.numberFormat = '$#,##0';

writeTable(dataDict, 'A1', ['Field', 'Description'], [
  ['order_value_usd', 'Order value exposed to logistics and supplier performance risk.'],
  ['delay_days', 'Days of delay. Positive values indicate delayed orders.'],
  ['supply_risk_flag', 'Binary risk flag supplied by the Kaggle dataset.'],
  ['risk_score', 'Composite score created from risk flag, delay, reliability, disruption history, and parameter change.'],
  ['risk_tier', 'Low, Medium, or High grouping based on the composite risk score.'],
  ['supplier_reliability_score', 'Supplier reliability measure from the dataset.'],
  ['energy_consumption_joules', 'Energy consumption proxy for sustainability/logistics analysis.'],
  ['communication_cost_mb', 'Communication overhead proxy for federated supply-chain coordination.'],
]);

for (const sheet of [dashboard, supplierSheet, monthlySheet, categorySheet, dataDict]) {
  sheet.getUsedRange().format.autofitColumns();
  sheet.getUsedRange().format.autofitRows();
}

await fs.mkdir(outDir, { recursive: true });
const preview = await wb.render({ sheetName: 'Executive Dashboard', autoCrop: 'all', scale: 1, format: 'png' });
await fs.writeFile(new URL('../visuals/excel_dashboard_preview.png', import.meta.url), new Uint8Array(await preview.arrayBuffer()));

const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(fileURLToPath(new URL('../excel/supply_chain_risk_dashboard.xlsx', import.meta.url)));
