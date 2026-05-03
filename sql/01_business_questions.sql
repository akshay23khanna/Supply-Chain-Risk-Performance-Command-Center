-- Supply Chain Risk Analytics: Business Questions

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
