import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(page_title="Enterprise AI Analytics Platform", layout="wide")

st.title("Enterprise AI Analytics Platform")
st.write("Power BI Dashboard + AI Copilot for Business Insights")

# -----------------------------
# EXECUTIVE DASHBOARD
# -----------------------------

st.subheader("Executive Dashboard")

st.image("powerbi_dashboard.png", use_container_width=True)

# -----------------------------
# LOAD DATA
# -----------------------------

try:
    sales = pd.read_csv("sales_data.csv")
    share = pd.read_csv("product_share.csv")
    returns = pd.read_csv("returns_data.csv")
    website = pd.read_csv("website_data.csv")

except:
    st.error("Dataset loading failed. Check file names in GitHub.")
    st.stop()

sales["Date"] = pd.to_datetime(sales["Date"])
sales["Year"] = sales["Date"].dt.year

# -----------------------------
# KPI PANEL
# -----------------------------

st.subheader("Key Business Metrics")

col1, col2, col3, col4 = st.columns(4)

total_revenue = sales["Sales"].sum()
top_product = sales.groupby("Product")["Sales"].sum().idxmax()
total_returns = returns["Returns"].sum()
traffic_growth = website["Visits"].iloc[-1] - website["Visits"].iloc[0]

col1.metric("Total Revenue", total_revenue)
col2.metric("Top Product", top_product)
return_rate = (returns["Returns"].sum() / sales["Sales"].sum()) * 100
col3.metric("Return Rate", f"{round(return_rate,2)}%")
col4.metric("Traffic Growth", traffic_growth)

# -----------------------------
# DATASET PREVIEW
# -----------------------------

st.subheader("Dataset Preview")

preview = sales.copy()

if "SalesSharePercent" in share.columns:
    preview["SalesSharePercent"] = share["SalesSharePercent"]

if "Cancellations" in returns.columns:
    preview["Cancellations"] = returns["Cancellations"]

if "Returns" in returns.columns:
    preview["Returns"] = returns["Returns"]

st.dataframe(preview.head())

# -----------------------------
# SIDEBAR AI COPILOT
# -----------------------------

st.sidebar.title("AI Data Copilot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.sidebar.chat_message("user").write(msg["content"])

    else:
        st.sidebar.chat_message("assistant").write(msg["content"])

prompt = st.sidebar.chat_input("Ask about your business data")

# -----------------------------
# AI QUESTION ENGINE
# -----------------------------

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    q = prompt.lower()

    detected_product = None
    products = sales["Product"].unique()

    for p in products:
        if str(p).lower() in q:
            detected_product = p

    response_text = "AI could not understand the question."

    with st.sidebar.chat_message("assistant"):

    # -----------------------------
    # TOTAL SALES
    # -----------------------------
    
    if "total sales" in q or "total revenue" in q:
    
        total_sales = sales["Sales"].sum()
    
        response_text = f"Total sales across all products: {total_sales}"
    
        st.success(response_text)
    
    # -----------------------------
    # TOTAL RETURNS
    # -----------------------------
    
    elif "total returns" in q:
    
        total_returns = returns["Returns"].sum()
    
        response_text = f"Total returns across all products: {total_returns}"
    
        st.success(response_text)

        
        # PRODUCT SALES
        if detected_product and "sales" in q:

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

                response_text = f"Average sales of {detected_product} in {year}: {round(avg,2)}"

                st.success(response_text)

            else:

                total = data["Sales"].sum()

                response_text = f"Total sales of {detected_product}: {total}"

                st.success(response_text)

            fig, ax = plt.subplots()

            data.groupby("Date")["Sales"].sum().plot(ax=ax)

            ax.set_title(f"Sales Trend - {detected_product}")

            st.pyplot(fig)

        # RETURNS ANALYSIS
        elif "return" in q:

            result = returns.groupby("Product")["Returns"].sum()

            response_text = "Return analysis generated."

            st.info(response_text)

            fig, ax = plt.subplots()

            result.plot(kind="bar", ax=ax)

            ax.set_title("Returns by Product")

            st.pyplot(fig)

        # PRODUCT SHARE
        elif "share" in q:

            result = share.groupby("Product")["SalesSharePercent"].mean()

            response_text = "Product share analysis generated."

            st.info(response_text)

            fig, ax = plt.subplots()

            result.plot(kind="pie", autopct="%1.1f%%", ax=ax)

            ax.set_title("Product Share")

            st.pyplot(fig)

        # TRAFFIC TREND
        elif "traffic" in q or "visit" in q:

            trend = website.groupby("Date")["Visits"].sum()

            response_text = "Website traffic trend generated."

            st.info(response_text)

            fig, ax = plt.subplots()

            trend.plot(ax=ax)

            ax.set_title("Website Traffic Trend")

            st.pyplot(fig)

        # SALES TREND
        elif "trend" in q:

            trend = sales.groupby("Date")["Sales"].sum()

            response_text = "Sales trend generated."

            st.info(response_text)

            fig, ax = plt.subplots()

            trend.plot(ax=ax)

            ax.set_title("Sales Trend")

            st.pyplot(fig)

        else:

            st.warning(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})

    # -----------------------------
    # AI EXECUTIVE REPORT
    # -----------------------------

    st.subheader("AI Executive Report")

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
# FOOTER
# -----------------------------

st.write("---")

st.caption("Enterprise AI Analytics Platform | Powered by Rishikriti Technologies")
