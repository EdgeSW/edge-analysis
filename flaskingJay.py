from flask import Flask
import flask
from flask import request
from datetime import datetime
import json
from edgeLogProcessor import edgeLogProcessor
from crossdomain import crossdomain

app = Flask(__name__)
app.debug = True

@app.route('/logs',methods=['GET', 'POST'])
@crossdomain(origin='*')
def logs():
    args = request.args

    skipRepeats = True
    if 'skipRepeats' in args:
        skipRepeats = args['skipRepeats']

    edgeId = 4
    if 'edgeId' in args:
        edgeId = args['edgeId']

    start = datetime.now()
    if 'start' in args:
        startTime = args['start']
        print startTime
        mdy = startTime.split('-')
        start = datetime (int(startTime[0:4]), int(startTime[4:6]), int(startTime[6:8]))

    end = datetime.now()
    if 'end' in args:
        endTime = args['end']
        mdy = endTime.split('-')
        end = datetime (int(endTime[0:4]), int(endTime[4:6]), int(endTime[6:8]))

 #   if request.method == 'GET':
#    jsonOutput = edgeLogProcessor.getMachineLogsAsJson(edgeId, datetime(2012,11,15), datetime(2012,12,31), skipRepeats)
    jsonOutput = edgeLogProcessor.getMachineLogsAsJson(edgeId, start, end, skipRepeats)
    return jsonOutput        
    #return json.dumps ("Hello world")

if __name__ == '__main__':
 #   app.run(debug=True, use_debugger=True, use_reloader=True,host='0.0.0.0',port=8080)
    app.run(debug=True, use_debugger=True, use_reloader=True,host='0.0.0.0', port=8082)
    #app.run()

# <codecell>


