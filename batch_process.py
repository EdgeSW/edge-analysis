# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, os
#sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
import boto, time, json, pprint
from datetime import datetime, timedelta
import numpy as np

import scoring
import fetch.myS3 as myS3
import fetch.mySQS as mySQS
import validity_metrics as vm
from aws import aws_ak, aws_sk
from boto.sqs.message import Message

# <codecell>

'''Define Connections'''
sqs_conn = boto.connect_sqs(aws_ak, aws_sk)
q = sqs_conn.get_queue('Files2Ship')
comq = sqs_conn.get_queue('EdgeFiles2Process')
#Connect to ses
ses_conn = boto.connect_ses(aws_ak, aws_sk)
#Connect to SimpleDB
sdb_conn = boto.connect_sdb(aws_ak, aws_sk)
sdb_domain = sdb_conn.get_domain('ProcessedEdgeFiles')

# <codecell>

print mySQS.approx_total_messages(comq)
if mySQS.approx_total_messages(comq)==0:
    
    print 'processing'
    conn = boto.connect_s3(aws_ak, aws_sk)
    bucket = conn.get_bucket('incoming-simscore-org')
    theforgotten = myS3.getLeftBehind(daysback=5, conn=conn, sdb_domain=sdb_domain)
    print theforgotten
    
    if len(theforgotten) > 0:
        mySQS.append_list_to_queue(theforgotten, comq)

# <codecell>

if mySQS.approx_total_messages(comq)==0:
    print 'processing'
    conn = boto.connect_s3(aws_ak, aws_sk)
    bucket = conn.get_bucket('incoming-simscore-org')
    
    t0 = datetime.now()-timedelta(days=30)
    #filelist = myS3.getFilesBetween(mindate=t0, maxdate=datetime.now(), bucket=bucket, onlyTxtFiles=True)
    filelist =  ['edge3/2012/12/05.15.43.58.109.3.txt']
    print filelist
    
    if len(filelist) > 0:
        mySQS.append_list_to_queue(filelist, comq)
     

# <codecell>

comq.clear()

# <codecell>




