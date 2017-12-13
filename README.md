# xenserver_scripts

snapPool.py: automated snapshot creation

 Takes a snapshot for all VMs in the xenserver pool, must run on master host of the pool
 
 Alternatively you can specify a specific host so the snapshots will be taken only on VMs on that host of the pool
 
```
 $ ./snapPool.py -h
 Usage: snapPool.py [options]

 Options:
  -h, --help            show this help message and exit
  --host=XHOSTNAME      take snapshots only on given XEN host (the default is
                        on all hosts in the pool)
  --pool-conf-file=POOLFILE
                        full path of pool.conf file (default
                        /etc/xensource/pool.conf)
  -n                    dry run - simulate snapshots
  --vm-prefix=VMPREFIX  name-label prefix of vms to include
  --vm-suffix=VMSUFFIX  name-label suffix of vms to include
```
