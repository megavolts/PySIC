#! /usr/bin/python3
# -*- coding: UTF-8 -*-
#
# openpyxl, numpy, pandas, matplotlib
#
__name__ = "ElsonLagoonTesting"

import os
import numpy as np
import pysic
import json
import logging.config
import matplotlib.pyplot as plt


# Enable logging
LOG_CFG = 'docs/logging.json'
if os.path.exists(LOG_CFG):
    with open(LOG_CFG, 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)
else:
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


if os.uname()[1] == 'adak':
    dirpath = '/mnt/data/UAF-data/pysic/core/BRW-EL-winter/'
    source_fp = '/mnt/data/UAF-data/pysic/core/BRW-EL-winter/ics_list.txt'
elif os.uname()[1] == 'arran':
    dirpath = '/home/megavolts/data/pysic/core/BRW-EL-winter/'
else:
    logger.error("directory path unknown")

fileext = '.xlsx'
source_fp = pysic.make_ic_sourcefile(dirpath, fileext)


ics_dict = pysic.import_ic_sourcefile(source_fp, v_ref='top')
ics_stack = pysic.stack_cores(ics_dict)



ics_stack = ics_stack.discretize(display_figure=False, y_bins=np.arange(0, max(ics_stack.length)+0.05, 0.05))
stats = ['min', 'mean', 'max', 'std']
groups = {'length': [0, 0.77, 1.27, 1.77], 'y_mid': y_bins}
ics_stat = ics_stack.section_stat(groups=groups, stats=stats, variables=['temperature', 'salinity'])

bins = [key for key, value in ics_stat.items() if key.lower().startswith('bin_')]
bin_value = [ics_stat[b].unique() for b in bins]
bins_max_value = [max(v)+1 for v in bin_value]
if bin_value.__len__() == 1:
    bin_value = bin_value[0]
    bins_max_value = [max(bin_value)+1]

figure_number = 0

vmin = {'temperature': -20, 'salinity': 0}
vmax = {'temperature': 0, 'salinity': 10}

for index in pysic.core.tool.indices(bins_max_value):
    func_arg = 'ics_stat['
    for i in range(index.__len__()):
        func_arg += '(ics_stat[bins['+str("%i" %i)+']]==bin_value['+str("%i" % index[i])+']) & '
    func_arg = func_arg[:-3]+']'
    data = eval(func_arg)

    fig, ax = plt.subplots(1, 2, facecolor='white', sharey=True)
    n_ax = 0
    for variable in data.variable.unique():
        ic_data = data[data.variable == variable]
        variable_dict = {'variable': variable}
        # TODO add number of core, need to check how number of core is calculated
        ax[n_ax] = pysic.climatology.plot_envelop(ic_data, variable_dict, ax=ax[n_ax], param_dict={})

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

    plt.suptitle('ice thickness range :'+ str(groups['length'][np.array(index)[0]]) + '-' +
                 str(groups['length'][np.array(index)[0]+1]) + '(m)')
    plt.subplots_adjust(top=0.83)
