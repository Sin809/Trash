import requests
import os
from PIL import Image #Pillow = bildbearbeitung
import numpy as np #zum berechnen von tensoren (downgrade version für tflite)
import tflite_runtime.interpreter as tflite
from datetime import datetime
import subprocess
import lgpio
import time

SERVER_URL = "http://error.taild6d121.ts.net:8000/api/upload/"
MODEL_PFAD = "/home/schambach/Trashy/Model/model_unquant.tflite"
LABELS_PFAD = "/home/schambach/Trashy/Model/labels.txt"
BILD_VERZEICHNIS = "/home/schambach/Trashy/Bilder/"
NICHT_GESENDET_VERZEICHNIS = os.path.join(BILD_VERZEICHNIS, "nicht_gesendet")
UUID = "4ca2e077-4e5e-42ab-8aa6-c15336fb88a9" #hier die uuid des entsprechend users (trashApp)

#klassifikationsmodell vorbereiten
interpreter = tflite.Interpreter(model_path=MODEL_PFAD)
interpreter.allocate_tensors() #reserviert speicherplatz
input_index = interpreter.get_input_details()[0]["index"]
output_index = interpreter.get_output_details()[0]["index"]

#labels aus .txt in eine liste packen
with open(LABELS_PFAD, "r") as datei:
    zeilen = datei.readlines()
    LABELS = []
    for zeile in zeilen:
        zeile_sauber = zeile.strip()
        LABELS.append(zeile_sauber)

ROT_PIN = 17
BLAU_PIN = 18
TASTER_PIN = 12

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, ROT_PIN)
lgpio.gpio_claim_output(h, BLAU_PIN)
lgpio.gpio_claim_input(h, TASTER_PIN, lgpio.SET_PULL_UP)

def klassifizieren(pfad):
    bild = Image.open(pfad).resize((224, 224))
    array = np.expand_dims(np.array(bild, dtype=np.float32) / 255.0, axis=0) #bild wird in numpy-array (float) umgewandelt... frag mich nicht, übersteigt meine gehaltsstufe
    interpreter.set_tensor(input_index, array) #füttert das model mit bild-numpy-floaty-array-ding
    interpreter.invoke()
    output = interpreter.get_tensor(output_index)[0] #gibt wahrscheinlichkeiten für die unterschiedlichen klassen/labels z.B. [0.1, 0.9, 0.0]
    index = int(np.argmax(output)) # wählt die klasse/label mit der höchsten wahrscheinlichkeit
    label = LABELS[index]

    if label.lower() == "papier":
        lgpio.gpio_write(h, ROT_PIN, 1)
        time.sleep(1)
        lgpio.gpio_write(h, ROT_PIN, 0)
    elif label.lower() == "plastik":
        lgpio.gpio_write(h, BLAU_PIN, 1)
        time.sleep(1)
        lgpio.gpio_write(h, BLAU_PIN, 0)

    return label

def aufnehmen_und_senden():
    os.makedirs(BILD_VERZEICHNIS, exist_ok=True)
    os.makedirs(NICHT_GESENDET_VERZEICHNIS, exist_ok=True)

    timestamp = datetime.now()
    datum = timestamp.strftime("%Y-%m-%d")
    uhrzeit = timestamp.strftime("%H:%M:%S")
    temp_bildname = f"{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
    pfad = os.path.join(BILD_VERZEICHNIS, temp_bildname)

    subprocess.run(["libcamera-still", "-o", pfad, "--timeout", "1000", "--width", "224", "--height", "224", "--nopreview"], check=True) #cheese :)

    label = klassifizieren(pfad)

    bildname = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{label}.jpg"
    neuer_pfad = os.path.join(BILD_VERZEICHNIS, bildname)
    os.rename(pfad, neuer_pfad)

    #versuch das bild an den server zu schicken
    try:
        with open(neuer_pfad, "rb") as datei:
            response = requests.post(SERVER_URL, files={
                "bild": (bildname, datei, "image/jpeg"),
            }, data={
                "label": label,
                "datum": datum,
                "uhrzeit": uhrzeit,
                "uuid": UUID
            })

        print("Antwort vom Server:", response.status_code, response.text)

        if not response.ok:
            raise Exception("Fehlerhafte Serverantwort")

    except Exception as e:
        print("Fehler beim Senden, speichere lokal:", e)
        fehler_pfad = os.path.join(NICHT_GESENDET_VERZEICHNIS, bildname)
        os.rename(neuer_pfad, fehler_pfad)

if __name__ == "__main__":
    try:
        print("Warte auf Tastendruck ...")
        while lgpio.gpio_read(h, TASTER_PIN) == 1:
            time.sleep(0.1)

        aufnehmen_und_senden()
    finally:
        lgpio.gpiochip_close(h)