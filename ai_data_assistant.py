import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
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
sales["Month_Name"] = sales["Date"].dt.strftime("%B")

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def extract_entities(question):
    q = question.lower()

    # YEAR
    year_match = re.search(r"\b(20\d{2})\b", q)
    year = int(year_match.group()) if year_match else None

    # MONTH
    months = {
        "january":1,"february":2,"march":3,"april":4,
        "may":5,"june":6,"july":7,"august":8,
        "september":9,"october":10,"november":11,"december":12
    }

    month = None
    for m in months:
        if m in q:
            month = months[m]

    # PRODUCT
    product = None
    for p in sales["Product"].unique():
        if str(p).lower() in q:
            product = p

    # REGION
    region = None
    if "Region" in sales.columns:
        for r in sales["Region"].dropna().unique():
            if str(r).lower() in q:
                region = r

    # CATEGORY
    category = None
    if "Category" in sales.columns:
        for c in sales["Category"].dropna().unique():
            if str(c).lower() in q:
                category = c

    # TOP N
    top_match = re.search(r"top (\d+)", q)
    top_n = int(top_match.group(1)) if top_match else None

    return q, year, month, product, region, category, top_n


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


def generate_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    total_sales = sales["Sales"].sum()
    top_product = sales.groupby("Product")["Sales"].sum().idxmax()

    c.drawString(50,750,"AI Executive Report")
    c.drawString(50,700,f"Total Sales: {round(total_sales,2)}")
    c.drawString(50,670,f"Top Product: {top_product}")

    c.save()
    buffer.seek(0)
    return buffer


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

            q, year, month, product, region, category, top_n = extract_entities(question)

            response = {"role":"assistant"}

            # -----------------------------
            # SALES
            # -----------------------------
            if "sales" in q or "revenue" in q:

                data = apply_filters(sales, product, region, category, year, month)

                # TOP N
                if top_n:
                    result = data.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(top_n)
                    response["content"] = f"Top {top_n} Products:\n{result.to_string()}"

                # YOY
                elif "vs" in q and year:
                    prev_year = year - 1

                    curr = sales[sales["Year"] == year]["Sales"].sum()
                    prev = sales[sales["Year"] == prev_year]["Sales"].sum()

                    growth = ((curr - prev)/prev*100) if prev != 0 else 0

                    response["content"] = f"""
Sales {year}: {round(curr,2)}
Sales {prev_year}: {round(prev,2)}
Growth: {round(growth,2)}%
"""

                # NORMAL
                else:
                    total = data["Sales"].sum()

                    msg = "Total sales"

                    if product: msg += f" for {product}"
                    if category: msg += f" ({category})"
                    if region: msg += f" in {region}"
                    if month: msg += f" Month {month}"
                    if year: msg += f" {year}"

                    msg += f": {round(total,2)}"

                    if total == 0:
                        msg += "\n⚠️ No data found"

                    response["content"] = msg

            # -----------------------------
            # RETURNS
            # -----------------------------
            elif "return" in q:

                data = apply_filters(returns, product, region, category, year, month)

                if top_n:
                    result = data.groupby("Product")["Returns"].sum().sort_values(ascending=False).head(top_n)
                    response["content"] = f"Top {top_n} Returns:\n{result.to_string()}"
                else:
                    total = data["Returns"].sum()
                    response["content"] = f"Total Returns: {total}"

            # -----------------------------
            # TRAFFIC
            # -----------------------------
            elif "traffic" in q or "visit" in q:
                trend = website.groupby("Date")["Visits"].sum()

                fig, ax = plt.subplots()
                trend.plot(ax=ax)
                st.pyplot(fig)

                response["content"] = "Website traffic trend shown."

            else:
                response["content"] = "Try asking about sales, returns, or comparisons."

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

    pdf = generate_pdf()

    st.download_button(
        label="Download Report",
        data=pdf,
        file_name="report.pdf"
    )
