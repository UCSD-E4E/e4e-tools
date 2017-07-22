#!/bin/bash
log="cpu_log.log"
if [ "$#" -eq "1" ]
then
	log=$1
fi
while [ 1 ]
do
	data=`head -n 1 /proc/stat`
	time=`date +%s`
	echo "$time $data" >> $log
	# record period below
	sleep 0.5
done
