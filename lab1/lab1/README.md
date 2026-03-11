# ECE 270 - Lab 1  
## Edge Node Bring-Up, Local Sensing and Actuation

## Overview
This project implements an embedded smart-home edge node using a Raspberry Pi Pico W running MicroPython. The system integrates multiple sensors and actuators to demonstrate local sensing, interrupt-driven control, actuation logic, and periodic system logging.

The edge node monitors environmental conditions and user input while controlling LEDs, an alarm buzzer, and logging device states for later analysis.

---

## Features

### Local Actuation
- Three rooms simulated using LEDs:
  - Room 1 (Blue LED)
  - Room 2 (Green LED)
  - Living Room (White LED)
- Garage alarm indicator (Red LED)
- PWM buzzer used as an audible alarm.

### User Interaction
Push buttons are used to toggle system behaviour:
- Button 1 → Toggle Room 1 lights.
- Button 2 → Toggle Room 2 lights.
- Button 3 → Reset/disable alarm.

All buttons use interrupt service routines (ISR) with software debouncing.

---

## Sensors

### DHT11 Temperature Sensor
- Periodically measures ambient temperature and humidity.
- Temperature readings are logged for monitoring purposes.

### PIR Motion Sensor
- Detects motion events.
- Automatically activates the alarm system when motion is detected.
- Includes warm-up stabilization delay at startup.

### IR Sensor
- Detects nearby objects or obstruction.
- Turns on living room lights temporarily when triggered.

---

## Alarm System
When motion is detected:

- Alarm buzzer toggles on/off periodically.
- Garage red LED flashes.
- Alarm remains active until manually reset using Button 3.

---

## Timing Behaviour

The system runs inside a main loop using timed ticks:

- Loop delay: 200 ms per tick.

Task scheduling:

| Task | Frequency |
|---|---|
LED Updates | Every 2 ticks |
IR + Motion Sensors | Every 5 ticks |
Logging | Every 5 ticks |
Temperature Measurement | Every 10 ticks |

---

## Logging Format

System status is printed to the serial console as structured log entries:
```
{timestamp, location, device, status}
```

### Example:
```
{144, room1, lights, on}
{144, thermostat, temperature, 20}
{144, garage, alarm, on}
```


Fields:

- **Timestamp**: Relative seconds since execution start.
- **Location**: Room or subsystem identifier.
- **Device**: Sensor or actuator name.
- **Status**: Operational state or measured value.

Logs provide visibility into system behaviour and are intended for later analysis and database integration in subsequent labs.

---

## Hardware Components

- Raspberry Pi Pico W
- DHT11 Temperature Sensor
- PIR Motion Sensor
- IR Proximity Sensor
- Push Buttons (x3)
- LEDs (Blue, Green, White, Red)
- PWM Buzzer
- Breadboard and GPIO wiring.

---

## Software Requirements

- MicroPython firmware.
- Thonny IDE or serial console access.

Required modules:
```python
import machine
import time
import dht
```


---

## Operation

1. Power the Pico W.
2. PIR sensor warms up for approximately 5 seconds.
3. System enters continuous monitoring loop.
4. Sensors and buttons generate events.
5. LED states, alarm status, and temperature readings are logged periodically.

---

## Known Limitations

- PIR motion sensor sensitivity may vary during early stabilization.
- DHT11 measurements may occasionally fail and are retried automatically.
- Timing is software-based and dependent on loop execution.

---

## Purpose

This lab demonstrates:

- GPIO configuration.
- Interrupt-based input handling.
- PWM actuation.
- Sensor integration.
- Embedded scheduling techniques.
- Structured device logging.
