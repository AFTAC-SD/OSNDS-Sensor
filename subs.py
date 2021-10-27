# This file is designed to constantly monitor a mqtt as a subscriber.  When it observes a message at
# osnds/configuration/station, it converts the message into a dictionary, observes whether it is for this station, and if so, updates
# all keys found within the message file.

import time
import paho.mqtt.client as paho
import ssl
import json 
import ast  #for evaluation the mqtt message and converting it into a dict
from collections import defaultdict #for manipulating dictionaries with potentially missing keys
import os

class system_vars():
    debug = True

debug=system_vars.debug

def setup_gpio():
    # for utilizing LED's to display the inner-workings at-a-glance
    
    # message received
    os.system('echo 194 > /sys/class/gpio/unexport')
    os.system('echo 194 > /sys/class/gpio/export') #stealing LCD TE pin 29    
    os.system('echo out > /sys/class/gpio/gpio194/direction') #set as output for LED
    return


def updateJSON(mqtt_dict):
    # print(chr(27) + "[2J")
    messageLED(True)
    if debug: print('# opening the non-volatile storage for device settings')
    filepath ='/home/oasis/Desktop/settings.txt'
    # filepath ='C:/Users/SAMMY/OneDrive/Desktop/settings.txt'
    try:
        with open(filepath,'r') as file: 
            if debug: print('# open file for read, as this might not be settings for this device')
            try: 
                if debug: print('# try loading the existing json/dict')
                static_file_dict=json.load(file)
            except: 
                if debug: print('# no json/dict found or corrupted')
                static_file_dict=defaultdict(dict) #make new dict, lets us assign keys to empty dict
                static_file_dict['settings']['station_number']=0 #assign a dummy station number just so we can build out a mqtt publish path
    except:
        if debug: print('# file doesnt exist, creating...')
        # if debug: time.sleep(1)
        static_file_dict = {
            'settings':{
            'station_number' : 1
            }
        }
        try:
            with open(filepath, "w+") as file: #since this was settings for us, open and overwrite contents
                        json.dump(static_file_dict,file) # write and close file
            if debug: print('# write complete')
            # if debug: time.sleep(1)
        except:
            if debug: print('write error')
    
    #cleaning the mqtt message
    if debug: print('mqtt before', mqtt_dict)
    # if debug: time.sleep(1)

    for key in mqtt_dict:
            mqtt_dict[key]=int(mqtt_dict[key]) #simple key reassign

    if debug: print('mqtt after', mqtt_dict)
    # if debug: time.sleep(1)

    if debug: print('# is this message for us?')
    if 'station_number' in mqtt_dict and static_file_dict['settings']['station_number']==mqtt_dict['station_number']:
        if debug: print('# yes message is for us')
        # if debug: time.sleep(1)
        # if debug: print(mqtt_dict)
        # if debug: time.sleep(1)
        # code blocks for options set by user

        if debug: print('# restart services in mqtt?')
        # if debug: time.sleep(1)
        if 'restart_services' in mqtt_dict:
            if debug: print('# restart services found')
            # if debug: time.sleep(1)
            if mqtt_dict['restart_services']==1:
                msg_str='# restart services command true'
                if debug: print(msg_str)
                # if debug: time.sleep(1)
                # mqtt_ext.publish(station_configured_as_location,msg_str,qos=0)
                # time.sleep(1)
                os.system('systemctl restart node-red && systemctl restart nodered.service')
            mqtt_dict.pop('restart_services', None)
        else:
            if debug: print('# restart services not found')
            # if debug: time.sleep(1)

        if debug: print('# restart node?')
        # if debug: time.sleep(1)
        if 'restart' in mqtt_dict:
            if debug: print('# restart command found')
            # if debug: time.sleep(1)
            if mqtt_dict['restart']==1:
                msg_str='# restart command true'
                if debug: print(msg_str)
                # if debug: time.sleep(1)
                # mqtt_ext.publish(station_configured_as_location,msg_str,qos=0)
                # time.sleep(1)
                os.system('shutdown -r now')
            mqtt_dict.pop('restart', None)
        else:
            if debug: print('# restart command not found')
            # if debug: time.sleep(1)

        if debug: print('# fan speed command?')
        # if debug: time.sleep(1)
        if 'fan_speed' in mqtt_dict:
            if debug: print('# fan_speed found in dict', mqtt_dict['fan_speed'])
            # if debug: time.sleep(1)
            if int(mqtt_dict['fan_speed'])==-1:
                mqtt_dict.pop('fan_speed',None)
            else:
                msg_str='# fan_speed found'
                if debug: print(msg_str)
                # if debug: time.sleep(1)
                # mqtt_ext.publish(station_configured_as_location,msg_str,qos=0)
                # time.sleep(1)
                command_str = '{}{}{}'.format('sh -c \'echo ',mqtt_dict['fan_speed'],' > /sys/devices/pwm-fan/target_pwm\'')
                if debug: print(command_str)
                os.system(command_str)
                mqtt_dict.pop('restart', None)
        else:
            if debug: print('fan_speed not found')
            # if debug: time.sleep(1)

        if 'sensor_tap' in mqtt_dict:
            if debug: print('# sensor_tap found in dict', mqtt_dict['sensor_tap'])
            teststr = '{}{}{}'.format('echo 255 > /sys/devices/pwm-fan/target_pwm && sleep ', mqtt_dict['sensor_tap'] ,' && echo 0 > /sys/devices/pwm-fan/target_pwm &')
            # print(teststr)
            os.system(teststr)
            # if mqtt_dict['sensor_tap']==1:
            #     os.system('echo 255 > /sys/devices/pwm-fan/target_pwm && sleep 5 && echo 0 > /sys/devices/pwm-fan/target_pwm &')
            # if mqtt_dict['sensor_tap']==2:
            #     os.system('echo 255 > /sys/devices/pwm-fan/target_pwm && sleep 10 && echo 0 > /sys/devices/pwm-fan/target_pwm &')
            mqtt_dict.pop('sensor_tap', None)

        if 'sps' in mqtt_dict:
            if debug: print('# sps found in dict', mqtt_dict['sps'])
            if mqtt_dict['sps']==-1 or static_file_dict['settings']['sps']==mqtt_dict['sps']:
                msg_str='# sps is unchanged'
                if debug: print(msg_str)
                # if debug: time.sleep(1)
                # mqtt_ext.publish(station_configured_as_location,msg_str,qos=0)
                # time.sleep(1)
                mqtt_dict.pop('sps', None)
                # if debug: time.sleep(1)
            else:
                if debug: print('# sps is changed')
                # if debug: time.sleep(1)
                if debug: print('# delayed restart to update sample rate')
                # if debug: time.sleep(1)
                # os.system('sleep 2 && reboot &')
                # os.system('sleep 2 && systemctl restart nodered.service &')
                if debug: print('# should post immediately, showing that restart is happening the background')

        if debug: print('# are we reassigning the station number?')
        if 'new_station_number' in mqtt_dict: 
            if debug: print('# maybe, new_station_number found')
            # if debug: time.sleep(1)
            if mqtt_dict['new_station_number']== -1:
                if debug: print('# not for us, new_station_number==0')
                # if debug: time.sleep(1)
                if debug: print('# removing this key for the key loop, since we dont want to update')
                # if debug: time.sleep(1)
                mqtt_dict.pop('new_station_number', None) # remove this key from the dict, we are done with it
            else:
                if debug: print('# yes new_station_number is for us')
                # if debug: time.sleep(1)
                if debug: print('# reassigning new station id to the storage')
                # if debug: time.sleep(1)
                static_file_dict['settings']['station_number']=mqtt_dict['new_station_number']
                if debug: print('# deleting new id key')
                # if debug: time.sleep(1)
                mqtt_dict.pop('new_station_number', None) # remove this key from the dict, we are done with it
                if debug: print('# deleting the current station id key')
                # if debug: time.sleep(1)
                mqtt_dict.pop('station_number',None)  #remove this key as well
        else:
            if debug: print('# new_station_number not found')
            # if debug: time.sleep(1)
            # not reassigning
            # debugging code was here
            pass
        
        if debug: print('# step through each key in the mqtt msg')
        # if debug: time.sleep(1)
        for key in mqtt_dict:
            static_file_dict['settings'][key]=mqtt_dict[key] #simple key reassign
        with open(filepath, "w+") as file: #since this was settings for us, open and overwrite contents
            json.dump(static_file_dict,file) # write and close file
    else:
        if debug: print('# msg not for us')

    station_configured_as_location = "osnds/livestream/station/current_config/"
    if debug: print(f'# publish address is:{station_configured_as_location}')
    # if debug: time.sleep(1)
    if debug: print(f'# writing current configuration {static_file_dict}')
    # if debug: time.sleep(1)
    # print(type(static_file_dict))

    mqtt_ext.publish(station_configured_as_location,json.dumps(static_file_dict),qos=0)
            

#define callback
def on_message(client, userdata, mqtt_msg):
    if debug: print('# message received:', mqtt_msg.payload)
    mqtt_msg=mqtt_msg.payload #pull out the payload from the message
    mqtt_msg=mqtt_msg.decode('utf-8') #convert the byte literal to string
    if mqtt_msg[0]=='[' and mqtt_msg[-1]==']': # correcting format issues
        mqtt_msg=mqtt_msg[1:-1] #trim the string for [ ] characters
    mqtt_dict = ast.literal_eval(mqtt_msg) #convert string to dictionary
    updateJSON(mqtt_dict) # send dictionary to be saved to non-volatile storage


def on_connect(client, userdata, flags, rc):
    # if debug: print("# Connecting...")
    mqtt_ext.subscribe("osnds/configuration/station")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

def messageLED(status=True):
    if status==True:
        os.system('echo 1 > /sys/class/gpio/gpio194/value && sleep 1 && echo 0 > /sys/class/gpio/gpio194/value &')
    else:
        os.system('echo 0 > /sys/class/gpio/gpio194/value')
    return

setup_gpio()

mqtt_ext= paho.Client(client_id="Subscriber Client") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
######Bind function to callback
mqtt_ext.on_message=on_message
mqtt_ext.on_connect=on_connect
#####
if debug: print("# connecting to broker ",mqtt_ext)

mqtt_ext.username_pw_set(username="aftac", password="sensor")
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
mqtt_ext.tls_set_context(context)
mqtt_ext.connect("mqtt.osnds.net",port=8883,keepalive=45)
time.sleep(2)
if debug: print("# starting loop forever")
mqtt_ext.loop_forever() #start loop to process received messages
