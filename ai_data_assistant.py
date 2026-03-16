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
# DATA PREVIEW
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

    # Total revenue by product
    sales_summary = sales.groupby("Product")["Sales"].sum()

    top_product = sales_summary.idxmax()
    top_sales = sales_summary.max()

    # Lowest performing product
    low_product = sales_summary.idxmin()

    # Returns analysis
    if "Returns" in returns.columns:
        return_summary = returns.groupby("Product")["Returns"].sum()
        high_returns = return_summary.idxmax()
    else:
        high_returns = "Unknown"

    # Website traffic trend
    if "Visits" in website.columns:
        first_visit = website["Visits"].iloc[0]
        last_visit = website["Visits"].iloc[-1]

        if last_visit > first_visit:
            traffic_trend = "increasing"
        else:
            traffic_trend = "declining"
    else:
        traffic_trend = "unknown"

    # Executive insights
    st.success(f"Top Revenue Driver: **{top_product}** generates the highest sales ({top_sales}).")

    st.warning(f"Product Risk: **{high_returns}** has the highest return volume.")

    st.info(f"Website traffic is **{traffic_trend}**, indicating changing customer demand.")

    st.write("### Strategic Recommendations")

    st.write(f"• Focus marketing investment on **{top_product}** to maximize revenue growth.")

    st.write(f"• Investigate quality or logistics issues causing high returns in **{high_returns}**.")

    st.write("• Monitor website engagement trends to optimize digital marketing performance.")

except:

    st.error("AI Executive Report could not be generated.")
# -----------------------------
# AUTO AI INSIGHTS
# -----------------------------

st.subheader("AI Executive Insights")

top_product = sales.groupby("Product")["Sales"].sum().idxmax()
top_value = sales.groupby("Product")["Sales"].sum().max()

highest_returns = returns.groupby("Product")["Returns"].sum().idxmax()

traffic_growth = website["Visits"].iloc[-1] - website["Visits"].iloc[0]

st.success(f"Top Product: {top_product} generates the highest revenue ({top_value}).")

st.warning(f"Returns Insight: {highest_returns} has the highest product returns.")

if traffic_growth > 0:
    st.info("Website traffic is growing over time, indicating increasing demand.")
else:
    st.info("Website traffic is declining and may require marketing intervention.")

# -----------------------------
# SALES VISUALIZATION
# -----------------------------

st.subheader("Sales Overview")

sales_by_product = sales.groupby("Product")["Sales"].sum()

fig, ax = plt.subplots()

sales_by_product.plot(kind="bar", ax=ax)

ax.set_title("Total Sales by Product")

st.pyplot(fig)

# -----------------------------
# AI COPILOT SETUP
# -----------------------------

st.subheader("AI Data Copilot")

question = st.text_input("Ask business questions about your data")

# Combine datasets

data = sales.merge(share, on=["Product","Date"], how="left")

data = data.merge(returns, on=["Product","Date"], how="left")

# AI Model

llm = OpenAI(api_token="YOUR_OPENAI_API_KEY")

ai_df = SmartDataframe(data, config={"llm": llm})

# -----------------------------
# AI QUESTION ENGINE
# -----------------------------

if question:

    st.write("Generating AI insight...")

    try:

        result = ai_df.chat(question)

        st.write(result)

    except:

        st.error("AI could not understand the question. Try rephrasing.")

# -----------------------------
# FOOTER
# -----------------------------

st.write("---")

st.caption("Enterprise AI Analytics Platform | Powered by Rishikriti Technologies")
