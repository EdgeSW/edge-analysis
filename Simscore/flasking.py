# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from flask import Flask
import flask
from flask import request
import os

app = Flask(__name__)
app.debug = True


def tail(fname, window):
    """Read last N lines from file fname."""
    f = open(fname, 'r')
    
    BUFSIZ = 1024
    f.seek(0, os.SEEK_END)
    fsize = f.tell()
    block = -1
    data = ""
    done = False
    
    while not done:
        step = (block * BUFSIZ)
        if abs(step) >= fsize:
            f.seek(0)
            done = True
        else:
            f.seek(step, os.SEEK_END)
        data = f.read().strip()
        if data.count('\n') >= window:
            break
        else:
            block -= 1
    
    return data.splitlines()[-window:]

def print_lines(lines):
    out = ""
    for line in lines:
        out += (line+'<br/>')
    return out



@app.route('/computehealth/',methods=['GET', 'POST'])
def compute_tail():
    #args = flask.request.args
    
    window = 40
    fname='C:\\Users\\Tyler\\ComputeFails.log'
    
    lines = tail(fname, window)
    return print_lines(lines)    

@app.route('/shiphealth/',methods=['GET', 'POST'])
def ship_tail():
    #args = flask.request.args
    
    window = 40
    fname='C:\\Users\\Tyler\\ShipFails.log'
    
    lines = tail(fname, window)
    return print_lines(lines)    


if __name__ == '__main__':
    app.run(debug=True, use_debugger=True, use_reloader=True,host='0.0.0.0',port=8080)

# <codecell>


