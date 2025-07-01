
import lgpio
import time

ROT_PIN = 17

# GPIO-Chip öffnen (normalerweise 0 auf Raspberry Pi)
h = lgpio.gpiochip_open(0)

try:
    lgpio.gpio_claim_output(h, ROT_PIN)  # PIN als Ausgang setzen
    print("Rote LED an...")
    lgpio.gpio_write(h, ROT_PIN, 1)      # AN
    time.sleep(2)
    print("Rote LED aus.")
    lgpio.gpio_write(h, ROT_PIN, 0)      # AUS
finally:
    lgpio.gpiochip_close(h)              # Ressourcen freigeben
