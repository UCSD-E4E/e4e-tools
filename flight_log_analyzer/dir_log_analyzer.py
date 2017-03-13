#!/usr/bin/env python
from bin_log_analyzer import analyzeFlightLog
from bin_log_analyzer import decodeError
import argparse
import os
import numpy as np

def main():
    parser = argparse.ArgumentParser(description = 'E4E Ardupilot Autopilot '
            'Flight Log Analyzer')
    parser.add_argument('-i', '--input', help = 'Input directory',
            metavar = 'dir', dest = 'dir', default = './')
    parser.add_argument('-p', '--pilot', default = '', help = 'Pilot Name')
    parser.add_argument('-C', '--certificate', default = '', help = 'Pilot Certificate')
    parser.add_argument('-R', '--registration', default = '', help = 'Aircraft Registration')

    args = parser.parse_args()
    inputDir = args.dir
    pilotname = args.pilot
    pilotcert = args.certificate
    acftreg = args.registration
    total_time_in_air = 0
    retvals = []
    maxLat = -180.0
    maxLon = -180.0
    minLon = 180.0
    minLat = 180.0
    modes = set()
    errors = []

    for file in os.listdir(inputDir):
        if os.path.splitext(os.path.basename(file))[1].lower() in ['.bin', '.log', '.tlog', '.px4log']:
            retval = analyzeFlightLog(os.path.join(inputDir, file), pilotname, pilotcert, acftreg)
            total_time_in_air = total_time_in_air + retval['timeInAir']
            maxLat = np.amax([maxLat, retval['maxLat']])
            maxLon = np.amax([maxLon, retval['maxLon']])
            minLon = np.amin([minLon, retval['minLon']])
            minLat = np.amin([minLat, retval['minLat']])
            modes.union(retval['flightModes'])
            errors.extend(retval['errors'])
            retvals.append(retval)
    print('Total Time in Air: %.2f' % total_time_in_air)
    print("Flight Area: %.6f, %.6f x %.6f, %.6f" % (retval['maxLat'], retval['maxLon'], retval['minLat'], retval['minLon']))
    print("Flight Modes: ")
    for i in modes:
        print('\t%s' % i)

    print('Errors: %d' % len(errors))
    for error in errors:
        print('        %s' % (decodeError(error.to_dict()['Subsys'], error.to_dict()['ECode'])))


if __name__ == '__main__':
    main()