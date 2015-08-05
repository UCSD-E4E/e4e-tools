#!/bin/bash
log="tmp_log.log"
if [ "$#" -eq "1" ]
then
	log=$1
fi
while [ 1 ]
do
	data=`cat /sys/class/hwmon/hwmon0/temp1_input`
	time=`date +%s`
	echo "$time $data" >> $log
	# Record period below
	sleep 3
done
