# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%load_ext autoreload
%autoreload 2
import fetch.shapeS3 as shape
import fetch.fetchS3 as fetchS3
import report.tools.validate as validate
import numpy as np
import time
import json, sys, getopt, string, os, datetime, pprint
import StringIO, base64

# <codecell>

filename = 'edge6/2012/10/24.21.59.05.325.0.txt'
bucketname = 'incoming-simscore-org'
is_secure = False if '.' in bucketname else True
data, meta = shape.getData(filename, bucketname, is_secure=is_secure)

# <codecell>

%whos module

# <codecell>

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(meta)

# <headingcell level=5>

# Test Summary Metrics

# <codecell>

jsonSimscore = {
                
                
#TestID    Int    The uniquely generated ID for this test score to associate all other data with.
    'TestID' : meta['DataFileNameOnS3'][:-4] 
#IsPractice    Boolean    Is this a scored test?
    , 'IsPractice' : meta["IsPracticeTest"]
#MetadataFilename    String    Metadata Filename and location in S3.
    ,'MetadataFilename' : meta["MetaDataFileNameOnS3"]    
#TestDataFilename    String    Test Data Filename and location in S3.
    ,'TestDataFilename' : meta['DataFileNameOnS3']    
#VideoDataFilename    String    Video Data Filename and location in S3.
 ,'VideoDataFilename' : meta["VideoFileNameOnS3"]
#UserID    String    User ID.
    ,'UserID' : str(meta['UserId'])
#ProctorID    String    Proctor ID.
    ,'ProctorID' : str(meta["ProctorId"])
#EdgeID    String    EDGE ID.
    ,'EdgeID' : str(meta["EdgeUnitId"])
#SwVersion    String    EDGE software version.
    ,'SwVersion' : meta["EdgeSoftwareVersion"]
#RToolID    String    Right Tool ID.
    ,'RToolID' : meta["EdgeToolIdRight"]
    ,'LToolID' : meta["EdgeToolIdLeft"]
#TestLength    String    The length of time it took to complete the task. Ex: 02:00.0.
    ,'TestLength' : meta["TestDurationInSeconds"]
#UploadDate    String    Upload Date
    ,'UploadDate' : '.'.join(str(meta['DataFileNameOnEdge']).split('\\')[3].split('.')[:6])

    
                }

#InstitutionID    String    EDGE Institution ID.
inst = ['Engineering','Tulane','SIU','UPMC','Madigan','Duke','UC Irvine','UNM','Cleveland Clinic','UW','OSU','NA','NA']
try: InstitutionID = inst[meta['EdgeUnitId']]
except: InstitutionID = 'Unknown'
jsonSimscore['InstitutionID'] = InstitutionID   

#TaskType    String    Task Type.
tasks = ['PegTransfer','Cutting','Suture','ClipApply']
try: TaskType = tasks[meta["TaskId"]]
except: TaskType = 'Unknown'
jsonSimscore['TaskType'] = TaskType 

#UploadDateUnix    Time    Date converted into Unix Epoch C Time for fast sorting.
filename = str(meta['DataFileNameOnEdge']).split('\\')[3].split('.')
edgetime = '.'.join(filename[:6])
jsonSimscore['UploadDateUnix'] = int(time.mktime(time.strptime(edgetime, '%Y.%m.%d.%H.%M.%S'))) 

#testlength	Boolean	Length of test is within acceptable bounds

#pathlength	Boolean	Total tool path length is above an accepted minimum

#pathlenthvalue	String	

#proctor	Boolean	Sanity check on proctor field values

#continuous	Boolean	Check for any temporal discontinuities 

print json.dumps(jsonSimscore)

# <headingcell level=5>

# Test Data Metrics

# <codecell>

from fetch.configuration import isClipTask
#testID	Int	The test ID this record is associated with. See Test Summary.
#Metric	String	

jsonSimscore.update({
    #Max	Float	Min	Float                 
     'MinMax' : validate.findMinMax(data)
    #Dead	Boolean	
    ,'Dead' : validate.findDeadSensor(validate.findMinMax(data))
    #Out of Range	Boolean
    ,'OutOfRange' : validate.findOutOfRange(validate.findMinMax(data))
    #NaN	Boolean	
    ,'NaN' : validate.findNans(data, isClipTask(filename))
})

if not jsonSimscore['MinMax'] and not jsonSimscore['Dead']:
if not jsonSimscore['MinMax'] and not jsonSimscore['Dead']:
    status = False
else: status =  True
print status
#Status	String

#pp.pprint(jsonSimscore)

# <headingcell level=5>

# Machine Health Metrics

# <codecell>

#MachineHealthReportID	Int	
#TestID	Int	
#ActiveRecord	Boolean	Used to keep track of what machine health record is shown in the dashboard.
#kinematics	Boolean	Kinematics set to default values
#md5hash	Boolean	MD5 hash is intact
#tooltippos	Boolean	Tool tip position same at beginning and end of test (tooltip drift)
#tooltipposvalue	Float	
#ToolID	Boolean	Check that tool IDs exist in database
#nulldata	Boolean	Sensor data does not contain NaNs, null data

#lastCalibration	String	Date of last machine calibration.
#lastUpload	String	Date of last uploaded test to machine.
#pendingUploads	String	Number of pending uploads.
#fail_type	String	Concatenated string of items that failed. Ex: OB Data, Video Corruption
#bad_sensors	String	Concatenated string of sensors that are bad. Ex: J1_R, Fg_L.
#sw_ver	String	EDGE software version

# <headingcell level=1>

# Simscore Communications

# <codecell>

import pycurl
import cStringIO
#10.23.12 - written to retrieve aua user skill as per Martin's email 10/18/12

def loginSimscore(c):
    """Login to Simscore with Grading account"""
    #buf = cStringIO.StringIO()
     
    c.setopt(c.URL, 'http://simscore.org/simscores-v1/user/login')
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(c.POSTFIELDS, '{"username":"grading", "password":"r*tFQqmb"}')
    c.setopt(c.COOKIEFILE, '')
    #c.setopt(c.VERBOSE, True)
    #c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()
    return c
    
#c = pycurl.Curl()  
#c = loginSimscore(c)

# <codecell>

import ast

def getSkillSimscore(c):
    """GET json of AUA users from Simscore given previous login & global cookie"""
    #c = pycurl.Curl()
    auausers = cStringIO.StringIO()
    
    c.setopt(c.URL, 'http://simscore.org/simscores-v1/auainfo')
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(c.HTTPGET, 1)
    #c.setopt(c.VERBOSE, True)
    c.setopt(c.WRITEFUNCTION, auausers.write)
    
    c.perform()
    #Given the string in auausers, convert to dict
    xx = ast.literal_eval(auausers.getvalue())
    aua_skill = {}
    for u in xx:
        aua_skill[ u['uid']] = u['level'] #two values: user id and that user's level
    return aua_skill

#auausers = getSkillSimscore(c)
#print auausers

# <codecell>

def logoutSimscore(c):
    """Logout from Simscore"""
    #c = pycurl.Curl()
    c.setopt(c.URL, 'http://simscore.org/simscores-v1/user/logout')
    c.setopt(c.POST, 1)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    #c.setopt(c.VERBOSE, True)
    
    c.perform()
    return c

#c = logoutSimscore(c)

