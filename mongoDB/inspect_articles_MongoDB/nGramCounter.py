from pymongo import MongoClient
import spacy
from collections import Counter
import json

# Lade das SpaCy-Modell
nlp = spacy.load("en_core_web_sm")

# Verbindungsdaten
username = 'admin'
password = 'admin'
host = 'localhost'
port = '27017'
authSource = 'admin'

# MongoDB-Verbindung herstellen
mongo_uri = f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}'
client = MongoClient(mongo_uri)
db = client['web_articles']
collection = db['articles']

# Funktion zum Generieren von N-Grammen
def generate_ngrams(doc, n):
    ngrams = []
    # Erzeuge N-Gramme aus den Token, die keine Leerzeichen sind
    tokens = [token.text for token in doc if not token.is_space]
    for i in range(len(tokens)-n+1):
        ngrams.append(' '.join(tokens[i:i+n]))
    return ngrams

# Funktion zur Verarbeitung von Texten und Extraktion der häufigsten N-Gramme
def process_texts(cursor, n_values=[2, 3, 4]):
    ngram_frequencies = {n: Counter() for n in n_values}
    schleife=0
    for document in cursor:
        print(f"Durchgang Nummer: {schleife}")
        schleife+=1
        preprocessed_text = document.get('preprocessed_text', '')
        doc = nlp(preprocessed_text)
        for n in n_values:
            ngram_frequencies[n].update(generate_ngrams(doc, n))
    
    # Extrahiere die 100 häufigsten N-Gramme für jedes N
    most_common_ngrams = {n: ngram_frequencies[n].most_common(100) for n in n_values}
    
    return most_common_ngrams

# Initialisiere einen Cursor für die schrittweise Verarbeitung
cursor = collection.find(no_cursor_timeout=True, projection={'preprocessed_text': True})

# Führe die N-Gramm-Analyse durch
most_common_ngrams = process_texts(cursor)

# Schließe den Cursor
cursor.close()

# Speichere die Ergebnisse in einer JSON-Datei
with open('ngrams.json', 'w', encoding='utf-8') as f:
    json.dump(most_common_ngrams, f, ensure_ascii=False, indent=4)

print("Die N-Gramm-Analyse wurde erfolgreich durchgeführt und in 'most_common_ngrams.json' gespeichert.")
