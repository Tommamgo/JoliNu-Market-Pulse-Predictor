from pymongo import MongoClient
import json
from dateutil import parser
import pytz
import re
import spacy

# Pfade zu Artikel JSONS
cnbc_pfad = "./../cnbc/CNBC_articles.json"
nasdaq_pfad = "./../nasdaq/data/BoeingData.json"
reuters_pfad = "./../reuters/reuters_articles.json"

# Ersetze diese Werte mit deinen eigenen Anmeldeinformationen
username = 'admin'
password = 'admin'
host = 'localhost'
port = '27017'
authSource = 'admin'  # Die Datenbank, die für die Authentifizierung verwendet wird, oft 'admin'

# Erstelle die Verbindungs-URI
mongo_uri = f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}'

# Verbinde dich mit MongoDB unter Verwendung der Authentifizierung
client = MongoClient(mongo_uri)

# Referenziere deine Datenbank und Collection
db = client['web_articles']
collection = db['articles']

# Artikel in mongo speichern -----------------------------------------------------------
# Lade deine JSON-Daten
with open(reuters_pfad, 'r') as file:
    data = json.load(file)

# Konvertiere die Daten in ein Array von Dokumenten
articles = list(data['articles'].values())

# Füge die Dokumente in die MongoDB Collection ein
collection.insert_many(articles)

with open(nasdaq_pfad, 'r') as file:
    data = json.load(file)

# Konvertiere die Daten in ein Array von Dokumenten
articles = list(data['articles'].values())

# Füge die Dokumente in die MongoDB Collection ein
collection.insert_many(articles)

with open(cnbc_pfad, 'r') as file:
    data = json.load(file)

# Konvertiere die Daten in ein Array von Dokumenten
articles = list(data['articles'].values())

# Füge die Dokumente in die MongoDB Collection ein
collection.insert_many(articles)

print("Dokumente erfolgreich eingefügt")

# Datum vereinheitlichen --------------------------------------------------------------------

def preprocess_date(date_str):
    # Ersetze — mit einem Leerzeichen, um das Parsing zu vereinfachen
    date_str = date_str.replace("—", " ")
    # Ersetze Kommas und korrigiere das Format, wenn nötig
    date_str = re.sub(r',', '', date_str)
    return date_str

def convert_date_format(date_str):
    try:
        # Vorverarbeitung für spezielle Formate
        preprocessed_date_str = preprocess_date(date_str)
        # Parser erkennt automatisch das Format und konvertiert es zu einem datetime Objekt
        dt = parser.parse(preprocessed_date_str)
        # Konvertiere das datetime Objekt zu einem einheitlichen ISO 8601 String
        return dt.astimezone(pytz.utc).isoformat()
    except ValueError:
        # Wenn das Parsing fehlschlägt, gib den ursprünglichen String zurück oder handle den Fehler
        return date_str

cursor = collection.find(no_cursor_timeout=True)

try:
    schleife = 0
    for document in cursor:
        print(f"Durchgang Nummer:{schleife}")
        schleife+=1
        if 'publish_date' in document:
            new_date = convert_date_format(document['publish_date'])
            collection.update_one({'_id': document['_id']}, {'$set': {'publish_date': new_date}})
finally:
    cursor.close()

print("Datumsformate aktualisiert.")

# Text vorverarbeitung ------------------------------------------------------------------
# Lade das spaCy Modell
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    # Erstelle ein Doc-Objekt
    doc = nlp(text)
    # Entferne Stopwörter, Satzzeichen und führe Lemmatisierung durch, behalte nur alphabetische Zeichen
    clean_text = " ".join(token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and token.is_alpha)
    return clean_text

# Initialisiere einen Cursor für die schrittweise Verarbeitung
cursor = collection.find(no_cursor_timeout=True)  # Verhindert das Timeout für große Collections

try:
    c = 0
    for document in cursor:
        print(f"Verarbeite Tex Nummer {c}")
        c+=1
        # Extrahiere den Text des Dokuments
        text = document.get("text", "")
        # Führe die Textvorverarbeitung durch
        processed_text = preprocess_text(text)
        # Aktualisiere das Dokument mit dem neuen Feld "processed_text"
        collection.update_one({"_id": document["_id"]}, {"$set": {"preprocessed_text": processed_text}})
finally:
    cursor.close()  # Stelle sicher, dass der Cursor ordnungsgemäß geschlossen wird

print("Textvorverarbeitung abgeschlossen.")