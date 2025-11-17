# collect_twitter.py
import os
import re
import tweepy
import csv
import json
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

TWITTER_BEARER = os.getenv("TWITTER_BEARER_TOKEN")

# --- CONFIG ---
KEYWORDS = ["love", "news", "hate"]  # Change these to whatever you want
RESULTS_CSV = "results.csv"
RESULTS_JSON = "results.jsonl"
MAX_RESULTS = 50  # Twitter free tier allows max 100 per request
# ---------------

def connect_twitter():
    if not TWITTER_BEARER:
        raise ValueError("Twitter bearer token not set in .env")
    return tweepy.Client(bearer_token=TWITTER_BEARER, wait_on_rate_limit=True)

def search_twitter(client, keywords):
    print(f"🔎 Searching Twitter for: {keywords}")
    query = " OR ".join(keywords)

    matches = []
    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=MAX_RESULTS,
            tweet_fields=["author_id", "created_at", "lang", "text"]
        )
        if response.data:
            for i, tweet in enumerate(response.data, start=1):
                text = tweet.text
                for kw in keywords:
                    if re.search(kw, text, re.IGNORECASE):
                        print(f" ✅ Match {i}: {text[:60]}...")
                        matches.append({
                            "id": tweet.id,
                            "author_id": tweet.author_id,
                            "created_at": str(tweet.created_at),
                            "text": text,
                            "keyword": kw,
                            "source": "twitter"
                        })
                        break
        else:
            print("⚠️ No tweets found for these keywords.")
    except Exception as e:
        print("❌ Twitter API error:", e)

    return matches

def save_results(results):
    if not results:
        print("⚠️ No results to save.")
        return

    # Save CSV
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"📁 Wrote {len(results)} rows to {RESULTS_CSV}")

    # Save JSONL
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"📁 Wrote {len(results)} rows to {RESULTS_JSON}")

def main():
    client = connect_twitter()
    results = search_twitter(client, KEYWORDS)
    save_results(results)
    print("🎉 Done.")

if __name__ == "__main__":
    main()
