#!/usr/bin/env python3
from DIRAC.Core.Base import Script
Script.parseCommandLine()
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Interfaces.API.Job import Job

with open('lfn.txt') as f:
    headlist = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
headlist = [x.strip() for x in headlist]
#print(headlist)

with open('input.txt') as f:
    headinput = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
headinput = [x.strip() for x in headinput]
#print(headinput)

with open('days.txt') as f:
    days = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
days = [x.strip() for x in days]
print('You have submitted ', len(headlist), ' jobs for the day ', days)

jn=0
for ii in range(len(headlist)):
  jn+=1
  sublist=[headlist[ii]]
  sublist1=[jn]
  sublist2=[headinput[ii]]
  sublist3=[days[0]]
  j = Job()
  j.setName("SoLid_data_%(argjn)s")
  j.setPlatform('ANY')
  j.setDestination('LCG.UKI-LT2-IC-HEP.uk')
  #j.setDestination('LCG.BEgrid-ULB-VUB.be')
  j.setInputSandbox(['dataOnGrid.sh','onlineMonitoringBR2.txt ','baselines.root'])
  j.setParameterSequence('InputData', sublist, addToWorkflow='ParametricInputData')
  j.setParameterSequence('argjn', sublist1, addToWorkflow=False)
  j.setParameterSequence('argli', sublist2, addToWorkflow=False)
  j.setParameterSequence('argdy', sublist3, addToWorkflow=False)
  j.setExecutable('dataOnGrid.sh', arguments='%(argjn)s %(argli)s %(argdy)s')
#  Dirac().submit(j)
#  print(sublist,sublist1, sublist2, sublist3)

