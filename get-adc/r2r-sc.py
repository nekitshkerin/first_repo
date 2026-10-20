from r2r_adc import R2R_ADC
from adc_plot import plot_voltage_vs_time, plot_sampling_period_hist
import time


voltage_values = []
time_values = []

duration = 3.0
dynamic_range = 3.3

adc = None

try:
    adc = R2R_ADC(dynamic_range, compare_time=0.0001)

    start_time = time.time()

    while time.time() - start_time < duration:
        voltage = adc.get_sc_voltage()
        current_time = time.time() - start_time

        voltage_values.append(voltage)
        time_values.append(current_time)

    if len(time_values) > 0:
        plot_voltage_vs_time(time_values, voltage_values, dynamic_range)

    if len(time_values) > 1:
        plot_sampling_period_hist(time_values)

finally:
    if adc is not None:
        adc.deinit()

