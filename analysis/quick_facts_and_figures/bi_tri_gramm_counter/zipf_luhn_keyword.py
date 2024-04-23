from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Konfigurationseinstellungen
config = {
    'db_username': 'admin',
    'db_password': 'admin',
    'db_host': 'localhost',
    'db_port': '27017',
    'db_auth_source': 'admin',
    'stop_words': 'english',  # Stopwörter für Englisch
    'n_keywords': 20,  # Anzahl der Schlüsselwörter, die gespeichert werden sollen
    'min_df': 5,   # Minimale Dokumentfrequenz für Wörter
    'max_df': 0.8, # Maximale Dokumentfrequenz für Wörter (als Anteil)
    'bar_length': 50  # Länge des Fortschrittsbalkens
}

# Verbindung zur MongoDB
client = MongoClient(f'mongodb://{config["db_username"]}:{config["db_password"]}@{config["db_host"]}:{config["db_port"]}/?authSource={config["db_auth_source"]}')
db = client.web_articles
articles_collection = db.articles

# Alle Artikel abrufen
articles_cursor = articles_collection.find()
all_texts = []
article_ids = []

# Texte und IDs sammeln
for article in articles_cursor:
    all_texts.append(article['preprocessed_text'])
    article_ids.append(article['_id'])

# TF-IDF-Vectorizer initialisieren mit Häufigkeitsfiltern
vectorizer = TfidfVectorizer(stop_words=config['stop_words'], min_df=config['min_df'], max_df=config['max_df'])
tfidf_matrix = vectorizer.fit_transform(all_texts)
feature_names = np.array(vectorizer.get_feature_names_out())

# Schlüsselwörter für jeden Artikel identifizieren und speichern
for i, article_id in enumerate(article_ids):
    tfidf_scores = tfidf_matrix[i, :].toarray().flatten()
    sorted_indices = np.argsort(tfidf_scores)[::-1]

    top_n_indices = sorted_indices[:config['n_keywords']]
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
