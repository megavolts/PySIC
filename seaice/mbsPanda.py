#! /usr/bin/python3.5
# -*- coding: UTF-8 -*-

"""
Created on Fri Aug 29 08:47:19 2014
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2014/11/25"
"""

import numpy as np
import datetime
import logging
import seaice.icdtools
import pandas as pd

# ----------------------------------------------------------------------------------------------------------------------#
def read(MBS_path, lcomment='n'):
    """
		Calculate the volume fraction of brine in function of the temperature and salinity

		Parameters
		----------
		MBS_path : string
			File path, included filename, to the file containing the data to import

		Returns
		----------
		vf_b: ndarray
			array containing the mbs data in the following column
			1 to 5  year month day hour minute
			6       ice thickness
			7       mean snow thickness (mean of sensor 1 to sensor 3)
			8       snow thickness (sensor 1)
			9       snow thickness (sensor 2)
			10      snow thickness (sensor 3)
			11      water depth
			12      water temperature
			13      air temperature
			14      HR
			15...21 air thermistor
			22      ice surface thermistor
			23...end ice and water thermistor

	"""

    import csv
    import datetime as dt

    MBSyear = int(MBS_path.split('/')[-1][3:5])
    ## CSV with dialect
    fopen = open(MBS_path, 'rU')

    # CSV dialect
    csv.register_dialect('MBS06', delimiter='\t', doublequote=False, quotechar='', lineterminator='\r\n', escapechar='',
                         quoting=csv.QUOTE_NONE)
    csv.register_dialect('MBS09', delimiter='\t', doublequote=True, quotechar='', lineterminator='\r\n', escapechar='',
                         quoting=csv.QUOTE_NONE)
    csv.register_dialect('MBS13', delimiter=',', doublequote=False, quotechar='', lineterminator='\n', escapechar='',
                         quoting=csv.QUOTE_NONE)

    if 13 <= MBSyear:
        source = csv.reader(fopen)
        nheader = 1
        col_date = 6 - 1  # YYYY-MM-DD HH:MM:SS
        col_Hi = 48 - 1
        col_Hs = np.nan
        col_Hs1 = 49 - 1
        col_Hs2 = 50 - 1
        col_Hs3 = 51 - 1
        col_Hw = 52 - 1
        col_Tw = 38 - 1
        col_Tair = 53 - 1
        col_HR = 2 - 1
        col_Tice_00 = 8 - 1
        n_th_air = 7
        n_th = 30
        tz = 'UTC'
    elif 10 <= MBSyear < 13:  # for 2012, 2011, 2010
        source = csv.reader(fopen, 'MBS09')
        nheader = 0
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Hs = np.nan
        col_Hs1 = 10 - 1
        col_Hs2 = 11 - 1
        col_Hs3 = 12 - 1
        col_Hi = 13 - 1
        col_Hw = 14 - 1
        col_Tw = 7 - 1
        col_Tair = 9 - 1
        col_HR = 8 - 1
        col_Tice_00 = 17 - 1
        n_th_air = 7
        n_th = 29
        if MBSyear == 12:
            tz = 'AKST'
        else:
            tz = 'UTC'
    elif 8 <= MBSyear < 10:  # for 2009, 2008
        source = csv.reader(fopen, 'MBS09')
        nheader = 0
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Hs = np.nan
        col_Hs1 = 10 - 1
        col_Hs2 = 11 - 1
        col_Hs3 = 12 - 1
        col_Hi = 13 - 1
        col_Hw = 14 - 1
        col_Tw = 7 - 1
        col_Tair = 9 - 1
        col_HR = 8 - 1
        col_Tice_00 = 16 - 1
        n_th_air = 4
        n_th = 29
        if MBSyear == 8:
            tz = 'UTC'
        elif MBSyear == 9:
            tz = 'AKST'
    elif 6 <= MBSyear < 8:  # for 2007
        source = csv.reader(fopen, 'MBS06')
        nheader = 0
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Hs = 10 - 1
        col_Hs1 = np.nan
        col_Hs2 = np.nan
        col_Hs3 = np.nan
        col_Hi = 11 - 1
        col_Hw = 12 - 1
        col_Tw = 7 - 1
        col_Tair = 9 - 1
        col_HR = 8 - 1
        col_Tice_00 = 14 - 1
        if MBSyear == 7:
            n_th_air = 0
            n_th = 19
        elif MBSyear == 6:
            n_th_air = 4
            n_th = 29
        tz = 'UTC'
    else:
        if lcomment == 'y':
            print('out of range')

    data = []
    # skip header
    for iiHeader in range(0, nheader):
        next(source)

    rownum = 0
    for row in source:
        data.append([])
        for col in row:
            if col == '-9999' or col == '-9999.0' or col == '-9999.000' or col == 'NAN' or col == 'nan' or col == '':
                col = np.nan
            data[rownum].append(col)
        rownum += 1

    dataout = []

    # parse data
    if tz == 'UTC':
        dtzone = +9 * 3600
    else:
        dtzone = 0

    for ii in range(0, len(data)):
        dataout.append([])
        # date and time
        if 12 < MBSyear:
            d = dt.datetime.strptime(data[ii][col_date], "%Y-%m-%d %H:%M:%S") + dt.timedelta(0, dtzone)
            dataout[ii].append(int(d.strftime("%Y")))  # 1
            dataout[ii].append(int(d.strftime("%m")))  # 2
            dataout[ii].append(int(d.strftime("%d")))  # 3
            dataout[ii].append(int(d.strftime("%H")))  # 4
            dataout[ii].append(int(d.strftime("%M")))  # 5
        elif 5 < MBSyear <= 12:
            d = dt.datetime(int(float(data[ii][col_date])), 1, 1) + dt.timedelta(
                float(data[ii][col_date - 1]) - 1) + dt.timedelta(0, dtzone)
            dataout[ii].append(int(d.strftime("%Y")))  # 1
            dataout[ii].append(int(d.strftime("%m")))  # 2
            dataout[ii].append(int(d.strftime("%d")))  # 3
            dataout[ii].append(int(d.strftime("%H")))  # 4
            dataout[ii].append(int(d.strftime("%M")))  # 5

        # ice
        dataout[ii].append(float(data[ii][col_Hi]))  # 6

        # snow
        if 6 <= MBSyear < 8:
            dataout[ii].append(float(data[ii][col_Hs]))  # 7
            dataout[ii].append(np.nan)  # 8
            dataout[ii].append(np.nan)  # 9
            dataout[ii].append(np.nan)  # 10
        else:
            dataout[ii].append(
                np.nanmean([float(data[ii][col_Hs1]), float(data[ii][col_Hs2]), float(data[ii][col_Hs3])]))  # 7
            dataout[ii].append(float(data[ii][col_Hs1]))  # 8
            dataout[ii].append(float(data[ii][col_Hs2]))  # 9
            dataout[ii].append(float(data[ii][col_Hs3]))  # 10

        # water depth
        dataout[ii].append(float(data[ii][col_Hw]))  # 11
        dataout[ii].append(float(data[ii][col_Tw]))  # 12
        dataout[ii].append(float(data[ii][col_Tair]))  # 13
        dataout[ii].append(float(data[ii][col_HR]))  # 14

        # thermistor
        for iiT in range(0, 7 - n_th_air):
            dataout[ii].append(np.nan)
        for iiT in range(col_Tice_00, col_Tice_00 + n_th):
            dataout[ii].append(float(data[ii][iiT]))
    return np.array(dataout)


def ice_temperature_profile(mbs_data, start_day, end_day='False', ice_thickness=float('nan'), section_thickness=0.05, comment='n'):
    '''
    :rtype: np.ndarray: blabal
    :param mbs_data: dict
    :param time:
    :param ice_thickness:
    :param section_thickness:
    :param comment:
    :return:
    '''

    mbs_ice_surface = {}
    mbs_ice_surface[2006] = 8
    mbs_ice_surface[2007] = 8
    mbs_ice_surface[2008] = 8
    mbs_ice_surface[2009] = 8
    mbs_ice_surface[2010] = 8
    mbs_ice_surface[2011] = 8
    mbs_ice_surface[2012] = 8
    mbs_ice_surface[2013] = 8
    mbs_ice_surface[2014] = 8

    year = start_day.year
    if end_day == 'False':
        end_day = start_day

    index = np.array([], dtype=int)
    while start_day <= end_day:
        index_month = np.where(mbs_data[year][:, 1] == start_day.month)[0]
        index_day = np.where(mbs_data[year][index_month, 2] == start_day.day)[0]
        index = np.append(index, index_month[index_day])
        start_day += datetime.timedelta(1)

    if index.size == 0:
        logging.warning('no data present for this date in the dataset')
        return None

    else:
        T_mbs = np.nanmean(mbs_data[year][index], axis=0)[15 + mbs_ice_surface[year] - 1:]

        h_max_mbs = np.nanmax(mbs_data[year][index, 5])
        if np.isnan(h_max_mbs) and np.isnan(ice_thickness):
            h_max_mbs = ice_thickness
        elif np.isnan(h_max_mbs):
            h_max_mbs = 0.1*(15 + mbs_ice_surface[int(year)] - 1)
            logging.warning('ice thickness not defined, ')
        y_mbs = np.arange(0, h_max_mbs, 0.1)

        if y_mbs[-1] < h_max_mbs:
            T_h_mbs = np.interp(h_max_mbs, np.append(y_mbs, [y_mbs[-1] + 0.1]), T_mbs[0:len(y_mbs)+1])
            T_mbs = np.append(T_mbs[0:len(y_mbs)], T_h_mbs)
            y_mbs = np.append(y_mbs, h_max_mbs)
        else:
            T_mbs = T_mbs[0:len(y_mbs)]

        return [T_mbs, y_mbs]

def daily_max(mbs_data, year, ii_col):
    day_start = datetime.datetime(year, int(mbs_data[year][0, 1]), int(mbs_data[year][0, 2]))
    day_end = datetime.datetime(year, int(mbs_data[year][-1, 1]), int(mbs_data[year][-1, 2]))
    ii_day = day_start
    ii_col = 6
    hi_day = []
    while ii_day <= day_end:
        day_index = seaice.icdtools.index_from_day(mbs_data[year], ii_day)
        try:
            hi_mean = np.nanmean(mbs_data[year][day_index, ii_col-1])
        except IndexError:
            hi_mean = np.nan
        else:
            hi_day.append(hi_mean)
        ii_day += datetime.timedelta(1)
    hi_max = np.nanmax(hi_day)
    np.where(np.array(hi_day) == hi_max)
    hi_max_index = np.where(np.array(hi_day) == hi_max)[0]
    hi_max_index
    if len(np.atleast_1d(hi_max_index)) > 1:
        hi_max_index = hi_max_index[-1]
    hi_max_day = day_start + datetime.timedelta(np.float(hi_max_index))
    return hi_max_day, hi_max


def freezup_date_of_year(freezup_dates_data, year=None, source='si'):
    '''
    :param freezup_dates_data:
    :param year:
        if year is none, look for freezup year for the entire array
    :param source:
    :return:
    '''
    # if year is none, return freezup year for every year
    if year is None:
        year = np.array(freezup_dates_data[:, 0])
        year = year[~np.isnan(year)]
    src = ['si', 'cg', 'jl']

    # select source
    if source not in src:
        logging.warning('source not defined')
        return 0

    freezup_dates = {}
    for ii_year in year:
        ii_year = int(ii_year)
        date = freezup_dates_data[np.where(freezup_dates_data[:,0] == ii_year)[0], src.index(source)+1][0]

        if np.isnan(date):
            src_temp = list(src)
            src_temp.remove(source)
            ii_src = 0
            while np.isnan(date) and ii_src < len(src_temp):
                date = freezup_dates_data[np.where(freezup_dates_data[:,0] == ii_year)[0], src.index(src_temp[ii_src])+1][0]
                ii_src += 1
        if np.isnan(date):
            logging.warning('freezup date is not defined for year %s', ii_year)
        else:
            freezup_dates[ii_year] = (datetime.datetime(ii_year, 1, 1) + datetime.timedelta(int(date)-1)).toordinal()
    return freezup_dates
