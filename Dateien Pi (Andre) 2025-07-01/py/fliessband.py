import lgpio
import time
from time import sleep
from ultraschall import berechne_fuellstand

# GPIO-Pins für den Stepper-Motor (Fließband)
in1, in2, in3, in4 = 6, 13, 19, 26
time_step = 0.002

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

def fliessband_drehen(label: str, steps=560):
    """
    Dreht das Fließband (Stepper-Motor) und misst danach den Füllstand
    des aktuell unter dem Band stehenden Müllbehälters (Label: Papier, Plastik, ...).
    """
    print(f"[Fließband] Starte Drehung ({steps} Steps) …")
    for _ in range(steps):
        Step1(); Step2(); Step3(); Step4(); Step5(); Step6(); Step7(); Step8()
    print("[Fließband] Drehung abgeschlossen.")

    # Messung starten & speichern über ultraschall-Modul
    _, prozent = berechne_fuellstand(label)
    if prozent is not None:
        print(f"[Fließband] Füllstand {label}: {prozent:.1f} %")
    else:
        print(f"[Fließband] Fehlerhafte Messung für {label}")

if __name__ == "__main__":
    fliessband_drehen("Papier")
    lgpio.gpiochip_close(h)
