***UDEV RULES***
These rules files dictate how linux connects with hardware.
The biggest use is to modify read/write permissions automatically
since by default, devices are only write-able by root.

To use these rules files, run 
'sudo cp rulesfilename.rules /etc/udev/rules.d/'

then 
'sudo udevadm control --reload-rules'.

Use 10-rct_store.rules to execute a shell script upon insertion of an external 
storage unit.  If the storage unit enumerates the same every time (i.e. 
`/dev/mmcblk0` or `/dev/sde`), then simply replace the device name.  You can 
use the shell script to statically mount the drive somewhere.
*****************
