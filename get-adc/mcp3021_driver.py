"""Чтение 10-битного MCP3021 на I2C-1, адрес 0x4D."""

import argparse
import math
import time

from smbus2 import SMBus, i2c_msg


class MCP3021:
    def __init__(self, dynamic_range, verbose=False):
        # dynamic_range — измеренное питание VDD микросхемы, в В.
        if not math.isfinite(dynamic_range) or dynamic_range <= 0:
            raise ValueError("Диапазон должен быть положительным числом")
        self.dynamic_range = dynamic_range
        self.verbose = verbose
        self.address = 0x4D
        self.bus = SMBus(1)
        self._closed = False

    def get_number(self):
        # У MCP3021 нет регистра с адресом 0: читаем сразу два байта.
        message = i2c_msg.read(self.address, 2)
        self.bus.i2c_rdwr(message)
        upper_data_byte, lower_data_byte = list(message)
        # Первый байт: 0000 D9 D8 D7 D6. Второй: D5 ... D0 X X.
        number = ((upper_data_byte & 0x0F) << 6) | (lower_data_byte >> 2)
        if self.verbose:
            print(f"Байты: {upper_data_byte:02X} {lower_data_byte:02X}; код: {number}")
        return number

    def get_voltage(self):
        return self.get_number() * self.dynamic_range / 1024

    def deinit(self):
        if not self._closed:
            self.bus.close()
            self._closed = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--range", dest="dynamic_range", type=float, required=True,
                        help="Измеренное питание MCP3021, В")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    adc = None
    try:
        adc = MCP3021(args.dynamic_range, args.verbose)
        while True:
            print(f"Напряжение: {adc.get_voltage():.4f} В")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nИзмерения остановлены")
    finally:
        if adc is not None:
            adc.deinit()
