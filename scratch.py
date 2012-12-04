# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')

import boto
import json
import pycurl
import validity_metrics as vm
import report.simscore as sim
from fetch.mySQS import sqs_connection as conn
import fetch.shapeS3 as shape

# <codecell>

c = pycurl.Curl() 
%load_ext autoreload
%autoreload
compute = 'http://dev.simscore.md3productions.com/simscores-v1/machinereport'
#login = 'http://simscore.org/simscores-v1/user/login'
login = 'http://dev.simscore.md3productions.com/simscores-v1/user/login'



%load_ext autoreload
if sim.is_expired_cookie(c):
    c, buf = sim.loginSimscore(c, address=login)
    print c.getinfo(pycurl.HTTP_CODE)
    print buf.getvalue()

# <codecell>

bucketname = 'incoming-simscore-org'
filename = 'edge6/2012/11/05.19.16.31.340.3.txt'
data, meta = shape.getData(filename, bucketname, is_secure=True)
#Compute Summary Metrics
jsonSimscore = vm.summary_metrics(meta,data)
#Compute additional data validity metrics
jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
#Compute machine health metrics
jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)
jsonSimscore = vm.round_dict(jsonSimscore,3)
print 'jsonSimscore computed!'

# <codecell>

compute = 'http://dev.simscore.md3productions.com/simscores-v1/machinereport' 
pp = sim.RESTfields(address=compute, header=['Content-Type: application/json'], values=json.dumps(jsonSimscore))
c, out = pp.posthttp(c)
print c.getinfo(c.HTTP_CODE)
print out.getvalue()

# <codecell>

(c.HTTP_CODE)

# <codecell>

import time 
logout='http://dev.simscore.md3productions.com/simscores-v1/user/logout'
c = sim.logoutSimscore(c, address=logout)
print c.getinfo(pycurl.HTTP_CODE)


#print buf.getvalue()

# <codecell>

json.dumps({'username': 'grading', 'password': 'r*tFQqmb'})

# <headingcell level=1>

# SQS 

# <codecell>

q = conn.get_queue('EdgeFiles2Process')
q.set_message_class(boto.sqs.message.RawMessage)
rs = q.read()
print rs.get_body()

# <codecell>

bucketname = 'incoming-simscore-org'
filename = 'edge6/2012/11/05.19.16.31.340.3.txt'
data, meta = shape.getData(filename, bucketname, is_secure=True)
#Compute Summary Metrics
jsonSimscore = vm.summary_metrics(meta,data)
#Compute additional data validity metrics
jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
#Compute machine health metrics
jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)
jsonSimscore = vm.round_dict(jsonSimscore,3)
print 'jsonSimscore computed!'

# <codecell>

qq = conn.get_queue('Files2Ship')
from boto.sqs.message import Message

for i in range(1, 11):
   m = Message()
   m.set_body(json.dumps(jsonSimscore))
   qq.write(m)


# <codecell>


