#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
icecoredata.py: icecore data is a toolbox to import ice core data file from xlsx spreadsheet. Xlsx spreadsheet should be
formatted according to the template provided by the Sea Ice Group of the Geophysical Institute of University of Alaska,
Fairbanks.
"""

import numpy as np
import matplotlib.pyplot as plt
import logging
from seaice.properties import si_prop_list
from seaice.properties import si_prop_unit
from seaice.properties import si_state_variable

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "2.1.0"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2014/11/25"
__all__ = ['Core', 'CoreSet', 'Profile']

LOG_FILENAME = 'import.log'
LOG_LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}
log_level = 'warning'
missvalue = float('NaN')
# logging.basicConfig(filename='example.log',level=logging.DEBUG)
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')
# ic_path = '/mnt/data_lvm/seaice/core/BRW/2010_11/BRW_CS-20110122A.xlsx'
unit = {'salinity': '[PSU]', 'temperature': '[°C]', 'vb': '[%]', 'brine volume fraction': '[%]'}


class Profile:
    def __init__(self, x, y, profile_label, variable, comment=None, note=None, length=None):
        self.x = x
        self.y = y
        self.profile_label = profile_label
        self.variable = variable
        self.note = note
        if length is None:
            self.length = x[-1] - x[0]
        else:
            self.length = length
        self.comment = comment

    def plot(self, fig_num=None):
        import matplotlib.pyplot as plt
        if fig_num is not None:
            plt.figure(fig_num)
        plt.plot(self.x, self.y[0:len(self.x)])


class Core:
    def __init__(self, name, date, location, ice_thickness, snow_thickness, comment=None):
        self.name = name
        self.date = date
        self.location = location
        self.corenames = [name]
        self.ice_thickness = ice_thickness
        self.snow_thickness = snow_thickness
        self.profiles = {}
        self.comment = None
        if comment is not None:
            self.add_comment(comment)

    def add_profile(self, x, y, profile_label, variable, comment=None, note=None, length=None):
        self.profiles[variable] = Profile(x, y, profile_label, variable, comment, note, length)

    def add_corenames(self, corename):
        if corename not in self.corenames:
            self.corenames.append(corename)

    def add_comment(self, comment):
        if self.comment is None:
            self.comment = [comment]
        else:
            self.comment.append(comment)

    def calc_prop(self, prop):
        """
        :param prop:
        :return:
        """
        # check properties variables
        if prop not in si_prop_list.keys():
            logging.warning('property %s not defined in the ice core property module' % prop)
            return None
        elif 'salinity' not in self.profiles:
            logging.warning('ice core %s is missing salinity profile for further calculation' % self.name)
            return None
        elif 'temperature' not in self.profiles:
            logging.warning('ice core %s is missing temperature profile for further calculation' % self.name)
            return None
        else:
            import seaice.properties
            variable = si_prop_list[prop]
            function = getattr(seaice.properties, variable.replace(" ", "_"))
            profilet = self.profiles['temperature']
            profiles = self.profiles['salinity']
            # y axis where data are present for both profile
            y = np.sort(np.unique(np.concatenate((profilet.y, profiles.y))))
            y = y[np.where(y <= max(max(profilet.y), max(profiles.y)))]
            y = y[np.where(y >= max(min(profilet.y), min(profiles.y)))]
            y_mid = y[0:-1] + np.diff(y) / 2

            xt = np.interp(y_mid, profilet.y, profilet.x)
            xs = np.interp(y_mid, profiles.y[:-1] + np.diff(profiles.y) / 2, profiles.x)
            x = function(xt, xs)

            # comment = None*np.zeros(len(y))
            # length = max(y)-min(y)
            note = 'computed from ' + self.profiles['temperature'].profile_label+ ' temperature profile and ' + \
                   self.profiles['salinity'].profile_label + ' salinity profile'
            profile_label = self.name
            self.add_profile(x, y, profile_label, variable, note=note)
            self.add_comment('computed %s' % variable)


    def plot(self, ax, prop, param_dict=None):
        if prop in si_state_variable.keys():
            profile_label = si_state_variable[prop.lower()]
        elif prop in si_prop_list.keys():
            profile_label = si_prop_list[prop.lower()]
            if profile_label not in self.profiles.keys():
                logging.warning('computing %s' % prop)
                self.calc_prop(prop)
        else:
            logging.warning('no data available to plot')
            return None
        profile = self.profiles[profile_label]

        y = profile.y
        x = profile.x
        if profile.y.__len__() > profile.x.__len__():
            x = np.concatenate((x, np.atleast_1d(x[-1])))
            if param_dict is None:
                out = ax.step(x, y)
            else:
                out = ax.step(x, y, **param_dict)
        else:
            if param_dict is None:
                out = ax.plot(x, y)
            else:
                out = ax.plot(x, y, **param_dict)

        ax.set_xlabel(profile_label + ' ' + si_prop_unit[profile_label])
        ax.set_ylim(max(ax.get_ylim()), 0)
        return out

    def plot_state_variable(self, param_dict=None):
        fig, (ax1, ax2) = plt.subplots(1, 2)
        if 'salinity' in self.profiles.keys():
            self.plot(ax1, 'salinity', param_dict)
            ax1.set_ylabel('depth [m]')
        else:
            logging.warning('salinity profile missing for %s' % self.name)

        if 'temperature' in self.profiles.keys():
            ax2 = self.plot(ax2, 'temperature', param_dict)
        else:
            logging.warning('temperature profile missing for %s' % self.name)
        return fig, (ax1, ax2)




class CoreSet:
    def __init__(self, setname, core):
        self.name = setname
        self.core_data = {core.name: core}
        self.core = [core.name]

    def add_core(self, core):
        self.core_data[core.name] = core
        self.core.append(core.name)

    def ice_thickness(self):
        hi = []
        for key in self.core_data.keys():
            if self.core_data[key].ice_thickness is not None:
                hi.append(self.core_data[key].ice_thickness)
        if hi == [] or np.isnan(hi).all():
            return None
        else:
            return hi, np.nanmean(hi), np.nanmax(hi)

    def core_length(self):
        lc = []
        for key in self.core_data.keys():
            core = self.core_data[key]
            for a in dir(core):
                try:
                    temp = core.__getattribute__(a).length
                except:
                    temp = 0
                else:
                    lc.append(temp)
        return lc, np.nanmean(lc), np.nanmax(lc)

    def mean_temperature(self, section_thickness=0.05):
        t = None
        if self.ice_thickness() is None:
            hi = self.core_length()[1]
        else:
            hi = self.ice_thickness()[1]

        y = np.arange(section_thickness / 2, hi, section_thickness)
        if (hi + len(y) * section_thickness) / 2 < hi:
            y = np.append(y, (hi + len(y) * section_thickness) / 2)
        for key in self.core_data.keys():
            if self.core_data[key].__getattribute__('temperature') is not None:
                t_core = self.core_data[key].__getattribute__('temperature').x
                y_core = self.core_data[key].__getattribute__('temperature').y
                if t is None:
                    t = np.interp(y, y_core[~np.isnan(t_core)], t_core[~np.isnan(t_core)])
                else:
                    t = np.append(t, np.interp(y, y_core[~np.isnan(t_core)], t_core[~np.isnan(t_core)]))
        if t is not None:
            return np.mean(np.atleast_2d(t), axis=0), y
        else:
            return None


def importcore(ic_path, missvalue=missvalue):
    import openpyxl
    import datetime

    wb = openpyxl.load_workbook(filename=ic_path, use_iterators=True)  # load the xlsx spreadsheet
    ws_name = wb.get_sheet_names()
    ws_summary = wb.get_sheet_by_name('summary')  # load the data from the summary sheet

    # extract basic information about the ice core
    # name
    ic_name = ws_summary['C21'].value
    print(ic_name)

    # logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])
    # logging.info('Processing ' + ic_name + '...')

    # date
    temp_cell = ws_summary['C2']
    if isinstance(temp_cell.value, (float, int)):
        ic_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(temp_cell.value)
    else:
        ic_date = temp_cell.value

    # location
    ic_loc = ws_summary['C5'].value

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
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a', 'unknown']:
        imported_core.t_water = temp_cell.value

    ii_row = 23
    ii_col = 3
    while ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)] is not None and ws_summary[
                openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)].value is not None:
        imported_core.add_corenames(ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)].value)
        ii_col += 1

    # SALINITY S
    if 'S_ice' in ws_name:
        # logging.info('\t salinity profile present')
        ws = wb.get_sheet_by_name('S_ice')  # load data from the salinity sheet

        # profile name
        profile_name = ws['C1'].value

        # note
        note = ws['C3'].value

        # vertical coordinate
        bin_flag = 1
        jj = 6
        ybin_sup = []
        ybin_low = []
        ybin_mid = []
        while bin_flag > 0:
            try:
                y1 = ws.cell(column=1, row=jj).value
                y2 = ws.cell(column=2, row=jj).value
            except IndexError:
                break
            if y1 is not None and y2 is not None:
                ybin_sup.append(y1)
                ybin_low.append(y2)
                ybin_mid.append((y1 + y2) / 2)
            elif ws.cell(column=2, row=jj).value is not None:
                ybin_sup.append(None)
                ybin_low.append(None)
                ybin_mid.append(ws.cell(colum=2, row=jj).value)
                bin_flag = 2
            else:
                break
            jj += 1

        if bin_flag is 2:
            for ii_bin in np.arange(0, len(ybin_mid)):
                half_bin_length = (ybin_mid[ii_bin + 1] - ybin_mid[ii_bin]) / 2
                ybin_sup[ii_bin] = ybin_mid[ii_bin] - half_bin_length
                ybin_low[ii_bin] = ybin_mid[ii_bin] + half_bin_length

        # salinity
        ybin = np.append(ybin_sup, ybin_low[-1])
        s = missvalue * np.empty(len(ybin) - 1)
        for jj in range(6, 6 + len(s)):
            s_y = ws.cell(column=4, row=jj).value
            if isinstance(s_y, (float, int)):
                s[jj - 6] = s_y

        # comment
        comment = [None for ii in ybin]
        for jj in range(6, 6 + len(comment) - 1):
            comment[jj - 6] = ws.cell(column=8, row=jj).value
        comment[-1] = [ws['C3'].value]

        # length
        length = ws['C2'].value
        if length is None:
            length = ybin[-1] - ybin[0]
        elif ybin[-1] - ybin[0] < length:
            length = ybin[-1] - ybin[0]
        else:
            length is None
        # save profile
        imported_core.add_profile(s, ybin, profile_name, 'salinity', comment, note, length)
    else:
        logging.info('\tsalinity profile missing')

    # TEMPERATURE T
    if 'T_ice' in ws_name:
        logging.info('\ttemperature profile present')
        ws = wb.get_sheet_by_name('T_ice')  # load data from the salinity sheet

        # profile name
        profile_name = ws['C1'].value

        # note
        note = ws['C3'].value

        # vertical coordinate
        bin_flag = 1
        jj = 6
        ybin = []
        while bin_flag > 0:
            try:
                y1 = ws.cell(column=1, row=jj).value
            except IndexError:
                break
            if y1 is not None:
                ybin.append(y1)
            else:
                break
            jj += 1

        # temperature
        t = missvalue * np.empty(len(ybin))
        for jj in range(6, 6 + len(t)):
            t_y = ws.cell(column=2, row=jj).value
            if isinstance(t_y, (float, int)):
                t[jj - 6] = t_y

        # comment
        c = [None for ii in ybin]
        for jj in range(6, 6 + len(c) - 1):
            c[jj - 6] = ws.cell(column=8, row=jj).value
        c.append(ws['C3'].value)

        # length
        length = ws['C2'].value
        if length is None:
            length = max(ybin)
        # save profile
        imported_core.add_profile(t, ybin, profile_name, 'temperature', c, note, length)
    else:
        logging.info('\tsalinity profile missing')
    return imported_core


def make_section(core, section_thickness=0.05):
    core = core
    for a in dir(core):
        if isinstance(core.__getattribute__(a), Profile) and core.__getattribute__(a) is not None:
            profile = core.__getattribute__(a)
            if profile.length is not None:
                length = profile.length
            else:
                length = core.ice_thickness
            # TODO: start point should be the closet to section_thickness/2
            y_mid_section = np.arange(section_thickness / 2, length, section_thickness)
            if (length + len(y_mid_section) * section_thickness) / 2 < length:
                y_mid_section = np.append(y_mid_section, (length + len(y_mid_section) * section_thickness) / 2)
            x = profile.x
            y = np.array(profile.y)

            if len(y) is len(x) + 1:
                y = (y[1:] + y[:-1]) / 2

            x_mid_section = np.interp(y_mid_section, y[~np.isnan(y)], x[~np.isnan(y)])
            profile.x = x_mid_section
            profile.y = y_mid_section
            core.__delattr__(a)
            core.__setattr__(a, profile)
    return core


def getfilepath(datadir, dataext, subdir='no'):
    import os
    filepath = []
    if subdir == 'yes':
        for path, subdirs, files in os.walk(datadir):
            subdirs.sort()
            files.sort()
            for name in files:
                if name.endswith(dataext):
                    f = os.path.join(path, name)
                    filepath.append(f)
    else:
        files = os.listdir(datadir)
        for name in files:
            if name.endswith(dataext):
                f = os.path.join(datadir, name)
                filepath.append(f)
    return filepath


def generatesrc(datadir, dataext):
    list = getfilepath(datadir, dataext)
    with open(datadir + '/ic_list.txt', 'w') as f:
        for ii in range(0, len(list)):
            f.write(list[ii] + "\n")


## import specific ice core
def importprop(ic_path):
    import openpyxl
    import datetime

    wb = openpyxl.load_workbook(filename=ic_path, use_iterators=True)  # load the xlsx spreadsheet
    ws_name = wb.get_sheet_names()

    ws_summary = wb.get_sheet_by_name('summary')  # load the data from the summary sheet

    # name
    temp_cell = ws_summary['C21']
    ic_name = temp_cell.value
    print(ic_name)

    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])
    logging.info('Processing ' + ic_name + '...')

    # date
    temp_cell = ws_summary['C2']
    if isinstance(temp_cell.value, (float, int)):
        ic_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(temp_cell.value)
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
    while ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)] is not None and ws_summary[
                openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)].value is not None:
        imported_core.add_corenames(ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)].value)
        ii_col += 1

    # comment
    try:
        temp_cell = ws_summary['A33'].value
    except IndexError:
        temp_cell = None
    else:
        imported_core.comment = temp_cell

    # salinity spreadsheet
    if 'S_ice' in ws_name:
        ws_s = wb.get_sheet_by_name('S_ice')  # load data from the temperature sheet
        flag = 1
        jj = 6
        while flag == 1:
            try:
                x1 = ws_s.cell(column=1, row=jj).value
                x2 = ws_s.cell(column=2, row=jj).value
            except IndexError:
                try:
                    x3 = ws_s.cell(column=3, row=jj).value
                except IndexError:
                    break
                else:
                    if isinstance(x3, (float, int)):
                        xmid = x3
            else:
                if isinstance(x1, (float, int)):
                    xmid = (x1 + x2) / 2
            if jj == 6 and flag:
                x = np.array(xmid)
            else:
                x = np.append(x, xmid)
            jj += 1

        # core length
        if x2 is not None:
            imported_core.s_length = x2
        else:
            if ws_s['C2'] is not None:
                imported_core.s_length = ws_s['C2'].value
        # s
        s = np.nan * np.empty(len(x))
        for jj in range(6, 6 + len(x)):
            ws_s_s = ws_s.cell(column=4, row=jj).value
            if isinstance(ws_s_s, (float, int)):
                s[jj - 6] = ws_s_s
            jj += 1  # core length
        if ~np.isnan(s).all():
            imported_core.s = 'X'

        # d18O
        s = np.nan * np.empty(len(x))
        for jj in range(6, 6 + len(x)):
            ws_s_s = ws_s.cell(column=6, row=jj).value
            if isinstance(ws_s_s, (float, int)):
                s[jj - 6] = ws_s_s
            jj += 1  # core length
        if ~np.isnan(s).all():
            imported_core.d180 = 'X'
        # dO2
        s = np.nan * np.empty(len(x))
        for jj in range(6, 6 + len(x)):
            ws_s_s = ws_s.cell(column=7, row=jj).value
            if isinstance(ws_s_s, (float, int)):
                s[jj - 6] = ws_s_s
            jj += 1  # core length
        if ~np.isnan(s).all():
            imported_core.dO2 = 'X'

    # Temperature
    if 'T_ice' in ws_name:
        ws_t = wb.get_sheet_by_name('T_ice')  # load data from the temperature sheet
        flag = 1
        jj = 6

        # y coordinate
        while flag == 1:
            try:
                ytemp = ws_t.cell(column=1, row=jj).value
            # TODO: check if need AttributeError
            except AttributeError and IndexError:
                flag = 0
            else:
                if jj == 6:
                    y = np.array(ytemp)
                else:
                    y = np.append(y, ytemp)
                jj += 1

        # remove trailing None Cell
        temp = []
        for ii in y[::-1]:
            if ii is not None:
                temp.append(ii)
        y = np.array(temp[::-1])
        del temp

        t = np.nan * np.empty(len(y))
        for jj in range(6, 6 + len(y)):
            ws_s_t = ws_t.cell(column=2, row=jj).value
            if isinstance(ws_s_t, (float, int)):
                t[jj - 6] = ws_s_t
            jj += 1  # core length
        if ~np.isnan(t).all():
            imported_core.t = 'X'

        # core length
        temp_cell = ws_t['C2'].value
        if isinstance(temp_cell, (float, int)):
            imported_core.t_length = temp_cell

    # sediment
    if 'sediment' in ws_name:
        ws_s = wb.get_sheet_by_name('sediment')  # load data from the temperature sheet
        flag = 1
        jj = 6
        while flag == 1:
            try:
                x1 = ws_s.cell(column=1, row=jj).value
                x2 = ws_s.cell(column=2, row=jj).value
            except IndexError:
                try:
                    x3 = ws_s.cell(column=3, row=jj).value
                except IndexError:
                    break
                else:
                    if isinstance(x3, (float, int)):
                        xmid = x3
            else:
                if isinstance(x1, (float, int)):
                    xmid = (x1 + x2) / 2
            if jj == 6 and flag:
                x = np.array(xmid)
            else:
                x = np.append(x, xmid)
            jj += 1

        s = np.nan * np.empty(len(x))
        for jj in range(6, 6 + len(x)):
            ws_s_s = ws_s.cell(column=6, row=jj).value
            if isinstance(ws_s_s, (float, int)):
                s[jj - 6] = ws_s_s
            jj += 1  # core length
        if ~np.isnan(s).all():
            imported_core.sediment = 'X'

    # algae
    if 'algal_pigment' in ws_name:
        ws_s = wb.get_sheet_by_name('algal_pigment')  # load data from the temperature sheet
        flag = 1
        jj = 6
        while flag == 1:
            try:
                x1 = ws_s.cell(column=1, row=jj).value
                x2 = ws_s.cell(column=2, row=jj).value
            except IndexError:
                try:
                    x3 = ws_s.cell(column=3, row=jj).value
                except IndexError:
                    break
                else:
                    if isinstance(x3, (float, int)):
                        xmid = x3
            else:
                if isinstance(x1, (float, int)):
                    xmid = (x1 + x2) / 2
            if jj == 6 and flag:
                x = np.array(xmid)
            else:
                x = np.append(x, xmid)
            jj += 1

        s = np.nan * np.empty(len(x))
        for jj in range(6, 6 + len(x)):
            ws_s_s = ws_s.cell(column=5, row=jj).value
            if isinstance(ws_s_s, (float, int)):
                s[jj - 6] = ws_s_s
            jj += 1  # core length
        if ~np.isnan(s).all():
            imported_core.Chla = 'X'

        s = np.nan * np.empty(len(x))
        for jj in range(6, 6 + len(x)):
            ws_s_s = ws_s.cell(column=6, row=jj).value
            if isinstance(ws_s_s, (float, int)):
                s[jj - 6] = ws_s_s
            jj += 1  # core length
        if ~np.isnan(s).all():
            imported_core.Phaeo = 'X'
    return imported_core


def importcorebin(ic_path, section_thickness=0.05, missvalue=missvalue, log_level='warning'):
    import openpyxl
    import datetime

    wb = openpyxl.load_workbook(filename=ic_path, use_iterators=True)  # load the xlsx spreadsheet
    ws_name = wb.get_sheet_names()

    ws_summary = wb.get_sheet_by_name('summary')  # load the data from the summary sheet

    # name
    temp_cell = ws_summary['C21']
    ic_name = temp_cell.value
    print(ic_name)

    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])
    logging.info('Processing ' + ic_name + '...')

    # date
    temp_cell = ws_summary['C2']
    if isinstance(temp_cell.value, (float, int)):
        ic_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(temp_cell.value)
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
    while ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)] is not None and ws_summary[
                openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)].value is not None:
        imported_core.add_corenames(ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)].value)
        ii_col += 1

    # SALINITY S
    if 'S_ice' in ws_name:
        logging.info('\tsalinity profile present')

        ws_s = wb.get_sheet_by_name('S_ice')  # load data from the salinity sheet

        # note
        temp_cell = ws_s['C3']
        if temp_cell is None:
            s_note = None
        else:
            s_note = temp_cell.value

        # vertical coordinate
        flag = 1
        jj = 6

        xbin_sup = []
        xbin_down = []
        while flag == 1:
            try:
                x1 = ws_s.cell(column=1, row=jj).value
                x2 = ws_s.cell(column=2, row=jj).value
            except IndexError:
                if len(xbin_sup) is 0:
                    print('no bin present: contact developer to generate bin from midpoint')
                break

                # try:
                # x3 = ws_s.cell(column=3, row=jj).value
                # except IndexError:
                #     break
                # else:
                #     if isinstance(x3, (float, int)):
                #          xmid = x3
                #         # to do write the end of the x3
            else:
                xbin_sup.append(x1)
                xbin_down.append(x2)
            jj += 1

        # generate the x_bin
        xbin = np.append(xbin_sup, xbin_down[-1])

        # reading salinity value

        # using the bottom section value for the bin
        s = np.nan * np.empty(len(xbin_down))

        for jj in range(6, 6 + len(xbin_down)):
            ws_s_s = ws_s.cell(column=4, row=jj).value
            if isinstance(ws_s_s, (float, int)):
                s[jj - 6] = ws_s_s
            jj += 1

        # core length
        if ~np.isnan(s).all():
            # core length
            temp_cell = ws_s['C2']
            if temp_cell is None or temp_cell.value in ['n/m', 'n/a']:
                slength = x2.value
            else:
                slength = temp_cell.value

            # profile writing with dx section
            # profile writing with dx section, S constant in every bin
            imported_core.s_profile(np.array(s), np.array(xbin), slength, s_note)
    else:
        logging.info('\tsalinity profile missing')

    # TEMPERATURE
    if 'T_ice' in ws_name:
        logging.info('\ttemperature profile present')
        ws_t = wb.get_sheet_by_name('T_ice')  # load data from the temperature sheet
        flag = 1
        jj = 6
        # y coordinate
        while flag == 1:
            try:
                ytemp = ws_t.cell(column=1, row=jj).value
            # TODO: check if need AttributeError
            except AttributeError and IndexError:
                flag = 0
            else:
                if jj == 6:
                    y = np.array(ytemp)
                else:
                    y = np.append(y, ytemp)
                jj += 1

        # remove trailing None Cell
        temp = []
        for ii in y[::-1]:
            if ii is not None:
                temp.append(ii)
        y = np.array(temp[::-1])
        del temp

        # core length
        temp_cell = ws_t['C2'].value
        if isinstance(temp_cell, (float, int)):
            tlength = temp_cell
        else:
            tlength = y[-1]

        # note
        temp_cell = ws_t['C3']
        if temp_cell is None:
            t_note = None
        else:
            t_note = temp_cell.value

        t = np.nan * np.empty(len(y))
        for jj in range(6, 6 + len(y)):
            ws_s_t = ws_t[openpyxl.cell.get_column_letter(2) + str('%.0f' % jj)]
            if ws_s_t is None:
                temp = missvalue
            elif isinstance(ws_s_t.value, (float, int)):
                temp = ws_s_t.value
            else:
                temp = missvalue
            t[jj - 6] = temp
            jj += 1
        imported_core.t_profile(np.array(t), np.array(y), tlength, t_note)
    return imported_core


## import all ice core data which path are given in a source text file
def importsrc(txtfilepath, section_thickness=None, missvalue=float('nan'), log_level=log_level):
    print('Ice core data importation in progress ...')
    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])
    a = open(txtfilepath)
    filepath = [line.strip() for line in a]
    filepath = sorted(filepath)
    ic_dict = {}
    for ii in range(0, len(filepath)):
        if not filepath[ii].startswith('#'):
            ic_data = importcore(filepath[ii], missvalue)
            if section_thickness is not None:
                ic_data = make_section(ic_data, section_thickness)
            ic_dict[ic_data.name] = ic_data

    logging.info('Ice core importation complete')
    print('done')

    return ic_dict


def importlist(ics_list, missvalue=missvalue, log_level='warning'):
    print('Ice core data importation in progress ...')

    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])

    ic_dict = {}
    for ii in range(0, len(ics_list)):
        print(ics_list[ii])
        ic_data = importcore(ics_list[ii], missvalue)
        ic_dict[ic_data.name] = ic_data

    logging.info('Ice core importation complete')
    print('done')

    return ic_dict
    #
    #
    # class CoreSet:
    #     def __init__(self, name, date):
    #         self.name = name
    #         self.datestamp = [date]
    #
    #         self.ice_thickness = []
    #         self.snow_depth = []
    #         self.corenames = [name]
    #
    #         self.s_profile = np.array([[]])
    #         self.sy_profile = np.array([[]])
    #         self.s_length = []
    #         self.s_legend = []
    #
    #         self.t_profile = np.array([[]])
    #         self.st_profile = np.array([[]])
    #         self.t_length = []
    #         self.t_legend = []
    #
    #         self.t_air = []
    #         self.t_snow = []
    #         self.t_ice0 = []
    #         self.t_water = []
    #
    #     def date(self):
    #         if len(self.datestamp)<2:
    #             return self.datestamp[0]
    #         else:
    #             return self.datestamp
    #
    #     def error(message):
    #         import sys
    #         sys.stderr.write("error: %s\n" % message)
    #         sys.exit(1)
    #
    #     def t_avg(self, core_to_ignore=None):
    #         if core_to_ignore is not None:
    #             if isinstance(core_to_ignore, str):
    #                 core_to_ignore = [core_to_ignore]
    #             t_bkp = [self.t_profile, self.t_length]
    #             for c in core_to_ignore:
    #                 self.del_t_profile(c)
    #         t_avg_profile = np.nanmean(self.t_profile, axis=1)
    #         t_avg_length = np.nanmax(self.t_length)
    #
    #         if core_to_ignore is not None:
    #             self.t_profile = t_bkp[0]
    #             self.t_length = t_bkp[1]
    #
    #         return t_avg_profile, t_avg_length, 't-avg'
    #
    #     def add_s_profile(self, s, s_length, core_name, dt=None):
    #         self.s_profile = icdtools.column_merge([self.s_profile, s])
    #         self.s_length.append(s_length)
    #         self.s_legend.append(core_name)
    #         if core_name not in self.corenames:
    #             self.corenames.append(core_name)
    #         if dt not in self.datestamp and dt is not None:
    #             self.date.append(dt)
    #
    #     def add_t_profile(self, t, t_length, core_name, dt=None):
    #         self.t_profile = icdtools.column_merge([self.t_profile, t])
    #         self.t_length.append(t_length)
    #         self.t_legend.append(core_name)
    #         if core_name not in self.corenames:
    #             self.corenames.append(core_name)
    #         if dt not in self.datestamp and dt is not None:
    #             self.date.append(dt)
    #
    #     @property
    #     def length(self):
    #         all_length = self.t_length + self.s_length
    #         return all_length
    #
    # #    @property
    # #    def _nanmean_(self, key):
    # #        return np.nanmean(self._keys)
    #
    #     def del_s_profile(self, s_name):
    #         if s_name in self.s_legend:
    #             index = self.s_legend.index(s_name)
    #             self.s_legend.pop(index)
    #             self.s_length.pop(index)
    #             np.delete(self.s_profile, index, axis=1)
    #             if s_name not in self.t_legend:
    #                 self.corenames.pop(s_name)
    #         else:
    #             print('selected profile does not exist')
    #
    #     def del_t_profile(self, t_name):
    #         if t_name in self.t_legend:
    #             index = self.t_legend.index(t_name)
    #             self.t_legend.pop(index)
    #             self.t_length.pop(index)
    #             np.delete(self.t_profile, index, axis=1)
    #             if t_name not in self.s_legend:
    #                 self.corenames.pop(t_name)
    #         else:
    #             print('selected profile does not exist')
    #
    #
    #     def add_t_air(self, t):
    #         self.t_air.append(t)
    #
    #     def add_t_snow(self, t):
    #         self.t_snow.append(t)
    #
    #     def add_t_ice0(self, t):
    #         self.t_ice0.append(t)
    #
    #     def add_t_water(self, t):
    #         self.water.append(t)
    #
    #     def __getattr__(self, key):
    #         return None
    #
    #     def __getstate__(self):
    #         return self.__dict__
    #
    #     def __setstate__(self, d):
    #         self.__dict__.update(d)
