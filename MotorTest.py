from RPi import GPIO
from time import sleep
import random

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

in1 = 6 #4 Pins für den Motor; Strom kommt seperat an den Controller des Motors
in2 = 13
in3 = 19
in4 = 26

time = 0.002 #Geschwindigkeit des Motors; geringerer Wert = schneller

GPIO.setup(in1, GPIO.OUT) #Pin Setup für Motor
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)

GPIO.output(in1, False) #Ich glaube False und True ist Low und High
GPIO.output(in2, False)
GPIO.output(in3, False)
GPIO.output(in4, False)

def Step1():					# Der Schrittmotor hat 8 Schritte die er nacheinander durchführt
	GPIO.output(in4, True)		# Die Schritte müssen in der richtigen Reihenfolge ausgeführt werden
	sleep(time)					# Sonst überspringt der Motor alle Schritte bis er dort ist wo er 
	GPIO.output(in4, False)		# den letzten Schritt nicht machen konnte, also immer von 1 zu 8 oder 8 zu 1 (1, 2, 3,...)
	
def Step2():
	GPIO.output(in4, True)
	GPIO.output(in4, True)
	sleep(time)
	GPIO.output(in4, False)
	GPIO.output(in4, False)
	
def Step3():
	GPIO.output(in3, True)
	sleep(time)
	GPIO.output(in3, False)
	
def Step4():
	GPIO.output(in2, True)
	GPIO.output(in3, True)
	sleep(time)
	GPIO.output(in2, False)
	GPIO.output(in3, False)
	
def Step5():
	GPIO.output(in2, True)
	sleep(time)
	GPIO.output(in2, False)
	
def Step6():
	GPIO.output(in1, True)
	GPIO.output(in2, True)
	sleep(time)
	GPIO.output(in1, False)
	GPIO.output(in2, False)
	
def Step7():
	GPIO.output(in1, True)
	sleep(time)
	GPIO.output(in1, False)
	
def Step8():
	GPIO.output(in4, True)
	GPIO.output(in1, True)
	sleep(time)
	GPIO.output(in4, False)
	GPIO.output(in1, False)

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
		print("Step LEFT: "), i
		
if random.randint(0, 1) >= 1:		# Was das genau macht weiß ich auch nicht...
	left(random.randint(100, 1024))

	GPIO.cleanup()
	print("restart")
