# JoliNu-Market-Pulse-Predictor

## Wir sammeln Daten über Boeing und wollen mir NLP was cooles machen.

[screenshots\flugzeug_nlp.png]

### 1. Links zu Onlineartikeln über "Boeing" wurden gescraped 

- [CNBC](cnbc/cnbc_link_crawler.py)

- [NASDAQ](nasdaq/extractLink.py)

- [Reuters](reuters/reuters_link_crawler.py)

Die Skripte gehen jeweils auf die Onlineplattform und wenden deren Suchfunktion an. Meist kann dies durch verändern der URL durchgeführt werden. 

Beispiel: https://www.cnbc.com/search/?query=boeing&qsearchterm=boeing <- wobei Boeing der Suchbegriff ist

Die gesammelten Links werden in Listen (z.B. [cnbc/CNBC_links.json](cnbc/CNBC_links.json)) gespeichert, welche von den Text-Crawlern später weiterverwendet werden.

---

### 2. Onlineartikel und Metadaten herunterladen 
Da jede Website eine andere vorgehensweise in der Anzeige ihrer Artikel verwendet, gehem die jeweiligen Cawler unterschiedlich vor. 

Für jeden Artikel werden Folgende Daten gespeichert:

|       Bezeichnung      |   Beschreibung                        |
|:----------------------:|---------------------------------------|         
| **keywords**           | Enthält Schlüsselwörter wie z.B. Ressort (Finanzen und Dienstleistungen) |
| **authors**            | Enthält eine Liste der Autoren |
| **title**              | Titel des Onlineartikels |
| **text**               | Text / Content des Artikels |
| **link**               | Link zum Artikel |
| **original_publisher** | Wenn sich der Artikel auf eine andere Quelle beruft, dann ist diese hier enthalten. Ansonsten gleich zu article_publisher |
| **article_publisher**  | Die Plattform, von der gescrapte Artikel heruntergeladen wurde |
| **search_word**        | Das verwendete Suchwort, in diesem Projek "Boeing"
| **short_description**  | Kurzbeschreibung des Artikels. Ansonsten gleich zu title
| **last_modified_date** | Letztes Änderungsdatum. Ansonsten Veröffentlichungsdatum | 

Die durch die Crawler resultierende JSON mit allen Artileln sieht demnach wiefolgt aus:

```json
{
    "articles": {
        "Boeing CEO to step down in broad management shake-up as 737 Max crisis weighs on aerospace giant": {
            "publish_date": "2024-03-25T12:00:25+0000",
            "keywords": [
                "Industrials",
                "Business News"
            ],
            "authors": [
                "Leslie Josephs",
                "Phil LeBeau",
                "Meghan Reeder"
            ],
            "title": "Boeing CEO to...",
            "text": "Boeing CEO Dave Calhoun will step ...",
            "link": "https://www.cnbc....",
            "original_publisher": "CNBC.com",
            "article_publisher": "CNBC",
            "search_word": "Boeing",
            "short_description": "Boeing CEO Dave Calhoun ...",
            "last_modified_date": "2024-03-25T20:45:18+0000"
        },
        .
        .
        .
    }
}
```


#### 2.1 [CNBC](cnbc/cnbc_text_crawler.py) Artikel Crawler
Der CNBC Crawler verwendet die eingebettete JSON, welche beim Aufruf eines Artikels geladen wird. Die JSON ist im HTML-Code der Artikel eingebettet und wird z.B. mithilfe von RegEx daraus extrahiert. 
<p align="center">
<img src="screenshots\cnbc_json.png" width="512"/>
</p>
Um die eingebettete JSON zu finden wird nach dem tag *window.__s_data* gesucht.

Die extrahierten Artikel und deren Metadaten werden allesamt in einer neuen JSON gespeichert. [cnbc/CNBC_articles.json]


#### 2.2 [NASDAQ](nasdaq/downloadArtikel.py) Artikel Crawler



#### 2.3 [Reuters](reuters/reuters_text_crawler.py) Artikel Crawler
Der Reuters Crawler kann aufgrund von redirects und eingebettetem javaScript nicht direkt auf die HTML Datei der Artikel zugreifen. Aufgrun dessen muss mittels selenium automationen jeder Artikel vollständig in einem Browser geladen werden, sodass auch die eingebetteten javaScript Funktionen ausgeführt werden. Erst danach kann die HTML des Artikels auf die geforderten Elemente untersucht werden. 

Im Beispiel wird *presence_of_all_elements_located* von selenium verwendet, um nach dem Laden der Seite alle Inhalte aus *[rel="author"]* zu extrahieren.

```python
try:
            autoren_elemente = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[rel="author"]')))
            autoren = [element.text for element in autoren_elemente]
            autoren_str = ', '.join(autoren)
        except TimeoutException:
            autoren_str = "nan"
```
Anschließend werden auch hier alle gefundenen Artikel und Metadaten in einer JSON zusammengefasst. [reuters/reuters_articles.json]

---

### 3. MongoDB zur Speicherung aller Artikel und Metadaten
Um mit der Masse an Artikeln einheitlich und performant arbeiten zu können, werden diese in einer MongoDB abgelegt. Verwendet wird hierfür das [klassische MongoDB Docker Image](https://hub.docker.com/_/mongo). 
Als grafische Benutzeroberfläche für die Datenbank wird ebenfalls das [Mongo-Express Image](https://hub.docker.com/_/mongo-express) installiert. 

Da eine einheitliche Verwendung der Datenbank unter den verschiedenen Entwicklern angestrebt wird, wurde eine *docer-compose.yml* zum Starten und Stoppen der Datenbank angefertig. Diese Compose Datei, als auch die vollständige Datenbank sind in diesem Repository [hier](mongoDB/docker-compose.yml) zu finden. 

---

## Was ist sonst noch so passiert???

* Texte wurden in Mongo geladen [mongoDB/ArticleJSON_to_MongoDB.py]

* Datumsformate wurden angeglichen [mongoDB/date_preprocessing.py]

* Texte wurden Vorverarbeitet [mongoDB/Text_Preprocessing.py]

..* Worthäufigkeiten wurden gezählt [mongoDB/Keyword_Counter.py]

..* Wortkombinationen wurden gezählt [mongoDB/nGramCounter.py]

..* [Jonas ist cool](https://de.wikipedia.org/wiki/Wurmautomat)

