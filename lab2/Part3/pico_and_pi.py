import network
import time
from machine import Pin
from simple import MQTTClient

# --- Configuration ---
SSID = "ece270-5"                # Replace with the Access Point's SSID
PASSWORD = "ece270_wifi_7168"              # Replace with the Access Point's Password
MQTT_BROKER = "10.42.0.1"             # Replace with Pi's IP Address
CLIENT_ID = "PicoW_Room1"             # Name of Device
TOPIC_CONTROL = b"room1/control"      # The topic Pico listens to
TOPIC_STATUS = b"room1/status"        # The topic Pico publishes to

# Hardware Setup
room1 = Pin(16, Pin.OUT)                # Initialize room1 on Pin 16

def connect_wifi():
    #Handles the connection to the local Wi-Fi network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Waiting for WiFi...")
        time.sleep(1)
        
    print("Connected to IP:", MQTT_BROKER)
    return wlan

def on_message(topic, msg):
    #Callback function that triggers whenever a message is received from the Pi
    command = msg.decode().lower()
    print(f"Received command: {command}")
    
    if command == "room1 on":
        room1.value(1)
        # Immediate status update for better feedback
        client.publish(TOPIC_STATUS, "Room1 ON (Command Executed)")
    elif command == "room1 off":
        room1.value(0)
        # Immediate status update for better feedback
        client.publish(TOPIC_STATUS, "Room1 OFF (Command Executed)")

def start_mqtt():
    #Initializes the MQTT client, subscribes to topics, and starts the loop
    global client
    status_interval = 5000            # 5 seconds in milliseconds
    last_status_time = 0

    try:
        client = MQTTClient(CLIENT_ID, MQTT_BROKER)
        client.set_callback(on_message) # Attach the listener function
        client.connect()
        client.subscribe(TOPIC_CONTROL) # Listen for commands from the Pi
        print("Subscribed to control topic. Listening...")

        while True:
            # 1. Listen for incoming MQTT commands (Non-blocking)
            client.check_msg()
            
            # 2. Check if 5 seconds have passed to send a status heartbeat
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, last_status_time) >= status_interval:
                status = "ON" if room1.value() else "OFF"
                client.publish(TOPIC_STATUS, f"Node: Room1, Status: {status}")
                last_status_time = current_time
            
            # 3. Small delay to keep the system stable and responsive
            time.sleep(0.1)
            
    except Exception as e:
        print("Error in MQTT loop:", e)

def main():
    connect_wifi()
    start_mqtt()

if __name__ == "__main__":
    main()