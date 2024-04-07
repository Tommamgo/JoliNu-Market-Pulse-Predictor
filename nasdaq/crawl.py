import downloadSearch as nqSearch
import extractLink as nqExLinks
import downloadArtikel as nqArtikel
import extractAktikel as nqExAr  # "extractAktikel" sollte wahrscheinlich "extractArtikel" sein, wenn es ein Tippfehler ist.

def startCrawling(name): 
    # Wir holen uns alle möglichen Links von der Suchseite.
    nqSearch.setUp(name)
    nqExLinks.extractLinks(name)  # Wir extrahieren alle Links aus den zuvor heruntergeladenen Suchergebnissen.
    nqArtikel.start(name)  # Jetzt laden wir alle Artikel herunter.
    nqExAr.start(name)  # Nun holen wir alle Informationen und speichern diese in einer JSON-Datei.
