#! /usr/bin/python3
# -*- coding: UTF-8 -*-
"""
    test scripts
"""

import logging.handlers
import os
import numpy as np
import pysic
import matplotlib.pyplot as plt




# LOGGING
debug = 'vv'

# -------------------------------------------------------------------------------------------------------------------- #
# VARIABLES
# -------------------------------------------------------------------------------------------------------------------- #
if os.uname()[1] == 'adak' :
    data_RSOIT = '/home/megavolts/git/pysic/data_sample'
else:
    logging.warning("Unknown computer. Cannot find data folder root.")

vertical_resolution = 5/100

# -------------------------------------------------------------------------------------------------------------------- #
# CONFIG
# -------------------------------------------------------------------------------------------------------------------- #

ic_dir = '/home/megavolts/git/pysic/data_sample/ice_cores'

# -------------------------------------------------------------------------------------------------------------------- #
# LOGGING
# -------------------------------------------------------------------------------------------------------------------- #
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

logger.info('pysic testing module is running on %s' % os.uname()[1])

fill_gap = False
fill_extremity = False
display_figure = True
y_mid = None
variables = None

# import a single ice core from a specific path
ic_path = '/home/megavolts/git/pysic/data_sample/ice_cores/testing-gap_extremity-TS.xlsx'
#ic_path = '/home/megavolts/git/pysic/data_sample/ice_cores/testing-nogap_extremity-TS.xlsx'
variables = None
v_ref='top'
ic_data = pysic.core.import_ic_path(ic_path, variables=variables, v_ref='top', drop_empty=True)
y_bins = np.arange(0, max(ic_data.length())+vertical_resolution, vertical_resolution)
profile = ic_data.profile
profile = profile.set_vertical_reference(None, new_v_ref='bottom')

ics_stack = pysic.core.corestack.discretize_profile(profile, y_bins, display_figure=True, fill_gap=fill_gap,
                                                    fill_extremity=fill_extremity)

# import all ice cores from a directory
ics_dict = pysic.core.import_ic_sourcefile(pysic.core.make_ic_sourcefile(ic_dir, '.xlsx'), drop_empty=True)
ics_stack = pysic.core.corestack.stack_cores(ics_dict)
ics_stack = ics_stack.set_vertical_reference('bottom')
y_bins = np.arange(0, max(max(ics_stack.y_sup), max(ics_stack.length), max(ics_stack.ice_thickness))+vertical_resolution,
                   vertical_resolution)
ics_stack = ics_stack.discretize(display_figure=True, y_bins=y_bins, fill_gap=fill_gap,
                                 fill_extremity=fill_extremity)

stats = ['mean', 'min', 'max', 'std']
groups = [{'y_mid': y_bins}, {'length': [0.25, 0.5]}]
variables = None
# TODO make it works with other RSOI MOSIDEO cold ice percolatin
ics_stat = ics_stack.section_stat(groups=groups, stats=stats, variables=variables)

#
# bins = [key for key, value in ics_stat.items() if key.lower().startswith('bin_')]
# bin_value = [ics_stat[b].unique() for b in bins]
# bins_max_value = [max(v)+1 for v in bin_value]
# if bin_value.__len__() == 1:
#     bin_value = bin_value[0]
#     bins_max_value = [max(bin_value)+1]
#
#
# figure_number = 0
# vmin = {'temperature': -20, 'salinity': 0}
# vmax = {'temperature': 0, 'salinity': 20}
#
# for index in pysic.core.corestack.indices(bins_max_value):
#     func_arg = 'ics_stat['
#     for i in range(index.__len__()):
#         func_arg += '(ics_stat[bins['+str("%i" %i)+']]==bin_value['+str("%i" % index[i])+']) & '
#     func_arg = func_arg[:-3]+']'
#     data = eval(func_arg)
#
#     fig, ax = plt.subplots(1, 2, facecolor='white', sharey='all')
#     n_ax = 0
#     for variable in data.variable.unique():
#         ic_data = data[data.variable == variable]
#         variable_dict = {'variable': variable}
#         ax[n_ax] = pysic.core.plot.plot_envelop(data, variable_dict, ax=ax[n_ax], flag_number=True)
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
#
# si_prop = ['brine volume fraction', 'permeability']
# si_prop_format = 'step'
# z
# for name in ics_stack.name.unique():
#     s_profile = ics_stack.loc[(ics_stack.name == name) & (ics_stack.variable == 'salinity')]
#     t_profile = ics_stack.loc[(ics_stack.name == name) & (ics_stack.variable == 'temperature')]
#
#     temp = pysic.property.compute_phys_prop_from_core(s_profile, t_profile, si_prop, resize_core='S', display_figure=True)
#     ics_stack = ics_stack.add_profile(temp)