import os
import sys

import numpy as np
import matplotlib.pyplot as plt

# Запуск из папки jet/scripts:
#   python3 jetProcessing.py                   - свои данные из ../data/
#   python3 jetProcessing.py ../data/example/  - пример из стартового набора

data_path = '../data/'
if len(sys.argv) > 1:
    data_path = sys.argv[1]
plots_path = '../plots/'
os.makedirs(plots_path, exist_ok=True)

calibration_steps = 500            # калибровка двигателя: шагов...
calibration_mm = 18                # ...и на сколько мм сдвинулась трубка
distances = [0, 10, 20, 30, 40, 50, 60, 70]   # сечения, мм
rho = 1.2                          # плотность воздуха, кг/м³
n = 5                              # точек края профиля для нуля


# Чтение файла: шаги и отсчёты без сбойных точек
def load_adc(filename):
    data = np.loadtxt(filename)
    steps = data[:, 0]
    adc = data[:, 1]
    good = adc < 500000            # сбой АЦП на порядок больше
    return steps[good], adc[good]


# 1. Калибровка давления: P = k * N + b
cal_adc = []
cal_pressure = []
for name in sorted(os.listdir(data_path + 'calibration')):
    steps, adc = load_adc(data_path + 'calibration/' + name)
    cal_adc.append(np.mean(adc))
    cal_pressure.append(float(name.split()[0]))   # "45 Pa.txt" -> 45

k, b = np.polyfit(cal_adc, cal_pressure, 1)
print(f'k = {k:.4f} Па/отсчёт')

plt.figure(figsize=(8, 6))
plt.plot(cal_adc, cal_pressure, 'o', label='Измерения')
plt.plot(cal_adc, np.polyval([k, b], cal_adc),
         label=f'P = {k:.4f} * N {b:+.0f} [Па]')
plt.title('Калибровка датчика давления')
plt.xlabel('Отсчёт АЦП')
plt.ylabel('Давление, Па')
plt.grid(True)
plt.legend()
plt.savefig(plots_path + 'pressure-calibration.png', dpi=300)


# 2. Калибровка перемещения: x = step_m * шаги
cal_steps = [0, calibration_steps]
cal_mm = [0, calibration_mm]
step_m = calibration_mm / 1000 / calibration_steps
print(f'1 шаг = {step_m:.2e} м')

plt.figure(figsize=(8, 6))
plt.plot(cal_steps, cal_mm, 'o', label='Измерения')
plt.plot(cal_steps, np.array(cal_steps) * step_m * 1000,
         label=f'x = {step_m * 1000:.4f} * шаги [мм]')
plt.title('Калибровка перемещения трубки Пито')
plt.xlabel('Шаги двигателя')
plt.ylabel('Перемещение, мм')
plt.grid(True)
plt.legend()
plt.savefig(plots_path + 'distance-calibration.png', dpi=300)


# 3. Профиль скорости одного сечения
def calculate_velocity(filename):
    steps, adc = load_adc(filename)

    # ноль - прямая между медианами левого и правого края
    left = np.median(adc[:n])
    right = np.median(adc[-n:])
    zero = np.interp(np.arange(len(adc)), [n / 2, len(adc) - n / 2], [left, right])

    # давление
    p = k * (adc - zero)

    # порог: три шума края, но не меньше 3 Па
    edges = np.concatenate((p[:n], p[-n:]))
    threshold = max(3 * np.std(edges), 3)
    p[p < threshold] = 0

    # скорость по Бернулли и координата
    u = np.sqrt(2 * p / rho)
    x = steps * step_m
    return x, u


# 4. Центр профиля: середина между краями по половине максимума
def find_center(x, u):
    half = np.max(u) / 2
    above = np.where(u > half)[0]  # номера точек выше половины
    return (x[above[0]] + x[above[-1]]) / 2


# 5. Расход: сумма трапеций по профилю, делённая на два
def calculate_outgo(x, u):
    r = np.abs(x)
    f = rho * 2 * np.pi * r * u
    q = 0
    for i in range(len(x) - 1):
        q += (f[i] + f[i + 1]) / 2 * (x[i + 1] - x[i])
    return q / 2                   # среднее двух половин, кг/с


# 6. Обрабатываем все сечения
profiles_x = []
profiles_u = []
outgo = []
for d in distances:
    x, u = calculate_velocity(data_path + '%02d mm.txt' % d)
    x = x - find_center(x, u)
    q = calculate_outgo(x, u)
    profiles_x.append(x)
    profiles_u.append(u)
    outgo.append(q)
    print(f'{d:2d} мм: u_max = {np.max(u):.1f} м/с, Q = {q * 1000:.2f} г/с')


# 7. График скоростей
plt.figure(figsize=(10, 6))
for i in range(len(distances)):
    plt.plot(profiles_x[i] * 1000, profiles_u[i], label=f'{distances[i]} мм')
plt.title('Профили скорости в сечениях струи')
plt.xlabel('Расстояние от оси струи, мм')
plt.ylabel('Скорость, м/с')
plt.grid(True)
plt.legend()
plt.savefig(plots_path + 'velocity.png', dpi=300)


# 8. График скоростей с расходами в легенде
plt.figure(figsize=(10, 6))
for i in range(len(distances)):
    plt.plot(profiles_x[i] * 1000, profiles_u[i],
             label='Q (%02d мм) = %.2f [г/с]' % (distances[i], outgo[i] * 1000))
plt.title('Профили скорости и расход в сечениях струи')
plt.xlabel('Расстояние от оси струи, мм')
plt.ylabel('Скорость, м/с')
plt.grid(True)
plt.legend()
plt.savefig(plots_path + 'velocity-outgo.png', dpi=300)


# 9. Расход от расстояния с прямой
outgo_g = np.array(outgo) * 1000
a, c = np.polyfit(distances, outgo_g, 1)
print(f'Прямая: Q = {a:.3f} * L + {c:.2f} [г/с]')

plt.figure(figsize=(8, 6))
plt.plot(distances, outgo_g, 'o', label='Расход в сечении')
plt.plot(distances, np.polyval([a, c], distances),
         label=f'Q = {a:.3f} * L + {c:.2f} [г/с]')
plt.title('Расход струи от расстояния до сопла')
plt.xlabel('Расстояние от сопла, мм')
plt.ylabel('Расход, г/с')
plt.grid(True)
plt.legend()
plt.savefig(plots_path + 'outgo-distance.png', dpi=300)

print(f'Графики сохранены в {plots_path}')
