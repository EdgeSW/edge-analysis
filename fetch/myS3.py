import json, cStringIO
from datetime import datetime, timedelta
from fetch.configuration import formats
from fetch.configuration import converterdict
import numpy as np
import boto
from aws import aws_ak, aws_sk

edges = ['edge0/', 'edge1/', 'edge10/', 'edge11/', 'edge12/', 'edge2/', 'edge3/', 'edge4/', 'edge5/', 'edge6/', 'edge7/', 'edge8/', 'edge9/']
#edges = ['edge10/', 'edge11/', 'edge12/', 'edge2/', 'edge3/', 'edge4/', 'edge5/', 'edge6/', 'edge7/', 'edge8/', 'edge9/']



def getRawData(bucket=None, filename=None, labeled=False):
    '''Pull and format raw data from a .txt file on S3. Return as
    Numpy array of 64bit floats'''
    if bucket == None: bucket = getBucketConn()
    bKey = bucket.get_key(filename)
    if not bKey: raise ValueError, "File not found on S3"
    txt = cleanRaw(bKey)
    header = txt.readline().strip().split() 
    
    if not header or txt.tell() == 0:  #added 1/7/13 to deal with edge uploads of empty files
        return None                 #edited 1/30 to include length of header (220bytes)
    if not txt.readline():
        return None
    
    txt.seek(0)
    txt.readline()
    return dataParse(txt, header, labeled)
    
def getMetaData(filename=None, bucket=None):  
    '''Returns metadata .log file. Can provide .txt raw data file and get corresponding .log'''
    if bucket == None: bucket = getBucketConn()
    if filename[-3:] == 'txt': filename = filename[:-3]+'log'
    
    bKey = bucket.get_key(filename) #boto.bucket
    meta = bKey.get_contents_as_string() #boto.key
    return json.loads(meta)

def getData(bucket=None, filename=None, labeled=False):
    '''Fetches both raw and meta data from S3. Labeled parameter asks if you want the data
    returned with an associated dtype or not (see dataParse below)'''
    assert bucket, 'Please provide a bucket or S3 connection instance'
    data = getRawData(bucket, filename, labeled)
    meta = getMetaData(filename, bucket)
    return data, meta

def getFilesBetween(mindate=None, maxdate=datetime.utcnow(), bucket=None, onlyTxtFiles=False): #edit to take in conn and bucketname for consistency?
    '''Fetch a list of EVERY file on S3 between given dates. MUCH faster than retreiving 
    all file keys and then parsing, especially as S3 grows. I know its a lot of for loops, deal with it
    Output: files is a list of strings'''
    if bucket == None: bucket = getBucketConn()
    dates_in_range = datesInRange(mindate,maxdate)
    files = []
    for edge in edges:  #edges imported above
        for year in dates_in_range.keys():
            for month in dates_in_range[year]:
                rs = bucket.list(prefix= ''.join([edge,str(year),'/', "%02d"%month]) )
                
                for k in rs:
                    if onlyTxtFiles and str(k.name)[-3:]=='log': continue
                    try: 
                        if isBetweenDates(mindate,maxdate,str(k.name)): files.append(str(k.name)) 
                    except IndexError: pass
    #files is a list of strings                
    return files

def getTestFiles(filelist=None, bucket=None, getPractice=False):
    '''pull a list of EDGE files that were "Tests" instead of "Practices". Can 
    also perform the inverse. If you want all files, use getFilesBetween'''
    output = []
    for f in filelist:
        meta = getMetaData(f, bucket)
        if meta["IsPracticeTest"] == False and not getPractice:
            output.append(f)
        elif meta["IsPracticeTest"] == True and getPractice:
            output.append(f)
    return output
    
def getTestFilesBetween(mindate=None, maxdate=datetime.utcnow(), bucket=None, getPractice=False):
    '''wrapper for getTestFiles'''
    filelist = getFilesBetween(mindate, maxdate, bucket, onlyTxtFiles=True)
    return getTestFiles(filelist, bucket, getPractice)
    
def getDataFromTxtFileList(bucket=None, files=None, labeled=False, includeMeta=True, includePractice=True):
    '''Given a list of .txt files on S3, will return data associated with each file in that list.
    MUST be given only list of .txt files. If you want only meta data, use getMetaDataBetween()
    Can be set to return meta data too. Can return data as "labeled" data with assigned dtype. '''
    if bucket == None: bucket = getBucketConn()
    allData = {}
    for f in files:
        if not includePractice: 
            metadata = getMetaData(f, bucket); 
            m = metadata['IsPracticeTest']
        else: m = False
        
        if includeMeta and not m: allData[f] = {'meta': metadata if not includePractice else getMetaData(f, bucket), 'data': getRawData(bucket, f, labeled)}
        elif not m: allData[f] = getRawData(bucket, f, labeled) 
        
        
    return allData   

def getDataBetween(mindate=None, maxdate=datetime.utcnow(), bucket=None, labeled=False, includeMeta=True, includePractice=True):
    '''Returns data between two dates as dict, can include meta data if you want.
    Basically a glorified wrapper for getDataFromTxtFileList'''
    if bucket == None: bucket = getBucketConn()
    files = getFilesBetween(mindate, maxdate, bucket, onlyTxtFiles=True)
    return getDataFromTxtFileList(bucket, files, labeled, includeMeta, includePractice)
    
def getMetaDataBetween(mindate=None, maxdate=None, bucket=None):
    '''Go get only meta data between 2 dates'''
    if bucket == None: bucket = getBucketConn()
    meta = {}
    files = getFilesBetween(mindate, maxdate, bucket, onlyTxtFiles=False)
    for f in files:
        if f[-3:]=='log': meta[f] = getMetaData(f, bucket)
    return meta  

def getLeftBehind(daysback, conn=None, sdb_domain=None):
    '''locate files on S3 that have not been added as items to a SimpleDB domain'''
    mindate = datetime.utcnow() -timedelta(days=daysback)
    s3_files = getFilesBetween(mindate, datetime.utcnow(), conn.get_bucket('incoming-simscore-org'), onlyTxtFiles=True)
    sdb_items = [item.name for item in sdb_domain]
    
    return [f for f in s3_files if f[:-4] not in sdb_items]
    
    

def getFileDateFromKey(keyName): 
    '''Parse out the date from a given filename'''
    slash = keyName.split('/') 
    dot = slash[-1].split('.') 
    sdatum = '%s %s %s %s %s %s' %(slash[-2], dot[0], slash[-3], dot[1], dot[2], dot[3])
    return datetime.strptime(sdatum, '%m %d %Y %H %M %S')

def isBetweenDates(mindate, maxdate, keyname):
    '''example keyname: 'edge10/2012/12/04.15.32.07.109.0.txt' '''
    #print keyname
    thisdate = getFileDateFromKey(keyname)
    return (thisdate >= mindate and thisdate <= maxdate)

def datesInRange(mind,maxd):
    '''returns dict of years and the months that are between
    the minimum date (mind) and max date (maxd) '''
    dates = {}
    for year in range(mind.year, maxd.year+1):
        if year == mind.year:
            dates[year] = range(mind.month, (maxd.month if year==maxd.year else 12) +1)
        elif year > mind.year and year < maxd.year:
            dates[year] = range(1, 12+1)
        elif year == maxd.year and year != mind.year:
            dates[year] = range(1, maxd.month+1)
            
    return dates

def dataParse(f, names, labeled):
    '''Convert a cStringIO object of raw data into a numpy float array.
    can return array given value of 'labeled' such that data['varname'] 
    returns variable vector, or simply as MxN array to be called as data[:,3] '''
    try:
        dt = {'names' : names, 'formats' : formats}
        #comments set to none because defaults to # and #I.IO is Jay's version of NaN
        if labeled:  data = np.loadtxt(f,  comments='%', skiprows=0, dtype=dt, converters=converterdict)
        else:  data = np.loadtxt(f,  comments='%', skiprows=0,  converters=converterdict) 
        
        return data
    except Exception as e:
        raise e #return e instead to log?
    
def cleanRaw(bKey):
    '''Removes header, cleans each line of extra whitespace'''
    txt = cStringIO.StringIO()
    bKey.get_contents_to_file(txt)
    txt.seek(0) #seeks to start of file
    return txt
    #header = txt.readline().strip().split() 
      
def getEdgeFolderNamesOnS3(conn=None, bucketname='incoming-simscore-org'):
    '''return the prefixes on s3 buckets that correspond to folders containing Edge data'''
    bucket = conn.get_bucket(bucketname); edges=[]
    return [edges.append(str(key.name)) for key in bucket.list(prefix='edge', delimiter='/')]

def getBucketConn(bucketname='incoming-simscore-org'):
    conn = boto.connect_s3(aws_ak, aws_sk)
    return conn.get_bucket(bucketname)
    
    