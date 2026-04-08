import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import re

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
# PDF REPORT GENERATOR
# -----------------------------

def generate_pdf():

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter

    total_revenue = sales["Sales"].sum()
    top_product = sales.groupby("Product")["Sales"].sum().idxmax()

    return_summary = returns.groupby("Product")["Returns"].sum()
    high_returns = return_summary.idxmax()

    c.setFont("Helvetica-Bold",16)
    c.drawString(50,height-50,"Enterprise AI Executive Report")

    c.setFont("Helvetica",12)

    y = height - 120

    c.drawString(50,y,f"Total Revenue: {round(total_revenue,2)}")
    y -= 30

    c.drawString(50,y,f"Top Product: {top_product}")
    y -= 30

    c.drawString(50,y,f"Highest Returns Product: {high_returns}")
    y -= 40

    c.drawString(50,y,"Strategic Recommendations")
    y -= 30

    c.drawString(50,y,f"- Increase marketing focus on {top_product}")
    y -= 25

    c.drawString(50,y,f"- Investigate return causes for {high_returns}")
    y -= 25

    c.drawString(50,y,"- Monitor website engagement trends")

    c.save()
    buffer.seek(0)

    return buffer

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Dashboard","Dataset Explorer","Executive Insights"]
)

# -----------------------------
# DASHBOARD PAGE
# -----------------------------

if page == "Dashboard":

    col1,col2 = st.columns([2,1])

    # -----------------------------
    # DASHBOARD
    # -----------------------------

    with col1:

        st.subheader("Executive Dashboard")

        st.image("powerbi_dashboard.png",use_container_width=True)

        st.subheader("Key Business Metrics")

        k1,k2,k3,k4 = st.columns(4)

        total_revenue = sales["Sales"].sum()
        top_product = sales.groupby("Product")["Sales"].sum().idxmax()
        return_rate = (returns["Returns"].sum()/sales["Sales"].sum())*100
        traffic_growth = website["Visits"].iloc[-1] - website["Visits"].iloc[0]

        k1.metric("Total Revenue",round(total_revenue,2))
        k2.metric("Top Product",top_product)
        k3.metric("Return Rate",f"{round(return_rate,2)}%")
        k4.metric("Traffic Growth",traffic_growth)

    # -----------------------------
    # AI ASSISTANT
    # -----------------------------

    with col2:

        st.subheader("AI Assistant")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # DISPLAY CHAT HISTORY
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])

                if chat.get("chart") == "sales_trend":
                    product = chat["product"]
                    data = sales.copy()

                    if product:
                        data = data[data["Product"] == product]

                    fig,ax = plt.subplots()
                    data.groupby("Date")["Sales"].sum().plot(ax=ax)
                    ax.set_title(f"Sales Trend - {product if product else 'All Products'}")
                    st.pyplot(fig)

                elif chat.get("chart") == "returns":
                    data = returns.copy()

                    if chat.get("product"):
                        data = data[data["Product"] == chat["product"]]

                    result = data.groupby("Product")["Returns"].sum()

                    fig,ax = plt.subplots()
                    result.plot(kind="bar",ax=ax)
                    ax.set_title("Returns by Product")
                    st.pyplot(fig)

                elif chat.get("chart") == "traffic":
                    trend = website.groupby("Date")["Visits"].sum()
                    fig,ax = plt.subplots()
                    trend.plot(ax=ax)
                    ax.set_title("Website Traffic Trend")
                    st.pyplot(fig)

        question = st.chat_input("Ask a business question")

        if question:

            st.session_state.chat_history.append(
                {"role":"user","content":question}
            )

            q = question.lower()

            # -----------------------------
            # 🔥 ENTITY EXTRACTION
            # -----------------------------

            # Detect year
            year_match = re.search(r"\b(20\d{2})\b", q)
            detected_year = int(year_match.group()) if year_match else None

            # Detect product
            detected_product = None
            products = sales["Product"].unique()

            for p in products:
                if str(p).lower() in q:
                    detected_product = p

            response = {"role":"assistant"}

            # -----------------------------
            # 🔥 SALES LOGIC (DYNAMIC)
            # -----------------------------

            if "sales" in q or "revenue" in q:

                data = sales.copy()

                if detected_product:
                    data = data[data["Product"] == detected_product]

                if detected_year:
                    data = data[data["Year"] == detected_year]

                total_sales = data["Sales"].sum()

                if detected_product and detected_year:
                    msg = f"Total sales for {detected_product} in {detected_year}: {round(total_sales,2)}"
                elif detected_product:
                    msg = f"Total sales for {detected_product}: {round(total_sales,2)}"
                elif detected_year:
                    msg = f"Total sales in {detected_year}: {round(total_sales,2)}"
                else:
                    msg = f"Total sales: {round(total_sales,2)}"

                if total_sales == 0:
                    msg += "\n⚠️ No data found for given filters."

                response["content"] = msg
                response["chart"] = "sales_trend"
                response["product"] = detected_product

            # -----------------------------
            # 🔥 RETURNS LOGIC (DYNAMIC)
            # -----------------------------

            elif "return" in q:

                data = returns.copy()

                if detected_product:
                    data = data[data["Product"] == detected_product]

                total_returns = data["Returns"].sum()

                if detected_product:
                    msg = f"Total returns for {detected_product}: {total_returns}"
                else:
                    msg = f"Total returns: {total_returns}"

                response["content"] = msg
                response["chart"] = "returns"
                response["product"] = detected_product

            # -----------------------------
            # TRAFFIC
            # -----------------------------

            elif "traffic" in q or "visit" in q:
                response["content"] = "Here is the website traffic trend."
                response["chart"] = "traffic"

            else:
                response["content"] = "I could not understand the question. Try asking about sales, returns, or traffic."

            st.session_state.chat_history.append(response)
            st.rerun()

        st.write("### Suggested Questions")

        st.markdown("""
        • What is total sales in 2019  
        • Total sales for board games  
        • Total sales for board games in 2019  
        • Total returns for board games  
        • Show website traffic  
        """)

# -----------------------------
# DATASET EXPLORER
# -----------------------------

elif page == "Dataset Explorer":

    st.subheader("Dataset Explorer")

    dataset_choice = st.selectbox(
        "Select dataset",
        ["Sales","Returns","Product Share","Website Traffic"]
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
# EXECUTIVE INSIGHTS
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

    traffic_trend = "increasing" if last_visit>first_visit else "declining"

    st.success(f"Top Revenue Driver: **{top_product}** generates the highest sales ({top_sales}).")
    st.warning(f"Product Risk: **{high_returns}** has the highest return volume.")
    st.info(f"Website traffic is **{traffic_trend}**, indicating changing customer demand.")

    st.write("### Strategic Recommendations")
    st.write(f"• Focus marketing investment on **{top_product}**")
    st.write(f"• Investigate return causes for **{high_returns}**")
    st.write("• Monitor website engagement trends")

    pdf = generate_pdf()

    st.download_button(
        label="Download AI Executive Report (PDF)",
        data=pdf,
        file_name="AI_Executive_Report.pdf",
        mime="application/pdf"
    )
