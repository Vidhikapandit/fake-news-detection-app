import streamlit as st
import joblib
import re
import string
import requests
from newspaper import Article

# 1. Load the saved model and vectorizer
vectorizer = joblib.load("vectorizer.pkl")
model = joblib.load("model.pkl")

# 2. Text cleaning function (same as your Jupyter notebook)
def wordopt(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\\W', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

# 3. Scrape article from URL
def fetch_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://google.com'
    }
    response = requests.get(url, headers=headers, timeout=10)
    article = Article(url)
    article.set_html(response.text)
    article.parse()
    return article.title, article.text

# 4. Build the Website UI
st.set_page_config(page_title="Fake News Detector", page_icon="📰")
st.title("📰 Fake News Detection System")
st.write("Paste a news article URL or raw news text below to verify its authenticity.")

input_type = st.radio("Choose input method:", ("News Article URL", "Paste News Text"))

if input_type == "News Article URL":
    url = st.text_input("Enter the news URL:")
    if st.button("Analyze URL"):
        if url.strip():
            with st.spinner("Fetching and analyzing article..."):
                try:
                    title, text = fetch_article(url)
                    if not text.strip():
                        st.warning("Could not extract article text. The site may be blocking scrapers.")
                    else:
                        st.subheader(title)
                        st.caption(text[:300] + "...")
                        cleaned = wordopt(text)
                        vec = vectorizer.transform([cleaned])
                        prediction = model.predict(vec)[0]
                        if prediction == 0:
                            st.error("🚨 Prediction: Fake News")
                        else:
                            st.success("✅ Prediction: Not A Fake News (Genuine)")
                except Exception as e:
                    st.error(f"Error fetching URL: {e}")
        else:
            st.warning("Please enter a valid URL.")

else:
    raw_text = st.text_area("Paste the full news article text here:", height=200)
    if st.button("Analyze Text"):
        if raw_text.strip():
            cleaned = wordopt(raw_text)
            vec = vectorizer.transform([cleaned])
            prediction = model.predict(vec)[0]
            if prediction == 0:
                st.error("🚨 Prediction: Fake News")
            else:
                st.success("✅ Prediction: Not A Fake News (Genuine)")
        else:
            st.warning("Please paste some text first.")