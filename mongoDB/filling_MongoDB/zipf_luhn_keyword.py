from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

import plotly.express as px


# Konfigurationseinstellungen
config = {
    'stop_words': 'english',  # Stopwörter für Englisch
    'n_keywords': 100,  # Anzahl der Schlüsselwörter, die maximal gespeichert werden sollen
    'min_df': 5,   # Minimale Dokumentfrequenz für Wörter
    'max_df': 0.8, # Maximale Dokumentfrequenz für Wörter (als Anteil)
    'bar_length': 50  # Länge des Fortschrittsbalkens
}

# Datenbank-Zugangsdaten
username = 'admin'
password = 'admin'
host = 'localhost'
port = '27017'
authSource = 'admin'


# Verbindung zur MongoDB
client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}')
db = client.web_articles
articles_collection = db.articles

# Alle Artikel abrufen
articles_cursor = articles_collection.find({}, {'preprocessed_text': 1, '_id': 1})
all_texts = []
article_ids = []
word_counts = []

# Texte und IDs sammeln und Wortzählung durchführen
for article in articles_cursor:
    text = article['preprocessed_text']
    if text.strip():  # Überprüfen, ob der Text nicht leer ist
        all_texts.append(text)
        article_ids.append(article['_id'])
        word_counts.append(len(set(text.split())))  # Zählen der einzigartigen Wörter

# TF-IDF-Vectorizer initialisieren mit Häufigkeitsfiltern
vectorizer = TfidfVectorizer(stop_words=config['stop_words'], min_df=config['min_df'], max_df=config['max_df'])
tfidf_matrix = vectorizer.fit_transform(all_texts)
feature_names = np.array(vectorizer.get_feature_names_out())

# Schlüsselwörter für jeden Artikel identifizieren und speichern
for i, (article_id, word_count) in enumerate(zip(article_ids, word_counts)):
    tfidf_scores = tfidf_matrix[i, :].toarray().flatten()
    sorted_indices = np.argsort(tfidf_scores)[::-1]

    # Anpassen der Anzahl der Schlüsselwörter basierend auf der Wortanzahl
    max_keywords = min(word_count, config['n_keywords'])
    top_n_indices = sorted_indices[:max_keywords]
    top_n_words = feature_names[top_n_indices]

    articles_collection.update_one(
        {'_id': article_id},
        {'$set': {'zipf_luhn_keywords': top_n_words.tolist()}}
    )

    progress = (i + 1) / len(article_ids)
    filled_length = int(round(config['bar_length'] * progress))
    bar = '#' * filled_length + '-' * (config['bar_length'] - filled_length)
    print(f'\r[{bar}] {round(progress*100, 2)}%', end='')

print("\nFertig mit der Verarbeitung aller Artikel.")
