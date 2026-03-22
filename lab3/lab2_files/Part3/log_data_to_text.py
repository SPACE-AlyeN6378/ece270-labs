import paho.mqtt.client as mqtt
#to be used for lab 2 part 3e

# Configuration
LOG_FILE = "logged_node_status.txt"        # Name of output file
TOPIC = "logging"               # Topic to match the Pico

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected successfully to broker.")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        
        #  1. Write the data to the file object (userdata)
        userdata.write(payload + "\n")
        
        # 2. force the write to the file right away
        userdata.flush() 
        
        print(f"Logged: {payload}")
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    # Open the file in append mode ('a')
    # buffering=1 tells Python to line-buffer, but we still use flush () for  safety
    f = open(LOG_FILE, "a")

    # Pass the file object 'f' as userdata so its accessible in on_message
    client = mqtt.Client(userdata=f)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect("localhost", 1883, 60)
        print(f"Pi Logger is running... Saving to {LOG_FILE}")
        print("Press Ctrl + C to stop.")
        
        # start the loop to listen for   messages
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 3. Ensure the file is closed properly even if the script crashes
        f.close()
        print("File closed. Exit successful.")

if __name__ == "__main__":
    main()