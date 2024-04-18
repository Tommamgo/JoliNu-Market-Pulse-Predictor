from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
import numpy as np

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

# TF-IDF-Vectorizer initialisieren
vectorizer = TfidfVectorizer(stop_words='english')  # Stopwörter für Englisch, für andere Sprachen anpassen

# Funktion zur Verarbeitung eines Batches von Artikeln
def process_batch(batch_texts, batch_ids):
    try:
        # TF-IDF-Werte für den Batch berechnen
        tfidf_matrix = vectorizer.fit_transform(batch_texts)
        feature_names = np.array(vectorizer.get_feature_names_out())

        # Schlüsselwörter für jeden Artikel im Batch identifizieren
        for i, article_id in enumerate(batch_ids):
            # Sortiere TF-IDF-Scores
            tfidf_scores = tfidf_matrix[i, :].toarray().flatten()
            sorted_indices = np.argsort(tfidf_scores)[::-1]

            # Die Anzahl der Schlüsselwörter festlegen, z.B. die Top 10 Wörter
            n_keywords = 10
            top_n_indices = sorted_indices[:n_keywords]
            top_n_words = feature_names[top_n_indices]

            # Schlüsselwörter in der neuen Spalte 'zipf_luhn_keywords' speichern
            articles_collection.update_one(
                {'_id': article_id},
                {'$set': {'zipf_luhn_keywords': top_n_words.tolist()}}
            )
    except Exception as e:
        print(f"Ein Fehler trat auf während der Verarbeitung des Batches: {e}")

# Artikel aus MongoDB abrufen und in Batches verarbeiten
batch_size = 100  # Festlegung der Batch-Größe
articles_cursor = articles_collection.find()
total_articles = articles_collection.count_documents({})
processed_articles = 0

# Fortschrittsbalken initialisieren
def print_progress_bar(progress):
    bar_length = 50  # Ändern Sie dies für eine längere oder kürzere Leiste
    filled_length = int(round(bar_length * progress))
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r[{bar}] {round(progress*100, 2)}%', end='')

# Verarbeiten der Artikel in Batches
while processed_articles < total_articles:
    batch_texts = []
    batch_ids = []
    for _ in range(batch_size):
        try:
            article = next(articles_cursor)
            batch_texts.append(article['text'])
            batch_ids.append(article['_id'])
        except StopIteration:
            break  # Keine weiteren Dokumente zum Verarbeiten

    process_batch(batch_texts, batch_ids)
    processed_articles += len(batch_texts)
    
    # Fortschrittsbalken aktualisieren
    print_progress_bar(processed_articles / total_articles)

print("\nFertig mit der Verarbeitung aller Artikel.")
