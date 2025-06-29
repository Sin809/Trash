import lgpio
from time import sleep
import random

# GPIO-Pins (BCM) Zuordnung kann hier angepasst werden, für zwei Motoren können weitere 4 Pins genutzt werden mit demselben code
in1 = 6
in2 = 13
in3 = 19
in4 = 26

time = 0.002  # Geschwindigkeit des Motors

h = lgpio.gpiochip_open(0) # GPIO wird initiiert mit dem "handler" namens h in diesem Fall (Referenz für diesen GPIO Anschluss)

# pins werden hier gesetzt
for pin in [in1, in2, in3, in4]:
    lgpio.gpio_claim_output(h, pin, 0) # hier wird jeder Pin aus der obigen Liste initiiert, mit einem Startwert von 0 (LOW)

def set_pin(pin, state):
    lgpio.gpio_write(h, pin, int(state))
    
# Hier wird bei jedem Schritt dafür gesorgt, dass der Rotor sich weiter dreht. Wird ein Schritt ausgelassen, überspringt er die folgenden 7. Der Motor sollte nicht überlastet werden!

def Step1():
    set_pin(in4, True)
    sleep(time)
    set_pin(in4, False)

def Step2():
    set_pin(in4, True)
    set_pin(in3, True)
    sleep(time)
    set_pin(in4, False)
    set_pin(in3, False)

def Step3():
    set_pin(in3, True)
    sleep(time)
    set_pin(in3, False)

def Step4():
    set_pin(in2, True)
    set_pin(in3, True)
    sleep(time)
    set_pin(in2, False)
    set_pin(in3, False)

def Step5():
    set_pin(in2, True)
    sleep(time)
    set_pin(in2, False)

def Step6():
    set_pin(in1, True)
    set_pin(in2, True)
    sleep(time)
    set_pin(in1, False)
    set_pin(in2, False)

def Step7():
    set_pin(in1, True)
    sleep(time)
    set_pin(in1, False)

def Step8():
    set_pin(in4, True)
    set_pin(in1, True)
    sleep(time)
    set_pin(in4, False)
    set_pin(in1, False)

# Hier werden die 8 Steps nacheinander ausgeführt, so oft wie der Input es sagt. Dieser müsste automatisch weitergegeben werden, am besten drehen wir die Scheibe nachdem der Müll im jeweiligen Fach ist wieder auf eine Standardposition, das vereinfacht den Code, dauert aber länger

def left(step):
    for i in range(step):
        Step1()
        Step2()
        Step3()
        Step4()
        Step5()
        Step6()
        Step7()
        Step8()
        print(f"Step LEFT: {i}")

# Hier wird die Anzahl an Drehungen ausgesucht, 130 entsprechen ziemlich genau 90 Grad

while True:
	print("Folgendes bitte nur als Zahl")
	schritte = int(input("Geben Sie ein, wie viele Steps nach LINKS gemacht werden sollen: "))

	left(schritte)

lgpio.gpiochip_close(h)
