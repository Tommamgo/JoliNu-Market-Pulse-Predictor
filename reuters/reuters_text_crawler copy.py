from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.common.by import By

import time
import random

'''
#________________________________________________________________________
# Nur wenn Firefox verwendet werden soll
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Benutzerdefinierten User-Agent String festlegen
CUSTOM_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# FirefoxOptions instanzieren
options = FirefoxOptions()

# Den User-Agent im Firefox durch Options ändern
options.set_preference("general.useragent.override", CUSTOM_USER_AGENT)
#options.add_argument("--headless")

# Für lokale WebDriver-Sitzungen, Firefox direkt instanziieren:
driver = webdriver.Firefox(options=options)
#________________________________________________________________________
'''

#_____________________________________________
# Nur wenn Safari verwendet werden soll
driver = webdriver.Safari()
#_____________________________________________


# URL des Artikels
url = "https://www.reuters.com/business/aerospace-defense/airbus-open-second-china-assembly-line-finalises-jet-order-2023-04-06/"
searchString = "Boeing"
article_publisher = "Reuters"
original_publisher = "Reuters"

# Öffne die Webseite
driver.get(url)

# Warte einen Moment, um sicherzustellen, dass die Seite geladen ist
driver.implicitly_wait(5)


# Autor extrahieren
try:
    # Verwende find_elements, um eine Liste aller Elemente zu erhalten, die dem Selector entsprechen
    autoren_elemente = driver.find_elements(By.CSS_SELECTOR, '[rel="author"]')
    # Extrahiere den Text jedes Elements und speichere die Namen in einer Liste
    autoren = [element.text for element in autoren_elemente]
    # Verwende join(), um die Liste in einen String umzuwandeln, falls mehrere Autoren vorhanden sind
    autoren_str = ', '.join(autoren)
except NoSuchElementException:
    autoren_str = "Autoren nicht gefunden"


# Titel extrahieren
try:
    # Versuche, das Element mit dem ersten Selector zu finden
    titel_element = driver.find_element(By.CSS_SELECTOR, '[class="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_3__1kDhc heading__base__2T28j heading__heading_3__3aL54"]')
except NoSuchElementException:
    titel = "Titel nicht gefunden"
titel = titel_element.text


# Abteilung / Bereich extrahieren
try:
    bereich_element= driver.find_element(By.CSS_SELECTOR, '[class="text__text__1FZLe text__dark-grey__3Ml43 text__regular__2N1Xr text__extra_small__1Mw6v link__link__3Ji6W link__underline_on_hover__2zGL4 tags-with-tooltip__link__3Mb0Y"]')
except NoSuchElementException:
    bereich = "Bereich nicht gefunden"
bereich = bereich_element.text

try:
    # Versuche, das Element zu finden, das die Kategorie oder das Keyword enthält
    kategorie_element = driver.find_element(By.CSS_SELECTOR, 'a[aria-label*="category"]')
    kategorie = kategorie_element.text
except NoSuchElementException:
    kategorie = "Kategorie nicht gefunden"



# Erscheinungsdatum und Uhrzeit extrahieren
datum_zeit_elemente = driver.find_elements(By.CSS_SELECTOR, 'time[data-testid="Body"] .date-line__date___kNbY')
datum = datum_zeit_elemente[0].text if datum_zeit_elemente else 'Datum nicht gefunden'
zeit = datum_zeit_elemente[1].text if len(datum_zeit_elemente) > 1 else 'Zeit nicht gefunden'


# Text extrahieren
try: # Ein Text ist in mehrere Paragraphen unterteilt
    paragraphs_elements = driver.find_elements(By.CSS_SELECTOR, 'div.article-body__paragraph__2-BtD')
except NoSuchElementException:
    bereich = "Text nicht gefunden"

# Extrahiere den Text aus jedem Paragraphen
text = " ".join([paragraph.text for paragraph in paragraphs_elements])
    

# Ausgabe der extrahierten Informationen
print("Autor:", autoren_str)
print("Titel:", titel)
print("Abteilung:", bereich)
print("Datum:", datum)
print("Zeit:", zeit)
#print("Text:", text)
print("keyWords:", kategorie)

# WebDriver schließen
driver.quit()
