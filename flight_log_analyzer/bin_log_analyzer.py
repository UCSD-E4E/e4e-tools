#!/usr/bin/env python

from pymavlink import mavutil
from pymavlink.dialects.v10 import ardupilotmega as mavlink
import argparse
import numpy as np
import os
import datetime
from enum import Enum
import pytz
from dateutil.tz import tzlocal



class ACFT(Enum):
    UNKNOWN = -1
    SOLO    = 0
    PX4     = 1

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

class mavLog:
    class MAV_PARAM():
        def __init__(self, name, value):
            self.name = name
            self.value = value
        def __repr__(self):
            return "mavLog.MAV_PARAM(%s, %s)" % (self.name, self.value)
    def __init__(self, log_filename, pilot_name = None, pilot_cert = None, aircraft_reg = None, report_file_name = None):
        self.log_number = int(os.path.splitext(os.path.basename(log_filename))[0])
        self.mav_master = mavutil.mavlink_connection(log_filename)
        self.pilot = pilot_name
        self.pilot_certificate = pilot_cert
        self.aircraft_registration = aircraft_reg
        if report_file_name is None:
            self.report_fname = os.path.splitext(log_filename)[0] + '.rpt'
        else:
            self.report_fname = report_file
        self.log_type = os.path.splitext(log_filename)[1]

    def analyze(self):
        self.timeInAir = 0
        FMT = []
        self.PARAM = []
        self.modes = set()
        self.maxLat = -180.0
        self.maxLon = -180.0
        self.minLon = 180.0
        self.minLat = 180.0
        self.takeoff_times = []
        self.landing_times = []
        self.errors = []
        self.takeoffWithoutGPS = 0
        self.acft = ACFT.UNKNOWN
        takeoff_seq = []
        landing_seq = []
        seqNum = 0
        prevCurr = -1
        flying = False
        lastGPS = -1

        mav_master = self.mav_master
        while True:
            msg = mav_master.recv_match(blocking = False)
            if msg is None:
                break
            if msg.get_type() == 'FMT':
                FMT.append(msg)
                pass
            elif msg.get_type() == 'PARM':
                self.PARAM.append(mavLog.MAV_PARAM(msg.to_dict()['Name'], msg.to_dict()['Value']))
                pass
            elif msg.get_type() == 'GPS':
                if msg.to_dict()['Status'] >= 3:
                    if self.acft == ACFT.SOLO:
                        gps_time = int(msg.to_dict()['TimeMS'])
                        gps_week = int(msg.to_dict()['Week'])
                        apm_time = int(msg.to_dict()['T'])
                    elif self.acft == ACFT.PX4:
                        gps_time = int(msg.to_dict()['GMS'])
                        gps_week = int(msg.to_dict()['GWk'])
                        apm_time = int(msg.to_dict()['TimeUS']) / 1e3
                        
                    offset = gps_time - apm_time
                    lastGPS = seqNum
                    self.maxLat = np.max((msg.to_dict()['Lat'], self.maxLat))
                    self.maxLon = np.max((msg.to_dict()['Lng'], self.maxLon))
                    self.minLat = np.min((msg.to_dict()['Lat'], self.minLat))
                    self.minLon = np.min((msg.to_dict()['Lng'], self.minLon))
            elif msg.get_type() == 'CURR':
                if int(msg.to_dict()['Curr']) > 500:
                    flying = True
                    self.modes.add(currentMode)
                    
                    if self.acft == ACFT.SOLO:
                        msgtimestamp = int(msg.to_dict()['TimeMS'])
                    elif self.acft == ACFT.PX4:
                        msgtimestamp = int(msg.to_dict()['TimeUS']) / 1e3

                    if prevCurr != -1:
                        self.timeInAir = self.timeInAir + msgtimestamp - prevCurr
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
                            # print("Takeoff at %s UTC" % (date.strftime('%Y-%m-%d %H:%M:%S')))
                            takeoff_seq.append(lastGPS)
                            self.takeoff_times.append(date)
                        else:
                            # print("Takeoff without GPS fix!")
                            takeoffWithoutGPS = takeoffWithoutGPS + 1
                else:
                    flying = False
                    if prevCurr != -1:
                        if lastGPS != -1:
                            secs_in_week = 604800
                            gps_epoch = datetime.datetime(1980, 1, 6, 0, 0, 0)
                            date_before_leaps = (gps_epoch + datetime.timedelta(
                                seconds = gps_week * secs_in_week + (prevCurr + 
                                offset) / 1e3))
                            date = (date_before_leaps - datetime.timedelta(seconds = 
                                leap(date_before_leaps)))
                            # print("Takeoff at %s UTC" % (date.strftime('%Y-%m-%d %H:%M:%S')))
                            landing_seq.append(lastGPS)
                            self.landing_times.append(date)
                        else:
                            landing_seq.append(seqNum)
                    prevCurr = -1
            elif msg.get_type() == 'MODE':
                currentMode = mavutil.mode_mapping_acm[msg.to_dict()['ModeNum']]
                if flying:
                    self.modes.add(currentMode)
            elif msg.get_type() == 'ERR':
                self.errors.append(msg)
            elif msg.get_type() == 'MSG':
                version = msg.to_dict()['Message'].split()[1]
                if version == 'solo-1.3.1':
                    self.acft = ACFT.SOLO
                elif version == 'V3.3.3':
                    self.acft = ACFT.PX4
            seqNum = seqNum + 1
        self.timeInAir = self.timeInAir / 1e3 / 60 / 60
        # Fix TO times
        TOremove = []
        for i in xrange(len(self.takeoff_times) - 1):
            if self.takeoff_times[i+1] == self.landing_times[i]:
                TOremove.append(i)

        if len(self.takeoff_times) == 0:
            self.takeoff_date = None
        else:
            self.takeoff_date = pytz.utc.localize(self.takeoff_times[0]).astimezone(tzlocal()).date()

    def generate_report(self, output_filename = None):
        if output_filename is None:
            ofname = self.report_fname
        else:
            ofname = output_filename
        readmeFile = open(ofname, 'w')
        readmeFile.write('Pilot: %s\n' % self.pilot)
        readmeFile.write('Certificate #: %s\n' % self.pilot_certificate)
        readmeFile.write('Aircraft Registration: %s\n' % self.aircraft_registration)
        if len(self.takeoff_times) != 0:
            readmeFile.write('Flight Operations Area: %3.3f, %3.3f\n' % ((self.maxLat + self.minLat) / 2, (self.maxLon + self.minLon) / 2))
            readmeFile.write('Time In Air: %.2f\n' % self.timeInAir)

        readmeFile.write('Takeoffs: %d\n' % len(self.takeoff_times))
        for i in xrange(len(self.takeoff_times)):
            readmeFile.write('          %s UTC\t%s UTC\n' % (self.takeoff_times[i].strftime('%Y-%m-%d %H:%M:%S'), self.landing_times[i].strftime('%Y-%m-%d %H:%M:%S')))

        if self.takeoffWithoutGPS != 0:
            readmeFile.write("Takeoffs without GPS: %d\n" % self.takeoffWithoutGPS)

        if len(self.takeoff_times) != 0:
            readmeFile.write('Flight Modes: ')
            for i in self.modes:
                readmeFile.write('%s, ' % i)
            readmeFile.write('\n')

        readmeFile.write('Errors: ')
        if len(self.errors) == 0:
            readmeFile.write('None\n')
        else:
            readmeFile.write('%d\n' % len(self.errors))
            for error in self.errors:
                readmeFile.write('        %s\n' % (decodeError(error.to_dict()['Subsys'], error.to_dict()['ECode'])))
        readmeFile.close()


def analyzeFlightLog(fileName, pilotname, pilotcert, acftreg):

    mavlog = mavLog(fileName, pilotname, pilotcert, acftreg)
    mavlog.analyze()
    mavlog.generate_report()

    retval = dict()
    retval['timeInAir'] = mavlog.timeInAir
    retval['pilotName'] = pilotname
    retval['pilotCert'] = pilotcert
    retval['acftReg'] = acftreg
    retval['maxLat'] = mavlog.maxLat
    retval['maxLon'] = mavlog.maxLon
    retval['minLat'] = mavlog.minLat
    retval['minLon'] = mavlog.minLon
    retval['flightModes'] = mavlog.modes
    retval['takeoffs'] = mavlog.takeoff_times
    retval['numTakeoffs'] = len(mavlog.takeoff_times) + mavlog.takeoffWithoutGPS
    retval['errors'] = mavlog.errors
    return retval

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

    retval = analyzeFlightLog(fileName, pilotname, pilotcert, acftreg)
    print('')
    print('Time In Air: %.2f' % retval['timeInAir'])

    print("Flight Area: %.2f, %.2f x %.2f, %.2f" % (retval['maxLat'], retval['maxLon'], retval['minLat'], retval['minLon']))

    print("Flight Modes: ")
    for i in retval['flightModes']:
        print(i)

    print('Errors: %d' % len(retval['errors']))
    for error in retval['errors']:
        print('        %s' % (decodeError(error.to_dict()['Subsys'], error.to_dict()['ECode'])))

if __name__ == '__main__':
    main()
