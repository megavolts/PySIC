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

ics_dict = seaice.io.excel.ic_source(source_fp, verbose=logging.DEBUG)
