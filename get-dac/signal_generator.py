"""Общая математика сигналов. Этот модуль можно использовать и без платы."""

import time
import numpy as np


def get_sin_wave_amplitude(freq, current_time):
    """Значение синусоиды от 0 до 1 в момент current_time (секунды)."""
    return (np.sin(2 * np.pi * freq * current_time) + 1) / 2


def get_triangle_wave_amplitude(freq, current_time):
    """Значение треугольного сигнала от 0 до 1: сначала рост, потом спад."""
    phase = (freq * current_time) % 1  # Доля текущего периода: от 0 до 1.
    if phase < 0.5:
        return 2 * phase             # Первая половина: от 0 до 1.
    return 2 * (1 - phase)            # Вторая половина: от 1 до 0.


def wait_for_sampling_period(sampling_frequency, started_at=None):
    """Пауза на период; если передано начало шага, вычесть время вычислений."""
    if not np.isfinite(sampling_frequency) or sampling_frequency <= 0:
        raise ValueError("Частота дискретизации должна быть положительной")

    period = 1 / sampling_frequency
    if started_at is None:
        delay = period
    else:
        delay = period - (time.perf_counter() - started_at)

    if delay > 0:
        time.sleep(delay)


def validate_parameters(amplitude, signal_frequency, sampling_frequency,
                        dynamic_range):
    """Проверить настройки до включения оборудования."""
    if not np.isfinite(dynamic_range) or dynamic_range <= 0:
        raise ValueError("Диапазон ЦАП должен быть положительным")
    if not np.isfinite(amplitude) or not 0 <= amplitude <= dynamic_range:
        raise ValueError("Амплитуда должна лежать в диапазоне ЦАП")
    if not np.isfinite(signal_frequency) or signal_frequency <= 0:
        raise ValueError("Частота сигнала должна быть положительной")
    if (not np.isfinite(sampling_frequency)
            or sampling_frequency <= 2 * signal_frequency):
        raise ValueError("Частота дискретизации должна быть выше 2 * f сигнала")
    # Это лишь минимальная проверка. Для наглядного треугольника нужно
    # существенно больше точек: например, 100 на период, как в наших скриптах.

