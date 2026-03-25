import feedparser
import json
import time
from datetime import datetime
import os

# --- CONFIGURATION ---
# We use targeted Google News searches and Reddit RSS feeds for each category
FEEDS = {
    "top_stories": ["https://news.google.com/rss/search?q=gaming+industry+news+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "viral": [
        "https://news.google.com/rss/search?q=viral+gaming+tiktok+OR+trending+game+when:1d&hl=en-US&gl=US&ceid=US:en",
        "https://www.reddit.com/r/gaming/top/.rss?t=day"
    ],
    "updates": ["https://news.google.com/rss/search?q=patch+notes+OR+game+update+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "errors": [
        "https://news.google.com/rss/search?q=servers+down+OR+error+code+gaming+when:1d&hl=en-US&gl=US&ceid=US:en"
    ],
    "guides": ["https://news.google.com/rss/search?q=how+to+win+OR+best+loadout+OR+game+guide+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "assets": ["https://news.google.com/rss/search?q=new+skins+OR+game+weapons+leaked+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "browser": ["https://news.google.com/rss/search?q=unblocked+games+OR+io+games+OR+wordle+today+when:1d&hl=en-US&gl=US&ceid=US:en"],
    "streamers": [
        "https://news.google.com/rss/search?q=twitch+streamer+OR+youtube+gaming+when:1d&hl=en-US&gl=US&ceid=US:en",
        "https://www.reddit.com/r/LivestreamFail/new/.rss"
    ],
    "mobile": ["https://news.google.com/rss/search?q=mobile+gaming+OR+iOS+game+OR+android+game+when:1d&hl=en-US&gl=US&ceid=US:en"]
}

def fetch_feed_data(feed_urls, category_name):
    items = []
    for url in feed_urls:
        print(f"Scraping {category_name}: {url}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:15]: # Get top 15 from each feed to prevent bloat
            # Determine Source
            source_name = "Gaming News"
            if "reddit.com" in url:
                source_name = "Reddit"
            elif hasattr(entry, 'source') and hasattr(entry.source, 'title'):
                source_name = entry.source.title
            else:
                # Fallback: Google News often appends "- Source Name" to the title
                if " - " in entry.title:
                    source_name = entry.title.split(" - ")[-1]
                    entry.title = entry.title.rsplit(" - ", 1)[0] # Clean title

            # Parse Timestamp
            timestamp = int(time.time())
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                timestamp = int(time.mktime(entry.published_parsed))

            items.append({
                "title": entry.title,
                "link": entry.link,
                "source": source_name,
                "timestamp": timestamp
            })
            
    # Sort newest first and return top 20 per category
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items[:20]

def main():
    print("Starting Gaming News Aggregator...")
    
    output_data = {
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {}
    }
    
    # Scrape all specific categories
    all_news_pool = []
    for category, urls in FEEDS.items():
        category_items = fetch_feed_data(urls, category)
        output_data["data"][category] = category_items
        all_news_pool.extend(category_items)
        
    # Generate the 'all' category by combining everything and sorting
    all_news_pool.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Remove duplicates for 'all' feed based on link
    seen_links = set()
    unique_all = []
    for item in all_news_pool:
        if item["link"] not in seen_links:
            seen_links.add(item["link"])
            unique_all.append(item)
            
    output_data["data"]["all"] = unique_all[:50] # Keep top 50 overall

    # Save to JSON
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print("Successfully generated news.json!")

if __name__ == "__main__":
    main()
