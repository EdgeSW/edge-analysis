# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\edge-analysis')

import boto, time, json, pprint
from datetime import datetime, timedelta
import numpy as np

import helpers
import fetch.myS3 as myS3
import fetch.mySQS as mySQS
import Simscore.validity_metrics as vm
from fetch.aws import aws_ak, aws_sk
from Simscore.report.configuration import isClipTask   
import Simscore.report.validate as validate
conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')

# <codecell>

unit_files = [#Name, Dead, OOR, NaN
(	"edge6/2013/01/31.00.42.06.392.3.txt"	,	[]	,	[]	,	[]	),
(	"edge10/2013/01/22.18.09.46.209.0.txt"	,	[]	,	[]	,	[]	),
(	"edge10/2013/01/26.16.02.02.365.0.txt"	,	[]	,	[]	,	[]	),
(	"edge3/2013/01/18.18.54.37.336.1.txt"	,	[]	,	[]	,	[]	),
(	"edge6/2013/01/31.00.50.47.392.2.txt"	,	[]	,	[]	,	[]	),
(	"edge10/2013/01/24.17.05.48.389.2.txt"	,	[]	,	[]	,	[]	),
(	"edge10/2013/01/10.15.22.12.389.2.txt"	,	[]	,	[]	,	[]	),
(	"edge6/2013/01/31.00.46.29.392.2.txt"	,	[]	,	[]	,	[]	),
																
(	"edge7/2012/12/07.15.37.27.109.2.txt"	,	[]	,	["ThG_L", "Fg_L", "ThG_R"]	,	[]	),
(	"edge9/2012/11/29.01.24.15.251.1.txt"	,	[]	,	["Fg_L", "Fg_R"]	,	[]	),
(	"edge9/2012/11/29.01.22.22.251.3.txt"	,	[]	,	["Fg_L", "Lin_R"]	,	[]	),
																
(	"edge8/2012/12/06.18.40.18.109.1.txt"	,	["Fg_L"]	,	[]	,	[]	),
(	"edge8/2012/12/06.18.39.40.109.1.txt"	,	["Fg_L"]	,	[]	,	[]	),								
																
(	"edge6/2012/11/05.18.59.45.340.1.txt"	,	[]	,	["Fg_L"]	,	["Fg_R"]	),
(	"edge6/2012/11/05.18.46.23.340.0.txt"	,	[]	,	["Fg_L"]	,	["Fg_R"]	),																
								
(	"edge6/2012/11/05.19.24.12.340.2.txt"	,	["Fg_L", "Rot_L"]	,	["Fg_L", "ThG_L"]	,	[]	),
(	"edge1/2012/10/08.15.22.48.323.1.txt"	,	["Fg_L"]	,	["Fg_L"]	,	[]	),
(	"edge6/2013/01/25.21.33.58.393.0.txt"	,	["Rot_L," "ThG_L"]	,	["ThG_L"]	,	[]	),
(	"edge2/2013/01/09.16.06.18.378.3.txt"	,	["Fg_R"]	,	["Rot_L"]	,	[]	),
(	"edge2/2012/12/03.20.12.46.109.3.txt"	,	["Fg_R"]	,	["Lin_R"]	,	[]	),
(	"edge6/2013/01/25.22.30.14.312.0.txt"	,	["Fg_R", "ThG_R", "Rot_R"]	,	["ThG_R"]	,	[]	)

]

# <codecell>

new_deads = []
for test in unit_files:
    try:
        data, meta = myS3.getData(bucket, test[0], labeled=True)
        minmax = validate.findMinMax(data)
        
        new_dead = validate.findDeadSensors(data, minmax, meta['TaskId'], meta['IsPracticeTest'])
        old_dead = validate.oldFindDeadSensor(validate.findMinMax(data), isClipTask(test[0]))
        #oors = validate.findOutOfRange(minmax)
        
        print 'verifying',test[0]
        print 'Dead sensors should be:', test[1]
        print 'New method caught:', new_dead
        print 'Old method caught:', old_dead
        print 
    except Exception as e:
        print e
        print 'error in',fn

# <codecell>

'''
import time
for filename in biglist:
    try:
        data, meta = myS3.getData(bucket, filename, labeled=True)
        minmax = validate.findMinMax(data)
        
        new_dead = findDeadSensors(data, minmax, meta['TaskId'], meta['IsPracticeTest'])
        old_dead = validate.findDeadSensor(validate.findMinMax(data), isClipTask(filename))
        
        if filename[-5:]=='2.txt':
            print filename,old_dead, new_dead
        time.sleep(0.1)
    except Exception as e:
        print e
        print filename
'''

# <codecell>

biglist = myS3.getFilesBetween(datetime.utcnow()-timedelta(days=160), datetime.utcnow(), bucket, True)
print len(biglist)

# <codecell>

def lists_contain_same(lis1, lis2):
    if lis1 == lis2:
        return True
    if len(lis1)!=len(lis2):
        return False
    for item in lis1:
        if item not in lis2:
            return False
    for item in lis2:
        if item not in lis1:
            return False
    return True

# <codecell>

import time

filestoredo = []

for filename in biglist:
    try:
        data, meta = myS3.getData(bucket, filename, labeled=True)
        minmax = validate.findMinMax(data)
        
        old_oors = validate.oldFindOutOfRange(minmax)
        old_deads = validate.oldFindDeadSensor(minmax, isClipTask(filename))
        js = vm.summary_metrics(meta, data, conn)
        js = vm.data_metrics_append(js, data, filename)
        new_oors = js['OutOfRange']
        new_deads = js['DeadSensors']
        ignore = js['IgnoreErrors']
        
        _oors = []
        _deads = []
        for oor in new_oors:
            if oor not in old_oors and 'OutOfRange' not in ignore.get(oor, []):
                _oors.append(oor)
                if filename not in filestoredo: filestoredo.append(filename)
        for dead in new_deads:
            if dead not in old_deads and 'DeadSensors' not in ignore.get(dead, []):
                _deads.append(dead)
                if filename not in filestoredo: filestoredo.append(filename)
                    
        if js['TaskType'] == 1: filestoredo.append(filename)
            
        if _oors or _deads: print filename, _oors, _deads
        time.sleep(0.1)
    except Exception as e:
        print e, filename
        
print filestoredo

# <codecell>

len(filestoredo)

# <codecell>

import fetch.mySQS as mySQS

# <codecell>

from aws import aws_ak, aws_sk
from boto.sqs.message import Message
'''Define Connections'''
sqs_conn = boto.connect_sqs(aws_ak, aws_sk)
q = sqs_conn.get_queue('Files2Ship')
comq = sqs_conn.get_queue('EdgeFiles2Process')
#Connect to ses
ses_conn = boto.connect_ses(aws_ak, aws_sk)
#Connect to SimpleDB
sdb_conn = boto.connect_sdb(aws_ak, aws_sk)
sdb_domain = sdb_conn.get_domain('ProcessedEdgeFiles')

mySQS.append_list_to_queue(filestoredo, comq)

# <codecell>


