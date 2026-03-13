import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from openai import OpenAI

st.title("AI Data Assistant")

# Load datasets
sales = pd.read_csv("sales_data.csv")
share = pd.read_csv("product_share.csv")
returns = pd.read_csv("returns_data.csv")
traffic = pd.read_csv("website_data.csv")

# Merge analytical dataset
data = sales.merge(share, on="Product", how="left")
data = data.merge(returns, on="Product", how="left")

traffic["Date"] = pd.to_datetime(traffic["Date"])

st.subheader("Dataset Preview")
st.dataframe(data.head())

# OpenAI client
client = OpenAI(api_key="YOUR_API_KEY")

question = st.text_input("Ask any question about your data")

if question:

    q = question.lower()

    # Chart generation
    if "sales by product" in q:
        chart = data.groupby("Product")["Sales"].sum()
        st.bar_chart(chart)

    elif "returns vs cancellations" in q:
        df = returns.set_index("Product")[["Returns","Cancellations"]]
        st.bar_chart(df)

    elif "revenue trend" in q:
        st.line_chart(traffic.set_index("Date")["Revenue"])

    # Forecasting
    elif "forecast revenue" in q:

        df = traffic.rename(columns={"Date":"ds","Revenue":"y"})

        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=6, freq="M")
        forecast = model.predict(future)

        st.line_chart(forecast.set_index("ds")["yhat"])

    else:

        prompt = f"""
        You are a senior business analyst.

        Dataset columns:
        {list(data.columns)}

        Sample data:
        {data.head(10)}

        Question:
        {question}

        Provide:
        1. Answer
        2. Key Insight
        3. Business Recommendation
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"You are an expert business data analyst"},
                    {"role":"user","content":prompt}
                ]
            )

            insight = response.choices[0].message.content

            st.write("### AI Insight")
            st.write(insight)

        except Exception as e:
            st.error("AI service unavailable. Please check API key or quota.")