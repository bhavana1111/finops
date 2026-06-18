from dotenv import load_dotenv
import os
import requests
import pandas as pd

load_dotenv()

LANGFUSE_HOST = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

response = requests.get(
f"{LANGFUSE_HOST}/api/public/observations",
auth=(PUBLIC_KEY, SECRET_KEY),
params={"limit": 100}
)

response.raise_for_status()

observations = response.json().get("data", [])

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
    "latency": obs.get("latency") or 0
})
    

df = pd.DataFrame(rows)

print("\n==============================")
print("AI FINOPS REPORT")
print("==============================\n")

print("Total Requests:", len(df))
print("Total Input Tokens:", df["input_tokens"].sum())
print("Total Output Tokens:", df["output_tokens"].sum())
print("Total Tokens:", df["total_tokens"].sum())
print("Total Cost: $", round(df["cost"].sum(), 6))

print("\n=== COST BY MODEL ===\n")

print(
df.groupby("model")["cost"]
.sum()
.sort_values(ascending=False)
)

print("\n=== TOKENS BY MODEL ===\n")

print(
df.groupby("model")["total_tokens"]
.sum()
.sort_values(ascending=False)
)

print("\n=== COST BY ENVIRONMENT ===\n")

print(
df.groupby("environment")["cost"]
.sum()
.sort_values(ascending=False)
)

print("\n=== COST BY APPLICATION ===\n")

print(
df.groupby("application")["cost"]
.sum()
.sort_values(ascending=False)
)

print("\n=== TOP EXPENSIVE REQUESTS ===\n")

print(
df[[
"model",
"cost",
"input_tokens",
"output_tokens"
]]
.sort_values("cost", ascending=False)
.head(10)
)
