import streamlit as st
from api import fetch_news, generate_tts

def main():
    st.title("📢 Hindi News & Sentiment Analysis")
    company = st.text_input("🔍 Enter Company Name")

    if st.button("Analyze News"):
        data = fetch_news(company)

        if "error" in data:
            st.error(data["error"])
        else:
            # Show News Articles
            st.subheader(f"📢 {company} - Top News Headlines")
            for article in data["articles"]:
                st.markdown(f"### 🔹 {article['title']}")
                st.write(f"📌 **Summary:** {article['summary']}")
                st.write(f"📌 **Topics:** {', '.join(article['topics'])}")
                st.write(f"📌 **Sentiment:** {article['sentiment']}")
                st.markdown(f"[Read More]({article['link']})")

            # Show Overall Sentiment Analysis
            analysis = data["analysis"]
            st.subheader(f"📊 Overall Sentiment Analysis for {company}")
            st.write(f"📌 **Total Articles Analyzed:** {analysis['total_articles']}")
            st.write(f"📌 **Sentiment Breakdown:**")
            st.write(f"➡️ **Positive:** {analysis['sentiment_counts']['Positive']}")
            st.write(f"➡️ **Negative:** {analysis['sentiment_counts']['Negative']}")
            st.write(f"➡️ **Neutral:** {analysis['sentiment_counts']['Neutral']}")

            # Comparative Analysis
            st.subheader(f"🔍 Comparative News Coverage for {company}")
            st.write("📌 **Key Topics Covered Across Reports:**")
            st.markdown("🔹 " + " 🔹 ".join(analysis["unique_topics"]))

            # ✅ Generate and Play TTS
            st.subheader("🎙️ Listen to Hindi Audio Summary")
            tts_response = generate_tts(company)

            if "file" in tts_response:
                st.audio(tts_response["file"])
            else:
                st.error("🔴 TTS generation failed. Please try again.")

if __name__ == "__main__":
    main()
