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


conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')
filename = 'edge0/2013/01/10.06.22.05.109.0.txt'
data, meta = myS3.getData(bucket, filename, labeled=True)


jsonSimscore = vm.summary_metrics(meta, data, conn)
jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)

# <codecell>

print jsonSimscore['IgnoreErrors']
print jsonSimscore['NaNSensors']
# <codecell>


