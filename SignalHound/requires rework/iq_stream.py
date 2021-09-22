# -*- coding: utf-8 -*-

# This example tests the throughput of the IQ acquisition mode
# of the receiver. Adjust the DECIMATION parameter to decimate
# the IQ data stream. DECIMATION must be a power of two.
# You should see samples rates of 40 MS/sec / DECIMATION

from bbdevice.bb_api import *
import datetime

SAMPLES_PER_CAPTURE = 262144
NUM_CAPTURES = 1000
DECIMATION = 1
BANDWIDTH = 20.0e6 / DECIMATION

def stream_iq():
    # Open device
    handle = bb_open_device()["handle"]

    # Configure device
    bb_configure_center_span(handle, 1.0e9, 100.0e6)
    bb_configure_level(handle, -30.0, BB_AUTO_ATTEN)
    bb_configure_gain(handle, BB_AUTO_GAIN)
    bb_configure_IQ(handle, DECIMATION, BANDWIDTH)

    # Initialize
    bb_initiate(handle, BB_STREAMING, BB_STREAM_IQ)

    # Stream IQ
    print ("Streaming...")
    sample_count = 0
    start_time = datetime.datetime.now()
    for i in range(NUM_CAPTURES):
        iq = bb_get_IQ_unpacked(handle, SAMPLES_PER_CAPTURE, BB_FALSE)["iq"]
        sample_count += SAMPLES_PER_CAPTURE

    # Print stats
    time_diff = (datetime.datetime.now() - start_time).total_seconds()
    print (f"\nCaptured {sample_count} samples @ {sample_count / time_diff / 1e6} megasamples/sec")

    # Close device
    bb_close_device(handle)


if __name__ == "__main__":
    stream_iq()
