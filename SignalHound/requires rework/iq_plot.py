# -*- coding: utf-8 -*-

# This example configures the receiver for IQ acquisition and plots
# the spectrum of a single IQ acquisition.

from bbdevice.bb_api import *

from scipy.signal import get_window
import matplotlib.pyplot as plt
import seaborn as sns; sns.set() # styling

def iq():
    # Open device
    handle = bb_open_device()["handle"]

    # Configure device
    bb_configure_center_span(handle, 1.0e9, 100.0e6)
    bb_configure_level(handle, -30.0, BB_AUTO_ATTEN)
    bb_configure_gain(handle, BB_AUTO_GAIN)
    bb_configure_IQ(handle, 1, 15.0e6)

    # Initialize
    bb_initiate(handle, BB_STREAMING, BB_STREAM_IQ)

    # Get IQ data
    iq = bb_get_IQ_unpacked(handle, 16384, BB_TRUE)["iq"]

    # No longer need device, close
    bb_close_device(handle)

    # FFT and plot

    # Create window
    window = get_window('hamming', len(iq))
    # Normalize window
    window *= len(window) / sum(window)
    # Window, FFT, normalize FFT output
    iq_data_FFT = numpy.fft.fftshift(numpy.fft.fft(iq * window) / len(window))
    # Convert to dBm
    plt.plot(10 * numpy.log10(iq_data_FFT.real ** 2 + iq_data_FFT.imag ** 2))
    plt.show()

if __name__ == "__main__":
    iq()
