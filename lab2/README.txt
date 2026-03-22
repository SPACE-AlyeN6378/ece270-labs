lab1_cps_system.py
This was the main program run on the Pico W.
It includes all the logging logic from lab1, but
instead of printing to console, it publishes the
data to the MQTT broker hosted on the RP5.
The only other changes are slightly more set-up code
to connect the board to the network and the broker,
as well as defining the relevant topics.

logger.py
This was the main program run on the RP5.
No significant changes were made to this code

simple.py
This was provided code to facilitate sending and
recieving messages over MQTT and this file needed
to be copied to the Pico W to run all other code.

pico_and_pi.py, simple_pico_to_pi.py, simple_pi_to_pico.py
These were exercise files not substancially changed
to ensure we understood how to send and recieve messages
over MQTT before part 3D.

sql_files [DIRECTORY]
Short SQL queries which were our first attempts at
analyzing trends. Refer to the code in the lab report
for final versions.
