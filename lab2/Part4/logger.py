#logger.py
import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime
import re

DB_FILE = "home_system.db"

def init_db():
    #Initialize the database and create the table if it doesn't exist
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  real_time TEXT,
                  counter INTEGER,
                  node_id TEXT,
                  sensor_type TEXT,
                  value INTEGER)''')
    conn.commit()
    conn.close()

# 1. Open a persistent connection before starting the MQTT loop
db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
db_cursor = db_conn.cursor()

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    # Extract: {counter, node, object, status}
    data = re.findall(r"\{(.*)\}", payload)
    
    if data:
        parts = [p.strip() for p in data[0].split(',')]
        if len(parts) == 4:
            count, node, sensor, status = parts
            
            if status.lower() == "on":
                val = 1
            elif status.lower() == "off":
                val = 0
            else:
                try:
                    val = int(status) 
                except ValueError:
                    val = -1 

            # 2. Use the persistent cursor to insert data
            try:
                db_cursor.execute(
                    "INSERT INTO logs (real_time, counter, node_id, sensor_type, value) VALUES (?, ?, ?, ?, ?)",
                    (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, node, sensor, val)
                )
                db_conn.commit() 
                print(f"Stored: {node} {sensor} = {val}")
            except sqlite3.Error as e:
                print(f"Database error: {e}")

# Initialize Database
init_db()

# Setup MQTT Client
client = mqtt.Client()
client.on_message = on_message

try:
    print("Connecting to broker...")
    client.connect("localhost", 1883)
    client.subscribe("logging")
    
    print("Listener started. Press Ctrl+C to stop.")
    client.loop_forever()

except KeyboardInterrupt:
    print("\nStopping script...")

finally:
    db_conn.close()
    print("Database connection closed safely.")