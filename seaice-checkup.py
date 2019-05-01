#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
2019-03-08
Project: ASIEMOV

Script to checkup the good functionnement of
- bottom alignement
- discretization
- stat

"""

import os
import seaice
import configparser
import pickle
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
# =====================================================================================================================#
# USER VARIABLE INPUT
# =====================================================================================================================#
ice_thickness_section = 0.05  # thickness of ice section / vertical bin in m
min_hi = 0.585
max_hi = 0.76
y_bins = np.arange(0, 1, ice_thickness_section)
variables = ['temperature', 'salinity']

# =====================================================================================================================#
# LOAD CONFIG
# =====================================================================================================================#
myhost = os.uname()[1]
config = '/home/megavolts/git/MOSAiC_ASIEMOV/BRW.ini'
config_path = os.path.join(config)
if myhost == 'islay':
    fig_dir = '/home/megavolts/Desktop/'
elif myhost == 'arran':
    fig_dir = '/home/megavolts/Desktop/'
elif myhost == 'adak':
    fig_dir = '/home/megavolts/Desktop/'

config = configparser.ConfigParser()
config.read(config_path)


# =====================================================================================================================#
# LOAD DATA
# =====================================================================================================================#
# ice core from BRW long term observation
path = os.path.join(config['DEFAULT']['data_dir'], config['CLIMATOLOGY']['subdir'], config['CLIMATOLOGY']['obs core'])
with open(path, 'rb') as f:
    ic_obs_stack = seaice.core.corestack.CoreStack(pickle.load(f))

# Select ice core
# (1) growth period only ( date < April 15)
end_growth_doy = pd.Series(pd.to_datetime(['2015-4-15'])).dt.dayofyear.values[0]

# (2) ice thickness in between min-ice_thickness_section/2 and max+ice_thickness_section/2
ic_obs_stack = ic_obs_stack.loc[(min_hi < ic_obs_stack['ice_thickness']) &
                                (ic_obs_stack['ice_thickness'] < max_hi) &
                                (ic_obs_stack.date.dt.dayofyear < end_growth_doy)]

# 1. Zero at the ice surface
# 1.1 Discretizatoin:
ic_obs_stack_d = ic_obs_stack.discretize(y_bins, display_figure=False)
# if DEBUG:
#     name = 'BRW_CS-20070125A'
#     for name in ic_obs_stack.names():
#         profiles = ic_obs_stack.loc[ic_obs_stack.name == name]
#         y_mid=None
#         display_figure=True
#         fill_gap=False
#         fill_extremity=False
#         discretized_profile = seaice.core.profile.discretize_profile(profiles, y_bins=y_bins, display_figure=True)

# 1.2 Statistic
ic_stat = ic_obs_stack_d.section_stat(groups={'y_mid': y_bins})
#if DEBUG:
    # ic_sub = ic_obs_stack_d[ic_obs_stack_d.y_low==0.65]
    # ic_stack = ic_sub.copy()
    # groups={'y_mid': y_bins}
    # variables = 'salinity'
    # stats=['min', 'mean', 'max', 'std']
    # ic_sub_s = ic_sub.section_stat(groups=groups)

# if DEBUG:
#     ic_stack = ic_obs_stack_d
#     groups={'y_mid'}
#     variables=None
#     stats=['min', 'mean', 'max', 'std']
# 1.3 Plot
# 1.3.1 Plot stat and discretized profiles
fig, ax = plt.subplots(1, len(ic_stat.variables()), sharey='row', sharex='col')
ax = np.atleast_2d(ax)
ax_n = 0

# core colors:
date_list = ic_obs_stack_d.date.dt.date.unique()
colors = {date_list[i_core]: cm.jet(i_core / date_list.__len__()) for i_core in range(0, len(date_list))}

for variable in variables:
    # TOP
    variable_dict = {'variable': variable, 'v_ref': 'top'}

    # plot envelop
    ax[0, ax_n] = seaice.core.plot.plot_envelop(ic_stat, variable_dict.copy(), ax=ax[0, ax_n], flag_number=True)
    # if DEBUG:
    #     ax = ax[0, ax_n]
    #     flag_number=True
    #     legend=False
    #     param_dict={}
    #     z_delta=0
    #     every=1

    # plot profile
    core_list = ic_obs_stack_d.loc[ic_obs_stack_d.variable.str.contains(variable), 'name'].unique()
    date_list = ic_obs_stack_d.date.dt.date.unique()
    colors = {date_list[i_core]: cm.jet(i_core / date_list.__len__()) for i_core in range(0, len(date_list))}
    core_n = 0
    # TODO color by year
    for core in core_list:
        core_data = ic_obs_stack_d.loc[ic_obs_stack_d.name == core]
        color = colors[core_data.date.dt.date.unique()[0]]
        ax[0, ax_n] = seaice.core.plot.plot_profile_variable(core_data, variable_dict, ax=ax[0, ax_n],
                                                             param_dict={'color': color, 'linewidth': 1})
        core_n += 1

    ax_n += 1

# legend
legends = ['min', 'mean $\pm std$', 'max'] + sorted(date_list)
handles = [mlines.Line2D([], [], color='b', linewidth=2),
           (mpatches.Patch(color='grey', alpha=0.6), mlines.Line2D([], [], color='k', linewidth=2)),
           mlines.Line2D([], [], color='r', linewidth=2)] + \
          [mlines.Line2D([], [], color=colors[date], linestyle='-', linewidth=1) for date in date_list]
plt.legend(handles, legends, ncol=1)
plt.savefig(os.path.join(fig_dir, 'climatology-all.pdf'))
plt.show()

# 1.3.2 Plot stat and profiles
fig, ax = plt.subplots(1, len(ic_stat.variables()), sharey='row', sharex='col')
ax = np.atleast_2d(ax)
ax_n = 0
for variable in variables:
    # TOP
    variable_dict = {'variable': variable, 'v_ref': 'top'}

    # plot envelop
    ax[0, ax_n] = seaice.core.plot.plot_envelop(ic_stat, variable_dict.copy(), ax=ax[0, ax_n], flag_number=True)
    # if DEBUG:
    #     ax = ax[0, ax_n]
    #     flag_number=True
    #     legend=False
    #     param_dict={}
    #     z_delta=0
    #     every=1

    # plot profile
    core_list = ic_obs_stack.loc[ic_obs_stack.variable.str.contains(variable), 'name'].unique()
    date_list = ic_obs_stack.date.dt.date.unique()
    colors = {date_list[i_core]: cm.jet(i_core / date_list.__len__()) for i_core in range(0, len(date_list))}
    core_n = 0
    # TODO color by year
    for core in core_list:
        core_data = ic_obs_stack.loc[ic_obs_stack.name == core]
        color = colors[core_data.date.dt.date.unique()[0]]
        ax[0, ax_n] = seaice.core.plot.plot_profile_variable(core_data, variable_dict, ax=ax[0, ax_n],
                                                             param_dict={'color': color, 'linewidth': 1})
        core_n += 1
    ax_n += 1

# legend
legends = ['min', 'mean $\pm std$', 'max'] + sorted(date_list)
handles = [mlines.Line2D([], [], color='b', linewidth=2),
           (mpatches.Patch(color='grey', alpha=0.6), mlines.Line2D([], [], color='k', linewidth=2)),
           mlines.Line2D([], [], color='r', linewidth=2)] + \
          [mlines.Line2D([], [], color=colors[date], linestyle='-', linewidth=1) for date in date_list]
plt.legend(handles, legends, ncol=1)
plt.savefig(os.path.join(fig_dir, 'climatology-all.pdf'))
plt.show()


# 2. Zero at the ice bottom
# 2.0 Change vertical reference
ic_obs_stack_b = ic_obs_stack.copy().set_orientation('bottom')

# 2.1 Discretizatoin:
ic_obs_stack_b_d = ic_obs_stack_b.discretize(y_bins, display_figure=False)


# 2.2 Statistic
ic_stat_b = ic_obs_stack_b_d.section_stat(groups={'y_mid': y_bins})
# if DEBUG:
#     ic_sub = ic_obs_stack_d[ic_obs_stack_d.y_low==0.75]
#     ic_stack = ic_sub.copy()
#     groups={'y_mid': y_bins}
#     variables = 'temperature'
#     stats=['min', 'mean', 'max', 'std']
#     ic_sub_s = ic_sub.section_stat(groups=groups)
# if DEBUG:
#     ic_stack = ic_obs_stack_d
#     groups={'y_mid'}
#     variables=None
#     stats=['min', 'mean', 'max', 'std']
# 2.3 Plot
# 2.3.1 Plot stat and discretized profiles
fig, ax = plt.subplots(1, len(ic_stat_b.variables()), sharey='row', sharex='col')
ax = np.atleast_2d(ax)
ax_n = 0
for variable in variables:
    # TOP
    variable_dict = {'variable': variable, 'v_ref': 'top'}

    # plot envelop
    ax[0, ax_n] = seaice.core.plot.plot_envelop(ic_stat_b, variable_dict.copy(), ax=ax[0, ax_n], flag_number=True)
    # if DEBUG:
    #     ax = ax[0, ax_n]
    #     flag_number=True
    #     legend=False
    #     param_dict={}
    #     z_delta=0
    #     every=1

    # plot profile
    core_list = ic_obs_stack_b_d.loc[ic_obs_stack_b_d.variable.str.contains(variable), 'name'].unique()
    date_list = ic_obs_stack_b_d.date.dt.date.unique()
    colors = {date_list[i_core]: cm.jet(i_core / date_list.__len__()) for i_core in range(0, len(date_list))}
    core_n = 0
    # TODO color by year
    for core in core_list:
        core_data = ic_obs_stack_b_d.loc[ic_obs_stack_b_d.name == core]
        color = colors[core_data.date.dt.date.unique()[0]]
        ax[0, ax_n] = seaice.core.plot.plot_profile_variable(core_data, variable_dict, ax=ax[0, ax_n],
                                                             param_dict={'color': color, 'linewidth': 1})
        core_n += 1
    #ax[0, ax_n].set_ylim([0, 0.8])
    ax_n += 1

# legend


legends = ['min', 'mean $\pm std$', 'max'] + sorted(date_list)
handles = [mlines.Line2D([], [], color='b', linewidth=2),
           (mpatches.Patch(color='grey', alpha=0.6), mlines.Line2D([], [], color='k', linewidth=2)),
           mlines.Line2D([], [], color='r', linewidth=2)] + \
          [mlines.Line2D([], [], color=colors[date], linestyle='-', linewidth=1) for date in date_list]
plt.legend(handles, legends, ncol=1)
plt.savefig(os.path.join(fig_dir, 'climatology-all.pdf'))
plt.show()

# 2.3.2 Plot stat and  profiles
fig, ax = plt.subplots(1, len(ic_stat_b.variables()), sharey='row', sharex='col')
ax = np.atleast_2d(ax)
ax_n = 0
for variable in variables:
    # TOP
    variable_dict = {'variable': variable, 'v_ref': 'top'}

    # plot envelop
    ax[0, ax_n] = seaice.core.plot.plot_envelop(ic_stat_b, variable_dict.copy(), ax=ax[0, ax_n], flag_number=True)
    # if DEBUG:
    #     ax = ax[0, ax_n]
    #     flag_number=True
    #     legend=False
    #     param_dict={}
    #     z_delta=0
    #     every=1

    # plot profile
    core_list = ic_obs_stack_b.loc[ic_obs_stack_b.variable.str.contains(variable), 'name'].unique()
    date_list = ic_obs_stack_b.date.dt.date.unique()
    colors = {date_list[i_core]: cm.jet(i_core / date_list.__len__()) for i_core in range(0, len(date_list))}
    core_n = 0
    # TODO color by year
    for core in core_list:
        core_data = ic_obs_stack_b.loc[ic_obs_stack_b.name == core]
        color = colors[core_data.date.dt.date.unique()[0]]
        ax[0, ax_n] = seaice.core.plot.plot_profile_variable(core_data, variable_dict, ax=ax[0, ax_n],
                                                             param_dict={'color': color, 'linewidth': 1})
        core_n += 1
    #ax[0, ax_n].set_ylim([0, 0.8])
    ax_n += 1

# legend
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

legends = ['min', 'mean $\pm std$', 'max'] + sorted(date_list)
handles = [mlines.Line2D([], [], color='b', linewidth=2),
           (mpatches.Patch(color='grey', alpha=0.6), mlines.Line2D([], [], color='k', linewidth=2)),
           mlines.Line2D([], [], color='r', linewidth=2)] + \
          [mlines.Line2D([], [], color=colors[date], linestyle='-', linewidth=1) for date in date_list]
plt.legend(handles, legends, ncol=1)
plt.savefig(os.path.join(fig_dir, 'climatology-all.pdf'))
plt.show()