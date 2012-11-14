# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from flask import Flask
import flask
from flask import request
import json

app = Flask(__name__)
app.debug = True

@app.route('/sns/',methods=['GET', 'POST'])
def hello_world():
    #args = flask.request.args

    
    if request.method == 'POST':
            
        snsmessage = json.loads(request.data)
        
        subj = snsmessage["Subject"]
        mess = snsmessage["Message"]
        
        print "Subject: " + subj
        print "Message: " + mess
        #Store these in a local log file??
        return 'Hello World!\n' 
        

if __name__ == '__main__':
    app.run(debug=True, use_debugger=True, use_reloader=True,host='0.0.0.0',port=8080)

# <codecell>


