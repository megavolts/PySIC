#! /usr/bin/python3
# -*- coding: UTF-8 -*-
#
# openpyxl, numpy, pandas, matplotlib
#
#
import logging

import seaice

dirpath = '/home/megavolts/git/seaice/data_sample/ice_cores'
fileext = '.xlsx'

source_fp = seaice.generate_source(dirpath, fileext)

ics_dict = seaice.import_ic_path(source_fp, verbose=logging.DEBUG, v_ref='top')

ics_stack = seaice.stack_cores(ics_dict)

ics_stack = ics_stack.discretize(display_figure=True, inplace=True)

stats = ['min', 'mean', 'max', 'std']
groups = {'length': sorted([0.3, 0.4, 0.5])}

test = ics_stack.section_stat(groups=groups, stats=stats)
