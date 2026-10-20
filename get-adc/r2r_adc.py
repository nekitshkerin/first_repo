import RPi.GPIO as GPIO
import time


class R2R_ADC:
    def __init__(self, dynamic_range, compare_time=0.01, verbose=False):
        self.dynamic_range = dynamic_range
        self.compare_time = compare_time
        self.verbose = verbose

        self.bits_gpio = [26, 20, 19, 16, 13, 12, 25, 11]
        self.comp_gpio = 21

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.bits_gpio, GPIO.OUT, initial=0)
        GPIO.setup(self.comp_gpio, GPIO.IN)

    def deinit(self):
        GPIO.output(self.bits_gpio, 0)
        GPIO.cleanup()

    def number_to_dac(self, number):
        if not isinstance(number, int) or not (0 <= number <= 255):
            print("Число должно быть целым от 0 до 255")
            return

        bits = [int(element) for element in bin(number)[2:].zfill(8)]
        GPIO.output(self.bits_gpio, bits)

        if self.verbose:
            print(f"Число: {number}, двоичный код: {bits}")

    def sequential_counting_adc(self):
        self.number_to_dac(0)
        time.sleep(self.compare_time)

        start_state = GPIO.input(self.comp_gpio)

        for number in range(1, 256):
            self.number_to_dac(number)
            time.sleep(self.compare_time)

            comp_state = GPIO.input(self.comp_gpio)

            if comp_state != start_state:
                if self.verbose:
                    print(f"Найдено число: {number}")
                return number

        return 255

    def get_sc_voltage(self):
        number = self.sequential_counting_adc()
        voltage = number * self.dynamic_range / 255

        return voltage


if __name__ == "__main__":
    adc = None

    try:
        adc = R2R_ADC(3.3, compare_time=0.01, verbose=False)

        while True:
            voltage = adc.get_sc_voltage()
            print(f"Напряжение: {voltage:.3f} В")

    except KeyboardInterrupt:
        print("\nИзмерения остановлены")

    finally:
        if adc is not None:
            adc.deinit()




