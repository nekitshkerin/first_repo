"""Графики напряжения и интервалов между отсчётами."""

import matplotlib.pyplot as plt


def plot_voltage_vs_time(time, voltage, max_voltage):
    if len(time) != len(voltage):
        raise ValueError("Списки времени и напряжения должны иметь одинаковую длину")
    if not time:
        print("Нет измерений для построения графика")
        return
    plt.figure(figsize=(10, 6))
    plt.plot(time, voltage, marker=".", markersize=3)
    plt.title("Напряжение на входе АЦП")
    plt.xlabel("Время от начала опыта, с")
    plt.ylabel("Напряжение, В")
    plt.xlim(0, max(time[-1], 0.001))
    plt.ylim(0, max_voltage)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_sampling_period_hist(time):
    if len(time) < 2:
        print("Для гистограммы нужны хотя бы два измерения")
        return
    sampling_periods = []
    for index in range(1, len(time)):
        period = time[index] - time[index - 1]
        if period <= 0:
            raise ValueError("Метки времени должны строго возрастать")
        sampling_periods.append(period)
    plt.figure(figsize=(10, 6))
    plt.hist(sampling_periods, bins=20, edgecolor="black")
    plt.title("Распределение интервалов между измерениями")
    plt.xlabel("Интервал между отсчётами, с")
    plt.ylabel("Количество интервалов")
    # В методичке 0.06 с. Автомасштаб нужен, чтобы не скрыть медленные отсчёты.
    plt.xlim(0, max(sampling_periods) * 1.1)
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.show()
