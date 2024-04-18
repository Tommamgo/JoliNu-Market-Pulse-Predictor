import requests
import time
import random
import json
import re

# Variablen für die Konfiguration
input_file = "cnn/scraped_data.json"
output_file = "cnn/extracted_data.json"
user_agents_file = "cnn/userAgents.txt"

min_delay = 10
max_delay = 20

def load_user_agents(filename):
    with open(filename, "r") as file:
        agents = [line.strip() for line in file.readlines()]
    print("User-Agents geladen.")
    return agents

def load_json_data(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

def filter_news_articles(data):
    return [item for item in data if item.get('type') == 'NewsArticle']

def extract_json_from_html(url, user_agent):
    headers = {
        "User-Agent": user_agent
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        else:
            print(f"Fehler beim Abrufen der URL {url}: Status-Code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Netzwerkanfrage für {url}: {e}")
    return None

def save_data(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file)
    print("Daten gespeichert.")

def print_progress(current, total):
    progress_length = 50
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}% - Artikel {current} von {total}", end="")

def main():
    user_agents = load_user_agents(user_agents_file)
    articles = load_json_data(input_file)
    news_articles = filter_news_articles(articles)
    
    extracted_jsons = []
    for index, article in enumerate(news_articles):
        extracted_json = extract_json_from_html(article['url'], random.choice(user_agents))
        if extracted_json:
            extracted_jsons.append(extracted_json)
        
        print_progress(index + 1, len(news_articles))
        time.sleep(random.randint(min_delay, max_delay))  # Delay zwischen den Abrufen

        # Zwischenspeicherung alle 10 Artikel
        if (index + 1) % 10 == 0 or index == len(news_articles) - 1:
            save_data(extracted_jsons, output_file)

    print("\nScraping abgeschlossen!")

if __name__ == "__main__":
    main()
