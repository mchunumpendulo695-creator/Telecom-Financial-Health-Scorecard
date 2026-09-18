-- ============================================================
-- Telecom Risk Project
-- 03_risk_model.sql
-- ============================================================

USE telecom_project;

DROP TABLE IF EXISTS telecom_risk_scores;

CREATE TABLE telecom_risk_scores AS
SELECT
    company,
    fiscal_year,
    revenue_risk,
    profit_risk,
    margin_risk,
    subscriber_value_risk,

    (
        revenue_risk
        + profit_risk
        + margin_risk
        + subscriber_value_risk
    ) AS total_risk_score,

    CASE
        WHEN (
            revenue_risk
            + profit_risk
            + margin_risk
            + subscriber_value_risk
        ) >= 4
        THEN 'High Risk'

        WHEN (
            revenue_risk
            + profit_risk
            + margin_risk
            + subscriber_value_risk
        ) >= 2
        THEN 'Medium Risk'

        ELSE 'Low Risk'
    END AS risk_category

FROM telecom_risk_signals;

-- View final risk scoring output
SELECT * 
FROM telecom_risk_scores 
ORDER BY fiscal_year, total_risk_score DESC, company;