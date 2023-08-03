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
__all__ = ["plot_profile", 'plot_profiles']

logger = logging.getLogger(__name__)

# New version have 2019 in name

variable_unit_dict = {'salinity': '(g kg$^{-1}$)', 'salinity_value': '(g kg$^{-1}$)',
                      'temperature': '$^\circ$C', 'temperature_value': '$^\circ$C',}
continuous_property = ['temperature']

ax=None
param_dict=None
ax_dict=None
variables=None

module_logger = logging.getLogger(__name__)

def plot_profile(profile, ax=ax, param_dict=param_dict, display_figure=False):
    """
    Plot profile, by default 0 is the ice surface, and positive towards the ocean.
    :param profile:
    :param ax:
    :param param_dict:
    :return:
    """
    # check number of variable
    if len(profile.variable) > 1:
        module_logger.warning("more than one variable is selected")
    else:
        variable = profile.variable[0]

    # check vertical reference
    if 'v_ref_loc' not in profile.columns:
        profile.v_ref_loc = None
    elif len(profile.v_ref_loc.unique()) > 1:
        module_logger.error('vertical reference is not unique')
    else:
        v_ref_loc = profile.v_ref_loc.unique()[0]
    if 'v_ref_h' not in profile.columns:
        profile.v_ref_h = [0] * len(profile)
    elif len(profile.v_ref_h.unique()) > 1:
        module_logger.error('vertical reference is not unique')
    else:
        v_ref_h = profile.v_ref_h.unique()[0]
    if 'v_ref_dir' not in profile.columns:
        profile.v_ref_dir = ['down'] * len(profile)
    elif len(profile.v_ref_dir.unique()) > 1:
        module_logger.error('vertical reference is not unique')
    else:
        v_ref_dir = profile.v_ref_dir.unique()[0]

    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if not profile.empty:
        # Step variable
        if 'y_low' in profile.columns:
            if any(profile.y_low.isna()) or any(profile.y_sup.isna()):
                module_logger.error("some upper or lower section depth are not a number")
            else:
                x = profile[variable + '_value'].values
                x = np.concatenate((x, [x[-1]]))
                y = profile.y_low.values
                y = np.concatenate((y, [profile.y_sup.values[-1]]))
                if param_dict is None:
                    ax.step(x, y, )
                else:
                    ax.step(x, y, **param_dict)
        else:
            x = profile[variable+'_value'].values
            y = profile.y_mid.values
            if param_dict is None:
                ax.plot(x, y, )
            else:
                ax.plot(x, y, **param_dict)

        # set label
        y_lim_min = np.nanmin(ax.get_ylim())
        y_lim_max = np.nanmax(ax.get_ylim())
        x_lim_min = np.nanmin(ax.get_xlim())
        x_lim_max = np.nanmax(ax.get_xlim())
        if v_ref_loc == 'ice surface':
            ax.set_ylabel('Distance from ice surface (m)')
            ax.xaxis.set_label_position('top')
            ax.xaxis.tick_top()
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(False)
        elif v_ref_loc == 'ice bottom':
            ax.set_ylabel('Distance from ice bottom (m)')
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(True)
            ax.xaxis.set_label_position('bottom')
            ax.xaxis.tick_bottom()
        elif v_ref_loc == 'water surface':
            ax.set_ylabel('Distance from water surface (m)')
        else:
            ax.set_ylabel('Ice thickness (m)')
            module_logger.waring('Vertical reference location not defined for plot')
        ax.set_xlabel(variable.capitalize() + ' (' + variable_unit_dict[variable] + ')')

        if v_ref_dir == 'down':
            if all(y <= 0):
                ax.set_ylim([0, y_lim_min])
            elif all(0 <= y):
                ax.set_ylim([y_lim_max, 0])
            else:
                ax.set_ylim([y_lim_max, y_lim_min])
        else:
            if all(y <= 0):
                ax.set_ylim([y_lim_min, 0])
            elif all(0 <= y):
                ax.set_ylim([0, y_lim_max])
            else:
                ax.set_ylim([y_lim_min, y_lim_max])

        # # decorator
        if all(x <= 0):
            ax.yaxis.set_label_position('right')
            ax.yaxis.tick_right()
            ax.spines['right'].set_visible(True)
            ax.spines['left'].set_visible(False)
            ax.set_xlim([x_lim_min, 0])
        else:
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(True)
            ax.yaxis.set_label_position('left')
            ax.yaxis.tick_left()
        if all(0 <= x):
            ax.set_xlim([0, x_lim_max])

        if display_figure:
            plt.show()
    return ax


def plot_profiles(profile, variables=None, ax=ax, ax_dict=None, param_dict=param_dict, display_figure=False):
    from pysic.core.profile import Profile
    if variables is None:
        variables = profile.variable

    if ax is None:
        _, ax = plt.subplots(1, len(variables), sharey=True)
    elif len(ax) < len(variables):
        module_logger.warning('length of ax does not match number of variable')

    if not isinstance(ax, np.ndarray):
        ax = np.array([ax])

    if ax_dict is None:
        ax_dict = {variables[ii]: ii for ii in range(0, len(ax))}
    if 'name' in profile.columns:
        for core in profile.name.unique():
            profile_core = profile.loc[profile.name == core]
            profile_core = profile_core.drop(['name'], axis=1)
            profile_core = Profile(profile_core)
            ax = plot_profiles(profile_core, variables=variables, ax=ax, ax_dict=ax_dict, param_dict=param_dict)
    else:
        for variable in variables:
            ax_n = ax_dict[variable]
            profile_data = profile.select_variable(variable)
            ax[ax_n] = plot_profile(profile_data, ax=ax[ax_n], param_dict=param_dict)

    if display_figure:
        plt.show()

    return ax
