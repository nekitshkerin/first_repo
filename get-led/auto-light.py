import RPi.GPIO as GPIO

led = 26
volt_div = 6
state = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(led, GPIO.OUT)
GPIO.setup(volt_div, GPIO.IN)

while True:
    if GPIO.input(volt_div):
        GPIO.output(led, 0)
    else:
        GPIO.output(led, 1)