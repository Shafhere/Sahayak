import os
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

print("API Key found:", os.getenv("LANGCHAIN_API_KEY")[:10] + "..." if os.getenv("LANGCHAIN_API_KEY") else "MISSING")
print("Tracing enabled:", os.getenv("LANGCHAIN_TRACING_V2"))

@traceable(name="LangSmith Test Node")
def my_test_function(text):
    return {"result": f"Processed: {text}"}

print("Running function...")
result = my_test_function("Hello World")
print("Done:", result)