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
