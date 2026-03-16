import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(page_title="Enterprise AI Analytics Platform", layout="wide")

st.title("Enterprise AI Analytics Platform")

# -----------------------------
# LOAD DATA
# -----------------------------

sales = pd.read_csv("sales_data.csv")
share = pd.read_csv("product_share.csv")
returns = pd.read_csv("returns_data.csv")
website = pd.read_csv("website_data.csv")

sales["Date"] = pd.to_datetime(sales["Date"])
sales["Year"] = sales["Date"].dt.year

# -----------------------------
# GENERATE EXECUTIVE PDF REPORT
# -----------------------------

def generate_pdf_report():

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Enterprise AI Analytics Executive Report")

    c.setFont("Helvetica", 12)

    # Business Metrics
    total_revenue = sales["Sales"].sum()
    top_product = sales.groupby("Product")["Sales"].sum().idxmax()
    return_summary = returns.groupby("Product")["Returns"].sum()
    high_returns = return_summary.idxmax()

    first_visit = website["Visits"].iloc[0]
    last_visit = website["Visits"].iloc[-1]

    traffic_trend = "Increasing" if last_visit > first_visit else "Declining"

    y = height - 100

    c.drawString(50, y, f"Total Revenue: {round(total_revenue,2)}")
    y -= 25

    c.drawString(50, y, f"Top Product: {top_product}")
    y -= 25

    c.drawString(50, y, f"Highest Returns Product: {high_returns}")
    y -= 25

    c.drawString(50, y, f"Website Traffic Trend: {traffic_trend}")
    y -= 40

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Strategic Recommendations")
    y -= 25

    c.setFont("Helvetica", 11)

    c.drawString(50, y, f"- Increase marketing focus on {top_product}")
    y -= 20

    c.drawString(50, y, f"- Investigate return causes for {high_returns}")
    y -= 20

    c.drawString(50, y, "- Monitor website engagement trends")

    c.save()

    buffer.seek(0)

    return buffer



# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "AI Copilot",
        "Dataset Explorer",
        "Executive Insights"
    ]
)

# -----------------------------
# DASHBOARD PAGE
# -----------------------------

if page == "Dashboard":

    st.subheader("Executive Dashboard")

    st.image("powerbi_dashboard.png", use_container_width=True)

    st.subheader("Key Business Metrics")

    col1, col2, col3, col4 = st.columns(4)

    total_revenue = sales["Sales"].sum()
    top_product = sales.groupby("Product")["Sales"].sum().idxmax()
    return_rate = (returns["Returns"].sum() / sales["Sales"].sum()) * 100
    traffic_growth = website["Visits"].iloc[-1] - website["Visits"].iloc[0]

    col1.metric("Total Revenue", round(total_revenue,2))
    col2.metric("Top Product", top_product)
    col3.metric("Return Rate", f"{round(return_rate,2)}%")
    col4.metric("Traffic Growth", traffic_growth)

# -----------------------------
# DATASET EXPLORER
# -----------------------------

elif page == "Dataset Explorer":

    st.subheader("Dataset Explorer")

    dataset_choice = st.selectbox(
        "Select dataset",
        ["Sales", "Returns", "Product Share", "Website Traffic"]
    )

    if dataset_choice == "Sales":
        st.dataframe(sales)

    elif dataset_choice == "Returns":
        st.dataframe(returns)

    elif dataset_choice == "Product Share":
        st.dataframe(share)

    elif dataset_choice == "Website Traffic":
        st.dataframe(website)

# -----------------------------
# AI COPILOT PAGE
# -----------------------------

elif page == "AI Copilot":

    st.subheader("AI Data Copilot")

    question = st.text_input(
        "Ask a business question",
        placeholder="Example: average sales of board games in 2018"
    )

    if question:

        q = question.lower()

        detected_product = None
        products = sales["Product"].unique()

        for p in products:
            if str(p).lower() in q:
                detected_product = p

        # TOTAL SALES
        if "total sales" in q or "total revenue" in q:

            total_sales = sales["Sales"].sum()

            st.success(f"Total sales across all products: {round(total_sales,2)}")

        # TOTAL RETURNS
        elif "total returns" in q:

            total_returns = returns["Returns"].sum()

            st.success(f"Total returns across all products: {total_returns}")

        # PRODUCT SALES
        elif detected_product and "sales" in q:

            data = sales[sales["Product"] == detected_product]

            year = None

            if "2018" in q:
                year = 2018
            elif "2019" in q:
                year = 2019
            elif "2020" in q:
                year = 2020

            if year:
                data = data[data["Year"] == year]

            if "average" in q:

                avg = data["Sales"].mean()

                st.success(
                    f"Average sales of {detected_product} in {year}: {round(avg,2)}"
                )

            else:

                total = data["Sales"].sum()

                st.success(f"Total sales of {detected_product}: {total}")

            fig, ax = plt.subplots()

            data.groupby("Date")["Sales"].sum().plot(ax=ax)

            ax.set_title(f"Sales Trend - {detected_product}")

            st.pyplot(fig)

        # RETURNS ANALYSIS
        elif "return" in q:

            result = returns.groupby("Product")["Returns"].sum()

            fig, ax = plt.subplots()

            result.plot(kind="bar", ax=ax)

            ax.set_title("Returns by Product")

            st.pyplot(fig)

        # TRAFFIC TREND
        elif "traffic" in q or "visit" in q:

            trend = website.groupby("Date")["Visits"].sum()

            fig, ax = plt.subplots()

            trend.plot(ax=ax)

            ax.set_title("Website Traffic Trend")

            st.pyplot(fig)

        # SALES TREND
        elif "trend" in q:

            trend = sales.groupby("Date")["Sales"].sum()

            fig, ax = plt.subplots()

            trend.plot(ax=ax)

            ax.set_title("Sales Trend")

            st.pyplot(fig)

        else:

            st.warning("AI could not understand the question.")

# -----------------------------
# EXECUTIVE INSIGHTS PAGE
# -----------------------------

elif page == "Executive Insights":

    st.subheader("AI Executive Insights")

    sales_summary = sales.groupby("Product")["Sales"].sum()

    top_product = sales_summary.idxmax()
    top_sales = sales_summary.max()

    return_summary = returns.groupby("Product")["Returns"].sum()
    high_returns = return_summary.idxmax()

    first_visit = website["Visits"].iloc[0]
    last_visit = website["Visits"].iloc[-1]

    traffic_trend = "increasing" if last_visit > first_visit else "declining"

    st.success(
        f"Top Revenue Driver: **{top_product}** generates the highest sales ({top_sales})."
    )

    st.warning(
        f"Product Risk: **{high_returns}** has the highest return volume."
    )

    st.info(
        f"Website traffic is **{traffic_trend}**, indicating changing customer demand."
    )

    st.write("### Strategic Recommendations")

    st.write(f"• Focus marketing investment on **{top_product}** to maximize revenue.")

    st.write(f"• Investigate quality issues causing high returns in **{high_returns}**.")

    st.write("• Monitor website engagement to optimize marketing performance.")

# -----------------------------
# DOWNLOAD EXECUTIVE REPORT
# -----------------------------

st.subheader("Download Executive Report")

pdf_file = generate_pdf_report()

st.download_button(
    label="Download AI Executive Report (PDF)",
    data=pdf_file,
    file_name="AI_Executive_Report.pdf",
    mime="application/pdf"
)
