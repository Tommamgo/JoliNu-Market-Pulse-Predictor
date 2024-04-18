import requests
import time
import random
import json
import re
from datetime import datetime

# Konfiguration
input_file = "bbc/bbc_scraped_links.json"
output_file = "bbc/bbc_scraped_articles.json"
user_agents_file = "bbc/userAgents.txt"
min_delay = 10
max_delay = 20

def load_user_agents(filename):
    with open(filename, "r") as file:
        agents = [line.strip() for line in file.readlines()]
    print("User-Agents geladen.")
    return agents

def load_json_data(filename):
    with open(filename, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}  # Wenn die Datei leer oder beschädigt ist, starten Sie mit leeren Daten
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
            json_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        else:
            print(f"Fehler beim Abrufen der URL {url}: Status-Code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Netzwerkanfrage für {url}: {e}")
    return None

def parse_date(date_str):
    if not date_str:
        return None  # Verhindert einen Fehler, wenn date_str None oder leer ist
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None  # Gibt None zurück, wenn kein gültiges Datum gefunden wurde


def transform_article_data(article, titles_done):
    if not isinstance(article, dict):
        return {}
    
    title = article.get("headline", "nan")
    if title in titles_done:
        return None  # Überspringe Artikel, die bereits verarbeitet wurden
    
    authors_list = article.get("author", [{"name": "nan"}])
    authors = ", ".join([author.get("name", "nan") for author in authors_list if author.get("name")])

    transformed = {
        title: {
            "publish_date": parse_date(article.get("datePublished", "nan")).strftime("%B %d, %Y %I:%M %p GMT+2") if parse_date(article.get("datePublished")) else "nan",
            "keywords": ", ".join(article.get("articleSection", ["nan"])),
            "authors": authors if authors else "nan",
            "title": title,
            "text": article.get("articleBody", "nan"),
            "link": article.get("mainEntityOfPage", {}).get("url", "nan"),
            "original_publisher": article.get("publisher", {}).get("name", "nan"),
            "article_publisher": article.get("publisher", {}).get("name", "nan"),
            "search_word": "Boeing",
            "short_description": article.get("description", "nan"),
            "last_modified_date": parse_date(article.get("dateModified", "nan")).strftime("%B %d, %Y %I:%M %p GMT+2") if parse_date(article.get("dateModified")) else "nan"
        }
    }
    return transformed

def save_data(data, filename):
    with open(filename, "w") as file:
        json.dump({"articles": data}, file, indent=4)
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
    transformed_data = load_json_data(output_file)
    titles_done = set(transformed_data.get("articles", {}).keys())  # Ladet bereits gespeicherte Titel
    news_articles = filter_news_articles(articles)
    
    transformed_articles = transformed_data.get("articles", {})
    for index, article in enumerate(news_articles):
        extracted_json = extract_json_from_html(article['url'], random.choice(user_agents))
        if extracted_json:
            transformed_article = transform_article_data(extracted_json, titles_done)
            if transformed_article:
                transformed_articles.update(transformed_article)
                titles_done.update(transformed_article.keys())
        
        print_progress(len(titles_done) + index + 1, len(news_articles))
        time.sleep(random.randint(min_delay, max_delay))  # Delay zwischen den Abrufen

        # Zwischenspeicherung alle 10 Artikel
        if (index + 1) % 10 == 0 or index == len(news_articles) - 1:
            save_data(transformed_articles, output_file)

    print("\nScraping abgeschlossen!")

if __name__ == "__main__":
    main()
