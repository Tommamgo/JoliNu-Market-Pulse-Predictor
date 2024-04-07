from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import csv

def read_links_from_csv(csv_filename):
    links = []
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Füge nur den Link zur Liste hinzu
            links.append(row['Link'])
    return links



def start(name): 
    # Konfiguriere Selenium, um Firefox im Headless-Modus zu verwenden
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Headless-Modus aktivieren

    # Pfad zum GeckoDriver
    webdriver_path = './../linux/geckodriver'  # Aktualisiere diesen Pfad

    # Initialisiere den WebDriver
    service = Service(executable_path=webdriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    
    links = read_links_from_csv("./data/nasdaqLinks" + name + ".csv")
    for link in links: 
        # Navigiere zur URL
        driver.get(link)

        # Warte, bis die Seite geladen ist (hier könntest du explizit auf Elemente warten)
        driver.implicitly_wait(10)  # Wartet bis zu 10 Sekunden

        # Extrahiere den gesamten Seiteninhalt
        content = driver.page_source

        # Erstellen einer Datei um die Daten zu speichern
        filename = "./data/nasdaqArtikel/" + name + "/" + str(counter) + name + "Artikel.html"
        # Öffne die Datei zum Schreiben und speichere den Inhalt
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)

        print("Download: " + link)  # Zeige den Inhalt in der Konsole an

    # Beende den WebDriver und schließe das Browserfenster
    driver.quit()