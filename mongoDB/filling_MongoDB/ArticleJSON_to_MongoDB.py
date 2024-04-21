from pymongo import MongoClient
import json
#-----------------------------------------
json_path = 'bbc/bbc_scraped_articles.json'
#-----------------------------------------

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

# Lade deine JSON-Daten
with open(json_path, 'r') as file:
    data = json.load(file)

# Konvertiere die Daten in ein Array von Dokumenten
articles = list(data['articles'].values())

# Füge die Dokumente in die MongoDB Collection ein
collection.insert_many(articles)

print("Dokumente erfolgreich eingefügt")
