from machine import Pin, I2C, UART, ADC
from time import sleep
import dht
from lcd_api import LcdApi
from i2c_lcd import I2cLcd



from machine import Pin, UART
from time import sleep

def send_cmd(uart, cmd, delay=1000):
    print(f"Sending: {cmd}")
    uart.write(cmd + "\r\n")
    sleep(delay / 1000)
    response = b""
    while uart.any():
        response += uart.read()
    print(f"Raw bytes: {response}")
    try:
        decoded = response.decode()
        print(f"Decoded: {decoded}")
    except:
        print("Cannot decode response")
    return response

def test_baud_rates():
    baud_rates = [9600, 19200, 38400, 57600, 115200, 74880]
    for baud in baud_rates:
        print(f"\nTesting baud rate: {baud}")
        uart = UART(1, baudrate=baud, tx=Pin(4), rx=Pin(5))
        send_cmd(uart, "AT+RST", 5000)
        send_cmd(uart, "AT", 2000)
        send_cmd(uart, "AT+GMR", 2000)
        uart.deinit()

test_baud_rates()
# ========== LCD SETUP ==========
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()

# ========== SENSOR SETUP ==========
sensor = dht.DHT22(Pin(14))  # DHT22 on GP14
mq135 = ADC(0)  # MQ135 analog on GP26 (ADC0)

# ========== ESP UART SETUP ==========
uart = UART(1, tx=Pin(4), rx=Pin(5))

# ========== WIFI CREDENTIALS ==========
SSID = "John Network"
PASSWORD = "$*CO8I3m"
THINGSPEAK_API_KEY = 'IS28D2SJ28KAHFC3'


def send_cmd(cmd, delay=1000):
    print(f"Sending: {cmd}")
    uart.write(cmd + "\r\n")
    sleep(delay / 1000)
    response = ""
    while uart.any():
        response += uart.read().decode()
    print(f"Response: {response}")
    return response

def test_uart():
    print("Testing UART...")
    response = send_cmd("AT")
    print("AT response:", response)
    response = send_cmd("AT+GMR")
    print("Firmware response:", response)
test_uart()

def connect_to_wifi():
    print("Connecting to Wi-Fi...")
    send_cmd("AT")
    send_cmd("AT+CWMODE=1")
    response = send_cmd(f'AT+CWJAP="{SSID}","{PASSWORD}"', delay=15000)
    print("Raw Wi-Fi response:", response)
    # Check for success indicators
    if "WIFI CONNECTED" in response or "WIFI GOT IP" in response or "+CWJAP:0" in response or "OK" in response:
        print("Wi-Fi likely connected!")
        ip_response = send_cmd("AT+CIFSR")
        print("IP response:", ip_response)
        lcd.clear()
        lcd.putstr("Wi-Fi OK")
    else:
        print("Wi-Fi connection failed!")
        lcd.clear()
        lcd.putstr("Wi-Fi Failed")
    sleep(5)

def send_to_thingspeak(temp, hum, air):
    try:
        print("Sending to ThingSpeak...")
        send_cmd('AT+CIPSTART="TCP","api.thingspeak.com",80', delay=3000)
        query = f"GET /update?api_key={THINGSPEAK_API_KEY}&field1={temp}&field2={hum}&field3={air} HTTP/1.1\r\nHost: api.thingspeak.com\r\n\r\n"
        send_cmd(f'AT+CIPSEND={len(query)}', delay=1000)
        uart.write(query)
        print("Data sent!")
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Success...")
        sleep(3)
    except Exception as e:
        print("Send failed:", e)
        lcd.clear()
        lcd.putstr("Send Failed")
        sleep(3)

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

        send_to_thingspeak(temp, hum, air)
        sleep(15)

    except Exception as e:
        print("Error:", e)
        lcd.clear()
        lcd.putstr("Sensor Error")
        sleep(5)