#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import logging.config
import os
import numpy as np
import seaice

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
ic_path = os.path.join(ic_dir, '2015-B1-OR19.xlsx')


#ics_dict = seaice.import_ic_sourcefile(seaice.make_ic_sourcefile(ic_dir, '.xlsx'))
display_figure=True
fill_gap = True
y_mid= None
variables='salinity'
ic_data = seaice.import_ic_path(ic_path, variables=variables, v_ref='top')
profile1 = ic_data.profile
y_bins = np.arange(0, max(max(profile1.y_sup), ic_data.length)+vert_resolution, vert_resolution)
profile = profile1
profile2 = discretize_profile(profile, y_bins, display_figure=True)
profile3 = discretize_profile(profile2, y_bins, display_figure=True)
ics_stack = seaice.stack_cores(ics_dict)

y_bins = np.arange(0, max(max(ics_stack.y_sup), max(ics_stack.length), max(ics_stack.ice_thickness))+vert_resolution, vert_resolution)
ics_stack = ics_stack.discretize(display_figure=True, y_bins=y_bins)



stats = ['min', 'mean', 'max', 'std']
groups = {'length': [0.25, 0.5, 0.75], 'y_dim': y_bins}
ics_stack.groups

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
