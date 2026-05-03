# Power BI DAX Measures

Create these measures on the `clean_supply_chain_orders` table.

```DAX
Total Orders =
COUNTROWS(clean_supply_chain_orders)

Total Order Value =
SUM(clean_supply_chain_orders[order_value_usd])

Delayed Orders =
CALCULATE(
    [Total Orders],
    clean_supply_chain_orders[is_delayed] = 1
)

Delay Rate =
DIVIDE([Delayed Orders], [Total Orders])

Risk Orders =
CALCULATE(
    [Total Orders],
    clean_supply_chain_orders[supply_risk_flag] = 1
)

Risk Rate =
DIVIDE([Risk Orders], [Total Orders])

Average Delay Days =
AVERAGE(clean_supply_chain_orders[delay_days])

Average Risk Score =
AVERAGE(clean_supply_chain_orders[risk_score])

Average Supplier Reliability =
AVERAGE(clean_supply_chain_orders[supplier_reliability_score])

High Risk Orders =
CALCULATE(
    [Total Orders],
    clean_supply_chain_orders[risk_tier] = "High"
)

High Risk Value =
CALCULATE(
    [Total Order Value],
    clean_supply_chain_orders[risk_tier] = "High"
)

Delayed Value =
CALCULATE(
    [Total Order Value],
    clean_supply_chain_orders[is_delayed] = 1
)

Average Energy Consumption =
AVERAGE(clean_supply_chain_orders[energy_consumption_joules])

Average Communication Cost MB =
AVERAGE(clean_supply_chain_orders[communication_cost_mb])
```

