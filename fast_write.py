# -*- coding: utf-8 -*-
"""Tutorial how to use the class helper `SeriesHelper`."""

from influxdb import InfluxDBClient
from influxdb import SeriesHelper
import time
import numpy as np
from scipy import signal
from itertools import chain
# InfluxDB connections settings
# host = 'localhost'
# port = 8086
# user = ''
# password = ''
# dbname = 'telegraf'

# myclient = InfluxDBClient(host, port, user, password, dbname)

# Uncomment the following code if the database is not yet created
# myclient.create_database(dbname)
# myclient.create_retention_policy('awesome_policy', '3d', 3, default=True)


# class MySeriesHelper(SeriesHelper):
#     """Instantiate SeriesHelper to write points to the backend."""

#     class Meta:
#         """Meta class stores time series helper configuration."""

#         # The client should be an instance of InfluxDBClient.
#         client = myclient

#         # The series name must be a string. Add dependent fields/tags
#         # in curly brackets.
#         series_name = 'events.stats.{server_name}'

#         # Defines all the fields in this time series.
#         fields = ['time','data']

#         # Defines all the tags for the series.
#         tags = ['server_name']
#         # Defines the number of data points to store prior to writing
#         # on the wire.
#         bulk_size = 5

#         # autocommit must be set to True when using bulk_size
#         autocommit = False


# The following will create *five* (immutable) data points.
# Since bulk_size is set to 5, upon the fifth construction call, *all* data
# points will be written on the wire via MySeriesHelper.Meta.client.
# print(time.gmtime())       
x=np.arange(1,10,1)                                                     
print(x)
print(len(x))
#this grabs every third starting at 0
downsampled_ch1 = x[0::3]
#this grabs every third starting at 1
downsampled_ch2 = x[1::3]
downsampled_ch3 = x[2::3]
print(downsampled_ch1)
print(downsampled_ch2)
print(downsampled_ch3)

#set channels, or samnples per ns here
channels=3
channels_range=range(channels)
downsampled_ch=[]
for i in channels_range:
    downsampled_ch.append(x[i::channels])
    # print(downsampled_ch[i])

print([downsampled_ch[i] for i in channels])
# y=list(chain(*zip(downsampled_ch[0],downsampled_ch[1], downsampled_ch[2])))
# print(y)

# print(list(chain.from_iterable(zip(downsampled_ch[0],downsampled_ch[1],downsampled_ch[2]))))

# MySeriesHelper(server_name='us.east-1', data=1, time=1632260164000000)
# print(MySeriesHelper._json_body_())

# MySeriesHelper(server_name='us.east-1', data=2, time=1632260165000000)

# MySeriesHelper(server_name='us.east-1', data=3, time=1632260166000000)

# MySeriesHelper(server_name='us.east-1', data=4, time=1632260168000000)

# MySeriesHelper(server_name='us.east-1', data=5, time=1632260169000000)

# MySeriesHelper(server_name='us.east-1', data=6, time=1632260174000000)


# To manually submit data points which are not yet written, call commit:
# MySeriesHelper.commit()

# To inspect the JSON which will be written, call _json_body_():
# print(MySeriesHelper._json_body_())