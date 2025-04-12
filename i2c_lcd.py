from lcd_api import LcdApi
from machine import I2C
from time import sleep_ms

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = 0x08
        self.init_lcd()
        super().__init__(num_lines, num_columns)

    def init_lcd(self):
        sleep_ms(50)
        self.hal_write_command(0x33)
        self.hal_write_command(0x32)
        self.hal_write_command(0x28)
        self.hal_write_command(0x0C)
        self.hal_write_command(0x06)
        self.clear()

    def hal_write_command(self, cmd):
        self.send(cmd, 0)

    def hal_write_data(self, data):
        self.send(data, 1)

    def send(self, data, mode):
        high = data & 0xF0
        low = (data << 4) & 0xF0
        self.write4bits(high | mode | self.backlight)
        self.write4bits(low | mode | self.backlight)

    def write4bits(self, data):
        self.i2c.writeto(self.i2c_addr, bytearray([data | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytearray([data & ~0x04]))

    def backlight_on(self):
        self.backlight = 0x08
        self.send(0x00, 0)

    def backlight_off(self):
        self.backlight = 0x00
        self.send(0x00, 0)
