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
from fetch.mySQS import sqs_connection as conn

from boto.sqs.message import Message

# <codecell>

def send_fail(failure, conn): 
    conn.send_email(source='thartley@simulab.com',
        subject='shipSimscore.py Errors', format='html',
        body=failure,
        to_addresses=['thartley@simulab.com'])
    
def logit(log, message):
    log.write(message)
    log.flush()

def trysleeptimes(trys, sleeptimes=None):
    if sleeptimes == None: sleeptimes=[0, 1, 10, 100, 200, 1000]
    if trys < len(sleeptimes):
        time.sleep(sleeptimes[trys])
    else:
        time.sleep(sleeptimes[-1])
sleeptimes=[0, 1, 10, 100, 200, 1000]

# <codecell>

# Open up log file to write pycurl info to
log = open (os.getcwd()+'\\ShipFails.log', 'a')
logit(log, '*************************\n%s\nBooting up shipSimscore.py\n*************************\n' % str(datetime.now()))

# Login to Simscore
c = pycurl.Curl() 
login = 'http://dev.simscore.md3productions.com/simscores-v1/user/login'
c, buf = sim.loginSimscore(c, address=login)
logit(log, 'Login response: '+str(c.getinfo(c.HTTP_CODE))+'\n'+buf.getvalue()+'\n')

# <codecell>

#make a retry loop for posting to simscore (could put this in thread/sep .py)

#Define Connections
q = conn.get_queue('Files2Ship')
from fetch.mySQS import ses_conn

#TODO: needs to be simpledb stuff here


#Run Eternally
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
            
    #POST to simscore
    if sim.is_expired_cookie(c):
        c, buf = sim.loginSimscore(c, address=login)
    
    while True:
        compute = 'http://dev.simscore.md3productions.com/simscores-v1/machinereport' 
        pp = sim.RESTfields(address=compute, header=['Content-Type: application/json'], values=json.dumps(jsonSimscore))
        c, out = pp.posthttp(c)
        http_response = c.getinfo(c.HTTP_CODE)
        
        http_response = 100
        print http_response; print out.getvalue()
        
        #if simscore DEFINITELY recieves POST, returns 200, etc:
        if http_response == 200:
            logit(log,'Message received - HTTP/1.1:%d \n'%http_response)
            
            #delete message from queue.
            d = q.delete_message(rs)
            if d:
                logit(log,'Messsage deleted from queue\n')
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
    
else:
    #perform check on S3
    pass
         

# <codecell>


# <codecell>


