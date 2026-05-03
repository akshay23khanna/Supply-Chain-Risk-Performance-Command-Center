from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "data.csv"
OUT = ROOT / "data" / "processed"
SQL_DIR = ROOT / "sql"
VISUALS = ROOT / "visuals"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def build_clean_dataset() -> pd.DataFrame:
    df = normalize_columns(pd.read_csv(RAW))

    for col in ["order_date", "dispatch_date", "delivery_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["cycle_time_days"] = (df["delivery_date"] - df["order_date"]).dt.days
    df["dispatch_lag_days"] = (df["dispatch_date"] - df["order_date"]).dt.days
    df["is_delayed"] = (df["delay_days"] > 0).astype(int)
    df["risk_label"] = np.where(df["supply_risk_flag"] == 1, "At Risk", "Stable")
    df["delay_bucket"] = pd.cut(
        df["delay_days"],
        bins=[-1, 0, 3, 7, 999],
        labels=["On time", "1-3 days", "4-7 days", "8+ days"],
    ).astype(str)
    df["reliability_band"] = pd.cut(
        df["supplier_reliability_score"],
        bins=[0, 0.70, 0.85, 1.00],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    ).astype(str)
    df["risk_score"] = (
        35 * df["supply_risk_flag"]
        + 25 * np.minimum(df["delay_days"] / 10, 1)
        + 20 * (1 - df["supplier_reliability_score"])
        + 10 * np.minimum(df["historical_disruption_count"] / 20, 1)
        + 10 * np.minimum(df["parameter_change_magnitude"] / df["parameter_change_magnitude"].max(), 1)
    ).round(1)
    df["risk_tier"] = pd.cut(
        df["risk_score"],
        bins=[-1, 25, 50, 100],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    return df


def weighted_avg(series: pd.Series, weights: pd.Series) -> float:
    return float(np.average(series, weights=weights)) if weights.sum() else 0.0


def make_summary_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    monthly = (
        df.groupby("order_month", as_index=False)
        .agg(
            orders=("order_id", "count"),
            order_value_usd=("order_value_usd", "sum"),
            delayed_orders=("is_delayed", "sum"),
            avg_delay_days=("delay_days", "mean"),
            risk_orders=("supply_risk_flag", "sum"),
            avg_risk_score=("risk_score", "mean"),
        )
        .sort_values("order_month")
    )
    monthly["delay_rate"] = monthly["delayed_orders"] / monthly["orders"]
    monthly["risk_rate"] = monthly["risk_orders"] / monthly["orders"]

    supplier = (
        df.groupby("supplier_id", as_index=False)
        .agg(
            orders=("order_id", "count"),
            order_value_usd=("order_value_usd", "sum"),
            delayed_orders=("is_delayed", "sum"),
            avg_delay_days=("delay_days", "mean"),
            risk_orders=("supply_risk_flag", "sum"),
            supplier_reliability_score=("supplier_reliability_score", "mean"),
            historical_disruption_count=("historical_disruption_count", "mean"),
            avg_risk_score=("risk_score", "mean"),
        )
        .sort_values(["avg_risk_score", "order_value_usd"], ascending=[False, False])
    )
    supplier["delay_rate"] = supplier["delayed_orders"] / supplier["orders"]
    supplier["risk_rate"] = supplier["risk_orders"] / supplier["orders"]

    category = (
        df.groupby("product_category", as_index=False)
        .agg(
            orders=("order_id", "count"),
            order_value_usd=("order_value_usd", "sum"),
            delayed_orders=("is_delayed", "sum"),
            avg_delay_days=("delay_days", "mean"),
            risk_orders=("supply_risk_flag", "sum"),
            avg_risk_score=("risk_score", "mean"),
        )
        .sort_values("order_value_usd", ascending=False)
    )
    category["delay_rate"] = category["delayed_orders"] / category["orders"]
    category["risk_rate"] = category["risk_orders"] / category["orders"]

    shipping = (
        df.groupby("shipping_mode", as_index=False)
        .agg(
            orders=("order_id", "count"),
            order_value_usd=("order_value_usd", "sum"),
            delayed_orders=("is_delayed", "sum"),
            avg_delay_days=("delay_days", "mean"),
            risk_orders=("supply_risk_flag", "sum"),
            avg_energy_joules=("energy_consumption_joules", "mean"),
            avg_comm_cost_mb=("communication_cost_mb", "mean"),
            avg_risk_score=("risk_score", "mean"),
        )
        .sort_values("avg_risk_score", ascending=False)
    )
    shipping["delay_rate"] = shipping["delayed_orders"] / shipping["orders"]
    shipping["risk_rate"] = shipping["risk_orders"] / shipping["orders"]

    disruption = (
        df.groupby(["disruption_type", "disruption_severity"], as_index=False)
        .agg(
            orders=("order_id", "count"),
            order_value_usd=("order_value_usd", "sum"),
            avg_delay_days=("delay_days", "mean"),
            avg_risk_score=("risk_score", "mean"),
        )
        .sort_values("orders", ascending=False)
    )

    executive = pd.DataFrame(
        [
            ["Total Orders", len(df), "Number of supply-chain transactions"],
            ["Total Order Value", df["order_value_usd"].sum(), "Revenue/value exposed to supply-chain performance"],
            ["Delay Rate", df["is_delayed"].mean(), "Share of orders with positive delay days"],
            ["Risk Rate", df["supply_risk_flag"].mean(), "Share of orders flagged as supply risk"],
            ["Average Delay Days", df["delay_days"].mean(), "Average delay across all orders"],
            ["Average Supplier Reliability", df["supplier_reliability_score"].mean(), "Mean supplier reliability score"],
            ["High Risk Orders", int((df["risk_tier"] == "High").sum()), "Orders with modeled risk score above 50"],
        ],
        columns=["metric", "value", "definition"],
    )

    return {
        "monthly_summary": monthly,
        "supplier_scorecard": supplier,
        "category_summary": category,
        "shipping_summary": shipping,
        "disruption_summary": disruption,
        "executive_kpis": executive,
    }


def write_sql_assets(df: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    db_path = SQL_DIR / "supply_chain_risk.db"
    with sqlite3.connect(db_path) as conn:
        df.to_sql("fact_orders", conn, if_exists="replace", index=False)
        for name, table in tables.items():
            table.to_sql(name, conn, if_exists="replace", index=False)

    (SQL_DIR / "01_business_questions.sql").write_text(
        """-- Supply Chain Risk Analytics: Business Questions

-- 1. Which suppliers create the highest combined value and risk exposure?
SELECT
  supplier_id,
  orders,
  ROUND(order_value_usd, 2) AS order_value_usd,
  ROUND(delay_rate * 100, 1) AS delay_rate_pct,
  ROUND(risk_rate * 100, 1) AS risk_rate_pct,
  ROUND(avg_risk_score, 1) AS avg_risk_score
FROM supplier_scorecard
ORDER BY avg_risk_score DESC, order_value_usd DESC
LIMIT 10;

-- 2. Which product categories carry the largest delayed-value exposure?
SELECT
  product_category,
  orders,
  ROUND(order_value_usd, 2) AS order_value_usd,
  ROUND(delay_rate * 100, 1) AS delay_rate_pct,
  ROUND(avg_delay_days, 2) AS avg_delay_days
FROM category_summary
ORDER BY order_value_usd * delay_rate DESC;

-- 3. Which disruption types drive the longest delays?
SELECT
  disruption_type,
  disruption_severity,
  orders,
  ROUND(avg_delay_days, 2) AS avg_delay_days,
  ROUND(avg_risk_score, 1) AS avg_risk_score
FROM disruption_summary
WHERE disruption_type <> 'None'
ORDER BY avg_delay_days DESC;

-- 4. How does performance trend monthly?
SELECT
  order_month,
  orders,
  ROUND(order_value_usd, 2) AS order_value_usd,
  ROUND(delay_rate * 100, 1) AS delay_rate_pct,
  ROUND(risk_rate * 100, 1) AS risk_rate_pct,
  ROUND(avg_risk_score, 1) AS avg_risk_score
FROM monthly_summary
ORDER BY order_month;
""",
        encoding="utf-8",
    )


def write_metadata(df: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    kpis = tables["executive_kpis"].copy()
    records = {row["metric"]: row["value"] for _, row in kpis.iterrows()}
    top_supplier = tables["supplier_scorecard"].iloc[0].to_dict()
    top_category = tables["category_summary"].iloc[0].to_dict()

    insights = [
        f"Overall delay rate is {records['Delay Rate']:.1%} across {int(records['Total Orders']):,} orders.",
        f"Supply risk rate is {records['Risk Rate']:.1%}, creating a clear supplier-monitoring use case.",
        f"Highest-risk supplier is {top_supplier['supplier_id']} with average risk score {top_supplier['avg_risk_score']:.1f}.",
        f"Largest value category is {top_category['product_category']} with ${top_category['order_value_usd']:,.0f} in order value.",
    ]

    metadata = {
        "project": "Supply Chain Risk & Performance Command Center",
        "source": "Kaggle: US Supply Chain Risk Analysis Dataset",
        "source_url": "https://www.kaggle.com/datasets/yuanchunhong/us-supply-chain-risk-analysis-dataset",
        "rows": int(len(df)),
        "columns": list(df.columns),
        "insights": insights,
    }
    (ROOT / "docs" / "project_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (ROOT / "docs" / "executive_insights.md").write_text(
        "# Executive Insights\n\n" + "\n".join(f"- {item}" for item in insights) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    VISUALS.mkdir(parents=True, exist_ok=True)
    (ROOT / "docs").mkdir(parents=True, exist_ok=True)

    df = build_clean_dataset()
    tables = make_summary_tables(df)

    df.to_csv(OUT / "clean_supply_chain_orders.csv", index=False)
    for name, table in tables.items():
        table.to_csv(OUT / f"{name}.csv", index=False)

    write_sql_assets(df, tables)
    write_metadata(df, tables)


if __name__ == "__main__":
    main()
