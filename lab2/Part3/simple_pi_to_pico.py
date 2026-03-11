import network
import time
from simple import MQTTClient

# WiFi & MQTT Config
SSID = "ece270-5"                #Replace with the Access Point's SSID
PASSWORD = "ece270_wifi_7168"              #Replace with the Access Point's Password
MQTT_BROKER = "10.42.0.1"             #Replace with Pi's IP Address
CLIENT_ID = "PicoW"                   #Name of Device
TOPIC = b"ece270/lab2/test2"          #The topic of the conversation

# Callback: This function runs when the Pi sends a message
def sub_cb(topic, msg):
    print("Received: ", msg.decode())

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
    client.set_callback(sub_cb)              #Set the function to handle incoming messages
    client.connect()
    client.subscribe(TOPIC)                  #Subscribe to the topic to listen for Pi
    print("Connected Successfully to MQTT Broker")
    
    print("Waiting for messages from Pi...")
    
    while True:
        client.check_msg()                   #Check for incoming messages from mosquitto_pub
        time.sleep(0.1)                      #every 0.1s
        
except Exception as e:
    print("Error:", e)