# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=4>

# POST computed files to Simscore

# <codecell>

import sys, os
#sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')

import boto
import json, time
from datetime import datetime, timedelta
import pycurl
import validity_metrics as vm
import report.simscore as sim
import fetch.mySQS as mySQS
import fetch.myS3 as myS3
from aws import aws_ak, aws_sk
from boto.sqs.message import Message, RawMessage

def send_fail(failure, conn): 
    conn.send_email(source='thartley@simulab.com',
        subject='shipSimscore.py Errors', format='html',
        body=failure,
        to_addresses=['thartley@simulab.com'])
    
def logit(log, message):
    log.write(message)
    log.flush()

def trysleeptimes(trys):
    global sleeptimes
    sleeptimes = [0, 1, 10, 100, 200, 1000]
    
    if trys < len(sleeptimes):
        time.sleep(sleeptimes[trys])
    else:
        time.sleep(sleeptimes[-1])

def leftBehindCheck(daysback):
    conn = boto.connect_s3(aws_ak, aws_sk)
    theforgotten = myS3.getLeftBehind(daysback=daysback, conn=conn, sdb_domain=sdb_domain)
    
    if len(theforgotten) > 0:
        mySQS.append_list_to_queue(theforgotten, comq)
        logit(log,'ERROR: %d files on S3 do not match processed file list.\nAdded these files to queue:\n'%len(theforgotten))
        for f in theforgotten: logit(log,'%s\n'%f)

# <codecell>

'''Define Connections'''
sqs_conn = boto.connect_sqs(aws_ak, aws_sk)
q = sqs_conn.get_queue('Files2Ship')
comq = sqs_conn.get_queue('EdgeFiles2Process')

#Connect to SimpleDB
sdb_conn = boto.connect_sdb(aws_ak, aws_sk)
sdb_domain = sdb_conn.get_domain('ProcessedEdgeFiles')

# <codecell>

def main(c):
   
    #long poll queue containing files to ship to simscore
    rs = q.read(wait_time_seconds=20)
    
    #if long poll returns file,
    if rs:
        #Parse out json to be sent
        jsonSimscore = json.loads(rs.get_body())
        logit(log, '--------------------\n%s\n' %datetime.now())
        logit(log,'Read in file '+jsonSimscore['TestID']+' from queue\n')
        print jsonSimscore['TestID']
        
        trys = 0
                
        #Login if logincookie is expired
        if sim.is_expired_cookie(c):
            c, buf = sim.loginSimscore(address=login)
        
        '''POSTING Retry Logic'''
        while True:
            #POST to simscore 
            compute = 'http://simscore.org/simscores-v1/machinereport' #'http://dev.simscore.md3productions.com/simscores-v1/macinereport'
            pp = sim.RESTfields(address=compute, header=['Content-Type: application/json'], values=json.dumps(jsonSimscore))
            c, out = pp.posthttp(c)
            http_response = c.getinfo(c.HTTP_CODE)
            
            #http_response = 100
            print http_response #; print out.getvalue()
            
            
            #if simscore DEFINITELY recieves POST, returns 200, etc:
            if http_response in [200, 202]:
                logit(log,'Message received - HTTP/1.1:%d \n'%http_response)
                sdb_domain.put_attributes(jsonSimscore['TestID'],{'IsSent':True},replace=False)
                
                #delete message from queue.
                d = q.delete_message(rs)
                if d: logit(log,'Deleted from queue\n')
                break
                
            #else if no response, don't receive 200, simscore down, etc:
            elif http_response in range(500,599):
                logit(log,'Simscore error, HTTP/1.1:%d, waiting %d seconds\n%s'%(http_response, sleeptimes[trys], out.getvalue()) )
                trysleeptimes(trys)
                trys += 1
                
            elif http_response == 409:
                logit(log,'Local error, HTTP: {0}. Attempted to send duplicate test {1}\n'.format(http_response, jsonSimscore['TestID']))
                d = q.delete_message(rs)
                if d: logit(log,'Deleted from queue\n')
                break
            elif http_response == 419:
                logit(log,'Local error, HTTP: {0}. Invalid value in json: {1}\n{2}\n'.format(http_response, jsonSimscore['TestID'], out.getvalue()))
                d = q.delete_message(rs)
                if d: logit(log,'Deleted from queue\n')
                break    
                
            #else if error related to content of post, how post is made, 
            else:
                rs.change_visibility(300) #if having local trouble with it, make invisible for 2 min
                #log&report error and filename
                logit(log, 'Local error, HTTP: '+str(http_response)+'\n'+out.getvalue()+'\nSending email...\n')
                
                #email me
                failmessage = 'Error sending '+jsonSimscore['TestID']+'\n'+'shipSimscore error: %d\n%s\n'%(http_response,out.getvalue())
                #Connect to ses
                ses_conn = boto.connect_ses(aws_ak, aws_sk)
                send_fail(failmessage, ses_conn)
                break

# <codecell>

    
    #perform check on S3    
    '''
    elif mySQS.approx_total_messages(comq)==0:
        
        f = open('/home/ubuntu/logs/lastchecks.log','rw') 
        #If one week has passed:
        if time.time() > int(f.readlines()[0].strip())+3600*24*7:
            leftBehindCheck(30)
            #change the big and little check time to now
            f.write(str(int(time.time()))+'\n'+str(int(time.time())) )
        
        elif time.time() > int(f.readlines()[1].strip())+3600*24:
            leftBehindCheck(7)
            #change the big and little check time to now
            f.write(f.readlines()[0].strip()+'\n'+str(int(time.time())) )
        f.close()
    '''
                    
    return rs, c

# <codecell>

if __name__ == "__main__":
    # Open up log file to write pycurl info to
    #log = open (os.getcwd()+'\\ShipFails.log', 'a')
    log = open ('/home/ubuntu/logs/ShipFails.log', 'a')
    logit(log, '{0}\n{1}\n{2}\n{0}\n'.format('*'*26,datetime.now(),'Booting up shipSimscore.py'))
    
    # Login to Simscore
    #login = 'http://dev.simscore.md3productions.com/simscores-v1/user/login'
    c, buf = sim.loginSimscore()
    logit(log, 'Login response: '+str(c.getinfo(c.HTTP_CODE))+'\n'+buf.getvalue()+'\n')
    
    '''Run Eternally'''
    rs = True
    #while rs: #this is changed to while True when eternal server needed
    while True:
        rs, c = main(c)
        

