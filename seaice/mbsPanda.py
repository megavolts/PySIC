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
import seaice.corePanda
import pandas as pd


# ----------------------------------------------------------------------------------------------------------------------#
def read(mbs_path, lcomment='n'):
    """
    :param mbs_path:
    :param lcomment:
    :return:

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
			 7       snow thickness (sensor 1)
			 8       snow thickness (sensor 2)
			 9      snow thickness (sensor 3)
			10      mean snow thickness (mean of sensor 1 to sensor 3)
			11      water depth
			12      water temperature
			13      air temperature
			14      HR
			15      number of thermistor in air
			16      depth in meter of the first thermistor in ice
			17...17+[16-1] air thermistor
			17+[16]      first thermistor in ice
			17+[16+1]... end ice and water thermistor
	"""

    import csv
    import datetime as dt

    ## CSV with dialect
    csv.register_dialect('MBS06', delimiter='\t', doublequote=False, quotechar='', lineterminator='\r\n', escapechar='',
                         quoting=csv.QUOTE_NONE)
    csv.register_dialect('MBS09', delimiter='\t', doublequote=True, quotechar='', lineterminator='\r\n', escapechar='',
                         quoting=csv.QUOTE_NONE)
    csv.register_dialect('MBS13', delimiter=',', doublequote=False, quotechar='', lineterminator='\n', escapechar='',
                         quoting=csv.QUOTE_NONE)

    MBSyear = int(mbs_path.split('/')[-1].split('_')[-1][2:-4])
    fopen = open(mbs_path, 'rU')
    source = csv.reader(fopen)


    tz = 'UTC'
    nheader = 1
    if MBSyear == 11:
        nheader = 2

    if 13 <= MBSyear: # 2013, 2014
        col_date = 2 -1   # 2: year, 3: day of year, 4: time
        col_Hs = np.nan
        col_Tw = 7 - 1
        col_HR = 8 - 1
        col_Tair = 9 - 1
        col_Hs1 = 10 - 1
        col_Hs2 = 11 - 1
        col_Hs3 = 12 - 1
        col_Hi = 13 - 1
        col_Hw = 14 - 1
        col_th = 15 - 1  #
        pos_Tice_00 = 0  #
        n_th_air = 7
        n_th = 30
    elif 10 <= MBSyear < 13:  # for 2012, 2011, 2010
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Tw = 7 - 1
        col_HR = 8 - 1
        col_Tair = 9 - 1
        col_Hs1 = 10 - 1
        col_Hs2 = 11 - 1
        col_Hs3 = 12 - 1
        col_Hi = 13 - 1
        col_Hw = 14 - 1
        col_th = 15 - 1  #
        pos_Tice_00 = 0  #
        n_th_air = 7
        n_th = 29
    elif 8 <= MBSyear < 10 or MBSyear == 6:  # for 2006, 2008, 2009
        nheader = 1
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Tw = 7 - 1  # water temperature
        col_HR = 8 - 1  # Rel. Humidity
        col_Tair = 9 - 1  # air temperature
        col_Hs1 = 10 - 1  # snow pinger 1
        col_Hs2 = 11 - 1  # snow pinger 2
        col_Hs3 = 12 - 1  # snow pinger 3
        col_Hi = 13 - 1  # ice thickness
        col_Hw = 14 - 1  # water depth
        col_th = 15 - 1  #
        pos_Tice_00 = 0  # depth in meter of first thermistor from ice surface
        n_th_air = 4
        n_th = 29
    elif 7 <= MBSyear < 8:  # for 2007
        nheader = 1
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Tw = 7 - 1
        col_HR = 8 - 1
        col_Tair = 9 - 1
        col_Hs1 = 10 - 1  # only one snow pinger
        col_Hs2 = np.nan
        col_Hs3 = np.nan
        col_Hi = 11 - 1
        col_Hw = 12 - 1
        col_th = 15 - 1  #
        pos_Tice_00 = 0.05  # depth in meter of first thermistor from ice surface
        n_th_air = 0
        n_th = 29
    elif 6 <= MBSyear < 7:  # for 2006, 2008, 2009
        nheader = 1
        col_date = 2 - 1  # 2: year, 3: day of year, 4: time
        col_Tw = 7 - 1  # water temperature
        col_HR = 8 - 1  # Rel. Humidity
        col_Tair = 9 - 1  # air temperature
        col_Hs1 = 10 - 1  # snow pinger 1
        col_Hs2 = np.nan  # snow pinger 2
        col_Hs3 = np.nan  # snow pinger 3
        col_Hi = 13 - 1  # ice thickness
        col_Hw = 14 - 1  # water depth
        col_th = 15 - 1  #
        pos_Tice_00 = 0  # depth in meter of first thermistor from ice surface
        n_th_air = 4
        n_th = 29
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
            if col not in ['-9999', '-9999.0', '-9999.000', 'NAN', 'nan', '', '#VALUE!']:
                data[rownum].append(col)
            else:
                data[rownum].append(np.nan)
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
        if not np.isnan(float(data[ii][col_date])):
            d = dt.datetime(int(float(data[ii][col_date])), 1, 1) + dt.timedelta(float(data[ii][col_date - 1]) - 1) + dt.timedelta(0, dtzone)
            dataout[ii].append(int(d.strftime("%Y")))  # 1
            dataout[ii].append(int(d.strftime("%m")))  # 2
            dataout[ii].append(int(d.strftime("%d")))  # 3
            dataout[ii].append(int(d.strftime("%H")))  # 4
            dataout[ii].append(int(d.strftime("%M")))  # 5

            # ice thickness
            dataout[ii].append(float(data[ii][col_Hi]))  # 6 Hi

            # snow thickness
            if 6 <= MBSyear < 8:
                dataout[ii].append(float(data[ii][col_Hs1]))  # 7 Hs1
                dataout[ii].append(np.nan)  # 8 Hs2
                dataout[ii].append(np.nan)  # 9 Hs3
            else:
                dataout[ii].append(float(data[ii][col_Hs1]))  # 7 Hs1
                dataout[ii].append(float(data[ii][col_Hs2]))  # 8 Hs2
                dataout[ii].append(float(data[ii][col_Hs3]))  # 9 Hs3
            dataout[ii].append(np.nanmean(dataout[ii][-3:]))  # 10 mean(Hs)

            # water depth
            dataout[ii].append(float(data[ii][col_Hw]))  # 11

            # water temperature
            dataout[ii].append(float(data[ii][col_Tw]))  # 12 Air temperature

            # air temperature
            dataout[ii].append(float(data[ii][col_Tair]))  # 13 Water temperature

            # relative humidity
            dataout[ii].append(float(data[ii][col_HR]))  # 14 Relative humidity

            # number of thermistor in air
            dataout[ii].append(float(n_th_air))  # 15

            # position first thermistor in ice
            dataout[ii].append(float(pos_Tice_00))  # 16

            # thermistor
            for iiT in range(0, n_th):
                if isinstance(data[ii][col_th+iiT], float):
                    dataout[ii].append(float(data[ii][col_th+iiT]))  # 17...
                else:
                    dataout[ii].append(np.nan)
    return np.array(dataout)


def import_core(mbs_data, day, location=None, ice_thickness=np.nan, comment = None):
    """
    :param mbs_data:
    :param day:
    :param ice_thickness:
    :return:
    """

    index_month = np.where(mbs_data[day.year][:, 1] == day.month)[0]
    index_day = np.where(mbs_data[day.year][index_month, 2] == day.day)[0]

    if index_day.size == 0:
        return None

    else:
        # import temperature
        t_mbs = np.nanmean(mbs_data[day.year][index_day], axis=0)[int(17 + np.unique(mbs_data[day.year][index_day][:, 15-1]))-1:]
        t_mbs_y = np.array([np.unique(mbs_data[day.year][index_day][:, 16-1])+0.1*ii for ii in range(t_mbs.__len__())]).flatten()

        if np.isnan(t_mbs).all():
            return None

        else:
            # generate ice core
            import seaice.corePanda

            core_name = 'mbs-' + day.strftime('%Y%m%d')
            coring_location = location
            coring_date = day
            ice_thickness_mbs = None
            if not np.isnan(np.nanmax(mbs_data[day.year][index_day, 5])):
                ice_thickness_mbs = np.nanmedian(mbs_data[day.year][index_day, 5])
                comment = 'ice thickness from underwater pinger'
            else:
                T_flag = 0
                while T_flag <= t_mbs.__len__() - 1:
                    if (-2 < t_mbs[T_flag] < -1.8 and -2 < t_mbs[T_flag + 1] < -1.8):
                        break
                    else:
                        T_flag += 1
                if T_flag+1 != t_mbs.__len__():
                    ice_thickness_mbs = 0.1 * (T_flag + 1)
                comment = 'ice thickness estimated from temperature profile'
            # TODO: read snow thickness from mbs data file
            snow_thickness = None
            ic = seaice.corePanda.Core(core_name, coring_date, coring_location, ice_thickness_mbs, snow_thickness,
                                           comment=comment)

            # import temperature
            if ice_thickness_mbs is not None:
                ice_thickness = ice_thickness_mbs

            columns = ['temperature', 'y_mid', 'comment', 'variable', 'core', 'ice_core_length',
                       'sample_name']
            profile = pd.DataFrame(columns=columns)
            core_name = 'mbs-'+ day.strftime('%Y%m%d')
            print(core_name)
            comment = 'temperature profile from mbs'
            variable = 'temperature'

            ii = 0
            while t_mbs_y[ii] <= ice_thickness:
                sample_name = core_name + str('%02d' %ii)
                x = t_mbs[ii]
                y_mid = t_mbs_y[ii]
                measure = pd.DataFrame(
                                    [[x, y_mid, comment, variable, core_name, ice_thickness, sample_name]],
                                    columns=columns, index=[sample_name])
                profile = profile.append(measure)
                ii+=1
            if y_mid < ice_thickness and ice_thickness < t_mbs_y[-1]:
                sample_name = core_name + str('%02d' %ii)
                y_mid = ice_thickness
                x = np.interp(ice_thickness, t_mbs_y, t_mbs)
                measure = pd.DataFrame(
                                    [[x, y_mid, comment, variable, core_name, ice_thickness, sample_name]],
                                    columns=columns, index=[sample_name])
                profile = profile.append(measure)
            ic.add_profile(profile)
            return ic


def ice_core(mbs_data, day, ice_thickness = np.nan):
    return None


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
