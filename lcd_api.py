import time

class LcdApi:
    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.clear()

    def clear(self):
        self.move_to(0, 0)
        self.write_command(0x01)
        time.sleep_ms(2)

    def move_to(self, row, col):
        self.cursor_x = col
        self.cursor_y = row
        address = col + 0x40 * row
        self.write_command(0x80 | address)

    def putchar(self, char):
        self.write_data(ord(char))

    def putstr(self, string):
        for char in string:
            self.putchar(char)

    def hide_cursor(self):
        self.write_command(0x0C)

    def show_cursor(self):
        self.write_command(0x0E)

    def blink_cursor_on(self):
        self.write_command(0x0F)

    def blink_cursor_off(self):
        self.write_command(0x0C)

    def display_on(self):
        self.write_command(0x0C)

    def display_off(self):
        self.write_command(0x08)

    def backlight_on(self):
        pass

    def backlight_off(self):
        pass

    def write_command(self, cmd):
        raise NotImplementedError

    def write_data(self, data):
        raise NotImplementedError
