import requests
import os
import json

# Ziel-URL (anpassen!)
SERVER_URL = "http://error.taild6d121.ts.net:8000/api/fuellstand/" 
FUELLSTAND_DATEI = "/home/schambach/Trashy/fuellstand.json"
PI_ID_PATH = "/home/schambach/Trashy/pi_id.txt"

# PI-ID laden
try:
    with open(PI_ID_PATH, "r") as f:
        pi_id = f.read().strip()
except Exception as e:
    print("Fehler beim Laden der Pi-ID:", e)
    exit()

# Füllstand laden
if not os.path.exists(FUELLSTAND_DATEI):
    print("Füllstanddatei nicht gefunden.")
    exit()

try:
    with open(FUELLSTAND_DATEI, "r") as f:
        messung = json.load(f)  # gesamte Datei ist ein JSON-Objekt
except Exception as e:
    print("Fehler beim Einlesen der Füllstanddaten:", e)
    exit()

# Daten senden
try:
    response = requests.post(SERVER_URL, json={
        "pi_id": pi_id,
        "messung": messung
    }, timeout=10)

    print("Antwort:", response.status_code, response.text)

except Exception as e:
    print("Fehler beim Senden:", e)
