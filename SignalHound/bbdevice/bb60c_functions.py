
from influxdb import DataFrameClient
import pandas as pd
import numpy as np
import pyvisa
import time, math
import matplotlib.pyplot as plt
from scipy.signal import get_window
import seaborn as sns; sns.set()


# initialize connection to a generic VISA resource (this snippet can be used for most VISA applications)
def initialize_connection(adapter,ip_address,port,connection,timeout):
	# address:  (string) a combination of the adapter, IP, port, and connection method (e.g.)
	#    (ex.)  "TCPIP0::localhost::5025::SOCKET" 

	address = str(adapter+'::'+ip_address+'::'+port+'::'+connection)

	try:
		rm = pyvisa.ResourceManager()
		inst = rm.open_resource(address,open_timeout=timeout)
		print('[!] pyVISA resource has successfully connected to the folloing resource:',inst)

	except pyvisa.errors.VisaIOError as e:
		print('[!] ERROR: pyVISA resource (instrument) failed to connect.')
		inst.close()
	
	return inst


# configures the SignalHound BB60C for zero-span mode (neccessary for IQ streaming) 
def configure_single_sweep(inst,ref_level,center_freq,span):

	try:
		inst.read_termination = '\n'
		inst.write_termination = '\n'

		# Set the measurement mode to sweep
		inst.write("INSTRUMENT:SELECT SA")
		# Disable continuous meausurement operation
		inst.write("INIT:CONT OFF")

		# Configure a 20MHz span sweep at 1GHz
		# Set the RBW/VBW to auto
		inst.write("SENS:BAND:RES:AUTO ON; :BAND:VID:AUTO ON; :BAND:SHAPE FLATTOP")
		# Center/span
		inst.write(str("SENS:FREQ:SPAN "+span+"; CENT "+center_freq))
		# Reference level/Div
		inst.write("SENS:POW:RF:RLEV "+ref_level+"; PDIV 10")
		# Peak detector
		inst.write("SENS:SWE:DET:FUNC MINMAX; UNIT POWER")
	
		print('[!] INFO: pyVISA resource has been successfully configured for measurement.')

	except pyvisa.errors.VisaIOError as e:
		
		print('[!] ERROR: pyVISA resource (instrument) measurement configuration failed.')

	return inst


# requests IQ data from the instrument
#    - mode:         continuous vs instantaneous (not used at the moment)
#    - sample_rate:  sample rate of the device (hardcoded at the moment)
def retrieve_single_sweep(inst):

	try:

		t0 = time.time_ns()
		fft_array = pd.DataFrame()

		# Trigger a sweep, and wait for it to complete
		inst.query(":INIT; *OPC?")

		# Sweep data is returned as comma separated values
		data = inst.query("TRACE:DATA?")

		# Split the returned string into a list
		points = [float(x) for x in data.split(',')]
		fft_array['amplitudes'] = points
		fft_array['amplitudes'].astype(float)

		# Query information needed to know what frequency each point in the sweep refers to
		start_freq = float(inst.query("TRACE:XSTART?"))
		bin_size = float(inst.query("TRACE:XINC?"))
		numfftbins = len(points)
		stop_freq = start_freq + (bin_size * numfftbins)
		
		fftbins = np.linspace(start_freq,stop_freq,numfftbins)
		fft_array['frequencies'] = fftbins.astype(float)

		#fft_array.index = fft_array['frequencies']
		#signal.index = signal.index.astype('datetime64[ns]')
		
		print("[!] INFO: The following data was successfully collected (sample below).\n")

		print(fft_array.head(),'\n')

		# Find the peak point in the sweep
		peak_val = max(points)
		peak_idx = points.index(peak_val)
		peak_freq = start_freq + peak_idx * bin_size

		# Print out peak information
		print (f"[!] INFO: The peak amplitude was found to be {peak_val} dBm at {peak_freq / 1.0e6} MHz.\n")
		
		freq = peak_freq / 1.0e6

		#print("\n",signal.head(),"\n")

	except pyvisa.errors.VisaIOError as e:

		print("\n[!] ERROR: Instrument query failed to execute.\n[!] ERROR CODE:",e,"\n")

		try:

			inst.close()
			print('[!] INFO: pyVISA resource (instrument) has been successfully closed.')

		except:

			print('[!] ERROR: pyVISA resource (instrument) failed to close.')

	return fft_array


# configures the SignalHound BB60C for zero-span mode (neccessary for IQ streaming) 
def configure_single_iq(inst,ref_level,center_freq,sample_rate,sweep_time):
		
	try:

		inst.read_termination = '\n'
		inst.write_termination = '\n'

		inst.write("INSTRUMENT:SELECT ZS")

		inst.write("INIT:CONT OFF")
		#inst.write("INIT:CONT ON")

		inst.write(str("SENSE:ZS:CAPTURE:RLEVEL "+ref_level))
		inst.write(str("SENS:ZS:CAP:CENT "+center_freq))

		inst.write("ZS:CAP:CENT UP")
		inst.write("ZS:CAP:IFBW:AUTO")
		inst.write(str("ZS:CAPTURE:SRATE "+sample_rate))
		inst.write(str("ZS:CAP:SWEEP:TIME "+sweep_time))
		
		print('[!] INFO: pyVISA resource has been successfully configured for measurement.')

	except pyvisa.errors.VisaIOError as e:
		
		print('[!] ERROR: pyVISA resource (instrument) measurement configuration failed.')

	return inst


# configures the SignalHound BB60C for zero-span mode (neccessary for IQ streaming) 
def configure_streaming_iq(inst,ref_level,center_freq,sample_rate,sweep_time):
		
	try:

		inst.read_termination = '\n'
		inst.write_termination = '\n'

		inst.write("INSTRUMENT:SELECT ZS")

		#inst.write("INIT:CONT OFF")
		inst.write("INIT:CONT ON")

		inst.write(str("SENSE:ZS:CAPTURE:RLEVEL "+ref_level))
		inst.write(str("SENS:ZS:CAP:CENT "+center_freq))

		inst.write("ZS:CAP:CENT UP")
		inst.write("ZS:CAP:IFBW:AUTO")
		inst.write(str("ZS:CAPTURE:SRATE "+sample_rate))
		inst.write(str("ZS:CAP:SWEEP:TIME "+sweep_time))
		
		print('[!] INFO: pyVISA resource has been successfully configured for measurement.')

	except pyvisa.errors.VisaIOError as e:
		
		print('[!] ERROR: pyVISA resource (instrument) measurement configuration failed.')

	return inst


def plot_fftarray(fft_array):
	plt.plot(fft_array['frequencies'],fft_array['amplitudes'])
	plt.xlabel('Frequency (GHz)')
	plt.ylabel('Amplitude (dBm)')
	plt.show()


def plot_iqscatter(iq_data):

	print('[!] INFO: See pop-up display for (un)calibrated IQ.')
	plt.scatter(iq_data['I'],iq_data['Q'])
	plt.show

	# !!!!!!!!!!!!
	# experimental - this section was written after @stroup no longer had access to the receiver
	# !!!!!!!!!!!!
	
	window = get_window('hamming', len(iq_data['I']))
	window *= len(window) / sum(window)
	iq_data_FFT = np.fft.fftshift(np.fft.fft(iq_data * window) / len(window))
	
	print('[!] INFO: See pop-up display for calibrated IQ.')
	plt.plot(10 * np.log10(iq_data_FFT.real ** 2 + iq_data_FFT.imag ** 2))
	plt.show()


# configures the primary trace to get the data from
def configure_trace(inst):

	try:

		inst.write("TRAC:SEL 1") # Select trace 1
		inst.write("TRAC:TYPE WRITE") # Set clear and write mode
		inst.write("TRAC:UPD ON") # Set update state to on
		inst.write("TRAC:DISP ON") # Set un-hidden
		print('[!] INFO: pyVISA resource has been successfully configured for tracing.')

	except pyvisa.errors.VisaIOError as e:
			
		print('[!] ERROR: pyVISA resource (instrument) trace configuration failed.')


# requests IQ data from the instrument
#    - mode:         continuous vs instantaneous (not used at the moment)
#    - sample_rate:  sample rate of the device (hardcoded at the moment)
def retrieve_iq_ascii(inst, sample_rate):
	
	signal = pd.DataFrame()
	
	try:

		t0 = time.time_ns()

		timing = []
		
		data = inst.query(":FETCh:ZS? 1")
		data = data.split(',')
		data_array = pd.DataFrame(data)
		
		print("[!] INFO: The following data was successfully collected (sample below).")
		
		real = data_array.iloc[::2].reset_index(drop=True)
		imag = data_array.iloc[1::2].reset_index(drop=True)
		
		signal["I"] = real[0].astype(float)
		signal["Q"] = imag[0].astype(float)
		
		sample_rate = 19531
		numpoints = len(signal["I"])
		td =  (1/sample_rate)*numpoints
		t1 = t0 + int(td)
		
		timing = np.linspace(t0,t1,len(signal["I"]))
		#print(timing)
		#print("t0", t0,"\nt1",t1,"\nnumpoints",numpoints,"\ntd",td)

		signal.index = timing
		
		signal.index = pd.to_datetime(signal.index, unit='ns')
		signal.index = signal.index.astype('datetime64[ns]')

		print("\n",signal.head(),"\n")

	except pyvisa.errors.VisaIOError as e:

		print("\n[!] ERROR: Instrument query failed to execute.\n[!] ERROR CODE:",e,"\n")

		try:

			inst.close()
			print('[!] INFO: pyVISA resource (instrument) has been successfully closed.')

		except:

			print('[!] ERROR: pyVISA resource (instrument) failed to close.')

	return signal


# closes the connection to the provided instrument
def close_connection(inst):
	try:

		inst.close()
		print('[!] INFO: pyVISA resource (instrument) has been successfully closed.')

	except:

		print('[!] ERROR: pyVISA resource (instrument) failed to close.')


# writes a dataframe (with a datetime64[ns] index) to an influxdb instance
def df_toInflux(data,data_type,host,port,username,password,database,measurement):
	try:
		client = DataFrameClient(
						host=host, 
						port=port, 
						username=username, 
						password=password)

		client.create_database(database)

		r = client.write_points(
						data,
						measurement=measurement,
						database=database,
						time_precision="n",
						protocol='line')
		
		if r == True:
			print("[!] INFO: IQ data was successfully transferred to OSNDS.")

		else:

			print("\n[!] ERROR: The IQ data failed to be transferred to OSNDS.\n")

	except TypeError as e:
		print("\n[!] ERROR:",e,"\n")

