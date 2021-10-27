#!/usr/bin/python3

#Import packages
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
import adafruit_icm20x
from termcolor import colored

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
packet_id = 0
execution_time = 0

#with open('/home/pi/Desktop/settings.txt') as w:
#  data = json.load(w)
  
#sps = data['settings'][0]['sample_rate']
sps = 200
print(1/sps)

message = str("Setting initial sample rate of "+str(sps)+" sps...")
print(colored(message,'cyan'))
sample_rate = 1/sps  
station_number = 1

if os.system('systemctl is-active telegraf --quiet') == 0:
    print(colored('telegraf consumer is online...','green'))
else:
    print(colored('[!] telegraf consumer is inactive...','red'))

if os.system('systemctl is-active influxdb --quiet') == 0:
    print(colored('influxdb storage is online...','green'))
else:
    print(colored('[!] influxdb storage is inactive...','red'))
    
#Initialize the I2C bus.
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    print(colored('i2c initialized successfully ...','green'))
except:
    print(colored('[!] i2c failed to initialize...','red'))

#Validate the LSM9DS1 is available on the i2c bus
try:
    #sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
    sensor = adafruit_icm20x.ICM20948(i2c)
    print(sensor.accelerometer_data_rate)
    print(sensor.gyro_data_rate)
    sensor.reset()
    sensor.initialize()
    print(sensor.accelerometer_data_rate)
    print(sensor.gyro_data_rate)
    sensor.accelerometer_data_rate_divisor = 0
    sensor.gyro_data_rate_divisor = 0
    print(sensor.accelerometer_data_rate)
    print(sensor.gyro_data_rate)

    #sensor.accel_range = adafruit_icm20x.ACCELRANGE_2G
    #sensor.accel_range = adafruit_lsm9ds1.ACCELRANGE_4G
    print(colored('lsm9ds1 initialized successfully ...','green'))
except(OSError, ValueError):
    print(colored('[!] Acceleration sensor not detected...','red'))



#Initialize the MQTT client for remote publishing
#This is the client that is responsile for the cloud-based storage of data.
#Data is stored in InfluxDB via a Telegraf/MQTT input plugin (see project documentation)


#This function acquires data from the LSM9DS1 9DOF sensor and publishes the data in an MQTT data stream
#Please note that this function is called by the twisted.internet.task.LoopingCall function and executed by Reactor
def publishMessage():
    global packet_id    #This is essentially a loop counter used to validate that packets weren't dropped and arrived in order
    global execution_time   #required for the first packet to be sent
    global sample_rate
    global sample_time
    t = time.time()
    #if packet_id == 0:
    #    sample_time = time.time_ns()    #gets UNIX time in ns
    #else:
    #    sample_time = sample_time + (sample_rate*1000000000)
    sample_time = time.time_ns() 
    # x, y, z = sensor.acceleration   #gets data from the accelerometer
    x = sensor.acceleration   #gets data from the accelerometer
    # x = 0
    # y = 0
    # z = 0
    
    # data = [
    #     {
    #         "time": sample_time,
    #         "x": x,
    #         "y": y,
    #         "z": z,
    #         "packet_id": packet_id,
    #         "delta_time":execution_time
    #     }
    # ]
    # msg = json.dumps(data)  #MQTT requires data to be formatted into JSON
    # #print(msg)
    # mqtt_int.publish("local/sensor/",msg,qos=0) #publish the data to the local mqtt server
    # mqtt_ext.publish("osnds/livestream/station/1/acceleration/",msg,qos=0)  #publish the data to the remote mqtt server
    # execution_time = time.time_ns()- sample_time    #used for troubleshooting - measures the function's execution time
    
    # if packet_id == sps:
    #     packet_id = 0
    # else:
    #     packet_id = packet_id + 1
    print(time.time()-t)

def on_message(client, userdata, message):
    
    global sample_rate
    global settings_change
    global sample_time
    global station_number
    
    req = str("[!] Settings request recieved:"+str(message.payload)+"...")
    print(colored(req,'magenta'))
    
    settings = json.loads(message.payload)
    station = settings['station']
    
    #mqtt_ext.publish("osnds/configuration/station",payload=None,qos=0)    
    
    if station != station_number:
        
        print(colored('[!] Settings request not applicable to this sensor...','magenta'))

    else:

        sps = settings['sample_rate']

        if sps > 400 or sps < 1 or sps == (1/sample_rate):
            print("Sample rate not supported or the same")
        else:
            sample_rate = round(1/sps,3)
            print(colored('[!][!][!] Restarting sensor with new sample rate... [!][!][!]','red'))
            data = {}
            data['settings'] = []
            data['settings'].append({
                'sample_rate': sps,
            })
    
            file = '/home/pi/Desktop/settings.txt'

            with open(file, 'w') as outfile:
                json.dump(data, outfile)
            
            mqtt_ext.loop_stop()
            print(colored('MQTT daemon stopped...','red'))
            reactor.stop()
            print(colored('Twised Reactor daemon stopped...','red'))
            time.sleep(2)
            os.execv(sys.executable, ['python3'] + sys.argv) #working

try:
    mqtt_int = mqtt.Client(client_id="OSNDS Station 1", userdata=None, transport="tcp")
    #mqtt_int.username_pw_set(username="aftac", password="sensor")
    #mqttc.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
    mqtt_int.connect("127.0.0.1",port=1883,keepalive=45)
    print(colored('Internal MQTT client connected successfully...','green'))
except:
    print(colored('Internal MQTT client failed to connect...','red'))
    
try:
    mqtt_ext = mqtt.Client(client_id="OSNDS Station 1", userdata=None, transport="tcp")
    mqtt_ext.username_pw_set(username="aftac", password="sensor")
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    mqtt_ext.tls_set_context(context)
    #mqtt_ext.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
    mqtt_ext.connect("mqtt.osnds.net",port=8883,keepalive=45)
    mqtt_ext.subscribe("osnds/configuration/station",qos=2)
    print(colored('External MQTT client connected successfully...','green'))
except:
    print(colored('External MQTT client failed to connect...','red'))


mqtt_ext.on_message= on_message
mqtt_ext.loop_start()
task.LoopingCall(publishMessage).start(sample_rate)    #sets the sample rate (200 sps = 1/200 = 0.005 seconds)
print(colored('System is now online and publishing data...','green'))
reactor.run()   #runs the function called in the argument of the LoopingCall
