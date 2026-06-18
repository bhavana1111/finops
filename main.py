from dotenv import load_dotenv
import os
import requests
import pandas as pd

load_dotenv()

LANGFUSE_HOST = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

response = requests.get(
f"{LANGFUSE_HOST}/api/public/traces",
auth=(PUBLIC_KEY, SECRET_KEY),
params={"limit": 100}
)

response.raise_for_status()

traces = response.json().get("data", [])

if not traces:
    print("No traces found.")
    exit()

rows = []

for trace in traces:
    rows.append({
"trace_id": trace.get("id"),
"name": trace.get("name"),
"timestamp": trace.get("timestamp"),
"environment": trace.get("environment"),
"cost": float(trace.get("totalCost") or 0),
"latency": trace.get("latency") or 0
})

df = pd.DataFrame(rows)

print("\n=== AI COST REPORT ===\n")

print("Total Requests:", len(df))
print("Total Cost: $", round(df["cost"].sum(), 6))
print("Average Cost per Request: $", round(df["cost"].mean(), 6))
print("Average Latency:", round(df["latency"].mean(), 2), "seconds")

print("\n=== COST BY ENVIRONMENT ===\n")

print(
df.groupby("environment")["cost"]
.sum()
.sort_values(ascending=False)
)

print("\n=== MOST EXPENSIVE TRACES ===\n")

print(
df[["name", "cost", "latency"]]
.sort_values("cost", ascending=False)
.head(10)
)
