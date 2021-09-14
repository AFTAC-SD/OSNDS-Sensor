from obspy import read
# import matplotlib.pyplot as plt
st = read("C:/Users/samuel.stevens/Documents/GitHub/OSNDS-TICKG/0.mseed")
# print(st)
# print(st[0].stats)
# for k, v in sorted(st[0].stats.mseed.items()):
#     print("'%s': %s" % (k, str(v))) 
# print(st[0].data)
# plt.plot(st[0].data)
# plt.show()

from telegraf.client import TelegrafClient
client = TelegrafClient(host='localhost', port=8092)

# Records a single value with no tags
# client.metric('some_metric', 123)

# Records a three values with different data types
# client.metric('mseedfile', st[0].data)
# while(1):
    # print('looping')
for i in st[0]:
    print(i)
    client.metric('some_metric', int(i))

# # Records a single value with one tag
# client.metric('some_metric', 123, tags={'server_name': 'my-server'})