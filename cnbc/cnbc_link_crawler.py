import requests
import json
import time
import random
import math

# Funktion zum Speichern der Daten
def save_data(all_data, filename='CNBC_links.json'):
    with open(filename, 'w') as file:
        json.dump(all_data, file, indent=4)
    print("Daten wurden erfolgreich zwischengespeichert.")

# URL und Basis-Parameter für die GET-Anfrage
url = "https://api.queryly.com/cnbc/json.aspx"
queryly_key = "31a35d40a9a64ab3"
batch_size = 10  # Stellen Sie sicher, dass dies der Batchsize Ihrer Anfrage entspricht
params = {
    "queryly_key": queryly_key,
    "query": "boeing",
    "batchsize": batch_size,
    "callback": "",
    "showfaceted": "false",
    "timezoneoffset": "-60",
    "facetedfields": "formats",
    "facetedkey": "formats|",
    "facetedvalue": "!Press Release|",
    "sort": "date",
    "additionalindexes": "4cd6f71fbf22424d,937d600b0d0d4e23,3bfbe40caee7443e,626fdfcd96444f28"
}

# Initialanfrage, um die Gesamtzahl der Ergebnisse zu ermitteln
response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    total_results = data['metadata']['totalresults']
    total_requests_needed = math.ceil(total_results / batch_size)

    all_data = []  # Sammeln aller Daten hier

    for endindex in range(0, total_requests_needed * batch_size, batch_size):
        # Parameter aktualisieren für jede Anfrage
        params['endindex'] = endindex
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data['results'])
            print(f"{int(endindex/batch_size)+1} von {total_requests_needed} Durchgängen ausgeführt. {len(all_data)} Artikel geladen.")
            
            # Speichern der Daten nach jeweils 100 geladenen Ergebnissen
            if len(all_data) % 100 == 0 or (int(endindex/batch_size)+1) == total_requests_needed:
                save_data(all_data)

            # Warten für eine zufällige Zeit zwischen 2 und 10 Sekunden
            wait_time = random.randint(2, 10)
            print(f"Warte {wait_time} Sekunden...")
            time.sleep(wait_time)
        else:
            print("Fehler bei der Anfrage:", response.status_code)
            break

    # Speichern der gesammelten Daten in einer Datei
    with open('CNBC_articles.json', 'w') as file:
        json.dump(all_data, file, indent=4)

    print("Gesamte Daten wurden erfolgreich heruntergeladen und gespeichert.")
else:
    print("Initialanfrage fehlgeschlagen:", response.status_code)