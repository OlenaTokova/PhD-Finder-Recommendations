import feedparser
import urllib.parse

def fetch_arxiv_topics(query="machine learning"):
    # Encode the query to handle spaces and special characters
    encoded_query = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results=5"
    feed = feedparser.parse(url)
    topics = []
    for entry in feed.entries:
        topics.append({
            "title": entry.title,
            "summary": entry.summary,
            "authors": [author.name for author in entry.authors],
            "published": entry.published
        })
    return topics
