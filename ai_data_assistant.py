import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="AI Copilot Dashboard", layout="wide")
st.title("🤖 AI Copilot Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
sales = pd.read_csv("sales_data.csv")
returns = pd.read_csv("returns_data.csv")
website = pd.read_csv("website_data.csv")

# -----------------------------
# DATE PREP
# -----------------------------
sales["Date"] = pd.to_datetime(sales["Date"])
sales["Year"] = sales["Date"].dt.year
sales["Month"] = sales["Date"].dt.month

# 🔥 Make RETURNS time-aware (IMPORTANT FIX)
returns_merged = sales[["Product","Date","Year","Month"]].merge(
    returns, on="Product", how="left"
)

# -----------------------------
# ENTITY EXTRACTION
# -----------------------------
def extract_entities(question):

    q = question.lower()

    # YEAR
    year_match = re.search(r"\b(20\d{2})\b", q)
    year = int(year_match.group()) if year_match else None

    # PRODUCT MATCH (robust)
    product = None
    for p in sales["Product"].unique():
        if str(p).lower() in q:
            product = p

    # TOP N
    top_match = re.search(r"top (\d+)", q)
    top_n = int(top_match.group(1)) if top_match else None

    # METRIC DETECTION
    if any(x in q for x in ["sales","revenue","income"]):
        metric = "sales"
    elif any(x in q for x in ["return","returns","refund"]):
        metric = "returns"
    elif any(x in q for x in ["top","best"]):
        metric = "top"
    else:
        metric = None

    return q, year, product, top_n, metric

# -----------------------------
# FILTER FUNCTION
# -----------------------------
def apply_filters(df, product, year):

    data = df.copy()

    if product:
        data = data[data["Product"] == product]

    if year and "Year" in df.columns:
        data = data[data["Year"] == year]

    return data

# -----------------------------
# INSIGHTS ENGINE (LIKE PBI)
# -----------------------------
def generate_insights():

    yearly = sales.groupby("Year")["Sales"].sum()

    if len(yearly) > 1:
        growth = ((yearly.iloc[-1] - yearly.iloc[0]) / yearly.iloc[0]) * 100
    else:
        growth = 0

    insight = f"📊 Revenue changed by {round(growth,2)}% over the period."

    return insight

# -----------------------------
# LAYOUT
# -----------------------------
col1, col2 = st.columns([2,1])

# -----------------------------
# LEFT: DASHBOARD IMAGE + INSIGHTS
# -----------------------------
with col1:

    st.subheader("📊 Executive Dashboard")
    st.image("powerbi_dashboard.png", use_container_width=True)

    st.subheader("📊 AI Insights")
    st.info(generate_insights())

# -----------------------------
# RIGHT: CHAT
# -----------------------------
with col2:

    st.subheader("💬 AI Copilot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    question = st.chat_input("Ask a business question...")

    if question:

        st.session_state.chat_history.append(
            {"role":"user","content":question}
        )

        try:
            q, year, product, top_n, metric = extract_entities(question)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

        response = {"role":"assistant"}

        # -----------------------------
        # SALES
        # -----------------------------
        if metric == "sales":

            data = apply_filters(sales, product, year)

            if top_n:
                result = data.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(top_n)
                response["content"] = f"🏆 Top {top_n} Products:\n{result.to_string()}"

            elif "vs" in q and year:
                prev = year - 1
                curr_val = sales[sales["Year"] == year]["Sales"].sum()
                prev_val = sales[sales["Year"] == prev]["Sales"].sum()

                growth = ((curr_val - prev_val)/prev_val*100) if prev_val != 0 else 0

                response["content"] = f"""
Sales {year}: {round(curr_val,2)}
Sales {prev}: {round(prev_val,2)}
Growth: {round(growth,2)}%
"""

            else:
                total = data["Sales"].sum()

                msg = "💰 Total Sales"

                if product:
                    msg += f" for {product}"
                if year:
                    msg += f" in {year}"

                msg += f": {round(total,2)}"

                if total == 0:
                    msg += "\n⚠️ No data found"

                response["content"] = msg

        # -----------------------------
        # RETURNS (FIXED)
        # -----------------------------
        elif metric == "returns":

            data = apply_filters(returns_merged, product, year)

            total = data["Returns"].sum()

            msg = "🔁 Total Returns"

            if product:
                msg += f" for {product}"
            if year:
                msg += f" in {year}"

            msg += f": {int(total)}"

            if total == 0:
                msg += "\n⚠️ No data found"

            response["content"] = msg

        # -----------------------------
        # TOP PRODUCTS
        # -----------------------------
        elif metric == "top":

            result = sales.groupby("Product")["Sales"].sum().sort_values(ascending=False)

            response["content"] = f"""
🏆 Top Products:
{result.head(5).to_string()}
"""

        else:
            response["content"] = "Try asking about sales, returns, or top products."

        st.session_state.chat_history.append(response)
        st.rerun()
