#!/usr/bin/env python3

from __main__ import *
import os
from XRootD import client
from XRootD.client.flags import DirListFlags, StatInfoFlags

def walk_xrootd(path, host, host_obj=None):
  """ Works just like os.walk but for paths on an xrootd server.
      Returned paths do not include the server information.
  """
  if not host_obj:
    host_obj = client.FileSystem(host)
  # List the current directory
  status, listing = host_obj.dirlist(path, DirListFlags.STAT)
  # Sort the directories and files into two lists
  files = []
  dirs = []
  for entry in listing:
    if entry.statinfo.flags & StatInfoFlags.IS_DIR:
      dirs.append(entry.name)
    else:
      files.append(entry.name)
  # Return the directory information
  yield (path, dirs, files)
  # Loop over all sub-directories
  for dname in dirs:
    next_path = os.path.join(path, dname)
    yield from walk_xrootd(next_path, host, host_obj)

DAY=input('Which day do you wanna analyse? (ex. 2017_12_15) -> ')
HOST = "gfe02.grid.hep.ph.ic.ac.uk"
BASE = "/pnfs/hep.ph.ic.ac.uk/data/solid/solidexperiment.org/Data/phase1_BR2/DAQ/days/"+DAY+"/RO-data/"

day=[DAY]
headlist, headinput = [], []
for path, dnames, fnames in walk_xrootd(BASE, HOST):
  for fname in fnames:
    full_path = os.path.join(path, fname)
    full_path = full_path.replace('/pnfs/hep.ph.ic.ac.uk/data/solid','')
    headlist+=["LFN:%s" % (full_path)]
    subfull = '/solidexperiment.org/Data/phase1_BR2/DAQ/days/'+DAY+'/RO-data/'
    full_path = full_path.replace(subfull,'')
    headinput+=["%s" % (full_path)]
