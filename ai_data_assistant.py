import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Enterprise AI Analytics Platform",
    layout="wide"
)

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
return_rate = returns["Returns"].sum()
traffic_growth = website["Visits"].iloc[-1] - website["Visits"].iloc[0]

col1.metric("Total Revenue", f"{total_revenue}")
col2.metric("Top Product", top_product)
col3.metric("Total Returns", f"{return_rate}")
col4.metric("Traffic Growth", f"{traffic_growth}")

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
# AI EXECUTIVE REPORT
# -----------------------------

st.subheader("AI Executive Report")

try:

    sales_summary = sales.groupby("Product")["Sales"].sum()

    top_product = sales_summary.idxmax()
    top_sales = sales_summary.max()

    low_product = sales_summary.idxmin()

    return_summary = returns.groupby("Product")["Returns"].sum()
    high_returns = return_summary.idxmax()

    first_visit = website["Visits"].iloc[0]
    last_visit = website["Visits"].iloc[-1]

    if last_visit > first_visit:
        traffic_trend = "increasing"
    else:
        traffic_trend = "declining"

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

except:
    st.warning("AI executive insights unavailable.")

# -----------------------------
# SALES OVERVIEW CHART
# -----------------------------

st.subheader("Sales Overview")

sales_by_product = sales.groupby("Product")["Sales"].sum()

fig, ax = plt.subplots()

sales_by_product.plot(kind="bar", ax=ax)

ax.set_title("Total Sales by Product")

st.pyplot(fig)

# -----------------------------
# AI COPILOT SECTION
# -----------------------------

st.subheader("AI Data Copilot")

# Create chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])

    else:
        st.chat_message("assistant").write(msg["content"])


# Chat input
prompt = st.chat_input("Ask a question about your business data")

if prompt:

    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.chat_message("user").write(prompt)

    q = prompt.lower()

    response_text = "AI could not understand the question."

    detected_product = None

    products = sales["Product"].unique()

    for p in products:
        if str(p).lower() in q:
            detected_product = p

    with st.chat_message("assistant"):

        # -----------------------------
        # PRODUCT SALES
        # -----------------------------

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

        # -----------------------------
        # RETURNS
        # -----------------------------

        elif "return" in q:

            result = returns.groupby("Product")["Returns"].sum()

            response_text = "Return analysis generated."

            st.info(response_text)

            fig, ax = plt.subplots()

            result.plot(kind="bar", ax=ax)

            ax.set_title("Returns by Product")

            st.pyplot(fig)

        # -----------------------------
        # PRODUCT SHARE
        # -----------------------------

        elif "share" in q:

            result = share.groupby("Product")["SalesSharePercent"].mean()

            response_text = "Product share analysis generated."

            st.info(response_text)

            fig, ax = plt.subplots()

            result.plot(kind="pie", autopct="%1.1f%%", ax=ax)

            ax.set_title("Product Share")

            st.pyplot(fig)

        # -----------------------------
        # TRAFFIC
        # -----------------------------

        elif "traffic" in q or "visit" in q:

            trend = website.groupby("Date")["Visits"].sum()

            response_text = "Website traffic trend generated."

            st.info(response_text)

            fig, ax = plt.subplots()

            trend.plot(ax=ax)

            ax.set_title("Website Traffic Trend")

            st.pyplot(fig)

        # -----------------------------
        # SALES TREND
        # -----------------------------

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

    # Save AI response
    st.session_state.messages.append({"role": "assistant", "content": response_text})
