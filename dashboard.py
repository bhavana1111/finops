from dotenv import load_dotenv
import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px

load_dotenv()

LANGFUSE_HOST = os.getenv("LANGFUSE_BASE_URL")
PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

st.set_page_config(
page_title="AI FinOps Dashboard",
layout="wide"
)

st.title("💰 AI FinOps Dashboard")

response = requests.get(
f"{LANGFUSE_HOST}/api/public/observations",
auth=(PUBLIC_KEY, SECRET_KEY),
params={"limit": 5}
)

response.raise_for_status()

observations = response.json()["data"]

rows = []

for obs in observations:
    rows.append({
    "model": obs.get("model"),
    "environment": (
        obs.get("metadata", {}).get("environment")
        or obs.get("environment")
        or "unknown"
    ),
    "application": (
        obs.get("metadata", {}).get("application")
        or "unknown"
    ),
    "input_tokens": obs.get("promptTokens", 0),
    "output_tokens": obs.get("completionTokens", 0),
    "total_tokens": obs.get("totalTokens", 0),
    "cost": float(obs.get("calculatedTotalCost") or 0),
    "latency": obs.get("latency") or 0,
    "timestamp": obs.get("createdAt")
})


df = pd.DataFrame(rows)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Requests", len(df))
col2.metric("Total Cost", f"${df['cost'].sum():.4f}")
col3.metric("Input Tokens", f"{df['input_tokens'].sum():,}")
col4.metric("Output Tokens", f"{df['output_tokens'].sum():,}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Cost by Model")

cost_model = (
    df.groupby("model")["cost"]
    .sum()
    .reset_index()
)

fig = px.bar(
    cost_model,
    x="model",
    y="cost"
)

st.plotly_chart(fig, use_container_width=True)


with right:
    st.subheader("Cost by Environment")

env_cost = (
    df.groupby("environment")["cost"]
    .sum()
    .reset_index()
)

fig = px.pie(
    env_cost,
    names="environment",
    values="cost"
)

st.plotly_chart(fig, use_container_width=True)


st.divider()

st.subheader("Cost by Application")

app_cost = (
df.groupby("application")["cost"]
.sum()
.reset_index()
)

fig = px.bar(
app_cost,
x="application",
y="cost"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Raw Usage Data")

st.dataframe(df, use_container_width=True)
