#!/usr/bin/python3
#version 202109200854
#Import packages
import pdb
#import socks
#import sockets
import time
import os
import sys
#import board
#import busio
import json
import ssl
import paho.mqtt.client as mqtt
from twisted.internet import task
from twisted.internet import reactor
# import adafruit_lsm9ds1
import random
import numpy as np
os.system('clear')
import pylops
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
sps = 1
print("Setting initial sample rate of",sps,"sps")
sample_rate = 1/sps
# station_number = 1


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
class globalXYZ():
    x=0
    y=0
    z=0
    jump = 0
    boomX = []
    boomY = []
    boomZ = []
#Initialize the MQTT client for remote publishing
#This is the client that is responsile for the cloud-based storage of data.
#Data is stored in InfluxDB via a Telegraf/MQTT input plugin (see project documentation)


#This function acquires data from the LSM9DS1 9DOF sensor and publishes the data in an MQTT data stream
#Please note that this function is called by the twisted.internet.task.LoopingCall function and executed by Reactor
def addboom():
    #bigboom = [1,2,1,2,1]
    par = {
            "ox" : -200*random.random(),
            "dx" : 5*random.random(),
            "nx" : 201*random.random(),
            "oy" : -100*random.random(),
            "dy" : 5*random.random(),
            "ny" : 101*random.random(),
            "ot" : 0.10,
            "dt" : 0.04*random.random(),
            "nt" : 5010*random.random(),
            "f0" : 10*random.random(),
            "nfmax" : 210*random.random()
            }
    t, t2, x ,y = pylops.utils.seismicevents.makeaxis(par)
    wav = pylops.utils.wavelets.ricker(np.arange(41)*par["dt"], f0=par["f0"])[0]
    v = 15000
    t0 = [0.2, 1.7, 6.6]
    theta = [40, 0 , -60]
    amp = [1.0, 0.6, -2.0]
    mlin, mlinwav = pylops.utils.seismicevents.linear2d(x, t, v, t0, theta, amp, wav)
    #print(len(mlin))
    #print(len(mlinwav))
    #print(mlin)
    #print(type(mlinwav[0].tolist()))
    wave = mlinwav[0].tolist()
    #wave = list(np.asarray(list(np.asarray(wave)+100)*2)-100)
    wave = wave * np.random.rand(len(wave))*2
    wave = wave.tolist()
    print(len(wave))
    return wave

def addboom2():
    length = random.randint(0,1000)
    time = np.arange(0, length, 0.1)
    amp = [0]*length*10
    for x in range(0, random.randint(1,10)):
        amp = np.add(amp,np.sin(time)*random.random(),np.sinc(time)*random.random())
    print(type(amp))
    return amp.tolist()


def publishMessage():
    global packet_id    #This is essentially a loop counter used to validate that packets weren't dropped and arrived in order
    global execution_time   #required for the first packet to be sent
    sample_time = time.time_ns()    #gets UNIX time in ns
    # x,__ y, z = sensor.acceleration   #gets data from the accelerometer
#    spike_chance=random.random()
#    if spike_chance > 0.9995:
#     x = np.random.normal(0,1,100)*10
#     y = 5-np.random.normal(0,1,100)
#     z = 5+np.random.normal(0,1,100)  
#    else:
    x = globalXYZ.x + random.gauss(0, 1)/1000
    y = globalXYZ.y + random.gauss(0, 1)/1000
    z = globalXYZ.z + random.gauss(0, 1)/1000
    globalXYZ.x = x
    globalXYZ.y = y
    globalXYZ.z = z
    #jump = globalXYZ.jump
    boomX = globalXYZ.boomX
    boomY = globalXYZ.boomY
    boomZ = globalXYZ.boomZ
    #print(random.random())
    if random.random() >= 0.99975:
        #jump = jump + 3*random.random()
        boomX = boomX + addboom()
        boomY = boomY + addboom()
        boomZ = boomZ + addboom()
        #print(f'adding to boom:{boom}')
    if len(boomX)>0:
        tempAddX = boomX[0]
        #print(f'before length {len(boom)}')
        boomX.pop(0)
        #print(f'after length {len(boom)}')
        #print(tempAdd)
    else:
        tempAddX = 0

    if len(boomY)>0:
        tempAddY = boomY[0]
        boomY.pop(0)
    else:
        tempAddY = 0

    if len(boomZ)>0:
        tempAddZ = boomZ[0]
        boomZ.pop(0)
    else:
        tempAddZ = 0


    #globalXYZ.jump = jump
    globalXYZ.boomX = boomX
    globalXYZ.boomY = boomY
    globalXYZ.boomZ = boomZ
    data = [
        {
            "time": sample_time,
            "x": x + random.random()/20 + tempAddX * .2,
            "y": y + random.random()/20 + tempAddX *.5,
            "z": z + random.random()/20 - tempAddX,
            #            "crit": spike_chance,
            "packet_id": packet_id,
            "delta_time":execution_time,
            "name":"osnds_station_1"
        }
    ]
    msg = json.dumps(data)  #MQTT requires data to be formatted into JSON
    #print(msg)
    mqtt_int.publish("osnds", msg, qos=0) #publish the data to the local mqtt server
    # mqtt_ext.publish("osnds/livestream/station/1/acceleration/",msg,qos=1)  #publish the data to the remote mqtt server
    packet_id = packet_id + 1
    if packet_id >= sps:
     packet_id = 0

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
    broker_address="198.47.75.50" 
    #broker_address="iot.eclipse.org" #use external broker
    # client = mqtt.Client("P1") #create new instance
    mqtt_int = mqtt.Client(client_id=".GOV", userdata=None, transport="tcp")
    mqtt_int.connect(broker_address, 1883, 60) #connect to broker

    #mqtt_int.username_pw_set(username="aftac", password="sensor")
    #mqttc.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
    # mqtt_int.connect("127.0.0.1",port=1883,keepalive=45)
    print(".GOV MQTT client connected successfully...")
except:
    print(".GOV MQTT client failed to connect...")

# try:
#  #   pdb.set_trace()
#     mqtt_ext = mqtt.Client(client_id="OSNDS Station 1", userdata=None, transport="tcp")
#     mqtt_ext.username_pw_set(username="aftac", password="sensor")
# #    mqtt_ext.proxy_set(proxy_type=socks.HTTP, proxy_addr='https://10.150.206.21', proxy_port=8080)
#     # socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_HTTP, addr="10.150.206.21", port=8080, rdns=True)
#     # socket.socket = socks.socksocket
#     context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#     mqtt_ext.tls_set_context(context)
#     #mqtt_ext.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
#     mqtt_ext.connect("mqtt.osnds.net",port=8883,keepalive=45)
#     mqtt_ext.subscribe("osnds/configuration/station",qos=2)
#     print("External MQTT client connected successfully...")
# except:
#     print("External MQTT client failed to connect...")


mqtt_int.on_message= on_message
mqtt_int.loop_start()
task.LoopingCall(publishMessage).start(sample_rate)    #sets the sample rate (200 sps = 1/200 = 0.005 seconds)
print("System is now online and publishing data...")
reactor.run()   #runs the function called in the argument of the LoopingCall
