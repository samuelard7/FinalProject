class LcdApi:
    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns

    def clear(self):
        self.hal_write_command(0x01)
        self.hal_write_command(0x02)

    def putstr(self, string):
        for char in string:
            self.hal_write_data(ord(char))

    def move_to(self, col, row):
        addr = col + 0x40 * row
        self.hal_write_command(0x80 | addr)

    def hal_write_command(self, cmd): pass
    def hal_write_data(self, data): pass
