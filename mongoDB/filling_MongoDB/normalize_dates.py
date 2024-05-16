from pymongo import MongoClient
from dateutil import parser as date_parser
from datetime import datetime
import pytz
import re

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

