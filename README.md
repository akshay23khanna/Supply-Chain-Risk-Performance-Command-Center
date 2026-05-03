# Supply Chain Risk & Performance Command Center

An end-to-end data analyst portfolio project using a Kaggle supply-chain dataset to identify delivery delays, high-risk suppliers, disruption patterns, logistics efficiency, and executive action priorities.

## Business Problem

Supply-chain teams need to know where operational risk is concentrated before delays become expensive. This project answers:

- Which suppliers create the highest risk exposure?
- Which product categories carry the largest delayed-value exposure?
- Which disruption types and shipping modes drive delays?
- How are risk and delay rates trending over time?
- What actions should leadership take first?

## Dataset

Source: [Kaggle - US Supply Chain Risk Analysis Dataset](https://www.kaggle.com/datasets/yuanchunhong/us-supply-chain-risk-analysis-dataset)

The dataset contains 1,000 supply-chain orders with fields for order value, quantity, supplier, product category, shipping mode, disruption type, delay days, supplier reliability, energy consumption, communication cost, and supply risk flags.

## Tools Used

- **Excel**: executive KPI dashboard, charts, supplier scorecard, monthly trend analysis
- **Power BI**: DAX measures, Power Query transformations, report blueprint
- **SQL / SQLite**: business question queries and reusable database
- **Python**: data cleaning, feature engineering, KPI tables, risk scoring
- **GitHub**: project documentation and version control

## Project Highlights

- Built a clean analytics fact table from raw Kaggle data
- Engineered delay flags, risk tiers, reliability bands, cycle time, and composite risk score
- Created executive KPI tables and supplier/category/shipping scorecards
- Built SQL queries for stakeholder business questions
- Created an Excel dashboard workbook with KPI cards and charts
- Prepared Power BI DAX measures and report design documentation

## Key Insights

- Overall delay rate is **51.4%** across 1,000 orders.
- Supply risk rate is **51.4%**, showing a strong monitoring opportunity.
- Highest-risk supplier is **S21** with an average risk score of **44.1**.
- Largest value category is **Electronics** with about **$5.69M** in order value.

## Folder Structure

```text
data/
  raw/                         Kaggle source data
  processed/                   Cleaned data and dashboard tables
excel/
  supply_chain_risk_dashboard.xlsx
powerbi/
  dax_measures.md
  power_query_m.md
  report_blueprint.md
sql/
  supply_chain_risk.db
  01_business_questions.sql
scripts/
  build_analysis.py
  build_excel_dashboard.mjs
docs/
  executive_insights.md
  project_metadata.json
visuals/
  excel_dashboard_preview.png
```

## How to Run

Install Python dependencies if needed:

```bash
pip install pandas numpy
```

Run the data pipeline:

```bash
python scripts/build_analysis.py
```

Build the Excel dashboard:

```bash
node scripts/build_excel_dashboard.mjs
```

## Deliverables

- Excel dashboard: `excel/supply_chain_risk_dashboard.xlsx`
- Clean dataset: `data/processed/clean_supply_chain_orders.csv`
- SQLite database: `sql/supply_chain_risk.db`
- SQL analysis: `sql/01_business_questions.sql`
- Power BI guide: `powerbi/report_blueprint.md`
- DAX measures: `powerbi/dax_measures.md`

## Recommended Power BI Pages

1. Executive Overview
2. Supplier Risk
3. Logistics & Disruptions
4. Action Plan

The Power BI files include exact DAX measures and Power Query steps so the report can be recreated quickly in Power BI Desktop.

