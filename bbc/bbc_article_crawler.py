import requests
import random
import json
from datetime import datetime
from bs4 import BeautifulSoup
import time
import re

# Configuration
input_file = "bbc/bbc_scraped_links.json"
output_file = "bbc/bbc_scraped_articles.json"
user_agents_file = "bbc/userAgents.txt"
min_delay = 8
max_delay = 12

def filter_news_articles(data):
    articles = []
    keywords = ["Boeing", "Airbus", "Plane"]
    for item in data:
        # Überprüfen, ob es sich um einen Artikel handelt
        if item.get('type') == 'article':
            title = item.get('title', '').lower()
            summary = item.get('summary', '').lower()
            alt_text = item.get('indexImage', {}).get('model', {}).get('blocks', {}).get('altText', '')
            
            # Überprüfen, ob eines der Schlüsselwörter in Titel, Zusammenfassung oder Bildtext enthalten ist
            if alt_text is not None:  # Überprüfen, ob alt_text nicht None ist
                alt_text = alt_text.lower()
            for keyword in keywords:
                if keyword.lower() in title or keyword.lower() in summary or (alt_text and keyword.lower() in alt_text):
                    articles.append(item)
                    break  # Beenden Sie die Schleife, sobald ein Schlüsselwort gefunden wurde
    
    return articles

def load_user_agents(filename):
    with open(filename, "r") as file:
        agents = [line.strip() for line in file.readlines()]
    print("User-Agents geladen.")
    return agents

def load_json_data(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}  # Initialisiere eine leere Datenstruktur, wenn die Datei nicht gefunden wird
    except json.JSONDecodeError:
        data = {}  # Initialisiere eine leere Datenstruktur, wenn die Datei beschädigt ist
    return data

def build_full_url(path):
    return f"https://www.bbc.com{path}"

def get_html_content(url, user_agent):
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "de-DE,de;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.bbc.com/search?q=Boeing"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def extract_keywords_from_url(url):
    # Extrahiert die Stücke zwischen den Bindestrichen vor der letzten Nummer
    match = re.search(r'/([\w-]+)-\d+', url)
    if match:
        parts = match.group(1).split('-')
        return [] + parts
    return ['nan']

def extract_data_from_html(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract JSON-LD data for metadata
    script_json_ld = soup.find('script', type='application/ld+json')
    metadata = json.loads(script_json_ld.string) if script_json_ld else {}

    data = {}
    full_text = []
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
    if script_tag:
        data = json.loads(script_tag.string)
        page_data = data['props']['pageProps']['page']
        article_id = list(page_data.keys())[0]
        contents = page_data[article_id]['contents']

        for content in contents:
            if content['type'] == 'text':
                for block in content['model']['blocks']:
                    if block['type'] == 'paragraph':
                        full_text.append(block['model']['text'])

    full_text = ' '.join(full_text)
    authors = metadata.get('author', [{}])

    author_names = [author.get('name', 'nan') for author in authors] if isinstance(authors, list) else [authors.get('name', 'nan')]

    # Verwenden des ursprünglichen URL als Link
    article_link = url

    # Keywords aus URL extrahieren
    keywords = extract_keywords_from_url(url)

    article_data = {
        'publish_date': metadata.get('datePublished', 'nan'),
        'last_modified_date': metadata.get('dateModified', 'nan'),
        'authors': author_names,
        'title': metadata.get('headline', 'nan'),
        'text': full_text,
        'link': article_link,
        'original_publisher': metadata.get('publisher', {}).get('name', 'nan'),
        'article_publisher': "BBC",
        'search_word': "Boeing",
        'keywords': keywords,
        'short_description': metadata.get('description', 'nan')
    }
    return article_data


def save_data(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)  # Direktes Speichern der übergebenen Daten ohne zusätzliche Verpackung in "articles"
    print(" Daten gespeichert.")


def print_progress(current, total):
    progress_length = 50
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}% - Artikel {current} von {total}", end="")

def main():
    user_agents = load_user_agents(user_agents_file)
    articles = filter_news_articles(load_json_data(input_file).get('results', []))
    transformed_data = load_json_data(output_file)
    if "articles" not in transformed_data:
        transformed_data["articles"] = {}

    processed_articles_count = len(transformed_data["articles"])
    print(f"Fortgeschritten: {processed_articles_count} von {len(articles)} Artikel verarbeitet.")

    start_index = processed_articles_count

    for index, article in enumerate(articles[start_index:], start=start_index):
        full_url = build_full_url(article['path'])
        user_agent = random.choice(user_agents)
        html_content = get_html_content(full_url, user_agent)
        extracted_data = extract_data_from_html(html_content, full_url)
        if extracted_data:
            article_title = extracted_data.get('title', f"Unnamed Article {index}")
            transformed_data["articles"][article_title] = extracted_data

        processed_articles_count += 1
        print_progress(processed_articles_count, len(articles))
        time.sleep(random.randint(min_delay, max_delay))

        if processed_articles_count % 10 == 0 or index == len(articles) - 1:
            save_data(transformed_data, output_file)

    print("\nScraping abgeschlossen!")

if __name__ == "__main__":
    main()



