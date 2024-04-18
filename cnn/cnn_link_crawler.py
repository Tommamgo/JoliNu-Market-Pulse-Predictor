import requests
import time
import random
import json
import uuid

# Variablen für die Konfiguration
base_url = "https://search.prod.di.api.cnn.io/content"
query = "Boeing"
batch_size = 10
user_agents_file = "cnn/userAgents.txt"
output_file = "cnn/scraped_links.json"

def load_user_agents(filename):
    with open(filename, "r") as file:
        agents = [line.strip() for line in file.readlines()]
    print("User-Agents geladen.")
    return agents

def get_initial_data(user_agent):
    headers = {
        "Accept": "*/*",
        "User-Agent": user_agent
    }
    params = {
        "q": query,
        "size": 1,
        "request_id": str(uuid.uuid4())  # Generiere eine zufällige UUID für die Anfrage
    }
    response = requests.get(base_url, headers=headers, params=params)
    data = response.json()
    print(f"Erste Daten abgerufen: {data['meta']['of']} Datensätze gefunden.")
    return data

def print_progress(current, total):
    progress_length = 30
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}%", end="")

def scrape_articles(total_size, user_agents):
    results = []
    num_batches = (total_size // batch_size) + (1 if total_size % batch_size != 0 else 0)
    print(f"Beginne das Scraping von insgesamt {num_batches} Batches.")

    for batch_num in range(num_batches):
        headers = {
            "Accept": "*/*",
            "User-Agent": random.choice(user_agents),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }
        params = {
            "q": query,
            "size": batch_size,
            "from": batch_num * batch_size,
            "page": batch_num + 1,
            "sort": "newest",
            "request_id": str(uuid.uuid4())  # Jeder Batch erhält eine eigene request_id
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        data = response.json()
        results.extend(data.get("result", []))
        
        print_progress(batch_num + 1, num_batches)

        # Speichere alle 4 Batches
        if (batch_num + 1) % 4 == 0 or batch_num == num_batches - 1:
            with open(output_file, "w") as f:
                json.dump(results, f)
            print(f"\nZwischenspeicherung durchgeführt nach Batch {batch_num + 1}.")
        
        time.sleep(random.randint(5, 15))

    return "\nScraping abgeschlossen!"

if __name__ == "__main__":
    user_agents = load_user_agents(user_agents_file)
    initial_data = get_initial_data(random.choice(user_agents))
    total_size = initial_data['meta']['of']
    scrape_status = scrape_articles(total_size, user_agents)
    print(scrape_status)
