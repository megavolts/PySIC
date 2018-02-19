#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.coreset.py : CoreStack class

"""
import logging
import numpy as np
import pandas as pd
from seaice.core.profile import *

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

    def add_profile(self, profile):
        """

        :param profile:
        :return:
        """
        return CoreStack(self.append(profile))

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
        if ic_data.variables().size > 0:
            self.logger.info("Adding %s profiles for core %s" % (", ".join(ic_data.variables()), ic_data.name))
            profile = ic_data.profile
            #profile['name'] = ic_data.name
            #profile['length'] = ic_data.length[~np.isnan(ic_data.length())].mean()
            if ic_data.ice_thickness.__len__() == 1 and isinstance(ic_data.ice_thickness[0], (int, float)):
                profile['ice_thickness'] = ic_data.ice_thickness[0]
            else:
                profile['ice_thickness'] = np.nanmean(ic_data.ice_thickness)
                logging.info("ice thickness is the mean of all not-nan ice thickness")

            if ic_data.freeboard.__len__() == 1 and isinstance(ic_data.freeboard[0], (int, float)):
                profile['freeboard'] = ic_data.freeboard[0]
            else:
                profile['freeboard'] = np.nanmean(ic_data.freeboard)

            if ic_data.snow_depth.__len__() == 1 and isinstance(ic_data.snow_depth[0], (int, float)):
                profile['snow_depth'] = ic_data.snow_depth[0]
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

    def section_stat(self, groups=None, variables=None, stats=('min', 'mean', 'max', 'std')):
        """

        :param variables:
        :param stats:
        :param groups:
        :return:
        """

        return CoreStack(grouped_stat(self, groups, variables=variables, stats=stats))

    def discretize(self, y_bins=None, y_mid=None, variables=None, display_figure=False, fill_gap=False,
                   fill_extremity=False):
        """

        :param y_bins:
        :param y_mid:
        :param variables:
        :param display_figure:
        :param fill_extremity:
        :param fill_gap:
        :return:
        """
        if variables is None:
            variables = self.variable.unique().tolist()

        data_binned = pd.DataFrame()
        for core in self.name.unique():
            data_binned = data_binned.append(
                discretize_profile(self[self.name == core], y_bins=y_bins, y_mid=y_mid, variables=variables,
                                   display_figure=display_figure, fill_gap=fill_gap, fill_extremity=fill_extremity))
        data_binned.reset_index(drop=True, inplace=True)
        return CoreStack(data_binned)

    def compute_phys_prop(self, inplace=True):
        """

        :param inplace:
        :return:
        """

        if inplace is True:
            return self

    def set_vertical_reference(self, new_v_ref, h_ref = None):
        """
        :param v_ref:
        :return:
        """
        temp = CoreStack()
        for f_core in self.name.unique():
            ic_data = self[self.name == f_core]
            ic_data = set_vertical_reference(ic_data, new_v_ref=new_v_ref, h_ref=h_ref)
            temp = temp.append(ic_data)
        return CoreStack(temp)

    def core_in_collection(self, core):
        temp = self.loc[self.name == core, 'collection'].values
        col = []
        for ii in range(0, temp.__len__()):
            for c in temp[ii].split(', '):
                if c not in col:
                    col.append(c)
        return sorted(col)


# Ice core operation
def stack_cores(ics_dict):
    """"
    :param ics_dict:
        dictionnary of core
    :return ics_stack:
        panda.DataFrame()
    """
    logger = logging.getLogger(__name__)
    logger.info("Stacking ice cores:")
    ics_stack = CoreStack()
    for key in ics_dict.keys():
        ics_stack = ics_stack.add_profiles(ics_dict[key])
    return CoreStack(ics_stack)


def grouped_stat(ics_stack, groups, variables=None, stats=('min', 'mean', 'max', 'std')):
    """

    :param ics_stack:
    :param variables:
    :param groups:
    :param stats:
    :return:
    """

    logger = logging.getLogger(__name__)

    # function check
    if variables is None:
        variables = ics_stack.variable.unique().tolist()
    if not isinstance(variables, list):
        variables = [variables]
    if not isinstance(stats, list):
        stats = [stats]

    if 'weight' not in ics_stack:
        ics_stack['weight'] = 1
        logger.warning('No weight value are defined. Setting weight value to 1')
    if ics_stack['weight'].isna().any():
        ics_stack.loc[ics_stack['weight'].isna(), 'weight'] = 1
        logger.warning('some weight value are not defined. Setting weight value to 1')

    if groups is None:
        logger.error("Grouping option cannot be empty; it should contains at least vertical section y_mid")
    elif 'y_mid' not in groups:
        try:
            groups['y_mid'] = sorted(pd.concat([ics_stack.y_low, ics_stack.y_sup]).dropna().unique())
        except AttributeError:
            logger.error("y_mid not in grouping option; y_mid cannot be generated from section horizon")
        else:
            logger.info("y_mid not in grouping option; y_mid generated from section horizon")

    groups_order = list(groups.keys())

    # y_mid at the end in order to group first by argument, and then by depth
    groups_order.remove('y_mid')
    groups_order.append('y_mid')

    cuts = []
    dim = []
    for group in groups_order:
        cuts.append(pd.cut(ics_stack[group], groups[group], labels=False))
        dim.append(groups[group].__len__()-1)

    temp_all = pd.DataFrame()
    for variable in variables:
        logger.info('computing %s' % variable)

        # apply weight
        # if property weight is null, property value is set to np.nan
        _series = pd.Series(ics_stack.loc[ics_stack.variable == variable, 'weight'] *
                            ics_stack.loc[ics_stack.variable == variable, variable], index=ics_stack.loc[ics_stack.variable == variable].index)
        ics_stack.loc[ics_stack.variable == variable, '_weight_property'] = _series
        # set _weight_property to 0 if property weight is null
        ics_stack.loc[(ics_stack.variable == variable) & (ics_stack.weight == 0), '_weight_property'] = np.nan

        data_grouped = ics_stack.loc[ics_stack.variable == variable].groupby(cuts)

        for stat in stats:
            if stat in ['sum', 'mean']:
                func = "kgroups.loc[~kgroups._weight_property.isna(), '_weight_property']." + stat + "()"
            elif stat in ['min', 'max', 'std']:
                func = "kgroups.loc[~kgroups._weight_property.isna(), '" + variable + "']." + stat + "()"
            else:
                logger.error("%s operation not defined. Open a bug report" % stat)
            logger.info('\tcomputing %s' % stat)

            stat_var = np.nan * np.ones(dim)
            core_var = [None for i in range(int(np.prod(dim)))]
            for k1, kgroups in data_grouped:
                stat_var[tuple(np.array(k1, dtype=int))] = eval(func)
                core_var[int(np.prod(np.array(k1)+1)-1)] = ', '.join(list(kgroups.loc[~kgroups._weight_property.isna(),
                                                                                      'name'].unique()))
            core_var = np.reshape(core_var, dim)

            # run over ndim, minus the ice thickness
            for index in indices(dim[:-1]):
                temp = pd.DataFrame(stat_var[index], columns=[variable])
                temp = temp.join(pd.DataFrame(core_var[index], columns=['collection']))
                data = [x for x in index]+[stat, variable, ics_stack.v_ref.unique()[0]]
                columns = ['bin_'+x for x in groups_order[:-1]] + ['stats', 'variable', 'v_ref']
                rows = np.array(temp.index.tolist())
                temp = temp.join(pd.DataFrame([data], columns=columns, index=rows))

                # number of samples

                n = [int(temp.iloc[row]['collection'].split(', ').__len__()) if temp.iloc[row]['collection'] is not None else 0 for row in temp.index.tolist()]
                temp = temp.join(pd.DataFrame(n, columns=['n'], index=rows))

                columns = ['y_low', 'y_sup', 'y_mid']
                t2 = pd.DataFrame(columns=columns)

                # For step profile, like salinity
                if not ics_stack[ics_stack.variable == variable].y_low.isnull().any():
                    for row in rows:
                        data = [groups['y_mid'][row], groups['y_mid'][row + 1],
                                (groups['y_mid'][row] + groups['y_mid'][row + 1]) / 2]
                        t2 = t2.append(pd.DataFrame([data], columns=columns, index=[row]))
                # For linear profile, like temperature
                elif ics_stack[ics_stack.variable == variable].y_low.isnull().all():
                    for row in rows:
                        data = [np.nan, np.nan, (groups['y_mid'][row] + groups['y_mid'][row + 1]) / 2]
                        t2 = t2.append(pd.DataFrame([data], columns=columns, index=[row]))

                if temp_all.empty:
                    temp_all = temp.join(t2)
                else:
                    temp_all = temp_all.append(temp.join(t2), ignore_index=True)
    return CoreStack(temp_all)


# def grouped_ic(ics_stack, groups):
#     """
#
#     :param ics_stack:
#     :param groups:
#     :return:
#     """
#
#     logger = logging.getLogger(__name__)
#
#     groups_ordered = list(groups.keys())
#
#     cuts = []
#     dim = []
#     for group in groups_ordered:
#         cuts.append(pd.cut(ics_stack[group], groups[group], labels=False))
#         dim.append(groups[group].__len__()-1)
#
#     temp_all = pd.DataFrame()
#     logger.info('grouping ice core by %s' % ", ".join(groups_ordered))
#
#     data_grouped = ics_stack.groupby(cuts)
#
#     core_var = [None for i in range(int(np.prod(dim)))]
#     for k1, kgroups in data_grouped:
#         core_var[int(np.prod(np.array(k1)+1)-1)] = sorted(kgroups['name'].unique())
#     core_var = np.reshape(core_var, dim)
#
#     return CoreStack(temp_all)


def indices(dim):
    """
    :param dim:
    :return:
    """
    for d in range(dim[0]):
        if dim.__len__() == 1:
            yield (d,)
        else:
            for n in indices(dim[1:]):
                yield (d,) + n
