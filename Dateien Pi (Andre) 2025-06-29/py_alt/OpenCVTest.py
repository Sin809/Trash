# import cv2
# cam = cv2.VideoCapture(0) # 0 = erste Kamera
# while True:
#     ok, img = cam.read()
#     if ok:
#         cv2.imshow("Kamera #1", img)
#         cv2.waitKey(2)
###################################################

# import cv2
# img = cv2.imread("qr.png")
# qcd = cv2.QRCodeDetector()
# ok, data, _, _ = qcd.detectAndDecodeMulti(img)

# if ok:
#     print(data)
#################################
# import cv2

# cam = cv2.VideoCapture(0)
# print("Kamera geöffnet?", cam.isOpened())

# ret, frame = cam.read()
# if ret:
#     cv2.imwrite("foto.jpg", frame)
# cam.release()
#################################
# import cv2
# import time

# cam = cv2.VideoCapture(0)
# print("Kamera geöffnet?", cam.isOpened())
# time.sleep(2)  # Kamera aufwecken
# for _ in range(5): cam.read()  # Dummy-Reads

# ret, frame = cam.read()
# if ret:
#     cv2.imwrite("/home/schambach/Trashy/foto.jpg", frame)
# print("Bild erfolgreich aufgenommen?", ret)

# cam.release()
################################
import subprocess
import cv2

subprocess.run([
    "libcamera-still",
    "-o", "bild_kamera.jpg",
    "--width", "1920",
    "--height", "1080",        
    "--nopreview",
    "-t", "1000"
])

bild_kamera = cv2.imread("bild_kamera.jpg") #qr code zu klein, bzw. qualität zu schlecht
bild_vorlage1 = cv2.imread("py/qrcode.png")
bild_vorlage2 = cv2.imread("qrcode.png")
bild_vorlage3 = cv2.imread("/home/schambach/Trashy/WhatsApp Bild 2025-05-28 um 12.27.32_8ad24fa4.jpg")

detektor = cv2.QRCodeDetector()
res = detektor.detectAndDecodeMulti(bild_vorlage1)
gefunden, daten, _, _ = res

if gefunden:
    print(daten[0])

print(daten)
data, _, _ = detektor.detectAndDecode(bild_vorlage1)

print("QR-Code:", data)
