from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
# Warten auf das Element, das durch JavaScript geladen wird. Hier warte ich explizit auf ein bestimmtes Element.
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

    
def startDownloadFile(url01, url02, counter:int, name, driver):

    # Navigiere zur URL
    driver.get(url01 + str(counter) + url02)

    # Warte, bis die Seite geladen ist (hier könntest du explizit auf Elemente warten)
    driver.implicitly_wait(10)  # Wartet bis zu 10 Sekunden

    # Extrahiere den gesamten Seiteninhalt
    content = driver.page_source

    # Erstellen einer Datei um die Daten zu speichern
    filename = "./data/nasdaqSearch/" + name + "/" + str(counter) + "search" + ".html"
    try:         
        # Öffne die Datei zum Schreiben und speichere den Inhalt
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except: 
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Erstelle das Verzeichnis
        with open(filename, 'w', encoding='utf-8') as file:  # Versuche erneut zu öffnen
            file.write(content)


    print("Download: " + url01 + str(counter) + url02)  # Zeige den Inhalt in der Konsole an



def get_search_results(driver, url_1, url_2):
    url = url_1 + str(1) + url_2  # URL anpassen
    print(url)
    try:
        # URL laden
        driver.get(url)

        # WebDriverWait und EC verwenden, um auf die Sichtbarkeit eines Elements zu warten
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "search-results__results-numbers"))
        )
        
        # Extrahiere den Text des Elements
        results_text = element.text.strip()
        print("Gefundene Ergebnisse: ", results_text)
            # Aufspalten des Textes in Teile
        parts = results_text.split()
        return parts[2]
        
    except Exception as e:
        print("Ein Fehler ist aufgetreten:", e)


def buildURL(name): 
    url01_temp = "https://www.nasdaq.com/search?q="
    url01_temp += name
    url01_temp += "&page=" 

    return url01_temp


'''Mit dieser Funktion werden alle benötigten Module und Objekte geladen
    als diese Funktion benötigt den name des Unternehmnes als Eingabeparamter'''
def setUp(name): 
    # Konfiguriere Selenium, um Firefox im Headless-Modus zu verwenden
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Headless-Modus aktivieren
    # Pfad zum GeckoDriver
    webdriver_path = './../linux/geckodriver'  # Aktualisiere diesen Pfad

    # Initialisiere den WebDriver
    service = Service(executable_path=webdriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)

    # URL, die gescrapet werden soll
    url01 = "https://www.nasdaq.com/search?q=boeing&page=" 
    url02 = "&langcode=en"
    url01 = buildURL(name)
    
    # couter searchresults 
    pages = 0

    print("NASDAQ - start")
    pages = int(get_search_results(driver, url01, url02))
    
    # nächster Schritte alle Seiten und die Links holen
    startDownlaod(name, pages, url01, url02, driver)
    
    # Beende den WebDriver und schließe das Browserfenster
    driver.quit()


def startDownlaod(name, pageCounter, url_1, url_2, dirver): 
    for i in range(0, pageCounter):
        startDownloadFile(url01=url_1, url02=url_2, counter=i, name=name, driver=dirver)





# setUp("Tesla")
