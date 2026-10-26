"""Offline tests must not send traces or write runtime metrics."""
import os
os.environ['LANGSMITH_TRACING']='false'
os.environ['LANGCHAIN_TRACING_V2']='false'
os.environ['SAHAYAK_METRICS']='false'
