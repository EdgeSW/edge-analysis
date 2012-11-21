# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import json, string
import time, datetime
import fetch.shapeS3 as shape
import fetch.fetchS3 as fetchS3
import report.tools.validate as validate
import pprint

# <headingcell level=5>

# Test Summary Metrics

# <codecell>

def summary_metrics(meta,data):
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
        ,'LToolID' : meta.get('EdgeToolIdLeftHex',meta['EdgeToolIdLeft']) #return hex ID if available (old tests do not report hex)
        ,'RToolID' : meta.get('EdgeToolIdRightHex',meta['EdgeToolIdRight'])
    #TestLength    String    The length of time it took to complete the task. Ex: 02:00.0.
        ,'TestLength' : meta["TestDurationInSeconds"]
    #testlengthpass	Boolean	Length of test is within acceptable bounds
        ,'TestLengthPass': 1 if float(meta["TestDurationInSeconds"])>5 else 0
    #Badframe	Int	Video dropped frame count.
        ,'BadFrames': meta['VideoDroppedFrameCount']
        
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
    
    #ProctorValues
    jsonSimscore['ProctorValues'] = meta.get('Proctor'+TaskType,'Unknown')
    
    #UploadDate    String    Upload Date
    xx = str(meta['DataFileNameOnEdge']).split('\\')[3].split('.')[:6]
    jsonSimscore['UploadDate'] = '-'.join(xx[:3])+' '+':'.join(xx[3:])
    
    #UploadDateUnix    Time    Date converted into Unix Epoch C Time for fast sorting.
    filename = str(meta['DataFileNameOnEdge']).split('\\')[3].split('.')
    edgetime = '.'.join(filename[:6])
    jsonSimscore['UploadDateUnix'] = int(time.mktime(time.strptime(edgetime, '%Y.%m.%d.%H.%M.%S'))) 
    
    
    #pathlength	Boolean	Total tool path length is above an accepted minimum
    
    #pathlenthvalue	String	
    
    #proctor	Boolean	Sanity check on proctor field values
    
    #continuous	Boolean	Check for any temporal discontinuities 
    check = 1
    for x in np.diff(np.diff(data['%Time_V1']) ):
        if x > 0.005 or x < -.005: check = 0
    jsonSimscore['Continuous'] = check
    
    return jsonSimscore

#jsonSimscore = summary_metrics(meta,data,diff)
#pp.pprint(jsonSimscore)

# <headingcell level=5>

# Test Data Metrics

# <codecell>

from fetch.configuration import isClipTask

def data_metrics_append(jsonSimscore, data, filename):
    jsonSimscore.update({
        #Max	Float	Min	Float                 
         'MinMax' : validate.findMinMax(data)
        #Dead	Boolean	
        ,'DeadSensors' : validate.findDeadSensor(validate.findMinMax(data), isClipTask(filename))
        #Out of Range	Boolean
        ,'OutOfRange' : validate.findOutOfRange(validate.findMinMax(data))
        #NaN	Boolean	
        ,'NaNSensors' : validate.findNans(data, isClipTask(filename))
    })
    return jsonSimscore

#jsonSimscore = data_metrics_append(jsonSimscore, data, filename)
#pp.pprint(jsonSimscore)

# <headingcell level=5>

# Machine Health Metrics

# <codecell>

def start_v_end(*args):
    if len(args)>1:
        return tuple( e[-1]-e[0] for e in args)
    else: return args[0][-1]-args[0][0]

# <codecell>

def machine_health_append(jsonSimscore, meta, data):    
    #	MachineHealthReportID	Int	
    #	ActiveRecord	Boolean	Used to keep track of what machine health record is shown in the dashboard.
    #	kinematics	Boolean	Kinematics set to default values
    #	md5hash	Boolean	MD5 hash is intact
    
    #	ToolTipDriftValue	Float	
    jsonSimscore['ToolTipDriftValue'] = {'left':list(start_v_end(data['X_L'],data['Y_L'],data['Z_L'])), 'right':list(start_v_end(data['X_R'],data['Y_R'],data['Z_R']))}
    
    #	ToolTipDrift	Boolean	Tool tip position same at beginning and end of test (tooltip drift)
    vall = 0; valr = 0
    for v in list(start_v_end(data['X_L'],data['Y_L'],data['Z_L'])):
        if v > 3: vall = 1
    for v in list(start_v_end(data['X_R'],data['Y_R'],data['Z_R'])):        
        if v > 3: valr = 1    
    jsonSimscore['ToolTipDrift'] = {'left':vall, 'right':valr}
    
    #	LinEncDrift	Boolean	Is there linear encoder drift?
    jsonSimscore['LinEncDrift'] = {'left': 1 if abs(start_v_end(data['Lin_L'])) > 1 else 0, 'right': 1 if abs(start_v_end(data['Lin_R'])) > 1 else 0}
    #	LinEncDriftValue	Float	Offset from start and finish linear encoder point
    jsonSimscore['LinEncDriftValue'] = {'left': start_v_end(data['Lin_L']), 'right': start_v_end(data['Lin_R'])}
    #	InvalidToolID	Boolean	Check that tool IDs exist in database
    
    #	lastCalibration	String	Date of last machine calibration.
    temp = meta['CalibrationData']['CalibrationSavedDate'].split('T')
    jsonSimscore['LastCalibration'] = str(temp[0]+' '+temp[1])
    #	lastUpload	String	Date of last uploaded test to machine.
    #	FailType	String	Concatenated string of items that failed. Ex: OB Data, Video Corruption
    
    return jsonSimscore

#jsonSimscore = machine_health_append(jsonSimscore, data)

# <codecell>

#FailType	List of String	List of Failure Types for whole test: OB Data, Video Corruption
#List of errors to report (previously computed)
#errors = ['NaNSensors','DeadSensors','OutOfRange']#DroppedFrames, InvalidToolID, LinEncDrift
#jsonSimscore['FailTypes'] = [error for error in errors if jsonSimscore[error] != [] ]

#OutOfRange
#NaN
#DeadSensor
#DroppedFrames
#LinEncDrift
#InvalidToolID

# <codecell>

#from fetch.configuration import kinematics
#fetch.configuration.__file__

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

# <codecell>


