import requests

# Define API Base URL
BASE_URL = "http://127.0.0.1:8000"

# API Endpoints
NEWS_API = f"{BASE_URL}/scrape_news/"
TTS_API = f"{BASE_URL}/generate_tts/"

# Function to fetch news from backend
def fetch_news(company):
    """
    Calls the backend API to fetch news articles and sentiment analysis.

    :param company: The company name to search for news.
    :return: JSON response containing news articles and analysis.
    """
    try:
        response = requests.post(NEWS_API, json={"company": company}, timeout=15)
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"News API request failed: {e}"}

# Function to generate TTS from backend API
def generate_tts(company):
    """
    Calls the backend API to generate text-to-speech for news summary.

    :param company: The company name for news summary.
    :return: JSON response with TTS file info.
    """
    try:
        response = requests.post(TTS_API, json={"company": company}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"TTS API request failed: {e}"}
