import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="AI Copilot Analytics", layout="wide")
st.title("🤖 AI Analytics Copilot")

# -----------------------------
# LOAD DATA
# -----------------------------
sales = pd.read_csv("sales_data.csv")
returns = pd.read_csv("returns_data.csv")
website = pd.read_csv("website_data.csv")

# DATE FEATURES
sales["Date"] = pd.to_datetime(sales["Date"])
sales["Year"] = sales["Date"].dt.year
sales["Month"] = sales["Date"].dt.month

returns["Date"] = pd.to_datetime(returns["Date"])
returns["Year"] = returns["Date"].dt.year
returns["Month"] = returns["Date"].dt.month

# -----------------------------
# NORMALIZATION + MATCHING
# -----------------------------
def normalize(text):
    return str(text).lower().strip()

def smart_match(user_text, values):
    user_text = normalize(user_text)
    values_clean = [normalize(v) for v in values]

    for v in values:
        if normalize(v) in user_text:
            return v

    match = get_close_matches(user_text, values_clean, n=1, cutoff=0.6)
    if match:
        for v in values:
            if normalize(v) == match[0]:
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

    product = smart_match(q, sales["Product"].unique())
    region = smart_match(q, sales["Region"].dropna().unique()) if "Region" in sales.columns else None
    category = smart_match(q, sales["Category"].dropna().unique()) if "Category" in sales.columns else None

    top_match = re.search(r"top (\d+)", q)
    top_n = int(top_match.group(1)) if top_match else None

    metric = detect_metric(q)

    return q, year, month, product, region, category, top_n, metric

# -----------------------------
# FILTER ENGINE
# -----------------------------
def apply_filters(df, product, region, category, year, month):

    data = df.copy()

    if product and "Product" in df.columns:
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
# AUTO INSIGHTS
# -----------------------------
def generate_insights(data):

    insights = []

    if "Sales" in data.columns and len(data) > 1:

        trend = data.groupby("Date")["Sales"].sum()

        if len(trend) > 1:
            if trend.iloc[-1] > trend.iloc[0]:
                insights.append("📈 Sales are increasing")
            else:
                insights.append("📉 Sales are declining")

    if "Product" in data.columns:
        try:
            top = data.groupby("Product")["Sales"].sum().idxmax()
            insights.append(f"🏆 Top product: {top}")
        except:
            pass

    return insights

# -----------------------------
# KPI PANEL
# -----------------------------
st.subheader("📊 Live KPIs")

k1,k2,k3 = st.columns(3)

k1.metric("Total Sales", round(sales["Sales"].sum(),2))
k2.metric("Total Returns", returns["Returns"].sum())
k3.metric("Website Visits", website["Visits"].sum())

# -----------------------------
# CHAT UI
# -----------------------------
st.subheader("💬 AI Copilot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

question = st.chat_input("Ask anything about your data...")

if question:

    st.session_state.chat_history.append({"role":"user","content":question})

    q, year, month, product, region, category, top_n, metric = extract_entities(question)

    response = {"role":"assistant"}

    # -----------------------------
    # SALES
    # -----------------------------
    if metric == "sales":

        data = apply_filters(sales, product, region, category, year, month)

        if "vs" in q and year:
            prev_year = year - 1

            curr = sales[sales["Year"] == year]["Sales"].sum()
            prev = sales[sales["Year"] == prev_year]["Sales"].sum()

            growth = ((curr - prev)/prev*100) if prev != 0 else 0

            response["content"] = f"""
📊 Sales {year}: {round(curr,2)}
📊 Sales {prev_year}: {round(prev,2)}
📈 Growth: {round(growth,2)}%
"""

        elif top_n:
            result = data.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(top_n)
            response["content"] = f"🏆 Top {top_n} Products:\n{result.to_string()}"

        else:
            total = data["Sales"].sum()

            msg = "💰 Total sales"

            if product: msg += f" for {product}"
            if category: msg += f" ({category})"
            if region: msg += f" in {region}"
            if year: msg += f" {year}"

            msg += f": {round(total,2)}"

            if total == 0:
                msg += "\n⚠️ No data found"

            response["content"] = msg

    # -----------------------------
    # RETURNS
    # -----------------------------
    elif metric == "returns":

        data = apply_filters(returns, product, region, category, year, month)

        total = data["Returns"].sum()
        response["content"] = f"🔁 Total returns: {total}"

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
        response["content"] = "Try asking about sales, returns, or traffic."

    st.session_state.chat_history.append(response)

    # -----------------------------
    # DISPLAY RESPONSE (POLISHED)
    # -----------------------------
    with st.chat_message("assistant"):

        st.markdown("### 💡 Answer")
        st.write(response["content"])

        # AUTO INSIGHTS
        if metric == "sales":
            insights = generate_insights(data)

            if insights:
                st.markdown("### 📊 Insights")
                for i in insights:
                    st.write(f"- {i}")

        # CHART
        if metric == "sales":
            fig, ax = plt.subplots()
            data.groupby("Date")["Sales"].sum().plot(ax=ax)
            st.pyplot(fig)

    st.rerun()
