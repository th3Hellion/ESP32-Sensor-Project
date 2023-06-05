# Battery Powered Temperature and Humidity Weather Station

**Name:** Nikita Grishin ng222jk
https://hackmd.io/@lnu-iot/iot-tutorial

## Short project overview

This tutorial describes how to create own battery powered temperature and humidity weather station that displays and sends data to a remote server and presents the data as a graph on a webpage.
Dependent on experience this project could be completed in 1-2 hours.

## Objective

This project aims to effectively monitor the room temperature in households, catering to the needs of both humans and pets. By ensuring the ideal temperature and humidity levels are maintained, it contributes to a comfortable living environment and the well-being of residents and their animal companions.
While the design of this monitoring system may be simple, its applications span across various areas, offering numerous benefits to different environments. Its versatility and effectiveness make it an ideal choice for my project, catering to the needs of homes, stores and animal living areas.

## Material

For the project, I have used the following items:

- ESP32
- DHT11 Temperature and Humidity sensor
- Breadboard x 2
- LCD Display
- 9V Battery
- Breadboard Power Module
- Jumper wires

| Item                                                                                                                                                            | Link                                                                                                                             | Price      |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| ESP32                                                                                                                                                           | [ESP32 Link](https://www.amazon.de/-/en/Espressif-Development-Bluetooth-WROOM32-NodeMCU/dp/B07K68RQTS/261-5749575-9981741?psc=1) | 11.00 EUR  |
| Freenove RFID Starter Kit for Raspberry Pi (includes DHT11 Temperature and Humidity Sensor, Breadboard x 2, LCD Display, Breadboard Power Module, Jumper wires) | [Starter Kit for Raspberry Pi](https://www.amazon.de/-/en/Raspberry-Processing-53-Projects-391-pages-Components/dp/B06VTH7L28)   | 36.95 EUR  |
| 9V Battery                                                                                                                                                      |                                                                                                                                  |            |
## Computer setup

### Install Thonny

The IDE I chose to use for this project is Thonny. Thonny is a free and user-friendly Python IDE that is suitable. It provides a simple and intuitive interface, making it easy to write and debug Python code.

install Thonny IDE:

1. Visit the Thonny website.
2. Download the appropriate version for your operating system.
3. Run the installer file.
4. Follow the on-screen instructions to complete the installation.
The code then can be uploaded from the IDE interface by saving it on the microcontroller

### Flash Firmware

1. Followed [this](https://randomnerdtutorials.com/getting-started-thonny-micropython-python-ide-esp32-esp8266/) tutorial to get my ESP32 ready to work with. Flashing the firmware involves using Thonny, which makes it convenient.
2. Connect the ESP32 via USB cable to a computer with Thonny running.
3. Select "MicroPython ESP32" as the interpreter.
4. Click on "Install or update firmware."
5. A window will open where you need to specify a port. It should be the only option on the list if you don't have any other devices connected.
6. Download the firmware from the MicroPython official website [here](https://micropython.org/download/esp32/).
7. Browse and select the downloaded .bin file.
8. Click on "Install" to flash the firmware.

## Putting everything together

The image below illustrates how I have set up my project. I have used **red** wires for power,**black** for ground, other for data and clock.
I am supplying the power to DHT11 sensor with 3.3V. Then I have a data pin connected to pin 15 on ESP32. After the sensor is connected I have setup the LCD screen. LCD scren requires more power therfore I am supplying it with 5V. The SDA pin is connected to pin 21 and SCL is on pin 22. Other red and black wires are present and are used for additional power and grounding. From my power module I am using one pin of 5V to connect to microcontroller to power it.
  
This design is only meant for testing and development, mainly because nothing has been permanently connected. The wires can easily be removed from the breadboard, which can cause it to stop working properly. Another reason it's not ready for production is that there is no protective covering, so everything is at risk of being damaged by the environment. The wires are prone to breaking, and the whole unit could get damaged if it comes into contact with water.
![Alt text](/img/Fritzing.png)

## Platform

I have decided to use a TIG stack, it stands for:

**Telegraf**: Telegraf is a plugin-driven server agent that collects and sends metrics and data from various sources to the InfluxDB time series database. It supports a wide range of input plugins to gather data from systems, services, and APIs. Telegraf ensures that data is collected efficiently and reliably.

**InfluxDB**: InfluxDB is a powerful time series database designed to store and retrieve high volumes of time-stamped data. It provides a scalable solution for storing metrics, events, and logs. InfluxDB allows for efficient querying and flexible retention policies, making it suitable for storing and analyzing time-based data.

**Grafana**: Grafana is a feature-rich open-source platform for data visualization and analytics. It connects to data sources such as InfluxDB and provides a user-friendly interface to create dashboards and visualizations. Grafana offers a wide range of visualization options, alerting capabilities, and supports sharing and collaboration.

### Optional setup Mosquitto

I chose to host everything locally so MQTT broker will also need to be setup

```yaml
version: "3"
services:
  mosquitto:
    image: eclipse-mosquitto
    container_name: mosquitto
    ports:
      - 1883:1883
      - 9001:9001
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./data:/mosquitto/data
      - ./log:/mosquitto/log
```

In the mosquitto.conf file we need to specify the following fiels

```conf
listener 1883
protocol mqtt
listener 9001
protocol websockets
allow_anonymous true
```

and then run it with

`docker run -d --name mosquitto -p 1883:1883 -p 9001:9001 -v $(pwd)/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto
`

Now the MQTT broker should be accessible. You can check it with MQTT Explorer
![Alt text](/img/image-5.png)
If you are able to connect then you are sure that it is working, you also can inspect the data coming in.

### Setup a TIG stack

I chose to setup visualization stack by running all of it inside of a docker container, to do that I used docker compose to easily pull the images and make the containers. I mark ports from the container to my local machine this is so that I can access it from `localhost` and make volumes this is to preserve the data and the setting done after restarting the container.

```yaml
version: "3"
services:
  telegraf:
    image: telegraf
    container_name: telegraf
    volumes:
      - ./telegraf.conf:/etc/telegraf/telegraf.conf:ro

  influxdb:
    image: influxdb
    container_name: influxdb
    ports:
      - 8086:8086
    volumes:
      - ./influxdb:/var/lib/influxdb

  grafana:
    image: grafana/grafana
    container_name: grafana
    ports:
      - 3000:3000
    volumes:
      - ./grafana:/var/lib/grafana
```

Then I have used `docker-compose up -d
` to create all of them.

### Configure telegraf

To make telegraf work it needs a config file, in this file it is needed to configure telegraf's behavior, where it gets the data and where it sends the data. In this config I specify `InfluxDB` as the database where the data should be submitted and `mqtt` where the data should come from.

```conf
[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "10s"
  flush_jitter = "0s"
  precision = ""
  hostname = "your host name"
  omit_hostname = false

[[outputs.influxdb_v2]]

  urls = ["http://influxdb:8086"]
  token = "token from influx db"
  organization = "your organization"
  bucket = "you database bucket"

[[inputs.mqtt_consumer]]

  servers = ["mqtt server address"]
  qos = 2
  connection_timeout = "30s"
  topics = ["topic"]
  data_format = "json"
```

After this has been configured we no longer need to interact with the middleware.

### InfluxDB setup

Go to `localhost:8086`, on first login InfluxDB will prompt to create a user account together with an organization and a bucket. You will receive a token it is needed for the `telegraf` config file or if you happen to lose it you can generate a new one by clicking `Generate new token`

![Alt text](/img/image.png)

Go to `Data Explorer`, from it you will see a Query constructor
![Alt text](/img/image-1.png)
Click around and select the data you want to see, this is needed to give the proper query for the Grafana data source, click on **Script Editor** and copy the query, we will use it later in Grafana setup.
![Alt text](/img/image-2.png)

### Grafana setup

Go to `localhost:3000` there you can login with `username`: `admin` and `password`: `admin` you will be prompted to change it, do that.
After that we need to create a dashboard go to the left side menu -> dashboards and under the `New` button click `New Dashboard`, Then Add visualization, you will be prompted to select a data source, since we are using InfluxDB we need to select that.
![Alt text](/img/image-3.png)
Paste previously copied query in to the input area.

Now we have the data coming from the database to our Grafana page. Additionally you can customise it as you wish, changing colours and line thickness.

## The code

main.py file

```python
import machine
import dht
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from machine import Pin, SoftI2C
from time import sleep
from umqtt.simple import MQTTClient
import keys

I2C_ADDR = 0x3f
TOTAL_ROWS = 2
TOTAL_COLUMNS = 16
MQTT_SERVER = keys.url
MQTT_PORT = 1883
MQTT_TOPIC = keys.topic

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)
lcd = I2cLcd(i2c, I2C_ADDR, TOTAL_ROWS, TOTAL_COLUMNS)
sensor = dht.DHT11(Pin(15))

def send_sensor_data(temp, hum):
    payload = {
        'temperature': temp,
        'humidity': hum
    }
    client = MQTTClient('client_id', MQTT_SERVER, MQTT_PORT,keepalive=30)
    client.connect()
    message = '{ \"temperature\": %f, \"humidity\": %f}' % (temp,hum)
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

```

boot.py file

```python
import keys
import network

def connect_to_wifi():
    wifi_ssid = keys.ssid
    wifi_password = keys.wifi_pass

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    try:
        wifi.connect(wifi_ssid, wifi_password)
        return wifi.ifconfig()[0]
    except Exception as e:
        print("Failed to connect to Wi-Fi:", e)
        return None

ip_address = connect_to_wifi()
if ip_address:
    print("Connected to Wi-Fi")
    print("IP address:", ip_address)
```

## Transmitting the data / connectivity

As previously stated my Esp32 microcontroller has been programmed to connect to my WiFi network and uses my self hosted MQTT broker Mosquitto to transmit data to other devices. The below code represents that the Esp32 device measuring another reading. The delaystime can be adjusted to personal preferencing but since I am self hosting it I can allow myself to read it more frequintly, every 10 seconds, but the more time the device is sleeping the more you save on the battery’s life.
```python
    message = "{ \"temperature\": %f, \"humidity\": %f}" % (temp,hum)
    client.publish(MQTT_TOPIC, message)
    client.disconnect()
```

## Presenting the data

The TIG stack is convenient for setting up various user-friendly dashboards for multiple projects.

I have configured the dashboard to display the current temperature and humidity levels. Additionally, I have created two graphs to track these levels on a hourly basis. You can adjust the time period of these graphs based on how you want to analyze the data. Datacake instantly saves newly recorded data in its database.

Since I am self hosting ut, my data can be stored for any amount of time in the database. Examining this data can also assist in identifying the best moments to activate or deactivate cooling/heating systems, promoting a greener and more sustainable environment.
Finally the dashboard looks like this
![Alt text](/img/image-4.png)

## Final design

I really enjoyed working on this project, and it made me realize how much we rely on simple technology in our daily lives. I wish I had more time to create a more complex design, but I fell a bit behind because I had to wait for the Heltec devices, which were hard to find. Despite that, setting up this project was pretty straightforward, thanks to all the parts involved.
![Alt text](/img/IMG_2146.jpg)
