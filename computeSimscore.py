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
import fetch.myS3 as myS3
import fetch.mySQS as mySQS
import validity_metrics as vm
from aws import aws_ak, aws_sk
from boto.sqs.message import Message

# <codecell>

'''Define Connections'''
#connect to S3
conn = boto.connect_s3(aws_ak, aws_sk)
bucket_normal = conn.get_bucket('incoming-simscore-org')
bucket_test = conn.get_bucket('incoming-simscore-org-test')
#Connect to sqs
sqs_conn = boto.connect_sqs(aws_ak, aws_sk)
q = sqs_conn.get_queue('EdgeFiles2Process')
q.set_message_class(boto.sqs.message.RawMessage)
shipq = sqs_conn.get_queue('Files2Ship')

#Connect to SimpleDB
sdb_conn = boto.connect_sdb(aws_ak, aws_sk)
sdb_domain = sdb_conn.get_domain('ProcessedEdgeFiles')

#Load in codebooks, hmms:

# <codecell>

def send_fail(failure, conn): 
    conn.send_email(source='python@tylerhartley.com',
        subject='computeSimscore.py Errors', format='html',
        body=failure, to_addresses=['thartley@simulab.com'])
    
def logit(log, message):
    log.write(message)
    log.flush()
    
def add_file_sdb(domain, meta):
    attrs = {'IsProcessed':True, 'IsSent':False, 'UploadDateUnix':meta['UploadDateUnix'], 'UploadDate':meta['UploadDate']
            ,'Score':meta['Score'], 'FailTypes':json.dumps(meta['FailTypes'])
            , 'IsPractice':meta['IsPractice'], 'UserID':meta['UserID'], 'RToolID': meta['RToolID'] , 'LToolID': meta['LToolID']}
    return domain.put_attributes(meta['TestID'],attrs)

def whichBucket(bucketname):
    if bucketname == 'incoming-simscore-org':
        return bucket_normal
    elif 'test' in bucketname:
        return bucket_test
    else:
        return conn.get_bucket(bucketname)

# <codecell>

def main():  
    
    #Get a file off the SQS stack using 20sec long poll
    rs = q.read(wait_time_seconds=20)
    
    #if there's a file in the queue,
    if rs:
        '''Compute all metrics and send'''
        try:
            #Pull filename from S3
            filename = mySQS.get_sqs_filename(rs) #'edge6/2012/11/05.18.46.23.340.0.txt'
            bucketname = mySQS.get_sqs_bucket(rs)
            logit(log,'{0}\n{1}\nProcessing {2}\nfrom bucket {3}\n'.format('-'*20,datetime.now(),filename, bucketname) )
            
            #Ensure this isn't a Reference block trace
            if 'Trace' in filename: 
                logit(log,'Is a reference block trace.\n'); 
                d = q.delete_message(rs)
                logit(log, 'Deleted from queue\n'); print 'Deleted %s from queue' %filename
                return rs
                
            #If everything looks good, load the dataaa!
            #TODO - implement bucket load from test without re-connecting every damn time
            
            data, meta = myS3.getData(whichBucket(bucketname), filename, labeled=True)
            if data == None: raise ValueError, "Data file is empty!"
            
            '''Where the magic happens'''
            #Compute Summary Metrics
            jsonSimscore = vm.summary_metrics(meta, data, conn)
            jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)
            jsonSimscore = vm.machine_health_append(jsonSimscore, meta, data)
            #Score data
            jsonSimscore.update({'Score': 'None'}) #scoring.score_test(data, meta)} )
            
            #Processing is completed --Add this jsonSimscore to new SQS stack for POST
            jsonSimscore = vm.round_dict(jsonSimscore,3)
            jsonSimscore = vm.nan_replace(jsonSimscore)
            logit(log,'Successfully processed.\n'); print 'Successfully processed.'
            
            
            '''Add to queue for shipSimscore'''
            receipt = mySQS.append_to_queue(jsonSimscore, shipq, raw=False)
            assert receipt, "Could not write to queue"    
            #If json is DEFINITELY received by new SQS, delete from original Files2Process queue
            d = q.delete_message(rs)
            
            assert d, "Could not delete from queue"
            logit(log, 'Deleted from queue\n'); print 'Deleted %s from queue' %filename
                        
            s = add_file_sdb(sdb_domain, jsonSimscore)
            assert s, "SimpleDB not updated"
            logit(log, "Updated SimpleDB\n")
            
        except Exception as err:

            #make more invisible, print/log exception, email me, then continue
            rs.change_visibility(5*60)
            if filename == None: filename = 'Unknown'
            logit(log,'ERROR: %s - %s\n'%(filename, str(err)) )
            #Connect to ses
            ses_conn = boto.connect_ses(aws_ak, aws_sk)
            send_fail('Error computing {0}. computeSimscore.py error: {1}.'.format(filename, err), ses_conn)
            
            #TODO handle incoming-simscore-org-test bucket requests in better way
            if err.message in ["File not found on S3","Data file is empty!"]:
                d = q.delete_message(rs)
                logit(log, 'Deleted from queue\n'); print 'Deleted %s from queue' %filename
    return rs

# <codecell>

if __name__ == "__main__":
    # Open up log file to write pycurl info to
    #log = open (os.getcwd()+'\\ComputeFails.log', 'a')
    log = open ('/home/ubuntu/logs/ComputeFails.log', 'a')
    logit(log,'{0}\n{1}\n{2}\n'.format('*'*26,datetime.now(),'Booting up computeSimscore.py'))
    
    '''Run Eternally'''
    rs = True
    #while rs: #replace with while True to run eternally
    while True:
        rs = main()
        

