# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
import boto, time, json, pprint
from datetime import datetime
import numpy as np

import scoring, boto
import fetch.myS3 as myS3
import fetch.mySQS as mySQS
import validity_metrics as vm
from aws import aws_ak, aws_sk

# <codecell>

import scrub
from matplotlib import pyplot as plt
import scipy

# <codecell>

conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')
filename = 'edge1/2012/12/12.21.16.43.362.0.txt'
data, meta = myS3.getData(bucket, filename, labeled=True)

# <codecell>

feat = 'ThG_L'
time = data['%Time_V1']
fs = len(time)/time[-1]

plt.figure(figsize = (20,8))
plt.plot(time,  data[feat])

N = 10
filter_saftey_margin = 1.0
Fs = 10*2*np.pi
Wn = scrub.fcth[feat[:-2]][0]
from scipy.signal import butter, lfilter, filtfilt

b, a = scipy.signal.iirfilter(N, filter_saftey_margin*Wn/(Fs/2), btype='low', ftype='butter')
filt =  scipy.signal.filtfilt(b, a, data[feat])

plt.plot(time, filt, 'r')
df = scrub.holo(filt, 1/fs)
plt.plot(time, df, 'g')

# <codecell>

df

# <headingcell level=2>

# Filter and Derivative Validation

# <codecell>

x = arange(0,4*np.pi,.1)
siny = np.sin(x)
sin60 = np.sin(60/(2*np.pi)*x)*.2
noise = (np.random.rand(1, len(siny))[0]-0.5)*.3
sig = siny+noise+sin60
plt.plot(x,sig,x,siny)
plt.plot(x,sin60,'r')

# <codecell>

print b, a

# <codecell>

N = 10
filter_saftey_margin = 1.0
Fs = 10*2*np.pi
Wn = 3
from scipy.signal import butter, lfilter, filtfilt

b, a = scipy.signal.iirfilter(N, filter_saftey_margin*Wn/(Fs/2), btype='low', ftype='butter')
filt =  scipy.signal.filtfilt(b, a, sig)

dfilt = scrub.holo(filt, 1/Fs*2*np.pi)
plt.figure(figsize = (12,8))
plt.plot(x, siny, 'g', x, scrub.holo(siny,1/Fs*2*np.pi), 'm')
plt.plot(x, filt,'b', x, dfilt, 'r')
plt.plot(x, sig, 'b-')
plt.legend(('siny','dsiny','filt','dfilt','raw'))

# <codecell>


