from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

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

for counter in range(1, 2100): 

    # Navigiere zur URL
    driver.get(url01 + str(counter) + url02)

    # Warte, bis die Seite geladen ist (hier könntest du explizit auf Elemente warten)
    driver.implicitly_wait(10)  # Wartet bis zu 10 Sekunden

    # Extrahiere den gesamten Seiteninhalt
    content = driver.page_source

    # Erstellen einer Datei um die Daten zu speichern
    filename = "./data/nasdaq_content" + str(counter) + ".html"
    # Öffne die Datei zum Schreiben und speichere den Inhalt
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

    print("Download: " + url01 + str(counter) + url02)  # Zeige den Inhalt in der Konsole an
    

# Beende den WebDriver und schließe das Browserfenster
driver.quit()

