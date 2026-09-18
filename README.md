# 📊 Telecom Financial Health & Risk Scorecard

An analytical financial risk framework built to evaluate, score, and visualize the financial health and operational risk of major telecom operators in South Africa using **SQL**, **Python**, **Matplotlib**, and **Streamlit**.

---

## 📌 Executive Summary & Core Objective

Telecom companies often maintain stable headline revenue while underlying profitability, operational efficiency, and unit economics deteriorate. Relying on single metrics can mask fundamental financial distress. 

This project addresses a practical business question:
> **"Which telecom company is financially at risk, and what specific factors are driving that risk?"**

By combining SQL-based window functions, backtested financial indicators in Python, clear visual analytics, and an interactive Streamlit application, this project models risk across four major South African telecommunications providers.

---

## 🏢 Companies Analysed

| Company | Analysis Period | Scope / Key Focus |
| :--- | :---: | :--- |
| **MTN Group** | 2015–2025 | Large scale, FX exposure (e.g., Naira devaluation), operational shocks. |
| **Vodacom Group** | 2015–2025 | Consistent market leader, margin stability, strategic expansion. |
| **Telkom SA** | 2015–2025 | Legacy transition pressure, recurring high-risk operational periods. |
| **Cell C Holdings**| 2015–2025 | Capital restructuring, operating performance vs. balance sheet debt. |

---

## 📐 Risk Methodology

The core risk engine evaluates financial warning flags on a year-over-year ($YoY$) basis. A composite financial risk score is calculated using four specific warning signals:

### 1. Risk Signal Criteria
1. **Revenue Risk ($+1\text{ pt}$):** Assigned when $YoY$ revenue growth is negative ($Revenue_t < Revenue_{t-1}$).
2. **Profit Risk ($+2\text{ pts}$):** Assigned when net profit/loss is negative ($\text{Net Profit}_t < 0$). *Weighted higher due to financial severity.*
3. **EBITDA Margin Risk ($+1\text{ pt}$):** Assigned when EBITDA margin declines $YoY$ ($Margin_t < Margin_{t-1}$).
   $$\text{EBITDA Margin} = \left( \frac{\text{EBITDA}}{\text{Revenue}} \right) \times 100$$
4. **Subscriber Value Risk ($+1\text{ pt}$):** Assigned when average revenue per subscriber declines $YoY$.

### 2. Risk Score Categorisation
$$\text{Total Risk Score} = \text{Revenue Risk} + \text{Profit Risk} + \text{EBITDA Margin Risk} + \text{Subscriber Value Risk}$$

| Score Range | Risk Category | Operational Interpretation |
| :---: | :---: | :--- |
| **0 – 1** | 🟢 **Low Risk** | Strong operational health; minimal negative signals. |
| **2 – 3** | 🟡 **Medium Risk** | Moderate pressure; performance flags require monitoring. |
| **4+** | 🔴 **High Risk** | Severe operational friction across multiple metrics. |

---

## 🔄 Python Backtest & Results

To test whether a high risk score in Year $T$ correlates with deteriorated financial outcomes in Year $T+1$, the model was backtested using Pandas.

### Historical Performance Overview

| Risk Category | Observations | Avg. Next-Year Rev Growth | Avg. Next-Year Profit Change | Next-Year Losses |
| :--- | :---: | :---: | :---: | :---: |
| 🔴 **High Risk** | 3 | $+4.21\%$ | $+16,171\text{ ZAR m}$ | 0 |
| 🟡 **Medium Risk** | 9 | $+5.73\%$ | $-916.11\text{ ZAR m}$ | 1 |
| 🟢 **Low Risk** | 28 | $+4.82\%$ | $-1,658.09\text{ ZAR m}$ | 3 |

### High-Risk Event Detail

| Company | Risk Year | Risk Score | Following-Year Rev Growth | Outcome Note |
| :--- | :---: | :---: | :---: | :--- |
| **MTN** | 2016 | 4 | $-9.58\%$ | Model correctly flagged upcoming contraction. |
| **MTN** | 2024 | 5 | $+20.59\%$ | Model flagged temporary FX shock; company rebounded sharply. |
| **Telkom** | 2023 | 5 | $+1.64\%$ | Flagged structural margin compression & net losses. |

### Model Interpretation & Findings
* **Early-Warning Framework:** The scorecard functions as an operational early-warning system rather than a deterministic failure predictor.
* **Rebound Dynamics:** Severe operational risk years (e.g., MTN 2024, Telkom 2023) were frequently followed by corporate restructuring or market recovery, producing sharp positive profit turnarounds in $T+1$.

---

## 💡 Key Analytical Findings

* **Telkom SA:** Exhibits the highest average risk score in the dataset, culminating in a peak High Risk score ($5/5$) in 2023 driven by simultaneous net losses, margin compression, and declining subscriber value.
* **MTN Group:** Demonstrates broad operational resilience but experiences volatile periods driven by foreign currency fluctuations and regulatory shocks (e.g., 2016 and 2024).
* **Vodacom Group:** Demonstrates the most stable financial profile among the four operators, consistently avoiding the High Risk classification.
* **Cell C Holdings:** Scores relatively low on operational income-statement risk flags, highlighting the key limitation of operating metrics when evaluating heavily leveraged balance sheets.

---

## 🖥️ Streamlit Dashboard Features

The application layer (`app.py`) provides an interactive interface for financial analysts:

* **Company & Year Selectors:** Dynamic filtering for deep-dive analysis.
* **KPI Scorecards:** Real-time risk categorization and year-over-year delta tracking.
* **Trend Visualizations:** Multi-year risk trajectories and small-multiple financial trend charts.
* **Event Annotations:** Visual context overlaying structural events (e.g., Cell C recapitalization, Vodacom Egypt acquisition).
* **Analyst Commentary:** Automated summary narrative outlining primary contributing factors.

---

## 📁 Directory Structure

```text
Telecom-Financial-Health-Scorecard/
│
├── data/
│   ├── CellC financial summary.xlsx
│   ├── MTN financial summary.xlsx
│   ├── Telkom financial summary.xlsx
│   ├── Vodacom financial summary.xlsx
│   ├── telecom_analytical.csv
│   ├── telecom_master.csv
│   └── telecom_overall_ranking.csv
│
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_risk_signals.sql
│   └── 03_risk_model.sql
│
├── python/
│   ├── app.py
│   ├── backtest.py
│   ├── cleaning.py
│   └── combine_data.py
│
├── charts/
│   ├── financial_trends_small_multiples.png
│   ├── red_flag_events.png
│   └── risk_trend.png
│
├── interpretation and conclusions/
│   ├── Back test.docx
│
├── requirements.txt
├── readme.md
└── .gitignore
```

---

## 🛠️ Technology Stack

* **Database / SQL:** MySQL (Table Schema, `LAG()` Window Functions, Conditional Flag Logic)
* **Data Processing:** Python, Pandas, NumPy
* **Visualization:** Matplotlib, Seaborn
* **Dashboard / UX:** Streamlit
* **Version Control:** Git

---

## ⚠️ Model Limitations

1. **Missing Balance-Sheet Metrics:** The scorecard evaluates operating metrics (Revenue, EBITDA, Profit, ARPU) but does not include balance-sheet indicators like total debt, debt-to-equity, current ratio, or interest coverage ratio.
2. **Sample Size:** The dataset spans four major operators over eleven years ($N = 44$). While useful for directional insight, it is not a statistical sample for machine-learning credit modeling.
3. **Equal/Heuristic Weighting:** Weights ($+2$ for profit loss, $+1$ for operational declines) are analytical heuristics rather than statistically calibrated weights from a logistic regression or Altman Z-score approach.

### Future Scope

While the current telecom risk engine and interactive dashboard successfully analyze revenue, EBITDA, and subscriber metrics, the following areas highlight current limitations and immediate opportunities for future iteration:

* **Balance-Sheet & Liquidity Risk Integration**: The scoring model primarily relies on income statement trendlines and subscriber dynamics. To improve financial risk detection, future versions will incorporate balance-sheet metrics—specifically total debt, leverage ratios (Net Debt/EBITDA), and liquidity indicators—to flag non-operating solvent risks.
* **Backtesting Sample Size**: The historical validation evaluated 3 High-Risk events across 4 telecommunications providers. Expanding the evaluation to include international market peers and additional historical years will increase statistical power and validate long-term predictive accuracy.
* **Data Pipeline Automation**: While data transformation scripts clean and compile datasets into master CSV files, direct synchronization into the MySQL database currently requires manual execution. Implementing an automated ETL trigger will ensure seamless database updates.
* **Dashboard Resilience & Analytics**: Fallback handling for offline database scenarios currently relies on static local analytical files. Future UI enhancements will include side-by-side multi-company comparison views to evaluate risk trajectories across competitors simultaneously.
* **Threshold Calibration**: Weightings assigned to risk factors (e.g., negative net profit vs. revenue decline) will be refined using feature-importance models from expanding historical datasets to minimize false positives.
---

## 🚀 Quickstart & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/Telecom-Financial-Health-Scorecard.git
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Initialization (Optional)
Import `data/telecom_master.csv` into your MySQL instance and execute the SQL scripts sequentially:
```sql
SOURCE sql/01_create_tables.sql;
SOURCE sql/02_risk_signals.sql;
SOURCE sql/03_risk_model.sql;
```

### 4. Run Analysis & Generate Charts
```bash
python python/backtest.py
```

### 5. Launch the Streamlit Dashboard
```bash
python -m streamlit run python/app.py
```
## Live Dashboard

Access the live Streamlit dashboard here:

[View the live dashboard](http://localhost:8501)
