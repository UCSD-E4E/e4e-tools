#!/usr/bin/env python

from pymavlink import mavutil

def bin2log(bin_filename, log_filename):
	mavmaster = mavutil.mavlink_connection(bin_filename)
	logfile = open(log_filename, 'w')
	while True:
		msg = mavmaster.recv_match()
		if msg is None:
			break
		logfile.write('%s, '% msg.get_type())
		for field in xrange(len(msg.get_fieldnames()) - 1):
			logfile.write('%s, '% msg.to_dict()[msg.get_fieldnames()[field]])
		logfile.write('%s\n'% msg.to_dict()[msg.get_fieldnames()[len(msg.get_fieldnames()) - 1]])


def main():
	bin_filename = '5.BIN'
	log_filename = '5.log'
	bin2log(bin_filename, log_filename)

if __name__ == '__main__':
	main()