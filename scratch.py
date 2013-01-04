# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#Holoborodko for each variable

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
import boto, time, json, pprint
from datetime import datetime
import numpy as np

import scoring
import fetch.myS3 as myS3
import fetch.mySQS as mySQS
import validity_metrics as vm
from aws import aws_ak, aws_sk

# <codecell>

import scipy
from scipy.signal import butter, lfilter, filtfilt

Fs = 30 # 1 ns -> 1 GHz
N = 10 #filter order
Wn = 5 #this number is the cutoff freq for a lowpass. pull from Thesis
filter_saftey_margin = 1.15 #from filterAndDerivatives ln33

#Full code sample:
#b, a = scipy.signal.butter(N, Wn, 'low')
#above same as below (butter is wrapper for iirfilter w/ ftype=buter
b, a = scipy.signal.iirfilter(N, filter_saftey_margin*Wn/(Fs/2) , btype='low', ftype='butter')


#output_signal = scipy.signal.filtfilt(b, a, input_signal)

#filter_saftey_margin*Wn/(Fs/2)

# <codecell>

print b, a

# <codecell>


