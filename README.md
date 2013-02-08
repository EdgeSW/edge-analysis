Developed for Simulab Corporation by Tyler Hartley
EDGE System Error Checking, Intelligent Response, and HMM Training

NOTE: This repository is a merge of two previous repos - HMM-Train and Simscore-Computing. 

HMM covers all code necessary to 
a) filter and scrub EDGE sensors into proper features, 
b) quantize that data into compressed codebooks/codewords,
c) segment data into appropriate repetitive tasks (grasps),
d) train a hidden markov model to quantify surgical skill

Simscore covers all code necessary to:
a) load, parse data from Amazon S3, SQS, SimpleDB
b) compute/extract validity metrics and metadata from EDGE files
c) ship relevant info to simscore.org as a RESTful application
d) perform a variety of unit tests/reports against edge data

Each is meant to be accessed from its own ipython profile for simple web
editing and testing in-place either locally or on a remote server. Access
HMM through profile=training, access Simscore through profile=computing.

