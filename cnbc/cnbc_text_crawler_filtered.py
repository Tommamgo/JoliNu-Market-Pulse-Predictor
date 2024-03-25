import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
from pathlib import Path

def extract_article_urls_from_main_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    urls = []
    for item in data:
        if item.get('cn:type') != 'cnbcvideo' and not item.get('cn:contentClassification'):
            if 'url' in item:
                urls.append(item['url'])
    return urls

def replace_quotes_in_item(item):
    """
    Replace all instances of " with ' in the item.
    If the item is a list, apply this replacement to each string in the list.
    """
    if isinstance(item, str):
        return item.replace('"', "'")
    elif isinstance(item, list):
        return [replace_quotes_in_item(sub_item) for sub_item in item]
    else:
        return item

def get_value(data, keys, default="nan"):
    """
    Navigate through a nested dictionary using a list of keys.
    Returns the value if found, else returns default ('nan').
    Applies quote replacement to strings and lists of strings.
    """
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return replace_quotes_in_item(default)
        
    return replace_quotes_in_item(data) if data else replace_quotes_in_item(default)


def extract_article_data(data):

    # Versuch, die Autorenliste zu extrahieren
    authors_list = get_value(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "author"], [])
    authors_names = [author["name"] for author in authors_list] if authors_list else []

    # Fallback auf 'creatorOverwrite', falls keine Autoren gefunden wurden
    if not authors_names:
        creator_overwrite = get_value(data, ["page", "page", "layout", 2, "columns", 0, "modules", 2, "data", "creatorOverwrite"], "nan")
        authors_names = [creator_overwrite] if creator_overwrite != "nan" else []

    """
    Extrahiert erforderliche Daten aus einem JSON-Objekt, das aus einem Artikel stammt.
    """
    extracted_info = {
    "publish_date": get_value(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "datePublished"]),
    "keywords": [tag["headline"] for tag in get_value(data, ["page", "page", "additionalSectionContent"], [])],
    "authors": authors_names,
    "title": get_value(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "title"]),
    "text": get_value(data, ["page", "page", "layout", 2, "columns", 0, "modules", 2, "data", "articleBodyText"]),
    "link": get_value(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "url"]),
    "original_publisher": get_value(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "sourceOrganization", 0, "name"]),
    "article_publisher": "CNBC",
    "search_word": "Boeing",  # Placeholder for 'search_word' as its source wasn't specified
    "short_description": get_value(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "description"]),
    "last_modified_date": get_value(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "dateModified"])
    }
    return extracted_info


def crawl_article(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'lxml')
            script_tag = soup.find('script', string=re.compile('window\.__s_data'))
            if script_tag:
                script_content = script_tag.string
                json_data_match = re.search(r'window\.__s_data\s*=\s*(\{.*?\});', script_content, re.DOTALL)
                if json_data_match:
                    json_data_str = json_data_match.group(1)
                    json_data = json.loads(json_data_str)
                    # Anpassung: Rückgabe eines vereinfachten Datenstruktur-Objekts
                    return extract_article_data(json_data)
                else:
                    print("JSON-Daten konnten im Script-Tag nicht gefunden werden.")
            else:
                print("Entsprechender <script> Tag nicht gefunden.")
        else:
            print(f"Fehler beim Abrufen der Seite {url}: Statuscode {response.status_code}")
    except json.decoder.JSONDecodeError as e:
        print(f"JSONDecodeError beim Verarbeiten von {url}: {e}")
    except Exception as e:
        print(f"Unbekannter Fehler beim Verarbeiten von {url}: {e}")
    return None

def save_article(article, file_name="collected_articles.json"):
    # Path to the file
    file_path = Path(file_name)
    
    # Check if the file already exists
    if file_path.exists():
        # File exists, load the existing content
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                # If the file cannot be correctly read, start with an empty list
                data = []
    else:
        # File does not exist, start with an empty list
        data = []
    
    # Add article to the data list
    data.append(article)
    
    # Save the data in the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


file_path = '/Users/jonas/Documents/Master/S2/Natural Language Processing/codes/git/JoliNu-Market-Pulse-Predictor/cnbc/CNBC_links.json'  # Pfad aktualisieren


article_urls = extract_article_urls_from_main_json(file_path)

all_extracted_data = []  # Liste zum Speichern aller extrahierten Daten
counter = 0

for url in article_urls:
    print(f'Processing article {counter + 1} of {len(article_urls)}: {url}')
    article_data = crawl_article(url)
    if article_data:
        all_extracted_data.append(article_data)
        counter += 1
        # Zwischenspeichern alle 20 Artikel
        if counter % 20 == 0:
            save_article(all_extracted_data)
            all_extracted_data = []  # Reset der Liste nach dem Speichern
            wait_time = random.randint(2, 10)
            print(f"Warte {wait_time} Sekunden...")
            time.sleep(wait_time)

# Speichern der verbleibenden Daten, falls weniger als 20 übrig sind
if all_extracted_data:
    save_article(all_extracted_data)
    print("Data collection completed.")









