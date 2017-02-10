#!/usr/bin/env python

import numpy as np
import argparse
import Tkinter as tk
import tkFileDialog
import datetime

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
                 (2012, 6, 30), (2015, 6, 30)]
    leap_dates = map(lambda x: datetime.datetime(x[0], x[1], x[2], 23, 59, 59), leap_list)
    for j in xrange(len(leap_dates[:-1])):
        if leap_dates[j] < date < leap_dates[j + 1]:
            return j + 1
    return len(leap_dates)

def main():
	root = tk.Tk()
	root.withdraw()
	root.update()

	options = {}
	options['filetypes'] = [('MAVLINK Log Files', '.log')]

	# fileName = tkFileDialog.askopenfilename(**options)
	fileName = '/home/ntlhui/Downloads/8.log'

	if len(fileName) == 0:
		return

	timeInAir = 0;
	prevCurr = -1;

	with open(fileName) as file:
		for line in file:
			elements = [element.strip() for element in line.split(',')]
			if elements[0] == 'GPS':
				gps_time = int(elements[2])
				gps_week = int(elements[3])
				apm_time = int(elements[13])
				offset = gps_time - apm_time;
			if elements[0] == 'CURR':
				if int(elements[4]) > 200:
					if prevCurr != -1:
						timeInAir = timeInAir + int(elements[1]) - prevCurr
						prevCurr = int(elements[1])
					else:
						prevCurr = int(elements[1])
						# print("First sample: %.2f" % (prevCurr / 1000.0 / 60.0))
						secs_in_week = 604800
						gps_epoch = datetime.datetime(1980, 1, 6, 0, 0, 0)
						date_before_leaps = gps_epoch + datetime.timedelta(seconds=gps_week * secs_in_week + (prevCurr + offset) / 1000.0)
						date = date_before_leaps - datetime.timedelta(seconds=leap(date_before_leaps))
						print("Takeoff at %s UTC" % (date.strftime('%Y-%m-%d %H:%M:%S')))
				else:
					# if prevCurr != -1:
					# 	print("Last sample: %.2f" % (prevCurr / 1000.0 / 60.0))
					prevCurr = -1

	timeInAir = timeInAir / 1000.0 / 60 / 60
	print("Time In Air: %.2f" % timeInAir)

if __name__ == '__main__':
	main()