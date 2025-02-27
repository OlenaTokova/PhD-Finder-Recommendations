import requests

def fetch_semantic_scholar_topics(query, api_key, limit=5):
    """
    Fetches research papers from Semantic Scholar API based on a search query.
    :param query: String, the search term or topic to query.
    :param api_key: String, your Semantic Scholar API key.
    :param limit: Integer, the maximum number of results to return.
    :return: List of dictionaries containing paper details.
    """
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields=title,authors,year,url"
    headers = {"x-api-key": api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        topics = []
        for paper in data.get("data", []):
            topics.append({
                "title": paper.get("title", "No title available"),
                "authors": [author["name"] for author in paper.get("authors", [])],
                "year": paper.get("year", "Unknown year"),
                "url": paper.get("url", "No URL available")
            })
        return topics
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

# Example usage
if __name__ == "__main__":
    API_KEY = "YOUR_SEMANTIC_SCHOLAR_API_KEY"  # Replace with your API key
    topics = fetch_semantic_scholar_topics("machine learning healthcare", API_KEY)
    print("Semantic Scholar Topics:", topics)
