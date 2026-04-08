import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="AI Copilot Analytics", layout="wide")
st.title("🤖 AI Copilot (Power BI Style)")

# -----------------------------
# LOAD DATA (MATCH PBI)
# -----------------------------
sales = pd.read_csv("sales_data.csv")
returns = pd.read_csv("returns_data.csv")
share = pd.read_csv("product_share.csv")
website = pd.read_csv("website_data.csv")

# -----------------------------
# DATA PREP (CRITICAL)
# -----------------------------
sales["Date"] = pd.to_datetime(sales["Date"])
sales["Year"] = sales["Date"].dt.year
sales["Month"] = sales["Date"].dt.month

# Merge category into sales
sales = sales.merge(share, on="Product", how="left")

# Merge returns into sales
returns = returns.merge(share, on="Product", how="left")

# -----------------------------
# NORMALIZATION
# -----------------------------
def normalize(text):
    return str(text).lower().strip()

def smart_match(q, values):
    q = normalize(q)
    values = list(values)

    for v in values:
        if normalize(v) in q:
            return v

    matches = get_close_matches(q, [normalize(v) for v in values], n=1, cutoff=0.6)
    if matches:
        for v in values:
            if normalize(v) == matches[0]:
                return v

    return None

def detect_metric(q):
    if any(x in q for x in ["sales","revenue"]):
        return "sales"
    if any(x in q for x in ["return","refund"]):
        return "returns"
    if any(x in q for x in ["traffic","visit"]):
        return "traffic"
    return None

# -----------------------------
# ENTITY EXTRACTION
# -----------------------------
def extract_entities(question):

    q = normalize(question)

    year = None
    month = None

    year_match = re.search(r"\b(20\d{2})\b", q)
    if year_match:
        year = int(year_match.group())

    months = {
        "january":1,"february":2,"march":3,"april":4,
        "may":5,"june":6,"july":7,"august":8,
        "september":9,"october":10,"november":11,"december":12
    }

    for m in months:
        if m in q:
            month = months[m]

    product = smart_match(q, sales["Product"].unique())
    category = smart_match(q, sales["Category"].dropna().unique())

    top_match = re.search(r"top (\d+)", q)
    top_n = int(top_match.group(1)) if top_match else None

    metric = detect_metric(q)

    return q, year, month, product, category, top_n, metric

# -----------------------------
# FILTER ENGINE
# -----------------------------
def apply_filters(df, product, category, year, month):

    data = df.copy()

    if product:
        data = data[data["Product"] == product]

    if category:
        data = data[data["Category"] == category]

    if year and "Year" in df.columns:
        data = data[data["Year"] == year]

    if month and "Month" in df.columns:
        data = data[data["Month"] == month]

    return data

# -----------------------------
# KPI PANEL (LIKE PBI)
# -----------------------------
st.subheader("📊 Executive KPIs")

k1,k2,k3 = st.columns(3)

k1.metric("Total Sales", round(sales["Sales"].sum(),2))
k2.metric("Total Returns", returns["Returns"].sum())
k3.metric("Top Product", sales.groupby("Product")["Sales"].sum().idxmax())

# -----------------------------
# CHAT
# -----------------------------
st.subheader("💬 AI Copilot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

question = st.chat_input("Ask your business question...")

if question:

    st.session_state.chat_history.append({"role":"user","content":question})

    q, year, month, product, category, top_n, metric = extract_entities(question)

    response = {"role":"assistant"}

    # -----------------------------
    # SALES
    # -----------------------------
    if metric == "sales":

        data = apply_filters(sales, product, category, year, month)

        if top_n:
            result = data.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(top_n)
            response["content"] = f"🏆 Top {top_n} Products:\n{result.to_string()}"

        elif "vs" in q and year:
            prev = year - 1
            curr_val = sales[sales["Year"] == year]["Sales"].sum()
            prev_val = sales[sales["Year"] == prev]["Sales"].sum()

            growth = ((curr_val-prev_val)/prev_val*100) if prev_val != 0 else 0

            response["content"] = f"""
Sales {year}: {round(curr_val,2)}
Sales {prev}: {round(prev_val,2)}
Growth: {round(growth,2)}%
"""

        else:
            total = data["Sales"].sum()

            msg = "💰 Total Sales"

            if product: msg += f" for {product}"
            if category: msg += f" ({category})"
            if year: msg += f" {year}"

            msg += f": {round(total,2)}"

            if total == 0:
                msg += "\n⚠️ No matching data found"

            response["content"] = msg

        # Chart
        fig, ax = plt.subplots()
        data.groupby("Date")["Sales"].sum().plot(ax=ax)
        st.pyplot(fig)

    # -----------------------------
    # RETURNS
    # -----------------------------
    elif metric == "returns":

        data = apply_filters(returns, product, category, year, month)

        total = data["Returns"].sum()
        response["content"] = f"🔁 Total Returns: {total}"

    # -----------------------------
    # TRAFFIC
    # -----------------------------
    elif metric == "traffic":

        trend = website.groupby("Date")["Visits"].sum()

        fig, ax = plt.subplots()
        trend.plot(ax=ax)
        st.pyplot(fig)

        response["content"] = "🌐 Website traffic trend displayed"

    else:
        response["content"] = "Try asking about sales, returns, or top products."

    st.session_state.chat_history.append(response)
    st.rerun()
