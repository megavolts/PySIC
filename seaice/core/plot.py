#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.plot.py : Core and CoreStack class

"""
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

__name__ = "plot"
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/09/13"
__comment__ = "plot.py contained function to plot physical profile"
__CoreVersion__ = 1.1
# __all__ = ["plot_profile", "semilogx_profile"]

module_logger = logging.getLogger(__name__)


def plot_profile(profile, ax=None, param_dict=None):
    """
    :param profile:
    :param ax:
    :param param_dict:
    :return:
    """

    variable = profile.variable.unique().tolist()
    if variable.__len__() > 1:
        module_logger.error("more than one variable is selected")
        return 0
    elif variable.__len__() < 1:
        module_logger.warning("no data in the profile")
    else:
        variable = variable[0]

    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    # step variable
    if not profile[profile.variable == variable].y_low.isnull().all():
        x = []
        y = []
        for ii in profile[profile.variable == variable].index.tolist():
            y.append(profile['y_low'][ii])
            y.append(profile['y_sup'][ii])
            x.append(profile[variable][ii])
            x.append(profile[variable][ii])

    # continuous variable
    else:
        x = profile[variable].values
        y = profile.y_mid.values
    if param_dict is None:
        ax.plot(x, y)
    else:
        ax.plot(x, y, **param_dict)
    return ax


def semilogx_profile(profile, ax=None, param_dict=None):
    """
    :param profile:
    :param ax:
    :param param_dict:
    :return:
    """

    variable = profile.variable.unique().tolist()
    if variable.__len__() > 1:
        module_logger.error("more than one variable is selected")
        return 0
    elif variable.__len__() < 1:
        module_logger.warning("no data in the profile")
    else:
        variable = variable[0]

    # step variable
    if not profile[profile.variable == variable].y_low.isnull().all():
        x = []
        y = []
        for ii in profile[profile.variable == variable].index.tolist():
            y.append(profile['y_low'][ii])
            y.append(profile['y_sup'][ii])
            x.append(profile[variable][ii])
            x.append(profile[variable][ii])

    # continuous variable
    else:
        x = profile[variable].values
        y = profile.y_mid.values

    if param_dict is None:
        ax.semilogx(x, y)
    else:
        ax.semilogx(x, y, **param_dict)
    return ax


def plot_profile_variable(ic_data, variable_dict, ax=None, param_dict=None):
    """
    :param ic_data:
        pd.DataFrame
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0

    profile = select_profile(ic_data, variable_dict)
    ax = plot_profile(profile, ax=ax, param_dict=param_dict)
    return ax


def semilogx_profile_variable(ic_data, variable_dict, ax=None, param_dict=None):
    """
    :param ic_data:
        pd.DataFrame
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0

    profile = select_profile(ic_data, variable_dict)
    ax = semilogx_profile(profile, ax=ax, param_dict=param_dict)
    return ax
