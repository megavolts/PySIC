#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
core.py: ice core data is a toolbox to import ice core data file from xlsx spreadsheet, formatted according to the
 template developped by the Sea Ice Group of the Geophysical Institute of the University of Alaska, Fairbanks.
 core.py integrate the module panda into the module core version 2.1 to simplify the operation and decrease
 computation time. Core profiles are considered as collection of point in depth, time and properties (salinity,
 temperature or other variable)

"""
import datetime
import logging

import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import old_script.properties
import pandas as pd

__name__ = "core"
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/05/06"
__comment__ = "core.py contained classes and function destinated to analyezed sea ice core data "
__CoreVersion__ = 1.1

# create logger
module_logger = logging.getLogger(__name__)
TOL = 1e-6
variable_2_sheet = {'temperature': 'T_ice',
                    'salinity': 'S_ice',
                    'conductivity': 'S_ice',
                    'specific conductance': 'S_ice',
                    'd18O': 'S_ice',
                    'dD': 'S_ice',
                    'Vf_oil': 'Vf_oil', 'oil volume fraction': 'Vf_oil',  # MOSIDEO project
                    'Wf_oil': 'Wf_oil', 'oil weight fraction': 'Vf_oil',  # MOSIDEO project
                    'oil content': 'oil_content',  # CMI project
                    'm_oil': 'Vf_oil', 'oil mass': 'Vf_oil'
                    # 'seawater': 'seawater',
                    # 'sediment': 'sediment',
                    # 'Chla': 'algal_pigment',
                    # 'chlorophyl a': 'algal_pigment',
                    # 'Phae': 'algal_pigment'
                    }


def compute_phys_prop_from_core(s_profile, t_profile, si_prop, si_prop_format='step', resize_core=None,
                                display_figure=False):
    """
    :param s_profile:
    :param t_profile:
    :param si_prop:
    :param si_prop_format: 'linear' or 'step':
    :param main_core: 'S', 'T', default 'None':
    :return:
    """

    # parameters check
    if isinstance(si_prop_format, dict):
        for prop in si_prop:
            if prop not in si_prop_format.keys():
                print("no format for prop %s, please define linear or step" % prop)
                si_prop.remove(prop)
        si_prop_dict = si_prop_format
    elif not isinstance(si_prop, dict):
        if not isinstance(si_prop, list):
            si_prop = [si_prop]
        if not isinstance(si_prop_format, list):
            si_prop_format = [si_prop_format]
        if si_prop_format.__len__() > 1 and not si_prop_format.__len__() == si_prop.__len__():
            module_logger.error(
                "length of si_prop format does not match length of si_prop. si_prop should be length 1 or should match length si_prop")
        si_prop_dict = {}
        for ii in range(0, si_prop.__len__()):
            si_prop_dict[si_prop[ii]] = si_prop_format[ii]
    else:
        si_prop_dict = si_prop

    # initialisation
    prop_profile = pd.DataFrame()

    # check parameters
    if 'salinity' not in s_profile.keys() or not s_profile['salinity'].notnull().any():
        print("no salinity data")
        return prop_profile
    else:
        S_core_name = s_profile.name.values[0]
        s_profile['salinity'] = pd.to_numeric(s_profile['salinity'])

    if 'temperature' not in t_profile.keys() or not t_profile['temperature'].notnull().any():
        print("no temperature data")
        return prop_profile
    else:
        T_core_name = t_profile.name.values[0]
        t_profile['temperature'] = pd.to_numeric(t_profile['temperature'])

    if resize_core in ['S', S_core_name]:
        if s_profile.core_length.notnull().all():
            profile_length = s_profile.core_length.unique()[0]
        elif s_profile.core_length.notnull().all():
            profile_length = s_profile.ice_thickness.unique()[0]
            print("ice core length unknown, using ice thickness instead")
        else:
            profile_length = max(s_profile.y_low.min(), s_profile.y_sup.max())[0]
            print("todo: need warning text")
        if not t_profile.core_length.unique() == profile_length:
            t_profile = scale_profile(t_profile, profile_length)

    if resize_core in ['T', T_core_name]:
        if t_profile.core_length.notnull().all():
            profile_length = t_profile.core_length.unique()[0]
        elif t_profile.core_length.notnull().all():
            profile_length = t_profile.ice_thickness.unique()[0]
            print("ice core length unknown, using ice thickness instead")
        else:
            profile_length = max(t_profile.y_low.min(), t_profile.y_sup.max())[0]
            print("todo: need warning text")

        if not t_profile.core_length.unique() == profile_length:
            s_profile = scale_profile(s_profile, profile_length)

    # interpolate temperature profile to match salinity profile
    y_mid = s_profile.y_mid.dropna().values
    if y_mid.__len__() < 1:
        y_mid = (s_profile.y_low / 2. + s_profile.y_sup / 2).dropna().astype(float)

    interp_data = pd.concat([t_profile, pd.DataFrame(y_mid, columns=['y_mid'])])
    interp_data = interp_data.set_index('y_mid').sort_index().interpolate(method='index').reset_index().drop_duplicates(
        subset='y_mid')

    if 'temperature' in s_profile.keys():
        s_profile = s_profile.drop('temperature', axis=1)
    s_profile = pd.merge(s_profile, interp_data[['temperature', 'y_mid']], on=['y_mid'])

    # compute properties
    for f_prop in si_prop_dict.keys():
        if f_prop not in old_script.properties.si_prop_list.keys():
            print('property %s not defined in the ice core property module' % property)

        prop = old_script.properties.si_prop_list[f_prop]
        function = getattr(old_script.properties, prop.replace(" ", "_"))
        prop_data = function(t_profile['temperature'], s_profile['salinity'])

        prop_data = pd.DataFrame(np.vstack((prop_data, s_profile['y_mid'])).transpose(), columns=[prop, 'y_mid'])
        prop_data['name'] = list(set(s_profile.name))[0]
        comment_core = 'physical properties computed from ' + S_core_name + '(S) and ' + T_core_name + '(T)'
        prop_data['variable'] = prop

        var_drop = [var for var in ['salinity', 'temperature', 'variable', f_prop, 'name', 'core'] if
                    var in s_profile.keys()]
        core_frame = s_profile.drop(var_drop, axis=1)

        if si_prop_dict[f_prop] == 'linear':
            core_frame[['y_low', 'y_sup']] = np.nan
        prop_data = pd.merge(prop_data, core_frame, how='inner', on=['y_mid'])

        for index in prop_data.index:
            if 'comment' in prop_data.keys():
                if prop_data.loc[prop_data.index == index, 'comment'].isnull().all():
                    prop_data.loc[prop_data.index == index, 'comment'] = comment_core
                else:
                    prop_data.loc[prop_data.index == index, 'comment'] += ';' + comment_core
            else:
                prop_data.loc[prop_data.index == index, 'comment'] = comment_core

        if display_figure:
            ax = plot_profile_variable(prop_data, {'name': S_core_name, 'variable': prop},
                                       ax=None, param_dict=None)
            ax.set_xlabel(prop)
            ax.set_ylabel('ice thickness)')
            ax.set_title(S_core_name)
        prop_profile = prop_profile.append(prop_data, ignore_index=True, verify_integrity=False)

    return prop_profile


def compute_phys_prop_from_core_name(ics_stack, S_core_name, T_core_name, si_prop, si_prop_format='step',
                                     resize_core=None, inplace=True, display_figure=False):
    """
    :param ics_stack:
    :param S_core_name:
    :param T_core_name:
    :param si_prop:
    :param si_prop_format: 'linear' or 'step':
    :param resize_core: 'S', 'T', default 'None':
    :return:
    """

    # parameters check
    if isinstance(si_prop_format, dict):
        if isinstance(si_prop, list):
            for prop in si_prop:
                if prop not in si_prop_format.keys():
                    print("no format for prop %s, please define linear or step" % prop)
                    si_prop.remove(prop)
            si_prop_dict = si_prop_format
        else:
            si_prop_dict = si_prop
    elif not isinstance(si_prop, dict):
        if not isinstance(si_prop, list):
            si_prop = [si_prop]
        if not isinstance(si_prop_format, list):
            si_prop_format = [si_prop_format]
        if si_prop_format.__len__() > 1 and not si_prop_format.__len__() == si_prop.__len__():
            module_logger.error(
                "length of si_prop format does not match length of si_prop. si_prop should be length 1 or should match length si_prop")
        si_prop_dict = {}
        for ii in range(0, si_prop.__len__()):
            si_prop_dict[si_prop[ii]] = si_prop_format[ii]
    else:
        si_prop_dict = si_prop

    # check parameters
    if S_core_name not in ics_stack.name.unique():
        print("%s core not present in data" % S_core_name)
        return pd.DataFrame();
    elif 'salinity' not in ics_stack.loc[ics_stack.name == S_core_name, 'variable'].unique():
        print("salinity data not existing for %s " % S_core_name)
        return pd.DataFrame();
    else:
        s_profile = ics_stack[(ics_stack.name == S_core_name) & (ics_stack.variable == 'salinity')]

    if T_core_name not in ics_stack.name.unique():
        print("%s core not present in data" % T_core_name)
        return pd.DataFrame();
    elif 'temperature' not in ics_stack.loc[ics_stack.name == T_core_name, 'variable'].unique():
        print("temperature data not existing for %s " % T_core_name)
        return pd.DataFrame();
    else:
        t_profile = ics_stack[(ics_stack.name == T_core_name) & (ics_stack.variable == 'temperature')]

    prop_profile = compute_phys_prop_from_core(s_profile, t_profile, si_prop=si_prop_dict,
                                               si_prop_format=si_prop_format, resize_core=resize_core,
                                               display_figure=display_figure)

    if inplace is True:
        for f_prop in prop_profile.variable.unique():
            if not ics_stack[(ics_stack.name == S_core_name) & (ics_stack.variable == f_prop)].empty:
                ics_stack = ics_stack[(ics_stack.name != S_core_name) | (ics_stack.variable != f_prop)]
            ics_stack = ics_stack.append(prop_profile, ignore_index=True)
        return ics_stack
    else:
        return prop_profile


def discretize_profile(profile, y_bins=None, y_mid=None, variables=None, display_figure='y', fill_gap=False):
    """
    :param profile:
    :param y_bins:
    :param y_mid:
    :param variables:
    :param display_figure:
    :param fill_gap:
    :return:
    """
    v_ref = profile.v_ref.unique()[0]

    # VARIABLES CHECK
    if y_bins is None and y_mid is None:
        y_bins = pd.Series(profile.y_low.dropna().tolist() + profile.y_sup.dropna().tolist()).sort_values().unique()
        y_mid = profile.y_mid.dropna().sort_values().unique()
    elif y_bins is None:
        if y_mid is not None:
            y_mid = y_mid.sort_values().values
            dy = np.diff(y_mid) / 2
            y_bins = np.concatenate([[y_mid[0] - dy[0]], y_mid[:-1] + dy, [y_mid[-1] + dy[-1]]])
            if y_bins[0] < 0:
                y_bins[0] = 0
    elif y_mid is None:
        if y_bins is not None:
            y_mid = np.diff(y_bins) / 2 + y_bins[:-1]
        else:
            y_mid = profile.y_mid.dropna().sort_values().unique()

    if variables is None:
        variables = [variable for variable in profile.variable.unique().tolist() if variable in profile.keys()]

    if not isinstance(variables, list):
        variables = [variables]

    for variable in variables:
        # continuous profile (temperature-like)
        profile[variable] = pd.to_numeric(profile[variable])
        if (profile[profile.variable == variable].y_low.isnull().all() and
                    profile[profile.variable == variable].y_low.__len__() > 0):
            yx = profile[profile.variable == variable].set_index('y_mid').sort_index()[[variable]]
            y2x = yx.reindex(y_mid)
            for index in yx.index:
                y2x.loc[abs(y2x.index - index) < 1e-6, variable] = yx.loc[yx.index == index, variable].values
            if np.isnan(y2x[variable].astype(float)).all():
                dat_temp = np.interp(y2x.index, yx.index, yx[variable].astype(float), left=np.nan, right=np.nan)
                y2x = pd.DataFrame(dat_temp, index=y2x.index, columns=[variable])
            else:
                y2x.ix[(y2x.index <= max(yx.index)) & (min(yx.index) <= y2x.index)] = y2x.interpolate(method='index')[
                    (y2x.index <= max(yx.index)) & (min(yx.index) <= y2x.index)]
            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(y_mid.__len__()))
            temp.update(y2x.reset_index())

            profile_prop = profile.head(1)
            profile_prop = profile_prop.drop(variable, 1)
            profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            profile_prop = profile_prop.drop('y_sup', 1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))
            temp['date'] = temp['date'].astype('datetime64[ns]')

            if display_figure == 'y' or display_figure == 'c':
                if display_figure == 'c':
                    plt.close()
                plt.figure()
                yx = yx.reset_index()
                plt.plot(yx[variable], yx['y_mid'], 'k')
                plt.plot(temp[variable], temp['y_mid'], 'xr')
                plt.title(profile_prop.name.unique()[0] + ' - ' + variable)

        # step profile (salinity-like)
        elif (not profile[profile.variable == variable].y_low.isnull().any() and
                      profile[profile.variable == variable].y_low.__len__() > 0):
            if v_ref == 'bottom':
                yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                    ['y_sup', 'y_low', variable])
            else:
                yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                    ['y_low', 'y_sup', variable])
            x_step = []
            y_step = []
            ii_bin = 0
            if yx[0, 0] < y_bins[0]:
                ii_yx = np.where(yx[:, 0] <= y_bins[0])[0][-1]
            else:
                ii_yx = 0
                while y_bins[ii_bin] < yx[ii_yx, 0]:
                    y_step.append(y_bins[ii_bin])
                    y_step.append(y_bins[ii_bin + 1])
                    x_step.append(np.nan)
                    x_step.append(np.nan)
                    ii_bin += 1
                    y_bins[ii_bin]

            while ii_bin < y_bins.__len__() - 1:
                while y_bins[ii_bin + 1] <= yx[ii_yx, 1]:
                    S = s_nan(yx, ii_yx, fill_gap)
                    y_step.append(y_bins[ii_bin])
                    y_step.append(y_bins[ii_bin + 1])
                    x_step.append(S)
                    x_step.append(S)
                    ii_bin += 1

                    if ii_bin == y_bins.__len__() - 1:
                        break

                L = (yx[ii_yx, 1] - y_bins[ii_bin])
                S = (yx[ii_yx, 1] - y_bins[ii_bin]) * s_nan(yx, ii_yx, fill_gap)

                while ii_yx < len(yx[:, 1]) - 1 and yx[ii_yx + 1, 1] <= y_bins[ii_bin + 1]:
                    L += (yx[ii_yx + 1, 1] - yx[ii_yx + 1, 0])
                    S += (yx[ii_yx + 1, 1] - yx[ii_yx + 1, 0]) * s_nan(yx, ii_yx + 1, fill_gap)
                    ii_yx += 1
                    if ii_yx == yx[:, 1].__len__() - 1:
                        break

                if ii_bin + 1 == y_bins.__len__():
                    break

                if yx[ii_yx, 1] <= y_bins[ii_bin + 1] and ii_yx + 1 < yx.__len__():
                    L += (y_bins[ii_bin + 1] - yx[ii_yx + 1, 0])
                    S += (y_bins[ii_bin + 1] - yx[ii_yx + 1, 0]) * s_nan(yx, ii_yx + 1, fill_gap)
                S = S / L
                if S != 0:
                    y_step.append(y_bins[ii_bin])
                    y_step.append(y_bins[ii_bin + 1])
                    x_step.append(S)
                    x_step.append(S)
                    ii_bin += 1
                ii_yx += 1
                if y_bins[ii_bin] >= yx[-1, 1]:
                    while ii_bin + 1 < y_bins.__len__():
                        y_step.append(y_bins[ii_bin])
                        y_step.append(y_bins[ii_bin + 1])
                        x_step.append(np.nan)
                        x_step.append(np.nan)
                        ii_bin += 1

            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(y_bins[:-1].__len__()))
            temp.update(pd.DataFrame(np.vstack((y_bins[:-1], y_bins[:-1] + np.diff(y_bins) / 2, y_bins[1:],
                                                [x_step[2 * ii] for ii in
                                                 range(int(x_step.__len__() / 2))])).transpose(),
                                     columns=['y_low', 'y_mid', 'y_sup', variable], index=temp.index))

            # properties
            profile_prop = profile.head(1)
            profile_prop = profile_prop.drop(variable, 1)
            profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            profile_prop = profile_prop.drop('y_sup', 1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))
            temp['date'] = temp['date'].astype('datetime64[ns]')

            if display_figure == 'y' or display_figure == 'c':
                if display_figure == 'c':
                    plt.close()
                plt.figure()
                x = []
                y = []
                for ii in range(yx[:, 0].__len__()):
                    y.append(yx[ii, 0])
                    y.append(yx[ii, 1])
                    x.append(yx[ii, 2])
                    x.append(yx[ii, 2])
                plt.step(x, y, 'bx')
                plt.step(x_step, y_step, 'ro')
                plt.title(profile_prop.name.unique()[0] + ' - ' + variable)

        profile = profile[(profile.name != profile.name.unique().tolist()[0]) | (profile.variable != variable)]
        profile = profile.append(temp)

        if 'index' in profile.columns:
            profile.drop('index', axis=1)
    return CoreStack(profile)


def discretize_profileV2(profile, y_bins=None, y_mid=None, variables=None, display_figure='y', fill_gap=True):
    """
    :param profile:
    :param y_bins:
    :param y_mid:
    :param variables:
    :param display_figure:
    :param fill_gap:
    :return:
    """

    if profile.empty:
        return CoreStack(profile)

    v_ref = profile.v_ref.unique()[0]

    # VARIABLES CHECK
    if y_bins is None and y_mid is None:
        y_bins = pd.Series(profile.y_low.dropna().tolist() + profile.y_sup.dropna().tolist()).sort_values().unique()
        y_mid = profile.y_mid.dropna().sort_values().unique()
    elif y_bins is None:
        if y_mid is not None:
            y_mid = y_mid.sort_values().values
            dy = np.diff(y_mid) / 2
            y_bins = np.concatenate([[y_mid[0] - dy[0]], y_mid[:-1] + dy, [y_mid[-1] + dy[-1]]])
            if y_bins[0] < 0:
                y_bins[0] = 0
    elif y_mid is None:
        if y_bins is not None:
            y_mid = np.diff(y_bins) / 2 + y_bins[:-1]
        else:
            y_mid = profile.y_mid.dropna().sort_values().unique()

    y_bins = np.array(y_bins)
    y_mid = np.array(y_mid)

    if variables is None:
        variables = [variable for variable in profile.variable.unique().tolist() if variable in profile.keys()]

    if not isinstance(variables, list):
        variables = [variables]

    discretized_profile = pd.DataFrame()

    module_logger.debug("Processing %s" % profile.name.unique()[0])
    # print("Processing %s" %profile.name.unique()[0])

    for variable in variables:
        profile[variable] = pd.to_numeric(profile[variable])
        temp = pd.DataFrame()

        if profile[profile.variable == variable].empty:
            module_logger.debug("no %s data" % (variable))
        else:
            module_logger.debug("%s data discretized" % variable)
            # print("\t%s data discretized" % (variable))
        # continuous profile (temperature-like)
        if (profile[profile.variable == variable].y_low.isnull().all() and
                    profile[profile.variable == variable].y_low.__len__() > 0):
            yx = profile[profile.variable == variable].set_index('y_mid').sort_index()[[variable]]
            y2x = yx.reindex(y_mid)
            for index in yx.index:
                y2x.loc[abs(y2x.index - index) < 1e-6, variable] = yx.loc[yx.index == index, variable].values
            # if np.isnan(y2x[variable].astype(float)).all():
            dat_temp = np.interp(y2x.index, yx.index, yx[variable].astype(float), left=np.nan, right=np.nan)
            y2x = pd.DataFrame(dat_temp, index=y2x.index, columns=[variable])
            # else:
            #    y2x.ix[(y2x.index <= max(yx.index)) & (min(yx.index) <= y2x.index)] = y2x.interpolate(method='index')[(y2x.index <= max(yx.index)) & (min(yx.index) <= y2x.index)]
            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(y_mid.__len__()))
            temp.update(y2x.reset_index())

            profile_prop = profile.head(1)
            profile_prop = profile_prop.drop(variable, 1)
            profile_prop['variable'] = variable
            profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            profile_prop = profile_prop.drop('y_sup', 1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))
            temp['date'] = temp['date'].astype('datetime64[ns]')

            if display_figure == 'y' or display_figure == 'c':
                if display_figure == 'c':
                    plt.close()
                plt.figure()
                yx = yx.reset_index()
                plt.plot(yx[variable], yx['y_mid'], 'k')
                plt.plot(temp[variable], temp['y_mid'], 'xr')
                plt.title(profile_prop.name.unique()[0] + ' - ' + variable)

        # step profile (salinity-like)
        elif (not profile[profile.variable == variable].y_low.isnull().all() and
                      profile[profile.variable == variable].y_low.__len__() > 0):
            if v_ref == 'bottom':
                yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                    ['y_sup', 'y_low', variable])
                if yx[0, 0] > yx[0, 1]:
                    yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                        ['y_low', 'y_sup', variable])
            else:
                yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                    ['y_low', 'y_sup', variable])
            x_step = []
            y_step = []
            ii_bin = 0
            if yx[0, 0] < y_bins[0]:
                ii_yx = np.where(yx[:, 0] - y_bins[0] <= TOL)[0][-1]
            else:
                ii_bin = np.where(y_bins - yx[0, 0] <= TOL)[0][-1]
                ii_yx = 0
                ii = 0
                while ii < ii_bin:
                    y_step.append(y_bins[ii])
                    y_step.append(y_bins[ii + 1])
                    x_step.append(np.nan)
                    x_step.append(np.nan)
                    ii += 1

            while ii_bin < y_bins.__len__() - 1:
                while ii_bin + 1 < y_bins.__len__() and y_bins[ii_bin + 1] - yx[ii_yx, 1] <= TOL:
                    S = s_nan(yx, ii_yx, fill_gap)
                    y_step.append(y_bins[ii_bin])
                    y_step.append(y_bins[ii_bin + 1])
                    x_step.append(S)
                    x_step.append(S)
                    ii_bin += 1
                    # plt.step(x_step, y_step, 'ro')
                    # if ii_bin == y_bins.__len__() - 1:
                    #    break

                if not yx[-1, 1] - y_bins[ii_bin] <= TOL:
                    L = 0
                    S = 0
                    if ii_yx < yx[:, 0].__len__() - 1:
                        while ii_yx < yx[:, 0].__len__() - 1 and yx[ii_yx, 1] - y_bins[ii_bin + 1] <= TOL:
                            L += (yx[ii_yx, 1] - y_bins[ii_bin])
                            S += (yx[ii_yx, 1] - y_bins[ii_bin]) * s_nan(yx, ii_yx, fill_gap)
                            ii_yx += 1

                            # ABOVE
                            # while ii_yx < len(yx[:, 1]) - 1 and yx[ii_yx + 1, 1] - y_bins[ii_bin + 1] <= TOL:
                            #    L += (yx[ii_yx + 1, 1] - yx[ii_yx + 1, 0])
                            #    S += (yx[ii_yx + 1, 1] - yx[ii_yx + 1, 0]) * s_nan(yx, ii_yx + 1, fill_gap)
                            #    ii_yx += 1
                            #    if ii_yx == yx[:, 1].__len__() - 1:
                            #        break
                            #   break
                        if yx[ii_yx, 0] - y_bins[ii_bin + 1] <= TOL:
                            S += (y_bins[ii_bin + 1] - yx[ii_yx, 0]) * s_nan(yx, ii_yx, fill_gap)
                            L += y_bins[ii_bin + 1] - yx[ii_yx, 0]
                        if L > TOL:
                            S = S / L
                        else:
                            S = np.nan

                    else:
                        S = yx[-1, -1]
                        # y_step.append(y_bins[ii_bin])
                        # y_step.append(y_bins[ii_bin + 1])
                        # x_step.append(S)
                        # x_step.append(S)
                        # ii_bin += 1
                    # ABOVE
                    # if yx[ii_yx, 1] - y_bins[ii_bin + 1] <= TOL and ii_yx + 1 < yx.__len__():
                    #     if np.isnan(s_nan(yx, ii_yx + 1, fill_gap)) and not np.isnan(S) and y_bins[ii_bin + 1] - yx[ii_yx+1, 1] < TOL:
                    #         S += S/L*(y_bins[ii_bin + 1] - yx[ii_yx + 1, 0])
                    #     else:
                    #         S += (y_bins[ii_bin + 1] - yx[ii_yx + 1, 0]) * s_nan(yx, ii_yx + 1, fill_gap)
                    #     L += (y_bins[ii_bin + 1] - yx[ii_yx + 1, 0])

                    # if S != 0 : #and y_bins[ii_bin] - yx[ii_yx, 1] < TOL:
                    y_step.append(y_bins[ii_bin])
                    y_step.append(y_bins[ii_bin + 1])
                    x_step.append(S)
                    x_step.append(S)
                    ii_bin += 1
                    # plt.step(x_step, y_step, 'ro')

                else:
                    while ii_bin + 1 < y_bins.__len__():
                        y_step.append(y_bins[ii_bin])
                        y_step.append(y_bins[ii_bin + 1])
                        x_step.append(np.nan)
                        x_step.append(np.nan)
                        ii_bin += 1

            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(np.unique(y_step).__len__() - 1))
            temp.update(pd.DataFrame(np.vstack(
                (np.unique(y_step)[:-1], np.unique(y_step)[:-1] + np.diff(np.unique(y_step)) / 2, np.unique(y_step)[1:],
                 [x_step[2 * ii] for ii in
                  range(int(x_step.__len__() / 2))])).transpose(),
                                     columns=['y_low', 'y_mid', 'y_sup', variable],
                                     index=temp.index[0:np.unique(y_step).__len__() - 1]))

            # properties
            profile_prop = profile.head(1)
            profile_prop = profile_prop.drop(variable, 1)
            profile_prop['variable'] = variable
            profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            profile_prop = profile_prop.drop('y_sup', 1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))
            temp['date'] = temp['date'].astype('datetime64[ns]')

            if display_figure == 'y' or display_figure == 'c':
                if display_figure == 'c':
                    plt.close()
                plt.figure()
                x = []
                y = []
                for ii in range(yx[:, 0].__len__()):
                    y.append(yx[ii, 0])
                    y.append(yx[ii, 1])
                    x.append(yx[ii, 2])
                    x.append(yx[ii, 2])
                plt.step(x, y, 'bx')
                plt.step(x_step, y_step, 'ro')
                plt.title(profile_prop.name.unique()[0] + ' - ' + variable)

                # profile = profile[(profile.name != profile.name.unique().tolist()[0]) | (profile.variable != variable)]
        discretized_profile = discretized_profile.append(temp)

        # if temp.empty:
        #    print(profile.name.unique())
        # else:
        #    profile = profile.append(temp)

        # if 'index' in discretized_profile.columns:
        #    discretized_profile.drop('index', axis=1)
    return CoreStack(discretized_profile)


# HELPER
def s_nan(yx, ii_yx, fill_gap=True):
    """
    :param yx:
    :param ii_yx:
    :param fill_gap:
    :return:
    """
    if np.isnan(yx[ii_yx, 2]) and fill_gap:
        ii_yx_l = ii_yx - 1
        while ii_yx_l > 0 and np.isnan(yx[ii_yx_l, 2]):
            ii_yx_l -= 1
        s_l = yx[ii_yx_l, 2]

        ii_yx_s = ii_yx
        while ii_yx_s < yx.shape[0] - 1 and np.isnan(yx[ii_yx_s, 2]):
            ii_yx_s += 1
        s_s = yx[ii_yx_s, 2]

        s = (s_s + s_l) / 2
    else:
        s = yx[ii_yx, 2]
    return s


# --------------------------#

# OK

# OK
def plot_mean_envelop(ic_data, variable_dict, ax=None, param_dict=None):
    """

    :param ic_data:
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if param_dict is None:
        param_dict = {}

    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0

    ii_variable = variable_dict['variable']

    variable_dict.update({'stats': 'mean'})
    x_mean = select_profile(ic_data, variable_dict).reset_index()
    variable_dict.update({'stats': 'std'})
    x_std = select_profile(ic_data, variable_dict).reset_index()

    if x_mean.__len__() != 0:
        if x_std.__len__() < x_mean.__len__():
            index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
            x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))

        if not x_mean.y_low.isnull().all():
            y_low = x_mean['y_low']
            y_sup = x_mean['y_sup']
            y = np.concatenate((y_low.tolist(), [y_sup.tolist()[-1]]))
            x_std_l = x_mean[ii_variable] - x_std[ii_variable]
            x_std_h = x_mean[ii_variable] + x_std[ii_variable]

            x_std_l = seaice.toolbox.plt_step(x_std_l.tolist(), y).transpose()
            x_std_h = seaice.toolbox.plt_step(x_std_h.tolist(), y).transpose()
        elif x_mean.y_low.isnull().all():
            y_std = x_mean['y_mid']
            x_std_l = np.array([x_mean[ii_variable] - np.nan_to_num(x_std[ii_variable]), y_std])
            x_std_h = np.array([x_mean[ii_variable] + np.nan_to_num(x_std[ii_variable]), y_std])

        if 'facecolor' not in param_dict.keys():
            param_dict['facecolor'] = {'black'}
        if 'alpha' not in param_dict.keys():
            param_dict['alpha'] = {0.3}
        if 'label' not in param_dict.keys():
            param_dict['label'] = str(r"$\pm$" + "std dev")
        ax.fill_betweenx(x_std_l[1, :], x_std_l[0, :], x_std_h[0, :], facecolor='black', alpha=0.2,
                         label=param_dict['label'])
    return ax


def semilogx_mean_envelop(ic_data, variable_dict, ax=None, param_dict=None):
    """

    :param ic_data:
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if param_dict is None:
        param_dict = {}

    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0

    ii_variable = variable_dict['variable']

    variable_dict.update({'stats': 'mean'})
    x_mean = select_profile(ic_data, variable_dict).reset_index()
    variable_dict.update({'stats': 'std'})
    x_std = select_profile(ic_data, variable_dict).reset_index()

    if x_mean.__len__() != 0:
        if x_std.__len__() < x_mean.__len__():
            index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
            x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))

        if not x_mean.y_low.isnull().all():
            y_low = x_mean['y_low']
            y_sup = x_mean['y_sup']
            y = np.concatenate((y_low.tolist(), [y_sup.tolist()[-1]]))
            x_std_l = x_mean[ii_variable] - x_std[ii_variable]
            x_std_h = x_mean[ii_variable] + x_std[ii_variable]

            index_outlier = x_std_l[(x_std_l <= 0)].index.tolist()
            for ii in index_outlier:
                l = ''
                for key in variable_dict:
                    l += key + ': ' + variable_dict[key] + '; '
                l = l[:-2]
                module_logger.warning('%s index of %s bin modified lower value for logarithmic scale' % (ii, l))

            ii_outlier = 1
            if index_outlier.__len__() > 0:
                variable_dict.update({'stats': 'min'})
                x_min = select_profile(ic_data, variable_dict).reset_index(drop=True)
                while index_outlier.__len__() > 0:
                    # for index in index_outlier:
                    x_std_l[(x_std_l <= 0)] = x_min.loc[x_min.index.isin(index_outlier), ii_variable] - x_std.loc[
                                                                                                            x_std.index.isin(
                                                                                                                index_outlier), ii_variable] / ii_outlier
                    index_outlier = x_std_l[(x_std_l <= 0)].index.tolist()
                    ii_outlier += 1

            x_std_l = seaice.toolbox.plt_step(x_std_l.tolist(), y).transpose()
            x_std_h = seaice.toolbox.plt_step(x_std_h.tolist(), y).transpose()
        elif x_mean.y_low.isnull().all():
            y_std = x_mean['y_mid']
            x_std_l = np.array([x_mean[ii_variable] - np.nan_to_num(x_std[ii_variable]), y_std])
            x_std_h = np.array([x_mean[ii_variable] + np.nan_to_num(x_std[ii_variable]), y_std])

        if 'facecolor' not in param_dict.keys():
            param_dict['facecolor'] = {'black'}
        if 'alpha' not in param_dict.keys():
            param_dict['alpha'] = {0.3}
        if 'label' not in param_dict.keys():
            param_dict['label'] = str(r"$\pm$" + "std dev")

        ax.fill_betweenx(x_std_l[1, :], x_std_l[0, :], x_std_h[0, :], facecolor='black', alpha=0.2,
                         label=param_dict['label'])
    return ax


# OK
def plot_number(ic_data, variable_dict, ax=None, position='right', x_delta=0.1, z_delta=0.05, every=1,
                fontsize=mpl.rcParams['font.size']):
    """
    :param ic_data:
    :param variable_dict:
    :param ax:
    :param position:
    :param x_delta:
    :param z_delta:
    :param every:
    :param fontsize:
    :return:
    """
    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0

    ii_variable = variable_dict['variable']

    if position == 'left':
        stat = 'min'
    elif position == 'center':
        stat = 'mean'
    else:
        stat = 'max'

    depth = select_profile(ic_data, variable_dict).reset_index()['y_mid'].values
    n = select_profile(ic_data, variable_dict).reset_index()['n'].values
    variable_dict.update({'stats': stat})
    pos = select_profile(ic_data, variable_dict).reset_index()[ii_variable].values

    # check for nan value:
    depth = depth[~np.isnan(pos)]
    n = n[~np.isnan(pos)]
    pos = pos[~np.isnan(pos)]

    for ii in np.arange(0, pos.__len__(), every):
        ax.text(pos[ii] + x_delta, depth[ii] + z_delta, str('(%.0f)' % n[ii]), fontsize=fontsize)

    return ax


def ice_core_stat(ics_subset, variables, stats, ic_subset_name='average core'):
    """
    :param ics_subset:
    :param variables:
    :param stats:
        accept as statistical function all the main function of pandas.
    :param ic_subset_name:
    :return:
    """
    if 'y_low' not in ics_subset.keys() or np.isnan(ics_subset['y_low'].values.astype(float)).all():
        y_bins = np.unique(ics_subset.y_mid.values)
        y_bins = list(y_bins[:-1] - np.diff(y_bins) / 2) + list(y_bins[-2:] + np.diff(y_bins)[-2:] / 2)
    else:
        y_bins = np.unique(np.concatenate((ics_subset.y_low.values, ics_subset.y_sup.values)))
    y_cuts = pd.cut(ics_subset.y_mid, y_bins, labels=False)
    data_grouped = ics_subset.groupby([y_cuts])

    data = CoreStack()
    for ii_variable in variables:

        # core data
        columns = ['y_low', 'y_sup', 'y_mid']
        if not ics_subset[ics_subset.variable == ii_variable].y_low.isnull().any():
            data_core = [[y_bins[ii_layer], y_bins[ii_layer + 1], (y_bins[ii_layer] + y_bins[ii_layer + 1]) / 2] for
                         ii_layer in range(0, y_bins.__len__() - 1)]
        elif ics_subset[ics_subset.variable == ii_variable].y_low.isnull().all():
            data_core = [[np.nan, np.nan, (y_bins[ii_layer] + y_bins[ii_layer + 1]) / 2] for ii_layer in
                         range(0, y_bins.__len__() - 1)]
        data_core = pd.DataFrame(data_core, columns=columns)
        data_core['name'] = ic_subset_name
        data_core['variable'] = ii_variable

        # stat variable
        for ii_stat in stats:
            print('computing %s' % ii_stat)
            func = "groups['" + ii_variable + "']." + ii_stat + "()"
            data_stat = [[None, None, None] for x in range(y_bins.__len__())]
            for k1, groups in data_grouped:
                data_stat[k1][0] = eval(func)
                temp = list(groups.dropna(subset=[ii_variable])['name'].unique())
                data_stat[k1][1] = temp.__len__()
                data_stat[k1][2] = ', '.join(temp)

            data_stat = pd.DataFrame(data_stat[:-1], columns=[ii_variable, 'n', 'core_collection'])
            data_stat['stat'] = ii_stat
            if data.empty:
                data = pd.concat([data_core, data_stat], axis=1)
            else:
                print(ii_stat)
                data = data.append(pd.concat([data_core, data_stat], axis=1), ignore_index=True)
        data.reset_index()
    return data


def DD_fillup(ics_stack, DD, freezup_dates):
    import datetime

    for f_day in ics_stack.date.unique():
        # look for freezup_day
        if isinstance(f_day, np.datetime64):
            f_day = datetime.datetime.utcfromtimestamp(
                (f_day - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's'))
        f_day = datetime.datetime(f_day.year, f_day.month, f_day.day)
        if f_day < datetime.datetime(f_day.year, 9, 1):
            freezup_day = datetime.datetime.fromordinal(freezup_dates[f_day.year])
        else:
            freezup_day = datetime.datetime.fromordinal(freezup_dates[f_day.year + 1])

        # look for number of freezing/thawing degree day:
        if DD[f_day][1] < 0:
            ics_stack.loc[ics_stack.date == f_day, 'DD'] = DD[f_day][1]
        else:
            ics_stack.loc[ics_stack.date == f_day, 'DD'] = DD[f_day][0]

        ics_stack.loc[ics_stack.date == f_day, 'FDD'] = DD[f_day][0]
        ics_stack.loc[ics_stack.date == f_day, 'TDD'] = DD[f_day][1]
        ics_stack.loc[ics_stack.date == f_day, 'freezup_day'] = ['a']
        ics_stack.loc[ics_stack.date == f_day, 'freezup_day'] = [freezup_day]
    return CoreStack(ics_stack)


def stack_DD_fud(ics_data, DD, freezup_dates):
    ics_data_stack = CoreStack()
    for ii_core in ics_data.keys():
        core = ics_data[ii_core]
        ics_data_stack = ics_data_stack.add_profiles(core.profiles)

    for ii_day in ics_data_stack.date.unique():
        variable_dict = {'date': ii_day}
        ii_day = pd.DatetimeIndex([ii_day])[0].to_datetime()

        # freezup day:
        if ii_day < datetime.datetime(ii_day.year, 9, 1):
            freezup_day = datetime.datetime.fromordinal(freezup_dates[ii_day.year - 1])
        else:
            freezup_day = datetime.datetime.fromordinal(freezup_dates[ii_day.year])
        # DD
        if DD[ii_day][1] < 0:
            data = [[DD[ii_day][0], DD[ii_day][1], DD[ii_day][1], np.datetime64(freezup_day)]]
        else:
            data = [[DD[ii_day][0], DD[ii_day][1], DD[ii_day][0], np.datetime64(freezup_day)]]
        data_label = ['date', 'FDD', 'TDD', 'DD', 'freezup_day']
        data = pd.DataFrame(data, columns=data_label)

        ics_data_stack = ics_data_stack.add_variable(variable_dict, data)
    return ics_data_stack


def plot_state_variable(profile_stack, ax=None, variables='state variables', color_map='core'):
    """
    :param profile_stack:
    :param ax:
    :param variables:
        default 'state variables' which plot salinity and temperature
    :param color:
    :return:
    """
    if variables == None:
        variables = np.unique(profile_stack.variable).tolist()
    elif not isinstance(variables, list):
        variables = [variables]
    elif variables == 'state variables':
        variables = ['salinity, temperature']

    if ax is None:
        fig = plt.figure()
        ax = []
        for ii in range(len(variables)):
            ax.append(plt.subplot(1, len(variables), ii + 1))
    elif len(ax) != len(variables):
        logging.warning('ax (len %d) and variables (len %d) should be of same size' % (len(ax), len(variables)))
        return None

    # colors
    color = {}
    if color_map is 'core':
        n_core = np.unique(profile_stack.core_name).__len__()
        color[ii] = [cm.jet(float(ii) / n_core) for ii in n_core]
    elif color_map is 'year':
        n_year = pd.unique([ii.year for ii in profile_stack.date]).__len__()
        color[ii] = [cm.jet(float(ii) / n_year) for ii in n_year]

    for ii in len(variables):
        var = variables[ii]


def drop_profile(data, core_name, keys):
    data = data[(data.core_name != core_name) | (data.variable != keys)]
    return data


## DEPRECATED make_section, replace with discretize_profile
def make_section(core, variables=None, status='DEPRECATED', section_thickness=0.05):
    logging.error('DEPRECATION ERROR bottom reference is deprecated, use ics_stack.set_reference("bottom") instead')
    return None


# def make_section(core, variables=None, section_thickness=0.05):
#     """
#     :param core:
#     :param variables:
#     :param section_thickness:
#     """
#     if variables is None:
#         variables = sorted(core.profiles.keys())
#     if not isinstance(variables, list):
#         variables = [variables]
#
#     for ii_profile in variables:
#         profile = core.profiles[ii_profile]
#         if core.ice_thickness is not None and ~np.isnan(core.ice_thickness):
#             ice_thickness = core.ice_thickness
#         else:
#             ice_thickness = core.profiles.loc[core.profiles.variable=='salinity', 'core_length'].unique()
#
#         y_mid_section = np.arange(section_thickness / 2, ice_thickness, section_thickness)
#         delta_y = (ice_thickness + len(y_mid_section) * section_thickness) / 2
#
#         if delta_y < ice_thickness:
#             y_mid_section = np.append(y_mid_section, np.atleast_1d(delta_y))
#         x = np.array(core.profiles[ii_profile])
#         y = np.array(core.profiles[ii_profile])
#
#         if len(y) is len(x) + 1:
#             y = (y[1:] + y[:-1]) / 2
#
#         x_mid_section = np.interp(y_mid_section, y[~np.isnan(y)], x[~np.isnan(y)], left=np.nan, right=np.nan)
#
#         profile.x = x_mid_section
#         profile.y = y_mid_section
#         core.add_comment(
#             'artificial section thickness computed with a vertical resolution of ' + str(section_thickness) + 'm')
#         core.del_profile(ii_profile)
#         core.add_profile(profile)
#     return core


def scale_profile(profile, h_ice_f):
    """
    :param profile:
        CoreStack, ice core profile to scale to a target ice thickness
    :param h_ice_f:
        scalar, target ice thickness
    :return:
    """

    if profile.core_length.unique().size and ~np.isnan(profile.core_length.unique()[0]):
        h_ice = profile.core_length.unique()[0]
    elif profile.ice_thickness.unique().size and ~np.isnan(profile.ice_thickness.unique()[0]):
        h_ice = profile.ice_thickness.unique()[0]
    else:
        logging.error("Scale: no core length or ice thickness given for %s" % profile.core_name.unique()[0])
        return 0

    r = h_ice_f / h_ice
    if r == 1:
        return profile
    profile[['y_low', 'y_mid', 'y_sup']] = r * profile[['y_low', 'y_mid', 'y_sup']]
    profile.core_length = h_ice_f
    return profile


# DEPRECATED
def compute_phys_prop(ics_data, si_prop, S_core_name, T_core_name, si_prop_format='linear', resize_core=None):
    """
    :param ic_data:
        dict of ice core
    :param si_prop:
        physical properties or list of physical properties
    :param si_prop_format: 'linear' or 'step'
    :return:
    """
    print("comput_phys_prop is deprecated. use compute_phys_from_core_name instead")
    if not isinstance(si_prop, list):
        si_prop = [si_prop]

    ## function variable:
    property_stack = pd.DataFrame()

    ## check parameters
    if S_core_name not in ics_data.keys() or 'salinity' not in ics_data[S_core_name].profile.variable.unique():
        print("missing salinity core")
        return property_stack;
    else:
        s_data = ics_data[S_core_name].profile
        s_data = s_data.loc[s_data.variable == 'salinity']
    if T_core_name not in ics_data.keys() or 'temperature' not in ics_data[T_core_name].profile.variable.unique():
        print("missing temperature core")
        return property_stack;
    else:
        t_data = ics_data[T_core_name].profile
        t_data = t_data.loc[t_data.variable == 'temperature', ['y_mid', 'temperature']]

    # interpolate temperature profile to match salinity profile
    y_mid = s_data.y_mid.dropna().tolist()
    if y_mid.__len__() < 1:
        y_mid = (s_data.y_low / 2 + s_data.y_sup / 2).tolist()

    interp_data = pd.concat([t_data, pd.DataFrame(y_mid, columns=['y_mid'])])
    interp_data = interp_data.set_index('y_mid').sort_index().interpolate(method='index').reset_index().drop_duplicates(
        subset='y_mid')

    data = s_data
    if 'temperature' in s_data.keys():
        data = s_data.drop('temperature', axis=1)
    data = pd.merge(data, interp_data, on=['y_mid'])

    for f_prop in si_prop:
        if f_prop not in old_script.properties.si_prop_list.keys():
            print('property %s not defined in the ice core property module' % property)

        prop = old_script.properties.si_prop_list[f_prop]
        function = getattr(old_script.properties, prop.replace(" ", "_"))
        prop_data = function(data['temperature'], data['salinity'])

        property_frame = pd.DataFrame(np.vstack((prop_data, y_mid)).transpose(), columns=[prop, 'y_mid'])
        property_frame['name'] = list(set(s_data.name))[0]
        property_frame[
            'comment_core'] = 'physical properties computed from ' + S_core_name + '(S) and ' + T_core_name + '(T)'
        property_frame['variable'] = prop

        var_drop = [var for var in ['salinity', 'temperature', 'variable', 'name', 'core'] if var in s_data.keys()]
        core_frame = s_data.drop(var_drop, axis=1)

        if si_prop_format == 'linear':
            core_frame = core_frame.drop(['y_sup', 'y_low'], axis=1)

        prop_data = pd.merge(property_frame, core_frame, how='inner', on=['y_mid'])

        property_stack = property_stack.append(prop_data, ignore_index=True, verify_integrity=False)

    return property_stack


def grouped_stat(ics_stack, variables, stats, bins_DD, bins_y, comment=False):
    ics_stack = ics_stack.reset_index(drop=True)
    y_cuts = pd.cut(ics_stack.y_mid, bins_y, labels=False)
    t_cuts = pd.cut(ics_stack.DD, bins_DD, labels=False)

    if not isinstance(variables, list):
        variables = [variables]
    if not isinstance(stats, list):
        stats = [stats]

    temp_all = pd.DataFrame()
    for ii_variable in variables:
        if comment:
            print('\ncomputing %s' % ii_variable)
        data = ics_stack[ics_stack.variable == ii_variable]
        data_grouped = data.groupby([t_cuts, y_cuts])

        for ii_stat in stats:
            if comment:
                print('\tcomputing %s' % ii_stat)
            func = "groups['" + ii_variable + "']." + ii_stat + "()"
            stat_var = np.nan * np.ones((bins_DD.__len__() - 1, bins_y.__len__() - 1))
            core_var = [[[None] for x in range(bins_y.__len__())] for y in range(bins_DD.__len__() - 1)]
            for k1, groups in data_grouped:
                stat_var[int(k1[0]), int(k1[1])] = eval(func)
                core_var[int(k1[0])][int(k1[1])] = [list(groups.dropna(subset=[ii_variable])
                                                         ['name'].unique())]
            for ii_bin in range(stat_var.__len__()):
                temp = pd.DataFrame(stat_var[ii_bin], columns=[ii_variable])
                temp = temp.join(pd.DataFrame(core_var[ii_bin], columns=['core collection']))
                DD_label = 'DD-' + str(bins_DD[ii_bin]) + '_' + str(bins_DD[ii_bin + 1])
                data = [str(bins_DD[ii_bin]), str(bins_DD[ii_bin + 1]), DD_label, int(ii_bin), ii_stat,
                        ii_variable, ics_stack.v_ref.unique()[0]]
                columns = ['DD_min', 'DD_max', 'DD_label', 'DD_index', 'stats', 'variable', 'v_ref']
                index = np.array(temp.index.tolist())  # [~np.isnan(temp[ii_variable].tolist())]
                temp = temp.join(pd.DataFrame([data], columns=columns, index=index))
                temp = temp.join(pd.DataFrame(index, columns=['y_index'], index=index))
                for row in temp.index.tolist():
                    temp.loc[temp.index == row, 'n'] = temp.loc[temp.index == row, 'core collection'].__len__()
                columns = ['y_low', 'y_sup', 'y_mid']
                t2 = pd.DataFrame(columns=columns)
                # For step profile, like salinity
                # if ii_variable in ['salinity']:
                if not ics_stack[ics_stack.variable == ii_variable].y_low.isnull().any():
                    for ii_layer in index:
                        data = [bins_y[ii_layer], bins_y[ii_layer + 1],
                                (bins_y[ii_layer] + bins_y[ii_layer + 1]) / 2]
                        t2 = t2.append(pd.DataFrame([data], columns=columns, index=[ii_layer]))
                # For linear profile, like temperature
                # if ii_variable in ['temperature']:
                elif ics_stack[ics_stack.variable == ii_variable].y_low.isnull().all():
                    for ii_layer in index:
                        data = [np.nan, np.nan, (bins_y[ii_layer] + bins_y[ii_layer + 1]) / 2]
                        t2 = t2.append(pd.DataFrame([data], columns=columns, index=[ii_layer]))

                if temp_all.empty:
                    temp_all = temp.join(t2)
                else:
                    temp_all = temp_all.append(temp.join(t2), ignore_index=True)

    data_grouped = ics_stack.groupby([t_cuts, ics_stack['variable']])

    grouped_dict = {}
    for var in variables:
        grouped_dict[var] = [[] for ii_DD in range(bins_DD.__len__() - 1)]

    for k1, groups in data_grouped:
        if k1[1] in variables:
            grouped_dict[k1[1]][int(k1[0])] = groups['name'].unique().tolist()

    return CoreStack(temp_all.reset_index(drop=True)), grouped_dict
