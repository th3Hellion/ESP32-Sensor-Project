import machine
import dht
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from machine import Pin, SoftI2C
from time import sleep
from umqtt.simple import MQTTClient
import keys

# Constants
I2C_ADDR = 0x3f
TOTAL_ROWS = 2
TOTAL_COLUMNS = 16
MQTT_SERVER = keys.url
MQTT_PORT = 1883
MQTT_TOPIC = keys.topic

# Initialize peripherals
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)
lcd = I2cLcd(i2c, I2C_ADDR, TOTAL_ROWS, TOTAL_COLUMNS)
sensor = dht.DHT11(Pin(15))

def send_sensor_data(temp, hum):
    payload = {
        'temperature': temp,
        'humidity': hum
    }
    client = MQTTClient("client_id", MQTT_SERVER, MQTT_PORT,keepalive=30)
    client.connect()
    message = "{ \"temperature\": %f, \"humidity\": %f}" % (temp,hum)
    client.publish(MQTT_TOPIC, message)
    client.disconnect()
    print('Sensor data sent successfully')

while True:
    try:
        lcd.clear()
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        print('Temperature: %3.1f C' % temp)
        print('Humidity: %3.1f %%' % hum)

        lcd.putstr('Temp: %2.0f C\n' % temp)
        lcd.putstr('Humidity: %2.0f%%' % hum)

        try:
            send_sensor_data(temp, hum)
        except Exception as e:
            print('Failed to send sensor data:', e)
        sleep(10)
        
    except OSError as e:
        print('Failed to read sensor.')
