#!/usr/bin/env python3
from bin_log_analyzer import mavLog
from bin_log_analyzer import decodeError
import argparse
import os
import numpy as np
import glob
import itertools
from datetime import datetime
import time

def main():
    parser = argparse.ArgumentParser(description = 'E4E Ardupilot Autopilot '
            'Flight Log Analyzer')
    parser.add_argument('-i', '--input', help = 'Input directory',
            metavar = 'dir', dest = 'dir', default = './')
    parser.add_argument('-p', '--pilot', default = '', help = 'Pilot Name')
    parser.add_argument('-C', '--certificate', default = '', help = 'Pilot Certificate')
    parser.add_argument('-R', '--registration', default = '', help = 'Aircraft Registration')
    parser.add_argument('-nd', '--no_directory', action = 'store_false', help='Directory Sorting Flag', dest='date_sort')

    args = parser.parse_args()
    inputDir = args.dir
    pilotname = args.pilot
    pilotcert = args.certificate
    acftreg = args.registration
    date_sort = args.date_sort
    retvals = []
    flightLogs = set()
    dates = set()

    exts = ['.bin', '.log', '.tlog', '.px4log', '.BIN']

    for file in os.listdir(inputDir):
        if os.path.splitext(os.path.basename(file))[1] in exts:
            if os.path.splitext(os.path.basename(file))[0] in flightLogs:
                continue
            flightLogs.add(os.path.splitext(os.path.basename(file))[0])
            retval = mavLog(os.path.join(inputDir, file), pilotname, pilotcert, acftreg)
            retval.analyze()
            retvals.append(retval)
            if retval.takeoff_date != None:
                dates.add(retval.takeoff_date)
            else:
                retval.generate_report()

    for date in dates:
        if date_sort:
            new_dir = os.path.join(inputDir, '%4d.%02d.%02d' % (date.year, date.month, date.day))
            if not os.path.isdir(new_dir):
                os.mkdir(new_dir)
        else:
            new_dir = inputDir
        print('For %s' % date.isoformat())
        numTakeOffs = 0
        flightCounter = 0
        total_time_in_air = 0
        maxLat = -180
        maxLon = -180
        minLon = 180
        minLat = 180
        modes = set()
        errors = []
        to_times = []
        ld_times = []
        total_cons = 0

        for flight_log in retvals:
            if date == flight_log.takeoff_date:
                flightCounter = flightCounter + 1
                total_time_in_air = total_time_in_air + flight_log.timeInAir_hr
                maxLat = np.amax([maxLat, flight_log.maxLat])
                maxLon = np.amax([maxLon, flight_log.maxLon])
                minLon = np.amin([minLon, flight_log.minLon])
                minLat = np.amin([minLat, flight_log.minLat])
                numTakeOffs = len(flight_log.takeoff_times) + numTakeOffs
                to_times.extend(flight_log.takeoff_times)
                ld_times.extend(flight_log.landing_times)
                assert(len(to_times) == len(ld_times))
                total_cons += flight_log.batt_cons

                modes = modes.union(flight_log.modes)
                errors.extend(flight_log.errors)
                flight_log.generate_report(os.path.join(new_dir, flight_log.log_number + '.rpt'))
                if date_sort:
                    newPath = os.path.join(new_dir, flight_log.log_number + flight_log.log_type)
                    oldPath = os.path.join(inputDir, flight_log.log_number + flight_log.log_type)
                    try:
                        os.rename(oldPath, newPath)
                    except OSError:
                        print("Failed to move %s to %s" % (oldPath, newPath))
            # elif flight_log.takeoff_date is not None:
            #     print("Date mismatch!")
            #     print(date)
            #     print(flight_log.takeoff_date)

        to_times.sort()
        ld_times.sort()

        print('    %d logs analyzed' % flightCounter)
        print('    Total Time in Air: %.2f min' % (total_time_in_air * 60))
        print("    Flight Area: %.2f, %.2f" % ((maxLat + minLat) / 2, (maxLon + minLon) / 2))
        print("    Takeoffs: %d" % numTakeOffs)
        for i in range(numTakeOffs):
            start_time = time.mktime(to_times[i].timetuple())
            stop_time = time.mktime(ld_times[i].timetuple())
            duration = (stop_time - start_time) / 60
            print('          %s UTC\t%s UTC    %d min' % (to_times[i].strftime('%Y-%m-%d %H:%M:%S'), ld_times[i].strftime('%Y-%m-%d %H:%M:%S'), int(duration)))
        print("    Flight Modes: ")
        for i in modes:
            print('\t\t%s' % i)

        print('    Errors: %d' % len(errors))
        for error in errors:
            print('            %s' % (decodeError(error.to_dict()['Subsys'], error.to_dict()['ECode'])))
        print("    Consumed: %.3f Ah" % (total_cons))
            
        dir_rpt_name = os.path.join(new_dir, date.isoformat() + '.rpt')
        dir_rpt = open(dir_rpt_name, 'w')
        dir_rpt.write('Pilot: %s\n' % pilotname)
        dir_rpt.write('Certificate #: %s\n' % pilotcert)
        dir_rpt.write('Aircraft Registration: %s\n' % acftreg)
        if total_time_in_air != 0:
            dir_rpt.write('Flight Operations Area: %3.2f, %3.2f\n' % ((maxLat + minLat) / 2, (maxLon + minLon) / 2))
            dir_rpt.write('Time In Air: %.2f hr\n' % total_time_in_air)
        dir_rpt.write('Takeoffs: %d\n' % numTakeOffs)
        for i in range(numTakeOffs):
            start_time = time.mktime(to_times[i].timetuple())
            stop_time = time.mktime(ld_times[i].timetuple())
            duration = (stop_time - start_time) / 60
            dir_rpt.write('          %s UTC\t%s UTC    %d min\n' % (to_times[i].strftime('%Y-%m-%d %H:%M:%S'), ld_times[i].strftime('%Y-%m-%d %H:%M:%S'), int(duration)))
        
        if numTakeOffs != 0:
            dir_rpt.write('Flight Modes: ')
            for i in modes:
                dir_rpt.write('%s, ' % i)
            dir_rpt.write('\n')

        dir_rpt.write('Errors: ')
        if len(errors) == 0:
            dir_rpt.write('None\n')
        else:
            dir_rpt.write('%d\n' % len(errors))
            for error in errors:
                dir_rpt.write('        %s\n' % (decodeError(error.to_dict()['Subsys'], error.to_dict()['ECode'])))
        dir_rpt.write("Consumed: %.3f Ah\n" % (total_cons))
        dir_rpt.close()
    # clean up logs
    exts += '.rpt'
    regex = [os.path.join(inputDir, '*%s' % ext) for ext in exts]
    no_date_logs = list(itertools.chain.from_iterable([glob.glob(expr) for expr in regex]))
    no_date_dir = os.path.join(inputDir, 'no_date')
    if not os.path.isdir(no_date_dir):
        os.mkdir(no_date_dir)
    if date_sort:
        for log in no_date_logs:
            os.rename(log, os.path.join(no_date_dir, os.path.basename(log)))


if __name__ == '__main__':
    main()