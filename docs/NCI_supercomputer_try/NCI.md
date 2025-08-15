---
layout: default
title: "Guide to this brms model recovery site"
---


## Log in and load modules

ssh ha3155@gadi.nci.org.au

See R

ls /apps/R/4.5.0

README in that directory ("more /apps/R/4.5.0/README.nci")
says to execute the following probably to access packages:

module load intel-compiler-llvm/2025.0.4
module load intel-mkl/2025.0.1

Running
module list
shows that those loaded

## Installing R packages

https://sydneyuni.atlassian.net/wiki/spaces/RC/pages/3448733944/Sydney+Scheme

Install them locally and then transfer with some kind of login script?. 
He seemed to say there was instructions at opus.nci.org.au

But I can't find anything, so I need to email:
nci-sydney.scheme@sydney.edu.au



## Compiling packages

Some packages only compile using gcc.
Modify ~/.R/Makevars with C and CXX flags as below to force compilation using gc
c.

CXX=g++
CXX11=g++
CXX14=g++
CXX17=g++
CC=gcc




## Weekly drop-in sessions: moving from Artemis to NCI Gadi

These online sessions are led by the high-performance computing (HPC) experts at Sydney Informatics Hub. Get help and ask any questions you have about onboarding to NCI.

Date / time
Topic
Link
Weekly recurring drop-in session via zoom
(Wednesdays 12-12.30pm until 30 July)
Moving from Artemis to NCI Gadi
Join via zoom here.
