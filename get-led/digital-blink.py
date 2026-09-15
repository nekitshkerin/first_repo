import RPi.GPIO as GPIO
import time

led = 26
state = 0
period = 1.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(led, GPIO.OUT)

while True:
    GPIO.output(led, state)
    state = not state 
    time.sleep(period)