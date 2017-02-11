#!/usr/bin/env python

def bin2log(bin_filename, log_filename):
	binfile = open(bin_filename, 'rb')
	logfile = open(log_filename, 'w')

def main():
	bin_filename = '8.BIN'
	log_filename = '8.log'
	bin2log(bin_filename, log_filename)

if __name__ == '__main__':
	main()