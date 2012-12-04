# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=4>

# POST computed files to Simscore

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')

import boto
import json, time
from datetime import datetime
import pycurl
import validity_metrics as vm
import report.simscore as sim
from aws import aws_ak, aws_sk

from boto.sqs.message import Message

def send_fail(failure, conn): 
    conn.send_email(source='thartley@simulab.com',
        subject='shipSimscore.py Errors', format='html',
        body=failure,
        to_addresses=['thartley@simulab.com'])
    
def logit(log, message):
    log.write(message)
    log.flush()

def trysleeptimes(trys):
    global sleeptimes=[0, 1, 10, 100, 200, 1000]
    
    if trys < len(sleeptimes):
        time.sleep(sleeptimes[trys])
    else:
        time.sleep(sleeptimes[-1])

# <codecell>

# Open up log file to write pycurl info to
log = open (os.getcwd()+'\\ShipFails.log', 'a')
logit(log, '{0}\n{1}\n{2}\n{0}\n'.format('*'*26,datetime.now(),'Booting up shipSimscore.py'))

# Login to Simscore
login = 'http://dev.simscore.md3productions.com/simscores-v1/user/login'
c, buf = sim.loginSimscore(address=login)
logit(log, 'Login response: '+str(c.getinfo(c.HTTP_CODE))+'\n'+buf.getvalue()+'\n')


'''Define Connections'''
sqs_conn = boto.connect_sqs(aws_ak, aws_sk)
q = sqs_conn.get_queue('Files2Ship')
comq = sqs_conn.get_queue('EdgeFiles2Process')
#Connect to ses
ses_conn = boto.connect_ses(aws_ak, aws_sk)
#Connect to SimpleDB
sdb_conn = boto.connect_sdb(aws_ak, aws_sk)
sdb_domain = sbd_conn.get_domain('ProcessedEdgeFiles')


'''Run Eternally'''
#while True:

#long poll queue containing files to ship to simscore
rs = q.read(wait_time_seconds=20)

#if long poll returns file,
if rs:
    #Parse out json to be sent
    jsonSimscore = json.loads(rs.get_body())
    logit(log, '*************************\n%s\n' %datetime.now())
    logit(log,'Read in file '+jsonSimscore['TestID']+' from queue\n')
    print jsonSimscore['TestID']
    
    trys = 0
            
    #Login if logincookie is expired
    if sim.is_expired_cookie(c):
        c, buf = sim.loginSimscore(address=login)
    
    '''POSTING Retry Logic'''
    while True:
        #POST to simscore
        compute = 'http://dev.simscore.md3productions.com/simscores-v1/machinereport' 
        pp = sim.RESTfields(address=compute, header=['Content-Type: application/json'], values=json.dumps(jsonSimscore))
        c, out = pp.posthttp(c)
        http_response = c.getinfo(c.HTTP_CODE)
        
        #http_response = 100
        print http_response; print out.getvalue()
        
        
        #if simscore DEFINITELY recieves POST, returns 200, etc:
        if http_response == 200:
            logit(log,'Message received - HTTP/1.1:%d \n'%http_response)
            sdb_domain.put_attributes(jsonSimscore['TestID'],{'IsSent':True},replace=False)
            
            #delete message from queue.
            d = q.delete_message(rs)
            if d: logit(log,'Messsage deleted from queue\n')
            break
            
            
        #else if no response, don't receive 200, simscore down, etc:
        elif http_response in range(500,599):
            logit(log,'Simscore error, HTTP/1.1:%d, waiting %d seconds\n%s'%(http_response, sleeptimes[trys], out.getvalue()) )
            trysleeptimes(trys)
            
            trys += 1
            
            
        #else if error related to content of post, how post is made, 
        else:
            #log&report error and filename
            logit(log, 'Local error, HTTP: '+str(http_response)+'\n'+out.getvalue()+'\nSending email...')
            
            #email me
            failmessage = 'Error sending '+jsonSimscore['TestID']+'\n'+'shipSimscore error: %d\n\n%s'%(http_response,out.getvalue())
            send_fail(failmessage, ses_conn)
            break
            
#perform check on S3    
elif sim.approx_total_messages(comq)==0:
    #needs to be some sort of counter to see if it's a) really late at night, b) been at least 20hrs since last check
    pass
         

