#! /usr/bin/python3
# -*- coding: UTF-8 -*-
#
# openpyxl, numpy, pandas, matplotlib
#
#

__name__ = "ElsonLagoonTesting"

import numpy as np
import seaice
from seaice.core.tool import indices

import logging
import logging.handlers
import os
# Enable logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log everything to the rotating log viles
if not os.path.exists('logs'):
    os.mkdir('logs')
lf = logging.handlers.RotatingFileHandler('logs/args.log', maxBytes=100000, backupCount=5)
lf.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s'))
lf.setLevel(logging.DEBUG)
logger.addHandler(lf)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))  # define format
logger.addHandler(ch)

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')



dirpath = '/home/megavolts/data/seaice/core/BRW-EL-winter/'
fileext = '.xlsx'

source_fp = seaice.generate_source(dirpath, fileext)

ics_dict = seaice.import_ic_path(source_fp, v_ref='top')

ics_stack = seaice.stack_cores(ics_dict)

ics_stack = ics_stack.discretize(display_figure=False, y_bins=np.arange(0, max(ics_stack.length)+0.05, 0.05))

stats = ['min', 'mean', 'max', 'std']
groups = {'length': [0, 0.77, 1.27, 1.77]}

ics_stat = ics_stack.section_stat(groups=groups, stats=stats, variables=['temperature', 'salinity'])

bins = [key for key, value in ics_stat.items() if key.lower().startswith('bin_')]
bin_value = [ics_stat[b].unique() for b in bins]
bins_max_value = [max(v)+1 for v in bin_value]
if bin_value.__len__() == 1:
    bin_value = bin_value[0]
    bins_max_value = [max(bin_value)+1]


figure_number = 0

import seaice.core.plot as pltc
import matplotlib.pyplot as plt

vmin = {'temperature': -20, 'salinity': 0}
vmax = {'temperature': 0, 'salinity': 10}

for index in indices(bins_max_value):
    print(index)
    func_arg = 'ics_stat['
    for i in range(index.__len__()):
        print(i)
        func_arg += '(ics_stat[bins['+str("%i" %i)+']]==bin_value['+str("%i" % index[i])+']) & '
    func_arg = func_arg[:-3]+']'
    data = eval(func_arg)

    fig, ax = plt.subplots(1, 2, facecolor='white', sharey=True)
    n_ax = 0
    for variable in data.variable.unique():
        pltc.plot_profile_variable(data, {'variable': variable, 'stats': 'min'}, ax = ax[n_ax],
                                   param_dict={'linewidth': 1, 'color': 'b', 'label': 'min'})
        pltc.plot_profile_variable(data, {'variable': variable, 'stats': 'max'}, ax = ax[n_ax],
                                   param_dict={'linewidth': 1, 'color': 'r', 'label': 'max'})
        pltc.plot_profile_variable(data, {'variable': variable, 'stats': 'mean'}, ax = ax[n_ax],
                                   param_dict={'linewidth': 1, 'color': 'k', 'label': 'mean'})
        ax[n_ax].set_xlabel(variable)
        ax[n_ax].xaxis.set_label_position('top')
        ax[n_ax].get_xaxis().tick_top()
        ax[n_ax].spines['bottom'].set_visible(False)
        ax[n_ax].spines['right'].set_visible(False)
        ax[n_ax].set_xlim([vmin[variable], vmax[variable]])

        for y in [0.5, 1, 1.5]:
            ax[n_ax].plot(np.arange(vmin[variable], vmax[variable]+1),
                          [y]*len(np.arange(vmin[variable], vmax[variable]+1)),
                          "--", lw=0.5, color="black", alpha=0.5)
        n_ax += 1
    # y_axis
    ax[0].set_ylabel('depth (m)')
    ax[0].axes.set_ylim([2, 0])
    plt.yticks([0.5, 1, 1.5])

    plt.suptitle('ice thickness range :'+ str(groups['length'][np.array(index)[0]]) +'-'+ str(groups['length'][np.array(index)[0]+1]) + '(m)')
    plt.subplots_adjust(top=0.83)
