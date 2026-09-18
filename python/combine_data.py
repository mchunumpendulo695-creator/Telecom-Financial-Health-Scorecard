import pandas as pd
import mysql.connector

# ============================================================
# 1. CONNECT TO MYSQL
# ============================================================

connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="telecom_project"
)

print("Connected to MySQL successfully.")


# ============================================================
# 2. LOAD THE VALIDATED RAW DATA
# ============================================================

query = """
SELECT
    company,
    fiscal_year,
    revenue_zar_m,
    ebitda_zar_m,
    net_profit_loss_zar_m,
    subscribers_m
FROM telecom_financials
ORDER BY company, fiscal_year
"""

df = pd.read_sql(query, connection)


# ============================================================
# 3. SORT DATA
# ============================================================

df = df.sort_values(
    ["company", "fiscal_year"]
).reset_index(drop=True)


# ============================================================
# 4. REVENUE GROWTH (%)
# ============================================================
# Revenue growth is calculated against the previous
# available fiscal year for the same company.
#
# If either current or previous revenue is missing,
# the result remains NULL.

df["revenue_growth_pct"] = (
    df.groupby("company")["revenue_zar_m"]
      .pct_change(fill_method=None)
      * 100
)


# ============================================================
# 5. EBITDA MARGIN (%)
# ============================================================

df["ebitda_margin_pct"] = (
    df["ebitda_zar_m"]
    / df["revenue_zar_m"]
    * 100
)


# ============================================================
# 6. NET PROFIT MARGIN (%)
# ============================================================

df["net_profit_margin_pct"] = (
    df["net_profit_loss_zar_m"]
    / df["revenue_zar_m"]
    * 100
)


# ============================================================
# 7. REVENUE PER SUBSCRIBER
# ============================================================
# Revenue is ZAR millions.
# Subscribers are millions.
# Therefore:
#
# ZAR million / million subscribers = ZAR per subscriber

df["revenue_per_subscriber"] = (
    df["revenue_zar_m"]
    / df["subscribers_m"]
)


# ============================================================
# 8. HANDLE INVALID CALCULATIONS
# ============================================================

df.loc[
    df["revenue_zar_m"].isna() |
    df["subscribers_m"].isna() |
    (df["subscribers_m"] <= 0),
    "revenue_per_subscriber"
] = None


df.loc[
    df["revenue_zar_m"].isna() |
    (df["revenue_zar_m"] == 0),
    "ebitda_margin_pct"
] = None


df.loc[
    df["revenue_zar_m"].isna() |
    (df["revenue_zar_m"] == 0),
    "net_profit_margin_pct"
] = None


# ============================================================
# 9. ROUND CALCULATED VALUES
# ============================================================

df["revenue_growth_pct"] = df["revenue_growth_pct"].round(2)
df["ebitda_margin_pct"] = df["ebitda_margin_pct"].round(2)
df["net_profit_margin_pct"] = df["net_profit_margin_pct"].round(2)
df["revenue_per_subscriber"] = df["revenue_per_subscriber"].round(2)


# ============================================================
# 10. DISPLAY THE ANALYTICAL DATASET
# ============================================================

print("\n" + "=" * 70)
print("ANALYTICAL DATASET")
print("=" * 70)

print(
    df[
        [
            "company",
            "fiscal_year",
            "revenue_zar_m",
            "ebitda_zar_m",
            "net_profit_loss_zar_m",
            "subscribers_m",
            "revenue_growth_pct",
            "ebitda_margin_pct",
            "net_profit_margin_pct",
            "revenue_per_subscriber"
        ]
    ].to_string(index=False)
)


# ============================================================
# 11. VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("ANALYTICAL VALIDATION")
print("=" * 70)

print("\nNumber of observations:")
print(len(df))

print("\nRows per company:")
print(df.groupby("company").size())

print("\nDuplicate company-year combinations:")

duplicates = df[
    df.duplicated(
        subset=["company", "fiscal_year"],
        keep=False
    )
]

if duplicates.empty:
    print("None")
else:
    print(duplicates)


print("\nMissing calculated values:")
print(
    df[
        [
            "revenue_growth_pct",
            "ebitda_margin_pct",
            "net_profit_margin_pct",
            "revenue_per_subscriber"
        ]
    ].isna().sum()
)


# ============================================================
# 12. SAVE ANALYTICAL DATASET
# ============================================================

output_file = "data/telecom_analytical.csv"

df.to_csv(
    output_file,
    index=False
)

print("\nAnalytical dataset saved:")
print(output_file)


# ============================================================
# 13. CLOSE MYSQL
# ============================================================

connection.close()

print("\nMySQL connection closed.")
print("Analysis completed successfully.")

# ============================================================
# 14. WEIGHTED FINANCIAL RISK SCORING
# ============================================================
#
# Lower score = lower financial risk
# Higher score = higher financial risk
#
# Risk components:
#   Revenue risk
#   Profit risk
#   Margin risk
#   Subscriber-value risk
#
# The scoring follows the project's risk framework.
#
# IMPORTANT:
# Missing financial data does NOT automatically create risk.
# A risk point is assigned only when the relevant metric
# actually breaches the defined risk threshold.
# ============================================================


# ------------------------------------------------------------
# 14.1 REVENUE RISK
# ------------------------------------------------------------
# Revenue growth below 0% = revenue contraction.
#
# Score:
#   0 = no revenue contraction
#   1 = revenue contraction
#
# If revenue growth is unavailable, no risk point is assigned.

df["revenue_risk"] = (
    (df["revenue_growth_pct"] < 0)
    .astype(int)
)

df.loc[
    df["revenue_growth_pct"].isna(),
    "revenue_risk"
] = 0


# ------------------------------------------------------------
# 14.2 PROFIT RISK
# ------------------------------------------------------------
# Negative net profit is treated as the highest profit risk.
#
# Score:
#   0 = positive profit
#   2 = negative profit
#
# Missing net profit = no score.

df["profit_risk"] = 0

df.loc[
    df["net_profit_margin_pct"] < 0,
    "profit_risk"
] = 2

df.loc[
    df["net_profit_margin_pct"].isna(),
    "profit_risk"
] = 0


# ------------------------------------------------------------
# 14.3 EBITDA MARGIN RISK
# ------------------------------------------------------------
# EBITDA margin below the project's risk threshold
# receives a risk point.
#
# Threshold = 20%
#
# Score:
#   0 = EBITDA margin >= 20%
#   1 = EBITDA margin < 20%
#
# Missing EBITDA margin = no score.

df["margin_risk"] = 0

df.loc[
    df["ebitda_margin_pct"] < 20,
    "margin_risk"
] = 1

df.loc[
    df["ebitda_margin_pct"].isna(),
    "margin_risk"
] = 0


# ------------------------------------------------------------
# 14.4 SUBSCRIBER VALUE RISK
# ------------------------------------------------------------
# Revenue per subscriber is used as the subscriber-value
# measure.
#
# A year-on-year decline in revenue per subscriber
# receives one risk point.
#
# First available year = no risk score.
#
# Missing values = no risk score.

df["revenue_per_subscriber_growth_pct"] = (
    df.groupby("company")["revenue_per_subscriber"]
      .pct_change(fill_method=None)
      * 100
)

df["subscriber_value_risk"] = 0

df.loc[
    df["revenue_per_subscriber_growth_pct"] < 0,
    "subscriber_value_risk"
] = 1

df.loc[
    df["revenue_per_subscriber_growth_pct"].isna(),
    "subscriber_value_risk"
] = 0


# ------------------------------------------------------------
# 14.5 TOTAL RISK SCORE
# ------------------------------------------------------------

df["total_risk_score"] = (
    df["revenue_risk"]
    + df["profit_risk"]
    + df["margin_risk"]
    + df["subscriber_value_risk"]
)


# ============================================================
# 15. RISK CATEGORY
# ============================================================

def classify_risk(score):

    if pd.isna(score):
        return None

    if score >= 4:
        return "High Risk"

    elif score >= 2:
        return "Medium Risk"

    else:
        return "Low Risk"


df["risk_category"] = (
    df["total_risk_score"]
    .apply(classify_risk)
)


# ============================================================
# 16. YEARLY RISK RANKING
# ============================================================
#
# Companies are ranked against each other within each year.
#
# Lower risk score = better ranking.
# Rank 1 = lowest financial risk.

df["risk_rank"] = (
    df.groupby("fiscal_year")["total_risk_score"]
      .rank(
          method="min",
          ascending=True
      )
      .astype("Int64")
)


# ============================================================
# 17. DISPLAY RISK SCORES
# ============================================================

print("\n" + "=" * 70)
print("WEIGHTED FINANCIAL RISK SCORES")
print("=" * 70)

risk_output = df[
    [
        "company",
        "fiscal_year",
        "revenue_risk",
        "profit_risk",
        "margin_risk",
        "subscriber_value_risk",
        "total_risk_score",
        "risk_category",
        "risk_rank"
    ]
].sort_values(
    ["fiscal_year", "risk_rank", "company"]
)

print(
    risk_output.to_string(index=False)
)


# ============================================================
# 18. OVERALL COMPANY RANKING
# ============================================================
#
# Lower average risk score = lower overall financial risk.
#
# We also show:
#   - highest risk score
#   - number of high-risk years
#   - number of medium-risk years

overall_ranking = (
    df.groupby("company")
      .agg(
          average_risk_score=(
              "total_risk_score",
              "mean"
          ),

          highest_risk_score=(
              "total_risk_score",
              "max"
          ),

          high_risk_years=(
              "risk_category",
              lambda x: (x == "High Risk").sum()
          ),

          medium_risk_years=(
              "risk_category",
              lambda x: (x == "Medium Risk").sum()
          )
      )
      .reset_index()
)


# Overall ranking

overall_ranking["overall_rank"] = (
    overall_ranking["average_risk_score"]
    .rank(
        method="min",
        ascending=True
    )
    .astype(int)
)


overall_ranking = overall_ranking.sort_values(
    ["overall_rank", "company"]
)


# ============================================================
# 19. DISPLAY OVERALL RANKING
# ============================================================

print("\n" + "=" * 70)
print("OVERALL COMPANY RISK RANKING")
print("=" * 70)

print(
    overall_ranking.to_string(index=False)
)


# ============================================================
# 20. SAVE FINAL ANALYTICAL DATASETS
# ============================================================

df.to_csv(
    "data/telecom_analytical.csv",
    index=False
)

overall_ranking.to_csv(
    "data/telecom_overall_ranking.csv",
    index=False
)


print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print("data/telecom_analytical.csv")
print("data/telecom_overall_ranking.csv")


# ============================================================
# 21. VALIDATE RISK SCORING
# ============================================================

print("\n" + "=" * 70)
print("RISK SCORE VALIDATION")
print("=" * 70)

print("\nRisk categories:")
print(
    df["risk_category"]
    .value_counts()
)


print("\nAverage risk score by company:")
print(
    df.groupby("company")["total_risk_score"]
      .mean()
      .sort_values()
)


print("\nHighest risk score by company:")
print(
    df.groupby("company")["total_risk_score"]
      .max()
      .sort_values()
)


# ============================================================
# 22. CLOSE MYSQL
# ============================================================

connection.close()

print("\nMySQL connection closed.")
print("Weighted risk scoring and ranking completed successfully.")