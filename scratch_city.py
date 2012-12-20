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

b = 'edge11/2012/12/20.03.09.33.109.1.txt' #right rot w/o index
g = 'edge11/2012/12/20.03.12.47.109.1.txt' #rignt rot with index

conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org-test')
data, meta = myS3.getData(bucket, b, labeled=True)

# <codecell>

for a in np.diff(data['Rot_R']):
    if a > 1000: print a

# <codecell>

offset =  309237643.8/2
print round(offset)
#data['Rot_L'][:3000]+offset

# <codecell>

offset = int(309237644.304/2)
print data['Rot_L'][0] - offset

# <codecell>

print offset

# <codecell>

import matplotlib
plot(data['Rot_L'][30:3000]+offset)

# <codecell>


# <codecell>

conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')
filename = 'edge0/2012/07/21.07.05.31.109.0.txt'
data, meta = myS3.getData(bucket, filename, labeled=True)

jsonSimscore = vm.summary_metrics(meta, data, conn)
jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)
#Score data
jsonSimscore.update({'Score': scoring.score_test(data, meta)} )
jsonSimscore = vm.nan_replace(jsonSimscore)

#Processing is completed --Add this jsonSimscore to new SQS stack for POST
jsonSimscore = vm.round_dict(jsonSimscore,3)

# <codecell>


