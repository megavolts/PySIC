#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import logging.config
import os
import numpy as np
import seaice
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# LOGGING
debug = 'vv'

vert_resolution = 5/100

# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# always write everything to the rotating log files
if not os.path.exists('logs'):
    os.mkdir('logs')
log_file_handler = logging.handlers.TimedRotatingFileHandler('logs/args.log', when='M', interval=2)
log_file_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s'))
log_file_handler.setLevel(logging.DEBUG)
logger.addHandler(log_file_handler)

# also log to the console at a level determined by the --verbose flag
console_handler = logging.StreamHandler()  # sys.stderr
console_handler.setLevel(logging.CRITICAL)  # set later by set_log_level_from_verbose() in interactive sessions
console_handler.setFormatter(logging.Formatter('[%(levelname)s](%(name)s): %(message)s'))
logger.addHandler(console_handler)

levels = [logging.WARNING, logging.INFO, logging.DEBUG, logging.CRITICAL]
level = levels[min(len(levels)-1, debug.__len__())]  # capped to number of levels
logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")

if os.uname()[1] == 'islay':
    data_RSOI = '/mnt/data_local/UAF/data/RSOI/'
elif os.uname()[1] == 'arran':
    data_RSOI = '/mnt/data_lvm/RSOI/'
else:
    logging.warning("Unknown computer. Cannot find data folder root.")
logger.info('alaph_core.py is run on %s' % os.uname()[1])

logger.info('Reloading seaice.core.py')

ic_dir = '/home/megavolts/git/seaice/data_sample/ice_cores'
ic_path = os.path.join(ic_dir, '2015-B2-OR19.xlsx')


# display_figure=True
# fill_gap = True
# y_mid= None
# variables='temperature'
# ic_data = seaice.import_ic_path(ic_path, variables=variables, v_ref='top')
# profile1 = ic_data.profile
# y_bins = np.arange(0, max(ic_data.length)+vert_resolution, vert_resolution)
# profile = profile1
# profile2 = discretize_profile(profile, y_bins, display_figure=True)
# profile3 = discretize_profile(profile2, y_bins, display_figure=True)
# ics_stack = seaice.stack_cores(ics_dict)

ics_dict = seaice.import_ic_sourcefile(seaice.make_ic_sourcefile(ic_dir, '.xlsx'))
ics_stack = seaice.stack_cores(ics_dict)
y_bins = np.arange(0, max(max(ics_stack.y_sup), max(ics_stack.length), max(ics_stack.ice_thickness))+vert_resolution, vert_resolution)
ics_stack = ics_stack.discretize(display_figure=False, y_bins=y_bins)


#
# stats = ['min', 'mean', 'max', 'std']
# groups = {'length': [0.25, 0.5, 0.75]}
#
# ics_stat = ics_stack.section_stat(groups=groups, stats=stats, variables=['temperature', 'salinity'])
#
# bins = [key for key, value in ics_stat.items() if key.lower().startswith('bin_')]
# bin_value = [ics_stat[b].unique() for b in bins]
# bins_max_value = [max(v)+1 for v in bin_value]
# if bin_value.__len__() == 1:
#     bin_value = bin_value[0]
#     bins_max_value = [max(bin_value)+1]
#
# figure_number = 0
#
# vmin = {'temperature': -20, 'salinity': 0}
# vmax = {'temperature': 0, 'salinity': 10}
#
# for index in seaice.core.tool.indices(bins_max_value):
#     func_arg = 'ics_stat['
#     for i in range(index.__len__()):
#         func_arg += '(ics_stat[bins['+str("%i" %i)+']]==bin_value['+str("%i" % index[i])+']) & '
#     func_arg = func_arg[:-3]+']'
#     data = eval(func_arg)
#
#     fig, ax = plt.subplots(1, 2, facecolor='white', sharey=True)
#     n_ax = 0
#     for variable in data.variable.unique():
#         ic_data = data[data.variable == variable]
#         variable_dict = {'variable': variable}
#         # TODO add number of core, need to check how number of core is calculated
#         ax[n_ax] = seaice.climatology.plot_envelop(ic_data, variable_dict, ax=ax[n_ax], param_dict={})
#
#         ax[n_ax].set_xlabel(variable)
#         ax[n_ax].xaxis.set_label_position('top')
#         ax[n_ax].get_xaxis().tick_top()
#         ax[n_ax].spines['bottom'].set_visible(False)
#         ax[n_ax].spines['right'].set_visible(False)
#         ax[n_ax].set_xlim([vmin[variable], vmax[variable]])
#
#         for y in [0.5, 1, 1.5]:
#             ax[n_ax].plot(np.arange(vmin[variable], vmax[variable]+1),
#                           [y]*len(np.arange(vmin[variable], vmax[variable]+1)),
#                           "--", lw=0.5, color="black", alpha=0.5)
#         n_ax += 1
#     # y_axis
#     ax[0].set_ylabel('depth (m)')
#     ax[0].axes.set_ylim([2, 0])
#     plt.yticks([0.5, 1, 1.5])
#
#     plt.suptitle('ice thickness range :'+ str(groups['length'][np.array(index)[0]]) + '-' +
#                  str(groups['length'][np.array(index)[0]+1]) + '(m)')
#     plt.subplots_adjust(top=0.83)


import pandas as pd

def scale_profile(profile, h_ice_f):
    """
    :param profile:
        CoreStack, ice core profile to scale to a target ice thickness
    :param h_ice_f:
        scalar, target ice thickness
    :return:
    """

    if profile.length.unique().size and ~np.isnan(profile.length.unique()[0]):
        h_ice = profile.length.unique()[0]
    elif profile.ice_thickness.unique().size and ~np.isnan(profile.ice_thickness.unique()[0]):
        h_ice = profile.ice_thickness.unique()[0]
    else:
        logging.error("Scale: no core length or ice thickness given for %s" % profile.core_name.unique()[0])
        return 0

    r = h_ice_f / h_ice
    if r == 1:
        return profile
    profile[['y_low', 'y_mid', 'y_sup']] = r * profile[['y_low', 'y_mid', 'y_sup']]
    profile.length = h_ice_f
    return profile



def compute_phys_prop_from_core(s_profile, t_profile, si_prop, si_prop_format='step', resize_core=None,
                                display_figure=True, attribut_core='S'):
    """
    :param s_profile:
    :param t_profile:
    :param si_prop:
    :param si_prop_format: 'linear' or 'step' (default)
    :param resize_core: 'S', 'T', 'None' (default)
    :param attribut_core: 'S' (default), 'T'
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
            si_prop_dict = {si_prop: si_prop_format}
        elif not isinstance(si_prop_format, list):
            si_prop_dict = {}
            for prop in si_prop:
                si_prop_dict[prop] = si_prop_format
        elif si_prop_format.__len__() == si_prop.__len__():
            si_prop
            si_prop_format = [si_prop_format]
        if si_prop_format.__len__() > 1 and not si_prop_format.__len__() == si_prop.__len__():
            logger.error(
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
        s_profile.loc[s_profile.variable == 'salinity', 'salinity'] = pd.to_numeric(s_profile['salinity'])

    if 'temperature' not in t_profile.keys() or not t_profile['temperature'].notnull().any():
        print("no temperature data")
        return prop_profile
    else:
        T_core_name = t_profile.name.values[0]
        t_profile.loc[t_profile.variable == 'temperature', 'temperature'] = pd.to_numeric(t_profile['temperature'])

    if resize_core in ['S', S_core_name]:
        if s_profile.length.notnull().all():
            profile_length = s_profile.length.unique()[0]
        elif s_profile.length.notnull().all():
            profile_length = s_profile.ice_thickness.unique()[0]
            print("ice core length unknown, using ice thickness instead")
        else:
            profile_length = max(s_profile.y_low.min(), s_profile.y_sup.max())[0]
            print("todo: need warning text")
        if not t_profile.length.unique() == profile_length:
            t_profile = scale_profile(t_profile, profile_length)
    elif resize_core in ['T', T_core_name]:
        if t_profile.length.notnull().all():
            profile_length = t_profile.length.unique()[0]
        elif t_profile.length.notnull().all():
            profile_length = t_profile.ice_thickness.unique()[0]
            print("ice core length unknown, using ice thickness instead")
        else:
            profile_length = max(t_profile.y_low.min(), t_profile.y_sup.max())[0]
            print("todo: need warning text")

        if not t_profile.length.unique() == profile_length:
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
        if f_prop not in seaice.property.prop_list.keys():
            print('property %s not defined in the ice core property module' % property)

        prop = seaice.property.prop_list[f_prop]
        function = getattr(seaice.property.si, prop.replace(" ", "_"))
        prop_data = function(np.array(t_profile['temperature']), np.array(s_profile['salinity']))

        prop_data = pd.DataFrame(np.vstack((prop_data, s_profile['y_mid'])).transpose(), columns=[prop, 'y_mid'])
        comment_core = 'physical properties computed from ' + S_core_name + '(S) and ' + T_core_name + '(T)'
        prop_data['comment'] = comment_core
        prop_data['variable'] = prop
        prop_name = list(set(s_profile.name))[0]+'/'+list(set(t_profile.name))[0]

        if attribut_core is 'S':
            prop_data['name'] = list(set(s_profile.name))[0]
            var_drop = [var for var in ['salinity', 'temperature', 'variable', f_prop, 'name', 'core'] if
                        var in s_profile.keys()]
            core_frame = s_profile.drop(var_drop, axis=1)
        elif attribut_core is 'T':
            prop_data['name'] = list(set(t_profile.name))[0]
            var_drop = [var for var in ['salinity', 'temperature', 'variable', f_prop, 'name', 'core'] if
                        var in t_profile.keys()]
            core_frame = t_profile.drop(var_drop, axis=1)
        prop_data['name'] = prop_name

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
            ax = seaice.core.plot.plot_profile_variable(prop_data, {'name': prop_name, 'variable': prop},
                                       ax=None, param_dict=None)
            ax.set_xlabel(prop)
            ax.set_ylabel('ice thickness)')
            ax.set_title(S_core_name)
        prop_profile = prop_profile.append(prop_data, ignore_index=True, verify_integrity=False)

    return prop_profile


si_prop = ['brine volume fraction', 'permeability']

for name in ics_stack.name.unique():
    s_profile = ics_stack.loc[(ics_stack.name == name) & (ics_stack.variable == 'salinity')]
    t_profile = ics_stack.loc[(ics_stack.name == name) & (ics_stack.variable == 'temperature')]

    compute_phys_prop_from_core(s_profile, t_profile, si_prop, resize_core='S')