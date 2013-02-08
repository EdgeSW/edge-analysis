**************************************************
Developed for Simulab Corporation by Tyler Hartley
**************************************************
edge-analysis
=============

*EDGE System Error Checking, Intelligent Response, and HMM Training.....*

**NOTE:** This repository is a merge of two previous repos - HMM-Train and Simscore-Computing.*

HMM
---
HMM covers all code necessary to 

  - filter and scrub EDGE sensors into proper features,
  - quantize that data into compressed codebooks/codewords,
  - segment data into appropriate repetitive tasks (grasps),
  - train a hidden markov model to quantify surgical skill
	
Simscore
--------
Simscore covers all code necessary to:

  - compute/extract validity metrics and metadata from EDGE files
  - ship relevant info to simscore.org as a RESTful application
  - perform a variety of unit tests/reports against edge data
	
Both HMM and Simscore are meant to be accessed from its own ipython profile for simple web 
editing and testing in-place either locally or on a remote server. Access
HMM through profile=training, access Simscore through profile=computing.

fetch
-----
fetch can be thought of as a boto wrapper for specific Edge application. It contains highly
abstracted functions to pull a variety of data types from S3, including raw edge files and
metadata, through a variety of relevant filters. fetch also contains wrapper functions 
necessary to interface with Amazon SQS, used to queue uploaded edge files for processing.



