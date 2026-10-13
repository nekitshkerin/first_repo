"""Вспомогательный модуль из задания 3: ЦАП на ШИМ, GPIO12."""

import math
import RPi.GPIO as GPIO


class PWM_DAC:
    def __init__(self, gpio_pin, pwm_frequency, dynamic_range, verbose=False):
        if not math.isfinite(dynamic_range) or dynamic_range <= 0:
            raise ValueError("Диапазон ЦАП должен быть положительным")
        if not math.isfinite(pwm_frequency) or pwm_frequency <= 0:
            raise ValueError("Частота ШИМ должна быть положительной")
        self.gpio_pin = gpio_pin
        self.dynamic_range = dynamic_range
        self.verbose = verbose
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial=0)
        self.pwm = None
        try:
            self.pwm = GPIO.PWM(self.gpio_pin, pwm_frequency)
            self.pwm.start(0)  # Начинаем с заполнения 0%, то есть с нуля.
        except BaseException:
            self.deinit()
            raise

    def set_voltage(self, voltage):
        if not math.isfinite(voltage) or not 0 <= voltage <= self.dynamic_range:
            raise ValueError("Напряжение выходит за диапазон ЦАП")
        duty_cycle = voltage / self.dynamic_range * 100
        self.pwm.ChangeDutyCycle(duty_cycle)
        if self.verbose:
            print(f"Задано {voltage:.3f} В; заполнение {duty_cycle:.1f}%")

    def deinit(self):
        try:
            if self.pwm is not None:
                self.pwm.stop()
        finally:
            try:
                GPIO.output(self.gpio_pin, 0)
            finally:
                GPIO.cleanup(self.gpio_pin)


if __name__ == "__main__":
    dac = None
    try:
        dac = PWM_DAC(12, 500, 3.3, verbose=True)
        while True:
            try:
                dac.set_voltage(float(input("Напряжение, В: ")))
            except ValueError as error:
                print(error)
    except (KeyboardInterrupt, EOFError):
        print("\nОстановка")
    finally:
        if dac is not None:
            dac.deinit()

