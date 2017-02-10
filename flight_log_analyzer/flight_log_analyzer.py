#!/usr/bin/env python

import numpy as np
import argparse

def main():
	fileName = '8.log'

	timeInAir = 0;
	prevCurr = -1;

	with open(fileName) as file:
		for line in file:
			elements = [element.strip() for element in line.split(',')]
			if elements[0] == 'CURR':
				if int(elements[4]) > 200:
					if prevCurr != -1:
						timeInAir = timeInAir + int(elements[1]) - prevCurr
						prevCurr = int(elements[1])
					else:
						prevCurr = int(elements[1])
						# print("First sample: %.2f" % (prevCurr / 1000.0 / 60.0))
				else:
					# if prevCurr != -1:
					# 	print("Last sample: %.2f" % (prevCurr / 1000.0 / 60.0))
					prevCurr = -1

	timeInAir = timeInAir / 1000.0 / 60 / 60
	print("Time In Air: %.2f" % timeInAir)

if __name__ == '__main__':
	main()