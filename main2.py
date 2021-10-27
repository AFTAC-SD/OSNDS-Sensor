import board
import busio
import argparse
import adafruit_icm20x
import paho.mqtt.client as mqtt
from twisted.internet import task
from twisted.internet import reactor
import qwiic_titan_gps
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode
import adafruit_bme680
import time
import ssl
import json

class stationConfiguration():
    stationNumber = 1
    stationLocalIP = ''
    stationGlobalIP = ''

class devices():
    accel = None

class brokers():
    mqtt_ext = None


def start_services():
    brokers.mqtt_ext = mqtt.Client(client_id=f'OSNDS Station {stationConfiguration.stationNumber}', userdata=None, transport="tcp")
    brokers.mqtt_ext.username_pw_set(username="aftac", password="sensor")
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    brokers.mqtt_ext.tls_set_context(context)
    #mqtt_ext.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
    brokers.mqtt_ext.connect("mqtt.osnds.net",port=8883,keepalive=45)
    brokers.mqtt_ext.subscribe("osnds/configuration/station",qos=2)

def check_services():
    pass

def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', type=bool, default=False, help='enable verbose debugging with slow processing')
    opt = parser.parse_args()
    # debug=opt.debug
    # station_name = system_vars.station_name

def get_IP():
    try:
        stationConfiguration.stationGlobalIP=subprocess.check_output("curl ifconfig.me",shell=True)
        stationConfiguration.stationGlobalIP=stationConfiguration.stationGlobalIP.decode("utf-8")
    except:
        stationConfiguration.stationGlobalIP='unable to resolve global IP'
    try:
        stationConfiguration.stationLocalIP = subprocess.check_output("hostname -I",shell=True)
        stationConfiguration.stationLocalIP = stationConfiguration.stationLocalIP.decode("utf-8")
        stationConfiguration.stationLocalIP = stationConfiguration.stationLocalIP[:-2]
    except:
        stationConfiguration.stationLocalIP = 'unable to resolve local IP'

def start_GPIO():
    pass

def publish_data():
    sample_time = time.time_ns() 
    x, y, z = devices.accel.acceleration   #gets data from the accelerometer    # print(lat, lon, time_gps)
    data = [
            {
                "name" : 'osnds_station_1',
                # "packet_id": packet_id,
                "time":sample_time,
                "x": x,
                "y": y,
                "z": z,
                # "delta_time": execution_time,
            }
        ]
    data = json.dumps(data)
    brokers.mqtt_ext.publish("osnds/livestream/station/" + str(stationConfiguration.stationNumber) +"/acceleration/",data,qos=0)  #publish the data to the remote mqtt server
    
    if packet_id == sps:
        packet_id = 0
        # publishHealth()   
    else:
        packet_id = packet_id + 1

def start_devices():
    i2c = busio.I2C(board.SCL, board.SDA)
    devices.accel = adafruit_icm20x.ICM20948(i2c)

start_devices()
start_services()
get_IP()

task.LoopingCall(publish_data).start(.005)
reactor.run()
