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

def safe_get(data, path, default=None):
    """
    Sicherer Zugriff auf verschachtelte Datenstrukturen.
    :param data: Die Datenstruktur, aus der die Daten abgerufen werden sollen.
    :param path: Eine Liste von Schlüsseln/Indizes, die den Pfad zum Zielwert definieren.
    :param default: Der Standardwert, der zurückgegeben wird, wenn der Zielwert nicht gefunden wird.
    :return: Der Zielwert oder der Standardwert, falls der Zielwert nicht gefunden wird.
    """
    try:
        for key in path:
            data = data[key]
        return data
    except (KeyError, IndexError, TypeError):
        return default

def extract_article_data(data):
    """
    Verbesserte Extraktion von Artikeldaten mit sicherer Fehlerbehandlung.
    """
    try:
        # Versuch, die Autorenliste zu extrahieren
        authors_list = safe_get(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "author"], [])
        authors_names = [author.get("name", "") for author in authors_list] if authors_list else []

        # Fallback auf 'creatorOverwrite', falls keine Autoren gefunden wurden
        if not authors_names:
            creator_overwrite = safe_get(data, ["page", "page", "layout", 2, "columns", 0, "modules", 2, "data", "creatorOverwrite"], "nan")
            authors_names = [creator_overwrite] if creator_overwrite != "nan" else []

        # Extraktion der restlichen erforderlichen Daten
        extracted_info = {
            "publish_date": safe_get(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "datePublished"], "nan"),
            "keywords": [tag.get("headline", "") for tag in safe_get(data, ["page", "page", "additionalSectionContent"], [])],
            "authors": authors_names,
            "title": safe_get(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "title"], "nan"),
            "text": safe_get(data, ["page", "page", "layout", 2, "columns", 0, "modules", 2, "data", "articleBodyText"], "nan"),
            "link": safe_get(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "url"], "nan"),
            "original_publisher": safe_get(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "sourceOrganization", 0, "name"], "nan"),
            "article_publisher": "CNBC",
            "search_word": "Boeing",
            "short_description": safe_get(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "description"], "nan"),
            "last_modified_date": safe_get(data, ["page", "page", "layout", 1, "columns", 0, "modules", 0, "data", "dateModified"], "nan")
        }
        return extracted_info
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None



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









