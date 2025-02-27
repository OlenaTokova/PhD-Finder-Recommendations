import requests

def fetch_github_topics(query):
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars"
    headers = {"Authorization": "YOUR GITHUB API"}  # Replace with your GitHub token
    response = requests.get(url, headers=headers)
    
    # Check for a successful response
    if response.status_code == 200:
        data = response.json()
        topics = []
        for repo in data.get("items", [])[:5]:  # Safely handle missing "items" key
            topics.append({
                "name": repo.get("name", "Unknown name"),
                "description": repo.get("description", "No description available"),
                "url": repo.get("html_url", "No URL available"),
                "stars": repo.get("stargazers_count", 0)
            })
        return topics
    else:
        print(f"Error fetching data from GitHub: {response.status_code}")
        return []
