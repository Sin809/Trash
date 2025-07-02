import requests
import os
from PIL import Image
import numpy as np
import tflite_runtime.interpreter as tflite
from datetime import datetime
import subprocess
import lgpio
import time
from drehscheibe import drehscheibe_positionieren
from fliessband import fliessband_drehen

#SERVER_URL = "http://error.taild6d121.ts.net:8000/api/upload/" #Andre Lokal Tailscale VPN
SERVER_URL = "http://[2001:7c0:2320:2:f816:3eff:fea9:8a61]:8000/api/upload/"
MODEL_PFAD = "/home/schambach/Trashy/Model/model_unquant.tflite"
LABELS_PFAD = "/home/schambach/Trashy/Model/labels.txt"
BILD_VERZEICHNIS = "/home/schambach/Trashy/Bilder/"
NICHT_GESENDET_VERZEICHNIS = os.path.join(BILD_VERZEICHNIS, "nicht_gesendet")
PI_ID_PATH = "/home/schambach/Trashy/pi_id.txt"

with open(PI_ID_PATH, "r") as f:
    PI_ID = f.read().strip()

interpreter = tflite.Interpreter(model_path=MODEL_PFAD)
interpreter.allocate_tensors()
input_index = interpreter.get_input_details()[0]["index"]
output_index = interpreter.get_output_details()[0]["index"]

# Labels ohne führende Nummern laden
with open(LABELS_PFAD, "r") as f:
    LABELS = [zeile.strip().split(" ", 1)[1] for zeile in f if " " in zeile]

TASTER_PIN = 25

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, TASTER_PIN, lgpio.SET_PULL_UP)

def klassifizieren(pfad):
    bild = Image.open(pfad).resize((224, 224))
    array = np.expand_dims(np.array(bild, dtype=np.float32) / 255.0, axis=0)
    interpreter.set_tensor(input_index, array)
    interpreter.invoke()
    output = interpreter.get_tensor(output_index)[0]

    index = int(np.argmax(output))
    wahrscheinlichkeit = round(float(output[index]) * 100)
    label = LABELS[index]

    print(f"[Klassifikation] Index: {index}, Label: {label}, Wahrscheinlichkeit: {wahrscheinlichkeit}%")

    return label, wahrscheinlichkeit

def sende_bild(pfad, bildname, label, datum, uhrzeit, wahrscheinlichkeit):
    try:
        with open(pfad, "rb") as datei:
            response = requests.post(SERVER_URL, files={
                "bild": (bildname, datei, "image/jpeg"),
            }, data={
                "label": label,
                "wahrscheinlichkeit": wahrscheinlichkeit,
                "datum": datum,
                "uhrzeit": uhrzeit,
                "pi_id": PI_ID
            }, timeout=10)

        if response.status_code == 200:
            print(f"Bild erfolgreich gesendet: {bildname}")
            return True
        else:
            print("Serverfehler:", response.status_code, response.text)
            return False
    except Exception as e:
        print("Fehler beim Senden:", e)
        return False

def versuche_ausstehende_bilder_zu_senden():
    os.makedirs(NICHT_GESENDET_VERZEICHNIS, exist_ok=True)
    for datei in sorted(os.listdir(NICHT_GESENDET_VERZEICHNIS)):
        if not datei.lower().endswith(".jpg"):
            continue

        teile = os.path.splitext(datei)[0].split("_")
        if len(teile) != 4:
            print("Ungültiger Dateiname:", datei)
            continue

        datum_raw, uhrzeit_raw, label, wahrscheinlichkeit_str = teile
        datum = f"{datum_raw[:4]}-{datum_raw[4:6]}-{datum_raw[6:]}"
        uhrzeit = f"{uhrzeit_raw[:2]}:{uhrzeit_raw[2:4]}:{uhrzeit_raw[4:]}"
        try:
            wahrscheinlichkeit = int(wahrscheinlichkeit_str)
        except ValueError:
            print("Ungültige Wahrscheinlichkeit:", wahrscheinlichkeit_str)
            continue

        pfad = os.path.join(NICHT_GESENDET_VERZEICHNIS, datei)
        neuer_pfad = os.path.join(BILD_VERZEICHNIS, datei)

        if sende_bild(pfad, datei, label, datum, uhrzeit, wahrscheinlichkeit):
            os.rename(pfad, neuer_pfad)
        else:
            print(f"erneuter Versuch fehlgeschlagen für: {datei}")

def aufnehmen_und_senden():
    os.makedirs(BILD_VERZEICHNIS, exist_ok=True)
    os.makedirs(NICHT_GESENDET_VERZEICHNIS, exist_ok=True)

    versuche_ausstehende_bilder_zu_senden()

    timestamp = datetime.now()
    datum = timestamp.strftime("%Y-%m-%d")
    uhrzeit = timestamp.strftime("%H:%M:%S")
    zeitkompakt = timestamp.strftime("%Y%m%d_%H%M%S")

    temp_bildname = f"{zeitkompakt}.jpg"
    pfad = os.path.join(BILD_VERZEICHNIS, temp_bildname)

    subprocess.run(["libcamera-still", "-o", pfad, "--timeout", "1000", "--width", "224", "--height", "224", "--nopreview"], check=True)

    label, wahrscheinlichkeit = klassifizieren(pfad)

    bildname = f"{zeitkompakt}_{label}_{wahrscheinlichkeit}.jpg"
    neuer_pfad = os.path.join(BILD_VERZEICHNIS, bildname)
    os.rename(pfad, neuer_pfad)

    drehscheibe_positionieren(label)
    fliessband_drehen(label)

    if not sende_bild(neuer_pfad, bildname, label, datum, uhrzeit, wahrscheinlichkeit):
        print("Speichere Bild lokal unter 'nicht_gesendet'")
        os.rename(neuer_pfad, os.path.join(NICHT_GESENDET_VERZEICHNIS, bildname))

if __name__ == "__main__":
    try:
        while True:
            print("Warte auf Tastendruck ...")
            while lgpio.gpio_read(h, TASTER_PIN) == 1:
                time.sleep(0.1)

            aufnehmen_und_senden()

            while lgpio.gpio_read(h, TASTER_PIN) == 0:
                time.sleep(0.1)
    finally:
        lgpio.gpiochip_close(h)
