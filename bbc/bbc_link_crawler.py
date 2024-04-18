import requests
import time
import random
import json
import os

# Variablen für die Konfiguration
base_url = "https://web-cdn.api.bbci.co.uk/xd/search"
query = "Boeing"
total_pages = 1112  # Gesamtzahl der Seiten
user_agents_file = "bbc/userAgents.txt"
output_file = "bbc/bbc_scraped_links.json"

min_delay = 5
max_delay = 8

def load_user_agents(filename):
    try:
        with open(filename, "r") as file:
            agents = [line.strip() for line in file.readlines()]
        return agents
    except FileNotFoundError:
        print("User-Agent-Datei nicht gefunden.")
        return ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"]

def load_existing_data():
    if os.path.exists(output_file):
        with open(output_file, "r") as file:
            data = json.load(file)
            return data.get("results", []), data.get("last_page", 0)
    else:
        return [], 0

def get_page_data(page_number, user_agent):
    params = {
        "terms": query,
        "page": page_number
    }
    headers = {
        "User-Agent": user_agent
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def print_progress(current, total):
    progress_length = 30
    percent_complete = current / total
    bars = int(progress_length * percent_complete)
    progress_bar = '#' * bars + '-' * (progress_length - bars)
    print(f"\r[{progress_bar}] {int(100 * percent_complete)}% {current} / {total}", end="")

def save_data(results, last_page):
    data = {
        "results": results,
        "last_page": last_page
    }
    with open(output_file, "w") as f:
        json.dump(data, f)
    print(f"\nDaten gespeichert nach Seite {last_page}.")

def scrape_articles(user_agents):
    results, last_loaded_page = load_existing_data()
    start_page = last_loaded_page + 1

    for page_number in range(start_page, total_pages + 1):
        user_agent = random.choice(user_agents)
        data = get_page_data(page_number, user_agent)
        if data and "data" in data:
            results.extend(data["data"])
        
        print_progress(page_number, total_pages)
        
        if page_number % 10 == 0:
            save_data(results, page_number)

        time.sleep(random.randint(min_delay, max_delay))

    save_data(results, total_pages)  # Sicherstellen, dass die endgültigen Daten gespeichert werden
    return "\nScraping abgeschlossen!"

if __name__ == "__main__":
    user_agents = load_user_agents(user_agents_file)
    print("Starte das Crawling der BBC-Suchergebnisse für 'Boeing'.")
    scrape_status = scrape_articles(user_agents)
    print(scrape_status)
