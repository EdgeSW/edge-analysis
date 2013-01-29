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
from fetch.configuration import isClipTask   
import report.validate as validate
conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')

# <codecell>

filename = 'edge6/2013/01/09.23.55.20.368.3.txt'
data, meta = myS3.getData(bucket, filename, labeled=True)
if data == None: raise ValueError, "Data file is empty!"

# <codecell>

'''Where the magic happens'''
#Compute Summary Metrics
jsonSimscore = vm.summary_metrics(meta, data, conn)
jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)

print jsonSimscore['IgnoreErrors']

# <codecell>

print jsonSimscore["IsPractice"]

# <codecell>


