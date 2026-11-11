"""Зарядка и разрядка RC-цепи: GPIO14 управляет цепью, MCP3021 измеряет напряжение на конденсаторе."""

import time

import numpy as np
import RPi.GPIO as GPIO

from mcp3021_driver import MCP3021
import adc_plot

DYNAMIC_RANGE = 5.186   # измеренное питание MCP3021, В (замерить мультиметром и подставить своё)
RC_GPIO = 14            # выход, к которому подключена RC-цепь
DISCHARGE_TIME = 50     # предварительная разрядка, с
CHARGE_TIME = 50        # зарядка, с
MEASURE_DISCHARGE_TIME = 50  # разрядка с измерениями, с

time_values = []
voltage_values = []
state_values = []

GPIO.setmode(GPIO.BCM)
GPIO.setup(RC_GPIO, GPIO.OUT, initial=GPIO.LOW)
adc = None

try:
    adc = MCP3021(DYNAMIC_RANGE)

    # 1. Выход в 0: конденсатор полностью разряжается, ничего не записываем.
    print(f"Разрядка конденсатора {DISCHARGE_TIME} с...")
    GPIO.output(RC_GPIO, 0)
    time.sleep(DISCHARGE_TIME)

    # 2. Выход в 1: конденсатор заряжается, непрерывно измеряем напряжение.
    print(f"Зарядка {CHARGE_TIME} с...")
    state = 1
    GPIO.output(RC_GPIO, state)
    start_time = time.perf_counter()
    while time.perf_counter() - start_time < CHARGE_TIME + MEASURE_DISCHARGE_TIME:
        # 3. Через CHARGE_TIME с снова подаём 0: конденсатор разряжается через тот же резистор.
        if state == 1 and time.perf_counter() - start_time >= CHARGE_TIME:
            print(f"Разрядка {MEASURE_DISCHARGE_TIME} с...")
            state = 0
            GPIO.output(RC_GPIO, state)
        voltage = adc.get_voltage()
        elapsed = time.perf_counter() - start_time
        time_values.append(elapsed)
        voltage_values.append(voltage)
        state_values.append(state)

except KeyboardInterrupt:
    print("\nОпыт прерван, сохраняем накопленные данные")
finally:
    GPIO.output(RC_GPIO, 0)
    GPIO.cleanup(RC_GPIO)
    if adc is not None:
        adc.deinit()

# 4. Сохраняем время, напряжение и состояние выхода в lab.csv.
print(f"Получено отсчётов: {len(voltage_values)}")
data = np.column_stack((time_values, voltage_values, state_values))
np.savetxt('lab.csv',
           data,
           delimiter=',',
           fmt=['%.4f', '%.4f', '%d'],
           header='Время[c],Напряжение[В],GPIO14',
           comments='',
           encoding='utf-8')
print("Данные записаны в lab.csv")

adc_plot.plot_voltage_vs_time(time_values, voltage_values, DYNAMIC_RANGE)
