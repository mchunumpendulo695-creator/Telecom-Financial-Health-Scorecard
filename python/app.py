import mysql.connector
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt

# ============================================================
# Telecom Financial Health & Risk Scorecard
# ============================================================

st.set_page_config(
    page_title="Telecom Financial Risk Scorecard",
    page_icon="📊",
    layout="wide",
)


# ------------------------------------------------------------
# 1. Title
# ------------------------------------------------------------

st.title("Telecom Financial Health & Risk Scorecard")

st.markdown(
    """
    **South African Telecom Financial Risk Analysis**

    A financial-health scorecard assessing revenue, profitability,
    EBITDA margin and subscriber-value risk.
    """
)

# ------------------------------------------------------------
# 3. Load Financial + Risk Data
# ------------------------------------------------------------

try:
    # Try connecting to local MySQL database
    connection = mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="", 
        database="telecom_project"
    )

    query = """
    SELECT
        f.company,
        f.fiscal_year,
        f.revenue_zar_m,
        f.ebitda_zar_m,
        f.net_profit_loss_zar_m,
        f.subscribers_m,

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
    connection.close()

except Exception:
    # Fallback for Streamlit Community Cloud or offline execution
    df = pd.read_csv("data/telecom_analytical.csv")


# ------------------------------------------------------------
# 4. Sidebar Controls
# ------------------------------------------------------------

st.sidebar.header("Dashboard Controls")

companies = sorted(df["company"].unique())

selected_company = st.sidebar.selectbox("Company", companies)

company_df = df[df["company"] == selected_company].copy()

min_year = int(company_df["fiscal_year"].min())
max_year = int(company_df["fiscal_year"].max())

selected_years = st.sidebar.slider(
    "Year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

filtered_df = company_df[
    (company_df["fiscal_year"] >= selected_years[0])
    & (company_df["fiscal_year"] <= selected_years[1])
].copy()


# ------------------------------------------------------------
# 5. Current Risk Assessment
# ------------------------------------------------------------

latest = filtered_df.iloc[-1]

current_score = int(latest["total_risk_score"])
current_category = latest["risk_category"]
current_year = int(latest["fiscal_year"])


# ------------------------------------------------------------
# 6. Trend Arrow
# ------------------------------------------------------------

if len(filtered_df) >= 2:

    previous_score = int(filtered_df.iloc[-2]["total_risk_score"])

    score_change = current_score - previous_score

    if score_change > 0:
        trend_arrow = "↑"
        trend_text = "Risk increasing"

    elif score_change < 0:
        trend_arrow = "↓"
        trend_text = "Risk decreasing"

    else:
        trend_arrow = "→"
        trend_text = "Risk unchanged"

else:

    trend_arrow = "→"
    trend_text = "Insufficient history"


# ------------------------------------------------------------
# 7. Company Header
# ------------------------------------------------------------

st.header(f"{selected_company} Risk Assessment")

st.caption(f"Latest assessment year: {current_year}")


# ------------------------------------------------------------
# 8. Main KPI Cards
# ------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:

    st.metric("Current Risk Score", current_score)

with col2:

    st.metric("Risk Category", current_category)

with col3:

    st.metric("Risk Trend", f"{trend_arrow} {trend_text}")


# ------------------------------------------------------------
# 9. Risk Score Trend
# ------------------------------------------------------------

st.subheader("Risk Score Trend")

trend_data = filtered_df[["fiscal_year", "total_risk_score"]].copy()
trend_data["fiscal_year"] = trend_data["fiscal_year"].astype(int).astype(str)

# Create an Altair line chart with forced horizontal labels (labelAngle=0)
chart = (
    alt.Chart(trend_data)
    .mark_line(point=True, color="#FF4B4B")
    .encode(
        x=alt.X(
            "fiscal_year:O",
            title="Fiscal Year",
            axis=alt.Axis(labelAngle=0),  # Forces labels to remain horizontal
        ),
        y=alt.Y(
            "total_risk_score:Q",
            title="Total Risk Score",
            scale=alt.Scale(zero=True),
        ),
        tooltip=["fiscal_year", "total_risk_score"],
    )
    .properties(height=350)
)

st.altair_chart(chart, use_container_width=True)


# ------------------------------------------------------------
# 10. Top 3 Contributing Factors
# ------------------------------------------------------------

st.subheader("Top Contributing Risk Factors")

risk_factors = {
    "Revenue decline": int(latest["revenue_risk"]),
    "Negative net profit": int(latest["profit_risk"]),
    "EBITDA margin decline": int(latest["margin_risk"]),
    "Subscriber value decline": int(latest["subscriber_value_risk"]),
}

ranked_factors = sorted(
    risk_factors.items(), key=lambda x: x[1], reverse=True
)

active_factors = [
    (factor, points) for factor, points in ranked_factors if points > 0
]

if active_factors:

    for factor, points in active_factors[:3]:

        st.write(
            f"**{factor}** — {points} risk point"
            + ("s" if points != 1 else "")
        )

else:

    st.success("No risk factors are currently contributing to the score.")


# ------------------------------------------------------------
# 11. Company-Specific Analyst Notes
# ------------------------------------------------------------

analyst_notes = {
    "Cell C": """
    Cell C currently carries a relatively low modelled risk score,
    but its historical financial position warrants caution. The model
    captures operating indicators such as profitability and subscriber
    value, but does not include balance-sheet measures such as debt,
    liquidity or solvency.
    """,
    "MTN": """
    MTN generally shows strong operating performance but has experienced
    periods of significant financial pressure. The 2024 score is driven
    by multiple simultaneous risk signals, making that period a clear
    warning point despite the improvement in reported performance in 2025.
    """,
    "Telkom": """
    Telkom shows the highest average risk score in the model, with several
    periods of margin pressure and a particularly severe deterioration in
    2023. The 2023 High Risk classification reflects the combination of
    declining revenue, negative profit and weaker EBITDA margin.
    """,
    "Vodacom": """
    Vodacom has relatively stable financial performance and avoids the
    model's High Risk category. However, recurring Medium Risk periods
    indicate that margin and subscriber-value pressures should continue
    to be monitored.
    """,
}

st.subheader("Analyst Note")

st.info(
    analyst_notes.get(
        selected_company,
        "The selected company should be monitored using the financial risk indicators shown above.",
    )
)


# ------------------------------------------------------------
# 12. Financial Metrics
# ------------------------------------------------------------

st.subheader("Financial Performance")

metrics = filtered_df[
    [
        "fiscal_year",
        "revenue_zar_m",
        "ebitda_zar_m",
        "net_profit_loss_zar_m",
    ]
].copy()

metrics["ebitda_margin_pct"] = (
    metrics["ebitda_zar_m"] / metrics["revenue_zar_m"]
) * 100

metrics["ebitda_margin_pct"] = metrics["ebitda_margin_pct"].round(2)

metrics.columns = [
    "Year",
    "Revenue (ZAR m)",
    "EBITDA (ZAR m)",
    "Net Profit/Loss (ZAR m)",
    "EBITDA Margin (%)",
]

metrics["Year"] = metrics["Year"].astype(int).astype(str)

st.dataframe(metrics, use_container_width=True, hide_index=True)


# ------------------------------------------------------------
# 13. Methodology
# ------------------------------------------------------------

with st.expander("Risk Score Methodology"):

    st.write(
        """
        The composite risk score combines four financial warning signals:

        • Revenue decline = 1 point

        • Negative net profit = 2 points

        • EBITDA margin decline = 1 point

        • Subscriber-value decline = 1 point

        Score classification:

        0-1 = Low Risk

        2-3 = Medium Risk

        4+ = High Risk
        """
    )


# ------------------------------------------------------------
# 14. Footer
# ------------------------------------------------------------

st.caption(
    "Telecom Financial Health & Risk Scorecard"
)