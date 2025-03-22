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

# Download required NLTK data
nltk.download('punkt')

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
        return {"error": f"Request failed: {e}"}

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for item in soup.select("div.news-card")[:10]:  # Limit to 10 articles
        title_tag = item.select_one("a.title")
        summary_tag = item.select_one("div.snippet")

        title = title_tag.text.strip() if title_tag else "No title"
        summary = summary_tag.text.strip() if summary_tag else "No summary"
        link = title_tag["href"] if title_tag else "#"

        # Extract topics from title
        topics = [word.strip(",.?!") for word in title.split() if word.istitle()]  # Filters capitalized words as topics

        articles.append({
            "title": title,
            "summary": summary,
            "topics": topics,
            "link": link
        })

    return articles if articles else {"error": "No articles found"}

# Sentiment Analysis Function
def analyze_sentiment(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"

# Comparative Analysis Function
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

    # Get unique topics
    unique_topics = list(set(topics_covered))

    # Create a DataFrame for sentiment visualization
    df = pd.DataFrame({"Sentiment": sentiment_list})

    # Generate sentiment distribution plot
    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x="Sentiment", palette="coolwarm")
    plt.title("Overall Sentiment Distribution")
    plt.savefig("sentiment_distribution.png")

    return {
        "total_articles": len(articles),
        "sentiment_counts": sentiment_counts,
        "unique_topics": unique_topics,
        "sentiment_chart": "sentiment_distribution.png"
    }

# API Endpoint for News Scraping & Comparative Analysis
@app.post("/scrape_news/")
def fetch_news(news_request: NewsRequest):
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

# ✅ Fix: Translate News to Hindi Before TTS & Reduce Processing Time
@app.post("/generate_tts/")
def generate_tts(news_request: NewsRequest):
    articles = scrape_news(news_request.company)

    if "error" in articles:
        return articles

    # Perform comparative analysis
    analysis = comparative_analysis(articles)

    # Create structured summary before TTS (Limited to 3 articles)
    english_text = f"Comparative News Analysis for {news_request.company}: \n"
    english_text += f"Total articles analyzed: {analysis['total_articles']}.\n"
    english_text += f"Sentiment breakdown - Positive: {analysis['sentiment_counts']['Positive']}, "
    english_text += f"Negative: {analysis['sentiment_counts']['Negative']}, "
    english_text += f"Neutral: {analysis['sentiment_counts']['Neutral']}.\n"
    english_text += "Key topics covered: " + ", ".join(analysis["unique_topics"]) + ".\n\n"

    for i, article in enumerate(articles[:3], 1):  # Limit to 3 articles
        english_text += f"{i}. {article['title']} - {article['summary']}.\n\n"

    # Translate text to Hindi
    translated_text = translator.translate(english_text, src="en", dest="hi").text

    # Generate Hindi TTS
    tts = gTTS(text=translated_text, lang="hi")
    tts.save("output.mp3")

    return {"message": "TTS generated successfully!", "file": "output.mp3"}

# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True, timeout_keep_alive=60)
