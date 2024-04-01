import csv
import random
import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pathlib import Path

# Basis-URL festlegen
base_url = "https://www.reuters.com"

# Pfad zur CSV-Datei
csv_file_path = '/Users/jonas/Documents/Master/S2/Natural Language Processing/codes/git/JoliNu-Market-Pulse-Predictor/reuters/gesammelte_links.csv'



def save_article(articles_buffer, file_name="reuters_collected_articles.json"):
    # Path to the file
    file_path = Path(file_name)
    data = {"articles": {}}
    
    # Check if the file already exists
    if file_path.exists():
        # File exists, load the existing content
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                if "articles" not in data:
                    data["articles"] = {}
            except json.JSONDecodeError:
                data = {"articles": {}}

    for article in articles_buffer:
        title = article['title']
        data["articles"][title] = article
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

# Funktion zum Scrapen der Informationen von einem Artikel
def scrape_article(article_url):

    # Headless Browser-Optionen konfigurieren
    options = webdriver.FirefoxOptions()
    #options.add_argument("--headless")  # Firefox im Headless-Modus
    #options.add_argument("-private")
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 15)  # Maximal 10 Sekunden auf Elemente warten

    try:
        driver.get(article_url)
        
        # Autor extrahieren
        try:
            autoren_elemente = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[rel="author"]')))
            autoren = [element.text for element in autoren_elemente]
            autoren_str = ', '.join(autoren)
        except TimeoutException:
            autoren_str = "nan"

        # Titel extrahieren
        try:
            titel_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')))
            titel = titel_element.text
        except TimeoutException:
            titel = "nan"

        # Kategorie extrahieren
        try:
            kategorie_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label*="category"]')))
            kategorie = kategorie_element.text
        except TimeoutException:
            kategorie = "nan"

        # Erscheinungsdatum extrahieren
        try:
        # Erscheinungsdatum und Uhrzeit extrahieren
            datum_zeit_elemente = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'time[data-testid="Body"] .date-line__date___kNbY')))
            datum = datum_zeit_elemente[0].text if datum_zeit_elemente else 'nan'
            zeit = datum_zeit_elemente[1].text if len(datum_zeit_elemente) > 1 else 'nan'
            
            # Zusammenführen von Datum und Uhrzeit in einem String
            datetime_str = f"{datum} {zeit}"

            # Konvertieren in datetime Objekt ohne explizite Zeitzone
            # '%I:%M %p' verarbeitet die 12-Stunden Uhrzeit mit AM/PM
            #---datetime_obj = datetime.strptime(datetime_str, '%B %d, %Y %I:%M %p')
            # Konvertieren zu ISO 8601 Format
            #---datum_zeit = datetime_obj.isoformat()
    
        except TimeoutException:
            datum = "nan"
            zeit = "nan"

        # Text extrahieren
        try: # Ein Text ist in mehrere Paragraphen unterteilt
            paragraphs_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.article-body__paragraph__2-BtD')))
            # Extrahiere den Text aus jedem Paragraphen
            text = " ".join([paragraph.text for paragraph in paragraphs_elements])
            cutoffstart = re.sub(r'^.*?-\s', '', text)
            cleaned_text = re.sub(r'\s*, opens new tab\s*', ' ', cutoffstart)

        except NoSuchElementException:
            text = "nan"

        # Ausgabe der extrahierten Informationen
        extracted_info = {
            "publish_date": datetime_str,
            "keywords": kategorie,
            "authors": autoren_str,
            "title": titel,
            "text": cleaned_text,
            "link": article_url,
            "original_publisher":  "Reuters",
            "article_publisher": "Reuters",
            "search_word": "Boeing",
            "short_description": titel,
            "last_modified_date": datetime_str
            }

        print(titel)

    except Exception as e:
        print(f"Fehler beim Verarbeiten von {article_url}: {e}")
    
    finally:
        # Warte zwischen 2 und 8 Sekunden, um eine Überlastung des Servers zu vermeiden
        rt = random.randint(10, 45)
        print(f"Es wird {rt} Sekunden gewartet")
        time.sleep(rt)
        driver.quit()
        return extracted_info


all_extracted_data = []  # Liste zum Speichern aller extrahierten Daten
counter = 0

# CSV-Datei lesen und jeden Link scrapen
try:
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        link_reader = csv.reader(csvfile)
        for row in link_reader:
            full_url = base_url + row[0]
            print(counter)
            article_data = scrape_article(full_url)
            if article_data:
                all_extracted_data.append(article_data)
                counter += 1
                # Zwischenspeichern alle 20 Artikel
                if counter % 10 == 0:
                    save_article(all_extracted_data)
                    all_extracted_data = []  # Reset der Liste nach dem Speichern

except Exception as ex:
    print(ex)      
#finally:
#    driver.quit()

# Speichern der verbleibenden Daten, falls weniger als 20 übrig sind
if all_extracted_data:
    save_article(all_extracted_data)
    print("Data collection completed.")
