# -*- coding: utf-8 -*-

# Copyright (c) 2019 Signal Hound
# For licensing information, please see the API license in the software_licenses folder

from ctypes import *
import numpy

bblib = CDLL(r"bbdevice/bb_api.dll")


# ---------------------------------- Defines -----------------------------------

BB_TRUE = 1
BB_FALSE = 0

BB_MAX_DEVICES = 8

# Modes
BB_IDLE = -1
BB_SWEEPING = 0
BB_REAL_TIME = 1
BB_STREAMING = 4
BB_AUDIO_DEMOD = 7
BB_TG_SWEEPING = 8

# RBW shapes
BB_RBW_SHAPE_NUTTALL = 0
BB_RBW_SHAPE_FLATTOP = 1
BB_RBW_SHAPE_CISPR = 2

# Detectors
BB_MIN_AND_MAX = 0
BB_AVERAGE = 1

# Scales
BB_LOG_SCALE = 0
BB_LIN_SCALE = 1
BB_LOG_FULL_SCALE = 2
BB_LIN_FULL_SCALE = 3

# Levels
BB_AUTO_ATTEN = c_double(-1.0)
BB_AUTO_GAIN = -1

# Video processing units
BB_LOG = 0
BB_VOLTAGE = 1
BB_POWER = 2
BB_SAMPLE = 3

# Spur reject
BB_NO_SPUR_REJECT = 0
BB_SPUR_REJECT = 1

# Audio
BB_DEMOD_AM = 0
BB_DEMOD_FM = 1
BB_DEMOD_USB = 2
BB_DEMOD_LSB = 3
BB_DEMOD_CW = 4

# Streaming flags
BB_STREAM_IQ = 0
BB_STREAM_IF = 1 # Deprecated
BB_DIRECT_RF = 2 # BB60C only
BB_TIME_STAMP = 16

# Configure IO: port1
BB_PORT1_AC_COUPLED = 0
BB_PORT1_DC_COUPLED = 4
BB_PORT1_10MHZ_USE_INT = 0
BB_PORT1_10MHZ_REF_OUT = 256
BB_PORT1_10MHZ_REF_IN = 8
BB_PORT1_OUT_LOGIC_LOW = 20
BB_PORT1_OUT_LOGIC_HIGH = 28

# Configure IO: port2
BB_PORT2_OUT_LOGIC_LOW = 0
BB_PORT2_OUT_LOGIC_HIGH = 32
BB_PORT2_IN_TRIGGER_RISING_EDGE = 64
BB_PORT2_IN_TRIGGER_FALLING_EDGE = 96

# --------------------------------- Mappings ----------------------------------

bbOpenDeviceBySerialNumber = bblib.bbOpenDeviceBySerialNumber

bbOpenDevice = bblib.bbOpenDevice
bbCloseDevice = bblib.bbCloseDevice

bbConfigureAcquisition = bblib.bbConfigureAcquisition
bbConfigureCenterSpan = bblib.bbConfigureCenterSpan
bbConfigureIQCenter = bblib.bbConfigureIQCenter
bbConfigureLevel = bblib.bbConfigureLevel
bbConfigureGain = bblib.bbConfigureGain
bbConfigureSweepCoupling = bblib.bbConfigureSweepCoupling
bbConfigureProcUnits = bblib.bbConfigureProcUnits
bbConfigureIO = bblib.bbConfigureIO
bbConfigureDemod = bblib.bbConfigureDemod
bbConfigureIQ = bblib.bbConfigureIQ
bbConfigureIQDataType = bblib.bbConfigureIQDataType
bbConfigureRealTime = bblib.bbConfigureRealTime
bbConfigureRealTimeOverlap = bblib.bbConfigureRealTimeOverlap

bbInitiate = bblib.bbInitiate

bbFetchTrace_32f = bblib.bbFetchTrace_32f
bbFetchTrace_32f.argtypes = [
    c_int,
    c_int,
    numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
    numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C')
]
bbFetchTrace = bblib.bbFetchTrace # TODO: @stroup - requires rework w/ 32-bit DLL to 64 bit DLL
bbFetchTrace.argtypes = [
    c_int,
    c_int,
    numpy.ctypeslib.ndpointer(numpy.float64, ndim=1, flags='C'),
    numpy.ctypeslib.ndpointer(numpy.float64, ndim=1, flags='C')
]
bbFetchRealTimeFrame = bblib.bbFetchRealTimeFrame
bbFetchRealTimeFrame.argtypes = [
    c_int,
    numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
    numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
    numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
    numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C')
]
bbFetchAudio = bblib.bbFetchAudio
bbFetchAudio.argtypes = [
    c_int,
    numpy.ctypeslib.ndpointer(c_float, ndim=1, flags='C')
]
bbGetIQUnpacked = bblib.bbGetIQUnpacked
bbGetIQUnpacked.argtypes = [
    c_int,
    numpy.ctypeslib.ndpointer(numpy.complex64, ndim=1, flags='C'),
    c_int,
    POINTER(c_int),
    c_int,
    c_int,
    POINTER(c_int),
    POINTER(c_int),
    POINTER(c_int),
    POINTER(c_int)
]

bbQueryTraceInfo = bblib.bbQueryTraceInfo
bbQueryRealTimeInfo = bblib.bbQueryRealTimeInfo
bbQueryRealTimePoi = bblib.bbQueryRealTimePoi
bbQueryStreamInfo = bblib.bbQueryStreamInfo
bbGetIQCorrection = bblib.bbGetIQCorrection

bbAbort = bblib.bbAbort
bbPreset = bblib.bbPreset
bbPresetFull = bblib.bbPresetFull
bbSelfCal = bblib.bbSelfCal
bbSyncCPUtoGPS = bblib.bbSyncCPUtoGPS

bbGetDeviceType = bblib.bbGetDeviceType
bbGetSerialNumber = bblib.bbGetSerialNumber
bbGetFirmwareVersion = bblib.bbGetFirmwareVersion
bbGetDeviceDiagnostics = bblib.bbGetDeviceDiagnostics

bbAttachTg = bblib.bbAttachTg
bbIsTgAttached = bblib.bbIsTgAttached
bbConfigTgSweep = bblib.bbConfigTgSweep
bbStoreTgThru = bblib.bbStoreTgThru
bbSetTg = bblib.bbSetTg
bbGetTgFreqAmpl = bblib.bbGetTgFreqAmpl
bbSetTgReference = bblib.bbSetTgReference

bbGetAPIVersion = bblib.bbGetAPIVersion
bbGetAPIVersion.restype = c_char_p
bbGetProductID = bblib.bbGetProductID
bbGetProductID.restype = c_char_p
bbGetErrorString = bblib.bbGetErrorString
bbGetErrorString.restype = c_char_p


# ---------------------------------- Utility ----------------------------------

def error_check(func):
    def print_status_if_error(*args, **kwargs):
        return_vars = func(*args, **kwargs)
        if "status" not in return_vars.keys():
            return return_vars
        status = return_vars["status"]
        if status != 0:
            print (f"{'Error' if status < 0 else 'Warning'} {status}: {bb_get_error_string(status)} in {func.__name__}()")
        if status < 0:
            exit()
        return return_vars
    return print_status_if_error


# --------------------------------- Functions ---------------------------------

@error_check
def bb_open_device_by_serial_number(serial_number):
    device = c_int(-1)
    status = bbOpenDeviceBySerialNumber(byref(device), serial_number)
    return {
        "status": status,
        "handle": device.value
    }

@error_check
def bb_open_device():
    device = c_int(-1)
    status = bbOpenDevice(byref(device))
    return {
        "status": status,
        "handle": device.value
    }

@error_check
def bb_close_device(device):
    return {
        "status": bbCloseDevice(device)
    }

@error_check
def bb_configure_acquisition(device, detector, scale):
    return {
        "status": bbConfigureAcquisition(device, detector, scale)
    }

@error_check
def bb_configure_center_span(device, center, span):
    return {
        "status": bbConfigureCenterSpan(device, c_double(center), c_double(span))
    }

@error_check
def bb_configure_IQ_center(device, center):
    return {
        "status": bbConfigureIQCenter(device, c_double(center))
    }

@error_check
def bb_configure_level(device, ref, atten):
    return {
        "status": bbConfigureLevel(device, c_double(ref), atten)
    }

@error_check
def bb_configure_gain(device, gain):
    return {
        "status": bbConfigureGain(device, gain)
    }

@error_check
def bb_configure_sweep_coupling(device, rbw, vbw, sweep_time, rbw_shape, rejection):

    return {
        "status": bbConfigureSweepCoupling(device, c_double(rbw), c_double(vbw), c_double(sweep_time), rbw_shape, rejection)
    }

@error_check
def bb_configure_proc_units(device, units):
    return {
        "status": bbConfigureProcUnits(device, units)
    }

@error_check
def bb_configure_IO(device, port1, port2):
    return {
        "status": bbConfigureIO(device, port1, port2)
    }

@error_check
def bb_configure_demod(device, modulation_type, freq, IFBW, audio_low_pass_freq, audio_high_pass_freq, FM_deemphasis):
    return {
        "status": bbConfigureDemod(device, modulation_type, c_double(freq), c_float(IFBW), c_float(audio_low_pass_freq), c_float(audio_high_pass_freq), c_float(FM_deemphasis))
    }

@error_check
def bb_configure_IQ(device, downsample_factor, bandwidth):
    return {
        "status": bbConfigureIQ(device, downsample_factor, c_double(bandwidth))
    }

@error_check
def bb_configure_IQ_data_type(device, data_type):
    return {
        "status": bbConfigureIQDataType(device, data_type)
    }

@error_check
def bb_configure_real_time(device, frame_scale, frame_rate):
    return {
        "status": bbConfigureRealTime(device, c_double(frame_scale), frame_rate)
    }

@error_check
def bb_configure_real_time_overlap(device, advance_rate):
    return {
        "status": bbConfigureRealTimeOverlap(device, c_double(advance_rate))
    }

@error_check
def bb_initiate(device, mode, flag):
    return {
        "status": bbInitiate(device, mode, flag)
    }

@error_check
def bb_fetch_trace_32f(device, sweep_size):
    min_vals = numpy.zeros(sweep_size).astype(numpy.float32)
    max_vals = numpy.zeros(sweep_size).astype(numpy.float32)
    status = bbFetchTrace_32f(device, sweep_size, min_vals, max_vals)
    return {
        "status": status,
        "min": min_vals,
        "max": max_vals
    }

@error_check
def bb_fetch_real_time_frame(device):
    ret = bb_query_trace_info(device)
    if ret["status"] is not 0:
        return {
            "status": ret["status"]
        }
    sweep_size = ret["sweep_size"]

    ret = bb_query_real_time_info(device)
    if ret["status"] is not 0:
        return {
            "status": ret["status"]
        }
    frame_width = ret["frame_width"]
    frame_height = ret["frame_height"]

    sweep_min = numpy.zeros(sweep_size).astype(numpy.float32)
    sweep_max = numpy.zeros(sweep_size).astype(numpy.float32)
    frame = numpy.zeros(frame_width * frame_height).astype(numpy.float32)
    alpha_frame = numpy.zeros(frame_width * frame_height).astype(numpy.float32)

    status = bbFetchRealTimeFrame(device,
                                  sweep_min, sweep_max,
                                  frame, alpha_frame)
    return {
        "status": status,
        "sweep_min": sweep_min,
        "sweep_max": sweep_max,
        "frame": frame,
        "alpha_frame": alpha_frame
    }

@error_check
def bb_fetch_audio(device):
    audio = numpy.zeros(4096).astype(c_float)

    status = bbFetchAudio(device, audio)

    return {
        "status": status,
        "audio": audio
    }

@error_check
def bb_fetch_trace(device, sweep_size):
    min_vals = numpy.zeros(sweep_size).astype(numpy.float64)
    max_vals = numpy.zeros(sweep_size).astype(numpy.float64)
    status = bbFetchTrace(device, sweep_size, min_vals, max_vals)
    print_status_if_error(device, status, "bbFetchTrace")
    return {
        "status": status,
        "min": min_vals,
        "max": max_vals
    }

@error_check
def bb_get_IQ_unpacked(device, iq_count, purge, triggers = c_long(0), trigger_count = 0):
    iq_data = numpy.zeros(iq_count).astype(numpy.complex64)
    data_remaining = c_int(0)
    sample_loss = c_int(0)
    sec = c_int(0)
    nano = c_int(0)
    status = bbGetIQUnpacked(device, iq_data, iq_count, triggers, trigger_count, purge, byref(data_remaining), byref(sample_loss), byref(sec), byref(nano));
    return {
        "status": status,
        "iq": iq_data,
        "data_remaining": data_remaining.value,
        "sample_loss": sample_loss.value,
        "sec": sec.value,
        "nano": nano.value
    }

@error_check
def bb_query_trace_info(device):
    sweep_size = c_int(0)
    bin_size = c_double(0)
    start_freq = c_double(0)
    status = bbQueryTraceInfo(device, byref(sweep_size), byref(bin_size), byref(start_freq))
    return {
        "status": status,
        "sweep_size": sweep_size.value,
        "bin_size": bin_size.value,
        "start_freq": start_freq.value
    }

@error_check
def bb_query_real_time_info(device):
    frame_width = c_int(0)
    frame_height = c_int(0)
    status = bbQueryRealTimeInfo(device, byref(frame_width), byref(frame_height))
    return {
        "status": status,
        "frame_width": frame_width.value,
        "frame_height": frame_height.value
    }

@error_check
def bb_query_real_time_poi(device):
    poi = c_double(0)
    status = bbQueryRealTimePoi(device, byref(poi))
    return {
        "status": status,
        "poi": poi.value
    }

@error_check
def bb_query_stream_info(device):
    return_len = c_int(0)
    bandwidth = c_double(0)
    samples_per_sec = c_int(0)
    status = bbQueryStreamInfo(device, byref(return_len), byref(bandwidth), byref(samples_per_sec))
    return {
        "status": status,
        "return_len": return_len.value,
        "bandwidth": bandwidth.value,
        "samples_per_sec": samples_per_sec.value
    }

@error_check
def bb_get_IQ_Correction(device):
    correction = c_double(0)
    status = bbGetIQCorrection(device, byref(correction))
    return {
        "status": status,
        "correction": correction.value
    }

@error_check
def bb_abort(device):
    return {
        "status": bbAbort(device)
    }

@error_check
def bb_preset(device):
    return {
        "status": bbPreset()
    }

@error_check
def bb_self_cal(device):
    return {
        "status": bbSelfCal()
    }

@error_check
def bb_sync_CPU_to_GPS(device, com_port, baud_rate):
    return {
        "status": bbSyncCPUtoGPS(com_port, baud_rate)
    }

@error_check
def bb_get_device_type(device):
    dev_type = c_int(0)
    status = bbGetDeviceType(device, byref(dev_type))
    return {
        "status": status,
        "dev_type": dev_type.value
    }

@error_check
def bb_get_serial_number(device):
    sid = c_int(0)
    status = bbGetSerialNumber(device, byref(sid))
    return {
        "status": status,
        "serial": sid.value
    }

@error_check
def bb_get_firmware_version(device):
    version = c_int(0)
    status = bbGetFirmwareVersion(device, byref(version))
    return {
        "status": status,
        "version": version.value
    }

@error_check
def bb_get_device_diagnostics(device):
    temperature = c_float(0)
    usb_voltage = c_float(0)
    usb_current = c_float(0)
    status = bbGetDeviceDiagnostics(device, byref(temperature), byref(usb_voltage), byref(usb_current))
    return {
        "status": status,
        "temperature": temperature.value,
        "usb_voltage": usb_voltage.value,
        "usb_current": usb_current.value
    }

@error_check
def bb_attach_TG(device):
    return {
        "status": bbAttachTg()
    }

@error_check
def bb_is_TG_attached(device):
    is_attached = c_int(0)
    status = bbIsTgAttached(device, byref(is_attached))
    return {
        "status": status,
        "is_attached": is_attached.value
    }

@error_check
def bb_config_TG_sweep(device, sweep_size, high_dynamic_range, passive_device):
    return {
        "status": bbConfigTgSweep(device, sweep_size, high_dynamic_range, passive_device)
    }

@error_check
def bb_store_TG_thru(device, flag):
    return {
        "status": bbStoreTgThru(device, flag)
    }

@error_check
def bb_set_TG(device, frequency, amplitude):
    return {
        "status": bbSetTg(device, c_double(frequency), c_double(amplitude))
    }

@error_check
def bb_get_TG_freq_ampl(device):
    frequency = c_double(0)
    amplitude = c_double(0)
    status = bbGetTgFreqAmpl(byref(frequency), byref(amplitude))
    return {
        "status": status,
        "frequency": frequency,
        "amplitude": amplitude
    }

@error_check
def bb_set_TG_reference(device, reference):
    return {
        "status": bbSetTgReference(device, reference)
    }

def bb_get_API_version():
    return {
        "api_version": bbGetAPIVersion()
    }


def bb_get_product_ID():
    return {
        "product_id": bbGetProductID()
    }

def bb_get_error_string(status):
    return {
        "error_string": bbGetErrorString(status)
    }
