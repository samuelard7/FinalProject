import machine
import time
from time import sleep
import ubinascii
import ustruct
import dht
from i2c_lcd import I2cLcd, I2C
from machine import Pin, UART, ADC

count = 1

uart = UART(0, baudrate=9600, tx=Pin(12), rx= Pin(13))

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
lcd = I2cLcd(i2c, 0x27, 2, 16)

sensor = dht.DHT22(Pin(18))
mq135 = ADC(0)

def read_air_quality():
    raw = mq135.read_u16()
    
    # Map raw value (0-65535) to AQI scale (0-500)
    aqi = round((raw / 65535) * 500, 2)

    if aqi > 500:
        aqi = 500
    elif aqi < 0:
        aqi = 0

    return aqi


def read_and_send_data():
    sensor.measure()  
    temp = sensor.temperature() 
    hum = sensor.humidity() 
    air = read_air_quality()
    
    data = "{},{},{}\n".format(temp, hum, air)
    uart.flush()
    uart.write(data)
    print("Data sent to ESP8266:", data)
    
    lcd.clear()
    sleep(0.1)  
    lcd.putstr(f"T:{temp}C H:{hum}%")
    lcd.move_to(0, 1)
    lcd.putstr(f"AQI:{air}")
    sleep(0.1)

while True:
    try:
        if count<21:
            read_and_send_data()
            count = count +1
            time.sleep(6) 
        else:
            break
    except Exception as e:
        print("Sensor Error:", e)
        sleep(5)




