import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Enterprise AI Analytics Platform", layout="wide")
st.title("Enterprise AI Analytics Platform")

# -----------------------------
# LOAD DATA
# -----------------------------
sales = pd.read_csv("sales_data.csv")
returns = pd.read_csv("returns_data.csv")
website = pd.read_csv("website_data.csv")

sales["Date"] = pd.to_datetime(sales["Date"])
sales["Year"] = sales["Date"].dt.year
sales["Month"] = sales["Date"].dt.month

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def detect_metric(q):

    if any(x in q for x in ["sales","revenue"]):
        return "sales"

    if any(x in q for x in ["return","returns","refund"]):
        return "returns"

    if any(x in q for x in ["cancel","cancellation"]):
        return "cancellations"

    return None


def extract_entities(question):

    q = question.lower()

    year_match = re.search(r"\b(20\d{2})\b", q)
    year = int(year_match.group()) if year_match else None

    months = {
        "january":1,"february":2,"march":3,"april":4,
        "may":5,"june":6,"july":7,"august":8,
        "september":9,"october":10,"november":11,"december":12
    }

    month = None
    for m in months:
        if m in q:
            month = months[m]

    product = None
    for p in sales["Product"].unique():
        if str(p).lower() in q:
            product = p

    region = None
    if "Region" in sales.columns:
        for r in sales["Region"].dropna().unique():
            if str(r).lower() in q:
                region = r

    category = None
    if "Category" in sales.columns:
        for c in sales["Category"].dropna().unique():
            if str(c).lower() in q:
                category = c

    top_match = re.search(r"top (\d+)", q)
    top_n = int(top_match.group(1)) if top_match else None

    metric = detect_metric(q)

    return q, year, month, product, region, category, top_n, metric


def apply_filters(df, product, region, category, year, month):
    data = df.copy()

    if product:
        data = data[data["Product"] == product]

    if region and "Region" in df.columns:
        data = data[data["Region"] == region]

    if category and "Category" in df.columns:
        data = data[data["Category"] == category]

    if year and "Year" in df.columns:
        data = data[data["Year"] == year]

    if month and "Month" in df.columns:
        data = data[data["Month"] == month]

    return data


# -----------------------------
# UI
# -----------------------------
page = st.sidebar.radio("Navigation", ["Dashboard","Dataset Explorer","Executive Insights"])

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "Dashboard":

    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("Dashboard")
        st.image("powerbi_dashboard.png", use_container_width=True)

    with col2:
        st.subheader("AI Copilot")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])

        question = st.chat_input("Ask a business question")

        if question:

            st.session_state.chat_history.append({"role":"user","content":question})

            q, year, month, product, region, category, top_n, metric = extract_entities(question)

            response = {"role":"assistant"}

            # -----------------------------
            # SALES
            # -----------------------------
            if metric == "sales":

                data = apply_filters(sales, product, region, category, year, month)
                total_sales = data["Sales"].sum()

                response["content"] = f"💰 Total Sales: {round(total_sales,2)}"

            # -----------------------------
            # RETURNS
            # -----------------------------
            elif metric == "returns":

                data = apply_filters(returns, product, region, category, year, month)
                total_returns = data["Returns"].sum()

                response["content"] = f"🔁 Total Returns: {int(total_returns)}"

            # -----------------------------
            # CANCELLATIONS
            # -----------------------------
            elif metric == "cancellations":

                if "Cancellations" not in returns.columns:
                    response["content"] = "⚠️ Cancellations data not available"

                else:
                    data = apply_filters(returns, product, region, category, year, month)
                    total_cancel = data["Cancellations"].sum()

                    response["content"] = f"❌ Total Cancellations: {int(total_cancel)}"

            # -----------------------------
            # RATE ANALYSIS
            # -----------------------------
            elif "rate" in q or "ratio" in q:

                data_sales = apply_filters(sales, product, region, category, year, month)
                data_returns = apply_filters(returns, product, region, category, year, month)

                total_sales = data_sales["Sales"].sum()
                total_returns = data_returns["Returns"].sum()
                total_cancel = data_returns["Cancellations"].sum() if "Cancellations" in data_returns.columns else 0

                cancel_rate = (total_cancel / total_sales * 100) if total_sales != 0 else 0
                return_rate = (total_returns / total_sales * 100) if total_sales != 0 else 0

                response["content"] = f"""
📊 Return Rate: {round(return_rate,2)}%
❌ Cancellation Rate: {round(cancel_rate,2)}%

🔍 Insight:
{'⚠️ High cancellations observed' if cancel_rate > return_rate else 'Returns are higher than cancellations'}
"""

            # -----------------------------
            # COMBINED ANALYSIS
            # -----------------------------
            elif "return" in q and "cancel" in q:

                data = apply_filters(returns, product, region, category, year, month)

                total_returns = data["Returns"].sum()
                total_cancel = data["Cancellations"].sum()

                response["content"] = f"""
🔁 Returns: {int(total_returns)}
❌ Cancellations: {int(total_cancel)}
"""

            else:
                response["content"] = "Try asking about sales, returns, cancellations, or rates."

            st.session_state.chat_history.append(response)
            st.rerun()

# -----------------------------
# DATASET EXPLORER
# -----------------------------
elif page == "Dataset Explorer":
    st.dataframe(sales)

# -----------------------------
# EXECUTIVE INSIGHTS
# -----------------------------
elif page == "Executive Insights":

    st.subheader("Insights")

    top_product = sales.groupby("Product")["Sales"].sum().idxmax()
    high_returns = returns.groupby("Product")["Returns"].sum().idxmax()

    st.success(f"Top Product: {top_product}")
    st.warning(f"Highest Returns: {high_returns}")
