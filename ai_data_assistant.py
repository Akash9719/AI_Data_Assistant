import streamlit as st
import pandas as pd
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

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

# -----------------------------
# ENTERPRISE DATA MODEL
# -----------------------------
sales["Date"] = pd.to_datetime(sales["Date"])
sales["Year"] = sales["Date"].dt.year
sales["Month"] = sales["Date"].dt.month

# 🔥 Convert aggregated returns → time-aware
returns_expanded = sales[["Product","Date","Year","Month"]].merge(
    returns, on="Product", how="left"
)

# Normalize per product (VERY IMPORTANT)
returns_expanded["Returns"] = returns_expanded["Returns"] / \
    returns_expanded.groupby("Product")["Date"].transform("count")

if "Cancellations" in returns_expanded.columns:
    returns_expanded["Cancellations"] = returns_expanded["Cancellations"] / \
        returns_expanded.groupby("Product")["Date"].transform("count")

# -----------------------------
# ENTITY EXTRACTION
# -----------------------------
def extract_entities(question):

    q = question.lower()

    year_match = re.search(r"\b(20\d{2})\b", q)
    year = int(year_match.group()) if year_match else None

    month = None
    months = {
        "january":1,"february":2,"march":3,"april":4,
        "may":5,"june":6,"july":7,"august":8,
        "september":9,"october":10,"november":11,"december":12
    }

    for m in months:
        if m in q:
            month = months[m]

    product = None
    for p in sales["Product"].unique():
        if str(p).lower() in q:
            product = p

    top_match = re.search(r"top (\d+)", q)
    top_n = int(top_match.group(1)) if top_match else None

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

    return q, year, month, product, top_n, metric

# -----------------------------
# KPI CALCULATION (DAX-LIKE)
# -----------------------------
def calculate_kpis(product=None, year=None):

    s = sales.copy()
    r = returns_expanded.copy()

    if product:
        s = s[s["Product"] == product]
        r = r[r["Product"] == product]

    if year:
        s = s[s["Year"] == year]
        r = r[r["Year"] == year]

    total_sales = s["Sales"].sum()
    total_returns = r["Returns"].sum()

    total_cancel = 0
    if "Cancellations" in r.columns:
        total_cancel = r["Cancellations"].sum()

    return_rate = (total_returns / total_sales * 100) if total_sales else 0
    cancel_rate = (total_cancel / total_sales * 100) if total_sales else 0

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
# NAVIGATION
# -----------------------------
page = st.sidebar.radio("Navigation", ["Dashboard","Dataset Explorer","AI Insights"])

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "Dashboard":

    col1, col2 = st.columns([2,1])

    # LEFT SIDE
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

    # RIGHT SIDE (CHAT)
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

            q, year, month, product, top_n, metric = extract_entities(question)

            response = {"role":"assistant"}

            if metric == "sales":

                data = sales.copy()

                if product:
                    data = data[data["Product"] == product]
                if year:
                    data = data[data["Year"] == year]

                response["content"] = f"Total Sales: {round(data['Sales'].sum(),2)}"

            elif metric == "returns":

                data = returns_expanded.copy()

                if product:
                    data = data[data["Product"] == product]
                if year:
                    data = data[data["Year"] == year]

                response["content"] = f"Total Returns: {int(data['Returns'].sum())}"

            elif metric == "cancellations":

                data = returns_expanded.copy()

                if product:
                    data = data[data["Product"] == product]
                if year:
                    data = data[data["Year"] == year]

                response["content"] = f"Total Cancellations: {int(data['Cancellations'].sum())}"

            elif metric == "rate":

                total_sales, total_returns, total_cancel, return_rate, cancel_rate = calculate_kpis(product, year)

                response["content"] = f"""
Return Rate: {round(return_rate,2)}%
Cancellation Rate: {round(cancel_rate,2)}%
"""

            else:
                response["content"] = "Try asking about sales, returns, cancellations or rates."

            st.session_state.chat_history.append(response)
            st.rerun()

# -----------------------------
# DATASET EXPLORER
# -----------------------------
elif page == "Dataset Explorer":

    st.subheader("📂 Dataset Explorer")

    option = st.selectbox("Select dataset", ["Sales","Returns"])

    if option == "Sales":
        st.dataframe(sales)
    else:
        st.dataframe(returns)

# -----------------------------
# AI INSIGHTS
# -----------------------------
elif page == "AI Insights":

    st.subheader("🧠 AI Insights")

    total_sales = sales["Sales"].sum()
    total_returns = returns["Returns"].sum()

    return_rate = (total_returns / total_sales * 100) if total_sales else 0

    top_product = sales.groupby("Product")["Sales"].sum().idxmax()

    st.success(f"🏆 Top Product: {top_product}")
    st.warning(f"🔁 Return Rate: {round(return_rate,2)}%")

    if return_rate > 20:
        st.error("⚠️ High return rate detected")
    else:
        st.info("✅ Return rate is normal")

    pdf = generate_pdf()

    st.download_button(
        "📄 Download Report",
        pdf,
        file_name="AI_Report.pdf"
    )
