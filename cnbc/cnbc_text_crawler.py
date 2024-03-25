import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random

def extract_article_urls_from_main_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    urls = []
    for item in data:
        if item.get('cn:type') != 'cnbcvideo' and not item.get('cn:contentClassification'):
            if 'url' in item:
                urls.append(item['url'])
    return urls

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
                    return json_data
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

def save_data(data, file_name):
    with open(file_name, 'a', encoding='utf-8') as output_file:
        for item in data:
            json.dump(item, output_file, ensure_ascii=False)
            output_file.write('\n')

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
            save_data(all_extracted_data, 'CNBC_Texts.json')
            all_extracted_data = []  # Reset der Liste nach dem Speichern
            wait_time = random.randint(2, 10)
            print(f"Warte {wait_time} Sekunden...")
            time.sleep(wait_time)

# Speichern der verbleibenden Daten, falls weniger als 20 übrig sind
if all_extracted_data:
    save_data(all_extracted_data, 'CNBC_Texts.json')

print("Data collection completed.")
