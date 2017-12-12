#!/usr/bin/env python2
#
# Takes a regular snapshot of ALL VMs in the pool (xenserver)
# - tested on xenserver 6.5
# - must be on master pool host
# 
# Consult the help text for more details on functionality.
#
# Copyright (C) 2017 Tomaso Dessi'
#
# License:
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###

import commands, time, sys
from optparse import OptionParser

def onMaster(file):
   try:
     poolFile = open(file, 'r')
     poolFileContent = poolFile.read().rstrip("\n")
     poolFile.close()
     if poolFileContent == "master":
        return True
     else:
        return False
   except IOError, (errno, strerror):
      print "I/O error on file %s (%s): %s" % (file,errno, strerror)
      sys.exit(1)
   except:
      print "Unexpected error:", sys.exc_info()[0]
      raise

def getVmsOnPool():
   result = []
   cmd = "xe vm-list is-control-domain=false is-a-snapshot=false is-a-template=false power-state=running"
   status, output = commands.getstatusoutput(cmd)
   if status == 0:
      for vm in output.split("\n\n\n"):
         lines = vm.splitlines()
         uuid = lines[0].split(":")[1][1:]
         name = lines[1].split(":")[1][1:]
         result += [(uuid, name)]
      return result
   else:
      return None

def getVmsOnHost(XenHostUUID):
   result = []
   cmd = "xe vm-list is-control-domain=false is-a-snapshot=false is-a-template=false power-state=running resident-on=%s" % XenHostUUID
   status, output = commands.getstatusoutput(cmd)
   if status == 0:
      for vm in output.split("\n\n\n"):
         lines = vm.splitlines()
         uuid = lines[0].split(":")[1][1:]
         name = lines[1].split(":")[1][1:]
         result += [(uuid, name)]
      return result
   else:
      return None

def take_snapshot(uuid, timestamp, name):
   cmd = "xe vm-snapshot uuid=" + uuid + " new-name-label=" + timestamp + "_" + name
   status, output = commands.getstatusoutput(cmd)
   if status == 0:
      return output
   else:
      return None

def UUIDbyHostName():
   result = {}
   cmd = "xe host-list"
   output = commands.getoutput(cmd)
   for h in output.split("\n\n\n"):
      lines = h.splitlines()
      uuid = lines[0].split(":")[1][1:]
      name = lines[1].split(":")[1][1:]
      result[name]= uuid
   return result

## MAIN

def main():
   parser = OptionParser()
   parser.add_option("--host", dest="xhostname",
                  action="store", type="string",help="take snapshots only on given XEN host (the default is on all hosts in the pool")
   parser.add_option("--pool-conf-file", dest="poolFile",
                  action="store", type="string",default="/etc/xensource/pool.conf",help="full path of pool.conf file (default /etc/xensource/pool.conf)")
   (options, args) = parser.parse_args()

   # if not on master host of the pool exit
   if not onMaster(options.poolFile):
      print "you are not on master host of pool, exiting"
      sys.exit(1)
     
   # set a dict for hosts in the pool (by name)
   xhost = UUIDbyHostName()

   # get timestamp for snapshot name (es 20171211-1551_s01d0101)
   timestamp = time.strftime("%Y%m%d-%H%M", time.gmtime())
   # get vm list
   if options.xhostname:
      if options.xhostname in xhost:
         # get uuid of selected host
         uuidHost=xhost[options.xhostname]
         # get vm list in selected host
         vms = getVmsOnHost(uuidHost)
         if vms is None:
            print "ERROR: empty vm list"
            sys.exit(1)
      else:
         print "invalid hostname on current pool"
         sys.exit(1)
   else:
      # get vm list in ALL hosts
      vms = getVmsOnPool()
      if vms is None:
          print "ERROR: empty vm list"
          sys.exit(1)
   
   # go!
   for (uuid, name) in vms:
      snapUuid=take_snapshot(uuid, timestamp, name)
      if snapUuid is None:
         print "ERROR: empty snapshot UUID"
         sys.exit(1)
      else:
         print "created snapshot %s (UUID=%s) for vm %s" % (timestamp + "_" + name,snapUuid,name)
      

if __name__ == "__main__":
        main()
