from pymongo import MongoClient
import random


def pull_random_article(db_name='web_articles', collection_name='articles', seed=None):
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
    db = client[db_name]
    collection = db[collection_name]

    # Wenn ein Seed angegeben ist, nutzen wir diesen, um die Zufälligkeit zu steuern
    if seed is not None:
        random.seed(seed)
        # Bestimme die Anzahl der Dokumente in der Sammlung
        count = collection.count_documents({})
        # Wähle eine zufällige Position basierend auf dem Seed
        random_position = random.randint(0, max(0, count - 1))
        # Finde das Dokument an der zufälligen Position
        document = collection.find().skip(random_position).limit(1).next()
    else:
        # MongoDB Aggregationspipeline, um ein zufälliges Dokument zu erhalten
        document = collection.aggregate([{'$sample': {'size': 1}}]).next()

    return document
