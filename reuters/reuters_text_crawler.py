import csv
import random
import time
import json
import re
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from pathlib import Path


batch_size = 10

# Basis-URL festlegen
base_url = "https://www.reuters.com"

# Pfad zur CSV-Datei
csv_file_path = '/Users/jonas/Documents/Master/S2/Natural Language Processing/codes/git/JoliNu-Market-Pulse-Predictor/reuters/gesammelte_links.csv'

with open('/Users/jonas/Documents/Master/S2/Natural Language Processing/codes/git/JoliNu-Market-Pulse-Predictor/reuters/userAgents.txt', 'r') as file:
    user_agents = [line.strip() for line in file.readlines()]

def remove_top_line_from_csv(file_path, size):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines[size:])  # Schreibe alle Zeilen außer der ersten zurück in die Datei


def print_progress(current, total):
    progress_length = 50
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}% - Artikel {current} von {total}", end="")

def save_article(articles_buffer, file_name="reuters_articles.json"):
    c = 0
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

    for article in articles_buffer:
        c+=1
        title = article['title']
        data["articles"][title] = article

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f" -  {c} Artikel gespeichert!")

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    options.set_preference("permissions.default.image", 2)  # Kein Laden von Bildern
    #options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")  # Deaktiviert Flash
    #options.set_preference("privacy.trackingprotection.enabled", True)
    #options.set_preference("dom.enable_resource_timing", False)
    
    driver = webdriver.Firefox(options=options)
    driver.delete_all_cookies()
    return driver

def scrape_article(article_url):
    #options = webdriver.FirefoxOptions()
    #options.add_argument("--headless")
    #options.add_argument(f"--user-agent={random.choice(user_agents)}")
    #driver = webdriver.Firefox(options=options)
    driver = create_driver()
    wait = WebDriverWait(driver, 20)
    extracted_info = {}

    try:
        driver.get(article_url)

        # Extract elements as per the given CSS selectors and handle possible exceptions
        try:
            autoren_elemente = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[rel="author"]')))
            autoren = [element.text for element in autoren_elemente]
            autoren_str = ', '.join(autoren)
        except TimeoutException:
            autoren_str = "nan"

        try:
            titel_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')))
            titel = titel_element.text
        except TimeoutException:
            titel = "nan"

        try:
            kategorie_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label*="category"]')))
            kategorie = kategorie_element.text
        except TimeoutException:
            kategorie = "nan"

        try:
            datum_zeit_elemente = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'time[data-testid="Body"] .date-line__date___kNbY')))
            datum = datum_zeit_elemente[0].text if datum_zeit_elemente else 'nan'
            zeit = datum_zeit_elemente[1].text if len(datum_zeit_elemente) > 1 else 'nan'
            datetime_str = f"{datum} {zeit}"
            dt = parser.parse(datetime_str)
            date = dt.isoformat()   
        except TimeoutException:
            date = "nan"

        try:
            paragraphs_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.article-body__paragraph__2-BtD')))
            text = " ".join([paragraph.text for paragraph in paragraphs_elements])
            cutoffstart = re.sub(r'^.*?-\s', '', text)
            cleaned_text = re.sub(r'\s*, opens new tab\s*', ' ', cutoffstart)
        except NoSuchElementException:
            cleaned_text = "nan"

        extracted_info = {
            "publish_date": date,
            "keywords": kategorie,
            "authors": autoren_str,
            "title": titel,
            "text": cleaned_text,
            "link": article_url,
            "original_publisher": "Reuters",
            "article_publisher": "Reuters",
            "search_word": "Boeing",
            "short_description": titel,
            "last_modified_date": datetime_str
        }

    except Exception as e:
        print(f"Fehler beim Verarbeiten von {article_url}: {e}")
        return None

    rt = random.randint(5, 15)
    print(f" - Es wird {rt} Sekunden gewartet")
    time.sleep(rt)
    driver.quit()
    return extracted_info

all_extracted_data = []  # Liste zum Speichern aller extrahierten Daten
counter = 0
total_articles = sum(1 for row in csv.reader(open(csv_file_path, 'r', encoding='utf-8')))

try:
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        link_reader = csv.reader(csvfile)
        for row in link_reader:
            full_url = base_url + row[0]
            article_data = scrape_article(full_url)
            if article_data and article_data["text"] != "nan":
                all_extracted_data.append(article_data)
                counter += 1
                print_progress(counter, total_articles)
                if counter % batch_size == 0:
                    remove_top_line_from_csv(csv_file_path, batch_size)
                    save_article(all_extracted_data)
                    all_extracted_data = []
            else:
                print(f"Überspringe Artikel: https://www.reuters.com{row[0]}")

except Exception as ex:
    print(ex)

if all_extracted_data:
    save_article(all_extracted_data)
    print("Data collection completed.")
