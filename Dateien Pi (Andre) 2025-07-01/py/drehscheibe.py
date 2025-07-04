import lgpio
import time
import json
import os
from time import sleep

in1, in2, in3, in4 = 12, 16, 20, 21
time_step = 0.002

position_path = "/home/schambach/Trashy/position.json"

BEHAELTER = ["Papier", "Plastik", "Restmüll", "Uneindeutig"]

# 130 = 90°
STEPS_PRO_SEGMENT = 130

h = lgpio.gpiochip_open(0)

# pins als ausgang setzen
for pin in [in1, in2, in3, in4]:
    lgpio.gpio_claim_output(h, pin, 0)

def set_pin(pin, state):
    lgpio.gpio_write(h, pin, int(state))

# schritte 1–8
def Step1(): set_pin(in4, True); sleep(time_step); set_pin(in4, False)
def Step2(): set_pin(in4, True); set_pin(in3, True); sleep(time_step); set_pin(in4, False); set_pin(in3, False)
def Step3(): set_pin(in3, True); sleep(time_step); set_pin(in3, False)
def Step4(): set_pin(in2, True); set_pin(in3, True); sleep(time_step); set_pin(in2, False); set_pin(in3, False)
def Step5(): set_pin(in2, True); sleep(time_step); set_pin(in2, False)
def Step6(): set_pin(in1, True); set_pin(in2, True); sleep(time_step); set_pin(in1, False); set_pin(in2, False)
def Step7(): set_pin(in1, True); sleep(time_step); set_pin(in1, False)
def Step8(): set_pin(in4, True); set_pin(in1, True); sleep(time_step); set_pin(in4, False); set_pin(in1, False)

# motor "anzahl" schritte drehen
def drehe_steps(anzahl):
    for _ in range(anzahl):
        Step1(); Step2(); Step3(); Step4(); Step5(); Step6(); Step7(); Step8()

# letze position der müllbehälter holen
def lade_position():
    if not os.path.exists(position_path):
        print("[Drehscheibe] keine position.json – standard = 0")
        return 0
    try:
        with open(position_path, "r") as f:
            data = json.load(f)
            pos = data.get("position", 0)
            print(f"[Drehscheibe] geladen: {pos} ({BEHAELTER[pos]})")
            return pos
    except Exception as e:
        print(f"[Drehscheibe] fehler beim laden: {e}")
        return 0

# neue position speichern
def speichere_position(pos_index):
    try:
        with open(position_path, "w") as f:
            json.dump({"position": pos_index}, f)
        print(f"[Drehscheibe] gespeichert: {pos_index} ({BEHAELTER[pos_index]})")
    except Exception as e:
        print(f"[Drehscheibe] fehler beim speichern: {e}")

# scheibe zum ziel drehen
def drehscheibe_positionieren(label: str):
    ziel = BEHAELTER.index(label) if label in BEHAELTER else BEHAELTER.index("Uneindeutig")
    aktuell = lade_position()

    # differenz berechnen, ggf. im kreis weiterzählen
    if ziel >= aktuell:
        diff = ziel - aktuell
    else:
        diff = len(BEHAELTER) - (aktuell - ziel) #len behälter = anzahl der mülleimer

    steps = diff * STEPS_PRO_SEGMENT

    print(f"[drehscheibe] {BEHAELTER[aktuell]} → {BEHAELTER[ziel]} → {steps} schritte")

    drehe_steps(steps)
    speichere_position(ziel)
    print(f"[drehscheibe] neu: {BEHAELTER[ziel]}")


# test: auf "papier" drehen
if __name__ == "__main__":
    drehscheibe
