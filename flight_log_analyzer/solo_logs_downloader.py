#!/usr/bin/env python
import pysftp
import os
import time
import datetime
import pytz
from  dateutil import parser as dateparser
import sys
def leap(date):
	"""
	Return the number of leap seconds since 6/Jan/1980
	:param date: datetime instance
	:return: leap seconds for the date (int)
	"""
	if date < datetime.datetime(1981, 6, 30, 23, 59, 59):
		return 0
	leap_list = [(1981, 6, 30), (1982, 6, 30), (1983, 6, 30),
				 (1985, 6, 30), (1987, 12, 31), (1989, 12, 31),
				 (1990, 12, 31), (1992, 6, 30), (1993, 6, 30),
				 (1994, 6, 30), (1995, 12, 31), (1997, 6, 30),
				 (1998, 12, 31), (2005, 12, 31), (2008, 12, 31),
				 (2012, 6, 30), (2015, 6, 30), (2016, 12, 31)]
	leap_dates = map(lambda x: datetime.datetime(x[0], x[1], x[2], 23, 59, 59),
					 leap_list)
	for j in xrange(len(leap_dates[:-1])):
		if leap_dates[j] < date < leap_dates[j + 1]:
			return j + 1
	return len(leap_dates)

def getCallback(iteration, total):
	"""
	Call in a loop to create terminal progress bar
	@params:
		iteration   - Required  : current iteration (Int)
		total       - Required  : total iterations (Int)
		prefix      - Optional  : prefix string (Str)
		suffix      - Optional  : suffix string (Str)
		decimals    - Optional  : positive number of decimals in percent complete (Int)
		length      - Optional  : character length of bar (Int)
		fill        - Optional  : bar fill character (Str)
	"""
	decimals = 1
	prefix = ''
	suffix = ''
	length = 30
	fill = '*'
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
	# Print New Line on Complete
	if iteration == total: 
		print()

if not os.path.isdir('logs'):
	os.mkdir('logs')

cnopt = pysftp.CnOpts()
cnopt.hostkeys = None
connection = pysftp.Connection('10.1.1.10', username = 'root', password = 'TjSDBkAu', cnopts = cnopt)
connection.chdir('/log/dataflash')
files = connection.listdir()
file_attrs = connection.listdir_attr()
# today = datetime.datetime.fromtimestamp(int(time.time()), pytz.utc).date()
today = dateparser.parse('2017.08.31').date()
print(today)
for i in xrange(len(file_attrs) - 1):
	filetime = datetime.datetime.fromtimestamp(file_attrs[i].st_mtime, pytz.utc)
	filedate = filetime.date()
	if today == filedate:
		print(files[i])
		connection.get(files[i], localpath=os.path.join('.', 'logs', files[i]), callback = getCallback)
connection.close()