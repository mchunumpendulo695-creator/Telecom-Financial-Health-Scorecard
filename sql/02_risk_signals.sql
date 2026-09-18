-- ============================================================
-- Telecom Risk Project
-- 02_risk_signals.sql
-- ============================================================

USE telecom_project;

DROP TABLE IF EXISTS telecom_risk_signals;

CREATE TABLE telecom_risk_signals AS
WITH base_metrics AS (
    SELECT
        company,
        fiscal_year,
        revenue_zar_m,
        net_profit_loss_zar_m,
        CASE 
            WHEN revenue_zar_m IS NOT NULL AND revenue_zar_m <> 0 
            THEN (ebitda_zar_m / revenue_zar_m) * 100 
            ELSE NULL 
        END AS ebitda_margin_pct,
        CASE 
            WHEN subscribers_m IS NOT NULL AND subscribers_m <> 0 
            THEN (revenue_zar_m / subscribers_m) 
            ELSE NULL 
        END AS revenue_per_subscriber
    FROM telecom_financials
),
lags AS (
    SELECT
        company,
        fiscal_year,
        revenue_zar_m,
        net_profit_loss_zar_m,
        ebitda_margin_pct,
        revenue_per_subscriber,
        LAG(revenue_zar_m) OVER (PARTITION BY company ORDER BY fiscal_year) AS previous_revenue,
        LAG(ebitda_margin_pct) OVER (PARTITION BY company ORDER BY fiscal_year) AS previous_margin,
        LAG(revenue_per_subscriber) OVER (PARTITION BY company ORDER BY fiscal_year) AS previous_revenue_per_subscriber
    FROM base_metrics
)
SELECT
    company,
    fiscal_year,

    CASE
        WHEN previous_revenue IS NOT NULL 
             AND revenue_zar_m < previous_revenue
        THEN 1
        ELSE 0
    END AS revenue_risk,

    CASE
        WHEN net_profit_loss_zar_m < 0
        THEN 2
        ELSE 0
    END AS profit_risk,

    CASE
        WHEN previous_margin IS NOT NULL 
             AND ebitda_margin_pct < previous_margin
        THEN 1
        ELSE 0
    END AS margin_risk,

    CASE
        WHEN previous_revenue_per_subscriber IS NOT NULL 
             AND revenue_per_subscriber < previous_revenue_per_subscriber
        THEN 1
        ELSE 0
    END AS subscriber_value_risk

FROM lags;

-- Verify risk signals table
SELECT * FROM telecom_risk_signals ORDER BY company, fiscal_year;