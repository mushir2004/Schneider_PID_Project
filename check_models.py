import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Fallback if .env fails
if not api_key:
    # TODO: PASTE YOUR KEY HERE IF NEEDED
    api_key = "AIzaSy..." 

genai.configure(api_key=api_key)

print("Checking available models for your API key...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")