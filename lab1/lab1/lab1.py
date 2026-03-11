from machine import Pin, PWM
import time
import dht
import network
import time


DEBOUNCE_TIME = 250		# 250 ms

# Alarm state (OFF initially)
alarm_on = False

# LED Pins
blue = Pin(16, Pin.OUT)			# Room 1
blue_value = 0
green = Pin(17, Pin.OUT)		# Room 2
green_value = 0
white = Pin(13, Pin.OUT)		# Room 3
white_value = 0
red = Pin(22, Pin.OUT)			# Alarm
red_value = 0

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
    global last_press1, blue_value
    now = time.ticks_ms()
    
    if time.ticks_diff(now, last_press1) > DEBOUNCE_TIME:
        blue_value = (blue_value + 1) % 2
        last_press1 = now
        
def button2_handler(pin):
    global last_press2, green_value
    now = time.ticks_ms()
    
    if time.ticks_diff(now, last_press2) > DEBOUNCE_TIME:
        green_value = (green_value + 1) % 2
        last_press2 = now
    
def button3_handler(pin):
    global last_press3, alarm_on
    now = time.ticks_ms()
    
    if time.ticks_diff(now, last_press3) > DEBOUNCE_TIME:
        alarm_on = False		# <-- Actual task
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

def log():
    global time_second, temperature, alarm_on
    global blue_value, green_value, white_value, red_value
    
    room1_state = "on" if (blue_value == 1) else "off"
    print(f"{{{time_second}, room1, lights, {room1_state}}}")
    
    room2_state = "on" if (green_value == 1) else "off"
    print(f"{{{time_second}, room2, lights, {room2_state}}}")
    
    room3_state = "on" if (white_value == 1) else "off"
    print(f"{{{time_second}, livingroom, lights, {room3_state}}}")
    
    room4_state = "on" if (red_value == 1) else "off"
    print(f"{{{time_second}, garage, lights, {room4_state}}}")
    
    print(f"{{{time_second}, thermostat, temperature, {temperature}}}")
    
    alarm_state = "on" if alarm_on else "off"
    print(f"{{{time_second}, garage, alarm, {alarm_state}}}")

while True:
    # Buzzer
    # every tick
    if alarm_on:
        if duty == 0:
            duty = 30000
            red_value = 1
        else:
            duty = 0
            red_value = 0
        buzzer.duty_u16(duty)
    else:

        buzzer.duty_u16(0)
        red_value = 0
    
    # update LEDs
    # every 2 ticks
    if time_tick % 2 == 0:
        blue.value(blue_value)
        green.value(green_value)
        white.value(white_value)
        red.value(red_value)
    
    # DHT11 Temperature sensor
    # every 10 ticks
    if time_tick % 10:
        try:
            sensor.measure()
            temperature = sensor.temperature()
            humidity = sensor.humidity()
        
        except OSError as e:
            print("Read failed:", e)

    # IR Sensor
    # every 5 ticks
    if time_tick % 5 == 0:
        if ir_sensor.value() == 0:
            led_count = 10
            white_value = 1
        else:
            if led_count != 0:
                led_count -= 1
                
            if led_count == 0:
                white_value = 0  
    # Motion Sensor
        if pir.value() == 1:
            alarm_on = True

    # update logging
    # every 5 ticks
    if time_tick % 5 == 0:
        time_second += 1
        if time_second != 0:
            log()
        
    time_tick += 1
    time.sleep(0.20)