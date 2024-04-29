import requests
import random
import json
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pytz
import re
import os
import string


# Configuration
input_file = "marketwatch/marketwatch_scraped_links.json"
output_file = "marketwatch/marketwatch_scraped_articles.json"
invalid_links_file = "marketwatch/invalid_links.txt"
user_agents_file = "marketwatch/userAgents.txt"
random_urls_file = "marketwatch/random_urls.txt"
min_delay = 15
max_delay = 21
#session = requests.Session()

def generate_random_cookie():
    # Generiert einen zufälligen Cookie-Namen und Wert
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    value = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    return {name: value}

def load_user_agents(filename):
    with open(filename, "r") as file:
        agents = [line.strip() for line in file.readlines()]
    print("User-Agents geladen.")
    return agents

def load_random_urls(filename):
    with open(filename, "r") as file:
        agents = [line.strip() for line in file.readlines()]
    print("User-Agents geladen.")
    return agents

def load_json_data(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"articles": {}}

def save_invalid_link(link):
    with open(invalid_links_file, "a") as file:
        file.write(link + "\n")

def get_html_content(url, agent, r_url):
    headers = {
        #"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
        "User-Agent": agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": random.choice(["gzip, deflate, br", "gzip, deflate"]),
        "Accept-Language": random.choice(["de-DE,de;q=0.9", "en-US,en;q=0.9", "fr-FR,fr;q=0.9"]),
        "Connection": random.choice(["keep-alive", "close"]),
        "Referer": f"www.{r_url}",
        "DNT": "1" if random.random() > 0.5 else "0",
    }
    try:
        response = requests.get(url, headers=headers, cookies=generate_random_cookie())
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        save_invalid_link(url)
        return None

def parse_publish_date(text):
    try:
        match = re.search(r"(\w+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [ap]\.m\. ET)", text)
        if not match:
            return 'nan'
        date_string = match.group(1).replace('p.m.', 'PM').replace('a.m.', 'AM')
        date_time_obj = datetime.strptime(date_string, "%B %d, %Y at %I:%M %p ET")
        eastern = pytz.timezone('US/Eastern')
        date_time_obj = eastern.localize(date_time_obj).astimezone(pytz.utc)
        return date_time_obj.isoformat()
    except ValueError:
        return "nan"

def extract_data_from_html(html_content, url):
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        full_text = ' '.join([p.text for p in soup.find_all('p')])
        authors = [a.text.strip() for a in soup.select('.author.article__byline__name a')]
        if not authors:
            authors = [a.text.strip() for a in soup.select('.author h4')]
        if not authors:
            authors = [p.get_text(strip=True).replace('By ', '') for p in soup.select('p') if p.get_text(strip=True).startswith('By ')]
        if not authors:
            authors = ['nan']   

        publish_date_text = soup.select_one('time.timestamp--pub').text if soup.select_one('time.timestamp--pub') else soup.select_one('timestamp timestamp--pub').text if soup.select_one('timestamp timestamp--pub') else 'nan'
        publish_date = parse_publish_date(publish_date_text)
        title = soup.select_one('h1.article__headline[itemprop="headline"]').text.strip() if soup.select_one('h1.article__headline[itemprop="headline"]') else None
        if not title:
            return None
        
       # print(f"Extracted article: {title}")
        return {
            'publish_date': publish_date,
            'last_modified_date': publish_date,
            'authors': authors,
            'title': title,
            'text': full_text,
            'link': url,
            'original_publisher': 'MarketWatch',
            'article_publisher': 'MarketWatch',
            'search_word': 'Boeing',
            'keywords': ['nan'],
            'short_description': title
        }
    return None

def save_data(data, file_path):
    try:
        # Stelle sicher, dass die Datei existiert
        if not os.path.exists(file_path):
            print("Datei existiert nicht. Erstelle eine neue Datei.")
            with open(file_path, 'w') as file:
                json.dump({"articles": {}}, file, indent=4)
        
        # Datei für das Lesen und Schreiben öffnen
        with open(file_path, 'r+') as file:
            file.seek(0, os.SEEK_END)
            file.seek(file.tell() - 1, os.SEEK_SET)  # Gehe zurück vor die letzte schließende Klammer }

            # Füge ein Komma hinzu, wenn es bereits Daten gibt
            file.write(',\n')

            # Schreibe den neuen Artikel
            new_article_json = json.dumps({data}, indent=4)
            file.write(new_article_json[1:-1])  # Entferne die äußeren Klammern von json.dumps

            # Schließe das JSON-Objekt korrekt
            file.write('\n}')
            print("Artikel hinzugefügt.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
    

def print_progress(current, total):
    progress_length = 50
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}% - Artikel {current} von {total}", end="")

def main():
    user_agents = load_user_agents(user_agents_file)
    r_ruls = load_random_urls(random_urls_file)
    existing_data = load_json_data(output_file)
    already_processed = len(existing_data.get("articles", {}))
    data = load_json_data(input_file)
    article_urls = data.get('results', [])
    transformed_data = {}
    processed_articles_count = already_processed
    total_articles = len(article_urls) 
    print(f"Starting: {processed_articles_count} of {total_articles} articles processed.")

    for index, url in enumerate(article_urls, start=0):  # Startindex auf 0 setzen
        if index < already_processed:  # Überspringe bereits verarbeitete Artikel
            continue

        user_agent = random.choice(user_agents)
        r_url = random.choice(r_ruls)
        html_content = get_html_content(url, user_agent, r_url)
        if html_content:
            extracted_data = extract_data_from_html(html_content, url)
            if extracted_data:
                transformed_data[extracted_data['title']] = extracted_data

            processed_articles_count += 1
            print_progress(processed_articles_count, total_articles)
            time.sleep(random.randint(min_delay, max_delay))

            if processed_articles_count % 1 == 0 or index == len(article_urls):
                save_data(transformed_data, output_file)
                #time.sleep(random.randint(60, 120))
                transformed_data = {}  # Clear after saving

    print("\nScraping completed!")

if __name__ == "__main__":
    main()

