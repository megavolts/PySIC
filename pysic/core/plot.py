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

from pysic.core.profile import *
from pysic.core.profile import Profile

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


## Old plot

def plot_profileV0(profile, ax=None, param_dict=None):
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

    # if profile not empty
    if not profile.empty:
        # step variable
        if not profile.y_low.isnull().all() and profile.variables()[0] not in continuous_property:
            x = []
            y = []
            for ii in profile.index.tolist():
                y.append(profile['y_low'][ii])
                y.append(profile['y_sup'][ii])
                x.append(profile[prop][ii])
                x.append(profile[prop][ii])
        # continuous variable
        else:
            x = profile[prop].values
            y = profile.y_mid.values
        if param_dict is None:
            ax.plot(x, y)
        else:
            ax.plot(x, y, **param_dict)

    return ax


def plot_profile(profile, ax=None, param_dict=None):
    """
    :param profile:
    :param ax:
    :param param_dict:
    :return:
    """
    profile = Profile(profile)

    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    variable = profile.variables()
    if len(variable) > 1:
        module_logger.error("more than one variable is selected")
        return 0
    elif len(variable) < 1:
        module_logger.warning("no data in the profile")
    else:
        variable = variable[0]

    profile = profile.select_property(variable)
    # if profile not empty
    if not profile.empty:
        # step variable
        continuous_variable = False
        if variable in continuous_property:
            continuous_variable = True
        elif 'y_low' not in profile:
            continuous_variable = True
        elif profile[profile.variable == variable].y_low.isnull().all():
            continuous_variable = True

        if continuous_variable:
            x = profile[variable].values
            y = profile.y_mid.values
        else:
            x = []
            y = []
            for ii in profile[profile.variable == variable].index.tolist():
                y.append(profile['y_low'][ii])
                y.append(profile['y_sup'][ii])
                x.append(profile[variable][ii])
                x.append(profile[variable][ii])

        # continuous variable
        if param_dict is None:
            ax.plot(x, y)
        else:
            ax.plot(x, y, **param_dict)

        # label
        y_lim_max = np.nanmax(np.nanmax(ax.get_ylim()))
        if 'v_ref' in profile.columns:
            if len(profile.v_ref.unique()) == 1 and profile.v_ref.unique()[0] == 'bottom':
                ax.set_ylim([0, y_lim_max])
                ax.set_ylabel('Distance from ice bottom (m)')
            elif len(profile.v_ref.unique()) == 1 and profile.v_ref.unique()[0] == 'top':
                ax.set_ylim([y_lim_max, 0])
                ax.set_ylabel('Distance from ice surface (m)')
            else:
                ax.set_ylim([y_lim_max, 0])
                ax.set_ylabel('Ice thickness (m)')
        else:
            ax.set_ylim([y_lim_max, 0])
            ax.set_ylabel('Ice thickness (m)')
        ax.set_xlabel(variable.capitalize())
    else:
        module_logger.warning('Empty profile')
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

    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    # if profile not empty
    if not profile.empty:
        # step variable
        if not profile[profile.variable == variable].y_low.isnull().all() and variable not in continuous_property:
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


def plot_profile_variable(ic_data, variable_dict=None, ax=None, param_dict=None):
    """
    :param ic_data:
        pd.DataFrame
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """

    if variable_dict == None:
        print('FAILING: need at least one variable')
        variable_dict = {'variable': ic_data.variables()}

    if 'variable' not in variable_dict.keys():
        module_logger.error("a variable should be specified for plotting")

    profile = select_profile(ic_data, variable_dict)
    profile['variable'] = variable_dict['variable']
    if not profile.empty:
        ax = plot_profile(profile, ax=ax, param_dict=param_dict)
    return ax


def plot_all_profile_variable(ic_data, variable_dict={}, ax=None, ax_dict=None, display_figure=False, param_dict={}):
    """
    V2 : 2019-03-09
    :param ic_data:
        pd.DataFrame
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """

    ic_data = Profile(ic_data)

    # TODO : there could be only 1 ice core
    if len(variable_dict) == 0:
        variable_dict = {'variable': sorted(ic_data.variables(notnan=True))}

    if 'variable' not in variable_dict.keys():
        try:
            variable_dict.update({'variable': ic_data.variables()})
        except:  # TODO determine error if variable dict isnot there
            module_logger.error("a variable should be specified for plotting")

    # remove variable from variable_dict if empty
    for variable in variable_dict['variable']:
        if ic_data[variable].isna().all():
            variable_dict['variable'].remove(variable)

    if ax is None:
        _, ax = plt.subplots(1, len(variable_dict['variable']), sharey=True)
    elif len(ax) < len(variable_dict['variable']):
        module_logger.warning('length of ax does not match number of variable')

    if not isinstance(ax, np.ndarray):
        ax = np.array([ax])

    if ax_dict is None:
        ax_dict = {variable_dict['variable'][ii]: ii for ii in range(0, len(ax))}

    for variable in variable_dict['variable']:
        ax_n = ax_dict[variable]
        profile = Profile(ic_data.copy())
        profile.keep_variable(variable)
        ax[ax_n] = plot_profile(profile, ax=ax[ax_n], param_dict=param_dict)
        ax[ax_n].set_xlabel(variable)
        ax[ax_n].spines['top'].set_visible(False)
        ax[ax_n].spines['right'].set_visible(False)
        if variable + '_core' in ic_data.columns:
            if len(variable_dict['variable']) > 1:
                name = ic_data['temperature_core'].unique()[0]
                if name == ic_data.name.unique()[0]:
                    name = ''
            else:
                 name = ic_data['name'].unique()[0]
            print(name, ic_data['name'].unique()[0], ic_data['temperature_core'].unique()[0],
                  len(variable_dict['variable']))
        else:
            name = ic_data.name.unique()[0]
        ax[ax_n].set_title(name)

    y_lim_max = np.max([np.max(ax[ii].get_ylim()) for ii in range(0, len(ax))])
    if 'v_ref' in ic_data.columns:
        if len(ic_data.v_ref.unique()) == 1 and ic_data.v_ref.unique()[0] == 'bottom':
            ax[0].set_ylim([0, y_lim_max])
            ax[0].set_ylabel('Distance from ice bottom (m)')
        elif len(ic_data.v_ref.unique()) == 1 and ic_data.v_ref.unique()[0] == 'top':
            ax[0].set_ylim([y_lim_max, 0])
            ax[0].set_ylabel('Distance from ice surface (m)')
        else:
            ax[0].set_ylim([y_lim_max, 0])
            ax[0].set_ylabel('Ice thickness (m)')
    else:
        ax[0].set_ylim([y_lim_max, 0])
        ax[0].set_ylabel('Ice thickness (m)')
    plt.subplots_adjust(top=0.85, wspace=0.2, hspace=0.2)
    if display_figure:
        plt.show()

    return ax, ax_dict


def plot_stat_profile(ic_data, variable_dict, ax=None, param_dict=None):
    """
    :param ic_data:
        pd.DataFrame
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    if 'variable' not in variable_dict.keys():
        module_logger.error("a variable should be specified for plotting")

    variable_dict.pop('stats')

    profile = select_profile(ic_data, variable_dict)
    _ax = plot_profile(profile, ax=ax, param_dict=param_dict)

    return _ax


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
    else:
        ii_variable = variable_dict['variable']

    _profiles = select_profile(ic_data, variable_dict)

    x_mean = _profiles[[ii_variable+'_min', 'y_low', 'y_sup']]
    x_std = _profiles[[ii_variable+'_std', 'y_low', 'y_sup']]

    if x_mean.__len__() != 0:
        if x_std.__len__() < x_mean.__len__():
            index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
            x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))

        if not x_mean.y_low.isnull().all():
            y_low = x_mean['y_low']
            y_sup = x_mean['y_sup']
            y = np.concatenate((y_low.tolist(), [y_sup.tolist()[-1]]))
            x_std_l = _profiles[ii_variable+'_mean'] - _profiles[ii_variable+'_std']
            x_std_h = _profiles[ii_variable+'_mean'] + _profiles[ii_variable+'_std']

            x_std_l = plt_step(x_std_l.tolist(), y).transpose()
            x_std_h = plt_step(x_std_h.tolist(), y).transpose()
        elif x_mean.y_low.isnull().all():
            y_std = x_mean['y_mid']
            x_std_l = np.array([_profiles[ii_variable+'_mean'] - np.nan_to_num(_profiles[ii_variable+'_std']), y_std])
            x_std_h = np.array([_profiles[ii_variable+'_mean'] + np.nan_to_num(_profiles[ii_variable+'_std']), y_std])

        if 'facecolor' not in param_dict.keys():
            param_dict['facecolor'] = {'black'}
        if 'alpha' not in param_dict.keys():
            param_dict['alpha'] = {0.3}
        if 'label' not in param_dict.keys():
            param_dict['label'] = str(r"$\pm$" + "std dev")
        #x_std_l = np.atleast_2d(x_std_l)
        #x_std_h = np.atleast_2d(x_std_h)
        ax.fill_betweenx(x_std_l[1, :], x_std_l[0, :], x_std_h[0, :], facecolor='black', alpha=0.2,
                         label=param_dict['label'])  # use to be x_std_l [1] at first
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
    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0
    else:
        variable = variable_dict['variable']

    profile = select_profile(ic_data, variable_dict)

    # if profile not empty
    if not profile.empty:
        # step variable
        if not profile.y_low.isnull().all():
            x = []
            y = []
            for ii in profile.index.tolist():
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
    else:
        return 0


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
    else:
        ii_variable = variable_dict['variable']

    _profiles = select_profile(ic_data, variable_dict)

    x_mean = _profiles[[ii_variable+'_mean', 'y_low', 'y_sup']]
    x_std = _profiles[[ii_variable+'_std', 'y_low', 'y_sup']]

    # profile is not empty
    if not x_mean.empty:
        # x_std and x_mean same length
        if x_std.__len__() < x_mean.__len__():
            index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
            x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))

        if not x_mean.y_low.isnull().all():
            y_low = x_mean['y_low']
            y_sup = x_mean['y_sup']
            y = np.concatenate((y_low.tolist(), [y_sup.tolist()[-1]]))
            x_std_l = x_mean[ii_variable+'_mean'] - x_std[ii_variable+'_std']
            x_std_h = x_mean[ii_variable+'_mean'] + x_std[ii_variable+'_std']

            index_outlier = x_std_l[(x_std_l <= 0)].index.tolist()
            for ii in index_outlier:
                l = ''
                for key in variable_dict:
                    if isinstance(variable_dict[key], str):
                        l += key + ': ' + variable_dict[key] + '; '
                    else:
                        l += key + ': ' + str(variable_dict[key]) + '; '
                l = l[:-2]
                module_logger.warning('%s index of %s bin modified lower value for logarithmic scale' % (ii, l))

            if index_outlier.__len__() > 0:
                variable_dict.update({'stats': 'min'})
                x_min = select_profile(ic_data, variable_dict).reset_index(drop=True)
                ii_outlier = 1
                while index_outlier.__len__() > 0:
                    # for index in index_outlier:
                    x_std_l[(x_std_l <= 0)] = x_mean.loc[x_mean.index.isin(index_outlier), ii_variable] - x_std.loc[x_std.index.isin(index_outlier), ii_variable] / 10
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

        ax.fill_betweenx(x_std_l[1, :], x_std_l[0, :], x_std_h[0, :], facecolor=param_dict['facecolor'], alpha=0.2,
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
    n = select_profile(ic_data, variable_dict).reset_index()[ii_variable +'_count'].values
    variable_dict.update({'stats': stat})
    pos = select_profile(ic_data, variable_dict).reset_index()[ii_variable + '_' + stat].values

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


def plot_envelop(ic_data, variable_dict, ax=None, param_dict={}, flag_number=False, legend=False, z_delta=0.01,
                 every=1):
    """
    :param ic_data:
    :param variable_dict:
        contains variable to plot at least
    :param ax:
    :param param_dict:
    :return:
    """
    # TODO: check if all stat are present for the variable

    prop = variable_dict['variable']
    ic_data = Profile(ic_data)
    _profiles = select_profile(ic_data, variable_dict)

    # minimum
    param_dict.update({'linewidth': 1, 'color': 'b', 'label': 'min'})
    ax = plot_profileV0(_profiles[['y_low', 'y_mid', 'y_sup', prop+'_min', 'variable']], param_dict=param_dict, ax=ax)

    # mean
    param_dict.update({'linewidth': 1, 'color': 'k', 'label': 'mean'})
    ax = plot_profileV0(_profiles[['y_low', 'y_mid', 'y_sup', prop+'_mean', 'variable']], param_dict=param_dict, ax=ax)

    # maximum
    param_dict.update({'linewidth': 1, 'color': 'r', 'label': 'max'})
    ax = plot_profileV0(_profiles[['y_low', 'y_mid', 'y_sup', prop+'_max', 'variable']], param_dict=param_dict, ax=ax)

    # std/mean envelop
    plot_mean_envelop(ic_data, variable_dict, ax=ax)
    if flag_number:
        variable_dict.update({'stats': 'mean'})
        ax = plot_number(ic_data, variable_dict=variable_dict, ax=ax, z_delta=0.01, every=1)

    # cosmetic
    ax.xaxis.set_label_position('top')
    y_lim_max = np.nanmax(np.nanmax(ax.get_ylim()))
    if 'v_ref' in ic_data.columns:
        if len(ic_data.v_ref.unique()) == 1 and ic_data.v_ref.unique()[0] == 'bottom':
            ax.set_ylim([0, y_lim_max])
            ax.set_ylabel('Distance from ice bottom (m)')
        elif len(ic_data.v_ref.unique()) == 1 and ic_data.v_ref.unique()[0] == 'top':
            ax.set_ylim([y_lim_max, 0])
            ax.set_ylabel('Distance from ice surface (m)')
        else:
            ax.set_ylim([y_lim_max, 0])
            ax.set_ylabel('Ice thickness (m)')
    else:
        ax.set_ylim([y_lim_max, 0])
        ax.set_ylabel('Ice thickness (m)')
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xlabel(variable_dict['variable'].capitalize() + ' ' + variable_unit_dict[variable_dict['variable']])

    if legend:
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D

        legend_elements = [Line2D([], [], color='blue', label='min'),
                           Line2D([], [], color='black', label='mean'),
                           Line2D([], [], color='red', label='max'),
                           Patch(facecolor='grey', label='$\pm$ std dev')]

        ax.legend(handles=legend_elements, loc='bottom center')

    return ax


def plot_enveloplog(ic_data, variable_dict, ax=None, param_dict={}, flag_number=False, z_delta=0.01, every=1):
    """
    :param ic_data:
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """

    prop = variable_dict['variable']

    # for log scale, replace smallest value by minimum*2

    # minimum
    variable_dict.update({'variable': prop+'_min'})
    param_dict.update({'linewidth': 1, 'color': 'b', 'label': 'min'})
    ax = semilogx_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    variable_dict.update({'variable': prop+'_mean'})
    param_dict.update({'color': 'k'})
    ax = semilogx_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    variable_dict.update({'variable': prop+'_max'})
    param_dict.update({'color': 'r'})
    ax = semilogx_profile_variable(ic_data, variable_dict=variable_dict, param_dict=param_dict, ax=ax)
    # variable_dict.update({'variable': prop})
    # param_dict = None
    # ax = semilogx_mean_envelop(ic_data, variable_dict, ax=ax)

    return ax
