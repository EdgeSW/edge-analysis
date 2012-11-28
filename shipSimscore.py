# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=4>

# POST computed files to Simscore

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')

import boto
import json
import pycurl
import validity_metrics as vm
import report.simscore as sim
from fetch.mySQS import sqs_connection as conn

from boto.sqs.message import Message

# <codecell>

%load_ext autoreload
%autoreload

add = 'http://dev.simscore.md3productions.com/simscores-v1/machinereport'

p = sim.Postfields(user = 'grading', pw='r*tFQqmb')
p.print_post()

# <codecell>

#make a retry loop for posting to simscore (could put this in thread/sep .py)

#Define Connections
q = conn.get_queue('Files2Ship')
#needs to be simpledb stuff

max_retries = 6
trys = 0
trysleeptimes = [0, 1, 1, 10, 20, 60]

#Run Eternally
#while True:

#long poll queue containing files to ship to simscore
rs = q.read(wait_time_seconds=20)

#if long poll returns file,
if rs:
    #Parse out json to be sent
    jsonSimscore = json.loads(rs.get_body())

    #while trys < max_retries
        #if trys < len(trysleeptimes):
            #time.sleep(trysleeptimes[trys])
        #else: time.sleep(trysleeptimes[-1])
            
        #POST to simscore
        c = pycurl.Curl()  
        sim.postSimscore(c, json.dumps(jsonSimscore))
        
        #if simscore DEFINITELY recieves POST, returns 200, etc:
            #delete message from queue.
            #trys = 
            
        #else if no response, don't receive 200, simscore down, etc:
            #trys += 1
        #else if error related to content of post, how post is made, 
            #log&report error and filename
            #
        
#else pass
         

# <codecell>


