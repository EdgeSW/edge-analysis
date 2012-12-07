# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from flask import Flask
import flask
from flask import request
import json

app = Flask(__name__)
app.debug = True

@app.route('/computehealth/',methods=['GET', 'POST'])
def hello_world():
    #args = flask.request.args
    
    
    
    '''
    if request.method == 'POST':  
        snsmessage = json.loads(request.data)
        if False:
        
            subj = snsmessage["Subject"]
            mess = snsmessage["Message"]
        
            print "Subject: " + subj #Store these in a local log file??
            print "Message: " + mess
        
        print snsmessage
        return 'Hello World!\n' 
    '''
    return 'Hello World!\n'




if __name__ == '__main__':
    app.run(debug=True, use_debugger=True, use_reloader=True,host='0.0.0.0',port=8080)

# <codecell>


