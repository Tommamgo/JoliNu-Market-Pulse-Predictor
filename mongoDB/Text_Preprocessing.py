from pymongo import MongoClient
import spacy

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
    for document in cursor:
        # Extrahiere den Text des Dokuments
        text = document.get("text", "")
        # Führe die Textvorverarbeitung durch
        processed_text = preprocess_text(text)
        # Aktualisiere das Dokument mit dem neuen Feld "processed_text"
        collection.update_one({"_id": document["_id"]}, {"$set": {"preprocessed_text": processed_text}})
finally:
    cursor.close()  # Stelle sicher, dass der Cursor ordnungsgemäß geschlossen wird

print("Textvorverarbeitung abgeschlossen.")
