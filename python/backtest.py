import mysql.connector
import pandas as pd

# ============================================================
# Telecom Risk Project
# Python Risk Analysis & Backtesting
# ============================================================

# ------------------------------------------------------------
# 1. Connect to MySQL
# ------------------------------------------------------------

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="telecom_project"
)

print("Connected")


# ------------------------------------------------------------
# 2. Load financial data + risk scores
# ------------------------------------------------------------

query = """
SELECT
    f.company,
    f.fiscal_year,
    f.revenue_zar_m,
    f.net_profit_loss_zar_m,
    r.revenue_risk,
    r.profit_risk,
    r.margin_risk,
    r.subscriber_value_risk,
    r.total_risk_score,
    r.risk_category
FROM telecom_financials f
JOIN telecom_risk_scores r
    ON f.company = r.company
    AND f.fiscal_year = r.fiscal_year
ORDER BY f.company, f.fiscal_year;
"""

df = pd.read_sql(query, connection)


# ------------------------------------------------------------
# 3. Risk Model Summary
# ------------------------------------------------------------

print("\nRisk Summary by Company:")

summary = (
    df.groupby("company")
      .agg(
          average_risk_score=("total_risk_score", "mean"),
          high_risk_years=("risk_category", lambda x: (x == "High Risk").sum()),
          medium_risk_years=("risk_category", lambda x: (x == "Medium Risk").sum()),
          low_risk_years=("risk_category", lambda x: (x == "Low Risk").sum())
      )
      .reset_index()
)

summary["average_risk_score"] = summary["average_risk_score"].round(2)

print(summary.to_string(index=False))


# ------------------------------------------------------------
# 4. Risk Signal Frequency
# ------------------------------------------------------------

print("\nRisk Signal Frequency:")

signal_summary = pd.DataFrame({
    "risk_signal": [
        "Revenue Risk",
        "Profit Risk",
        "Margin Risk",
        "Subscriber Value Risk"],
    "flag_count": [
        (df["revenue_risk"] == 1).sum(),
        (df["profit_risk"] == 2).sum(),
        (df["margin_risk"] == 1).sum(),
        (df["subscriber_value_risk"] == 1).sum()]})

print(signal_summary.to_string(index=False))


# ------------------------------------------------------------
# 5. Create Next-Year Financial Outcomes
# ------------------------------------------------------------

df["next_year_revenue"] = (
    df.groupby("company")["revenue_zar_m"].shift(-1))

df["next_year_profit"] = (
    df.groupby("company")["net_profit_loss_zar_m"].shift(-1))

df["next_year"] = (
    df.groupby("company")["fiscal_year"].shift(-1))


# ------------------------------------------------------------
# 6. Calculate Next-Year Revenue Growth
# ------------------------------------------------------------

df["next_year_revenue_growth_pct"] = (
    (df["next_year_revenue"] - df["revenue_zar_m"])
    / df["revenue_zar_m"]) * 100


# ------------------------------------------------------------
# 7. Calculate Next-Year Profit Change
# ------------------------------------------------------------

df["next_year_profit_change"] = (
    df["next_year_profit"] - df["net_profit_loss_zar_m"])


# ------------------------------------------------------------
# 8. Identify Next-Year Negative Profit
# ------------------------------------------------------------

df["next_year_loss"] = (df["next_year_profit"] < 0)


# ------------------------------------------------------------
# 9. Keep Only Years With a Following Year
# ------------------------------------------------------------

backtest = df[df["next_year"].notna()].copy()


# ------------------------------------------------------------
# 10. Backtest Results
# ------------------------------------------------------------

print("\nBacktest Results:")

backtest_results = (backtest.groupby("risk_category")
    .agg(
        observations=("company", "count"),
        average_next_year_revenue_growth=(
            "next_year_revenue_growth_pct",
            "mean"),
        average_next_year_profit_change=(
            "next_year_profit_change",
            "mean"
        ),
        next_year_losses=(
            "next_year_loss",
            "sum"
        )
    )
    .reset_index()
)

backtest_results["average_next_year_revenue_growth"] = (
    backtest_results["average_next_year_revenue_growth"].round(2)
)

backtest_results["average_next_year_profit_change"] = (
    backtest_results["average_next_year_profit_change"].round(2)
)

print(backtest_results.to_string(index=False))


# ------------------------------------------------------------
# 11. High-Risk Events and Following-Year Outcomes
# ------------------------------------------------------------

print("\nHigh-Risk Events:")

high_risk = backtest[
    backtest["risk_category"] == "High Risk"]
[[
    "company",
    "fiscal_year",
    "total_risk_score",
    "next_year",
    "next_year_revenue_growth_pct",
    "next_year_profit",
    "next_year_loss"
]].copy()

high_risk["next_year_revenue_growth_pct"] = (
    high_risk["next_year_revenue_growth_pct"].round(2)
)

print(high_risk.to_string(index=False))


# ------------------------------------------------------------
# 12. Close MySQL Connection
# ------------------------------------------------------------

connection.close()

print("\nConnection closed.")
print("\nBacktesting complete!")