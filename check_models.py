
import os
from google import genai
import streamlit as st

try:
    # Try to get key from secrets.toml manually if not in env
    # Since we can't easily read secrets.toml with st.secrets outside of streamlit app context widely
    # I'll rely on the user having set it or I'll try to read the file manually for this script
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    api_key = secrets["GEMINI_API_KEY"]
except Exception as e:
    print(f"Could not load key from secrets: {e}")
    api_key = input("Please enter API Key: ")

client = genai.Client(api_key=api_key)

print("Listing models...")
try:
    # The SDK method might vary, usually it's client.models.list() or similar
    # Based on the error message implying 'Call ListModels'
    for m in client.models.list():
        print(f"Model: {m.name}")
        # print(f"Supported methods: {m.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"Error listing models: {e}")
