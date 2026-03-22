from machine import Pin, PWM
import time
import dht
import network
import time
import json
from simple import MQTTClient

# WiFi & MQTT Config
SSID = "ece270-5"               #Replace with the Access Point's SSID
PASSWORD = "ece270_wifi_7168"             #Replace with the Access Point's Password
MQTT_BROKER = "10.42.0.1"            #Replace with Pi's IP Address
CLIENT_ID = "PicoW"                  #Name of Device
TOPIC_LIGHTS = b"lights"         #The topic of the conversation
TOPIC_TEMP = b"temperature"         #The topic of the conversation
TOPIC_ALARM = b"alarm"         #The topic of the conversation
TOPIC = "logging"
TOPIC_CONTROL = b"control"

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    
    print("Connecting to WiFi...")
    time.sleep(1)

print("Successful Connection to IP:", MQTT_BROKER)

client = MQTTClient(CLIENT_ID, MQTT_BROKER)
client.connect()
print("Connected Successfully to MQTT Broker")

DEBOUNCE_TIME = 250		# 250 ms

# LED Pins
blue = Pin(16, Pin.OUT)			# Room 1
green = Pin(17, Pin.OUT)		# Room 2
white = Pin(13, Pin.OUT)		# Room 3
red = Pin(22, Pin.OUT)			# Alarm

DEVICES = {
    "room1": 0,
    "room2": 0,
    "living_room": 0,
    "alarm": 0
}

# Buttons
button1 = Pin(28, Pin.IN, Pin.PULL_UP)		# Room 1
last_press1 = 0

button2 = Pin(27, Pin.IN, Pin.PULL_UP)		# Room 2
last_press2 = 0

button3 = Pin(26, Pin.IN, Pin.PULL_UP)		# Alarm
last_press3 = 0

# Buzzer
buzzer = PWM(Pin(20))
duty = 0
buzzer.duty_u16(duty)
buzzer.freq(1760)

# Temperature Sensor
sensor = dht.DHT11(Pin(15, Pin.IN, Pin.PULL_UP))
temperature = 0

# IR sensor
led_count = 0
ir_sensor = Pin(14, Pin.IN)

# Motion sensor
pir = Pin(18, Pin.IN)

print("Warming up PIR sensor...")
time.sleep(5)			# allow PIR to stabilize
print("PIR ready")


# Interrupt service routine
def button1_handler(pin):
    global last_press1, DEVICES
    now = time.ticks_ms()
    
    if time.ticks_diff(now, last_press1) > DEBOUNCE_TIME:
        DEVICES["room1"] = (DEVICES["room1"] + 1) % 2
        last_press1 = now
        
def button2_handler(pin):
    global last_press2, DEVICES
    now = time.ticks_ms()
    
    if time.ticks_diff(now, last_press2) > DEBOUNCE_TIME:
        DEVICES["room2"] = (DEVICES["room2"] + 1) % 2
        last_press2 = now
    
def button3_handler(pin):
    global last_press3, DEVICES
    now = time.ticks_ms()
    
    if time.ticks_diff(now, last_press3) > DEBOUNCE_TIME:
        DEVICES["alarm"] = 0		# <-- Actual task
        last_press3 = now


button1.irq(
    trigger = Pin.IRQ_FALLING,		# triggered when signal goes HI to LO
    handler = button1_handler
)

button2.irq(
    trigger = Pin.IRQ_FALLING,		# triggered when signal goes HI to LO
    handler = button2_handler
)

button3.irq(
    trigger = Pin.IRQ_FALLING,		# triggered when signal goes HI to LO
    handler = button3_handler
)

time_tick = 0
time_second = -1


def system_control(topic, msg):
    global DEVICES
    payload = msg.decode()
    if payload:
        device, action = payload.split(':')
        action = 1 if action == "on" else 0
        DEVICES[device] = action
            

def log():
    global time_second, temperature, DEVICES
    global TOPIC, TOPIC_LIGHTS, TOPIC_TEMP, TOPIC_ALARM
    
    payload = {
        "time": time_second,
        "node": None,
        "device": None,
        "status": None
    }
    
    room1_state = "on" if (DEVICES["room1"] == 1) else "off"
    payload["node"] = "room1"
    payload["device"] = "lights"
    payload["status"] = room1_state
    client.publish(TOPIC_LIGHTS, json.dumps(payload).encode())
    client.publish(TOPIC, json.dumps(payload).encode())
    
    room2_state = "on" if (DEVICES["room2"] == 1) else "off"
    payload["node"] = "room2"
    payload["device"] = "lights"
    payload["status"] = room2_state
    client.publish(TOPIC_LIGHTS, json.dumps(payload).encode())
    client.publish(TOPIC, json.dumps(payload).encode())
    
    room3_state = "on" if (DEVICES["living_room"] == 1) else "off"
    payload["node"] = "living_room"
    payload["device"] = "lights"
    payload["status"] = room3_state
    client.publish(TOPIC_LIGHTS, json.dumps(payload).encode())
    client.publish(TOPIC, json.dumps(payload).encode())
    
    room4_state = "on" if (DEVICES["alarm"] == 1) else "off"
    payload["node"] = "garage"
    payload["device"] = "lights"
    payload["status"] = room4_state
    client.publish(TOPIC_LIGHTS, json.dumps(payload).encode())
    client.publish(TOPIC, json.dumps(payload).encode())
    
    payload["node"] = "thermostat"
    payload["device"] = "temperature"
    payload["status"] = temperature
    client.publish(TOPIC_TEMP, json.dumps(payload).encode())
    client.publish(TOPIC, json.dumps(payload).encode())
    
    alarm_state = "on" if DEVICES["alarm"] else "off"
    payload["node"] = "garage"
    payload["device"] = "alarm"
    payload["status"] = alarm_state
    client.publish(TOPIC_ALARM, json.dumps(payload).encode())
    client.publish(TOPIC, json.dumps(payload).encode())
    
def main():
    global duty, buzzer, time_tick, time_second, sensor, temperature, led_count
    global red, blue, green, white, client, DEVICES, TOPIC_CONTROL
    client.set_callback(system_control)
    client.subscribe(TOPIC_CONTROL)
    while True:
        client.check_msg()
        # Buzzer
        # every tick
        if DEVICES["alarm"] == 1:
            if duty == 0:
                duty = 30000
            else:
                duty = 0
            buzzer.duty_u16(duty)
        else:

            buzzer.duty_u16(0)
        
        # update LEDs
        # every 2 ticks
        if time_tick % 2 == 0:
            blue.value(DEVICES["room1"])
            green.value(DEVICES["room2"])
            white.value(DEVICES["living_room"])
            red.value(DEVICES["alarm"])
        
        # DHT11 Temperature sensor
        # every 10 ticks
        if time_tick % 10:
            try:
                sensor.measure()
                temperature = sensor.temperature()
            
            except OSError as e:
                print("Read failed:", e)

        # IR Sensor
        # every 5 ticks
        if time_tick % 5 == 0:
            if ir_sensor.value() == 0:
                led_count = 10
                DEVICES["living_room"] = 1
            else:
                if led_count != 0:
                    led_count -= 1
                    
                if led_count == 0:
                    DEVICES["living_room"] = 0  
        # Motion Sensor
            if pir.value() == 1:
                DEVICES["alarm"] = 1

        # update logging
        # every 5 ticks
        if time_tick % 5 == 0:
            time_second += 1
            if time_second != 0:
                log()
            
        time_tick += 1
        time.sleep(0.20)
        
if __name__ == "__main__":
    main()
