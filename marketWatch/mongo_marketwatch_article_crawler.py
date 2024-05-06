import requests
import random
import json
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pytz
import re
import string
from pymongo import MongoClient, errors

min_delay = 10
max_delay = 25

# MongoDB Verbindung
username = 'admin'
password = 'admin'
host = 'localhost'
port = '27017'
authSource = 'admin'
mongo_uri = f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}'
client = MongoClient(mongo_uri)
db = client['web_articles']
collection = db['marketwatch_articles']

input_file = "marketwatch/marketwatch_scraped_links.json"
user_agents_file = "marketwatch/userAgents.txt"
random_urls_file = "marketwatch/random_urls.txt"
invalid_links_file = "marketwatch/invalid_links.txt"

def generate_random_cookie():
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
        urls = [line.strip() for line in file.readlines()]
    print("Zufällige URLs geladen.")
    return urls

def load_json_data(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"articles": {}}

def get_last_processed_index():
    try:
        with open("marketwatch/last_index.json", "r") as file:
            return json.load(file).get("last_processed", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_last_processed_index(index):
    with open("marketwatch/last_index.json", "w") as file:
        json.dump({"last_processed": index}, file)

def save_invalid_link(link):
    with open(invalid_links_file, "a") as file:
        file.write(link + "\n")

def get_html_content(url, agent, r_url):
    headers = {
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
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der URL: {e}")
        save_invalid_link(url)
        return None


def parse_publish_date(text):
    try:
        # Erkennen des Datums und der Uhrzeit im Text, inklusive eines optionalen "Published: " Präfixes
        match = re.search(r"(?:First Published: |Published: )?(\w+\.?\s\d{1,2}, \d{4} at \d{1,2}:\d{2} [ap]\.m\. ET)", text)
        if not match:
            return 'nan'

        date_string = match.group(1).replace('p.m.', 'PM').replace('a.m.', 'AM')

        # Konvertiere Monatsnamen Abkürzungen in vollständige Namen
        replacements = {
            "Jan.": "January", "Feb.": "February", "Mar.": "March", "Apr.": "April",
            "May.": "May", "Jun.": "June", "Jul.": "July", "Aug.": "August", "Sept.": "September",
            "Sep.": "September", "Oct.": "October", "Nov.": "November", "Dec.": "December"
        }
        for short, long in replacements.items():
            date_string = date_string.replace(short, long)

        # Datum und Uhrzeit parsen
        date_time_obj = datetime.strptime(date_string, "%B %d, %Y at %I:%M %p ET")
        # Lokalisiere das Datum in der US/Eastern Zeitzone und konvertiere zu UTC
        eastern = pytz.timezone('US/Eastern')
        date_time_obj = eastern.localize(date_time_obj).astimezone(pytz.utc)
        
        return date_time_obj.isoformat()
    except ValueError:
        return 'nan'


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

        if publish_date == 'nan':
            save_invalid_link(url)
            raise ValueError("Kein Veröffentlichungsdatum im Artikel")
        
        title = soup.select_one('h1.article__headline[itemprop="headline"]').text.strip() if soup.select_one('h1.article__headline[itemprop="headline"]') else None
        if not title:
            print('Kein Titel gefunden.')
            return None

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

def save_data(article):
    try:
        if collection.find_one({"link": article['link']}):
            print(f"\n Artikel bereits in der Datenbank vorhanden: {article['title']}")
            return
        collection.insert_one(article)
        #print(f"Artikel hinzugefügt: {article['title']}")
    except errors.PyMongoError as e:
        print(f"Fehler beim Speichern in MongoDB: {e}")


def print_progress(current, total, titel):
    progress_length = 50
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}% - Artikel {current} von {total} - {titel[:30]}... ", end="")


def main():
    user_agents = load_user_agents(user_agents_file)
    r_urls = load_random_urls(random_urls_file)
    data = load_json_data(input_file)
    article_urls = data.get('results', [])
    last_processed = get_last_processed_index()
    total_articles = len(article_urls)
    invalid_link_count = 0  # Initialisiere den Zähler für ungültige Links

    print(f"Starting: {last_processed} of {total_articles} articles processed.")

    for index, url in enumerate(article_urls[last_processed+1:], start=last_processed):  # Beginne bei der letzten bearbeiteten URL
        if index < last_processed:
            continue

        try:
            user_agent = random.choice(user_agents)
            r_url = random.choice(r_urls)
            html_content = get_html_content(url, user_agent, r_url)
            if html_content is None:  
                invalid_link_count += 1
                if invalid_link_count == 3:
                    print("Drei ungültige Links hintereinander, Skript wird beendet.")
                    break
                continue
            article_data = extract_data_from_html(html_content, url)
            if article_data:
                save_data(article_data)
                invalid_link_count = 0  # Zurücksetzen des Zählers nach erfolgreichem Speichern
                print_progress(index + 1, total_articles, article_data.get('title', 'nan'))
        except ValueError as e:
            print(e)
            invalid_link_count += 1
            if invalid_link_count == 3:
                print("Drei ungültige Links hintereinander, Skript wird beendet.")
                break
        finally:
            save_last_processed_index(index)
            time.sleep(random.randint(min_delay, max_delay))

    print("\nScraping completed!")

if __name__ == "__main__":
    main()
