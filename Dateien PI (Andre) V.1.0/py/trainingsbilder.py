import os
import time
import lgpio
import subprocess
from datetime import datetime

#pins ggfs anpassen
TASTER_PIN = 25
LED_PIN = 24


BILD_VERZEICHNIS = "/home/schambach/Trashy/Bilder/Trainigsbilder"

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, TASTER_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_output(h, LED_PIN)
os.makedirs(BILD_VERZEICHNIS, exist_ok=True)

def mache_foto():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pfad = os.path.join(BILD_VERZEICHNIS, f"{timestamp}.jpg")
    subprocess.run([
        "libcamera-still",
        "-o", pfad,
        "--timeout", "1000",
        "--width", "224",
        "--height", "224",
        "--nopreview"
    ], check=True)
    print(f"Foto gespeichert: {pfad}")

try:
    while True:
        print("Warte auf Tastendruck ...")
        lgpio.gpio_write(h, LED_PIN, 1)  #led an

        while lgpio.gpio_read(h, TASTER_PIN) == 1:
            time.sleep(0.1)

        lgpio.gpio_write(h, LED_PIN, 0)  #led aus
        mache_foto()

        while lgpio.gpio_read(h, TASTER_PIN) == 0:
            time.sleep(0.1)

except KeyboardInterrupt:
    print("Beende Programm.")

finally:
    lgpio.gpio_write(h, LED_PIN, 0)
    lgpio.gpiochip_close(h)
