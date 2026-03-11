import network
import time
from simple import MQTTClient

# WiFi & MQTT Config
SSID = "ece270-5"               #Replace with the Access Point's SSID
PASSWORD = "ece270_wifi_7168"             #Replace with the Access Point's Password
MQTT_BROKER = "10.42.0.1"            #Replace with Pi's IP Address
CLIENT_ID = "PicoW"                  #Name of Device
TOPIC = b"ece270/lab2/test1"         #The topic of the conversation

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    
    print("Connecting to WiFi...")
    time.sleep(1)

print("Successful Connection to IP:", MQTT_BROKER)


# Connect to MQTT
try:
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.connect()
    print("Connected Successfully to MQTT Broker")
    
    client.publish(TOPIC, "Hello from Pico".encode())        #Publish message to Broker
    time.sleep(1)
    
    for i in range(1, 6):
        msg1 = f"This is message {i}"                        #Publish message to Broker
        client.publish(TOPIC, msg1.encode())
        print("Sent:", msg1, "to test1")
        time.sleep(1)
        
    client.publish(TOPIC, "Goodbye".encode())                #Publish message to Broker
    time.sleep(1)
    
except Exception as e:
    print("Error:", e)