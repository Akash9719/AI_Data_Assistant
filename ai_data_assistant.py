import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(page_title="Enterprise AI Analytics Platform", layout="wide")

st.title("Enterprise AI Analytics Platform")
st.write("Power BI Dashboard + AI Copilot for Data Insights")

# ----------------------------
# POWER BI DASHBOARD
# ----------------------------

st.subheader("Executive Dashboard")

powerbi_url = "https://app.powerbi.com/view?r=YOUR_EMBED_LINK"

st.image("powerbi_dashboard.png")

# ----------------------------
# LOAD DATA
# ----------------------------

try:
    sales = pd.read_csv("sales_data.csv")
    share = pd.read_csv("product_share.csv")
    returns = pd.read_csv("returns_data.csv")
    website = pd.read_csv("website_data.csv")
except Exception as e:
    st.error("Dataset loading failed. Check file names in GitHub.")
    st.stop()

# ----------------------------
# DATA PREVIEW
# ----------------------------

st.subheader("Dataset Preview")

preview = sales.copy()

if "SalesSharePercent" in share.columns:
    preview["SalesSharePercent"] = share["SalesSharePercent"]

if "Cancellations" in returns.columns:
    preview["Cancellations"] = returns["Cancellations"]

if "Returns" in returns.columns:
    preview["Returns"] = returns["Returns"]

st.dataframe(preview.head())

# ----------------------------
# AI COPILOT
# ----------------------------

st.subheader("AI Data Copilot")

question = st.text_input("Ask business questions about your data")

# ----------------------------
# AI ANALYSIS ENGINE
# ----------------------------

if question:

    q = question.lower()

    st.subheader("AI Analysis")

    # Detect product names
    detected_product = None

    if "Product" in sales.columns:
        products = sales["Product"].unique()

        for p in products:
            if str(p).lower() in q:
                detected_product = p

    # ----------------------------
    # PRODUCT SALES
    # ----------------------------

    if detected_product and "sales" in q:

        data = sales[sales["Product"] == detected_product]

        total = data["Sales"].sum()

        st.success(f"Total sales of {detected_product}: {total}")

        fig, ax = plt.subplots()

        data.groupby("Date")["Sales"].sum().plot(ax=ax)

        ax.set_title(f"Sales Trend - {detected_product}")

        st.pyplot(fig)

        st.info(
            f"{detected_product} contributes significantly to revenue performance."
        )

    # ----------------------------
    # SALES BY PRODUCT
    # ----------------------------

    elif "sales" in q:

        result = sales.groupby("Product")["Sales"].sum()

        fig, ax = plt.subplots()

        result.plot(kind="bar", ax=ax)

        ax.set_title("Sales by Product")

        st.pyplot(fig)

        leader = result.idxmax()

        st.success(f"{leader} generates the highest revenue.")

    # ----------------------------
    # RETURNS ANALYSIS
    # ----------------------------

    elif "return" in q:

        if "Product" in returns.columns:

            result = returns.groupby("Product")["Returns"].sum()

            fig, ax = plt.subplots()

            result.plot(kind="bar", ax=ax)

            ax.set_title("Returns by Product")

            st.pyplot(fig)

            worst = result.idxmax()

            st.warning(f"{worst} has the highest return rate.")

    # ----------------------------
    # CANCELLATIONS
    # ----------------------------

    elif "cancel" in q:

        if "Product" in returns.columns:

            result = returns.groupby("Product")["Cancellations"].sum()

            fig, ax = plt.subplots()

            result.plot(kind="bar", ax=ax)

            ax.set_title("Cancellations by Product")

            st.pyplot(fig)

            worst = result.idxmax()

            st.warning(f"{worst} experiences the highest cancellations.")

    # ----------------------------
    # PRODUCT SHARE
    # ----------------------------

    elif "share" in q:

        result = share.groupby("Product")["SalesSharePercent"].mean()

        fig, ax = plt.subplots()

        result.plot(kind="pie", autopct="%1.1f%%", ax=ax)

        ax.set_title("Product Sales Share")

        st.pyplot(fig)

        leader = result.idxmax()

        st.success(f"{leader} dominates the portfolio.")

    # ----------------------------
    # WEBSITE TRAFFIC
    # ----------------------------

    elif "traffic" in q or "visit" in q:

        if "Visits" in website.columns:

            trend = website.groupby("Date")["Visits"].sum()

            fig, ax = plt.subplots()

            trend.plot(ax=ax)

            ax.set_title("Website Traffic Trend")

            st.pyplot(fig)

            st.success("Website traffic trend generated.")

    # ----------------------------
    # SALES TREND
    # ----------------------------

    elif "trend" in q or "growth" in q:

        trend = sales.groupby("Date")["Sales"].sum()

        fig, ax = plt.subplots()

        trend.plot(ax=ax)

        ax.set_title("Overall Sales Trend")

        st.pyplot(fig)

        if trend.iloc[-1] > trend.iloc[0]:
            st.success("Sales show positive growth over time.")
        else:
            st.warning("Sales appear to be declining.")

    # ----------------------------
    # DEFAULT ANALYSIS
    # ----------------------------

    else:

        st.info("AI generating overall business insight...")

        result = sales.groupby("Product")["Sales"].sum()

        fig, ax = plt.subplots()

        result.plot(kind="bar", ax=ax)

        ax.set_title("Overall Sales Overview")

        st.pyplot(fig)

        top = result.idxmax()

        st.success(
            f"Based on current data, {top} is the top performing product category."
        )

        st.write("Try asking:")
        st.write("• total sales of lego")
        st.write("• show sales trend")
        st.write("• product share analysis")
        st.write("• website traffic trend")

# ----------------------------
# FOOTER
# ----------------------------

st.write("---")
st.caption("Enterprise AI Analytics Platform | Powered by AI Copilot")

