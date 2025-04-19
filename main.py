from machine import Pin, I2C, UART, SPI
from time import sleep
import dht
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

import network
import urequests as requests


# SPI setup (Pico as master to NodeMCU)
sck = Pin(16)
mosi = Pin(17)
miso = Pin(18)
cs = Pin(19, Pin.OUT)
spi = SPI(0, sck=sck, mosi=mosi, miso=miso, cs=cs, baudrate=100000)
# ========== LCD SETUP ==========
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()

# ========== SENSOR SETUP ==========
sensor = dht.DHT22(Pin(14))  # DHT22 on GP14
#mq135 = ADC(0)  # MQ135 analog on GP26 (ADC0)


# ========== WIFI CREDENTIALS ==========
SSID = "John Network - 1"
PASSWORD = "iMshd897$)*#"
THINGSPEAK_API_KEY = 'IS28D2SJ28KAHFC3'


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        sleep(1)
        print("Connecting to Wi-Fi...")
    print("Connected:", wlan.ifconfig())

    print("NodeMCU SPI slave ready")
    sleep(5)

# def send_to_thingspeak(temp, hum, air):
#     try:
#         while True:
#             if cs.value() == 0:  # CS low indicates data
#                 data = spi.read(16)  # Read up to 16 bytes
#                 data_str = "".join(chr(b) for b in data if b)  # Convert non-zero bytes
#                 if data_str:
#                     print("Received:", data_str)
#                     try:
#                         url = f"http://api.thingspeak.com/update?api_key=YOUR_API_KEY&{data_str}"  # Replace with your ThingSpeak API key
#                         response = requests.get(url)
#                         print("ThingSpeak response:", response.text)
#                         response.close()
#                     except Exception as e:
#                         print("ThingSpeak Error:", e)
#                 spi.write(b"ACK")  # Acknowledge
#             sleep(0.1)
#     except Exception as e:
#         print("Send failed:", e)
#         lcd.clear()
#         lcd.putstr("Send Failed")
#         sleep(3)
def send_to_thingspeak(temp, hum, air):
    try:
        print("Sending to ThingSpeak...")
        send_cmd('AT+CIPSTART="TCP","api.thingspeak.com",80', delay=3000)
        query = f'GET /update?api_key={THINGSPEAK_API_KEY}&field1={temp}&field2={hum}&field3={air}'
        send_cmd(f'AT+CIPSEND={len(query)+2}', delay=1000)
        uart.write(query + "\r\n")
        sleep(3)
    except Exception as e:
        print("Send failed:", e)
        
        
def read_air_quality():
    raw = mq135.read_u16()
    percent = round((raw / 65535) * 100, 2)
    return percent

# Start
connect_to_wifi()

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        # air = read_air_quality()
        air = 0

        print(f"T: {temp}°C | H: {hum}% | AQ: {air}%")

        # LCD Display
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(f"T:{temp}C H:{hum}%")
        sleep(3)
        lcd.move_to(0, 1)
        lcd.putstr(f"Air: {air}%")
        sleep(3)
        cs.off()
        spi.write(bytes(data, 'utf-8'))
        response = spi.read(3)
        cs.on()
        send_to_thingspeak(temp, hum, air)
        sleep(15)

    except Exception as e:
        print("Error:", e)
        lcd.clear()
        lcd.putstr("Sensor Error")
        sleep(5)