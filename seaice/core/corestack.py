#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.coreset.py : CoreStack class

"""
import logging
import numpy as np
import pandas as pd
from seaice.core.tool import discretize_profile

TOL = 1e-6

__name__ = "corestack"
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/09/13"
__comment__ = "corestack.py contained classes to handle ice core data"
__CoreVersion__ = 1.1

__all__ = ["CoreStack", "stack_cores"]
module_logger = logging.getLogger(__name__)
TOL = 1e-6

class CoreStack(pd.DataFrame):
    """
    CoreStack
    """

    def __getstate__(self):
        d = self.__dict__.copy()
        if 'logger' in d.keys():
            d['logger'] = d['logger'].name
        return d

    def __setstate__(self, d):
        if 'logger' in d.keys():
            d['logger'] = logging.getLogger(d['logger'])
        self.__dict__.update(d)

    def __init__(self, *args, **kwargs):
        super(CoreStack, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.info('creating an instance of CoreStack')

    def add_profile(self, profile):
        """

        :param profile:
        :return:
        """
        self = self.append(profile)
        return CoreStack(self)

    def delete_profile(self, variable_dict):
        """

        :param variable_dict:
        :return:
        """
        return CoreStack(delete_profile(self, variable_dict))

    def add_profiles(self, ic_data):
        """
        :param ic_data:
        :return:
        """
        if ic_data.variables is not None:
            self.logger.info("Adding %s profiles for core %s" % (", ".join(ic_data.variables), ic_data.name))
            print(ic_data.name)
            profile = ic_data.profile
            profile['name'] = ic_data.name
            profile['length'] = ic_data.length[~np.isnan(ic_data.length)].mean()
            if isinstance(ic_data.ice_thickness, (int, float)):
                profile['ice_thickness'] = ic_data.ice_thickness
            else:
                profile['ice_thickness'] = ic_data.ice_thickness[~np.isnan(ic_data.ice_thickness)].mean()

            if isinstance(ic_data.freeboard, (int, float)):
                profile['freeboard'] = ic_data.freeboard
            else:
                profile['freeboard'] = np.nanmean(ic_data.freeboard)

            if isinstance(ic_data.snow_depth, (int, float)):
                profile['snow_depth'] = ic_data.snow_depth
            else:
                profile['snow_depth'] = np.nanmean(ic_data.snow_depth)

            profile['date'] = ic_data.date
            profile['collection'] = ', '.join(ic_data.collection)
            temp = self.append(profile).reset_index(drop=True)
            return CoreStack(temp)
        else:
            return CoreStack(self)

    def remove_profile_from_core(self, core, variable=None):
        """

        :param core:
        :param variable:
        :return:
        """
        temp = ""
        if variable is None:
            temp = self[self.name != core]
        elif isinstance(variable, list):
            for ii_variable in core:
                temp = self[(self.name != core) & (self.variable != ii_variable)]
        else:
            temp = self[(self.name != core) & (self.variable != variable)]
        return CoreStack(temp)

    def grouped_stat(self, variables, stats, bins_DD, bins_y, comment='n'):
        """

        :param variables:
        :param stats:
        :param bins_DD:
        :param bins_y:
        :param comment:
        :return:
        """
        y_cuts = pd.cut(self.y_mid, bins_y, labels=False)
        t_cuts = pd.cut(self.DD, bins_DD, labels=False)

        if not isinstance(variables, list):
            variables = [variables]
        if not isinstance(stats, list):
            stats = [stats]

        temp_all = pd.DataFrame()
        for ii_variable in variables:
            if comment == 'y':
                print('\ncomputing %s' % ii_variable)
            data = self[self.variable == ii_variable]
            data_grouped = data.groupby([t_cuts, y_cuts])

            for ii_stat in stats:
                if comment == 'y':
                    print('computing %s' % ii_stat)
                func = "groups['" + ii_variable + "']." + ii_stat + "()"
                stat_var = np.nan * np.ones((bins_DD.__len__() - 1, bins_y.__len__()))
                core_var = [[[None] for x in range(bins_y.__len__())] for y in range(bins_DD.__len__() - 1)]
                for k1, groups in data_grouped:
                    stat_var[int(k1[0]), int(k1[1])] = eval(func)
                    core_var[int(k1[0])][int(k1[1])] = [list(groups.dropna(subset=[ii_variable])
                                                             ['core_name'].unique())]
                for ii_bin in range(stat_var.__len__()):
                    temp = pd.DataFrame(stat_var[ii_bin], columns=[ii_variable])
                    temp = temp.join(pd.DataFrame(core_var[ii_bin], columns=['core_collection']))
                    DD_label = 'DD-' + str(bins_DD[ii_bin]) + '_' + str(bins_DD[ii_bin + 1])
                    data = [str(bins_DD[ii_bin]), str(bins_DD[ii_bin + 1]), DD_label, int(ii_bin), ii_stat,
                            ii_variable, self.v_ref.unique()[0]]
                    columns = ['DD_min', 'DD_max', 'DD_label', 'DD_index', 'stats', 'variable', 'v_ref']
                    index = np.array(temp.index.tolist())  # [~np.isnan(temp[ii_variable].tolist())]
                    temp = temp.join(pd.DataFrame([data], columns=columns, index=index))
                    temp = temp.join(pd.DataFrame(index, columns=['y_index'], index=index))
                    for row in temp.index.tolist():
                        print('test')
                        temp.loc[temp.index == row, 'n'] = temp.loc[temp.index == row, 'core collection'].__len__()
                    columns = ['y_low', 'y_sup', 'y_mid']
                    t2 = pd.DataFrame(columns=columns)
                    # For step profile, like salinity
                    # if ii_variable in ['salinity']:
                    if not self[self.variable == ii_variable].y_low.isnull().any():
                        for ii_layer in index[:-1]:
                            data = [bins_y[ii_layer], bins_y[ii_layer + 1],
                                    (bins_y[ii_layer] + bins_y[ii_layer + 1]) / 2, DD_label + str('-%03d' % ii_layer)]
                            t2 = t2.append(pd.DataFrame([data], columns=columns, index=[ii_layer]))
                    # For linear profile, like temperature
                    # if ii_variable in ['temperature']:
                    elif self[self.variable == ii_variable].y_low.isnull().all():
                        for ii_layer in index[:-1]:
                            data = [np.nan, np.nan, (bins_y[ii_layer] + bins_y[ii_layer + 1]) / 2,
                                    DD_label + str('-%03d' % ii_layer)]
                            t2 = t2.append(pd.DataFrame([data], columns=columns, index=[ii_layer]))

                    if temp_all.empty:
                        temp_all = temp.join(t2)
                    else:
                        temp_all = temp_all.append(temp.join(t2), ignore_index=True)

        data_grouped = self.groupby([t_cuts, self['variable']])

        grouped_dict = {}
        for var in variables:
            grouped_dict[var] = [[] for ii_DD in range(bins_DD.__len__() - 1)]

        for k1, groups in data_grouped:
            if k1[1] in variables:
                grouped_dict[k1[1]][int(k1[0])] = groups['core'].unique().tolist()

        return CoreStack(temp_all.reset_index(drop=True)), grouped_dict

    def discretize(self, y_bins=None, y_mid=None, variables=None, display_figure='n'):
        """

        :param y_bins:
        :param y_mid:
        :param variables:
        :param display_figure:
        :return:
        """
        if variables is None:
            variables = self.variable.unique().tolist()

        data_binned = pd.DataFrame()
        for core in self.name.unique():
            data_binned = data_binned.append(
                discretize_profile(self[self.name == core], y_bins=y_bins, y_mid=y_mid, variables=variables,
                                   display_figure=display_figure))
        return CoreStack(data_binned)

    def compute_phys_prop(self, inplace=True):
        """

        :param inplace:
        :return:
        """

        if inplace is True:
            return self

    def set_reference(self, v_ref):
        """
        :param v_ref:
        :return:
        """
        temp = CoreStack()
        for f_core in self.name.unique():
            ic_data = self[self.name == f_core]
            ic_data = set_profile_orientation(ic_data, v_ref=v_ref)
            temp = temp.append(ic_data)
        return CoreStack(temp)

    # def plot_core(self, core_dict, ax=None, param_dict=None):
    #     for ii_core in core_dict:
    #         ic_data = self.select_profile(core_dict)[0]
    #         ax = plot_profile(ic_data, core_dict['variable'], ax=ax, param_dict=param_dict)
    #     return ax
    #
    # def plot_core_profile(self, core, ax=None, variable=None, param_dict=None):
    #     """
    #     :param core:
    #     :param ax:
    #     :param variable:
    #     :param param_dict:
    #     :return:
    #     """
    #     ic_data = self.select_profile({'variable': variable, 'core_name':core})[0].reset_index()
    #     if ic_data[ic_data.variable == variable].__len__() != 0:
    #         ax = plot_profile(ic_data, variable, ax = ax, param_dict=param_dict)
    #     ax.axes.set_xlabel(variable + ' ' + si_prop_unit[variable])
    #     ax.axes.set_ylim(max(ax.get_ylim()), 0)
    #     return ax
    #
    # def plot_stat_mean(self, ax, variable, bin_index):
    #     x_mean = self.select_profile({'stats': 'mean', 'variable': variable, 'DD_index': bin_index})[0].reset_index()
    #     x_max = self.select_profile({'stats': 'max', 'variable': variable, 'DD_index': bin_index})[0].reset_index()
    #     x_min  = self.select_profile({'stats': 'min', 'variable': variable, 'DD_index': bin_index})[0].reset_index()
    #     x_std = self.select_profile({'stats': 'std', 'variable': variable, 'DD_index': bin_index})[0].reset_index()
    #
    #     if x_mean[variable].__len__() !=0:
    #         plot_profile(x_max, variable, ax=ax, param_dict={'linewidth': 3, 'color': 'r', 'label': 'min'})
    #         plot_profile(x_min, variable, ax=ax, param_dict={'linewidth': 3, 'color': 'b', 'label': 'max'})
    #         plot_profile(x_mean, variable, ax=ax,  param_dict={'linewidth': 3, 'color': 'k', 'label': 'mean'})
    #
    #         if x_std.__len__() < x_mean.__len__():
    #             index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
    #             x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))
    #
    #         if variable in ['salinity']:
    #             y_low = x_mean['y_low']
    #             y_sup = x_mean['y_sup']
    #             x_std_l = x_mean[variable][0] - x_std[variable][0]
    #             x_std_h = x_mean[variable][0] + x_std[variable][0]
    #             y_std = y_low[0]
    #             for ii in range(1, len(x_mean)):
    #                 x_std_l = np.append(x_std_l, x_mean[variable][ii - 1] - x_std[variable][ii - 1])
    #                 x_std_l = np.append(x_std_l, x_mean[variable][ii] - x_std[variable][ii])
    #                 x_std_h = np.append(x_std_h, x_mean[variable][ii - 1] + x_std[variable][ii - 1])
    #                 x_std_h = np.append(x_std_h, x_mean[variable][ii] + x_std[variable][ii])
    #                 y_std = np.append(y_std, y_low[ii])
    #                 y_std = np.append(y_std, y_low[ii])
    #             if len(x_mean) == 1:
    #                 ii = 0
    #             x_std_l = np.append(x_std_l, x_mean[variable][ii] - x_std[variable][ii])
    #             x_std_h = np.append(x_std_h, x_mean[variable][ii] + x_std[variable][ii])
    #             y_std = np.append(y_std, y_sup[ii])
    #         elif variable in ['temperature']:
    #             y_std = x_mean['y_mid']
    #             x_std_l = []
    #             x_std_h = []
    #             for ii in range(0, len(x_mean)):
    #                 x_std_l = np.append(x_std_l, x_mean[variable][ii] - x_std[variable][ii])
    #                 x_std_h = np.append(x_std_h, x_mean[variable][ii] + x_std[variable][ii])
    #         ax = plt.fill_betweenx(y_std, x_std_l, x_std_h, facecolor='black', alpha=0.3,
    #                                label=str(r"$\pm$"+"std dev"))
    #         ax.axes.set_xlabel(variable + ' ' + si_prop_unit[variable])
    #         ax.axes.set_ylim([max(ax.axes.get_ylim()), min(ax.axes.get_ylim())])
    #     return ax
    #
    # def plot_stat_median(self, ax, variable, bin_index):
    #     x_mean = self.select_profile({'stats': 'median', 'variable': variable,
    #                                   'DD_index': bin_index})[0].reset_index()
    #     x_max = self.select_profile({'stats': 'max', 'variable': variable, 'DD_index': bin_index})[0].reset_index()
    #     x_min = self.select_profile({'stats': 'min', 'variable': variable, 'DD_index': bin_index})[0].reset_index()
    #     x_std = self.select_profile({'stats': 'mad', 'variable': variable, 'DD_index': bin_index})[0].reset_index()
    #
    #     if x_mean[variable].__len__() != 0:
    #         plot_profile(x_max, variable, ax=ax, param_dict={'linewidth': 3, 'color': 'r', 'label':'min'})
    #         plot_profile(x_min, variable, ax=ax, param_dict={'linewidth': 3, 'color': 'b', 'label':'max'})
    #         plot_profile(x_mean, variable, ax=ax,  param_dict={'linewidth': 3, 'color': 'k', 'label':'median'})
    #
    #         if x_std.__len__() < x_mean.__len__():
    #             index = [ii for ii in x_mean.index.tolist() if ii not in x_std.index.tolist()]
    #             x_std = x_std.append(pd.DataFrame(np.nan, columns=x_std.columns.tolist(), index=index))
    #
    #         if variable in ['salinity']:
    #             y_low = x_mean['y_low']
    #             y_sup = x_mean['y_sup']
    #             x_std_l = x_mean[variable][0] - x_std[variable][0]
    #             x_std_h = x_mean[variable][0] + x_std[variable][0]
    #             y_std = y_low[0]
    #             for ii in range(1, len(x_mean)):
    #                 x_std_l = np.append(x_std_l, x_mean[variable][ii - 1] - x_std[variable][ii - 1])
    #                 x_std_l = np.append(x_std_l, x_mean[variable][ii] - x_std[variable][ii])
    #                 x_std_h = np.append(x_std_h, x_mean[variable][ii - 1] + x_std[variable][ii - 1])
    #                 x_std_h = np.append(x_std_h, x_mean[variable][ii] + x_std[variable][ii])
    #                 y_std = np.append(y_std, y_low[ii])
    #                 y_std = np.append(y_std, y_low[ii])
    #             if len(x_mean) == 1:
    #                 ii = 0
    #             x_std_l = np.append(x_std_l, x_mean[variable][ii] - x_std[variable][ii])
    #             x_std_h = np.append(x_std_h, x_mean[variable][ii] + x_std[variable][ii])
    #             y_std = np.append(y_std, y_sup[ii])
    #         elif variable in ['temperature']:
    #             y_std = x_mean['y_mid']
    #             x_std_l = []
    #             x_std_h = []
    #             for ii in range(0, len(x_mean)):
    #                 x_std_l = np.append(x_std_l, x_mean[variable][ii] - x_std[variable][ii])
    #                 x_std_h = np.append(x_std_h, x_mean[variable][ii] + x_std[variable][ii])
    #         ax = plt.fill_betweenx(y_std, x_std_l, x_std_h, facecolor='black', alpha=0.1,
    #                                         label=str(r"$\pm$"+"mad"))
    #         ax.axes.set_xlabel(variable + ' ' + si_prop_unit[variable])
    #         ax.axes.set_ylabel('ice thickness [m]')
    #         ax.axes.set_ylim([max(ax.axes.get_ylim()), min(ax.axes.get_ylim())])
    #     return ax
    #
    # def core_set(self):
    #     return list(set(seaice.toolbox.flatten_list(self.core_collection.tolist())))
    #
    # def compute_physical_property(self, si_prop, s_profile_shape='linear', comment='n'):
    #     # look for all core belonging to a coring event:
    #     temp_core_processed = []
    #     ic_prop = seaice.core.CoreStack()
    #     for f_core in sorted(self.core_name.unique()):
    #         ic = self[self.core_name == f_core]
    #         ic_data = seaice.core.CoreStack()
    #         if comment == 'y':
    #             print('\n')
    #         if f_core not in temp_core_processed:
    #             for ff_core in list(set(seaice.toolbox.flatten_list(ic.core_collection.tolist()))):
    #                 if comment == 'y':
    #                     print(ff_core)
    #                 ic_data = ic_data.add_profiles(self[self.core_name == ff_core])
    #             ic_prop = ic_prop.append(seaice.core.calc_prop(ic_data, si_prop, s_profile_shape=s_profile_shape))
    #             temp_core_processed.append(ff_core)
    #
    #     ics_stack = seaice.core.CoreStack(self)
    #     ic_prop = seaice.core.CoreStack(ic_prop)
    #
    #     ics_stack = ics_stack.add_profiles(ic_prop)
    #     return CoreStack(ics_stack)


def set_profile_orientation(profile, v_ref, hi=None, comment=False):
    """

    :param profile:
    :param v_ref:
    :param hi:
    :param comment:
    :return:
    """
    profile = CoreStack(profile)
    for variable in profile.variable.unique():
        data = CoreStack(profile[profile.variable == variable])
        # look for ice thickness:
        if hi is None:
            if not np.isnan(profile.ice_thickness.astype(float)).all():
                hi = profile.ice_thickness.astype(float).dropna().unique()
            elif not np.isnan(profile.length.astype(float)).all():
                hi = profile.length.astype(float).dropna().unique()
            else:
                module_logger.warning(
                    "%s ice core length and ice thickness not available for the profile" % profile.name.unique())
                return CoreStack()
        if comment is True:
            print(profile.name.unique()[0], variable, hi)
        if data.v_ref.unique().__len__() > 1:
            module_logger.error("vertical reference for profile are not consistent")
            return CoreStack()
        elif not data.v_ref.unique()[0] == v_ref:
            data['y_low'] = hi - data['y_low']
            data['y_mid'] = hi - data['y_mid']
            data['y_sup'] = hi - data['y_sup']
            data['v_ref'] = v_ref
        profile = profile.delete_profile({'name': profile.name.unique()[0], 'variable': variable})
        profile = profile.append(data)
    return CoreStack(profile)


def select_profile(ics_stack, variable_dict):
    """

    :param ics_stack:
    :param variable_dict:
    :return:
    """
    str_select = '('
    ii_var = []
    ii = 0
    for ii_key in variable_dict.keys():
        if ii_key in ics_stack.columns.values:
            ii_var.append(variable_dict[ii_key])
            str_select = str_select + 'ics_stack.' + ii_key + '==ii_var[' + str('%d' % ii) + ']) & ('
            ii += 1
    str_select = str_select[:-4]
    return CoreStack(ics_stack.loc[eval(str_select)])


def delete_profile(ics_stack, variable_dict):
    """

    :param ics_stack:
    :param variable_dict:
    :return:
    """
    str_select = '('
    ii_var = []
    ii = 0
    for ii_key in variable_dict.keys():
        if ii_key in ics_stack.columns.values:
            ii_var.append(variable_dict[ii_key])
            str_select = str_select + 'ics_stack.' + ii_key + '!=ii_var[' + str('%d' % ii) + ']) | ('
            ii += 1
    str_select = str_select[:-4]
    return CoreStack(ics_stack.loc[eval(str_select)])


# Ice core operation
def stack_cores(ics_dict):
    """"
    :param ics_dict:
        dictionnary of core
    :return ics_stack:
        panda.DataFrame()
    """
    ics_stack = CoreStack()
    for key in ics_dict.keys():
        ics_stack = ics_stack.add_profiles(ics_dict[key])
    return CoreStack(ics_stack)
