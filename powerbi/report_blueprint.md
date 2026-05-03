# Power BI Report Blueprint

## Page 1: Executive Overview

Purpose: show leadership whether supply-chain performance is improving or deteriorating.

Visuals:
- KPI cards: Total Orders, Total Order Value, Delay Rate, Risk Rate, Average Delay Days
- Line chart: Order Month vs Delay Rate and Risk Rate
- Bar chart: Product Category by Total Order Value
- Donut chart: Risk Tier share
- Slicers: Product Category, Shipping Mode, Disruption Type, Risk Tier

## Page 2: Supplier Risk

Purpose: identify suppliers that need renegotiation, monitoring, or backup supplier plans.

Visuals:
- Table: Supplier ID, Orders, Total Order Value, Delay Rate, Risk Rate, Avg Risk Score, Reliability Score
- Scatter chart: Supplier Reliability Score vs Average Delay Days, bubble size = Order Value
- Bar chart: Top 10 Suppliers by Average Risk Score
- Conditional formatting: Avg Risk Score red above 50, amber 25-50, green below 25

## Page 3: Logistics & Disruptions

Purpose: connect shipping choices and disruption types to delay exposure.

Visuals:
- Bar chart: Shipping Mode by Average Delay Days
- Bar chart: Disruption Type by Orders
- Matrix: Disruption Type x Severity with Average Delay Days
- KPI cards: Average Energy Consumption, Average Communication Cost MB

## Page 4: Action Plan

Purpose: translate analytics into decisions.

Visuals:
- High-risk supplier watchlist
- Delayed-value exposure by category
- Recommended actions:
  - Prioritize backup suppliers for top high-risk suppliers
  - Monitor suppliers with low reliability and high order value
  - Review shipping modes with high average delay and high energy consumption
  - Build exception alerts for disruptions with severe delay patterns

