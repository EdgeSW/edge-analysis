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

biglist = myS3.getFilesBetween(datetime.utcnow()-timedelta(days=30), datetime.utcnow(), bucket, True)

# <codecell>

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

# <rawcell>

# Completely ignore ThG dead for filters more complex than max-min? edge10/2013/01/10.13.45.59.369.1.txt
# How to address suturing task where put down right tool to cut and they just really suck at it?
#     Perhaps ignore last 60sec of suturing task?
# 
# 
# edge10/2013/01/10.13.45.59.369.1.txt ['ThG_L']
# edge10/2013/01/10.15.22.12.389.2.txt ['J1_R', 'J2_R', 'Lin_R', 'Rot_R', 'X_R', 'Y_R', 'Z_R']
# edge10/2013/01/10.16.15.28.386.1.txt ['Fg_L']
# edge10/2013/01/10.16.33.59.386.3.txt ['Fg_L', 'Fg_R']
# edge10/2013/01/14.17.37.01.356.1.txt ['Fg_L']
# edge10/2013/01/17.12.36.57.286.0.txt ['Fg_L']
# edge10/2013/01/22.18.16.44.209.1.txt ['Fg_L']
# edge10/2013/01/22.18.38.26.209.2.txt ['Fg_L']
# edge10/2013/01/24.17.05.48.389.2.txt ['J1_R', 'J2_R', 'Lin_R', 'Rot_R', 'X_R', 'Y_R', 'Z_R']
# edge2/2013/01/09.17.29.40.382.2.txt ['J1_R', 'J2_R', 'Lin_R', 'Rot_R', 'X_R', 'Y_R', 'Z_R']
# edge6/2013/01/16.22.17.15.346.1.txt ['Fg_L']
# edge6/2013/01/17.18.47.05.313.1.txt ['Fg_L']
# edge6/2013/01/18.20.43.17.340.3.txt ['Fg_L']
# edge6/2013/01/18.21.25.44.307.1.txt ['Fg_L']
# edge6/2013/01/25.21.43.21.393.0.txt ['Rot_L']
# edge6/2013/01/31.00.30.19.392.1.txt ['Fg_L']
# edge6/2013/01/31.00.57.07.392.1.txt ['Fg_L']
# edge7/2013/01/07.16.11.12.370.0.txt ['Fg_R']
# edge7/2013/01/07.16.39.49.370.3.txt ['Fg_L']
# 'NoneType' object has no attribute 'dtype'
# error in edge7/2013/01/07.16.59.48.370.2.txt
# 
# WITH 1 AS THRESH FOR FG:
# 1 false positive, 2 would be ignored (pretty good for 1 month!)
# 3 need to be fixed
# edge10/2013/01/10.13.45.59.369.1.txt ['ThG_L']
# edge10/2013/01/10.15.22.12.389.2.txt ['J1_R', 'J2_R', 'Lin_R', 'Rot_R', 'X_R', 'Y_R', 'Z_R']
# edge10/2013/01/10.16.33.59.386.3.txt ['Fg_L']
# edge10/2013/01/14.17.37.01.356.1.txt ['Fg_L']
# edge10/2013/01/24.17.05.48.389.2.txt ['J1_R', 'J2_R', 'Lin_R', 'Rot_R', 'X_R', 'Y_R', 'Z_R']
# edge2/2013/01/09.17.29.40.382.2.txt ['J1_R', 'J2_R', 'Lin_R', 'Rot_R', 'X_R', 'Y_R', 'Z_R']
# edge6/2013/01/25.21.43.21.393.0.txt ['Rot_L'] (real)

