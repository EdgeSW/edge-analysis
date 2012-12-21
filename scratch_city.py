# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
import boto, time, json, pprint
from datetime import datetime
import numpy as np

import scoring
import fetch.myS3 as myS3
import fetch.mySQS as mySQS
import scrub
import validity_metrics as vm
from aws import aws_ak, aws_sk
from boto.sqs.message import Message

# <codecell>

'''
conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')
filename = 'edge1/2012/12/12.21.16.43.362.0.txt'
data, meta = myS3.getData(bucket, filename, labeled=True)
scoring.save_pickle(data, 'data.txt')
'''
data = scoring.load_pickle('C:\\Users\\Tyler\\data.txt')

# <codecell>

import numpy as np
import matplotlib.pyplot as plt
import time

plt.ion()

i=0

fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(-data['ThG_R'][i:i+600],  data['Fg_R'][i:i+600], '.') # Returns a tuple of line objects, thus the comma
ax.set_title('Time: %d sec'%i)
for i in range(i,len(data['Fg_R']),5):
    line1.set_ydata(data['Fg_R'][i:i+600])
    line1.set_xdata(-data['ThG_R'][i:i+600])
    if i == 0: i = 1
    ax.set_title('Time: %.1f sec'%(i/30.0) )
    fig.canvas.draw()
    #time.sleep(.08)

# <codecell>

data['%Time_V1'][-1]

# <codecell>

len(range(i,len(data['Fg_R']),5))

# <codecell>


