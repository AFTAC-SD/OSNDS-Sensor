
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
###  OSNDS SignalHound BB60C Plugin (Sweep/FFT Processing Plugin)
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

configure_single_sweep(
			inst=bb60c,
			ref_level='-20DBM',
			center_freq='850MHz',
			span='1GHz')

configure_trace(bb60c)

fft_array = retrieve_single_sweep(inst=bb60c)

plot_fftarray(fft_array)

close_connection(bb60c)