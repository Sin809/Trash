# taster_test.py
import lgpio
import time

TASTER_PIN = 12

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, TASTER_PIN, lgpio.SET_PULL_UP)

print("Drücke den Taster (GPIO12) ...")

try:
    while True:
        zustand = lgpio.gpio_read(h, TASTER_PIN)
        if zustand == 0:  # Taster gedrückt (gegen GND)
            print("Taster wurde gedrückt!")
            time.sleep(0.5)  # Entprellen
except KeyboardInterrupt:
    print("Beendet durch STRG+C")
finally:
    lgpio.gpiochip_close(h)
