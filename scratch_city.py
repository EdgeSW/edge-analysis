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
import validity_metrics as vm
from aws import aws_ak, aws_sk
from boto.sqs.message import Message

# <codecell>

filename = 'edge8/2012/12/07.20.57.25.358.1.txt'

conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')
data, meta = myS3.getData(bucket, filename, labeled=True)

# <codecell>

for a in np.diff(data['Rot_L']):
    if a > 1000: print a

# <codecell>

data['Rot_L'][:3000]+offset

# <codecell>

offset = int(309237644.304/2)
print data['Rot_L'][0] - offset

# <codecell>

print offset

# <codecell>

import matplotlib
plot(data['Rot_L'][30:3000]+offset)

# <codecell>


