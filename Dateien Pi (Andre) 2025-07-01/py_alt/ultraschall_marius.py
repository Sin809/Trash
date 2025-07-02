import lgpio
import time

# HC-SR04 GPIO-Pins (anpassen falls nötig)
TRIG = 23  # GPIO23
ECHO = 24  # GPIO24

# GPIO initialisieren
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

# Behälterhöhe in cm (von Sensor bis Behälterboden)
TANK_HOEHE_CM = 50.0  # <-- Anpassen je nach Tank

def entfernung_messen():
    # Ultraschallimpuls senden
    lgpio.gpio_write(h, TRIG, 0)
    time.sleep(0.000002)
    lgpio.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    start = time.time()
    timeout = start + 0.04  # Timeout: 40 ms für Start

    # Warte, bis ECHO auf HIGH geht
    while lgpio.gpio_read(h, ECHO) == 0 and time.time() < timeout:
        start = time.time()

    # Falls kein HIGH kam → ungültige Messung
    if time.time() >= timeout:
        return None

    stop = None
    timeout = time.time() + 0.04  # Neues Timeout: 40 ms für Ende

    # Warte, bis ECHO wieder auf LOW geht
    while lgpio.gpio_read(h, ECHO) == 1 and time.time() < timeout:
        stop = time.time()

    # Falls kein LOW erkannt → ungültig
    if stop is None:
        return None

    # Dauer berechnen
    duration = stop - start
    entfernung = (duration * 34300) / 2  # Schallgeschwindigkeit in cm/s

    # Plausibilitätscheck (typisch < 400 cm)
    if entfernung <= 0 or entfernung > 400:
        return None

    return entfernung

def berechne_fuellstand():
    abstand = entfernung_messen()
    if abstand is None:
        return None, None
    fuellhoehe = max(0.0, TANK_HOEHE_CM - abstand)
    prozent = min(100.0, (fuellhoehe / TANK_HOEHE_CM) * 100)
    return fuellhoehe, prozent

# Hauptprogramm
try:
    while True:
        hoehe, prozent = berechne_fuellstand()
        if hoehe is not None:
            print(f"Füllhöhe: {hoehe:.1f} cm ({prozent:.1f} %)")
        else:
            print("❗ Messung ungültig oder kein Echo empfangen")
        time.sleep(1)

except KeyboardInterrupt:
    print("Beende Programm.")
    lgpio.gpiochip_close(h)
