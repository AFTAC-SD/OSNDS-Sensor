
########################################################
########################################################
######                                           #######
######  OSNDS Plugin for the SignalHound BB60C   #######
######  Real-time Spectrum Analyzer              #######
######  IQ Streaming Plugin v0.0.1               #######
######                                           #######
######  Written by: Jim Stroup, Chief, SIME      #######
######                                           #######
########################################################
########################################################


from bbdevice.bb60c_functions import * 
import os

os.system('cls')
print('''
############################################################################################
###  
###  OSNDS SignalHound BB60C Plugin (IQ Streaming Plugin)
###
###  Please ensure you have an active "Spike" terminal open or else this script will not work.
###  
############################################################################################\n''')

bb60c = initialize_connection(
			adapter = 'TCPIP0',
			ip_address = 'localhost',
			port = '5025',
			connection = 'SOCKET',
			timeout=120000000)

configure_single_iq(
			inst=bb60c,
			ref_level='-20DBM',
			center_freq='1GHz',
			sample_rate='9.7655kHz',
			sweep_time='.002')

configure_trace(bb60c)

iq_data = retrieve_iq_ascii(
			inst=bb60c, 
			sample_rate=19531)

plot_iqscatter(iq_data)

df_toInflux(data= iq_data,
			data_type="iq",
			host='localhost',
			port=8086,
			username='',
			password='',
			database='IQ',
			measurement='live_IQ')
