Contact Information: support@signalhound.com

# Prerequisites:
Python 3 is required to use the Python interface functions. The API has been
tested with Python 3.6.1 on Windows.

The Spike software must be fully installed before using the Python
interface functions. Additionally, ensure the BB60C is stable and
functioning in Spike before using the Python interface.

Several SciPy and NumPy packages are required to use the Python interface
functions, due to the need for fast array processing. The easiest way is to
install the SciPy stack, available here: https://www.scipy.org/install.html.
Alternatively, the necessary individual packages could be installed.

For our tests we used the 64-bit version of Anaconda for Windows.

# Purpose:
This project enables the user to retrieve sampled IQ data and frequency
sweeps from the BB60C receiver through a number of convenience functions
written in Python. These functions serve as a thin wrapper to our BB API,
and perform the majority of C DLL interfacing necessary to communicate
with the receiver.

# Setup:
Place the bb_api.py and bb_api.dll files into the bbdevice/ folder.

To call the functions from outside the bbdevice/ directory you may need to add the
bbdevice folder to the Python search path and to the system path. This can be done
by editing PATH and PYTHONPATH in: Control Panel > System and Security > System
> Advanced system settings > Advanced > Environment Variables > System variables.

To run the example scripts, navigate to the folder containing the example
.py files. Each example file is standalone and provides example code for calling the
provided Python functions for the BB60C.

# Usage:
The functions under the "Functions" heading are callable from external scripts.
They are functionally equivalent to their C counterparts, except memory management
is handled by the API instead of the user. Data is returned in Numpy arrays by the
acquisition functions.
