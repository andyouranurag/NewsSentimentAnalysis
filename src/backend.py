from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from gtts import gTTS
from googletrans import Translator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ✅ Set a writable directory for NLTK inside the app folder
NLTK_DIR = "/app/nltk_data"
os.makedirs(NLTK_DIR, exist_ok=True)

# ✅ Tell NLTK to use the new directory
nltk.data.path.append(NLTK_DIR)

# ✅ Download NLTK data to the correct location
nltk.download('punkt', download_dir=NLTK_DIR)


# Initialize FastAPI app
app = FastAPI()

# Initialize sentiment analyzer and translator
analyzer = SentimentIntensityAnalyzer()
translator = Translator()

# Define input model
class NewsRequest(BaseModel):
    company: str

# Web Scraping Function
def scrape_news(company):
    search_url = f"https://www.bing.com/news/search?q={company}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"🔴 ERROR: Failed to fetch news - {e}")
        return {"error": f"Request failed: {e}"}

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for item in soup.select("div.news-card")[:10]:  # Limit to 10 articles
        try:
            title_tag = item.select_one("a.title")
            summary_tag = item.select_one("div.snippet")

            title = title_tag.text.strip() if title_tag else "No title"
            summary = summary_tag.text.strip() if summary_tag else "No summary"
            link = title_tag["href"] if title_tag else "#"

            # Extract topics from title
            topics = [word.strip(",.?!") for word in title.split() if word.istitle()]

            articles.append({
                "title": title,
                "summary": summary,
                "topics": topics,
                "link": link
            })
        except Exception as e:
            print(f"🔴 ERROR: Failed to parse an article - {e}")

    if not articles:
        print("⚠️ No articles found.")
        return {"error": "No articles found"}

    return articles


# Sentiment Analysis Function
def analyze_sentiment(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"



# ✅ Use `/tmp/` instead of `/app/tmp/` to avoid permission issues
SAVE_DIR = "/tmp/"
os.makedirs(SAVE_DIR, exist_ok=True)  # ✅ No permission error here

def comparative_analysis(articles):
    if not articles:
        return {"error": "No articles found"}

    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    sentiment_list = []
    topics_covered = []

    for article in articles:
        sentiment = analyze_sentiment(article["summary"])
        sentiment_counts[sentiment] += 1
        sentiment_list.append(sentiment)
        topics_covered.extend(article["topics"])

    unique_topics = list(set(topics_covered))

    return {
        "total_articles": len(articles),
        "sentiment_counts": sentiment_counts,
        "unique_topics": unique_topics
    }


# API Endpoint for News Scraping & Comparative Analysis
@app.post("/scrape_news/")
@app.post("/scrape_news/")
def fetch_news(news_request: NewsRequest):
    try:
        articles = scrape_news(news_request.company)
        if "error" in articles:
            return articles

        # Analyze sentiment for each article
        for article in articles:
            article["sentiment"] = analyze_sentiment(article["summary"])

        # Get comparative analysis
        analysis = comparative_analysis(articles)

        return {
            "company": news_request.company,
            "analysis": analysis,
            "articles": articles
        }
    except Exception as e:
        print(f"🔴 ERROR: {e}")
        return {"error": f"Internal Server Error: {e}"}


# ✅ Fix: Translate News to Hindi Before TTS & Reduce Processing Time
@app.post("/generate_tts/")
def generate_tts(news_request: NewsRequest):
    articles = scrape_news(news_request.company)
    if "error" in articles:
        return articles

    analysis = comparative_analysis(articles)

    # ✅ Create structured summary before TTS
    english_text = f"Comparative News Analysis for {news_request.company}:\n"
    english_text += f"Total articles analyzed: {analysis['total_articles']}.\n"
    english_text += f"Sentiment breakdown - Positive: {analysis['sentiment_counts']['Positive']}, "
    english_text += f"Negative: {analysis['sentiment_counts']['Negative']}, "
    english_text += f"Neutral: {analysis['sentiment_counts']['Neutral']}.\n"
    english_text += "Key topics covered: " + ", ".join(analysis["unique_topics"]) + ".\n\n"

    for i, article in enumerate(articles[:3], 1):  # Limit to 3 articles
        english_text += f"{i}. {article['title']} - {article['summary']}.\n\n"

    print(f"✅ English Text for TTS:\n{english_text}")  # ✅ Debug log

    try:
        # ✅ Translate to Hindi
        translated_text = translator.translate(english_text, src="en", dest="hi").text
        print(f"✅ Translated Text for TTS:\n{translated_text}")  # ✅ Debug log

    except Exception as e:
        print(f"🔴 ERROR: Translation failed - {e}")
        return {"error": f"Translation failed: {e}"}

    try:
        # ✅ Generate TTS in Hindi
        tts = gTTS(text=translated_text, lang="hi")
        tts_path = "/tmp/output.mp3"  # ✅ Use /tmp/ for saving
        tts.save(tts_path)
        print(f"✅ TTS saved at {tts_path}")  # ✅ Debug log

    except Exception as e:
        print(f"🔴 ERROR: TTS generation failed - {e}")
        return {"error": f"TTS generation failed: {e}"}

    return {"message": "TTS generated successfully!", "file": tts_path}

# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True, timeout_keep_alive=60)
