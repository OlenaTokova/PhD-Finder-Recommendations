import kaggle

def fetch_kaggle_datasets(query):
    datasets = kaggle.api.dataset_list(search=query, sort_by="hottest")
    topics = []
    for dataset in datasets:
        topics.append({
            "title": dataset.title,
            "url": f"https://www.kaggle.com/{dataset.ref}",
            "description": dataset.description
        })
    return topics
