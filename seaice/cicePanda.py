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


def index_from_day(cice_data, day):
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
        return index_year[index_month[index_day]][0]


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
        ice_thickness = cice_data[index_day, 3] / 100
        snow_thickness = cice_data[index_day, 4] / 100
        comment = 'from CICE model simulation'
        if run is not None:
            comment += '; ' + run

        ic = seaice.corePanda.Core(core_name, coring_day, location, ice_thickness, snow_thickness, comment=comment)
        variables = ['temperature', 'salinity']
        # columns = ['temperature', 'salinity', 'note', 'core', 'ice_core_length', 'variable', 'y_low', 'y_sup', 'y_mid', 'sample_name']
        # ic_df = pd.DataFrame(columns=columns)
        y = np.linspace(0, ice_thickness, 21)
        for ii_var in range(variables.__len__()):
            x = cice_data[index_day, 5 + ii_var * 20:5 + (ii_var + 1) * 20]
            df = pd.DataFrame(x, columns=[variables[ii_var]])

            note = 'ice core length is given by the ice thickness of the model'
            data = [note, core_name, ice_thickness, variables[ii_var]]
            columns = ['note', 'core', 'ice_core_length', 'variable']
            df = df.join(pd.DataFrame([data], columns=columns, index = df.index.tolist()))
            if variables[ii_var] in ['temperature']:
                df = df.join(pd.DataFrame(y[:-1] + np.diff(y) / 2, columns=['y_mid'], index=df.index.tolist()))
            elif variables[ii_var] in ['salinity']:
                df = df.join(pd.DataFrame(np.vstack((y[:-1], y[1:], y[:-1] + np.diff(y) / 2)).transpose(), columns=['y_low', 'y_sup', 'y_mid'], index=df.index.tolist()))

            for ii in range(x.__len__()):
                sample_name = core_name + '-' + variable_abv[variables[ii_var]] + '-' + str('-%02d' % (ii + 1))
                if ii == 0:
                    df = df.join(pd.DataFrame([sample_name], columns=['sample_name'], index=[ii]))
                else:
                    df.update(pd.DataFrame([sample_name], columns=['sample_name'], index=[ii]))
            ic.add_profile(df)
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


def freezup_date(cice_data, year, hi_freezup=0.05):
    if year not in cice_data.year.unique():
        return None
    f_ice = 0
    date = []
    for f_day in cice_data[cice_data.year == year].date:
        if not cice_data[(cice_data.date == f_day) & (cice_data['ice thickness'] > hi_freezup)].empty:
            if f_ice == 0:
                f_ice = 1
                date.append(f_day.to_datetime())
                # hi.append(float(cice_data[(cice_data.date == f_day) & (cice_data['ice thickness'] > hi_freezup)]['ice thickness']))
        else:
            f_ice = 0

    if date.__len__() == 0:
        return None
    else:
        return date[-1]