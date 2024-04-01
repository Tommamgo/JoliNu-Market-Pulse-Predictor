from pymongo import MongoClient
from dateutil import parser
import pytz
import re

# Ersetze diese Werte mit deinen eigenen Anmeldeinformationen
username = 'admin'
password = 'admin'
host = 'localhost'
port = '27017'
authSource = 'admin'

# Erstelle die Verbindungs-URI
mongo_uri = f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}'

# Verbinde dich mit MongoDB unter Verwendung der Authentifizierung
client = MongoClient(mongo_uri)

# Referenziere deine Datenbank und Collection
db = client['web_articles']
collection = db['articles']

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
