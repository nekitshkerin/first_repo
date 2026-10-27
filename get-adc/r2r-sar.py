"""АЦП последовательного приближения: сбор измерений, график и гистограмма."""

import argparse
import math
import time

from r2r_adc import R2R_ADC
import adc_plot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--range", dest="dynamic_range", type=float, required=True,
                        help="Измеренное U_DAC при коде 255, В")
    parser.add_argument("--duration", type=float, default=3.0,
                        help="Продолжительность опыта, с")
    args = parser.parse_args()
    duration = args.duration
    if not math.isfinite(duration) or duration <= 0:
        parser.error("Продолжительность должна быть положительным числом")

    voltage_values = []
    time_values = []
    adc = None
    try:
        adc = R2R_ADC(args.dynamic_range, compare_time=0.0001)
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < duration:
            voltage = adc.get_sar_voltage()
            elapsed = time.perf_counter() - start_time
            voltage_values.append(voltage)
            time_values.append(elapsed)
    except KeyboardInterrupt:
        print("\nОпыт прерван, показываем накопленные данные")
    finally:
        if adc is not None:
            adc.deinit()

    # Аппаратура уже освобождена; ожидание закрытия окон не удерживает GPIO/I2C.
    print(f"Получено отсчётов: {len(voltage_values)}")
    adc_plot.plot_voltage_vs_time(time_values, voltage_values, args.dynamic_range)
    adc_plot.plot_sampling_period_hist(time_values)


if __name__ == "__main__":
    main()
