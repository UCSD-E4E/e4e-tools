#!/usr/bin/env python
from bin_log_analyzer import mavLog
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

    for file in os.listdir(inputDir):
        if os.path.splitext(os.path.basename(file))[1].lower() in ['.bin', '.log', '.tlog', '.px4log']:
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
        for flight_log in retvals:
            if date == flight_log.takeoff_date:
                flightCounter = flightCounter + 1
                total_time_in_air = total_time_in_air + flight_log.timeInAir
                maxLat = np.amax([maxLat, flight_log.maxLat])
                maxLon = np.amax([maxLon, flight_log.maxLon])
                minLon = np.amin([minLon, flight_log.minLon])
                minLat = np.amin([minLat, flight_log.minLat])
                numTakeOffs = len(flight_log.takeoff_times) + numTakeOffs

                modes.union(flight_log.modes)
                errors.extend(flight_log.errors)
                flight_log.generate_report(os.path.join(new_dir, str(flight_log.log_number) + '.rpt'))
                if date_sort:
                    newPath = os.path.join(new_dir, str(flight_log.log_number) + flight_log.log_type)
                    oldPath = os.path.join(inputDir, str(flight_log.log_number) + flight_log.log_type)
                    os.rename(oldPath, newPath)
        print('    %d logs analyzed' % flightCounter)
        print('    Total Time in Air: %.2f min' % (total_time_in_air * 60))
        print("    Flight Area: %.2f, %.2f" % ((maxLat + minLat) / 2, (maxLon + minLon) / 2))
        print("    Takeoffs: %d" % numTakeOffs)
        print("    Flight Modes: ")
        for i in modes:
            print('\t\t%s' % i)

        print('    Errors: %d' % len(errors))
        for error in errors:
            print('            %s' % (decodeError(error.to_dict()['Subsys'], error.to_dict()['ECode'])))
            
        dir_rpt_name = os.path.join(new_dir, date.isoformat() + '.rpt')
        dir_rpt = open(dir_rpt_name, 'w')
        dir_rpt.write('Pilot: %s\n' % pilotname)
        dir_rpt.write('Certificate #: %s\n' % pilotcert)
        dir_rpt.write('Aircraft Registration: %s\n' % acftreg)
        if total_time_in_air != 0:
            dir_rpt.write('Flight Operations Area: %3.2f, %3.2f\n' % ((maxLat + minLat) / 2, (maxLon + minLon) / 2))
            dir_rpt.write('Time In Air: %.2f hr\n' % total_time_in_air)
        dir_rpt.write('Takeoffs: %d\n' % numTakeOffs)

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
        dir_rpt.close()




if __name__ == '__main__':
    main()