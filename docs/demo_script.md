# 2-Minute Demo Script

Hi, this is my Supply Chain Risk and Performance Command Center, an end-to-end data analyst project built using Excel, Power BI planning assets, SQL, and Python.

The business goal is to help a supply-chain team identify where delivery risk, supplier issues, and disruption exposure are concentrated.

The dataset comes from Kaggle's US Supply Chain Risk Analysis Dataset. It includes one thousand orders with supplier IDs, product categories, shipping modes, order values, delay days, disruption types, supplier reliability scores, energy usage, communication cost, and supply risk flags.

First, I used Python to clean the raw data and create new analytical fields such as delayed order flag, cycle time, risk label, delay bucket, supplier reliability band, and a composite risk score.

Then I created processed tables for executive KPIs, monthly trends, supplier scorecards, category performance, shipping performance, and disruption analysis.

In Excel, I built an executive dashboard with KPI cards for total orders, total order value, delay rate, risk rate, average delay days, and high-risk orders. The workbook also includes trend charts, category analysis, and a supplier risk watchlist.

For SQL, I created a SQLite database and wrote business queries to identify top risky suppliers, delayed-value exposure by category, disruption impact, and monthly performance trends.

For Power BI, I prepared a full report blueprint, DAX measures, and Power Query transformation steps so the report can be recreated as a professional BI dashboard.

The key insight is that over half of orders are delayed or risk-flagged, so the business should focus first on high-risk suppliers, high-value categories, and disruption types with the longest average delays.

This project demonstrates the full analyst workflow: data cleaning, KPI design, SQL analysis, Excel dashboards, Power BI modeling, and executive storytelling.

