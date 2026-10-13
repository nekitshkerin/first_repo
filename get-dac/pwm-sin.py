"""Задание 6. Запуск на Raspberry Pi: python3 pwm-sin.py. Остановка: Ctrl+C."""

import time
import pwm_dac as pwm
import signal_generator as sg

# Все напряжения положительные: выход изменяется от 0 до amplitude.
amplitude = 3.0           # Верхний уровень, В; размах сигнала тоже 3 В.
signal_frequency = 2.0    # Частота сигнала, Гц: два периода в секунду.
sampling_frequency = 200 # Желаемое число обновлений выхода в секунду.
dynamic_range = 3.3      # Приблизительный максимум ЦАП; уточнить измерением.
pwm_frequency = 500        # Частота несущей ШИМ, Гц. Это НЕ частота синуса.


def main():
    sg.validate_parameters(amplitude, signal_frequency,
                           sampling_frequency, dynamic_range)
    dac = None  # Пока объект управления платой не создан.
    try:
        dac = pwm.PWM_DAC(12, pwm_frequency, dynamic_range)
        start_time = time.perf_counter()  # Запоминаем момент начала.
        print("Генерация сигнала. Для остановки нажмите Ctrl+C.")

        while True:
            step_start = time.perf_counter()  # Начало текущего шага.
            current_time = step_start - start_time  # Время от начала, с.
            level = sg.get_sin_wave_amplitude(signal_frequency, current_time)
            voltage = amplitude * level  # Преобразуем 0...1 в 0...amplitude В.
            dac.set_voltage(voltage)  # Передаём напряжение выбранному ЦАП.
            sg.wait_for_sampling_period(sampling_frequency, step_start)

    except KeyboardInterrupt:  # Сюда попадаем при Ctrl+C.
        print("\nГенерация остановлена.")
    finally:  # Освобождаем ресурсы и при остановке, и при исключении.
        if dac is not None:
            dac.deinit()


if __name__ == "__main__":
    main()

