import lgpio
import time
import json
import os

TRIG = 22
ECHO = 27
BEHAELTER_HOEHE_CM = 15 #enstrepchend anpassen
ABSTAND_SENSOR_CM = 2 #enstrepchend anpassen
TANK_HOEHE_CM = BEHAELTER_HOEHE_CM + ABSTAND_SENSOR_CM

FUELLDATEI = "/home/schambach/Trashy/fuellstand.json"

# GPIO initialisieren
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

def entfernung_messen():
    # ultraschallimpuls senden
    lgpio.gpio_write(h, TRIG, 0)
    time.sleep(0.000002)
    lgpio.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    # auf startsignal (ECHO HIGH) warten
    start = time.time()
    timeout = start + 0.04
    while lgpio.gpio_read(h, ECHO) == 0:
        if time.time() >= timeout:
            return None
        start = time.time()

    # auf stopsignal (ECHO LOW) warten
    timeout = time.time() + 0.04
    while lgpio.gpio_read(h, ECHO) == 1:
        if time.time() >= timeout:
            return None
        stop = time.time()

    # entfernung berechnen
    dauer = stop - start
    entfernung = (dauer * 34300) / 2  # cm

    if 0 < entfernung <= 400:
        return entfernung
    return None

def berechne_fuellstand(label=None):
    abstand = entfernung_messen()
    if abstand is None:
        return None, None

    fuellhoehe = max(0.0, TANK_HOEHE_CM - abstand)
    prozent = min(100.0, (fuellhoehe / BEHAELTER_HOEHE_CM) * 100)

    if label:
        daten = {}
        if os.path.exists(FUELLDATEI):
            with open(FUELLDATEI, "r") as f:
                try:
                    daten = json.load(f)
                except json.JSONDecodeError:
                    pass  # wenn datei leer oder defekt

        daten[label] = round(prozent, 1)

        with open(FUELLDATEI, "w") as f:
            json.dump(daten, f, indent=2)

        print(f"Füllstand für {label}: {daten[label]} % gespeichert.")

    return fuellhoehe, prozent

if __name__ == "__main__":
    try:
        while True:
            hoehe, prozent = berechne_fuellstand("Papier")
            if hoehe is not None:
                print(f"Füllhöhe: {hoehe:.1f} cm ({prozent:.1f} %)")
            else:
                print("❗ Ungültige Messung")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Beende Programm.")
        lgpio.gpiochip_close(h)
