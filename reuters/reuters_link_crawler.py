from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

driver = webdriver.Safari()
searchString= "boeing"

# Liste für die Links erstellen
links_list = []

# WebDriver für Safari initialisieren


try:
    # Webseite öffnen
    driver.get(f'https://www.reuters.com/site-search/?query={searchString}&offset=20')
    
    # Warten, um sicherzustellen, dass die Seite vollständig geladen ist
    time.sleep(2)
    
    # Element mit der Anzahl der Artikel finden 
    element = driver.find_element(By.CSS_SELECTOR, 'span.search-results__text__13FtQ')
    
    # Gesamtzahl der Artikel extrahieren und berechnen, wie viele Seiten besucht werden müssen
    total_articles = int(element.text.split()[-1])
    pages = -(-total_articles // 20)  # Aufrunden der Division

    for page in range(1, pages):
        
        if page > 2:  # Bei der ersten Seite sind wir bereits, keine Notwendigkeit die Seite neu zu laden
            driver.get(f'https://www.reuters.com/site-search/?query={searchString}&offset={page * 20}')
            time.sleep(5)
        
        # Alle Blöcke mit der angegebenen Klasse finden
        items = driver.find_elements(By.CSS_SELECTOR, 'li.search-results__item__2oqiX')
        for item in items:
            # Innerhalb jedes Items nach dem Link-Element suchen
            link_element = item.find_element(By.CSS_SELECTOR, 'div.basic-card__container__2c0tk.default')
            link = link_element.get_attribute('href')
            links_list.append(link)
        print(f'Es wird Seite {page} von {pages} auf Links von Artikeln untersucht!')


finally:
    # Browser schließen
    driver.quit()

# Doppelt genannte Artikel entfernen
unique_links_list = list(set(links_list))

# Pfad zur CSV-Datei, die du erstellen möchtest
file_path = 'gesammelte_links.csv'

# CSV-Datei öffnen und Links schreiben
with open(file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Für jeden Link eine Zeile in der CSV-Datei erstellen
    for link in unique_links_list:
        writer.writerow([f"https://www.reuters.com{link}"])

print(f"Links wurden erfolgreich in {file_path} gespeichert.")


