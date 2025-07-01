import lgpio
import time
import json
import os

TRIG = 22
ECHO = 27
TANK_HOEHE_CM = 50.0  # Anpassen je nach Behälterhöhe
FUELLDATEI = "/home/schambach/Trashy/fuellstand.json"

# GPIO initialisieren
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

def entfernung_messen():
    lgpio.gpio_write(h, TRIG, 0)
    time.sleep(0.000002)
    lgpio.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    start = time.time()
    timeout = start + 0.04

    while lgpio.gpio_read(h, ECHO) == 0 and time.time() < timeout:
        start = time.time()

    if time.time() >= timeout:
        return None

    stop = None
    timeout = time.time() + 0.04
    while lgpio.gpio_read(h, ECHO) == 1 and time.time() < timeout:
        stop = time.time()

    if stop is None:
        return None

    duration = stop - start
    entfernung = (duration * 34300) / 2

    if entfernung <= 0 or entfernung > 400:
        return None

    return entfernung

def berechne_fuellstand(label=None):
    abstand = entfernung_messen()
    if abstand is None:
        return None, None

    fuellhoehe = max(0.0, TANK_HOEHE_CM - abstand)
    prozent = min(100.0, (fuellhoehe / TANK_HOEHE_CM) * 100)

    if label:
        daten = {}
        if os.path.exists(FUELLDATEI):
            with open(FUELLDATEI, "r") as f:
                try:
                    daten = json.load(f)
                except json.JSONDecodeError:
                    daten = {}

        # Neuen Wert speichern
        daten[label] = round(prozent, 1)

        # In Datei schreiben
        with open(FUELLDATEI, "w") as f:
            json.dump(daten, f, indent=2)

        print(f"Füllstand für {label}: {round(prozent, 1)} % gespeichert.")

    return fuellhoehe, prozent

# Einzeltest
if __name__ == "__main__":
    try:
        while True:
            hoehe, prozent = berechne_fuellstand("Papier")  # Beispiellabel
            if hoehe is not None:
                print(f"Füllhöhe: {hoehe:.1f} cm ({prozent:.1f} %)")
            else:
                print("❗ Ungültige Messung")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Beende Programm.")
        lgpio.gpiochip_close(h)
