## Erklärung der Änderungen
1. Verbindungsaufbau: Das Skript stellt eine Verbindung zu MongoDB her.
2. Fortschrittsanzeige: Eine Funktion print_progress wurde hinzugefügt, um den Fortschritt der Verarbeitung anzuzeigen.
3. Datum vereinheitlichen: 
- Die Funktion preprocess_date bereitet die Datumszeichenfolge vor, indem sie bestimmte Zeichen entfernt oder ersetzt.
- Die Funktion convert_date_format konvertiert die vorbereitete Datumszeichenfolge in das ISO 8601 Format. Falls das Datum ungültig ist, wird ein Standarddatum (1970-01-01T00:00:00Z) gesetzt.
4. Dokumente aktualisieren: Das Skript iteriert über alle Dokumente in der Sammlung und aktualisiert die publish_date und last_modified_date Felder, wenn sie vorhanden sind.
