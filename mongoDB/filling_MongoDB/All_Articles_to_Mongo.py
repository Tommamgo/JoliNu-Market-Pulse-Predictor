from pymongo import MongoClient
import json
from dateutil import parser as date_parser
from datetime import datetime
import pytz
import re
import spacy

# Pfade zu Artikel JSONs
cnbc_pfad = "./../../cnbc/CNBC_articles.json"
nasdaq_pfad = "./../../nasdaq/data/BoeingData.json"
reuters_pfad = "./../../reuters/reuters_articles.json"
bbc_pfad = "./../../bbc_scraped_articles.json"
marketwatch_pfad = "./../../marketWatch/tests/marketwatch_scraped_articles copy.json"

# Ersetze diese Werte mit deinen eigenen Anmeldeinformationen
username = 'admin'
password = 'admin'
host = 'localhost'
port = '27017'
authSource = 'admin'  # Die Datenbank, die für die Authentifizierung verwendet wird, oft 'admin'

# Erstelle die Verbindungs-URI
mongo_uri = f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}'

# Verbinde dich mit MongoDB unter Verwendung der Authentifizierung
print("Verbindungsaufbau zu MongoDB...")
client = MongoClient(mongo_uri)
print("Verbindung erfolgreich.")

# Referenziere deine Datenbank und Collection
db = client['web_articles']
collection = db['articles']

# Funktion zum Laden und Einfügen von Artikeln
def load_and_insert_articles(file_path):
    print(f"Lade Daten aus {file_path}...")
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        articles = list(data['articles'].values())
        collection.insert_many(articles)
        print(f"{len(articles)} Artikel erfolgreich aus {file_path} eingefügt.")
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError in Datei {file_path}: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten beim Laden der Datei {file_path}: {e}")

# Artikel aus allen JSON-Dateien laden und einfügen
file_paths = [cnbc_pfad, nasdaq_pfad, reuters_pfad, bbc_pfad, marketwatch_pfad]
for path in file_paths:
    load_and_insert_articles(path)

print("Alle Dokumente erfolgreich eingefügt.")

# Fortschrittsanzeige
def print_progress(current, total):
    progress_length = 50
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}% {current} / {total}", end="")

# Datum vereinheitlichen --------------------------------------------------------------------
def preprocess_date(date_str):
    date_str = date_str.replace("—", " ")
    date_str = re.sub(r',', '', date_str)
    return date_str

def convert_date_format(date_str):
    try:
        preprocessed_date_str = preprocess_date(date_str)
        dt = date_parser.parse(preprocessed_date_str)
        return dt.astimezone(pytz.utc).isoformat()
    except (ValueError, TypeError):
        return datetime(1970, 1, 1, tzinfo=pytz.utc).isoformat()

print("Beginne mit der Vereinheitlichung der Datumsformate...")
cursor = collection.find(no_cursor_timeout=True)
total_docs = collection.count_documents({})

try:
    for i, document in enumerate(cursor, start=1):
        updates = {}
        if 'publish_date' in document:
            new_date = convert_date_format(document['publish_date'])
            updates['publish_date'] = new_date
        if 'last_modified_date' in document:
            new_date = convert_date_format(document['last_modified_date'])
            updates['last_modified_date'] = new_date
        if updates:
            collection.update_one({'_id': document['_id']}, {'$set': updates})
        print_progress(i, total_docs)
finally:
    cursor.close()

print("\nDatumsformate erfolgreich aktualisiert.")

# Text vorverarbeitung ------------------------------------------------------------------
print("Lade spaCy-Modell...")
nlp = spacy.load("en_core_web_sm")
print("spaCy-Modell erfolgreich geladen.")

def preprocess_text(text):
    doc = nlp(text)
    clean_text = " ".join(token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and token.is_alpha)
    return clean_text

print("Beginne mit der Textvorverarbeitung...")
cursor = collection.find(no_cursor_timeout=True)

try:
    for i, document in enumerate(cursor, start=1):
        text = document.get("text", "")
        processed_text = preprocess_text(text)
        collection.update_one({"_id": document["_id"]}, {"$set": {"preprocessed_text": processed_text}})
        print_progress(i, total_docs)
finally:
    cursor.close()

print("\nTextvorverarbeitung erfolgreich abgeschlossen.")

