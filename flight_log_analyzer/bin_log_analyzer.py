#!/usr/bin/env python

from pymavlink import mavutil
from pymavlink.dialects.v10 import ardupilotmega as mavlink
import argparse
import numpy as np
import os
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
    leap_dates = map(lambda x: datetime.datetime(x[0], x[1], x[2], 23, 59, 59),
                     leap_list)
    for j in xrange(len(leap_dates[:-1])):
        if leap_dates[j] < date < leap_dates[j + 1]:
            return j + 1
    return len(leap_dates)

def main():
    parser = argparse.ArgumentParser(description = 'E4E Ardupilot Autopilot '
            'Flight Log Analyzer')
    parser.add_argument('-i', '--input', help = 'Input flight log',
            metavar = 'log', dest = 'log', default = None)
    parser.add_argument('-s', '--split_log', action = 'store_true',
            help = 'If present, split log into individual flights',
            dest = 'split_log')

    args = parser.parse_args()
    fileName = args.log
    split_log = args.split_log

    if fileName is None:
        # fix
        return
    else:
        if os.path.splitext(os.path.basename(fileName))[1].lower() != '.bin':
            print("Error: Input .bin files only!")
            return

    readmeName = os.path.splitext(fileName)[0] + '.rpt'

    timeInAir = 0
    prevCurr = -1
    FMT = []
    PARM = []
    takeoff_seq = []
    landing_seq = []
    seqNum = 0
    modes = set()
    maxLat = -180.0
    maxLon = -180.0
    minLon = 180.0
    minLat = 180.0
    takeoff_times = []
    flying = False
    errors = []
    lastGPS = -1
    takeoffWithoutGPS = 0

    mav_master = mavutil.mavlink_connection(fileName)
    while True:
        msg = mav_master.recv_match(blocking = False)
        if msg is None:
            break
        if msg.get_type() == 'FMT':
            FMT.append(msg)
            pass
        elif msg.get_type() == 'PARM':
            PARM.append(msg)
            pass
        elif msg.get_type() == 'GPS':
            if msg.to_dict()['Status'] >= 3:
                gps_time = int(msg.to_dict()['TimeMS'])
                gps_week = int(msg.to_dict()['Week'])
                apm_time = int(msg.to_dict()['T'])
                offset = gps_time - apm_time
                lastGPS = seqNum
                maxLat = np.max((msg.to_dict()['Lat'], maxLat))
                maxLon = np.max((msg.to_dict()['Lng'], maxLon))
                minLat = np.min((msg.to_dict()['Lat'], minLat))
                minLon = np.min((msg.to_dict()['Lng'], minLon))
        elif msg.get_type() == 'CURR':
            if int(msg.to_dict()['Curr']) > 200:
                flying = True
                if prevCurr != -1:
                    timeInAir = timeInAir + int(msg.to_dict()['TimeMS']) - prevCurr
                    prevCurr = int(msg.to_dict()['TimeMS'])
                else:
                    prevCurr = int(msg.to_dict()['TimeMS'])
                    if lastGPS != -1:
                        secs_in_week = 604800
                        gps_epoch = datetime.datetime(1980, 1, 6, 0, 0, 0)
                        date_before_leaps = (gps_epoch + datetime.timedelta(
                            seconds = gps_week * secs_in_week + (prevCurr + 
                            offset) / 1e3))
                        date = (date_before_leaps - datetime.timedelta(seconds = 
                            leap(date_before_leaps)))
                        print("Takeoff at %s UTC" % (date.strftime('%Y-%m-%d %H:%M:%S')))
                        takeoff_seq.append(lastGPS)
                        takeoff_times.append(date)
                    else:
                        print("Takeoff without GPS fix!")
                        takeoffWithoutGPS = takeoffWithoutGPS + 1
            else:
                flying = False
                if prevCurr != -1:
                    landing_seq.append(seqNum)
                prevCurr = -1
        elif msg.get_type() == 'MODE':
            if flying:
                modes.add(mavutil.mode_mapping_acm[msg.to_dict()['ModeNum']])
        elif msg.get_type() == 'ERR':
            errors.append(msg)
        seqNum = seqNum + 1
    print('')
    timeInAir = timeInAir / 1e3 / 60 / 60
    print('Time In Air: %.2f' % timeInAir)

    print("Flight Area: %.6f, %.6f x %.6f, %.6f" % (maxLat, maxLon, minLat, minLon))

    print("Flight Modes: ")
    for i in modes:
        print(i)


    readmeFile = open(readmeName, 'w')
    readmeFile.write('Pilot: \n')
    readmeFile.write('Certificate #: \n')
    readmeFile.write('Aircraft Registration: \n')
    readmeFile.write('Flight Operations Area: %3.8f, %3.8f x %3.8f, %3.8f\n' % (maxLat, maxLon, minLat, minLon))
    readmeFile.write('Time In Air: %.2f\n' % timeInAir)

    readmeFile.write('Takeoffs: %d\n' % len(takeoff_times))
    for i in takeoff_times:
        readmeFile.write('          %s UTC\n' % i.strftime('%Y-%m-%d %H:%M:%S'))
        
    if takeoffWithoutGPS != 0:
        readmeFile.write("Takeoffs without GPS: %d\n" % takeoffWithoutGPS)

    readmeFile.write('Flight Modes: ')
    for i in modes:
        readmeFile.write('%s, ' % i)
    readmeFile.write('\n')
    readmeFile.write('Errors: ')
    if len(errors) == 0:
        readmeFile.write('None\n')
    else:
        readmeFile.write('%d\n' % len(errors))
        for error in errors:
            readmeFile.write('        %d %d\n' % (error.to_dict()['Subsys'], error.to_dict()['ECode']))
    readmeFile.close()


if __name__ == '__main__':
    main()
