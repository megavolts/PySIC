#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
cicePanda.py provides function to handle CICE model input and output.

Require the following python3 library: pandas, numpy
Require the following seaice library: corePanda, available at https://github.com/megavolts/sea_ice.git
"""

import pandas as pd
import numpy as np
import datetime as dt
import seaice.corePanda

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2014/11/25"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]


# ---------------------------------------------------------------------------------------------------------------#
# General tool
# ---------------------------------------------------------------------------------------------------------------#


def index_from_day(cice_data, day, ):
    """

    :param cice_data:
    :param day:
    :return:
    """

    index_year = np.where(cice_data[:, 0] == day.year)[0]
    index_month = np.where(cice_data[index_year, 1] == day.month)[0]
    index_day = np.where(cice_data[index_year[index_month], 2] == day.day)[0]

    if index_day.size == 0:
        return None
    else:
        return index_day


# ---------------------------------------------------------------------------------------------------------------#
# CICE output tool
# ---------------------------------------------------------------------------------------------------------------#

variable_abv = {'temperature': 'T', 'salinity': 'S'}


def import_ice_core(cice_data, day, location=None, run=None):
    """

    :param cice_data:
    :param day:
    :param location:
    :param run:
    :return:
    """

    index_day = index_from_day(cice_data, day)

    if index_day is None:
        return None

    else:
        core_name = 'CICE-' + day.strftime('%Y%m%d')
        coring_day = day
        ice_thickness = cice_data[index_day, 3][0] / 100
        snow_thickness = cice_data[index_day, 4][0] / 100
        comment = 'from CICE model simulation'
        if run is not None:
            comment += '; ' + run

        ic = seaice.corePanda.Core(core_name, coring_day, location, ice_thickness, snow_thickness, comment=comment)
        variables = ['temperature', 'salinity']

        columns = ['x', 'y_mid', 'variable', 'core', 'ice_core_length', 'note']

        for ii_var in range(variables.__len__()):
            x = cice_data[index_day, 5 + ii_var * 20:5 + (ii_var + 1) * 20][0]
            y = np.linspace(0, ice_thickness, 20)
            note = 'ice core length is given by the ice thickness of the model'
            for ii in range(x.__len__()):
                sample_name = core_name + '-' + variable_abv[variables[ii_var]] + '-' + str('-%02d' % (ii + 1))
                ic.add_profile(pd.DataFrame(
                    [[x[ii], y[ii], variables[ii_var], core_name, ice_thickness, note]],
                    columns=columns, index=[sample_name]))
        return ic


def ice_core_range(cice_data, day, end_day=None, location=None, run=None):
    """
    not ready yet

    :param cice_data:
    :param day:
    :param end_day:
    :param location:
    :param run:
    :return:
    """

    if end_day is None:
        end_day = day

    if not isinstance(day, list):
        day_range = [day]

    while day_range[-1] < end_day:
        day_range.append(day_range[-1] + dt.timedelta(1))

    ics_model = {}
    for day in day_range:
        ic = ice_core(cice_data, day, location, run)
        ics_model[ic.core_name] = ic
    return ics_model
