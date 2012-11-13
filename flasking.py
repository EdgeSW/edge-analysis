# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from flask import Flask
import flask

app = Flask(__name__)
app.debug = True

@app.route('/sns/')
def hello_world():
    args = flask.request.args
    #args = request.args.get()
    print args
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True, use_debugger=True, use_reloader=True,host='0.0.0.0',port=8081)

# <codecell>


