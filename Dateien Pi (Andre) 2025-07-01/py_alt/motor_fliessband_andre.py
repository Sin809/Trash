import lgpio
import time
import json
from time import sleep
from ultraschall import berechne_fuellstand

# GPIO-Pins für den Stepper-Motor
in1, in2, in3, in4 = 6, 13, 19, 26
time_step = 0.002  # Geschwindigkeit
FUELLDATEI = "/home/schambach/Trashy/fuellstand.json"

# Initialisiere GPIO
h = lgpio.gpiochip_open(0)
for pin in [in1, in2, in3, in4]:
    lgpio.gpio_claim_output(h, pin, 0)

# Helferfunktion
def set_pin(pin, state):
    lgpio.gpio_write(h, pin, int(state))

# Einzelschritte
def Step1(): set_pin(in4, True); sleep(time_step); set_pin(in4, False)
def Step2(): set_pin(in4, True); set_pin(in3, True); sleep(time_step); set_pin(in4, False); set_pin(in3, False)
def Step3(): set_pin(in3, True); sleep(time_step); set_pin(in3, False)
def Step4(): set_pin(in2, True); set_pin(in3, True); sleep(time_step); set_pin(in2, False); set_pin(in3, False)
def Step5(): set_pin(in2, True); sleep(time_step); set_pin(in2, False)
def Step6(): set_pin(in1, True); set_pin(in2, True); sleep(time_step); set_pin(in1, False); set_pin(in2, False)
def Step7(): set_pin(in1, True); sleep(time_step); set_pin(in1, False)
def Step8(): set_pin(in4, True); set_pin(in1, True); sleep(time_step); set_pin(in4, False); set_pin(in1, False)

def fliessband_drehen(steps=130):
    """
    Dreht den Motor um eine bestimmte Anzahl Steps (z. B. 130 = 90 Grad)
    und misst danach automatisch den Füllstand via Ultraschallsensor.
    """
    print(f"Starte Drehung um {steps} Steps …")
    for i in range(steps):
        Step1(); Step2(); Step3(); Step4(); Step5(); Step6(); Step7(); Step8()
    print("Drehung abgeschlossen.")

    hoehe, prozent = berechne_fuellstand()
    messung = {
        "zeit": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hoehe_cm": round(hoehe, 1) if hoehe else None,
        "fuellstand_prozent": round(prozent, 1) if prozent else None
    }
    with open(FUELLDATEI, "a") as f:
        f.write(json.dumps(messung) + "\n")
    print("Füllstand gespeichert:", messung)

# Optional: nur für manuelle Tests direkt per Ausführung
if __name__ == "__main__":
    fliessband_drehen()
    lgpio.gpiochip_close(h)
