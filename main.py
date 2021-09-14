#!/usr/bin/python3

#Import packages
import pdb
import socks
import sockets
import time
import os
import sys
import board
import busio
import json
import ssl
import paho.mqtt.client as mqtt
from twisted.internet import task
from twisted.internet import reactor
# import adafruit_lsm9ds1
from random import random
os.system('clear')

print(r"""
   ____  _____ _   ______  _____    _____ _______   _______ ____  ____
  / __ \/ ___// | / / __ \/ ___/   / ___// ____/ | / / ___// __ \/ __ \
 / / / /\__ \/  |/ / / / /\__ \    \__ \/ __/ /  |/ /\__ \/ / / / /_/ /
/ /_/ /___/ / /|  / /_/ /___/ /   ___/ / /___/ /|  /___/ / /_/ / _, _/
\____//____/_/ |_/_____//____/   /____/_____/_/ |_//____/\____/_/ |_|

""")

#Initialize global variables
global packet_id
global execution_time

#Pass initial states to global variables
packet_id = 1
execution_time = 0

# with open('/home/pi/Desktop/settings.txt') as w:
#   data = json.load(w)

# sps = data['settings'][0]['sample_rate']
sps = 200
print("Setting initial sample rate of",sps,"sps")
sample_rate = 1/sps
station_number = 5


if os.system('systemctl is-active telegraf --quiet') == 0:
    print("telegraf consumer is online...")
else:
    print("[!] telegraf consumer is inactive...")

if os.system('systemctl is-active influxdb --quiet') == 0:
    print("influxdb storage is online...")
else:
    print("[!] influxdb storage is inactive...")

#Initialize the I2C bus.
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    print("i2c initialized successfully ...")
except:
    print("[!] i2c failed to initialize...")

# #Validate the LSM9DS1 is available on the i2c bus
# try:
#     sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
#     sensor.accel_range = adafruit_lsm9ds1.ACCELRANGE_4G
#     sensor.mag
#     #sensor.accel_range = adafruit_lsm9ds1.ACCELRANGE_4G
# except(OSError, ValueError):
#     print("[!] Acceleration sensor not detected...")



#Initialize the MQTT client for remote publishing
#This is the client that is responsile for the cloud-based storage of data.
#Data is stored in InfluxDB via a Telegraf/MQTT input plugin (see project documentation)


#This function acquires data from the LSM9DS1 9DOF sensor and publishes the data in an MQTT data stream
#Please note that this function is called by the twisted.internet.task.LoopingCall function and executed by Reactor
def publishMessage():
    global packet_id    #This is essentially a loop counter used to validate that packets weren't dropped and arrived in order
    global execution_time   #required for the first packet to be sent
    sample_time = time.time_ns()    #gets UNIX time in ns
    # x, y, z = sensor.acceleration   #gets data from the accelerometer
    x = random()
    y = random()
    z = random()

    data = [
        {
            "time": sample_time,
            "x": x,
            "y": y,
            "z": z,
            "packet_id": packet_id,
            "delta_time":execution_time,
            "name":"osnds_station_5"
        }
    ]
    msg = json.dumps(data)  #MQTT requires data to be formatted into JSON
    #print(msg)
    mqtt_int.publish("local/sensor/",msg,qos=0) #publish the data to the local mqtt server
    mqtt_ext.publish("osnds/livestream/station/5/acceleration/",msg,qos=1)  #publish the data to the remote mqtt server
    packet_id = packet_id + 1
    execution_time = time.time_ns()- sample_time    #used for troubleshooting - measures the function's execution time

def on_message(client, userdata, message):

    global sample_rate
    global settings_change

    print("%s %s" % (message.topic, message.payload))

    settings = json.loads(message.payload)
    station = settings['station']

    #mqtt_ext.publish("osnds/configuration/station",payload=None,qos=0)

    if station != 2:

        print("settings change not applicable")

    else:

        sps = settings['sample_rate']

        if sps > 200 or sps < 1 or sps == (1/sample_rate):
            print("Sample rate not supported or the same")
        else:
            sample_rate = round(1/sps,3)
            print("Restarting sensor with new sample rate:",sps,"sps")
            data = {}
            data['settings'] = []
            data['settings'].append({
                'sample_rate': sps,
            })

            file = 'settings.txt'

            with open(file, 'w') as outfile:
                json.dump(data, outfile)

            mqtt_ext.loop_stop()
            reactor.stop()
            os.execv(sys.executable, ['python3'] + sys.argv) #working

try:
    mqtt_int = mqtt.Client(client_id="OSNDS Station 5", userdata=None, transport="tcp")
    #mqtt_int.username_pw_set(username="aftac", password="sensor")
    #mqttc.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
    mqtt_int.connect("127.0.0.1",port=1883,keepalive=45)
    print("Internal MQTT client connected successfully...")
except:
    print("Internal MQTT client failed to connect...")

try:
    pdb.set_trace()
    mqtt_ext = mqtt.Client(client_id="OSNDS Station 5", userdata=None, transport="tcp")
    mqtt_ext.username_pw_set(username="aftac", password="sensor")
    mqtt_ext.proxy_set(proxy_type=socks.HTTP, proxy_addr='https://10.150.206.21', proxy_port=8080)
    # socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_HTTP, addr="10.150.206.21", port=8080, rdns=True)
    # socket.socket = socks.socksocket
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    mqtt_ext.tls_set_context(context)
    #mqtt_ext.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
    mqtt_ext.connect("mqtt.osnds.net",port=8883,keepalive=45)
    mqtt_ext.subscribe("osnds/configuration/station",qos=2)
    print("External MQTT client connected successfully...")
except:
    print("External MQTT client failed to connect...")


mqtt_ext.on_message= on_message
mqtt_ext.loop_start()
task.LoopingCall(publishMessage).start(sample_rate)    #sets the sample rate (200 sps = 1/200 = 0.005 seconds)
print("System is now online and publishing data...")
reactor.run()   #runs the function called in the argument of the LoopingCall