import os
import shutil
from bs4 import BeautifulSoup
import json
from pathlib import Path

BUFFER_SIZE = 1000  # Anzahl der Artikel, die im Speicher gehalten werden, bevor sie gespeichert werden

# Definieren der Quell- und Zielverzeichnisse
source_directory_path = './data/nasdaqArtikel/'
target_directory_path = './data/missingContent/'


# Globale Variable für Zwischenspeicherung der Artikel
articles_buffer = []

def flush_articles_to_file(file_name="collected_articles.json"):

    
    file_path = Path(file_name)
    data = {"articles": {}}
    
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                if "articles" not in data:
                    data["articles"] = {}
            except json.JSONDecodeError:
                data = {"articles": {}}
    
    # Füge Artikel aus dem Buffer zum 'data'-Dict hinzu
    for article in articles_buffer:
        title = article['title']
        if title not in data["articles"]:
            data["articles"][title] = article
        else:
            print(f"Artikel mit dem Titel '{title}' existiert bereits und wird nicht erneut hinzugefügt.")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    # Leere den Buffer nach dem Schreiben
    articles_buffer.clear()

def save_article(publish_date, keywords, authors, title, text, link, original_publisher, article_publisher, search_word, short_description, last_modified_date, file_name="collected_articles.json"):
    article = {
        "publish_date": publish_date,
        "keywords": keywords,
        "authors": authors,
        "title": title,
        "text": text,
        "link": link,
        "original_publisher": original_publisher,
        "article_publisher": article_publisher,
        "search_word": search_word,
        "short_description": short_description,
        "last_modified_date": last_modified_date
    }

    # Füge den Artikel zum globalen Buffer hinzu
    articles_buffer.append(article)
    
    # Wenn der Buffer die festgelegte Größe erreicht, schreibe die Daten in die Datei
    if len(articles_buffer) >= BUFFER_SIZE:
        flush_articles_to_file(file_name)

# Diese Funktion sollte aufgerufen werden, wenn alle Artikel verarbeitet wurden, um sicherzustellen, dass alle verbleibenden Artikel im Buffer gespeichert werden.
def finalize_article_saving(file_name="collected_articles.json"):
    if articles_buffer:
        flush_articles_to_file(file_name)


def finde_autor(html_dokument):
    # Nach dem JSON-LD-Skript suchen, das die Autorinformationen enthält
    script_tag = html_dokument.find('script', type='application/ld+json')
    try: 
        if script_tag:
            import json
            data = json.loads(script_tag.string)  # Den JSON-String in ein Python-Dictionary umwandeln
            
            author_info = data.get('author', {}).get('name', 'Kein Autor gefunden')
            return author_info
        else:
            return "Kein Autorinformationen gefunden"
    except: 
        #print("Error")
        return "nan"


def extract_information(soup):
    # Versuch, den Reporter und die E-Mail-Adresse zu finden
    reporter_info = soup.find_all('p')
    for info in reporter_info:
        if 'Reporting by' in info.text or '@' in info.text:
            ##print(info.text.strip())
            if info.text.strip() == "":
                return "nan"
            else:
                return info.text.strip()


def extract_publisher_info(soup):
    # Initialisierung eines leeren Dictionaries für die Verlegerinformationen
    publisher_info = {
        "Publisher": "nan",
        "Publisher Bio": "nan"
    }

    # Versuchen, den Verleger zu finden
    publisher_link = soup.find('a', class_='jupiter22-c-text-link')
    if publisher_link:
        publisher_info["Publisher"] = publisher_link.text.strip()

    # Versuchen, die Biografie des Verlegers zu finden
    publisher_bio = soup.find('div', class_='jupiter22-c-article-bio-source__bio')
    if publisher_bio:
        publisher_info["Publisher Bio"] = publisher_bio.text.strip()

    # Rückgabe des Dictionaries mit den gesammelten Informationen
    return publisher_info


def extract_ld_json_info(soup):
    # Initialisieren eines leeren Wörterbuchs für die gesammelten Informationen
    extracted_info = {
        "Headline": "nan",
        "About": "nan",
        "Description": "nan",
        "Date Published": "nan",
        "Date Modified": "nan",
        "Main Entity Of Page": "nan"
    }

    # Suchen nach allen <script type="application/ld+json"> Tags
    script_tags = soup.find_all('script', {'type': 'application/ld+json'})
    for tag in script_tags:
        # Versuchen, den JSON-Inhalt zu parsen
        try:
            json_content = json.loads(tag.string)
            # Überprüfen, ob es sich um den gewünschten @graph handelt
            if '@graph' in json_content:
                for item in json_content['@graph']:
                    if item['@type'] == 'NewsArticle':
                        # Extrahieren und Speichern der relevanten Informationen
                        extracted_info["Headline"] = item.get('headline', 'nan')
                        extracted_info["About"] = item.get('about', 'nan')
                        extracted_info["Description"] = item.get('description', 'nan')
                        extracted_info["Date Published"] = item.get('datePublished', 'nan')
                        extracted_info["Date Modified"] = item.get('dateModified', 'nan')
                        extracted_info["Main Entity Of Page"] = item.get('mainEntityOfPage', 'nan')
                        # Sobald der erste passende Artikel gefunden wurde, Abbruch der Schleife
                        return extracted_info
        except json.JSONDecodeError:
            continue
    
    # Rückgabe des Wörterbuchs mit den extrahierten Informationen
    return extracted_info




def process_file(file_path, filename, name):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        article_body_content = soup.find('section', class_="jupiter22-c-article-body")

        if article_body_content:
            body_content = article_body_content.find('div', class_="body__content")
            if body_content:
                text_content = body_content.get_text(separator=" ", strip=True)
                text_content = text_content.replace('"', "'")
                reporterMail = extract_information(soup)  # Reporter-E-Mail extrahieren
                publisherInfo = extract_publisher_info(soup)  # Publisher-Infos extrahieren
                ldData = extract_ld_json_info(soup)  # JSON-LD Infos extrahieren
                
                # Daten für save_article vorbereiten
                publish_date = ldData["Date Published"]
                title = ldData["Headline"]
                description = ldData["Description"]
                last_modified_date = ldData["Date Modified"]
                main_entity_of_page = ldData["Main Entity Of Page"]
                original_publisher = publisherInfo["Publisher"]
                article_publisher = "Nasdaq"  # Angenommen, basierend auf der Quelle
                
                # Angenommene oder fehlende Werte
                keywords = ldData["About"]  # 'About' als Stellvertreter für Keywords
                authors = finde_autor(soup)  # ReporterMail als Stellvertreter für Autoren
                authors = authors.replace('"', "'")

                # Es kommt des oft vor dass der Artikel von einer anderen Webseite kommt und des aus diesem Grund keine Autor gibt
                if authors == "null" or authors == "" or authors == "nan":
                    authors = publisherInfo["Publisher"]
                    print("New Author: " + authors)

                search_word = title  # Titel als Stellvertreter für Suchwort
                short_description = description  # Description als Stellvertreter für kurze Beschreibung
                link = main_entity_of_page  # Main Entity Of Page als Stellvertreter für Link
                
                # Speichern der Artikelinformationen
                save_article(publish_date, keywords, [authors], title, text_content, link, original_publisher, article_publisher, search_word, short_description, last_modified_date, name + "Data.json")

                print(f"Daten für {filename} gespeichert.")
            else:
                shutil.move(file_path, os.path.join(target_directory_path + "/" + name , filename))
                print(f"{filename} wurde wegen fehlendem 'body__content' verschoben.")
        else:
            shutil.move(file_path, os.path.join(target_directory_path + "/" + name, filename))
            print(f"{filename} wurde wegen fehlendem 'jupiter22-c-article-body' Tag verschoben.")




def start(name):
    # Stellen Sie sicher, dass das Zielverzeichnis existiert
    os.makedirs(target_directory_path + "/" + name, exist_ok=True)     
    # Alle Dateien im Verzeichnis durchgehen
    for filename in os.listdir(source_directory_path + "/" + name):
        if filename.endswith(name + "Artikel.html"):
            file_path = os.path.join(source_directory_path + "/" + name, filename)
            process_file(file_path, filename, name)


