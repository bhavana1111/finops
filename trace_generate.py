from dotenv import load_dotenv
import os

load_dotenv()

os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
os.environ["LANGFUSE_BASE_URL"] = os.getenv("LANGFUSE_BASE_URL")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from langfuse.openai import openai
from langfuse import get_client

client = openai.OpenAI()

response = client.responses.create(
    model="gpt-4o",
    input="What is AI FinOps?"
)

print(response.output_text)

langfuse = get_client()
langfuse.flush()