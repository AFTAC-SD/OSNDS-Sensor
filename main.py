#!/usr/bin/python3

#Import packages
import time
from time import mktime
import os
import sys
import board
import busio
import adafruit_icm20x
import json
import ssl
import paho.mqtt.client as mqtt
from twisted.internet import task
from twisted.internet import reactor
from termcolor import colored
import numpy as np
import json
import subprocess
import qwiic_titan_gps
from datetime import datetime
import functions as fp
import pygeohash as pgh
import psutil
from datetime import datetime
import argparse
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode
# import adafruit_ds3231
# import rtc
import adafruit_bme680

from pympler import summary
# tracker = SummaryTracker()
from pympler import muppy


#system variables class
class system_vars():
    time = time.time()
    station_name = "osnds_station_1"

class hardware_stats():
    cpu_time=0
    mem_percent=0
    disk_usage=0
    packet_drops=0
    cpu_load=0

class device_list():
    sensor = None
    qwiicGPS= None
    ads= None
    bme680= None
    temperature_offset= None

class location_info():
    lat = 0
    lon = 0
    geohash = ''

# Agrument parsing section
parser = argparse.ArgumentParser()
parser.add_argument('--debug', type=bool, default=False, help='enable verbose debugging with slow processing')
opt = parser.parse_args()
debug=opt.debug
station_name = system_vars.station_name

# if debug: print(r"""
# ____  _____ _   ______  _____    _____ _______   _______ ____  ____ 
# / __ \/ ___// | / / __ \/ ___/   / ___// ____/ | / / ___// __ \/ __ \
# / / / /\__ \/  |/ / / / /\__ \    \__ \/ __/ /  |/ /\__ \/ / / / /_/ /
# / /_/ /___/ / /|  / /_/ /___/ /   ___/ / /___/ /|  /___/ / /_/ / _, _/ 
# \____//____/_/ |_/_____//____/   /____/_____/_/ |_//____/\____/_/ |_|  
                                                                    
# """)

#Initialize global variables
global packet_id
global execution_time




#Pass initial states to global variables
packet_id = 0
execution_time = 0
sample_rate = 0
station_number = 0
lat=0
lon=0
time_gps=0



def get_hardware_status():
    try:
        # if debug: print(colored('getting hardware status','yellow'))
        # if debug: time.sleep(1)

        hardware_stats.cpu_time = (psutil.cpu_times().user)
        # cpu_time = 0
        # if debug: print(colored('cpu time is','yellow'))
        # if debug: print(colored(str(cpu_time)),'yellow')
        # if debug: time.sleep(1)

        # print(dict(psutil.virtual_memory()._asdict()))
        hardware_stats.mem_percent = (psutil.virtual_memory().percent)
        # mem_percent = 0
        # if debug: print(colored('mem percent is','yellow'))
        # if debug: print(colored(str(mem_percent),'yellow')) 
        # if debug: time.sleep(1)
        # print(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)

        # print(dict(psutil.disk_usage('/')._asdict()))
        hardware_stats.disk_usage= (psutil.disk_usage('/').percent)
        # disk_usage = 0
        # if debug: print(colored('disk usage is','yellow'))
        # if debug: print(colored(str(disk_usage),'yellow'))
        # if debug: time.sleep(1)


        hardware_stats.packet_drops = (psutil.net_io_counters().dropin)
        # packet_drops = 0
        # if debug: print(colored('packet drops are','yellow'))
        # if debug: print(colored(str(packet_drops),'yellow'))
        # if debug: time.sleep(1)
        # print(psutil.net_io_counters().dropout)
        # print(psutil.net_io_counters().errin)
        # print(psutil.net_io_counters().errout)

        hardware_stats.cpu_load = psutil.cpu_percent(interval=0.0001)
        # cpu_load = 0
        # if debug: print(colored('cpu load is','yellow'))
        # if debug: print(colored(str(cpu_load),'yellow'))
        # if debug: time.sleep(1)
    except:
        if debug: print(colored('health stat error','red'))


def get_IP_info():
    global globalIP, localIP
    # Find IP of the reporting station
    try:
        globalIP=subprocess.check_output("curl ifconfig.me",shell=True)
        globalIP=globalIP.decode("utf-8")
    except:
        globalIP='unable to resolve global IP'

    # Find Local IP of the reporting station
    try:
        localIP = subprocess.check_output("hostname -I",shell=True)
        localIP = localIP.decode("utf-8")
        localIP = localIP[:-2]
    except:
        localIP = 'unable to resolve local IP'

# os.system('clear')
def setup_gpio():
    # for utilizing LED's to display the inner-workings at-a-glance
    # power pin needs no setup, just connect it across 5v and gnd

    # cat /sys/kernel/debug/gpio
    os.system('echo 216 > /sys/class/gpio/unexport')
    os.system('echo 149 > /sys/class/gpio/unexport')
    # online
    os.system('echo 216 > /sys/class/gpio/export') #stealing LCD BL PWM pin 32
    # time.sleep(1)
    os.system('echo out > /sys/class/gpio/gpio216/direction') #set as output for LED
    # streaming data out
    os.system('echo 149 > /sys/class/gpio/export') #stealing CAM pin 29
    # time.sleep(1)
    os.system('echo out > /sys/class/gpio/gpio149/direction') #set as output for LED
    return

def cleanupGPIO():
    print('Disabling GPIO pins...')
    os.system('echo 0 > /sys/class/gpio/gpio200/value')
    # time.sleep(1)
    os.system('echo 216 > /sys/class/gpio/unexport')
    # time.sleep(1)
    os.system('echo 0 > /sys/class/gpio/gpio149/value')
    # time.sleep(1)
    os.system('echo 149 > /sys/class/gpio/unexport')
    # time.sleep(1)

def onlineLED(status=True):
    if status==True:
        os.system('echo 1 > /sys/class/gpio/gpio149/value && sleep 1 && echo 0 > /sys/class/gpio/gpio149/value &')
    else:
        os.system('echo 0 > /sys/class/gpio/gpio149/value')
    return

def streamingLED(status=True):
    if status==True:
        os.system('echo 1 > /sys/class/gpio/gpio216/value && sleep 1 && echo 0 > /sys/class/gpio/gpio216/value &')
    else:
        os.system('echo 0 > /sys/class/gpio/gpio216/value')
    return

def importConfig():
    # this periodically reads the contents of the non-volatile configuration file '/home/oasis/Dekstop/settings.txt'
    # based on those configuration parameters, the variables can be reassigned during runtime with no
    # interruption of service

    global sample_rate
    global station_number
    global sps
    global data


    # print(chr(27) + "[2J")

    try: #attempt to open file
        with open('/home/oasis/Desktop/settings.txt') as w:
            data = json.load(w)
        if debug: print(colored("Good file read","green")) 
    except:
        if debug: print(colored("Bad file read","red"))
        if debug: time.sleep(1)
    if debug: time.sleep(1)
    if debug: print(colored('Reading constants...','cyan'))

    try: #attempt to read sample per second
        sps = data['settings']['sps']
        # sps = 10
        # print(1/sps)
        if debug: print(colored(f'The sps read from json settings is {sps}','cyan'))
        if sps >400 or np.isnan(sps) or sps==0:
            sps = 200
            if debug: print(colored('Bad sps err 1: Number out of scope, or not a number','red'))
        else:
            if debug: print(colored('Good sps','green'))
    except:
        sps = 200 #b ad read, setting to default
        if debug: print(colored('Bad sps err 2: Value unreadable','red'))
        if debug: time.sleep(1)
    if debug: time.sleep(1)

    try: #attempt to read sample per second
        station_number = data['settings']['station_number']
        if debug: print(station_number)
        if debug: print(colored(f'The station id read from json settings is {station_number}'),'cyan')
        if np.isnan(station_number):
            station_number = 0
            if debug: print(colored('Bad station_number err 1: Not a number','red'))
        else:
            if debug: print(colored('Good station_number','green'))
    except:
        station_number = 0 # bad read, setting to default
        if debug: print(colored('Bad station_number err 2: Value unreadable','red'))
        if debug: time.sleep(1)
    if debug: time.sleep(1)

    message = f'Setting {sps} samples per second...'
    if debug: print(colored(message,'cyan'))
    message = f'Setting station_number of {station_number}...'
    if debug: print(colored(message,'cyan'))
    sample_rate = 1/sps  # !!important step here, dont comment this out!!
    message = f'Setting sample_rate of {sample_rate}...'
    if debug: print(colored(message,'cyan'))
    if debug: time.sleep(1)


# setup_gpio() # preparing the gpio pins to drive some LED's
importConfig() # initial configuration of the board, must read settings.txt file before proceeding
get_IP_info()

def services_startup():
    global sensor, qwiicGPS, ads, bme680, temperature_offset
    # checking telegraf service is active
    if os.system('systemctl is-active telegraf --quiet') == 0:
        if debug: print(colored('telegraf consumer is online...','green'))
    else:
        if debug: print(colored('[!] telegraf consumer is inactive...','red'))
        if debug: time.sleep(1)
    if debug: time.sleep(1)

    # checking influxdb service is active
    if os.system('systemctl is-active influxdb --quiet') == 0:
        if debug: print(colored('influxdb storage is online...','green'))
    else:
        if debug: print(colored('[!] influxdb storage is inactive...','red'))
        if debug: time.sleep(1)
    if debug: time.sleep(1)

    #Initialize the I2C bus.
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        if debug: print(colored('i2c initialized successfully ...','green'))
    except:
        if debug: print(colored('[!] i2c failed to initialize...','red'))
        if debug: time.sleep(1)
    if debug: time.sleep(1)

    #Validate the LSM9DS1 is available on the i2c bus
    try:
        #sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
        device_list.sensor = adafruit_icm20x.ICM20948(i2c)
        #sensor.accel_range = adafruit_icm20x.ACCELRANGE_2G
        #sensor.accel_range = adafruit_lsm9ds1.ACCELRANGE_4G
        if debug: print(colored('adafruit_icm20x initialized successfully ...','green'))
    except(OSError, ValueError):
        if debug: print(colored('[!] Acceleration sensor not detected...','red'))
        if debug: time.sleep(1)
    if debug: time.sleep(1)

    #bring the GPS online
    try:
        device_list.qwiicGPS = qwiic_titan_gps.QwiicTitanGps()
        if device_list.qwiicGPS.connected is False:
            if debug: print("Could not connect to to the SparkFun GPS Unit. Double check that\
                it's wired correctly.", file=sys.stderr)
        device_list.qwiicGPS.begin()
        if debug: print(colored("XA1110 gps connected","green"))
    except:
        if debug: print(colored('could not connect to gps board','red'))
        if debug: time.sleep(1)
    if debug: time.sleep(1)

    #bring the ADC online
    try:
        device_list.ads = ADS.ADS1015(i2c)
        device_list.ads.mode = Mode.CONTINUOUS
        if debug: print(colored("ADS1015 adc connected","green"))
    except:
        if debug: print(colored("could not connect to ADC",'red'))

    #bring the RTC online
    # try:
    #     rtc.get_time
    #     if debug: print(colored("rtc connected","green"))
    # except:
    #     if debug: print(colored("could not connect to RTC",'red')) 

    try:
        device_list.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
        # change this to match the location's pressure (hPa) at sea level
        device_list.bme680.sea_level_pressure = 1014
        device_list.temperature_offset = -5
        if debug: print(colored("temp/humid/pres connected","green"))
    except:
        if debug: print(colored("temp/humid/pres not connected","red"))


#Initialize the MQTT client for remote publishing
#This is the client that is responsile for the cloud-based storage of data.
#Data is stored in InfluxDB via a Telegraf/MQTT input plugin (see project documentation)


#This function acquires data from the LSM9DS1 9DOF sensor and publishes the data in an MQTT data stream
#Please note that this function is called by the twisted.internet.task.LoopingCall function and executed by Reactor
def publishHealth():

    if debug: print(colored('publish health','magenta'))
    # get_IP_info()
    get_hardware_status()
    sample_time = time.time_ns() 
    if debug: print(sample_time)
    if device_list.qwiicGPS.get_nmea_data() is True:
            lat, lon, time_gps = device_list.qwiicGPS.gnss_messages['Latitude'], device_list.qwiicGPS.gnss_messages['Longitude'], device_list.qwiicGPS.gnss_messages['Time']
    if debug: print('lat,lon,time_gps',lat,lon,time_gps)

    if lat != 0 and lon != 0:
        location_info.lat = lat
        location_info.lon = lon
        location_info.geohash = pgh.encode(lat,lon)

    try:
        time_gps = time_gps.strftime("%H:%M:%S")
    except:
        time_gps = 0
    if debug: print('time_gps',time_gps)


    # geohash = 0
    health = [
        {   
            "name" : station_name,
            "region_ID" : "South_East",
            "time" : sample_time,
            "lat" : location_info.lat,
            "lon": location_info.lon,
            "time_gps" : time_gps,
            "geohash" : location_info.geohash,
            "global_IP" : globalIP,
            "local_IP": localIP,
            # "CPU_time" : hardware_stats.cpu_time,
            # "CPU_load" : hardware_stats.cpu_load,
            # "CPU_temp" : 0,
            # "mem_usage" : hardware_stats.mem_percent,
            # "disk_usage" : hardware_stats.disk_usage,
            # "packets_dropped" : hardware_stats.packet_drops,
            # "battery": 0,
            # "Temperature": device_list.bme680.temperature + device_list.temperature_offset,
            # "Gas":device_list.bme680.gas,
            # "Humidity":device_list.bme680.relative_humidity,
            # "Pressure":device_list.bme680.pressure,
            # "Altitude": device_list.bme680.altitude,
        }
    ]
    if debug: print("health is ", health)
    try:
        health_dict = fp.list2dict(health)
    except:
        if debug: print("Unexpected error:", sys.exc_info()[0])

    try:
        health = json.dumps(health)  #MQTT requires data to be formatted into JSON
    except:
        if debug: print("Unexpected error:", sys.exc_info()[0])
        
        # print(pos_dict['lat'], pos_dict['lon'],pos_dict['time_gps'])
    # if int(health_dict['lat'])==0 or int(health_dict['lon'])==0:
    #     pass
    # else:
    try:
        if debug: print("trying to publish ext health")
        mqtt_ext.publish("osnds/livestream/station/" + str(station_number) +"/health/",health,qos=0)  #publish the data to the remote mqtt server
    except:
        if debug: print("Unexpected error:", sys.exc_info()[0])

    try:
        if debug: print("trying to publish int health")
        mqtt_int.publish("osnds/livestream/station/" + str(station_number) +"/health/",health,qos=0)  #publish the data to the remote mqtt server
    except:
        if debug: print("Unexpected error:", sys.exc_info()[0])

    try:
        del health
    except:
        pass
    try:
        del health_dict
    except:
        pass
    try:
        del geohash
    except:
        pass
    try:
        del time_gps
    except:
        pass
    try:
        del lat, lon
    except:
        pass
    try:
        del sample_time
    except:
        pass

# def set_health_flag():
#     global health_flag
#     health_flag=True

def publishMessage():
    # get time from the realtime clock
    # timevar = rtc.get_time()

    #format the datetime object into the epoch time format of the required precision for grafana
    #the formatting options 06d and 04d are to help force the epoch time to be the correct length
    # epoch_time = int('{}{:06d}{:04d}'.format(timevar.strftime('%s'),timevar.microsecond,0))

    t = time.time()
    importConfig()
    global packet_id    #This is essentially a loop counter used to validate that packets weren't dropped and arrived in order
    global execution_time   #required for the first packet to be sent
    global sample_rate
    global sample_time

    if mqtt_ext.is_connected():
        if debug:print(colored("MQTT is connected is True","green"))
        if debug: time.sleep(1)
        # onlineLED(True)
    else:
        # onlineLED(False)
        if debug:print(colored("MQTT is connected is False","red"))
        if debug: time.sleep(1)

    if debug:print(colored("getting accel data","green"))
    sample_time = time.time_ns() 
    x, y, z = device_list.sensor.acceleration   #gets data from the accelerometer    # print(lat, lon, time_gps)
    if debug:print(colored("accel data is","yellow"))
    if debug:print(colored(str(x),"yellow"))    

    if debug:print(colored("getting adc data","green"))
    # single ended adc
    adc = AnalogIn(device_list.ads, ADS.P0)

    # differential adc
    # adc = AnalogIn(device_list.ads, ADS.P0, ADS.P1)

    # if debug:print(colored("adc data is","yellow"))
    # if debug:print(colored(str(adc.value), str(adc.voltage),"yellow"))        
    


    accel = [
        {
            "name" : station_name,
            "packet_id": packet_id,
            # "time":epoch_time,
            "time":sample_time,
            # "time_onboard": sample_time,
            # "time_chk": str(sample_time),
            "x": x,
            "y": y,
            "z": z,
            "delta_time": execution_time,
            "adc" : adc.voltage,
            # "adc" : 0.
        }
    ]
    try:
        accel = json.dumps(accel)  #MQTT requires data to be formatted into JSON
    except:
        if debug: print('error converting to json')       

    try: # attempt to stream out data externally
        # attaching the stream to a link thats associated with this station_number
        mqtt_ext.publish("osnds/livestream/station/" + str(station_number) +"/acceleration/",accel,qos=0)  #publish the data to the remote mqtt server
        # if the try hasnt failed, light the beacons
        # streamingLED(True)  
        if debug: print('successfully ext publishing')
    except:
        if debug: print("Unexpected error:", sys.exc_info()[0])
        # no good, Gondor is on its own
        # streamingLED(False)    
        if debug: print('error with ext publishing')

    # try: # attempt to stream out data internally
    #     # attaching the stream to a link thats associated with this station_number
    #     mqtt_int.publish("osnds/livestream/station/" + str(station_number) +"/acceleration/",accel,qos=0)  #publish the data to the remote mqtt server
    #     # if the try hasnt failed, light the beacons
    #     # streamingLED(True)  
    #     if debug: print('successfully ext publishing')
    # except:
    #     if debug: print("Unexpected error:", sys.exc_info()[0])
    #     # no good, Gondor is on its own
    #     # streamingLED(False)    
    #     if debug: print('error with int publishing')

    execution_time = time.time_ns()- sample_time    #used for troubleshooting - measures the function's execution time
    
    # some packet ordering that resets every second
    if packet_id == sps:
        packet_id = 0
        publishHealth()   
    else:
        packet_id = packet_id + 1
    # print(time.time()-t)
    print(adc.voltage)
    # print(t)
    try:
        del t
    except:
        pass
    try:
        del sample_time
    except:
        pass
    try: 
        del x,y,z
    except:
        pass
    try: 
        del adc
    except:
        pass
    try: 
        del accel
    except:
        pass
    # try: 
    #     del execution_time
    # except:
    #     pass
    
def mem_tracker():
    # print(chr(27) + "[2J")
    all_objects = muppy.get_objects()
    sum1 = summary.summarize(all_objects)
    summary.print_(sum1)

# def set_rtc_via_gps():
#     if qwiicGPS.get_nmea_data() is True:
#             lat, lon, time_gps = qwiicGPS.gnss_messages['Latitude'], qwiicGPS.gnss_messages['Longitude'], qwiicGPS.gnss_messages['Time']
#     if time_gps != 0:
#         timevar = time_gps
#         rtc.set_time()
# internal mqtt testing
# TODO Scrap this?

def mqtt_startup():
    global mqtt_ext, mqtt_int
    # try:
    #     mqtt_int = mqtt.Client(client_id=f'OSNDS Station {station_number}', userdata=None, transport="tcp")
    #     mqtt_int.connect("127.0.0.1",port=1883,keepalive=45)
    #     if debug: print(colored('Internal MQTT client connected successfully...','green'))
    # except:
    #     if debug: print(colored('Internal MQTT client failed to connect...','red'))
    #     if debug: time.sleep(1)
    # if debug: time.sleep(1)

    # the external MQTT connection is made here
    try:
        mqtt_ext = mqtt.Client(client_id=f'OSNDS Station {station_number}', userdata=None, transport="tcp")
        mqtt_ext.username_pw_set(username="aftac", password="sensor")
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        mqtt_ext.tls_set_context(context)
        #mqtt_ext.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
        mqtt_ext.connect("mqtt.osnds.net",port=8883,keepalive=45)
        mqtt_ext.subscribe("osnds/configuration/station",qos=2)
        if debug: print(colored('External MQTT client connected successfully...','green'))
        # a good connection was made so far
    except:
        if debug: print(colored('External MQTT client failed to connect...','red'))
        # connection issue, do not light
        if debug: time.sleep(1)
    if debug: time.sleep(1)

    # try:
    #     mqtt_ext2 = mqtt.Client(client_id=f'OSNDS Station {station_number}', userdata=None, transport="tcp")
    #     mqtt_ext2.username_pw_set(username="aftac", password="sensor")
    #     context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #     mqtt_ext2.tls_set_context(context)
    #     #mqtt_ext.tls_set(ca_certs=None,certfile=None,keyfile=None,ciphers=None)
    #     mqtt_ext2.connect("mqtt.osnds.net",port=8883,keepalive=45)
    #     mqtt_ext2.subscribe("osnds/configuration/station",qos=2)
    #     if debug: print(colored('External MQTT client connected successfully...','green'))
    #     # a good connection was made so far
    # except:
    #     if debug: print(colored('External MQTT client failed to connect...','red'))
    #     # connection issue, do not light
    #     if debug: time.sleep(1)
    # if debug: time.sleep(1)


#assign initial time to the RTC
# ds3231.datetime = time.time()
# print(ds3231)
services_startup()
mqtt_startup()

# mqtt_ext.on_message= on_message
mqtt_ext.loop_start()
if debug: time.sleep(1)
accel_loop = task.LoopingCall(publishMessage)
if debug: time.sleep(1)
if debug: print('starting with sample rate',sample_rate)
if debug: time.sleep(1)
accel_loop.start(1 if debug else (sample_rate-0.0034))    #sets the sample rate (200 sps = 1/200 = 0.005 seconds)
# accel_loop.start(0.001)    #sets the sample rate (200 sps = 1/200 = 0.005 seconds)



# if debug: time.sleep(1)
# health_loop = task.LoopingCall(publishHealth)
# if debug: time.sleep(1)
# if debug: print('starting with health report rate ', 1)
# if debug: time.sleep(1)
# health_loop.start(1)    #sets the sample rate (200 sps = 1/200 = 0.005 seconds)

# if debug: time.sleep(1)
# health__flag_loop = task.LoopingCall(set_health_flag)
# if debug: time.sleep(1)
# if debug: print('starting health__flag_loop ', 1)
# if debug: time.sleep(1)
# health__flag_loop.start(1)    #sets the sample rate (200 sps = 1/200 = 0.005 seconds)


# task.LoopingCall(mem_tracker).start(60)

task.LoopingCall(importConfig).start(1)
if debug: time.sleep(1)
if debug: print(colored('System is now online and publishing data...','green'))
if debug: time.sleep(1)
reactor.run()   #runs the function called in the argument of the LoopingCall
print('code interrupted')
# cleanupGPIO()
