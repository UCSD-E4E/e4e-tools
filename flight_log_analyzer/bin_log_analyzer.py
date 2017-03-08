#!/usr/bin/env python

from pymavlink import mavutil
from pymavlink.dialects.v10 import ardupilotmega as mavlink
import argparse
import numpy as np
import os
import datetime
from enum import Enum

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

def decodeError(subsys, ecode):
    if subsys == 1:
        # Never used
        return 'Unknown Error'
    elif subsys == 2:
        return 'Late PPM from from control radio'
    elif subsys == 3:
        if ecode == 0:
            return 'Compass error resolved'
        elif ecode == 1:
            return 'Compass failed to initialize'
        elif ecode == 2:
            return 'Compass failed to read value'
    elif subsys == 4:
        return 'Optical Flow failed to initialize'
    elif subsys == 5:
        if ecode == 0:
            return 'Throttle Failsafe resolved'
        elif ecode == 1:
            return 'Throttle Failsafe triggered'
    elif subsys == 6:
        return 'Battery Failsafe triggered'
    elif subsys == 7:
        if ecode == 0:
            return 'GPS Lock restored'
        elif ecode == 1:
            return 'GPS Failsafe triggered'
    elif subsys == 8:
        if ecode == 0:
            return 'GCS Failsafe resolved'
        elif ecode == 1:
            return 'GCS Failsafe triggered'
    elif subsys == 9:
        if ecode == 0:
            return 'Fence breach resolved'
        elif ecode == 1:
            return 'Fence breach - altitude'
        elif ecode == 2:
            return 'Fence breach - lateral'
        elif ecode == 3:
            return 'Fence breach - altitude and lateral'
    elif subsys == 10:
        return 'Failed to enter mode'
    elif subsys == 11:
        if ecode == 0:
            return 'GPS glitch resolved'
        elif ecode == 2:
            return 'GPS glitch detected'
    elif subsys == 12:
        return 'Crash detected'

    return 'Unknown Error'

class ACFT(Enum):
    UNKNOWN = -1
    SOLO    = 0
    PX4     = 1

def main():
    parser = argparse.ArgumentParser(description = 'E4E Ardupilot Autopilot '
            'Flight Log Analyzer')
    parser.add_argument('-i', '--input', help = 'Input flight log',
            metavar = 'log', dest = 'log', default = None)
    parser.add_argument('-p', '--pilot', default = '', help = 'Pilot Name')
    parser.add_argument('-C', '--certificate', default = '', help = 'Pilot Certificate')
    parser.add_argument('-R', '--registration', default = '', help = 'Aircraft Registration')

    args = parser.parse_args()
    fileName = args.log
    pilotname = args.pilot
    pilotcert = args.certificate
    acftreg = args.registration

    if fileName is None:
        # fix
        return
    else:
        if os.path.splitext(os.path.basename(fileName))[1].lower() not in ['.bin', '.log', '.tlog', '.px4log']:
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
    acft = ACFT.UNKNOWN

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
                if acft == ACFT.SOLO:
                    gps_time = int(msg.to_dict()['TimeMS'])
                    gps_week = int(msg.to_dict()['Week'])
                    apm_time = int(msg.to_dict()['T'])
                elif acft == ACFT.PX4:
                    gps_time = int(msg.to_dict()['GMS'])
                    gps_week = int(msg.to_dict()['GWk'])
                    apm_time = int(msg.to_dict()['TimeUS']) / 1e3
                    
                offset = gps_time - apm_time
                lastGPS = seqNum
                maxLat = np.max((msg.to_dict()['Lat'], maxLat))
                maxLon = np.max((msg.to_dict()['Lng'], maxLon))
                minLat = np.min((msg.to_dict()['Lat'], minLat))
                minLon = np.min((msg.to_dict()['Lng'], minLon))
        elif msg.get_type() == 'CURR':
            if int(msg.to_dict()['Curr']) > 500:
                flying = True
                modes.add(currentMode)
                
                if acft == ACFT.SOLO:
                    msgtimestamp = int(msg.to_dict()['TimeMS'])
                elif acft == ACFT.PX4:
                    msgtimestamp = int(msg.to_dict()['TimeUS']) / 1e3

                if prevCurr != -1:
                    timeInAir = timeInAir + msgtimestamp - prevCurr
                    prevCurr = msgtimestamp
                else:
                    prevCurr = msgtimestamp
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
            currentMode = mavutil.mode_mapping_acm[msg.to_dict()['ModeNum']]
            if flying:
                modes.add(currentMode)
        elif msg.get_type() == 'ERR':
            errors.append(msg)
        elif msg.get_type() == 'MSG':
            version = msg.to_dict()['Message'].split()[1]
            if version == 'solo-1.3.1':
                acft = ACFT.SOLO
            elif version == 'V3.3.3':
                acft = ACFT.PX4
        seqNum = seqNum + 1
    print('')
    timeInAir = timeInAir / 1e3 / 60 / 60
    print('Time In Air: %.2f' % timeInAir)

    print("Flight Area: %.6f, %.6f x %.6f, %.6f" % (maxLat, maxLon, minLat, minLon))

    print("Flight Modes: ")
    for i in modes:
        print(i)

    print('Errors: %d' % len(errors))
    for error in errors:
        print('        %s' % (decodeError(error.to_dict()['Subsys'], error.to_dict()['ECode'])))

    readmeFile = open(readmeName, 'w')
    readmeFile.write('Pilot: %s\n' % pilotname)
    readmeFile.write('Certificate #: %s\n' % pilotcert)
    readmeFile.write('Aircraft Registration: %s\n' % acftreg)
    if len(takeoff_times) != 0:
        readmeFile.write('Flight Operations Area: %3.8f, %3.8f x %3.8f, %3.8f\n' % (maxLat, maxLon, minLat, minLon))
        readmeFile.write('Time In Air: %.2f\n' % timeInAir)

    readmeFile.write('Takeoffs: %d\n' % len(takeoff_times))
    for i in takeoff_times:
        readmeFile.write('          %s UTC\n' % i.strftime('%Y-%m-%d %H:%M:%S'))

    if takeoffWithoutGPS != 0:
        readmeFile.write("Takeoffs without GPS: %d\n" % takeoffWithoutGPS)

    if len(takeoff_times) != 0:
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
            readmeFile.write('        %s\n' % (decodeError(error.to_dict()['Subsys'], error.to_dict()['ECode'])))
    readmeFile.close()

if __name__ == '__main__':
    main()
