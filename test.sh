#!/bin/bash
# create adhoc network function
#createAdHocNetwork(){
    echo "Creating ad-hoc network"
    ifconfig wlan0 down
    iwconfig wlan0 mode ad-hoc
    iwconfig wlan0 essid AccessPoint
    echo 2 > /sys/module/bcmdhd/parameters/op_mode
    ifconfig wlan0 11.0.0.1 netmask 255.255.255.0 up
    echo "Ad-hoc network created"
#}
# connect to wifi function
#connect(){
#    echo "Trying to connect to configured wifi"
#    ifdown wlan0
#    wpa_supplicant -B -i wlan0 -c /home/pi/pics/wpa_supplicant.conf
#    ifup wlan0
#    echo "Wifi configured"
#}
#echo "================================="
#echo "Wifi setup"
#echo "================================="
#connect
#echo "Checking connectivity..."
#sleep 5s
#ping -c 5 -I wlan0 google.com > /dev/null 2>&1
#PINGSTATUS=$?
#echo "Status"
#echo $PINGSTATUS
#if [ $PINGSTATUS -eq 0 ];
#    then
#        echo "Connected to WiFi"
#    else
#        echo "Wifi not connected, fallback to ad-hoc"
#        createAdHocNetwork
#fi
#exit 0
