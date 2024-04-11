'''
Dieses Script geht alle Vorverarbeiteten Texte aus der Spalte "preprocessed_text" durch und Zählt, wie oft
bestimmte Nomen in allen Texten zusammengefasst vorkommen. Die x häufgsten Nomen werden in keyword_counter.json 
gespeichert.
'''

import json
from pymongo import MongoClient
import spacy
from collections import Counter

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

# Cursor zur Minimierung des Speicherverbrauchs
cursor = collection.find(projection={'preprocessed_text': True})

word_freq = Counter()

try:
    schleife = 0
    for document in cursor:
        print(f"Durchgang Nummer: {schleife}")
        schleife+=1
        # Extrahiere den vorverarbeiteten Text
        preprocessed_text = document.get('preprocessed_text', '')
        # Verarbeite den Text mit SpaCy
        doc = nlp(preprocessed_text)
        # Filtere nach Substantiven und Eigennamen
        words = [token.text for token in doc if token.pos_ in ('NOUN', 'PROPN')]
        # Aktualisiere die Häufigkeitszählung
        word_freq.update(words)
finally:
    cursor.close()

# Die X häufigsten Wörter
common_words = word_freq.most_common(1000)

# Speichere die Ergebnisse in einer JSON-Datei
with open('keyword_counter.json', 'w', encoding='utf-8') as f:
    json.dump(dict(common_words), f, ensure_ascii=False, indent=4)

print("Die Keyword-Analyse wurde erfolgreich in 'keyword_analysis_results.json' gespeichert.")
