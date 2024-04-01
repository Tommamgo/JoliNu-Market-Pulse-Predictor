import json

def transform_articles(file_path):
    # Versuchen, die Datei zu öffnen und den Inhalt zu lesen
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            articles_data = json.load(file)

        # Bearbeitung der Daten, um die gewünschte Struktur zu erstellen
        transformed_articles = {"articles": {}}

        for article_batch in articles_data:
            for article in article_batch:
                # Prüfen, ob der Text "nan" enthält und überspringen, falls ja
                if article["text"] != "nan":
                    transformed_articles["articles"][article["title"]] = article

        # Speichern der umgewandelten Daten in einer neuen Datei
        transformed_file_path = file_path.replace('.json', '_transformed.json')
        with open(transformed_file_path, 'w', encoding='utf-8') as new_file:
            json.dump(transformed_articles, new_file, indent=4, ensure_ascii=False)

        print(f"Die umgewandelten Daten wurden erfolgreich in {transformed_file_path} gespeichert.")

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

# Beispielhafter Dateipfad, den du entsprechend anpassen solltest
file_path = '/Users/jonas/Documents/Master/S2/Natural Language Processing/codes/git/JoliNu-Market-Pulse-Predictor/cnbc/old_data/old.json'
transform_articles(file_path)
