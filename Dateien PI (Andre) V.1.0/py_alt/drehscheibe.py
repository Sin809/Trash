import lgpio
import time
import json
import os
from time import sleep

# GPIO-Pins für Stepper-Motor der Drehscheibe
in1, in2, in3, in4 = 12, 16, 20, 21
time_step = 0.002
position_path = "/home/schambach/Trashy/position.json"

# Zuordnung der Behälter (Reihenfolge auf der Scheibe)
BEHAELTER = ["Papier", "Plastik", "Restmüll", "Uneindeutig"]
STEPS_PRO_SEGMENT = 130  # Schritte für 90° (1/4-Drehung)

# GPIO initialisieren
h = lgpio.gpiochip_open(0)
for pin in [in1, in2, in3, in4]:
    lgpio.gpio_claim_output(h, pin, 0)

def set_pin(pin, state):
    lgpio.gpio_write(h, pin, int(state))

def Step1(): set_pin(in4, True); sleep(time_step); set_pin(in4, False)
def Step2(): set_pin(in4, True); set_pin(in3, True); sleep(time_step); set_pin(in4, False); set_pin(in3, False)
def Step3(): set_pin(in3, True); sleep(time_step); set_pin(in3, False)
def Step4(): set_pin(in2, True); set_pin(in3, True); sleep(time_step); set_pin(in2, False); set_pin(in3, False)
def Step5(): set_pin(in2, True); sleep(time_step); set_pin(in2, False)
def Step6(): set_pin(in1, True); set_pin(in2, True); sleep(time_step); set_pin(in1, False); set_pin(in2, False)
def Step7(): set_pin(in1, True); sleep(time_step); set_pin(in1, False)
def Step8(): set_pin(in4, True); set_pin(in1, True); sleep(time_step); set_pin(in4, False); set_pin(in1, False)

def drehe_steps(anzahl):
    for _ in range(anzahl):
        Step1(); Step2(); Step3(); Step4(); Step5(); Step6(); Step7(); Step8()

def lade_position():
    if not os.path.exists(position_path):
        print("[Drehscheibe] position.json existiert nicht – Standardposition 0 (Papier)")
        return 0
    try:
        with open(position_path, "r") as f:
            data = json.load(f)
            aktuelle_position = data.get("position", 0)
            print(f"[Drehscheibe] Geladene Position: {aktuelle_position} ({BEHAELTER[aktuelle_position]})")
            return aktuelle_position
    except Exception as e:
        print(f"[Drehscheibe] Fehler beim Laden der Position: {e}")
        return 0

def speichere_position(pos_index):
    try:
        with open(position_path, "w") as f:
            json.dump({"position": pos_index}, f)
        print(f"[Drehscheibe] Neue Position gespeichert: {pos_index} ({BEHAELTER[pos_index]})")
    except Exception as e:
        print(f"[Drehscheibe] Fehler beim Speichern der Position: {e}")

def drehscheibe_positionieren(label: str):
    if label in BEHAELTER:
        ziel_index = BEHAELTER.index(label)
    else:
        ziel_index = BEHAELTER.index("Uneindeutig")

    aktuelle_position = lade_position()
    differenz = (ziel_index - aktuelle_position) % len(BEHAELTER)
    steps = differenz * STEPS_PRO_SEGMENT

    print(f"[Drehscheibe] Aktuell: {BEHAELTER[aktuelle_position]}, Ziel: {BEHAELTER[ziel_index]} → {steps} Schritte")

    drehe_steps(steps)
    speichere_position(ziel_index)

    print(f"[Drehscheibe] Neue Position: {BEHAELTER[ziel_index]}")


if __name__ == "__main__":
    drehscheibe_positionieren("Papier")
    lgpio.gpiochip_close(h)
