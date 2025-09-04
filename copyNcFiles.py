#!/usr/bin/env python3

usage = """ 
copyNcFiles
copies data from one NC to the other if 
* a directory has a file named ${copyto.txt}  
* fhe file is newer

- source host: ${NC_URL}
- source user: ${NC_USER}
- source pass: ${NC_PASS}


- target host: ${NC_TARGET_URL}
- target user: ${NC_TARGET_USER}
- target pass: ${NC_TARGET_PASS}


"""

# some constants for you to change
target_name='copyto.txt'

import os
import re
from io import BytesIO

from nc_py_api import Nextcloud


if os.environ['DEBUG_DEVELOP']=='true' :
  import pdb

def get_target_dir(c, copyto):
  return(c.files.download(copyto)).decode('utf-8')  

def handle_dir(c, nc, node, target = False):
  print ("handling ", node.user_path)
  
  if node.is_dir:
    entries= c.files.listdir(node.user_path)
  else:
    entries = c.files.listdir(os.path.dirname(node.user_path))
  
  # look for directory in target
  if not target :
    target = get_target_dir(c, node.user_path)
  else: 
    target = target+'/' + node.name
  try:
    nc.files.listdir(target)
  except:  
    nc.files.mkdir(target)
  #if node.is_dir:  # recurse into that dir
  #  handle_dir(c, nc, node, target = target)
  
  for entry in entries:
    if entry.is_dir:
      if os.environ['DEBUG_DEVELOP']=='true' :
          print ('subdir exists %s', entry.user_path)
      # create nonexisting directory on target
      # found = nc.files.find(["eq", "name", node.user_path])
      handle_dir(c,nc,entry,target)
    else: 
      # all files newer than target need to be copied
      
      # look for files
      try:
        
        targetfile= nc.files.by_path( target + '/' + entry.name)
        # now handle date comparison
        if os.environ['DEBUG_DEVELOP']=='true' :
          print (entry.name, entry.info._last_modified)
          print (targetfile.name, targetfile.info._last_modified)
          if entry.info._last_modified > targetfile.info._last_modified :
            copy_file(c,nc, entry, target + '/' + entry.name)

          ## compare dates and copy when entry is more recent


      except:
        copy_file(c,nc, entry, target + '/' + entry.name)


def copy_file(c, nc, inputfile, output_name):
  
  print(inputfile.user_path, '-->', output_name)
  # buf = BytesIO()
  data = c.files.download(inputfile)
  newfile = nc.files.upload(output_name, data)
  if os.environ['DEBUG_DEVELOP']=='true' :
    pdb.set_trace()






  




def main():
  # source and target clouds
  c = Nextcloud(nextcloud_url=os.environ['C_URL'], nc_auth_user=os.environ['C_USER'], nc_auth_pass=os.environ['C_PASS'])
  nc = Nextcloud(nextcloud_url=os.environ['NC_URL'], nc_auth_user=os.environ['NC_USER'], nc_auth_pass=os.environ['NC_PASS'])
  # only walk through the directories containing a copyto text
  directories=c.files.find(["eq", "name", "copyto.txt"])
  for d in directories:
    handle_dir (c, nc, d)

  




if __name__ == "__main__":
    main()
