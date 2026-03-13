import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------
# PAGE CONFIG
# ------------------------------

st.set_page_config(page_title="AI Business Copilot", layout="wide")

st.title("AI Data Copilot")
st.write("Ask business questions about your data and get insights automatically.")

# ------------------------------
# LOAD DATA
# ------------------------------

sales = pd.read_csv("sales_data.csv")
share = pd.read_csv("product_Share.csv")
returns = pd.read_csv("returns_Data.csv")
website = pd.read_csv("website_Data.csv")

# ------------------------------
# DATA PREVIEW
# ------------------------------

st.subheader("Dataset Preview")

preview = sales.copy()
preview["SalesSharePercent"] = share["SalesSharePercent"]
preview["Cancellations"] = returns["Cancellations"]
preview["Returns"] = returns["Returns"]

st.dataframe(preview.head())

# ------------------------------
# USER QUESTION
# ------------------------------

question = st.text_input("Ask any question about your data")

# ------------------------------
# AI ANALYSIS ENGINE
# ------------------------------

if question:

    question = question.lower()

    st.write("### AI Analysis")

    # --------------------------------
    # SALES BY PRODUCT
    # --------------------------------

    if "sales" in question and "product" in question:

        result = sales.groupby("Product")["Sales"].sum()

        st.subheader("Sales by Product")

        fig, ax = plt.subplots()
        result.plot(kind="bar", ax=ax)
        ax.set_ylabel("Sales")

        st.pyplot(fig)

        top_product = result.idxmax()

        st.success(f"Insight: {top_product} generates the highest sales.")

        st.info("Recommendation: Increase marketing investment for this category.")

    # --------------------------------
    # SALES TREND
    # --------------------------------

    elif "trend" in question or "growth" in question:

        trend = sales.groupby("Date")["Sales"].sum()

        st.subheader("Sales Trend")

        fig, ax = plt.subplots()
        trend.plot(ax=ax)

        st.pyplot(fig)

        change = trend.iloc[-1] - trend.iloc[0]

        if change > 0:
            st.success("Insight: Sales are showing an upward trend.")
        else:
            st.warning("Insight: Sales are declining.")

    # --------------------------------
    # RETURNS ANALYSIS
    # --------------------------------

    elif "return" in question:

        result = returns.groupby("Product")["Returns"].sum()

        st.subheader("Returns by Product")

        fig, ax = plt.subplots()
        result.plot(kind="bar", ax=ax)

        st.pyplot(fig)

        worst = result.idxmax()

        st.warning(f"Insight: {worst} has the highest returns.")

        st.info("Recommendation: Review product quality or logistics.")

    # --------------------------------
    # CANCELLATIONS
    # --------------------------------

    elif "cancel" in question:

        result = returns.groupby("Product")["Cancellations"].sum()

        st.subheader("Cancellations by Product")

        fig, ax = plt.subplots()
        result.plot(kind="bar", ax=ax)

        st.pyplot(fig)

        worst = result.idxmax()

        st.warning(f"{worst} has the highest cancellations.")

    # --------------------------------
    # WEBSITE VISITS
    # --------------------------------

    elif "visit" in question or "traffic" in question:

        traffic = website.groupby("Date")["Visits"].sum()

        st.subheader("Website Visits Trend")

        fig, ax = plt.subplots()
        traffic.plot(ax=ax)

        st.pyplot(fig)

        st.success("Insight: Website traffic influences sales performance.")

    # --------------------------------
    # PRODUCT SHARE
    # --------------------------------

    elif "share" in question:

        result = share.groupby("Product")["SalesSharePercent"].mean()

        st.subheader("Market Share by Product")

        fig, ax = plt.subplots()
        result.plot(kind="pie", autopct="%1.1f%%", ax=ax)

        st.pyplot(fig)

        leader = result.idxmax()

        st.success(f"{leader} dominates the product portfolio.")

    # --------------------------------
    # DEFAULT RESPONSE
    # --------------------------------

    else:

        st.warning("AI could not understand the question.")

        st.write("Try asking:")

        st.write("- Which product has highest sales?")
        st.write("- Show sales trend")
        st.write("- Which product has most returns?")
        st.write("- Show website traffic trend")

# ------------------------------
# FOOTER
# ------------------------------

st.write("---")
st.caption("AI Business Copilot for Data Analytics")


