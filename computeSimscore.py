# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=4>

# Determine metadata, validity metrics, HMM score and add to Simscore queue

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
import boto, time, json, pprint
from datetime import datetime
import numpy as np

import scoring
import fetch.shapeS3 as shape
import fetch.mySQS as mySQS
import validity_metrics as vm
from aws import aws_ak, aws_sk
from boto.sqs.message import Message

# <codecell>

def send_fail(failure, conn): 
    conn.send_email(source='thartley@simulab.com',
        subject='computeSimscore.py Errors', format='html',
        body=failure, to_addresses=['thartley@simulab.com'])
    
def logit(log, message):
    log.write(message)
    log.flush()
    
def add_file_sdb(domain, meta):
    attrs = {'IsProcessed':True, 'IsSent':False, 'UploadDateUnix':meta['UploadDateUnix'], 'UploadDate':meta['UploadDate'],'Score':meta['Score'], 
            'FailTypes':meta['FailTypes'], 'IsPractice':meta['IsPractice'], 'UserID':meta['UserID']}
    return domain.put_attributes(meta['TestID'],attrs)

    
#add if __name__ == '__main__':

# <codecell>

# Open up log file to write pycurl info to
log = open (os.getcwd()+'\\ComputeFails.log', 'a')
logit(log,'{0}\n{1}\n{2}\n{0}\n'.format('*'*26,datetime.now(),'Booting up computeSimscore.py'))

'''Define Connections'''
#Connect to sqs
sqs_conn = boto.connect_sqs(aws_ak, aws_sk)
q = sqs_conn.get_queue('EdgeFiles2Process')
q.set_message_class(boto.sqs.message.RawMessage)
shipq = sqs_conn.get_queue('Files2Ship')
#Connect to ses
ses_conn = boto.connect_ses(aws_ak, aws_sk)
#Connect to SimpleDB
sdb_conn = boto.connect_sdb(aws_ak, aws_sk)
sdb_domain = sdb_conn.get_domain('ProcessedEdgeFiles')

#Load in codebooks, hmms:

# <codecell>

'''Run Eternally'''
#while True:  

#Get a file off the SQS stack using 20sec long poll
rs = q.read(wait_time_seconds=20)

#if there's a file in the queue,
if rs:
    '''Compute all metrics'''
    try:
        #Pull filename from S3
        filename = mySQS.get_sqs_filename(rs) #'edge6/2012/11/05.18.46.23.340.0.txt'
        data, meta = shape.getData(filename, bucketname='incoming-simscore-org', is_secure=True)
        logit(log,'{0}\n{1}\nProcessing {2}\n'.format('-'*20,datetime.now(),filename) )
        
        '''Where the magic happens'''
        #Compute Summary Metrics
        jsonSimscore = vm.summary_metrics(meta,data)
        #Compute additional data validity metrics
        jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
        #Compute machine health metrics
        jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)
        #Score data
        jsonSimscore.update({'Score': scoring.score_test(data)} )
        
        #Processing is completed --Add this jsonSimscore to new SQS stack for POST
        jsonSimscore = vm.round_dict(jsonSimscore,3)
        logit(log,'Successfully processed.\n'); print 'Successfully processed.'
        
    except Exception as err:
        #print/log exception, email me, then continue
        logit(log,'ERROR: %s\n'%str(err) )
        if filename == None: filename = 'Unknown'
        send_fail('Error computing {0}. computeSimscore.py error: {1}.'.format(filename, err), ses_conn)
        #continue
        
    '''Add to queue for shipSimscore'''
    try:
        m = Message()
        m.set_body(json.dumps(jsonSimscore))
        receipt = shipq.write(m)
            
        #If json is DEFINITELY received by new SQS, delete from original Files2Process queue
        assert receipt, "Could not write to queue"
        d = q.delete_message(rs)
        
        assert d, "Could not delete from queue"
        logit(log, 'Deleted from queue\n'); print 'Deleted %s from queue' %filename
                    
        #Add entry to SimpleDB
        s = add_file_sdb(sdb_domain, jsonSimscore)
        assert s, "SimpleDB not updated"
        
    except Exception as err:
        logit(log, 'ERROR: %s\n'%str(err) )
        send_fail('Error sending {0}. computeSimscore.py error: {1}.'.format(filename, err), ses_conn)    
          
print 'done'

# <headingcell level=1>

# Scratch

# <codecell>

#Add some fake SNS messages to the queue
sns_conn = boto.connect_sns(aws_ak, aws_sk)
for i in range(5):
    sns_conn.publish('arn:aws:sns:us-east-1:409355352037:test','edge6/2012/11/05.19.16.31.340.3.txt',subject='EdgeData')

# <codecell>

'''
bucketname = 'incoming-simscore-org'
filename = 'edge6/2012/11/05.19.16.31.340.3.txt'
#data, meta = shape.getData(filename, bucketname, is_secure=True)
#Compute Summary Metrics
jsonSimscore = vm.summary_metrics(meta,data)
#Compute additional data validity metrics
jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
#Compute machine health metrics
jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)
jsonSimscore = vm.round_dict(jsonSimscore,3)

#pp = pprint.PrettyPrinter(indent=4)
#print pp.pprint(jsonSimscore)
'''

# <codecell>


