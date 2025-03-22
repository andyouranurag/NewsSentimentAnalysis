import os
import requests

# ✅ Automatically detect API URL for Hugging Face Spaces
BASE_URL = os.getenv("API_URL", "http://0.0.0.0:8000")

# API Endpoints
NEWS_API = f"{BASE_URL}/scrape_news/"
TTS_API = f"{BASE_URL}/generate_tts/"

# Function to fetch news
def fetch_news(company):
    try:
        response = requests.post(NEWS_API, json={"company": company}, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"News API request failed: {e}"}

# Function to generate TTS
def generate_tts(company):
    try:
        response = requests.post(TTS_API, json={"company": company}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"TTS API request failed: {e}"}

