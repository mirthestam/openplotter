#!/usr/bin/env python
# This file is part of Openplotter.
# Copyright (C) 2017 by sailoog <https://github.com/sailoog/openplotter>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import os
import time
import urllib2
from datetime import datetime, timedelta

from classes.conf import Conf


def run():
    if clean == '1':
        clean_folder()

    download_grib()


def download_grib():

    def get_filename(number):
        return 'gfs.t06z.pgrb2.0p25.f%(n)03d' % {
                    "n": number
                }

    def download_parts():
        # TODO: generic error handling, clean up if something went wrong (i.e. delete downloaded fXXX files)
        # TODO: File sizes are always small. could load to memory to prevent SD card IO
        utcnow = datetime.utcnow()

        # data should be available each 6 hours. However, it it not always present after 6 hours.
        # TODO: therefore at the moment i go back 12. However, i should try, and then adjust with 6 hours.
        if utcnow.hour > 18:
            folder_date = utcnow
            hour = 12

        elif utcnow.hour > 12:
            folder_date = utcnow
            hour = 6

        elif utcnow.hour > 6:
            folder_date = utcnow
            hour = 0

        else:
            # need latest fetch from previous day
            folder_date = utcnow - timedelta(days=1)
            hour = 18

        server_dir = '%(y)04d%(m)02d%(d)02d%(h)02d' % {
            "y": folder_date.year,
            "m": folder_date.month,
            "d": folder_date.day,
            "h": hour
        }

        for num in range(0, file_count):
            source_file = get_filename(num)

            # GUST: Wind Gust
            # TMP: Temperature
            # RH: Relative Humidity
            # APCP : Precipation
            # CAPE = CAPE
            # PRMSL = Pressure (MSL)
            # TMIN: Minimum temperature
            # TMAX: Maximum temperature
            # VRGD UGRD: wind components
            # TCDC: Total cloud cover

            # TODO: Use settings for available fieds

            url = 'http://www.nomads.ncep.noaa.gov' + \
                  '/cgi-bin/filter_gfs_0p25.pl' + \
                  '?file=' + source_file + \
                  '&lev_10_m_above_ground=on' + \
                  '&lev_2_m_above_ground=on' + \
                  '&lev_mean_sea_level=on' + \
                  '&lev_entire_atmosphere=on' + \
                  '&lev_surface=on' + \
                  '&var_GUST=on' + \
                  '&var_APCP=on' + \
                  '&var_RH=on' + \
                  '&var_TMP=on' + \
                  '&var_CAPE=on' + \
                  '&var_PRMSL=on' + \
                  '&var_TMIN=on' + \
                  '&var_TMAX=on' + \
                  '&var_VGRD=on' + \
                  '&var_UGRD=on' + \
                  '&var_TCDC=on' + \
                  '&subregion=&leftlon=' + str(lon_min) + '&rightlon=' + str(lon_max) + '&toplat=' + \
                  str(lat_min) + '&bottomlat=' + str(lat_max) + \
                  '&dir=%2Fgfs.' + server_dir

            print 'Downloading %(i)d / %(t)d %(f)s' % {
                'i': num,
                't': file_count,
                'f': source_file
            }

            response = urllib2.urlopen(url)

            # Download and write the file to disk
            target_filename = os.path.join(path, source_file)
            with open(target_filename, "wb") as local_file:
                local_file.write(response.read())

    def concat_parts():
        utc_now = datetime.utcnow()

        destination_file = '%(y)04d%(mon)02d%(d)02d%(h)02d%(min)02d%(s)02d.grb' % {
            'y': utc_now.year,
            'mon': utc_now.month,
            'd': utc_now.day,
            'h': utc_now.hour,
            'min': utc_now.minute,
            's': utc_now.second
        }

        destination_file = os.path.join(path, destination_file)

        print 'Writing data to \'' + destination_file + '\''

        fout = file(destination_file, 'wb')
        for n in range(0, file_count):
            filename = get_filename(n)
            filename = os.path.join(path, filename)
            fin = file(filename, 'rb')
            fout.write(fin.read())
            fin.close()
            os.remove(filename)
        fout.close()

    lon_min = float(conf.get('GRIB', 'lon_min'))
    lon_max = float(conf.get('GRIB', 'lon_max'))
    lat_min = float(conf.get('GRIB', 'lat_min'))
    lat_max = float(conf.get('GRIB', 'lat_max'))
    days = int(conf.get('GRIB', 'NOAA_days'))
    file_count = days * 12

    # How to calculate the latest run?
    # GFS refreshes each 6 yours. AT 00, 06, 12, 18 UTC.
    # to calculate the run, convert the current date back to UTC

    if lon_min < -180 or lon_min > 180:
        raise ValueError('longitude should be between -180 and 180')

    if lon_max < -180 or lon_max > 180:
        raise ValueError('longitude should be between -180 and 180')

    if lat_min < 0 or lat_min > 90:
        raise ValueError('latitude should be between 0 and 90')

    if lat_max < 0 or lat_max > 90:
        raise ValueError('latitude should be between 0 and 90')

    if days < 1 or days > 12:
        raise ValueError('days should be between 0 and 12')

    download_parts()
    concat_parts()


def clean_folder():
    now = time.time()

    print 'Cleaning folder \'' + path + '\''

    for filename in os.listdir(path):
        full_filename = os.path.join(path, filename)
        if os.path.isfile(full_filename):
            if os.stat(full_filename).st_mtime < now - 7 * (60 * 60 * 24):
                print "EXPIRED: %(f)s" % {
                    'f': filename
                }
                # TODO: Error handling, file could be in use
                os.remove(full_filename)
            else:
                print "PASSED:  %(f)s" % {
                    'f': filename
                }


# download settings
conf = Conf()
run_interval = conf.get('GRIB', 'run_interval')
run_at_startup = conf.get('GRIB', 'run_at_startup')
clean = conf.get('GRIB', 'clean')
path = conf.get('GRIB', 'path')

# calculate the sleep interval
# TODO: use a time diff, or cron job for this
sleep_interval = 0
if run_interval == hourly:
    sleep_interval = 60 * 60
elif run_interval == daily:
    sleep_interval = 60 * 60 * 24
else:
    sleep_interval = 60 * 60  # fallback to hourly

# Initially run
if run_at_startup == '1':
    run()

while True:
    print 'waiting for next queue'
    time.sleep(sleep_interval)
    run()
