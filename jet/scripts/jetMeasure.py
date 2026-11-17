import os
import sys
import time

import numpy as np
import jetFunctions as j

# Запуск из папки jet/scripts:
#   python3 jetMeasure.py "00 mm" 40              - профиль, 40 точек
#   python3 jetMeasure.py "calibration/00 Pa" 50 0 - калибровка, трубка стоит

name = sys.argv[1]                # имя файла без .txt
count = 60                        # точек в профиле
steps_between = 28                # шагов между точками (28 шагов = 1 мм)
samples = 10                      # отсчётов в одной точке

if len(sys.argv) > 2:
    count = int(sys.argv[2])
if len(sys.argv) > 3:
    steps_between = int(sys.argv[3])

filename = '../data/' + name + '.txt'
os.makedirs(os.path.dirname(filename), exist_ok=True)

rows = []
start_time = time.time()

try:
    # 1. Включаем АЦП и двигатель
    j.initSpiAdc()
    j.initStepMotorGpio()

    # 2. Проходим count точек
    for i in range(count):
        # отсчёты в точке, пауза: новый результат АЦП 10 раз в секунду
        values = []
        for k in range(samples):
            values.append(j.getAdc())
            time.sleep(0.05)

        # медиана не боится сбойных отсчётов
        rows.append((i * steps_between, np.median(values)))
        print(f'{i + 1}/{count}: шаг {i * steps_between}, отсчёт {np.median(values):.1f}')

        # сдвиг и пауза, чтобы датчик успокоился
        j.stepForward(steps_between)
        time.sleep(0.2)

    # 3. Возвращаем трубку в начало
    j.stepBackward(count * steps_between)

finally:
    j.deinitSpiAdc()
    j.deinitStepMotorGpio()

# 4. Сохраняем: шаг и отсчёт, по строке на точку
duration = time.time() - start_time
header = (f'jet lab, {name}, {time.strftime("%Y-%m-%d %H:%M:%S")}\n'
          f'points {count}, steps between {steps_between}, '
          f'samples per point {samples}, duration {duration:.0f} s\n'
          f'step adc')

np.savetxt(filename, np.array(rows), fmt=['%d', '%.1f'], header=header)
print(f'Точек: {len(rows)}, данные записаны в {filename}')
