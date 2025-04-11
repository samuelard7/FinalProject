from lcd_api import LcdApi
from machine import I2C
from time import sleep_ms

class I2cLcd(LcdApi):
    ENABLE = 0b00000100
    BACKLIGHT = 0b00001000

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = self.BACKLIGHT
        self.num_lines = num_lines
        self.num_columns = num_columns

        sleep_ms(50)
        self._write_init_nibble(0x03)
        sleep_ms(5)
        self._write_init_nibble(0x03)
        sleep_ms(1)
        self._write_init_nibble(0x03)
        self._write_init_nibble(0x02)

        self.write_command(0x28)  # Function set: 4-bit, 2 line
        self.write_command(0x0C)  # Display on, cursor off
        self.write_command(0x06)  # Entry mode set
        self.clear()

        super().__init__(num_lines, num_columns)

    def _write_byte(self, data):
        self.i2c.writeto(self.i2c_addr, bytes([data | self.backlight]))

    def _pulse(self, data):
        self._write_byte(data | self.ENABLE)
        sleep_ms(1)
        self._write_byte(data & ~self.ENABLE)
        sleep_ms(1)

    def _write_init_nibble(self, nibble):
        self._pulse(nibble << 4)

    def write_command(self, cmd):
        self._write_nibble(cmd >> 4)
        self._write_nibble(cmd & 0x0F)

    def write_data(self, data):
        self._write_nibble(data >> 4, rs=True)
        self._write_nibble(data & 0x0F, rs=True)

    def _write_nibble(self, nibble, rs=False):
        data = nibble << 4
        if rs:
            data |= 0x01
        self._pulse(data)
