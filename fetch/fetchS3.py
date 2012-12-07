"""
######################

DEPRICATED FOR USE IN FUTURE COMPUTING, 
TLH, 12/6/2012

######################
"""

import boto
import cStringIO
import re
import json
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from datetime import datetime
from configuration import names as hlist


def s3Connection(access=None, secret=None, is_secure=True):
    '''
    connect to s3
    returns live boto connection
    '''
    access = 'AKIAIFL36FMY6XX745CA'
    secret = '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'
    if access and secret:
        return S3Connection(access, secret, is_secure=is_secure)
    return S3Connection(is_secure=is_secure)

def getBucket(bucketname='incoming-simscore-org', access=None, secret=None, conn=None, is_secure=True):
    '''
    get a bucket by name
    returns boto s3 bucket
    '''
    if conn:
        return conn.get_bucket(bucketname)
    return s3Connection(is_secure=is_secure).get_bucket(bucketname)

def getFile(filename, bucketname='incoming-simscore-org', conn=None, is_secure=True):
    '''
    get a file by name, bucketname
    returns a numpy array with a header
    '''  
    bucket = getBucket(bucketname, conn, is_secure=is_secure) 
    bKey = bucket.get_key(filename)
    txt, names = cleanFile(bKey)
    return txt, names

def getMetaFile(filename, bucketname='incoming-simscore-org', conn=None, is_secure=True):
    ''' 
    get a meta data file by name, bucketname
    returns a python dict
    '''
    bucket = getBucket(bucketname, conn) 
    bKey = bucket.get_key(filename) #boto.bucket
    meta = bKey.get_contents_as_string() #boto.key
    return json.loads(meta)

def getFilesPastDate(minfilename, bucketname='incoming-simscore-org', conn=None, is_secure=True):
    k = None
    try:
        mindate = getFileDateFromKey(minfilename)
        keys = getBucket(bucketname, conn).list()   
        #Edited for debugging TLH 10.25.12
        files = [(key2file(k),getFileDateFromKey(k.name)) for k in keys if 'ReferenceBlock' not in k.name 
                                     and 'Logs' not in k.name 
                                     and pastdate(k, mindate)]
        #files = []
        #for k in keys:
        #    if 'ReferenceBlock'  not in k.name and 'Logs' not in k.name and pastdate(k,mindate):  
        #        files = (key2file(k),getFileDateFromKey(k.name))
                
        return files
    except Exception as e:
        errorName = k.name if k else "error"
        print 'fetch.getFilesPastDate: ', errorName, ': ', e

def getFilesByMachine(machine, bucketname='incoming-simscore-org', conn=None, is_secure=True):
    k = None
    try:
        keys = getBucket(bucketname, conn).list(machine) 
        return [(key2file(k), getFileDateFromKey(k.name)) for k in keys]
    except Exception as e:
        errorName = k.name if k else "error"
        print 'fetch.getFilesByMachine: ', errorName, ': ', e

def getFilesByUser(uids, bucketname='incoming-simscore-org', conn=None, is_secure=True):
    k = None
    isUser = lambda u: u.name.strip().split('.')[-3] in uids
    isData = lambda k: 'ReferenceBlock' not in k.name and 'Logs' not in k.name and ('.log' in k.name or '.txt' in k.name)
    try:
        keys = getBucket(bucketname, conn).list()  
        filteredKeys = filter(isData, keys)
        filtered = filter(isUser, filteredKeys) 
        return [(key2file(k), getFileDateFromKey(k.name)) for k in filtered]
    except Exception as e:
        errorName = k.name if k else "error"
        print 'fetch.getFilesByUser: ', errorName, ': ', e





'''
Utility Functions:
'''
def key2file(key):
    '''
    Given a key, returns the file in json or csv format
    '''
    try:
        if key.name[-4:] == '.txt':
            return ('data', key.name[ :-4], cleanFile(key))
        if key.name[-4:] == '.log':
            meta = key.get_contents_as_string()
            return ('meta', key.name[ :-4], json.loads(meta))
    except Exception as e:
        print 'fetch.k2f: ', e
        
def getFileDateFromKey(keyName): 
    '''
    the file date is encoded into the file name/path.  parse that out to date file
    '''
    slash = keyName.split('/') 
    dot = slash[-1].split('.') 
    sdatum = '%s %s %s %s %s %s' %(slash[-2], dot[0], slash[-3], dot[1], dot[2], dot[3])
    return datetime.strptime(sdatum, '%m %d %Y %H %M %S')

def cleanFilev0(k, txt):
    '''
    clean data files 
    new header, clear uneven trailing whitespace, make tab delimited
    '''
    
    header = '\t'.join(hlist)
    try:
        hack =re.split(r'\r?\n', k.get_contents_as_string())
    except Exception as e:
        return e
    txt.write(header)
    for line in hack[1:]:
        txt.write('\t'.join(line.strip().split()))
        txt.write('\n')
    txt.seek(0)
    return txt, hlist

def cleanFile(k):
    '''
    check for legacy log by date
    return data in consistent format for parsing
    optimal file type would be json object, however
    This is the closest which edge client can deliver
    '''
#k.lastmodified is iffy 1) changes to file days later 2) different formats returned
#    v0time = datetime.strptime('Mon, Jun 25 2012 14:28:27 GMT', '%a, %b %d %Y %H:%M:%S %Z')
#    ktime = datetime.strptime(k.last_modified, '%a, %d %b %Y %H:%M:%S %Z')
    v0time = getFileDateFromKey('/edge0/2012/06/25.15.16.29.170.0.txt')
    ktime = getFileDateFromKey(k.name) #boto.key
    txt = cStringIO.StringIO()#open(k.name.split('/')[-1].strip(), 'w+')
    if ktime < v0time:
        return cleanFilev0(k, txt)
    k.get_contents_to_file(txt) #boto.key
    txt.seek(0) #seeks to start of file
    header = txt.readline().strip().split()  
    return txt, header

def pastdate(key, mindate):
        try:
            if (key.name[-4:] == '.txt' or key.name[-4:] == '.log'):
                isPast = getFileDateFromKey(key.name) > mindate
                return isPast
            return False
        except Exception as e:
            print key, ':', e