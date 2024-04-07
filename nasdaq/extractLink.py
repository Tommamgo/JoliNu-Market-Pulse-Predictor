import os
import csv
from bs4 import BeautifulSoup

def extract_links_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        for link in soup.find_all('a', class_='search-results__item', href=True):
            links.append(link['href'])
        return links

def extractLinks(name):
    folder_path = "data/nasdaqSearch/" + name + "/"  # Hier den Pfad zum Ordner mit den HTML-Dateien angeben
    
    # CSV-Datei zum Schreiben öffnen
    with open("data/nasdaqLinks" + name +".csv", 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Filename', 'Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for filename in os.listdir(folder_path):
            if filename.endswith('.html'):
                file_path = os.path.join(folder_path, filename)
                links = extract_links_from_file(file_path)
                print(f"Links aus {filename}:")
                for link in links:
                    print("https://www.nasdaq.com" + link)
                    # Link in CSV-Datei schreiben
                    writer.writerow({'Filename': filename, 'Link': "https://www.nasdaq.com" + link})
                print()

