#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import logging
import seaice

dirpath = './data_sample/ice_cores'
fileext = '.xlsx'

source_fp = seaice.generate_source(dirpath, fileext)

ics_dict = seaice.load.ic_source(source_fp, verbose=logging.DEBUG)


