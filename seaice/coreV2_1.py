#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
icecoredata.py: ice core data is a toolbox to import ice core data file from xlsx spreadsheet. Xlsx spreadsheet should be
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
            y = np.sort(np.unique(np.concatenate((profilet.y, profiles.y))))
            y = y[np.where(y <= max(max(profilet.y), max(profiles.y)))]
            y = y[np.where(y >= max(min(profilet.y), min(profiles.y)))]
            y_mid = y[0:-1] + np.diff(y) / 2

            xt = np.interp(y_mid, profilet.y, profilet.x)
            xs = np.interp(y_mid, profiles.y[:-1] + np.diff(profiles.y) / 2, profiles.x)
            x = function(xt, xs)

            note = 'computed from ' + self.profiles['temperature'].profile_label + ' temperature profile and ' + \
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
    def __init__(self, set_name, core):
        self.name = set_name
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
                except AttributeError:
                    logging.warning('core length for %s not defined' % a)
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


def import_core(ic_path, missing_value=float('nan')):
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
        ic_snow_depth = missing_value
    else:
        ic_snow_depth = temp_cell.value

    # ice thickness
    temp_cell = ws_summary['C11']
    if temp_cell is None or temp_cell.value in ['n/m', 'n/a', 'unknow']:
        ic_ice_thickness = missing_value
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
    while ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)] is not None and ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)].value is not None:
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
        s = missing_value * np.empty(len(ybin) - 1)
        for jj in range(6, 6 + len(s)):
            s_y = ws.cell(column=4, row=jj).value
            if isinstance(s_y, (float, int)):
                s[jj - 6] = s_y

        # comment
        comment = [None] * len(ybin)
        for jj in range(6, 6 + len(comment) - 1):
            comment[jj - 6] = ws.cell(column=8, row=jj).value
        comment[-1] = [ws['C3'].value]

        # length
        length = ws['C2'].value
        if length is None:
            length = ybin[-1] - ybin[0]
        elif ybin[-1] - ybin[0] < length:
            length = ybin[-1] - ybin[0]
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
        t = missing_value * np.empty(len(ybin))
        for jj in range(6, 6 + len(t)):
            t_y = ws.cell(column=2, row=jj).value
            if isinstance(t_y, (float, int)):
                t[jj - 6] = t_y

        # comment
        c = [None] * len(ybin)
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
            delta_y = (length + len(y_mid_section) * section_thickness) / 2
            if delta_y < length:
                y_mid_section = np.append(y_mid_section, np.atleast_1d(delta_y))
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


def get_filepath(data_dir, data_ext, subdir='no'):
    import os
    filepath = []
    if subdir == 'yes':
        for path, subdirs, files in os.walk(data_dir):
            subdirs.sort()
            files.sort()
            for name in files:
                if name.endswith(data_ext):
                    f = os.path.join(path, name)
                    filepath.append(f)
    else:
        files = os.listdir(data_dir)
        for name in files:
            if name.endswith(data_ext):
                f = os.path.join(data_dir, name)
                filepath.append(f)
    return filepath


def generate_source(data_dir, data_ext):
    ic_path_list = get_filepath(data_dir, data_ext)
    with open(data_dir + '/ic_list.txt', 'w') as f:
        for ii in range(0, len(ic_path_list)):
            f.write(ic_path_list[ii] + "\n")


def import_prop(ic_path, missing_value=float('nan')):
    """
    import_prop import specific ice core
    :param ic_path:
    :param missing_value:
    :return:
    """

    import openpyxl
    import datetime

    wb = openpyxl.load_workbook(filename=ic_path, use_iterators=True)  # load the xlsx spreadsheet
    ws_name = wb.get_sheet_names()

    ws_summary = wb.get_sheet_by_name('summary')  # load the data from the summary sheet

    # name
    temp_cell = ws_summary['C21']
    ic_name = temp_cell.value
    print(ic_name)

    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS['warning'])
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
    if temp_cell is None or temp_cell.value in ['n/m', 'n/a']:
        ic_snow_depth = missing_value
    else:
        ic_snow_depth = temp_cell.value

    # ice thickness
    temp_cell = ws_summary['C11']
    if temp_cell is None or temp_cell.value in ['n/m', 'n/a']:
        ic_ice_thickness = missing_value
    else:
        ic_ice_thickness = temp_cell.value

    imported_core = Core(ic_name, ic_date, ic_loc, ic_ice_thickness, ic_snow_depth)

    # surface temperature
    temp_cell = ws_summary['C15']
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a']:
        imported_core.t_air = temp_cell.value
    temp_cell = ws_summary['C16']
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a']:
        imported_core.t_snow = temp_cell.value
    temp_cell = ws_summary['C17']
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a']:
        imported_core.t_ice0 = temp_cell.value
    temp_cell = ws_summary['C18']
    if temp_cell is not None or temp_cell.value not in ['n/m', 'n/a']:
        imported_core.t_water = temp_cell.value

    ii_row = 23
    ii_col = 3
    while ws_summary.cell(column=ii_col, row=ii_row) is not None and ws_summary.cell(column=ii_col, row=ii_row).value is not None:
        imported_core.add_corenames(ws_summary[openpyxl.cell.get_column_letter(ii_col) + str('%.0f' % ii_row)].value)
        ii_col += 1

    # comment
    imported_core.comment = ws_summary['A33'].value

    # salinity spreadsheet
    if 'S_ice' in ws_name:
        ws_s = wb.get_sheet_by_name('S_ice')
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
                        x_mid = x3
            else:
                if isinstance(x1, (float, int)):
                    x_mid = (x1 + x2) / 2
            if jj == 6 and flag:
                x = x_mid
            else:
                x = x.append(x_mid)
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
                        x_mid = x3
            else:
                if isinstance(x1, (float, int)):
                    x_mid = (x1 + x2) / 2
            if jj == 6 and flag:
                x = np.array(x_mid)
            else:
                x = np.append(x, x_mid)
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
                        x_mid = x3
            else:
                if isinstance(x1, (float, int)):
                    x_mid = (x1 + x2) / 2
            if jj == 6 and flag:
                x = np.array(x_mid)
            else:
                x = np.append(x, x_mid)
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


def import_src(txt_filepath, section_thickness=None, missing_value=float('nan'), log_level='warning'):
    """
    importsrc import all ice core data which path are given in a source text file
    :param txt_filepath:
    :param section_thickness:
    :param missing_value:
    :param log_level:
    :return:
    """
    print('Ice core data importation in progress ...')
    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])
    a = open(txt_filepath)
    filepath = [line.strip() for line in a]
    filepath = sorted(filepath)
    ic_dict = {}
    for ii in range(0, len(filepath)):
        if not filepath[ii].startswith('#'):
            ic_data = import_core(filepath[ii], missing_value)
            if section_thickness is not None:
                ic_data = make_section(ic_data, section_thickness)
            ic_dict[ic_data.name] = ic_data
    logging.info('Ice core importation complete')
    print('done')
    return ic_dict


def import_list(ics_list, missing_value=float('nan'), log_level='warning'):
    print('Ice core data importation in progress ...')

    logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVELS[log_level])

    ic_dict = {}
    for ii in range(0, len(ics_list)):
        print(ics_list[ii])
        ic_data = import_core(ics_list[ii], missing_value)
        ic_dict[ic_data.name] = ic_data

    logging.info('Ice core importation complete')
    print('done')

    return ic_dict
