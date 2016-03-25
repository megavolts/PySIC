#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
icecoredata.py: icecoredata is a toolbox to import ice core data file from xlsx spreadsheet. Xlsx spreadsheet should be
formatted according to the template provided by the Sea Ice Group of the Geophysical Institute of University of Alaska,
Fairbanks.
"""
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2014/11/25"

__all__ = ['Core', 'CoreSet']

import numpy as np
import logging
from . import icdtools

LOG_FILENAME='ICimport.log'
LOG_LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

class Core:
    def __init__(self, name, date, location, ice_thickness, snow_depth):
        self.name = name
        self.date = date
        self.location = location
        self.corenames = [name]
        self.number = 1
        self.ice_thickness = ice_thickness
        self.snow_depth = snow_depth
        self.t = None
        self.yt = None
        self.lengtht = None
        self.s = None
        self.ys = None
        self. lengths = None
        self.t_air = None

    def add_corenames(self, corename):
        if corename not in self.corenames:
            self.number += 1
            self.corenames.append(corename)

    def error(message):
        import sys
        sys.stderr.write("error: %s\n" % message)
        sys.exit(1)

    def t_profile(self, t, yt, lengtht):
        self.t = t
        self.yt = yt
        self.lengtht = lengtht

    def s_profile(self, s, ys, lengths):
        self.s = s
        self.ys = ys
        self.lengths = lengths


    def t_snow(self, t_snow):
        self.t_snow = t_snow

    def t_ice0(self, t_ice0):
        self.t_ice0 = t_ice0

    def t_water(self, t_water):
        self.water = t_water

    def __getattr__(self, key):
        return None

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

def getfilepath(datadir, dataext):
    import os
    filepath = []
    for path, subdirs, files in os.walk(datadir):
        subdirs.sort()
        files.sort()
        for name in files:
            if name.endswith(dataext):
                f = os.path.join(path, name)
                filepath.append(f)
    return filepath

def generatesrc(datadir, dataext):
    list=core.getfilepath(datadir, dataext)
    with open(datadir+'/ic_list.txt','w') as f:
        for ii in range(0, len(list)):
            f.write(list[ii]+"\n")

## import specific ice core
def importcore(ic_path, section_thickness=0.05, missvalue=float('nan'), log_level='warning'):
    import openpyxl
    import datetime

    wb = openpyxl.load_workbook(filename=ic_path, use_iterators=True)  # load the xlsx spreadsheet
    ws_name = wb.get_sheet_names()

    ws_summary = wb.get_sheet_by_name('summary')  # load the data from the summary sheet

    # name
    temp_cell = ws_summary['C21']
    ic_name = temp_cell.value

    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])
    logging.info('Processing ' + ic_name + '...')

    # date
    temp_cell = ws_summary['C2']
    if isinstance(temp_cell.value, (float, int)):
        ic_date = datetime.datetime(1899, 12, 30)+datetime.timedelta(temp_cell.value)
    else:
        ic_date = temp_cell.value

    # location
    temp_cell = ws_summary['C5']
    ic_loc = temp_cell.value

    # snow thickness
    temp_cell = ws_summary['C9']
    if temp_cell is None or temp_cell.value in ['n/m', 'n/a', 'unknow']:
        ic_snow_depth = missvalue
    else:
        ic_snow_depth = temp_cell.value

    # ice thickness
    temp_cell = ws_summary['C11']
    if temp_cell is None or temp_cell.value in ['n/m', 'n/a', 'unknow']:
        ic_ice_thickness = missvalue
    else:
        ic_ice_thickness = temp_cell.value

    imported_core = Core(ic_name, ic_date, ic_loc, ic_ice_thickness, ic_snow_depth)

    # surface temperature
    temp_cell = ws_summary['C15']
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a', 'unknow']:
        imported_core.t_air = temp_cell.value
    temp_cell = ws_summary['C16']
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a', 'unknow']:
        imported_core.t_snow = temp_cell.value
    temp_cell = ws_summary['C17']
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a', 'unknow']:
        imported_core.t_ice0 = temp_cell.value
    temp_cell = ws_summary['C18']
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a', 'unknow']:
        imported_core.t_water = temp_cell.value

    ii_row = 23
    ii_col = 3
    while ws_summary[n2excel(ii_col)+str('%.0f' % ii_row)] is not None and ws_summary[n2excel(ii_col)+str('%.0f' % ii_row)].value is not None :
        imported_core.add_corenames(ws_summary[n2excel(ii_col)+str('%.0f' % ii_row)].value)
        ii_col += 1

    # TEMPERATURE
    if 'T_ice' in ws_name:
        logging.info('\ttemperature profile present')

        ws_t = wb.get_sheet_by_name('T_ice')  # load data from the temperature sheet
        # temperature reading
        flag = 1
        jj = 6

        ytemp = ws_t[n2excel(1)+str('%.0f' % jj)]
        while flag == 1:
            if jj == 6:
                y = np.array(ytemp.value)
            else:
                y = np.append(y, ytemp.value)
            jj += 1
            try:
                ytemp=ws_t[n2excel(1)+str('%.0f' % jj)].value
            except AttributeError:
                flag = 0
            else:
                ytemp=ws_t[n2excel(1)+str('%.0f' % jj)]

        # core length
        temp_cell = ws_t['C2']
        if temp_cell is None or temp_cell.value in ['n/m', 'n/a']:
            tlength = y[-1]
        else:
            tlength = temp_cell.value

        t = np.empty(len(y))
        t[:] = np.nan
        for jj in range(6, 6 + len(y)):
            ws_s_t = ws_t[n2excel(2)+str('%.0f' % jj)]
            if ws_s_t is None:
                temp = missvalue
            elif isinstance(ws_s_t.value, (float, int)):
                temp = ws_s_t.value
            else:
                temp = missvalue
            t[jj - 6] = temp
            jj += 1

        # profile writing with dx section
        yt = np.arange(section_thickness / 2, y[-1], section_thickness)
        if section_thickness / 2 <= tlength - yt[-1]:
            yt = np.concatenate((yt, [yt[-1] + section_thickness]))
        t = np.interp(yt, y[~np.isnan(t)], t[~np.isnan(t)])
        imported_core.t_profile(t, yt, tlength)
    else:
        logging.info('\ttemperature profile absent')

    # SALINITY S
    if 'S_ice' in ws_name:
        logging.info('\tsalinity profile present')

        ws_s = wb.get_sheet_by_name('S_ice')  # load data from the salinity sheet

        # depth reading
        flag = 1
        x3flag = 0
        jj = 6

        while flag == 1:
            x1 = ws_s[n2excel(1)+str('%.0f' % jj)]
            x2 = ws_s[n2excel(2)+str('%.0f' % jj)]
            if isinstance(x1.value, (float, int)):
                xmid = (x1.value + x2.value) / 2
            else:
                xmid = ws_s[n2excel(3)+str('%.0f' % jj)]
                xmid = xmid.value
                x3flag = 1

            if jj == 6:
                x = np.array(xmid)
            else:
                x = np.append(x, xmid)
            jj += 1

            if x3flag == 0:
                try:
                    x1=ws_s[n2excel(1)+str('%.0f' % jj)].value
                except AttributeError:
                    flag = 0
                else:
                    x1 = x1
            else:
                try:
                    x3 == ws_s[n2excel(3)+str('%.0f' % jj)].value
                except AttributeError:
                    flag = 0
                else:
                    x3=x3

        s = np.empty(len(x))
        s[:] = missvalue

        for jj in range(6, 6 + len(x)):
            ws_s_s = ws_s[n2excel(4)+str('%.0f' % jj)]
            if ws_s_s is not None and isinstance(ws_s_s.value, (float, int)):
                s[jj - 6] = ws_s_s.value
            jj += 1  # core length


        if ~np.isnan(s).all():
            # core length
            temp_cell = ws_s['C2']
            if temp_cell is None or temp_cell.value in ['n/m', 'n/a']:
                slength = x2.value
            else:
                slength = temp_cell.value

            # profile writing with dx section
            ys = np.arange(section_thickness / 2, x[-1], section_thickness)
            if slength is not None and section_thickness / 2 <= slength - ys[-1]:
                ys = np.concatenate((ys, [ys[-1] + section_thickness]))
            s = np.interp(ys, x[~np.isnan(s)], s[~np.isnan(s)])
            imported_core.s_profile(s, ys, slength)
    else:
        logging.info('\tsalinity profile missing')
    return imported_core


## import all ice core data which path are given in a source text file
def importsrc(txtfilepath, section_thickness=0.05, missvalue=float('nan'), log_level='warning'):

    print('Ice core data importation in progress ...')

    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])

    a = open(txtfilepath)
    filepath = [line.strip() for line in a]
    filepath = sorted(filepath)

    ic_dict = {}
    for ii in range(0, len(filepath)):
        if not filepath[ii][0] == '#':
            ic_data = importcore(filepath[ii], section_thickness, missvalue, log_level=log_level)
            ic_dict[ic_data.name]=ic_data

    logging.info('Ice core importation complete')
    print('done')

    return ic_dict


def importlist(ics_list, section_thickness=0.05, missvalue=float('nan'), log_level='warning'):

    print('Ice core data importation in progress ...')

    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])

    ic_dict = {}
    for ii in range(0, len(ics_list)):
        print(ics_list[ii])
        ic_data = importcore(ics_list[ii], section_thickness, missvalue, log_level=log_level)
        ic_dict[ic_data.name]=ic_data

    logging.info('Ice core importation complete')
    print('done')

    return ic_dict


class CoreSet:
    def __init__(self, name, date):
        self.name = name
        self.datestamp = [date]

        self.ice_thickness = []
        self.snow_depth = []
        self.corenames = [name]

        self.s_profile = np.array([[]])
        self.s_length = []
        self.s_legend = []

        self.t_profile = np.array([[]])
        self.t_length = []
        self.t_legend = []

        self.t_air = []
        self.t_snow = []
        self.t_ice0 = []
        self.t_water = []

    def date(self):
        if len(self.datestamp)<2:
            return self.datestamp[0]
        else:
            return self.datestamp

    def error(message):
        import sys
        sys.stderr.write("error: %s\n" % message)
        sys.exit(1)

    def t_avg(self, core_to_ignore=None):
        if core_to_ignore is not None:
            if isinstance(core_to_ignore, str):
                core_to_ignore = [core_to_ignore]
            t_bkp = [self.t_profile, self.t_length]
            for c in core_to_ignore:
                self.del_t_profile(c)
        t_avg_profile = np.nanmean(self.t_profile, axis=1)
        t_avg_length = np.nanmax(self.t_length)

        if core_to_ignore is not None:
            self.t_profile = t_bkp[0]
            self.t_length = t_bkp[1]

        return t_avg_profile, t_avg_length, 't-avg'

    def add_s_profile(self, s, s_length, core_name, dt=None):
        self.s_profile = icdtools.column_merge([self.s_profile, s])
        self.s_length.append(s_length)
        self.s_legend.append(core_name)
        if core_name not in self.corenames:
            self.corenames.append(core_name)
        if dt not in self.datestamp and dt is not None:
            self.date.append(dt)

    def add_t_profile(self, t, t_length, core_name, dt=None):
        self.t_profile = icdtools.column_merge([self.t_profile, t])
        self.t_length.append(t_length)
        self.t_legend.append(core_name)
        if core_name not in self.corenames:
            self.corenames.append(core_name)
        if dt not in self.datestamp and dt is not None:
            self.date.append(dt)

    @property
    def length(self):
        all_length = self.t_length + self.s_length
        return all_length

#    @property
#    def _nanmean_(self, key):
#        return np.nanmean(self._keys)

    def del_s_profile(self, s_name):
        if s_name in self.s_legend:
            index = self.s_legend.index(s_name)
            self.s_legend.pop(index)
            self.s_length.pop(index)
            np.delete(self.s_profile, index, axis=1)
            if s_name not in self.t_legend:
                self.corenames.pop(s_name)
        else:
            print('selected profile does not exist')

    def del_t_profile(self, t_name):
        if t_name in self.t_legend:
            index = self.t_legend.index(t_name)
            self.t_legend.pop(index)
            self.t_length.pop(index)
            np.delete(self.t_profile, index, axis=1)
            if t_name not in self.s_legend:
                self.corenames.pop(t_name)
        else:
            print('selected profile does not exist')


    def add_t_air(self, t):
        self.t_air.append(t)

    def add_t_snow(self, t):
        self.t_snow.append(t)

    def add_t_ice0(self, t):
        self.t_ice0.append(t)

    def add_t_water(self, t):
        self.water.append(t)

    def __getattr__(self, key):
        return None

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

def n2excel(n):
    div=n
    string=""
    temp=0
    while div>0:
        module=(div-1)%26
        string=chr(65+module)+string
        div=int((div-module)/26)
    return string