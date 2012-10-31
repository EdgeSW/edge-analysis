from collections import defaultdict, OrderedDict
from itertools import groupby

import httplib2
import sys
import json
import pprint
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from apiclient.errors import HttpError
from flow import FLOW

projectId = '459512762119'
url = "https://www.googleapis.com/upload/bigquery/v2/projects/" + projectId + "/jobs"

def query(queryString):  
    timeout = 7000 
    service = build("bigquery", "v2", http=getHttp())
    jobCollection = service.jobs()
    queryData = {'query': queryString,
                 'timeoutMs': timeout,
                 'maxResults': 50000}
    try:
        queryReply = jobCollection.query(projectId=projectId,
                                         body=queryData).execute()
        
        jobReference=queryReply['jobReference']
        
        # Timeout exceeded: keep polling until the job is complete.
        while(not queryReply['jobComplete']):
            print 'Job not yet complete...'
            queryReply = jobCollection.getQueryResults(
                              projectId=jobReference['projectId'],
                              jobId=jobReference['jobId'],
                              timeoutMs=timeout).execute()                      
        return queryReply['rows']
        print ("The credentials have been revoked or expired, please re-run"
        "the application to re-authorize")
    
    except HttpError as err:
        print 'Error in runSyncQuery:', pprint.pprint(err.content)
    
    except Exception as err:
        print 'Undefined error' % err

def queryTableData(dataset, table, startIndex=0):
    data = {'rows': []}
    service = build("bigquery", "v2", http=getHttp())
    tableDataJob = service.tabledata()
    try:
        queryReply = tableDataJob.list(projectId=projectId,
                                     datasetId=dataset,
                                     tableId=table,
                                     startIndex=startIndex).execute()
        
        # When we've printed the last page of results, the next
        # page does not have a rows[] array.
        while 'rows' in queryReply:
            data['rows'].extend(queryReply['rows'])
            startIndex += len(queryReply['rows'])
            queryReply = tableDataJob.list(projectId=projectId,
                                     datasetId=dataset,
                                     tableId=table,
                                     startIndex=startIndex).execute()
            
        return data
    except HttpError as err:
        print 'Error in querytableData: ', pprint.pprint(err.content)

def loadTableFromCSV(bodydata):
    http = getHttp()
    headers = {'Content-Type': 'multipart/related; boundary=xxx'}
    res, content = http.request(url, method="POST", body=bodydata, headers=headers)
    print str(res) + "\n"
    print content

'''
Utilities
'''
def getHttp():
    # If the credentials don't exist or are invalid, run the native client
    # auth flow. The Storage object will ensure that if successful the good
    # credentials will get written back to a file.
    storage = Storage('bigquery.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run(FLOW, storage)
        storage = Storage('bigquery2.dat')
    
    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    return http


def getBody(data, fields, table, dataset, createDisposition, writeDisposition):
    bodyEnd = ('--xxx--\n')
    strbody = '''--xxx
Content-Type: application/json; charset=UTF-8

{
   "configuration": {
      "load": {
         "schema": {
            "fields" : %s
         },
         "destinationTable": {
            "projectId": "%s", 
            "datasetId": "%s",
            "tableId": "%s" 
            
         }, 
         "createDisposition": "%s", 
         "writeDisposition": "%s"
      }
   }
}
--xxx
Content-Type: application/octet-stream

''' %(fields, projectId, dataset, table, createDisposition, writeDisposition)

    return (strbody) + (data) + bodyEnd




    


    
    
        
        
        