#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import logging.config
import os

import seaice.core as sic

logger = logging.getLogger(__name__)

# LOGGING
debug = 'vv'

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

ic_dir = '/mnt/data_local/UAF/data/MOSIDEO/cores/'
ic_path = os.path.join(ic_dir, 'HSVA-20170402-T.xlsx')

sic.import_core(ic_path)
