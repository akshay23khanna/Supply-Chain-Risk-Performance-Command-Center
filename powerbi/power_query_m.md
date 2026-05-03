# Power Query M

Use **Get Data > Text/CSV** and load `data/processed/clean_supply_chain_orders.csv`.

Recommended type transformations:

```powerquery
let
    Source = Csv.Document(
        File.Contents("data/processed/clean_supply_chain_orders.csv"),
        [Delimiter=",", Columns=33, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromoteHeaders,
        {
            {"order_id", type text},
            {"buyer_id", type text},
            {"supplier_id", type text},
            {"product_category", type text},
            {"quantity_ordered", Int64.Type},
            {"order_date", type date},
            {"dispatch_date", type date},
            {"delivery_date", type date},
            {"shipping_mode", type text},
            {"order_value_usd", Currency.Type},
            {"delay_days", Int64.Type},
            {"disruption_type", type text},
            {"disruption_severity", type text},
            {"historical_disruption_count", Int64.Type},
            {"supplier_reliability_score", type number},
            {"organization_id", type text},
            {"dominant_buyer_flag", Int64.Type},
            {"available_historical_records", Int64.Type},
            {"data_sharing_consent", Int64.Type},
            {"federated_round", Int64.Type},
            {"parameter_change_magnitude", type number},
            {"communication_cost_mb", type number},
            {"energy_consumption_joules", type number},
            {"supply_risk_flag", Int64.Type},
            {"order_month", type text},
            {"cycle_time_days", Int64.Type},
            {"dispatch_lag_days", Int64.Type},
            {"is_delayed", Int64.Type},
            {"risk_label", type text},
            {"delay_bucket", type text},
            {"reliability_band", type text},
            {"risk_score", type number},
            {"risk_tier", type text}
        }
    )
in
    ChangedTypes
```

