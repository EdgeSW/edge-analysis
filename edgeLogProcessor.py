import sys, os
from datetime import datetime
import json
import boto
from boto.s3.connection import S3Connection
import boto.sqs.message
import pickle
import math
import string

class edgeLogProcessor:
    '''
    class which processes EDGE log files 
    '''

    def __init__(self, useTestBucket=False):
        self.connection = self._s3Connection()
        self.bucketName = 'incoming-simscore-org-test' if useTestBucket else 'incoming-simscore-org'
        self.bucket = self._getBucket(self.bucketName, conn = self.connection)

# ---------------------------------------------------------------------------------------------------------------------
# S3
# ---------------------------------------------------------------------------------------------------------------------
    
    def _s3Connection(self, access=None, secret=None, is_secure=True):
        '''
        connect to s3
        returns live boto connection
        '''
        access = 'AKIAIFL36FMY6XX745CA'
        secret = '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'
        if access and secret:
            return S3Connection(access, secret, is_secure=is_secure)
        return S3Connection(is_secure=is_secure)

    def _getBucket(self, bucketname='incoming-simscore-org', access=None, secret=None, conn=None, is_secure=True):
        '''
        get a bucket by name
        returns boto s3 bucket
        '''
        if conn:
            return conn.get_bucket(bucketname)
        return S3Connection(is_secure=is_secure).get_bucket(bucketname)

# ---------------------------------------------------------------------------------------------------------------------
# Functions which return filenames
# ---------------------------------------------------------------------------------------------------------------------

    def getMachineLogFilenames(self, prefix):
        '''
        get a list of machine log files.
        To get just a certain month, use prefix of 'Logs/edge4/2012/11' or day: 'Logs/edge4/2012/11.21' or year: 'Logs/edge4/2012'
        returns list of matching files
        '''
        k = None
        try:
            keys = self.bucket.list(prefix)
            names = [key.name for key in keys]
            return names
        except Exception as e:
            errorName = prefix if k else "error"
            print 'getMachineLogFilenames: ', errorName, ': ', e

    def getMachineLogFilenamesForDateRange(self, edgeId, start, end):
        '''
        get machine logs for a range of dates.
        '''
        logs = []
        for year in range (start.year, end.year +1):
            startMonth = start.month if (year == start.year) else 1
            endMonth = end.month if (year == end.year) else end.month
            for month in range (startMonth, endMonth+1):
                n = 'Logs/edge{0}/{1}/{2:02d}'.format (edgeId, year, month)
                for file in self.getMachineLogFilenames(n):
                    logs.append(file)
        return logs

# ---------------------------------------------------------------------------------------------------------------------
# Functions which return contents of machine log files
# ---------------------------------------------------------------------------------------------------------------------

    def getMachineLogContents(self, filename):
        '''
        get a machine log as a list of strings.
        '''
        k = None
        try:
            bKey = self.bucket.get_key(filename)
            strings = bKey.get_contents_as_string()
            newLines = strings.splitlines()
            return newLines
        except Exception as e:
            errorName = filename if filename else "error"
            print 'edgeLogProcessor.getMachineLogContents: ', errorName, ': ', e
            return []

    def getMachineLogContentsForDateRange(self, edgeId, start, end):
        '''
        munge together all log files for a given machine within a date range
        '''
        allLines = set()
        fileList = self.getMachineLogFilenamesForDateRange (edgeId, start, end)
        for file in fileList:
                fileDate = self.getFileDateFromKey(file)
                if (fileDate >= start and fileDate <= end):
                    lines = self.getMachineLogContents(file)
                    for line in lines:
                        if line not in allLines:
                            allLines.add(line)
        sortedLines = list(allLines)  
        sortedLines.sort()      
        return sortedLines

# ---------------------------------------------------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------------------------------------------------

    def getFileDateFromKey(self, keyName): 
        '''
        the file date is encoded into the file name/path.  parse that out to date file
        '''
        #remove leading slash if present
        if keyName[0] == '/':
            keyName = keyName.lstrip('/')

        slash = keyName.split('/') 
        dot = slash[-1].split('.') 
        if 'Logs' in slash:
            sdatum = '%s %s %s %s %s %s' %(dot[-0], dot[1], slash[2], dot[2], dot[3], dot[4])
        else:
            sdatum = '%s %s %s %s %s %s' %(slash[-2], dot[0], slash[-3], dot[1], dot[2], dot[3])
        return datetime.strptime(sdatum, '%m %d %Y %H %M %S')


    def edgeIdFromLogFile(self, f):
        '''
        input Log file name '/edge0/2012/06/25.15.16.29.170.0.log', 
        return EdgeID as int, in this case: 0
        '''
        return (f.split('edge')[1]).split('/')[0]

# ---------------------------------------------------------------------------------------------------------------------
# Parse and print
# ---------------------------------------------------------------------------------------------------------------------

    def processMachineLog(self, edgeId, lines):
        '''
        extract useful info from the machine log 
        '''
        # Show startups and shutdowns
        StartupLines = filter(lambda x: 'Simulab.Edge.MainWindow --' in x, lines)
        ShutdownLines = filter(lambda x: 'MainWindowClosing' in x, lines)
        StartupLines = StartupLines + ShutdownLines
        StartupLines = sorted (StartupLines)
        Startups = [(lines.index(s), s.split('Simulab.Edge.')[-1]) for s in StartupLines ]
        # Versions, free disk space, capture devices
        EdgeVersionLines = filter(lambda x: 'EdgeVersion' in x, lines)
        EdgeVersions = [(lines.index(s), s.split(' ')[-1]) for s in EdgeVersionLines ]
        ClrVersionLines = filter(lambda x: 'ClrVersion' in x, lines)
        ClrVersions = [(lines.index(s), s.split(' ')[-1]) for s in ClrVersionLines ]
        FreeDiskSpaceLines = filter(lambda x: 'Free disk space' in x, lines)
        FreeDiskSpaces = [(lines.index(s), int(s.split(' ')[-1])) for s in FreeDiskSpaceLines ]
        VideoCaptureDeviceLines = filter(lambda x: 'PageTaskAndVideo Using video capture device' in x, lines)
        VideoCaptureDevices = [(lines.index(s), s.split('device')[1]) for s in VideoCaptureDeviceLines ]

        UploadsInProgressLines = filter(lambda x: 'UploadsInProgress' in x, lines)
        UploadsInProgress = [(lines.index(s), s.split('=')[-1]) for s in UploadsInProgressLines ]

        UploadsCompletedLines = filter(lambda x: 'Upload completed:' in x, lines)
        UploadsCompleted = [(lines.index(s), s.split(':')[-1]) for s in UploadsCompletedLines ]

        ToolIdLines = filter(lambda x: 'New ToolId:' in x, lines)
        ToolIds = [(lines.index(s), s.split('New ToolId:')[-1]) for s in ToolIdLines ]

        ToolIdsUnique = (int(x.split(' ')[-1], 16) for x in ToolIdLines)
        ToolIdsUnique = list(set(ToolIdsUnique))
        ToolIdsUnique = sorted(ToolIdsUnique)
        ToolIdsUnique = [(0, '%08X' % tool) for tool in ToolIdsUnique]

        ErrorLines = filter(lambda x: '|Error|' in x, lines)
        Errors = [(lines.index(s), s.split('|Error|')[-1]) for s in ErrorLines ]

        PerformingHeartbeatLines = filter(lambda x: 'Performing heartbeat' in x, lines)
        PerformingHeartbeats = [(lines.index(s), s.split('Performing heartbeat')[-1]) for s in PerformingHeartbeatLines ]

        UpdatedToolDatabaseLines = filter(lambda x: 'Updated tool database' in x, lines)
        UpdatedToolDatabases = [(lines.index(s), s.split('Updated tool database')[-1]) for s in UpdatedToolDatabaseLines ]
        
        UploaderEnabledLines = filter(lambda x: 'UploaderEnabled' in x, lines)
        UploaderEnabled = [(lines.index(s), s.split('UploaderEnabled')[-1]) for s in UploaderEnabledLines]


        return {'EdgeId': edgeId,  
                'Startups': Startups, 
                'EdgeVersions': EdgeVersions, 'ClrVersions': ClrVersions, 
                'FreeDiskSpace': FreeDiskSpaces, 
                'VideoCaptureDevices': VideoCaptureDevices, 
                'ToolIds' : ToolIds,
                'ToolIdsUnique' : ToolIdsUnique,
                'ToolDatabaseUpdates': UpdatedToolDatabases,
                'UploadsInProgress': UploadsInProgress, 'UploadsCompleted': UploadsCompleted,
                'Errors': Errors,
                'PerformingHeartbeat': PerformingHeartbeats,
                'UploaderEnabled' : UploaderEnabled
                }
    

    def _printFragment (self, i, lines, skipRepeats = True):
        '''
        print a tuple. If value is the same as the last one, supress it
        '''
        output = self._mergeFragment (i, lines, skipRepeats)
        for o in output:
            print o

    def _mergeFragment (self, eventList, lines, skipRepeats = True):
        '''
        convert a the lines section (date and time) with the detected instance data. 
        Optional: If value is the same as the last one, supress it
        '''
        last = None
        output = []
        for k in eventList:
            line, value = k[0], k[1]
            if value != last:
                output.append('{0}   {1}'.format(lines[line][0:22], value))
            last = value if skipRepeats else None
        return output
   
    def _toJson (self, eventDict, lines, skipRepeats):
        '''
        convert to json format
        '''
        output = {}
        for key in eventDict:
            if type(eventDict[key]) == type(list()):
                fragment = self._mergeFragment (eventDict[key], lines, skipRepeats)
            else:
                fragment = eventDict[key] 
            output[key] = fragment 
        return json.dumps(output, indent=4, sort_keys=True)

    def printLog (self, d, lines, skipRepeats = True):
        '''
        print a parsed log.
        '''
        print '\n\nEDGE Id: ', d['EdgeId']

        print '\nEdge Versions:'
        self._printFragment(d['EdgeVersions'], lines, skipRepeats)

        print '\nClr Versions:'
        self._printFragment(d['ClrVersions'], lines, skipRepeats)

        print '\nTool Ids:'
        self._printFragment(d['ToolIds'], lines, skipRepeats)

        print '\nStartups:'
        self._printFragment(d['Startups'], lines, skipRepeats)

        print '\nFree Disk Space:'
        self._printFragment(d['FreeDiskSpaces'], lines, skipRepeats)
               
        print '\nVideo Capture Devices and Formats:'
        self._printFragment(d['VideoCaptureDevices'], lines, skipRepeats)
               
        print '\nUploads Completed:'
        self._printFragment(d['UploadsCompleted'], lines, skipRepeats)
               
        print '\nErrors:'
        self._printFragment(d['Errors'], lines, skipRepeats)

# ---------------------------------------------------------------------------------------------------------------------
# The point of it all.  External users should call this one function
# ---------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getMachineLogsAsJson(edgeId, start, end, skipRepeats = True, useTestBucket = False):
        '''
        get machine logs for a range of dates as Json.
        '''
        elp = edgeLogProcessor(useTestBucket)
        sortedLines = elp.getMachineLogContentsForDateRange (edgeId, start, end)
        output = elp.processMachineLog (edgeId, sortedLines)
        #elp.printLog (output, sortedLines, False)
        jsonOutput = elp._toJson (output, sortedLines, skipRepeats)
        return jsonOutput

# ---------------------------------------------------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def testEdgeLogProcessor():
        '''
        check the date conversion routine for .txt, .log, leading and no leading slash, 
        with and without 'Log' prepending
        '''
        elp = edgeLogProcessor()
        f1 = '/edge0/2012/06/25.15.16.29.170.0.txt'
        assert str(elp.getFileDateFromKey(f1)) == '2012-06-25 15:16:29'
        assert '0' == elp.edgeIdFromLogFile(f1)

        t1 = elp.getFileDateFromKey('/edge0/2012/06/25.15.16.29.170.0.log')
        assert str(t1) == '2012-06-25 15:16:29'
        t1 = elp.getFileDateFromKey('edge0/2012/06/25.15.16.29.170.0.log')
        assert str(t1) == '2012-06-25 15:16:29'
        t1 = elp.getFileDateFromKey('/Logs/edge3/2012/10.01.11.54.23.txt')
        assert str(t1) == '2012-10-01 11:54:23'
        f1 = 'Logs/edge12/2012/10.01.11.54.23.txt'
        assert str(elp.getFileDateFromKey(f1)) == '2012-10-01 11:54:23'
        assert '12' == elp.edgeIdFromLogFile(f1)

        filenames = elp.getMachineLogFilenames('Logs/edge0/2012/10')
        assert len(filenames) == 45

        txt = elp.getMachineLogContents('/Logs/edge3/2012/10.01.11.54.23.txt')
        assert len(txt) == 84

        rangeFilenames= elp.getMachineLogFilenamesForDateRange (0, datetime(2012,6,1), datetime(2012,11,30))
        assert len(rangeFilenames) == 518

        sortedLines = elp.getMachineLogContentsForDateRange (0, datetime(2012,11,20), datetime(2012,11,30))
        print len (sortedLines)

        output = elp.processMachineLog (0, sortedLines)
        elp.printLog (output, sortedLines)



# ---------------------------------------------------------------------------------------------------------------------
# Debug and Testing
# ---------------------------------------------------------------------------------------------------------------------

#if __debug__:

    #skipRepeats = True
    #for edgeId in range (8, 9):
    #    jsonOutput = edgeLogProcessor.getMachineLogsAsJson(edgeId, datetime(2012,11,15), datetime(2012,12,31), skipRepeats)
    #    print jsonOutput

    #edgeLogProcessor.testEdgeLogProcessor()

    #print "hiho"





