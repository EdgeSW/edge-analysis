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

# <codecell>

conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket('incoming-simscore-org')
allfiles = myS3.getFilesBetween(mindate=datetime.now()-timedelta(days=170), maxdate=datetime.now()-timedelta(days=79), bucket=bucket, onlyTxtFiles=True)

# <codecell>

userfiles = []
for f in allfiles:
    edge = f.split('/')[0][4:]
    if f.split('.')[-3] != '109' and edge not in ['0','11','12']:
        userfiles.append(f)
        
ffs = myS3.getTestFiles(userfiles, bucket) 

# <codecell>

print ffs

# <codecell>

report = {}
tasks = ['PegTx','Cutting','Suturing','ClipApply']
%load_ext autoreload
%autoreload

for f in ffs:
    print f
    uid = f.split('.')[-3]
    task = int(f.split('.')[-2])
    if not report.get(uid, False): report[uid] = {'Summary':[0,0,0,0], tasks[0]:[], tasks[1]:[], tasks[2]:[], tasks[3]:[]}
    
    data, meta = myS3.getData(bucket, f, labeled=True)
    #Compute Summary Metrics
    jsonSimscore = vm.summary_metrics(meta, data, conn)
    jsonSimscore = vm.data_metrics_append(jsonSimscore, data, f)
    jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)
    failtypes = jsonSimscore['FailTypes']
    
    report[uid]['Summary'][task] += 1
    report[uid][tasks[task]].append([f, failtypes])
        

# <codecell>

import scoring
report = scoring.load_pickle('user_report.txt')

# <codecell>

import pprint
pprint.pprint(report)

# <codecell>

%load_ext autoreload
%autoreload

import openpyxl, json
from openpyxl.workbook import Workbook
from openpyxl.writer.excel import ExcelWriter

from openpyxl.cell import get_column_letter

wb = Workbook()
dest_filename = r'User_Report.xlsx'
ws = wb.worksheets[0]
ws.title = "User Report"

tasks = ['PegTx','Cutting','Suturing','ClipApply']
i = 1
url = 'http://simscore.org/browse_simscore/show?bucket=incoming-simscore-org&path=/'
for u in report:
    ws.append([int(u), 'Tasks','Files','FailTypes','Links','Check'])
    for task in tasks:
        if report[u][task]: 
            for test in report[u][task]:
                ws.append(['', task, test[0], json.dumps(test[1]), url+test[0]])
        else:
            ws.append(['', task])
            
    ws.append(['', 'Tests:', json.dumps(report[u]['Summary']) ])
    ws.append(['', 'Needs:'])
    ws.append(['', 'Redo:'])
    ws.append(['', 'SUMMARY:'])
    ws.append([''])
    



wb.save(filename = dest_filename)

# <codecell>

for k in report.keys():
    filename = report[k]['Suturing'][0][0]
    
    print filename.split('/')[1]+'/'+filename.split('/')[2]+'/'+filename.split('/')[3].split('.')[0]

# <codecell>

for col_idx in xrange(1, 40):
    col = get_column_letter(col_idx)
    for row in xrange(1, 600):
        ws.cell('%s%s'%(col, row)).value = '%s%s' % (col, row)

