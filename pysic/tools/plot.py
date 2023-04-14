#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
pysic.core.plot.py : Core and CoreStack class

"""
import logging

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pysic.core.profileV0 import *
from pysic.core.profileV0 import Profile

__name__ = "plot"
__author__ = "Marc Oggier"
__license__ = "GPL"

__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/09/13"
__comment__ = "plot.py contained function to plot physical profile"
__CoreVersion__ = 1.1
__all__ = ["plot_profile", "semilogx_profile", "plot_profile_variable", "semilogx_profile_variable",
           "plot_mean_envelop", "plot_number", "plot_envelop", "plot_enveloplog"]

module_logger = logging.getLogger(__name__)

# New version have 2019 in name

variable_unit_dict = {'salinity': '(g kg$^{-1}$)', 'temperature': ' $^\circ$C'}
continuous_property = ['temperature']

ax=None
param_dict=None
## Old plot
def plot_profile(profile, ax=ax, param_dict=param_dict):
    """
    :param profile:
    :param ax:
    :param param_dict:
    :return:
    """

    prop = [key for key in profile if key not in ['y_low', 'y_mid', 'y_sup']][0]


    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if not profile.empty:
        # Step variable
        #
        ax.s
    return ax