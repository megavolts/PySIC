#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.plot.py : Core and CoreStack class

"""
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

from seaice.core.profile import *
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
__all__ = ["plot_profile", "semilogx_profile", "plot_profile_variable", "semilogx_profile_variable",
           "plot_mean_envelop", "plot_number", "plot_envelop", "plot_enveloplog"]

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
    _ax = plot_profile(profile, ax=ax, param_dict=param_dict)
    return _ax


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


def plot_mean_envelop(ic_data, variable_dict, ax=None, param_dict=None):
    """

    :param ic_data:
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """

    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if param_dict is None:
        param_dict = {}

    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0

    ii_variable = variable_dict['variable']

    variable_dict.update({'stats': 'mean'})
    x_mean = select_profile(ic_data, variable_dict).reset_index()
    variable_dict.update({'stats': 'std'})
    x_std = select_profile(ic_data, variable_dict).reset_index()

    if x_mean.__len__() != 0:
        if x_std.__len__() < x_mean.__len__():
            index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
            x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))

        if not x_mean.y_low.isnull().all():
            y_low = x_mean['y_low']
            y_sup = x_mean['y_sup']
            y = np.concatenate((y_low.tolist(), [y_sup.tolist()[-1]]))
            x_std_l = x_mean[ii_variable] - x_std[ii_variable]
            x_std_h = x_mean[ii_variable] + x_std[ii_variable]

            x_std_l = plt_step(x_std_l.tolist(), y).transpose()
            x_std_h = plt_step(x_std_h.tolist(), y).transpose()
        elif x_mean.y_low.isnull().all():
            y_std = x_mean['y_mid']
            x_std_l = np.array([x_mean[ii_variable] - np.nan_to_num(x_std[ii_variable]), y_std])
            x_std_h = np.array([x_mean[ii_variable] + np.nan_to_num(x_std[ii_variable]), y_std])

        if 'facecolor' not in param_dict.keys():
            param_dict['facecolor'] = {'black'}
        if 'alpha' not in param_dict.keys():
            param_dict['alpha'] = {0.3}
        if 'label' not in param_dict.keys():
            param_dict['label'] = str(r"$\pm$" + "std dev")
        ax.fill_betweenx(x_std_l[1, :], x_std_l[0, :], x_std_h[0, :], facecolor='black', alpha=0.2,
                         label=param_dict['label'])
    return ax


def semilogx_mean_envelop(ic_data, variable_dict, ax=None, param_dict=None):
    """

    :param ic_data:
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if param_dict is None:
        param_dict = {}

    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0

    ii_variable = variable_dict['variable']

    variable_dict.update({'stats': 'mean'})
    x_mean = select_profile(ic_data, variable_dict).reset_index()
    variable_dict.update({'stats': 'std'})
    x_std = select_profile(ic_data, variable_dict).reset_index()

    if x_mean.__len__() != 0:
        if x_std.__len__() < x_mean.__len__():
            index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
            x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))

        if not x_mean.y_low.isnull().all():
            y_low = x_mean['y_low']
            y_sup = x_mean['y_sup']
            y = np.concatenate((y_low.tolist(), [y_sup.tolist()[-1]]))
            x_std_l = x_mean[ii_variable] - x_std[ii_variable]
            x_std_h = x_mean[ii_variable] + x_std[ii_variable]

            index_outlier = x_std_l[(x_std_l <= 0)].index.tolist()
            for ii in index_outlier:
                l = ''
                for key in variable_dict:
                    l += key + ': ' + variable_dict[key] + '; '
                l = l[:-2]
                module_logger.warning('%s index of %s bin modified lower value for logarithmic scale' % (ii, l))

            ii_outlier = 1
            if index_outlier.__len__() > 0:
                variable_dict.update({'stats': 'min'})
                x_min = select_profile(ic_data, variable_dict).reset_index(drop=True)
                while index_outlier.__len__() > 0:
                    # for index in index_outlier:
                    x_std_l[(x_std_l <= 0)] = x_min.loc[x_min.index.isin(index_outlier), ii_variable] - x_std.loc[
                                                                                                            x_std.index.isin(
                                                                                                                index_outlier), ii_variable] / ii_outlier
                    index_outlier = x_std_l[(x_std_l <= 0)].index.tolist()
                    ii_outlier += 1

            x_std_l = plt_step(x_std_l.tolist(), y).transpose()
            x_std_h = plt_step(x_std_h.tolist(), y).transpose()
        elif x_mean.y_low.isnull().all():
            y_std = x_mean['y_mid']
            x_std_l = np.array([x_mean[ii_variable] - np.nan_to_num(x_std[ii_variable]), y_std])
            x_std_h = np.array([x_mean[ii_variable] + np.nan_to_num(x_std[ii_variable]), y_std])

        if 'facecolor' not in param_dict.keys():
            param_dict['facecolor'] = {'black'}
        if 'alpha' not in param_dict.keys():
            param_dict['alpha'] = {0.3}
        if 'label' not in param_dict.keys():
            param_dict['label'] = str(r"$\pm$" + "std dev")

        ax.fill_betweenx(x_std_l[1, :], x_std_l[0, :], x_std_h[0, :], facecolor='black', alpha=0.2,
                         label=param_dict['label'])
    return ax


def plot_number(ic_data, variable_dict, ax=None, position='right', x_delta=0.1, z_delta=0.05, every=1,
                fontsize=mpl.rcParams['font.size']):
    """
    :param ic_data:
    :param variable_dict:
    :param ax:
    :param position:
    :param x_delta:
    :param z_delta:
    :param every:
    :param fontsize:
    :return:
    """
    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0

    ii_variable = variable_dict['variable']

    if position == 'left':
        stat = 'min'
    elif position == 'center':
        stat = 'mean'
    else:
        stat = 'max'

    depth = select_profile(ic_data, variable_dict).reset_index()['y_mid'].values
    n = select_profile(ic_data, variable_dict).reset_index()['n'].values
    variable_dict.update({'stats': stat})
    pos = select_profile(ic_data, variable_dict).reset_index()[ii_variable].values

    # check for nan value:
    depth = depth[~np.isnan(pos)]
    n = n[~np.isnan(pos)]
    pos = pos[~np.isnan(pos)]

    for ii in np.arange(0, pos.__len__(), every):
        ax.text(pos[ii] + x_delta, depth[ii] + z_delta, str('(%.0f)' % n[ii]), fontsize=fontsize)

    return ax


def plt_step(x, y):
    # step function
    xy = np.array([x[0], y[0]])
    for ii in range(x.__len__()-1):
        xy = np.vstack((xy, [x[ii], y[ii+1]]))
        xy = np.vstack((xy, [x[ii+1], y[ii+1]]))
    return xy


def plot_envelop(ic_data, variable_dict, ax=None, param_dict={}, flag_number=False, z_delta=0.01, every=1):
    """
    :param ic_data:
    :param variable_dict:
        contains variable to plot at least
    :param ax:
    :param param_dict:
    :return:
    """

    # TODO: check if all stat are present for the variable

    variable_dict.update({'stats': 'min'})
    param_dict.update({'linewidth': 1, 'color': 'b', 'label': 'min'})
    ax = plot_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    variable_dict.update({'stats': 'mean'})
    param_dict.update({'color': 'k'})
    ax = plot_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    variable_dict.update({'stats': 'max'})
    param_dict.update({'color': 'r'})
    ax = plot_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    variable_dict.pop('stats')
    ax = plot_mean_envelop(ic_data, variable_dict, ax=ax)
    if flag_number:
        variable_dict.update({'stats': 'mean'})
        ax = plot_number(ic_data, variable_dict=variable_dict, ax=ax, z_delta=0.01, every=1)
    return ax


def plot_enveloplog(ic_data, variable_dict, ax=None, param_dict={}, flag_number=False, z_delta=0.01, every=1):
    """
    :param ic_data:
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """

    # for log scale, replace smallest value by minimum*2
    variable_dict.update({'stats': 'min'})
    param_dict.update({'linewidth': 1, 'color': 'b', 'label': 'min'})
    ax = semilogx_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    variable_dict.update({'stats': 'mean'})
    param_dict.update({'color': 'k'})
    ax = semilogx_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    variable_dict.update({'stats': 'max'})
    param_dict.update({'color': 'r'})
    ax = semilogx_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    variable_dict.pop('stats')
    ax = semilogx_mean_envelop(ic_data, variable_dict, ax=ax)

    return ax
