#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.plot.py : Core and CoreStack class

"""
import logging
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from seaice.core.profile import *
from seaice.core.profile import Profile
from seaice.core.corestack import CoreStack

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

# New version have 2019 in name

variable_unit_dict = {'salinity': '(g kg$^{-1}$)', 'temperature': '$^\circ$C'}
TOL = 1e-12


# Old plot
def plot_profileV0(profile, ax=None, param_dict={}):
    """
    :param profile:
    :param ax:
    :param param_dict:
    :return:
    """
    warnings.warn('Deprecated, use plot_profile() instead', FutureWarning)
    prop = [key for key in profile if key not in ['y_low', 'y_mid', 'y_sup']][0]

    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    # if profile not empty
    if not profile.empty:
        # step variable
        if not profile.y_low.isnull().all():
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
        if param_dict:
            ax.plot(x, y, **param_dict)
        else:
            ax.plot(x, y)
    return ax


def plot_profile(profile, ax=None, param_dict={}):
    """
    :param profile:
    :param ax:
    :param param_dict:
    :return:
    """

    profile = Profile(profile)

    # check parameters
    if len(profile.variables()) > 1:
        module_logger.warning('More than one variable to plot in the profile. Using plot.profiles instead')
        fig, ax = plot_profiles(profile, ax=ax, param_dict=param_dict)
        return fig, ax
    else:
        variable = profile.variables()[0]
        profile = profile.reset_index(drop=True)

    f_axnew = False
    if ax is None:
        plt.figure()
        fig, ax = plt.subplots(1, 1)
        f_axnew = True
        y_lim = []
    elif isinstance(ax, np.ndarray):
        y_lim = ax[0].get_ylim()
    else:
        y_lim = ax.get_ylim()
    # if profile not empty
    if not profile.empty:
        # continuous variable
        if profile.y_low.isnull().all() or variable in ['temperature']:
            x = profile[variable].values
            y = profile.y_mid.values

        # step variable
        else:
            # discard np.nan value
            x = []
            y = []

            index = profile.index.tolist()
            index_max = max(index)

            for ii in index:
                y.append(profile['y_low'][ii])
                y.append(profile['y_sup'][ii])
                x.append(profile[variable][ii])
                x.append(profile[variable][ii])

                # if step profile is discontinued, filled with np.nan
                if ii < index_max and np.abs(profile['y_sup'][ii] - profile['y_low'][ii+1]) > TOL:
                    y.append(profile['y_sup'][ii])
                    y.append(profile['y_low'][ii+1])
                    x.append(np.nan)
                    x.append(np.nan)

        # continuous variable
        if param_dict:
            ax.plot(x, y, **param_dict)
        else:
            ax.plot(x, y)

    # label
    ax.set_xlabel(variable + '  ' + variable_unit_dict[variable])

    if len(y_lim) > 0:
        y_min = min(min(y), min(y_lim))
        y_max = max(max(y), max(y_lim))
    else:
        y_min = min(y)
        y_max = max(y)

    # aesthetic
    ax.spines['right'].set_visible(False)
    if profile.v_ref.unique()[0] == 'bottom':
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.set_ylabel('Distance from\nice/water interface(m)')
        ax.set_ylim([y_min, y_max])
        ax.xaxis.set_label_position('bottom')
        ax.xaxis.set_ticks_position('bottom')
    else:
        ax.spines['top'].set_visible(True)
        ax.spines['bottom'].set_visible(False)
        ax.xaxis.set_label_position('top')
        ax.xaxis.set_ticks_position('top')
        ax.set_ylabel('Distance from\n snow/ice interface(m)')
        ax.set_ylim([y_max, y_min])

    if f_axnew:
        return fig, ax
    else:
        return ax


def plot_profiles(profiles, ax=None, param_dict={}):
    """
    :param profiles:
    :param ax:
    :param param_dict:
    :return:
    """

    variables = sorted(profiles.variables())

    f_axarray = True
    f_axnew = False
    if ax is None:
        plt.figure()
        fig, ax = plt.subplots(1, len(variables), sharey=True)
        f_axnew = True
    elif not isinstance(ax, np.ndarray):
        ax = np.array([ax])
        f_axarray = False
        if len(ax) < len(variables):
            module_logger.warning('Fig does not have enough subplots, regenerating subplots array')
            plt.figure()
            fig, ax = plt.subplots(1, len(variables), sharey=True)
            f_axnew = True
            f_axarray = True

    n_ax = 0
    y_max = 0

    for variable in variables:
        profile = profiles.select_variables(variable).copy()
        ax[n_ax] = plot_profile(profile, ax=ax[n_ax], param_dict=param_dict)

        # TODO: set maximum ylim as maximum value of either yaxis
        # aesthetic
        if n_ax > 0:
            ax[n_ax].yaxis.label.set_visible(False)
            ax[n_ax].yaxis.tick_left()

        if y_max < max(ax[n_ax].get_ylim()):
            y_max = max(ax[n_ax].get_ylim())

        if profiles.v_ref.unique()[0] == 'top':
            ax[n_ax].set_ylim([y_max, 0])
        elif profiles.v_ref.unique()[0] == 'bottom':
            ax[n_ax].set_ylim([0, y_max])

        n_ax += 1

    if f_axnew:
        return fig, ax
    else:
        if f_axarray:
            return ax
        else:
            return ax[0]


def semilogx_profile(profile, ax=None, param_dict={}):
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


def plot_profile_variable(ic_data, variable_dict=None, ax=None, param_dict={}):
    """
    :param ic_data:
        pd.DataFrame
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    if variable_dict == None:
        variable_dict = {'variable':ic_data.variables()}

    if 'variable' not in variable_dict.keys():
        module_logger.error("a variable should be specified for plotting")

    ic_data = Profile(ic_data)
    profile = ic_data.select_variables(variable_dict['variable'])

    #profile = select_profile(ic_data, variable_dict)
    _ax = plot_profile(profile, ax=ax, param_dict=param_dict)
    return _ax


from seaice.core import non_float_property


def plot_all_variable_in_stack(ic_data, variable_dict={}, ax=None, ax_dict=None, display_figure=False, param_dict={},
                               t_snow = False):
    """
    V2 : 2019-03-09
    :param ic_data:
        pd.DataFrame
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    try:
        ic_data = Profile(ic_data)
    except ValueError:
        module_logger.error('ic_data is not a Profile')

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
        # remove non numeric variable:
        elif variable in non_float_property:
            variable_dict['variable'].remove(variable)

    if len(variable_dict['variable']) == 0:
        _, ax = plt.subplots(1, 1)
        ax_dict = {}
        return ax, ax_dict

    if ax_dict is None:
        ax_dict = {variable: ii for ii, variable in enumerate(variable_dict['variable'])}

    if ax is None:
        n_ax = max(len(variable_dict['variable']), len(ax_dict))
        _, ax = plt.subplots(1, n_ax, sharey=True)
    elif len(ax) < len(variable_dict['variable']):
        module_logger.warning('length of ax does not match number of variable')

    if not isinstance(ax, np.ndarray):
        ax = np.array([ax])

    for variable in variable_dict['variable']:
        if variable not in ax_dict:
            ax_dict.update({variable: max(ax_dict.keys()+1)})

    cores = ic_data.name.unique()
    cmap = plt.get_cmap('jet_r')
    color_core = {name: cmap(float(i)/len(cores)) for i, name in enumerate(cores)}
    for variable in variable_dict['variable']:
        ax_n = ax_dict[variable]
        profile = Profile(ic_data.copy())
        profile.keep_variable(variable)
        for core in profile.name.unique():
            param_dict.update({'color': color_core[core]})
            ax[ax_n] = plot_profile(profile[profile.name == core], ax=ax[ax_n], param_dict=param_dict)
        ax[ax_n].set_xlabel(variable)
        ax[ax_n].xaxis.set_label_position('top')
        ax[ax_n].xaxis.tick_top()
        ax[ax_n].spines['top'].set_visible(True)
        ax[ax_n].spines['bottom'].set_visible(False)
        ax[ax_n].spines['right'].set_visible(False)
        #ax_pos = ax[ax_n].get_position().get_points()
        #ax[ax_n].set_position(np.concatenate((ax_pos[0], ax_pos[1])))

    if 'v_ref' in ic_data.columns:
        if len(ic_data.v_ref.unique()) == 1 and ic_data.v_ref.unique()[0] == 'bottom':
            ax[0].set_ylim([min(ax[0].get_ylim()), max(ax[0].get_ylim())])
            ax[0].set_ylabel('Distance from\nice/water inferface (m)')
        elif len(ic_data.v_ref.unique()) == 1 and ic_data.v_ref.unique()[0] == 'bottom':
            ax[0].set_ylim([max(ax[0].get_ylim()), min(ax[0].get_ylim())])
            ax[0].set_ylabel('Distance from ice surface(m)')
        else:
            ax[0].set_ylim([max(ax[0].get_ylim()), min(ax[0].get_ylim())])
            ax[0].set_ylabel('Ice thickness (m)')
    else:
        ax[0].set_ylim([max(ax[0].get_ylim()), min(ax[0].get_ylim())])
        ax[0].set_ylabel('Ice thickness (m)')

    if not t_snow:
        ax[0].set_ylim([max(ax[0].get_ylim()), 0])

    import matplotlib.lines as mlines
    h = [mlines.Line2D([], [], color=color_core[core]) for core in cores]
    l = list(cores)
    if min(ax[0].get_ylim()) <= 0:
        h += [mlines.Line2D([], [], color='k', linestyle=':')]
        l += ['ice surface']
        for ii, _ in enumerate(ax):
            ax[ii].plot([min(ax[ii].get_xlim()), max(ax[ii].get_xlim())], [0, 0], 'k:')
    ax[0].legend(h, l, loc='lower left', fancybox=True, shadow=False, frameon=True, ncol=1)
    plt.tight_layout()

    if display_figure:
        plt.show()
    return ax, ax_dict


def plot_all_variable_in_stack_by_date(ic_data, variable_dict={}, ax=None, ax_dict=None, display_figure=False,
                                       param_dict={}, t_snow = False):
    """
    V2 : 2019-03-09
    :param ic_data:
        pd.DataFrame
    :param variable_dict:
    :param ax:
    :param param_dict:
    :return:
    """
    try:
        ic_data = CoreStack(ic_data.copy())
    except ValueError:
        module_logger.error('ic_data is not a Profile')

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
        # remove non numeric variable:
        elif variable in non_float_property:
            variable_dict['variable'].remove(variable)

    if len(variable_dict['variable']) == 0:
        _, ax = plt.subplots(1, 1)
        ax_dict = {}
        return ax, ax_dict

    if ax_dict is None:
        ax_dict = {variable: ii for ii, variable in enumerate(variable_dict['variable'])}

    if ax is None:
        n_ax = max(len(variable_dict['variable']), len(ax_dict))
        _, ax = plt.subplots(1, n_ax, sharey=True)
    elif len(ax) < len(variable_dict['variable']):
        module_logger.warning('length of ax does not match number of variable')

    if not isinstance(ax, np.ndarray):
        ax = np.array([ax])

    for variable in variable_dict['variable']:
        if variable not in ax_dict:
            ax_dict.update({variable: max(ax_dict.keys()+1)})

    #cores = ic_data.name.unique()
    dates = ic_data.date.dt.date.unique()
    cmap = plt.get_cmap('jet_r')
    color_date = {name: cmap(float(i)/len(dates)) for i, name in enumerate(dates)}
    for variable in variable_dict['variable']:
        ax_n = ax_dict[variable]
        # keep only data from variable:
        profiles = Profile(ic_data.select_variables(variable))
        for date in dates:
            for core in profiles.loc[profiles.date.dt.date == date, 'name'].unique():
                param_dict.update({'color': color_date[date]})
                ax[ax_n] = plot_profile(profiles[profiles.name == core], ax=ax[ax_n], param_dict=param_dict)
        ax[ax_n].set_xlabel(variable)
        ax[ax_n].xaxis.set_label_position('top')
        ax[ax_n].xaxis.tick_top()
        ax[ax_n].spines['top'].set_visible(True)
        ax[ax_n].spines['bottom'].set_visible(False)
        ax[ax_n].spines['right'].set_visible(False)

    if 'v_ref' in ic_data.columns:
        if len(ic_data.v_ref.unique()) == 1 and ic_data.v_ref.unique()[0] == 'bottom':
            ax[0].set_ylim([min(ax[0].get_ylim()), max(ax[0].get_ylim())])
            ax[0].set_ylabel('Distance from\nice/water inferface (m)')
        elif len(ic_data.v_ref.unique()) == 1 and ic_data.v_ref.unique()[0] == 'bottom':
            ax[0].set_ylim([max(ax[0].get_ylim()), min(ax[0].get_ylim())])
            ax[0].set_ylabel('Distance from ice surface (m)')
        else:
            ax[0].set_ylim([max(ax[0].get_ylim()), min(ax[0].get_ylim())])
            ax[0].set_ylabel('Ice thickness (m)')
    else:
        ax[0].set_ylim([max(ax[0].get_ylim()), min(ax[0].get_ylim())])
        ax[0].set_ylabel('Ice thickness (m)')

    if not t_snow:
        ax[0].set_ylim([max(ax[0].get_ylim()), 0])

    import matplotlib.lines as mlines
    h = [mlines.Line2D([], [], color=color_date[date]) for date in dates]
    l = list(dates)
    if min(ax[0].get_ylim()) <= 0:
        h += [mlines.Line2D([], [], color='k', linestyle=':')]
        l += ['ice surface']
        for ii, _ in enumerate(ax):
            ax[ii].plot([min(ax[ii].get_xlim()), max(ax[ii].get_xlim())], [0, 0], 'k:')
    ax[0].legend(h, l, loc='lower left', fancybox=True, shadow=False, frameon=True, ncol=1)
    plt.tight_layout()

    if display_figure:
        plt.show()
    return ax, ax_dict


def plot_profile_ordered(profiles, ax=None, ax_dict=None, display_figure=False, param_dict={}):
    """
    V2 : 2019-03-09
    :param profiles:
    :param ax:
    :param param_dict:
    :return:
    """
    try:
        profiles = Profile(profiles)
    except ValueError:
        module_logger.error('ic_data is not a Profile')

    variables = sorted(profiles.variables())

    if len(variables) == 0:
        _, ax = plt.subplots(1, 1)
        ax_dict = {}
        return ax, ax_dict

    # ax should be an array
    f_axarray = True
    f_axnew = False
    if ax is None:
        plt.figure()
        fig, ax = plt.subplots(1, len(variables), sharey=True)
        f_axnew = True
    if not isinstance(ax, np.ndarray):
        ax = np.array([ax])
        f_axarray = False
        if len(ax) < len(variables):
            module_logger.warning('Fig does not have enough subplots, regenerating subplots array')
            plt.figure()
            fig, ax = plt.subplots(1, len(variables), sharey=True)
            f_axnew = True
            f_axarray = True

    if ax_dict is None:
        ax_dict = {variables[ii]: ii for ii in range(0, len(ax))}

    for variable in variables:
        if variable not in ax_dict:
            ax_dict[variable] = max(list(ax_dict.values()))+1

    y_max = 0
    for variable in ax_dict:
        n_ax = ax_dict[variable]
        profiles = profiles.copy()
        profile = profiles.select_variables(variable)

        profile = profile.loc[profile.variable.notnull()]  # remove all nan value

        ax[n_ax] = plot_profile(profile, ax=ax[n_ax], param_dict=param_dict)

        if variable + '_core' in profile.columns:
            name = profile[variable + '_core'].unique()[0]
            if name == profile.names():
                name = ''
        else:
            name = profile.names()
        ax[n_ax].set_title(name)

        if n_ax > 0:
            ax[n_ax].yaxis.label.set_visible(False)

        if y_max < max(ax[n_ax].get_ylim()):
            y_max = max(ax[n_ax].get_ylim())

    y_min = min(profile['y_mid'].min(), profile['y_low'].min())
    if 'v_ref' in profiles.columns:
        if len(profiles.v_ref.unique()) == 1 and profiles.v_ref.unique()[0] == 'bottom':
            ax[0].set_ylim([y_min, y_max])
            ax[0].set_ylabel('Distance from\nice/water inferface (m)')
        elif len(profiles.v_ref.unique()) == 1 and profiles.v_ref.unique()[0] == 'top':
            ax[0].set_ylim([y_max, y_min])
            ax[0].set_ylabel('Distance from snow/ice inferface (m)')
        else:
            ax[0].set_ylim([y_max, y_min])
            ax[0].set_ylabel('Ice thickness (m)')
    else:
        ax[0].set_ylim([y_max, y_min])
        ax[0].set_ylabel('Ice thickness (m)')

    #plt.subplots_adjust(top=0.85, wspace=0.2, hspace=0.2)
    if display_figure:
       plt.show()

    if f_axnew:
        return fig, ax, ax_dict
    else:
        if f_axarray:
            return ax, ax_dict
        else:
            return ax[0], ax_dict

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


def plot_mean_envelop(ic_data, variable_dict, ax=None, param_dict={}):
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

    if 'variable' not in variable_dict.keys():
        module_logger.warning("a variable should be specified for plotting")
        return 0
    else:
        variable = variable_dict['variable']

    ic_data = Profile(ic_data)
    _profiles = ic_data.select_variables(variable)

    x_mean = _profiles[[variable+'_mean', 'y_low', 'y_sup', 'y_mid']].astype(float)
    x_std = _profiles[[variable+'_std', 'y_low', 'y_sup', 'y_mid']].astype(float)

    if x_mean.__len__() != 0:
        if x_std.__len__() < x_mean.__len__():
            index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
            x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))


        if x_mean.y_low.isnull().all() or variable in ['temperature']:
            y_std = x_mean['y_mid']
            x_std_l = np.array([x_mean[variable+'_mean'] - np.nan_to_num(x_std[variable+'_std']), y_std])
            x_std_h = np.array([x_mean[variable+'_mean'] + np.nan_to_num(x_std[variable+'_std']), y_std])
        else:
            y_low = x_mean['y_low']
            y_sup = x_mean['y_sup']
            y = np.concatenate((y_low.tolist(), [y_sup.tolist()[-1]]))
            x_std_l = x_mean[variable+'_mean'] - x_std[variable+'_std']
            x_std_h = x_mean[variable+'_mean'] + x_std[variable+'_std']

            x_std_l = plt_step(x_std_l.tolist(), y).transpose()
            x_std_h = plt_step(x_std_h.tolist(), y).transpose()

        if 'facecolor' not in param_dict.keys():
            param_dict['facecolor'] = {'black'}
        if 'alpha' not in param_dict.keys():
            param_dict['alpha'] = {0.3}
        if 'label' not in param_dict.keys():
            param_dict['label'] = str(r"$\pm$" + "std dev")
        ax.fill_betweenx(x_std_l[1, :], x_std_l[0, :], x_std_h[0, :], facecolor='black', alpha=0.2,
                         label=param_dict['label'])

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


def plot_envelop(ic_stat, variable_dict, ax=None, param_dict={}, flag_number=False, legend=False, z_delta=0.01,
                 every=1):
    """
    :param ic_stat:
    :param variable_dict:
        contains variable to plot at least
    :param ax:
    :param param_dict:
    :return:
    """
    # TODO: check if all stat are present for the variable

    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    ic_stat = Profile(ic_stat)

    # select everything with temperature
    prop = variable_dict['variable']
    profile = ic_stat.select_variables(prop)

    # minimum
    param_dict.update({'linewidth': 2, 'linestyle': '-', 'color': 'b', 'label': 'min'})
    _p = profile[['y_low', 'y_mid', 'y_sup', prop + '_min', 'variable', 'v_ref']]
    _p = _p.rename(columns={prop + '_min': prop}).copy()
    ax = plot_profile(_p, param_dict=param_dict, ax=ax)

    # mean
    param_dict.update({'linewidth': 2, 'linestyle': '-', 'color': 'k'})
    variable_dict.update({'stats': 'mean'})
    _p = profile[['y_low', 'y_mid', 'y_sup', prop + '_mean', 'variable', 'v_ref']]
    _p = _p.rename(columns={prop + '_mean': prop}).copy()
    ax = plot_profile(_p, param_dict=param_dict, ax=ax)

    # maximum
    variable_dict.update({'stats': 'max'})
    param_dict.update({'linewidth': 2, 'linestyle': '-', 'color': 'r'})
    _p = profile[['y_low', 'y_mid', 'y_sup', prop + '_max', 'variable', 'v_ref']]
    _p = _p.rename(columns={prop + '_max': prop}).copy()
    ax = plot_profile(_p, param_dict=param_dict, ax=ax)

    # std/mean envelop
    plot_mean_envelop(ic_stat, variable_dict, ax=ax)
    if flag_number:
        variable_dict.update({'stats': 'mean'})
        ax = plot_number(ic_stat, variable_dict=variable_dict, ax=ax, z_delta=0.01, every=1)

    # cosmetic
    ax.xaxis.set_label_position('top')
    ax.axes.set_ylabel('Ice depth (m)')
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
