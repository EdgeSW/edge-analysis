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
import fetch.shapeS3 as shape
from aws import aws_ak, aws_sk

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

conn = boto.connect_sqs(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key)

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


# <headingcell level=2>

# SDB

# <codecell>

import sys, os, boto
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
from aws import aws_access_key, aws_secret_key

conn = boto.connect_sdb(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key)

# <codecell>

domain = conn.get_domain('ProcessedEdgeFiles')

item = domain.new_item('edge12/2013/10/14.17.08.01.109.2')
item['IsProcessed'] = True
item['IsSent'] = False
item['UploadDate'] = '2012/11/14.17.08.01'
item['Score'] = 1
item['UserID'] = 192
item.save()

# <codecell>

domain.put_attributes('edge12/2013/10/14.17.08.01.109.2',{'Score':'55'},replace=False)

# <codecell>

data = domain.get_item('edge12/2013/11/14.17.08.01.109.2')

# <codecell>

dom_name = 'ProcessedEdgeFiles'
#syntax: select * from `ProcessedEdgeFiles` where Score>'2' 
#alt syntax: select * from `ProcessedEdgeFiles` where IsSent='True' and IsProcessed='True'
query = "select {0} from `{1}` where {2}".format('*', dom_name, "IsSent='True' ")
print query
rs = domain.select(query)
for item in rs:
    print item.name, item

# <codecell>


