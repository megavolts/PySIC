#! /usr/bin/python3
# -*- coding: UTF-8 -*-
#
# openpyxl, numpy, pandas, matplotlib
#
#
import logging

import seaice

dirpath = '/home/megavolts/data/seaice/core/BRW-EL'
fileext = '.xlsx'

source_fp = seaice.generate_source(dirpath, fileext)

ics_dict = seaice.import_ic_path(source_fp, verbose=logging.DEBUG, v_ref='top')

ics_stack = seaice.stack_cores(ics_dict)

ics_stack.discretize(display_figure='n')

ics_stack.cl
