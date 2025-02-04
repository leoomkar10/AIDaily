import os
from dotenv import load_dotenv
import tweepy
import feedparser
import schedule
import time
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Securely load credentials from environment
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET_KEY = os.getenv('TWITTER_API_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
RSS_FEED_URL = os.getenv('AI_NEWS_RSS_FEED', "https://rss.app/feeds/tQ4nAMOlfNpguifn.xml")

def validate_credentials():
    """Validate that all required credentials are present."""
    required_keys = [API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]
    if not all(required_keys):
        raise ValueError("Missing Twitter API credentials. Check your .env file.")

def get_twitter_client():
    """Create and return Twitter client with error handling."""
    try:
        return tweepy.Client(
            consumer_key=API_KEY, 
            consumer_secret=API_SECRET_KEY,
            access_token=ACCESS_TOKEN, 
            access_token_secret=ACCESS_TOKEN_SECRET
        )
    except Exception as e:
        logging.error(f"Twitter client initialization failed: {e}")
        return None

def get_ai_news(max_entries=2):
    """Fetch AI-related news from RSS feed with robust error handling."""
    try:
        feed = feedparser.parse(RSS_FEED_URL)
        entries = feed.entries[:max_entries]
        return [entry.title for entry in entries if entry.title]
    except Exception as e:
        logging.error(f"RSS feed fetch error: {e}")
        return []

def tweet_ai_news(client):
    """Tweet AI news with length and error management."""
    if not client:
        logging.warning("No Twitter client available. Skipping tweet.")
        return

    news = get_ai_news()
    if not news:
        logging.info("No news available to tweet.")
        return
    
    tweet_text = "🤖 Top AI News Today:\n\n" + "\n".join([f"• {headline}" for headline in news])
    
    # Truncate tweet if too long
    tweet_text = tweet_text[:280] if len(tweet_text) > 280 else tweet_text
    
    try:
        client.create_tweet(text=tweet_text)
        logging.info(f"Successfully tweeted: {tweet_text}")
    except tweepy.TweepyException as e:
        logging.error(f"Tweet failed: {e}")

def main():
    """Main execution function with error handling."""
    try:
        validate_credentials()
        twitter_client = get_twitter_client()
        
        # Schedule daily tweet
        schedule.every().day.at("18:36").do(tweet_ai_news, twitter_client)
        
        logging.info("AI News Twitter Bot started successfully.")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    except Exception as e:
        logging.critical(f"Bot initialization failed: {e}")

if __name__ == "__main__":
    main()