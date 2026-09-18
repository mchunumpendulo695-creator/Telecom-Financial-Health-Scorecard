import pandas as pd

# ============================================================
# 1. FILE LOCATIONS
# ============================================================

files = {
    "MTN": "data/MTN financial summary.xlsx",
    "Vodacom": "data/Vodacom financial summary.xlsx",
    "Telkom": "data/Telkom financial summary.xlsx",
    "Cell C": "data/CellC financial summary.xlsx"
}


# ============================================================
# 2. SHEETS CONTAINING THE FINANCIAL DATA
# ============================================================

sheets = {
    "MTN": "Group Summary",
    "Vodacom": "Group Summary",
    "Telkom": "Group & Segment Summary",
    "Cell C": "Group Summary"
}


# ============================================================
# 3. LOAD EACH COMPANY
# ============================================================

company_data = []

for company, file in files.items():

    print(f"Loading {company}...")

    df = pd.read_excel(
        file,
        sheet_name=sheets[company],
        header=3
    )

    # Add company name
    df["Company"] = company

    company_data.append(df)


# ============================================================
# 4. COMBINE ALL COMPANIES
# ============================================================

telecom_data = pd.concat(
    company_data,
    ignore_index=True
)


# ============================================================
# 5. KEEP ONLY 2015–2025
# ============================================================

telecom_data = telecom_data[
    pd.to_numeric(
        telecom_data["Fiscal Year"],
        errors="coerce"
    ).between(2015, 2025)
].copy()


# Convert Fiscal Year to integer
telecom_data["Fiscal Year"] = (
    pd.to_numeric(
        telecom_data["Fiscal Year"],
        errors="coerce"
    ).astype(int)
)


# ============================================================
# 6. CONVERT ACCOUNTING-STYLE NUMBERS
# ============================================================

def convert_accounting_number(value):

    if pd.isna(value):
        return None

    if isinstance(value, str):

        value = value.strip()

        # Example: (829) -> -829
        if value.startswith("(") and value.endswith(")"):
            return -float(
                value[1:-1].replace(",", "")
            )

        return float(
            value.replace(",", "")
        )

    return value


financial_columns = [
    "Revenue (ZAR m)",
    "EBITDA (ZAR m)",
    "Net Profit / (Loss) (ZAR m)",
    "Subscribers (m)"
]


for column in financial_columns:

    if column in telecom_data.columns:

        telecom_data[column] = (
            telecom_data[column]
            .apply(convert_accounting_number)
        )


# ============================================================
# 7. NET PROFIT METHODOLOGY
# ============================================================
#
# The methodology requires:
#
# Net Profit/Loss =
# Profit/Loss AFTER TAX attributable to equity holders
# of the parent.
#
# Profit Before Tax (PBT) is NOT allowed.
#
# Cell C 2024 and 2025 were previously identified as
# PBT figures, therefore those values must be NULL.
#
# The original explanation remains in Audit Notes.
# ============================================================

cell_c_pbt_years = [2024, 2025]

telecom_data.loc[
    (telecom_data["Company"] == "Cell C") &
    (telecom_data["Fiscal Year"].isin(cell_c_pbt_years)),
    "Net Profit / (Loss) (ZAR m)"
] = None


# ============================================================
# 8. ARPU METHODOLOGY
# ============================================================
#
# The agreed methodology states:
#
# Consolidated/blended Group ARPU must NOT be manually
# calculated because a defensible Group-wide blended ARPU
# is not consistently published.
#
# Therefore:
#
# ARPU (Blended) = NULL for every company/year.
# ============================================================

# Remove old ARPU columns if they exist
arpu_columns_to_remove = [
    "ARPU (Blended)",
    "APRU blended",
    "ARPU (Blended, ZAR/US$)"
]

telecom_data = telecom_data.drop(
    columns=arpu_columns_to_remove,
    errors="ignore"
)


# Create the standardized analytical ARPU column
telecom_data["ARPU (Blended)"] = None


# ============================================================
# 9. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Fiscal Year",
    "Revenue (ZAR m)",
    "EBITDA (ZAR m)",
    "Net Profit / (Loss) (ZAR m)",
    "Subscribers (m)",
    "Audit Notes & Adjustments",
    "Sourced Document",
    "Company",
    "ARPU (Blended)"
]


missing_columns = [
    column
    for column in required_columns
    if column not in telecom_data.columns
]


if missing_columns:

    print("\nERROR: Required columns are missing:")

    for column in missing_columns:
        print(f" - {column}")

    raise ValueError(
        "Required columns are missing from the Excel files."
    )


# Keep only the final analytical columns
telecom_data = telecom_data[
    required_columns
]


# ============================================================
# 10. FINAL DATA VALIDATION
# ============================================================

print("\n")
print("=" * 60)
print("FINAL DATA VALIDATION")
print("=" * 60)


# ------------------------------------------------------------
# A. Shape
# ------------------------------------------------------------

print("\nShape:")
print(telecom_data.shape)


# ------------------------------------------------------------
# B. Columns
# ------------------------------------------------------------

print("\nFinal columns:")
print(telecom_data.columns.tolist())


# ------------------------------------------------------------
# C. Number of observations
# ------------------------------------------------------------

print("\nNumber of observations:")
print(len(telecom_data))


# ------------------------------------------------------------
# D. Rows per company
# ------------------------------------------------------------

print("\nRows per company:")
print(
    telecom_data["Company"]
    .value_counts()
    .sort_index()
)


# ------------------------------------------------------------
# E. Duplicate company-year combinations
# ------------------------------------------------------------

duplicates = telecom_data[
    telecom_data.duplicated(
        subset=["Company", "Fiscal Year"],
        keep=False
    )
]

print("\nDuplicate company-year combinations:")

if duplicates.empty:
    print("None")
else:
    print(duplicates)


# ------------------------------------------------------------
# F. Number of years per company
# ------------------------------------------------------------

print("\nNumber of years per company:")

print(
    telecom_data
    .groupby("Company")["Fiscal Year"]
    .nunique()
)


# ------------------------------------------------------------
# G. Year range per company
# ------------------------------------------------------------

print("\nYear range per company:")

print(
    telecom_data
    .groupby("Company")["Fiscal Year"]
    .agg(["min", "max"])
)


# ------------------------------------------------------------
# H. Missing values
# ------------------------------------------------------------

print("\nMissing values:")

print(
    telecom_data.isna().sum()
)


# ------------------------------------------------------------
# I. Data types
# ------------------------------------------------------------

print("\nData types:")

print(
    telecom_data.dtypes
)


# ------------------------------------------------------------
# J. ARPU validation
# ------------------------------------------------------------

arpu_count = telecom_data["ARPU (Blended)"].notna().sum()

print("\nNon-null blended ARPU values:")
print(arpu_count)

if arpu_count == 0:
    print("PASS: Blended Group ARPU is NULL for all rows.")
else:
    print("WARNING: Blended Group ARPU contains values.")


# ------------------------------------------------------------
# K. Cell C Net Profit validation
# ------------------------------------------------------------

print("\nCell C Net Profit/Loss:")

print(
    telecom_data[
        telecom_data["Company"] == "Cell C"
    ][
        [
            "Fiscal Year",
            "Net Profit / (Loss) (ZAR m)"
        ]
    ]
)


# ------------------------------------------------------------
# L. Check Cell C 2024/2025
# ------------------------------------------------------------

cell_c_invalid_pbt = telecom_data[
    (telecom_data["Company"] == "Cell C") &
    (telecom_data["Fiscal Year"].isin([2024, 2025])) &
    (telecom_data["Net Profit / (Loss) (ZAR m)"].notna())
]

print("\nCell C 2024/2025 PBT check:")

if cell_c_invalid_pbt.empty:
    print("PASS: PBT values are not included in Net Profit/Loss.")
else:
    print("WARNING: PBT values may still be present.")
    print(cell_c_invalid_pbt)


# ============================================================
# 11. CHECK SOURCE AND AUDIT INFORMATION
# ============================================================

print("\nMissing source documents:")
print(
    telecom_data["Sourced Document"]
    .isna()
    .sum()
)


print("\nMissing audit notes:")
print(
    telecom_data["Audit Notes & Adjustments"]
    .isna()
    .sum()
)


# ============================================================
# 12. CHECK THAT WE HAVE 44 OBSERVATIONS
# ============================================================

if len(telecom_data) == 44:
    print("\nPASS: Exactly 44 observations.")
else:
    print(
        f"\nWARNING: Expected 44 observations, "
        f"found {len(telecom_data)}."
    )


# ============================================================
# 13. CHECK THAT EACH COMPANY HAS 11 YEARS
# ============================================================

years_per_company = (
    telecom_data
    .groupby("Company")["Fiscal Year"]
    .nunique()
)

if (years_per_company == 11).all():
    print("PASS: Every company has 11 years.")
else:
    print("WARNING: One or more companies does not have 11 years.")


# ============================================================
# 14. CHECK FOR DUPLICATES
# ============================================================

if duplicates.empty:
    print("PASS: No duplicate company-year combinations.")
else:
    print("WARNING: Duplicate company-year combinations exist.")


# ============================================================
# 15. SAVE FINAL MASTER DATASET
# ============================================================

output_file = "data/telecom_master.csv"

telecom_data.to_csv(
    output_file,
    index=False
)


print("\n")
print("=" * 60)
print("MASTER DATASET SAVED")
print("=" * 60)

print(f"\nFile: {output_file}")
print(f"Rows: {len(telecom_data)}")
print(f"Columns: {len(telecom_data.columns)}")

print("\nThe MySQL database has NOT been changed.")
print("Validate this CSV before updating MySQL.")