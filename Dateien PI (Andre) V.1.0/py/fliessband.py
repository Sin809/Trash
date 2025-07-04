import lgpio
import time
from time import sleep
from ultraschall import berechne_fuellstand

in1, in2, in3, in4 = 6, 13, 19, 26

time_step = 0.002

h = lgpio.gpiochip_open(0)

# alle pins als ausgang reservieren
for pin in [in1, in2, in3, in4]:
    lgpio.gpio_claim_output(h, pin, 0)

# pin auf 0 oder 1 setzen
def set_pin(pin, state):
    lgpio.gpio_write(h, pin, int(state))

# einzelne schritte für den stepper-motor (halb-schritt-modus)
def Step1(): set_pin(in4, True); sleep(time_step); set_pin(in4, False)
def Step2(): set_pin(in4, True); set_pin(in3, True); sleep(time_step); set_pin(in4, False); set_pin(in3, False)
def Step3(): set_pin(in3, True); sleep(time_step); set_pin(in3, False)
def Step4(): set_pin(in2, True); set_pin(in3, True); sleep(time_step); set_pin(in2, False); set_pin(in3, False)
def Step5(): set_pin(in2, True); sleep(time_step); set_pin(in2, False)
def Step6(): set_pin(in1, True); set_pin(in2, True); sleep(time_step); set_pin(in1, False); set_pin(in2, False)
def Step7(): set_pin(in1, True); sleep(time_step); set_pin(in1, False)
def Step8(): set_pin(in4, True); set_pin(in1, True); sleep(time_step); set_pin(in4, False); set_pin(in1, False)

# anzahl der steps noch anpassen!
def fliessband_drehen(label: str, steps=1000):
    print(f"[Fließband] starte drehung ({steps} schritte) …")

    # motor n schritte vorwärts bewegen
    for _ in range(steps): #erste variable ist unwichtig "_" ist nur ein platzhalter
        Step1(); Step2(); Step3(); Step4(); Step5(); Step6(); Step7(); Step8()

    print("[Fließband] drehung abgeschlossen.")

    # füllstand messen und anzeigen
    _, prozent = berechne_fuellstand(label) # gib füllhöhe und prozent, wir brauchen nur prozent. "_" ist nur platzhalter
    if prozent is not None:
        print(f"[Fließband] füllstand {label}: {prozent:.1f} %")
    else:
        print(f"[Fließband] messfehler bei {label}")

# testlauf: dreht fließband für papier und schließt gpio
if __name__ == "__main__":
    fliessband_drehen("Papier")
    lgpio.gpiochip_close(h)
