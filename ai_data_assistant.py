import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

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

# -----------------------------
# DATE PREP
# -----------------------------
sales["Date"] = pd.to_datetime(sales["Date"])
sales["Year"] = sales["Date"].dt.year
sales["Month"] = sales["Date"].dt.month

# 🔥 Time-aware returns (Power BI style relationship)
returns_merged = sales[["Product","Date","Year","Month"]].merge(
    returns, on="Product", how="left"
)

# -----------------------------
# ENTITY EXTRACTION
# -----------------------------
def extract_entities(question):

    q = question.lower()

    year_match = re.search(r"\b(20\d{2})\b", q)
    year = int(year_match.group()) if year_match else None

    product = None
    for p in sales["Product"].unique():
        if str(p).lower() in q:
            product = p

    top_match = re.search(r"top (\d+)", q)
    top_n = int(top_match.group(1)) if top_match else None

    # Metric detection
    if any(x in q for x in ["sales","revenue"]):
        metric = "sales"
    elif any(x in q for x in ["return","returns"]):
        metric = "returns"
    elif any(x in q for x in ["cancel"]):
        metric = "cancellations"
    elif "rate" in q or "ratio" in q:
        metric = "rate"
    else:
        metric = None

    return q, year, product, top_n, metric

# -----------------------------
# FILTER ENGINE (DAX-LIKE)
# -----------------------------
def apply_filters(df, product, year):

    data = df.copy()

    if product:
        data = data[data["Product"] == product]

    if year and "Year" in df.columns:
        data = data[data["Year"] == year]

    return data

# -----------------------------
# KPI FUNCTION (DYNAMIC)
# -----------------------------
def calculate_kpis(product=None, year=None):

    s = apply_filters(sales, product, year)
    r = apply_filters(returns_merged, product, year)

    total_sales = s["Sales"].sum()
    total_returns = r["Returns"].sum()
    total_cancel = r["Cancellations"].sum() if "Cancellations" in r.columns else 0

    cancel_rate = (total_cancel / total_sales * 100) if total_sales else 0
    return_rate = (total_returns / total_sales * 100) if total_sales else 0

    return total_sales, total_returns, total_cancel, return_rate, cancel_rate

# -----------------------------
# PDF GENERATOR
# -----------------------------
def generate_pdf():

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    total_sales = sales["Sales"].sum()
    total_returns = returns["Returns"].sum()

    c.drawString(50,750,"AI Executive Report")
    c.drawString(50,700,f"Total Sales: {round(total_sales,2)}")
    c.drawString(50,670,f"Total Returns: {int(total_returns)}")

    c.save()
    buffer.seek(0)

    return buffer

# -----------------------------
# LAYOUT
# -----------------------------
col1, col2 = st.columns([2,1])

# -----------------------------
# LEFT SIDE (Dashboard + KPIs)
# -----------------------------
with col1:

    st.subheader("📊 Executive KPIs")

    total_sales, total_returns, total_cancel, return_rate, cancel_rate = calculate_kpis()

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Sales", round(total_sales,2))
    k2.metric("Returns", int(total_returns))
    k3.metric("Return %", f"{round(return_rate,2)}%")
    k4.metric("Cancel %", f"{round(cancel_rate,2)}%")

    st.subheader("📊 Dashboard")
    st.image("powerbi_dashboard.png", use_container_width=True)

# -----------------------------
# RIGHT SIDE (CHAT)
# -----------------------------
with col2:

    st.subheader("💬 AI Copilot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    question = st.chat_input("Ask a question...")

    if question:

        st.session_state.chat_history.append({"role":"user","content":question})

        q, year, product, top_n, metric = extract_entities(question)

        response = {"role":"assistant"}

        # SALES
        if metric == "sales":

            data = apply_filters(sales, product, year)

            if top_n:
                result = data.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(top_n)
                response["content"] = result.to_string()

            else:
                total = data["Sales"].sum()
                response["content"] = f"Total Sales: {round(total,2)}"

        # RETURNS
        elif metric == "returns":

            data = apply_filters(returns_merged, product, year)
            total = data["Returns"].sum()

            response["content"] = f"Total Returns: {int(total)}"

        # CANCELLATIONS
        elif metric == "cancellations":

            data = apply_filters(returns_merged, product, year)
            total = data["Cancellations"].sum()

            response["content"] = f"Total Cancellations: {int(total)}"

        # RATE ANALYSIS
        elif metric == "rate":

            s = apply_filters(sales, product, year)
            r = apply_filters(returns_merged, product, year)

            total_sales = s["Sales"].sum()
            total_returns = r["Returns"].sum()
            total_cancel = r["Cancellations"].sum()

            return_rate = (total_returns / total_sales * 100) if total_sales else 0
            cancel_rate = (total_cancel / total_sales * 100) if total_sales else 0

            response["content"] = f"""
Return Rate: {round(return_rate,2)}%
Cancellation Rate: {round(cancel_rate,2)}%
"""

        else:
            response["content"] = "Try sales, returns, cancellations, or rates."

        st.session_state.chat_history.append(response)
        st.rerun()

# -----------------------------
# PDF DOWNLOAD
# -----------------------------
pdf = generate_pdf()

st.download_button(
    "📄 Download Report",
    pdf,
    file_name="report.pdf"
)
