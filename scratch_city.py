# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, os
#sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
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

filename = 'edge5/2012/12/18.15.52.28.366.0.txt'
conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')
data, meta = myS3.getData(bucket, filename, labeled=True)

# <codecell>


# <codecell>

import report.validate as validate
from fetch.configuration import isClipTask
minmax = validate.findMinMax(data)
validate.findNans(data, isClipTask(filename))

# <codecell>

edge5/2012/12/18.15.52.28.366.0

