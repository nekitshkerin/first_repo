import RPi.GPIO as GPIO


class R2R_DAC:
    def __init__(self, dac_bits, dynamic_range, verbose = False):
        self.dac_bits = dac_bits
        self.dynamic_range = dynamic_range
        self.verbose = verbose 

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dac_bits, GPIO.OUT, initial = 0)

    def deinit(self):
        GPIO.output(self.dac_bits, 0)
        GPIO.cleanup()

    def set_number(self, number):
        bits = [int(element) for element in bin(number)[2:].zfill(8)]
        GPIO.output(self.dac_bits, bits)
        print(bits)

    def set_voltage(self, voltage):
        if not (0.0 <= voltage <= self.dynamic_range):
            print("Напряжение вне диапазона. Устанавливаем 0 В")
            voltage = 0.0

        number = int(voltage / self.dynamic_range * 255)
        self.set_number(number)

if __name__ == "__main__":
    try:
        dac = R2R_DAC([16, 20 , 21, 25, 26, 17, 27, 22], 3.183, True)

        while True:
            try:
                voltage = float(input("Введите напряжение в вольтах: "))
                dac.set_voltage(voltage)

            except ValueError:
                print("Вы ввели не число. Попробуйте еще раз\n")
    finally:
        dac.deinit()