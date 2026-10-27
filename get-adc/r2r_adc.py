"""8-битный АЦП на плате get-adc: счёт и поразрядное приближение."""

import argparse
import math
import time

import RPi.GPIO as GPIO


class R2R_ADC:
    def __init__(self, dynamic_range, compare_time=0.01, verbose=False):
        # dynamic_range — измеренное напряжение ЦАП при коде 255, в В.
        if not math.isfinite(dynamic_range) or dynamic_range <= 0:
            raise ValueError("Диапазон должен быть положительным числом")
        if not math.isfinite(compare_time) or compare_time < 0:
            raise ValueError("Пауза должна быть неотрицательным числом")

        self.dynamic_range = dynamic_range
        self.compare_time = compare_time
        self.verbose = verbose
        self.bits_gpio = [26, 20, 19, 16, 13, 12, 25, 11]  # bit7 ... bit0
        self.comp_gpio = 21
        self.bit_count = len(self.bits_gpio)
        self.max_number = 2 ** self.bit_count - 1
        # На get-adc из материалов высокий уровень означает U_DAC > U_in.
        self.dac_above_input_level = GPIO.HIGH
        self._closed = False

        GPIO.setmode(GPIO.BCM)
        try:
            GPIO.setup(self.bits_gpio, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.comp_gpio, GPIO.IN)
        except BaseException:
            GPIO.cleanup(self.bits_gpio + [self.comp_gpio])
            raise

    def number_to_dac(self, number):
        if not isinstance(number, int) or not 0 <= number <= self.max_number:
            raise ValueError("Код ЦАП должен быть целым числом от 0 до 255")
        # Например, 5 -> '00000101' -> [0, 0, 0, 0, 0, 1, 0, 1].
        bits = [int(bit) for bit in format(number, "08b")]
        GPIO.output(self.bits_gpio, bits)
        if self.verbose:
            print(f"ЦАП: {number:3d}, биты: {bits}")

    def sequential_counting_adc(self):
        for number in range(self.max_number + 1):
            self.number_to_dac(number)
            time.sleep(self.compare_time)
            if GPIO.input(self.comp_gpio) == self.dac_above_input_level:
                return number
        # Даже если компаратор не переключился, результат остаётся 8-битным.
        return self.max_number

    def successive_approximation_adc(self):
        number = 0
        for bit in range(self.bit_count - 1, -1, -1):
            trial_number = number | (1 << bit)
            self.number_to_dac(trial_number)
            time.sleep(self.compare_time)
            if GPIO.input(self.comp_gpio) != self.dac_above_input_level:
                number = trial_number  # Пробное напряжение не слишком велико.
        self.number_to_dac(number)  # Оставляем на ЦАП итоговый код.
        return number

    def get_sc_voltage(self):
        return self.sequential_counting_adc() * self.dynamic_range / self.max_number

    def get_sar_voltage(self):
        return self.successive_approximation_adc() * self.dynamic_range / self.max_number

    def deinit(self):
        if not self._closed:
            try:
                GPIO.output(self.bits_gpio, GPIO.LOW)
            finally:
                GPIO.cleanup(self.bits_gpio + [self.comp_gpio])
                self._closed = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--range", dest="dynamic_range", type=float, required=True,
                        help="Измеренное U_DAC при коде 255, В")
    parser.add_argument("--method", choices=["sc", "sar"], default="sc")
    parser.add_argument("--compare-time", type=float, default=0.01)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    adc = None
    try:
        adc = R2R_ADC(args.dynamic_range, args.compare_time, args.verbose)
        while True:
            if args.method == "sc":
                voltage = adc.get_sc_voltage()
            else:
                voltage = adc.get_sar_voltage()
            print(f"Напряжение: {voltage:.4f} В")
    except KeyboardInterrupt:
        print("\nИзмерения остановлены")
    finally:
        if adc is not None:
            adc.deinit()
