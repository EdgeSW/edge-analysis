# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
import boto, time, json, pprint
from datetime import datetime, timedelta
import numpy as np

import fetch.myS3 as myS3
import fetch.mySQS as mySQS
import validity_metrics as vm
from aws import aws_ak, aws_sk
from report.configuration import isClipTask   
import report.validate as validate
conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')

# <codecell>

filename = 'edge6/2013/01/09.23.55.20.368.3.txt'
data, meta = myS3.getData(bucket, filename, labeled=True)
if data == None: raise ValueError, "Data file is empty!"

# <codecell>

ll = ['edge6/2013/01/31.00.20.26.392.0.txt','edge6/2013/01/30.22.50.23.312.0.txt','edge6/2013/01/17.19.06.05.313.0.txt',
 'edge6/2013/01/18.20.25.12.340.0.txt','edge10/2013/01/26.16.02.02.365.0.txt','edge3/2013/01/18.18.42.22.336.0.txt','edge2/2013/01/09.17.05.15.382.0.txt']

data = myS3.getDataFromTxtFileList(bucket, ll, labeled=True)

# <codecell>

for k, v in data.iteritems():
    print k
    mil = np.min(v['data']['ThG_L'])
    mal = np.max(v['data']['ThG_L'])
    mir = np.min(v['data']['ThG_R'])
    mar = np.max(v['data']['ThG_R'])
    
    print 'right:','(',mar,',',mir,')', mar - mir
    print 'left:','(',mal,',',mil,')', mal - mil
    print 

# <codecell>

'''Where the magic happens'''
#Compute Summary Metrics
jsonSimscore = vm.summary_metrics(meta, data, conn)
jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)

print jsonSimscore['IgnoreErrors']

