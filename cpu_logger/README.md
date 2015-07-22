# CPU Logger
This script creates a log of CPU utilization every 3 seconds, with a timestamp, to allow for low-cost monitoring of the CPU load on embedded systems.

The output is a text file (generally cpu_log.log) with the following fields:
[time] cpu [user time] [nice time] [system time] [idle time] [iowait] [irq time] [softirq time] 0 0 0

time is time since Unix epoch (according to the OS time)
user time is time spent doing userspace processes in USER_HZ units
nice time is time spent doing nice processes in USER_HZ units
system time is time spend doing system processes in USER_HZ units
idle time is time idle in USER_HZ units
iowait is time waiting for I/O in USER_HZ units
irw time is time servicing HW IRQ in USER_HZ units
softirq time is time servicing softirq in USER_HZ units

