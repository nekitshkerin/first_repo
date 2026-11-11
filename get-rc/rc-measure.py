import time

import numpy as np
import RPi.GPIO as GPIO

from mcp3021_driver import MCP3021

dynamic_range = 5.186   # питание MCP3021, В (измерьте мультиметром на контакте PWR блока AUX)
rc_gpio = 14            # пин, к которому подключена RC-цепь
charge_time = 50.0      # продолжительность зарядки, с
discharge_time = 50.0   # продолжительность разрядки, с

voltage_values = []
time_values = []

GPIO.setmode(GPIO.BCM)
GPIO.setup(rc_gpio, GPIO.OUT, initial=GPIO.LOW)
adc = MCP3021(dynamic_range)

try:
    # 1. Перед опытом полностью разряжаем конденсатор, ничего не записываем
    print(f"Разрядка перед опытом {discharge_time} с...")
    GPIO.output(rc_gpio, 0)
    time.sleep(discharge_time)

    # 2. Подаём 1: конденсатор заряжается через резистор, измеряем напряжение
    print(f"Зарядка {charge_time} с...")
    GPIO.output(rc_gpio, 1)
    start_time = time.time()
    while time.time() - start_time < charge_time:
        voltage_values.append(adc.get_voltage())
        time_values.append(time.time() - start_time)

    # 3. Подаём 0: конденсатор разряжается через тот же резистор, продолжаем измерять
    print(f"Разрядка {discharge_time} с...")
    GPIO.output(rc_gpio, 0)
    while time.time() - start_time < charge_time + discharge_time:
        voltage_values.append(adc.get_voltage())
        time_values.append(time.time() - start_time)

finally:
    GPIO.output(rc_gpio, 0)
    GPIO.cleanup()
    adc.deinit()

# 4. Сохраняем два столбца (время и напряжение) в data.csv
data = np.column_stack((time_values, voltage_values))

np.savetxt('data.csv',
           data,
           delimiter=',',
           fmt='%.4f',
           header='Время[с],Напряжение[В]',
           comments='',
           encoding='utf-8')

print(f"Измерений: {len(time_values)}, данные записаны в data.csv")
