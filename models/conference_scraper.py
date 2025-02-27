import requests
from bs4 import BeautifulSoup

def fetch_conference_data(url="https://www.exampleconference.org/upcoming-events"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for 4xx/5xx status codes
        soup = BeautifulSoup(response.content, "html.parser")
        events = []
        for event in soup.find_all("div", class_="event-info"):
            events.append({
                "title": event.find("h2").get_text(strip=True),
                "date": event.find("span", class_="date").get_text(strip=True),
                "location": event.find("span", class_="location").get_text(strip=True)
            })
        return events
    except requests.exceptions.RequestException as e:
        print(f"Error fetching conference data: {e}")
        return []  # Return an empty list if fetching fails
