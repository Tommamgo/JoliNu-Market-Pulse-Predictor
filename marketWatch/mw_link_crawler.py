import requests
import time
import random
import json
import os
from bs4 import BeautifulSoup

# Variablen für die Konfiguration
base_url = "https://www.marketwatch.com/search/moreHeadlines"
query = "Boeing"
total_pages = 822  # 16442 Artikel / 20 Artikel pro Seite, 0-basierte Indexierung, also bleibt 822
user_agents_file = "marketwatch/userAgents.txt"
output_file = "marketwatch/marketwatch_scraped_links.json"

min_delay = 4
max_delay = 8

def load_user_agents(filename):
    try:
        with open(filename, "r") as file:
            agents = [line.strip() for line in file.readlines()]
        return agents
    except FileNotFoundError:
        print("User-Agent-Datei nicht gefunden.")
        return ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15"]

def load_existing_data():
    if os.path.exists(output_file):
        with open(output_file, "r") as file:
            data = json.load(file)
            return data.get("results", []), data.get("last_page", 0)
    else:
        return [], 0

def get_page_data(page_number, user_agent):
    params = {
        "q": query,
        "ts": 0,
        "partial": True,
        "tab": "All News",
        "pageNumber": page_number
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'de-DE,de;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.marketwatch.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('div', class_='article__content')
        links = [a['href'] for article in articles for a in article.find('h3', class_='article__headline').find_all('a') if 'href' in a.attrs]
        return links
    else:
        print(f'Fehler beim Abrufen der Seite: {response.status_code}')
        return None

def print_progress(current, total):
    progress_length = 50
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}% {current} / {total}", end="")

def save_data(results, last_page):
    data = {
        "results": results,
        "last_page": last_page
    }
    with open(output_file, "w") as f:
        json.dump(data, f)
    print(f"\nDaten gespeichert nach Seite {last_page}.")

def scrape_articles(user_agents):
    results, last_loaded_page = load_existing_data()
    start_page = last_loaded_page + 1

    for page_number in range(start_page, total_pages + 1):
        user_agent = random.choice(user_agents)
        links = get_page_data(page_number, user_agent)
        if links:
            results.extend(links)
        
        print_progress(page_number, total_pages)
        
        if page_number % 5 == 0:
            save_data(results, page_number)

        time.sleep(random.randint(min_delay, max_delay))

    save_data(results, total_pages)  # Sicherstellen, dass die endgültigen Daten gespeichert werden
    return "\nScraping abgeschlossen!"

if __name__ == "__main__":
    user_agents = load_user_agents(user_agents_file)
    print("Starte das Crawling der MarketWatch-Suchergebnisse für 'Boeing'.")
    scrape_status = scrape_articles(user_agents)
    print(scrape_status)
