***UDEV RULES***
These rules files dictate how linux connects with hardware.
The biggest use is to modify read/write permissions automatically
since by default, devices are only write-able by root.

To use these rules files, run 
'sudo cp rulesfilename.rules /etc/udev/rules.d/'

then 
'sudo udevadm control --reload-rules'.

*****************
