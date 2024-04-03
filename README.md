# JoliNu-Market-Pulse-Predictor
## Wir sammeln Daten über Boeing und wollen mir NLP was cooles machen. 


## Vorgehen

### 1. Links zu Onlineartikeln über "Boeing" wurden gescraped 

- [CNBC](cnbc/cnbc_link_crawler.py)

- [NASDAQ](nasdaq/extractLink.py)

- [Reuters](reuters/reuters_link_crawler.py)

Die Skripte gehen jeweils auf die Onlineplattform und wenden deren Suchfunktion an. Meist kann dies durch verändern der URL durchgeführt werden. 

Beispiel: https://www.cnbc.com/search/?query=boeing&qsearchterm=boeing <- wobei Boeing der Suchbegriff ist

Die gesammelten Links werden in Listen gespeichert, welche von den Text-Crawlern später weiterverwendet werden.



### 2. Onlineartikel und Metadaten herunterladen 
Da jede Website eine andere vorgehensweise in der Anzeige ihrer Artikel verwendet, gehem die jeweiligen Cawler unterschiedlich vor. 

Für jeden Artikel werden Folgende Daten gespeichert:

|       Bezeichnung      |   Beschreibung                        |
|------------------------|---------------------------------------|         
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


#### 2.1 [CNBC](cnbc/cnbc_text_crawler.py)
Der CNBC Crawler verwendet die eingebettete JSON, welche beim Aufruf eines Artikels geladen wird. Die JSON ist im HTML-Code der Artikel eingebettet und wird z.B. mithilfe von RegEx daraus extrahiert. 
<p align="center">
<img src="screenshots\cnbc_json.png" width="512"/>
</p>
Um die eingebettete JSON zu finden wird nach dem tag *window.__s_data* gesucht.

Die extrahierten Artikel und deren Metadaten werden allesamt in einer neuen JSON gespeichert. [cnbc\CNBC_articles.json]


#### 2.2 [NASDAQ](nasdaq/downloadArtikel.py)


#### 2.3 [Reuters](reuters/reuters_text_crawler.py)


- Die JSONS von CNBC, Reutes und NASDAQ wurden gesammelt in eine MongoDB überfürt. (MongoDB/ArticleJSON_to_MongoDB.py)

- Datumsformate wurden angeglichen (MongoDB/date_preprocessing.py)

- Texte wurden Vorverarbeitet



