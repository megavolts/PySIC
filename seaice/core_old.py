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
import seaice
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
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
        if f_prop not in seaice.property.brine.si_prop_list.keys():
            print('property %s not defined in the ice core property module' % property)

        prop = seaice.property.si.si_prop_list[f_prop]
        function = getattr(seaice.property.si, prop.replace(" ", "_"))
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
            ax = seaice.core.plot.plot_profile_variable(prop_data, {'name': S_core_name, 'variable': prop},
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
        if f_prop not in seaice.property.brine.si_prop_list.keys():
            print('property %s not defined in the ice core property module' % property)

        prop = seaice.property.brine.si_prop_list[f_prop]
        function = getattr(seaice.property.si, prop.replace(" ", "_"))
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

