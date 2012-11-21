# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=4>

# Determine metadata, validity metrics, HMM score and add to Simscore queue

# <codecell>

from computing_imports import *
import fetch.shapeS3 as shape
import fetch.fetchS3 as fetchS3
import report.tools.validate as validate
import validity_metrics as vm
%load_ext autoreload
%autoreload
from boto.sqs.message import Message
conn = boto.connect_sqs(
        aws_access_key_id='AKIAJFD5VPO6RFKGTWIA',
        aws_secret_access_key='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')
import pprint
pp = pprint.PrettyPrinter(indent=4)

# <codecell>

get_sqs_filename(message)

# <codecell>

def get_sqs_filename(message):
    '''given a decoded sqs message from SNS, return the Edge filename'''
    
    sqsmessage = json.loads(rs.get_body())["Message"]
    temp = sqsmessage.split('.')
    temp[-1] = 'txt'
    return str('.'.join(temp))

# <codecell>

#Define SQS connection:
q = conn.get_queue('EdgeFiles2Process')
endq = conn.get_queue('Files2Ship')
q.set_message_class(boto.sqs.message.RawMessage)

#Load in codebooks, hmms:

#Run Eternally
#while True:
    
#Get a file off the SQS stack using 20sec long poll
rs = q.read(wait_time_seconds=20)

#if there's a file in the queue,
if rs:
    
    try:
        #Pull filename from S3
        bucketname = 'incoming-simscore-org'
        filename = get_sqs_filename(rs)#'edge6/2012/11/05.18.46.23.340.0.txt'
        data, meta = shape.getData(filename, bucketname, is_secure=True)
        #print meta
        
        #Compute Summary Metrics
        jsonSimscore = vm.summary_metrics(meta,data,np.diff)
        
        #Compute additional data validity metrics
        jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
        
        #Compute machine health metrics
        jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)
        
        #Given which hand and task it is,
            #Score against HMMs in memory
            #Append score to jsonSimscore
        
        #Processing is completed --Add this jsonSimscore to new SQS stack for POST
        m = Message()
        m.set_body(json.dumps(jsonSimscore))
        receipt = endq.write(m)
        
        #If json is DEFINITELY received by new SQS, delete from original Files2Process queue
        #if receipt:
            #d = q.delete_message(rs)
            #if d: print 'Deleted %s from queue' %filename
            
    except:
        raise
        #print/log exception, then continue
        #delete file from queue?
        #Notify me of certain types of exception? Bad filenames? Unable to compute score? etc?
        
#if file is not there or in the Ship SQS,
    #Once per day, compare list of S3 files to simpledb list of processed files.
    #if S3 contains file not on processing list, add to queue NOW.
    #simpledb contains filename, boolean "computed", boolean "shipped"
      
print 'done'

# <codecell>


# <headingcell level=1>

# Scratch

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

#print pp.pprint(jsonSimscore)

# <codecell>

json.dumps(jsonSimscore)

# <codecell>


