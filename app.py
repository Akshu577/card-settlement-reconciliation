"""Streamlit dashboard: runs the same SQL as src/run_report.py and shows the results."""
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from src import generate_data
from src.run_report import named_queries

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="Card Settlement Reconciliation", page_icon="💳", layout="wide")
st.title("Card Settlement Reconciliation & Dispute Analytics")
st.caption("Synthetic data (20,000 card transactions). Every table below is a SQL query from the sql/ folder. "
           "Source: github.com/Akshu577/card-settlement-reconciliation")


@st.cache_data
def run_queries():
    # The database isn't committed, so build it on first launch
    if not generate_data.DB.exists():
        generate_data.main()
    results = {}
    with sqlite3.connect(generate_data.DB) as con:
        for sql_file in sorted((ROOT / "sql").glob("*.sql")):
            for name, query in named_queries(sql_file.read_text()):
                results[name] = (query, pd.read_sql_query(query, con))
    return results


results = run_queries()


def show(name, title):
    query, df = results[name]
    st.subheader(title)
    st.dataframe(df, hide_index=True, width="stretch")
    with st.expander("SQL"):
        st.code(query, language="sql")
    return df


recon = results["recon_summary"][1]
matched = recon.loc[recon.recon_status == "Matched", "transactions"].sum()
disputes = results["dispute_kpis"][1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Approved transactions", f"{recon.transactions.sum():,}")
c2.metric("Matched to settlement", f"{matched / recon.transactions.sum():.1%}")
c3.metric("Exceptions", f"{recon.transactions.sum() - matched:,}")
c4.metric("Disputes", f"{disputes.disputes.sum():,}")

tab1, tab2 = st.tabs(["Reconciliation", "Disputes"])
with tab1:
    show("recon_summary", "Reconciliation status")
    df = show("exceptions_by_channel", "Exception rate by channel")
    st.bar_chart(df, x="channel", y="exception_rate_pct")
    show("orphan_settlements", "Settled by the network but missing from the switch log")
with tab2:
    show("dispute_kpis", "Dispute KPIs by reason")
    df = show("monthly_dispute_trend", "Disputes opened per month")
    st.line_chart(df, x="month", y="disputes_opened")
    show("repeat_dispute_cards", "Cards with 3 or more disputes")
