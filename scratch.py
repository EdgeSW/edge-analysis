# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import boto
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
import fetch.myS3 as myS3
from aws import aws_ak, aws_sk
from datetime import datetime
import json
import cStringIO


bucketname='incoming-simscore-org'
minfilename = 'edge6/2012/12/05.21.59.05.325.0.txt'
mindate = myS3.getFileDateFromKey(minfilename)
maxdate = datetime.now()

conn = boto.connect_s3(aws_ak, aws_sk)
bucket = conn.get_bucket(bucketname)
        
start = datetime.now()


meta = myS3.getMetaDataBetween(mindate, maxdate, bucket)

# <codecell>

v = meta[meta.keys()[0]]
print type(v['IsPracticeTest'])
isPractice = lambda v: v['IsPracticeTest']

end = datetime.now()-start
print end

# <codecell>

#Add some fake SNS messages to the queue
sns_conn = boto.connect_sns(aws_ak, aws_sk)
for i in range(5):
    sns_conn.publish('arn:aws:sns:us-east-1:409355352037:test','edge6/2012/11/05.19.16.31.340.3.txt',subject='EdgeData')

# <headingcell level=1>

# SQS 

# <codecell>

c = pycurl.Curl() 
%load_ext autoreload
%autoreload
compute = 'http://dev.simscore.md3productions.com/simscores-v1/machinereport'
#login = 'http://simscore.org/simscores-v1/user/login'
login = 'http://dev.simscore.md3productions.com/simscores-v1/user/login'
logout='http://dev.simscore.md3productions.com/simscores-v1/user/logout'

# <codecell>

conn = boto.connect_sqs(
        aws_access_key_id=aws_ak,
        aws_secret_access_key=aws_sk)

q = conn.get_queue('EdgeFiles2Process')
q.set_message_class(boto.sqs.message.RawMessage)
rs = q.read()
#print rs.get_body()

# <codecell>

conn = boto.connect_sqs(aws_access_key_id=aws_ak, aws_secret_access_key=aws_sk)
q = conn.get_queue('Files2Ship')
q.get_attributes()

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

i='s'
assert type(i) is int, "i is not an integer: %r" % i

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


