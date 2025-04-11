from machine import Pin, ADC, I2C
from time import sleep
import dht
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import ssd1306

# Initialize DHT22 (GPIO15)
sensor = dht.DHT22(Pin(20))

# MQ135 Air Quality Sensor (ADC0 - GP26)
# mq135 = ADC(0)
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(10), sda=Pin(9))
print(i2c.scan())


# I2C LCD (0x27 address) on I2C0 (GP0=SDA, GP1=SCL)
lcd_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
lcd = I2cLcd(lcd_i2c, 0x27, 2, 16)

# OLED Display on I2C1 (GP5=SCL, GP4=SDA)
oled_i2c = I2C(1, scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 64, oled_i2c)

def read_air():
    raw = mq135.read_u16()
    return round(raw / 65535 * 100, 2)  # Convert to percentage

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        air = read_air()

        print(f"Temp: {temp}°C, Humidity: {hum}%, Air Quality: {air}%")

        # LCD Output
        lcd.clear()
        lcd.putstr(f"T:{temp}C H:{hum}%\nAir:{air}%")

        # OLED Output
        oled.fill(0)
        oled.text("ENV MONITOR", 15, 0)
        oled.text(f"Temp: {temp} C", 0, 20)
        oled.text(f"Hum : {hum} %", 0, 35)
        oled.text(f"Air : {air} %", 0, 50)
        oled.show()

        sleep(15)

    except Exception as e:
        print("Error:", e)
        sleep(5)
