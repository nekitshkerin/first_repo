import numpy as np
import matplotlib.pyplot as plt

charge_time = 50.0   # продолжительность зарядки, с (как в rc-measure.py)
R = 1e6              # сопротивление резистора по номиналу, Ом (подставьте со своей платы)
C = 10e-6            # ёмкость конденсатора по номиналу, Ф (подставьте со своей платы)

# 1. Загружаем данные из data.csv
data = np.loadtxt('data.csv',
                  delimiter=',',
                  skiprows=1,
                  encoding='utf-8')

time = data[:, 0].astype(float)
voltage = data[:, 1].astype(float)

# 2. Зарядка: максимальное напряжение и уровень 63 % от него
u_max = 0
for i in range(len(time)):
    if time[i] < charge_time and voltage[i] > u_max:
        u_max = voltage[i]

charge_level = 0.632 * u_max

# Первый момент, когда напряжение дошло до 63 % — это и есть τ
for i in range(len(time)):
    if voltage[i] >= charge_level:
        tau_charge = time[i]
        break

# 3. Разрядка: начальное напряжение и уровень 37 % от него
for i in range(len(time)):
    if time[i] >= charge_time:
        u_start = voltage[i]
        break

discharge_level = 0.368 * u_start

# Первый момент разрядки, когда напряжение упало до 37 %; τ считаем от начала разрядки
for i in range(len(time)):
    if time[i] >= charge_time and voltage[i] <= discharge_level:
        tau_discharge = time[i] - charge_time
        break

tau_nominal = R * C

print(f"Зарядка:  U_max = {u_max:.3f} В, уровень 63 % = {charge_level:.3f} В, τ = {tau_charge:.2f} с")
print(f"Разрядка: U_0 = {u_start:.3f} В, уровень 37 % = {discharge_level:.3f} В, τ = {tau_discharge:.2f} с")
print(f"По номиналам: τ = RC = {tau_nominal:.2f} с")

# 4. График напряжения от времени с отмеченными точками τ
plt.figure(figsize=(10, 6))
plt.plot(time, voltage, label='Измерения')
plt.plot(tau_charge, charge_level, 'o', color='red', markersize=8,
         label=f'63 % при зарядке: τ = {tau_charge:.2f} с')
plt.plot(charge_time + tau_discharge, discharge_level, 'o', color='green', markersize=8,
         label=f'37 % при разрядке: τ = {tau_discharge:.2f} с')
plt.title('Напряжение на конденсаторе RC-цепи')
plt.xlabel('Время, с')
plt.ylabel('Напряжение, В')
plt.xlim(0, max(time))
plt.ylim(0, u_max * 1.1)
plt.grid(True)
plt.legend()

# Вместо plt.show() сохраняем график в файл для отчёта
plt.savefig('rc-plot.png', dpi=300)
print("График сохранён в rc-plot.png")
