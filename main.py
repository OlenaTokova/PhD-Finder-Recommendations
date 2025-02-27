# main.py

from models.google_scholar_scraper import fetch_semantic_scholar_topics  # Оновлений імпорт
from models.arxiv_api import fetch_arxiv_topics
from models.kaggle_api import fetch_kaggle_datasets
from models.github_api import fetch_github_topics
from models.conference_scraper import fetch_conference_data
import json

def gather_research_data(query):
    """
    Збирає дані з кількох джерел на основі запиту.
    :param query: Пошуковий запит для всіх джерел.
    :return: Словник з даними від кожного джерела.
    """
    API_KEY = "YOUR_SEMANTIC_SCHOLAR_API_KEY"  # Замініть на ваш API ключ
    print("Fetching topics from Semantic Scholar...")
    google_scholar_topics = fetch_semantic_scholar_topics(query, API_KEY)
    
    print("Fetching topics from arXiv...")
    arxiv_topics = fetch_arxiv_topics(query)
    
    print("Fetching datasets from Kaggle...")
    kaggle_datasets = fetch_kaggle_datasets(query)
    
    print("Fetching repositories from GitHub...")
    github_repos = fetch_github_topics(query)
    
    print("Fetching upcoming conferences and journals...")
    conference_data = fetch_conference_data()

    # Об'єднуємо дані з усіх джерел в один словник
    combined_data = {
        "semantic_scholar": google_scholar_topics,  # Змінено назву на semantic_scholar
        "arxiv": arxiv_topics,
        "kaggle": kaggle_datasets,
        "github": github_repos,
        "conferences": conference_data
    }

    return combined_data

def save_to_json(data, filename="data/research_trends.json"):
    """
    Зберігає зібрані дані у JSON файл.
    :param data: Словник з даними.
    :param filename: Назва файлу для збереження.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Пошуковий запит
    query = "machine learning healthcare"
    
    # Збираємо дані з усіх джерел
    print(f"Gathering research data for query: '{query}'")
    research_data = gather_research_data(query)
    
    # Зберігаємо зібрані дані у research_trends.json
    save_to_json(research_data)
    
    print("Data gathering and saving complete.")
