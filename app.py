import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Loan Default Risk Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Banking Loan Default Risk Analysis")
st.write(
    "Analyze historical loan defaults, borrower segments "
    "and loan portfolio exposure."
)

df = pd.read_csv("data/Loan_default.csv")

st.sidebar.header("Filters")

age_range = st.sidebar.slider(
    "Age range",
    int(df["Age"].min()),
    int(df["Age"].max()),
    (int(df["Age"].min()), int(df["Age"].max()))
)

income_range = st.sidebar.slider(
    "Annual income range",
    int(df["Income"].min()),
    int(df["Income"].max()),
    (int(df["Income"].min()), int(df["Income"].max()))
)

purposes = sorted(df["LoanPurpose"].unique())

selected_purposes = st.sidebar.multiselect(
    "Loan purpose",
    purposes,
    default=purposes
)

filtered = df[
    df["Age"].between(*age_range)
    & df["Income"].between(*income_range)
    & df["LoanPurpose"].isin(selected_purposes)
]

if filtered.empty:
    st.warning("No records match your filters.")
    st.stop()

total = len(filtered)
defaults = int(filtered["Default"].sum())
rate = filtered["Default"].mean() * 100
amount = filtered["LoanAmount"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Loans", f"{total:,}")
c2.metric("Defaults", f"{defaults:,}")
c3.metric("Default Rate", f"{rate:.2f}%")
c4.metric("Original Loan Amount", f"{amount:,.0f}")

st.divider()

# Default rate by age
st.subheader("Default Rate by Age Group")

filtered = filtered.copy()

filtered["AgeBand"] = pd.cut(
    filtered["Age"],
    bins=[18, 25, 35, 45, 55, 65, 70],
    labels=["18-24", "25-34", "35-44",
            "45-54", "55-64", "65-69"],
    right=False
)

age_stats = (
    filtered.groupby("AgeBand", observed=False)
    .agg(
        Loans=("Default", "size"),
        Defaults=("Default", "sum")
    )
    .reset_index()
)

age_stats["DefaultRate"] = (
    age_stats["Defaults"] / age_stats["Loans"] * 100
)

fig1 = px.bar(
    age_stats,
    x="AgeBand",
    y="DefaultRate",
    hover_data=["Loans", "Defaults"],
    title="Default Rate by Age"
)

st.plotly_chart(fig1, use_container_width=True)

# Default rate by income
st.subheader("Default Rate by Income Band")

filtered["IncomeBand"] = pd.cut(
    filtered["Income"],
    bins=[0, 25000, 50000, 75000,
          100000, 125000, 150000],
    labels=["0-25K", "25K-50K", "50K-75K",
            "75K-100K", "100K-125K", "125K-150K"],
    include_lowest=True
)

income_stats = (
    filtered.groupby("IncomeBand", observed=False)
    .agg(
        Loans=("Default", "size"),
        Defaults=("Default", "sum")
    )
    .reset_index()
)

income_stats["DefaultRate"] = (
    income_stats["Defaults"] / income_stats["Loans"] * 100
)

fig2 = px.bar(
    income_stats,
    x="IncomeBand",
    y="DefaultRate",
    hover_data=["Loans", "Defaults"],
    title="Default Rate by Income"
)

st.plotly_chart(fig2, use_container_width=True)

# Loan purpose analysis
st.subheader("Portfolio Breakdown by Loan Purpose")

purpose_stats = (
    filtered.groupby("LoanPurpose")
    .agg(
        Loans=("Default", "size"),
        Defaults=("Default", "sum"),
        LoanAmount=("LoanAmount", "sum")
    )
    .reset_index()
)

purpose_stats["DefaultRate"] = (
    purpose_stats["Defaults"] / purpose_stats["Loans"] * 100
)

fig3 = px.bar(
    purpose_stats,
    x="LoanPurpose",
    y="DefaultRate",
    hover_data=["Loans", "Defaults", "LoanAmount"],
    title="Default Rate by Loan Purpose"
)

st.plotly_chart(fig3, use_container_width=True)

st.subheader("Loan Portfolio Details")
st.dataframe(purpose_stats, use_container_width=True)