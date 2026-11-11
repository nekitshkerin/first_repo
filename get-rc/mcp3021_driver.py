import smbus
import time


class MCP3021:
    def __init__(self, dynamic_range, verbose=False):
        self.bus = smbus.SMBus(1)        # шина I2C номер 1 на Raspberry Pi
        self.dynamic_range = dynamic_range
        self.address = 0x4D              # адрес микросхемы MCP3021 на шине
        self.verbose = verbose

    def deinit(self):
        self.bus.close()

    def get_number(self):
        data = self.bus.read_word_data(self.address, 0)
        # Байт, пришедший первым, оказывается в младших 8 битах числа data
        lower_data_byte = data >> 8
        upper_data_byte = data & 0xFF
        # Первый байт: 0000 D9 D8 D7 D6, второй: D5 D4 D3 D2 D1 D0 X X
        number = (upper_data_byte << 6) | (lower_data_byte >> 2)
        if self.verbose:
            print(f"Данные: {data}, старший байт: {upper_data_byte:x}, младший байт: {lower_data_byte:x}, число: {number}")
        return number

    def get_voltage(self):
        # 10-битный АЦП: 2**10 = 1024 уровня на весь динамический диапазон
        return self.get_number() * self.dynamic_range / 1024


if __name__ == "__main__":
    adc = MCP3021(5.186)  # питание MCP3021, измеренное мультиметром на контакте PWR блока AUX
    try:
        while True:
            print(f"Напряжение: {adc.get_voltage():.3f} В")
            time.sleep(1)
    finally:
        adc.deinit()
