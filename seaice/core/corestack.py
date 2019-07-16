#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.coreset.py : CoreStack class

"""
import datetime as dt
import logging
import warnings

import numpy as np
import pandas as pd

import seaice
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

essential_property = ['y_low', 'y_mid', 'y_sup', 'name', 'collection', 'comment', 'date', 'freeboard',
                      'ice_thickness', 'length', 'snow_depth', 'v_ref', 'variable', 'weight']

# enable logging module to capture warning
logging.captureWarnings(True)

y_bins = None
y_mid = None
display_figure = False
fill_gap = False
fill_extremity = False
variables = None
verbose = False
dropemptyrow=False

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
        return CoreStack(self.append(profile, sort=False).reset_index(drop=True))

    def delete_profile(self, variable_dict):
        """

        :param variable_dict:
        :return:
        """
        return CoreStack(delete_profile(self, variable_dict))

    def add_core(self, ic_data, verbose=False):
        """
        :param ic_data:
        :return:
        """
        if len(ic_data.variables()):
            self.logger.info("Adding %s profiles for core %s" % (", ".join(ic_data.variables()), ic_data.name))
            profile = seaice.core.profile.Profile(ic_data.profile)
            # TODO: should not need those 3 if case
            if isinstance(ic_data.ice_thickness, (int, float)):
                profile['ice_thickness'] = ic_data.ice_thickness
            else:
                profile['ice_thickness'] = np.nanmean(ic_data.ice_thickness)
                logging.info("ice thickness is the mean of all not-nan ice thickness")

            if isinstance(ic_data.freeboard, (int, float)):
                profile['ice_thickness'] = ic_data.freeboard
            else:
                profile['freeboard'] = np.nanmean(ic_data.freeboard)

            if isinstance(ic_data.snow_depth, (int, float)):
                profile['snow_depth'] = ic_data.snow_depth
            else:
                profile['snow_depth'] = np.nanmean(ic_data.snow_depth)

            profile['date'] = ic_data.date
            profile['collection'] = ', '.join(ic_data.collection)
            self = self.add_profile(profile)
            if verbose and ic_data.name not in self.names():
                print(ic_data.name)
            return CoreStack(self)
        else:
            return CoreStack(self)

    def remove_profile_from_core(self, name, variables=variables):
        """

        :param name: name of the core
        :param variable: variable profile to remove
        :return:
        """
        _ic_stack = self[self.name != name]
        _ic = self[self.name == name]

        if variables is None:
            return _ic_stack
        elif not isinstance(variables, list):
            variables = [variables]

        for variable in variables:
            for vg in [vg for vg in _ic.variable_groups() if variable in vg.split(', ')]:
                if len(vg.split(', ')) == 1:
                    _ic = _ic[_ic.variable != vg]
                else:
                    # set variable to np.nan
                    _ic.loc[(_ic.variable == vg), variable] = [np.nan] * len(_ic[(_ic.variable == vg)].index)
                    # remove variable from variables
                    new_vg = vg.split(', ')
                    new_vg.remove(variable)
                    _ic.loc[(_ic.variable == vg), 'variables'] = ', '.join(new_vg)
        return pd.concat([_ic_stack, _ic], sort=False)

    def section_stat(self, groups=None, variables=None, stats=['min', 'mean', 'max', 'std'], dropemptyrow=dropemptyrow):
        """

        :param variables:
        :param stats:
        :param groups:
        :return:
        """

        return grouped_stat(self, groups=groups, variables=variables, stats=stats, dropemptyrow=dropemptyrow)

    def discretize(self, y_bins=y_bins, y_mid=y_mid, display_figure=display_figure, fill_gap=fill_gap,
                   fill_extremity=fill_extremity, variables=variables, verbose=verbose, dropemptyrow=dropemptyrow):
        """
        :param y_bins:
        :param y_mid:
        :param display_figure:
        :param fill_extremity:
        :param fill_gap:
        :return:
        """

        ics_stack = self

        if variables is not None:
            from seaice.core.profile import select_variables
            ics_stack = select_variables(ics_stack, variables)

        data_binned = pd.DataFrame()
        for core in ics_stack.names():
            if verbose:
                print(core)
            profile = ics_stack[ics_stack.name == core]
            profile_d = seaice.core.profile.discretize_profile(profile, y_bins=y_bins, y_mid=y_mid,
                                                               display_figure=display_figure, fill_gap=fill_gap,
                                                               fill_extremity=fill_extremity, dropemptyrow=dropemptyrow)

            data_binned = data_binned.append(profile_d, sort=True)
        data_binned = CoreStack(data_binned)
        data_binned = data_binned.reset_index(drop=True)
        data_binned = data_binned.clean_stack()
        return CoreStack(data_binned)

    def set_vertical_reference(self, new_v_ref, h_ref = None):
        """
        :param v_ref:
        :return:
        """
        temp = CoreStack()
        for core in self.get_name():
            profile = seaice.core.profile.Profile(self[self.name == core].astype(seaice.core.profile.Profile()))
            profile.set_vertical_reference(new_v_ref=new_v_ref, h_ref=h_ref)
            temp = temp.append(profile)
        return CoreStack(temp)

    def set_orientation(self, v_ref):
        """

        :param v_ref:
        :return:
        """

        oriented_stack = self.loc[self.v_ref == v_ref]
        unoriented_stack = self.loc[self.v_ref != v_ref]

        if not unoriented_stack.empty:
            for hi in unoriented_stack.ice_thickness.unique().astype(float):
                if np.isnan(hi):
                    subset = unoriented_stack[unoriented_stack.ice_thickness.isna()]
                    for hi in subset.length.unique():
                        _subset = subset[subset.length == hi]
                        if not np.isnan(hi):
                            oriented_stack = oriented_stack.append(
                                seaice.core.profile.set_profile_orientation(_subset, v_ref))
                            self.logger.info('NO ICE THICKNESS ' + ', '.join(_subset.names()))
                        else:
                            _subset = subset[subset.length.isna()]
                            self.logger.info('NO LENGTH, NO ICE THICKNESS ' + ', '.join(_subset.names()))
                else:
                    subset = unoriented_stack[unoriented_stack.ice_thickness == hi]
                    oriented_stack = oriented_stack.append(seaice.core.profile.set_profile_orientation(subset, v_ref))
        return CoreStack(oriented_stack)

    def core_in_collection(self, core):
        temp = self.loc[self.name == core, 'collection'].values
        col = []
        for ii in range(0, temp.__len__()):
            for c in temp[ii].split(', '):
                if c not in col:
                    col.append(c)
        return sorted(col)

    def get_variable(self):
        warnings.warn('get_variables() will be deprecated in next version, use variables() instead', FutureWarning)
        variables = []
        for var_group in self.variable.unique():
            variables += var_group.split(', ')
        return variables

    def variables(self):
        variables = []
        for var_group in self.variable.unique():
            variables += var_group.split(', ')
        return list(set(variables))

    def names(self):
        if 'name' not in self.columns:
            return []
        else:
             return self.name.unique()

    def get_name(self):
        warnings.warn('get_name() will be deprecated in next version, use names() instead', FutureWarning)
        return self.name.unique()

    def core_names(self):
        logging.FutureWarning('getting deprecated and change to get_name()')
        return self.name.unique()

    def get_core_in_collection(self):
        names = []
        if 'collection' in self:
            for col in self.collection.unique():
                names.extend(col.split(', '))
            return list(set(names))
        else:
            self.logger.warning('No collection in core stack')
            return []

    def delete_variable(self, variables2del):
        """
        :param variables2del:
        :return:
        """

        # TODO merge with profile.delete_variables
        if not isinstance(variables2del, list):
            variables = [variables2del]
        else:
            variables = variables2del

        for variable in variables:
            if variable in self.variables():
                # delete variable column
                self.drop(variable, axis=1, inplace=True)

                # delete associated subvariable column
                if variable in seaice.subvariable_dict:
                    for subvariable in seaice.subvariable_dict[variable]:
                        if subvariable in self.variables():
                            self.drop(subvariable, axis=1, inplace=True)

                # delete variable from variable
                for group in self.variable.unique():
                    new_group = group.split(', ')
                    if variable in new_group:
                        new_group.remove(variable)

                        # if the group is empty, remove the row
                        if len(new_group) == 0:
                            self.drop(self[self.variable == group].index.values, inplace=True)
                        else:
                            self.loc[self.variable == group, 'variable'] = ', '.join(new_group)

        # clean profile by removing empty column
        # removed self.clean_stack()

    def fix_dtypes(self, verbose=False):
        # add essential column if missing:
        col_essential = ['y_low', 'y_mid', 'y_sup', 'length', 'ice_thickness', 'freeboard', 'snow_depth', 'comment']
        if not 'date' in self.columns:
            col_essential += ['datetime']
        c_essential = [c for c in col_essential if c not in self.columns]
        if len(c_essential) > 0 and verbose:
            print("Missing essential columns are added: ")
            for c in c_essential:
                print("\t%s" % c)
                self[c] = None

        # check types:
        col_string = ['name', 'collection', 'variable', 'comment', 'v_ref']
        col_string += [var+'_core' for var in self.variables()]
        col_string += [var+'_collection' for var in self.variables()]

        col_date = [c for c in ['date', 'datetime']]
        col_float = ['y_low', 'y_mid', 'y_sup']
        col_float += ['length', 'ice_thickness', 'freeboard', 'snow_depth']
        col_float += self.variables()
        if len(col_float) > 0:
            col_float += ['w_' + v for v in self.variables()]
        col_float += [c for c in self.columns if c not in col_string and c not in col_date]

        c_float = [c for c in col_float if c in self.columns]
        self[c_float] = self[c_float].apply(pd.to_numeric)
        c_date = [c for c in col_date if c in self.columns]
        self[c_date] = self[c_date].apply(pd.to_datetime)
        c_string = [c for c in col_string if c in self.columns]
        self[c_string] = self[c_string].astype(str).replace({'nan': None})

        return self

    def clean_stack(self):
        """
        :return:
        """
        self = self.fix_dtypes()

        # remove all-nan variable
        for variable in self.variables():
            if self[variable].isna().all():
                self.delete_variable(variable)

        # clean profile by removing all-nan column
        col = [c for c in self.columns if c not in ['y_low', 'y_mid', 'y_sup']]
        self = pd.concat([self[['y_low', 'y_mid', 'y_sup']], self[col].dropna(axis=1, how='all')], axis=1, sort=False)

        return self

    def keep_variables(self, variables2keep):
        """

        :param variables2keep:
        :return:
        """
        if not isinstance(variables2keep, list):
            variables2keep = [variables2keep]

        # list variables to delete
        variables2del = [var for var in self.variables() if var not in variables2keep]

        # delete variables
        self.delete_variable(variables2del)

    def get_property(self):
        properties = [prop for vg in self.variable.unique() for prop in vg.split(', ')]
        return list(set(properties))

    def select_property(self, vg_property=None, extra_keys=[]):
        # TODO hard code sea ice property
        # TODO merge with profile.select_variable
        if vg_property is None:
            vg_property =self.get_property()
        elif not isinstance(vg_property, list):
            vg_property = [vg_property]

        vg_group = [vg_group for vg_group in self.variable.unique() for vg_prop in vg_group.split(', ') if vg_prop in vg_property]

        # add property weight if it was discretized
        keys = essential_property + [prop for prop in vg_property] + ['w_'+prop for prop in vg_property]

        # add extra keys if define
        keys = list(set([key for key in keys if key in self.keys()]+extra_keys))

        # select profile
        data_prop = self[self.variable.isin(vg_group)][keys]

        # change variable:
        for vg in vg_group:
            new_vg = ', '.join([prop for prop in vg_property if prop in vg])
            data_prop.loc[data_prop.variable == vg, 'variable'] = new_vg

        return data_prop

    def select_variable(self, variable_group, extra_keys=[]):
        select_data = pd.DataFrame()

        if not isinstance(variable_group, list):
            variable_group = [variable_group]

        for vg in variable_group:
            data = self[self.variable == vg]
            select_data = select_data.append(data.select_property(extra_keys=extra_keys))
        return select_data

    def delete_profile(self, variable_dict):
        return delete_profile(self, variable_dict)

    def clean(self, inplace=True):
        if not inplace:
            self.dropna(axis=1, how='all', inplace=False)
        else:
            return self.dropna(axis=1, how='all', inplace=True)

    def variable_groups(self):
        """
        """
        return self.variable.unique()

    @property
    def _constructor(self):
        return CoreStack

    pass

# Ice core operation
def stack_cores(ics_dict, verbose=False):
    """"
    :param ics_dict:
        dictionnary of core
    :return ics_stack:
        panda.DataFrame()
    """
    logger = logging.getLogger(__name__)
    logger.info("Stacking ice cores")
    ics_stack = CoreStack()
    for core in ics_dict.keys():
        if verbose:
            print(core)
        ics_stack = ics_stack.add_core(ics_dict[core], verbose=verbose)
    ics_stack.reset_index(drop=True)

    # clean the stack
    #ics_stack.clean_stack()

    return CoreStack(ics_stack)


def grouped_stat(ic_stack, groups=['y_mid'], variables=None, stats=None, dropemptyrow=dropemptyrow):
    """
    :param ics_stack:
    :param variables:
    :param groups list of string or dictionnary:
    :param stats:
    :return:
    """

    logger = logging.getLogger(__name__)

    # function check
    if variables is None:
        variables = ic_stack.get_property()
    if not isinstance(variables, list):
        variables = [variables]
    if not isinstance(stats, list):
        stats = [stats]

    for variable in variables:
        if 'w_' + variable not in ic_stack:
            ic_stack['w_' + variable] = np.ones([1, len(ic_stack.index)]).transpose()
            logger.warning('No weight value are defined for %s. Setting weight value to 1' % variable)
        if ic_stack['w_' + variable].isna().any():
            # set w_variable to 0 if variable is nan
            ic_stack.loc[ic_stack[variable].isna(), 'w_' + variable] = 0

            # set w_variable to 1 if it exist
            ic_stack.loc[ic_stack['w_' + variable].isna(), 'w_' + variable] = 1

            logger.warning('some weight value are not defined for % s. Setting weight value to 1 if temperature exists, 0 otherway' % variable)

    # Discard any row with no valid data entry
    ic_stack = ic_stack[ic_stack[['w_' + variable for variable in variables]].sum(axis=1) != 0]

    no_y_mid_flag = True
    if isinstance(groups, dict):
        if 'y_mid' in groups:
            no_y_mid_flag = False
    elif isinstance(groups, list):
        for group in groups:
            if isinstance(group, dict):
                if 'y_mid' in group:
                    no_y_mid_flag = False
            elif 'y_mid' is group:
                groups.remove('y_mid')
    if no_y_mid_flag:
        logger.info("y_mid not in grouping option; try to generate y_mid from section horizon")
        try:
            y_bins = sorted(
                [0] + [y for y in ic_stack.y_low.dropna().unique() if y in ic_stack.y_sup.dropna().unique()] + [
                    ic_stack.y_sup.max()])
            groups.append({'y_mid': y_bins})
        except AttributeError:
            logger.error("y_mid not in grouping option; y_mid cannot be generated from section horizon")
        else:
            logger.info("y_mid succesfully generated from section horizon")

    # generate the cuts for groupby function and move 'y_mid' at the end if present
    cuts = []
    cuts_dict = {}
    dim = []
    groups_order = []
    _cut_y_mid = False

    if isinstance(groups, dict):
        for key in groups:
            if key is 'y_mid':
                _cut_y_mid = pd.cut(ic_stack[key], groups[key], labels=False)
                _dim_y_mid = groups[key].__len__() - 1
                _dict_y_mid = {key: groups[key]}
            else:
                cuts.append(pd.cut(ic_stack[key], groups[key], labels=False))
                dim.append(groups[key].__len__() - 1)
                cuts_dict.update({key: groups[key]})
                groups_order.append(key)
    else:
        for group in groups:
            if isinstance(group, dict):
                for key in group:
                    if key is 'y_mid':
                        _cut_y_mid = pd.cut(ic_stack[key], group[key], labels=False)
                        _dim_y_mid = group[key].__len__() - 1
                        _dict_y_mid = {key: group[key]}
                    else:
                        cuts.append(pd.cut(ic_stack[key], group[key], labels=False))
                        dim.append(group[key].__len__() - 1)
                        cuts_dict.update({key: group[key]})
                        groups_order.append(key)
            else:
                if group is 'y_mid':
                    y_mid = sorted(ic_stack[group].unique())
                    y_mid = np.concatenate(([0], [y_mid[0] + np.diff(y_mid)[0] / 2], y_mid[1:] + np.diff(y_mid) / 2))
                    _cut_y_mid = pd.cut(ic_stack[group], y_mid, labels=False)
                    _dim_y_mid = y_mid.__len__() - 1
                    _dict_y_mid = {group: y_mid}

                else:
                    cuts.append(group)
                    _dict = {}
                    n = 0
                    for entry in ic_stack[group].unique():
                        _dict[entry] = n
                        n += 1
                    dim.append(n)
                    cuts_dict.update({group: _dict})
                    groups_order.append(group)
                    del _dict
    if _cut_y_mid.any():
        cuts.append(_cut_y_mid)
        dim.append(_dim_y_mid)
        cuts_dict.update(_dict_y_mid)
    groups_order.append('y_mid')
    del _cut_y_mid, _dim_y_mid, _dict_y_mid


    all_stat = CoreStack()
    for prop in variables:
        logger.warning('Computing statistic for %s' % prop)

        gr = [element if isinstance(element, str) else list(element.keys())[0] for element in groups]

        prop_data = ic_stack.select_property(prop, extra_keys=gr).copy()

        prop_data['wtd_'+prop] = prop_data['w_' + prop] * prop_data[prop]

        # if property weight is null, weighted property is np.nan
        prop_data.loc[prop_data['w_'+prop] == 0, 'wtd_'+prop] = np.nan

        data_grouped = prop_data.groupby(cuts)

        stat_var = {}
        core_var = np.zeros(dim).astype(str)
        for stat in list(stats):
            # use np.FUNC(...) instead of .FUNC() as panda.groupby().FUNC() return np.nan rather than 0 if there
            # is only notnull element in the group
            if stat in ['sum', 'mean']:
                func = "np." + stat + "(kgroups.loc[~kgroups['wtd_" + prop + "'].isna(), 'wtd_" + prop + "' ])"
                w_func = "kgroups.loc[~kgroups['w_" + prop + "'].isna(), 'w_" + prop + "'].sum()"
                n_func = "kgroups.loc[~kgroups['wtd_" + prop + "'].isna(), 'wtd_" + prop + "'].count()"
            elif stat in ['min', 'max', 'std']:
                func = "np." + stat + "(kgroups.loc[~kgroups['wtd_" + prop + "'].isna(), '" + prop + "'])"
            else:
                logger.error("%s operation not defined. Open a bug report" % stat)
            logger.info('\tcomputing %s' % stat)

            stat_var[stat] = np.nan * np.ones(dim)
            core_var = np.zeros(dim).astype(str)
            for k1, kgroups in data_grouped:
                if isinstance(k1, (int, float)):
                    k1 = [k1]
                try:
                    stat_var[stat][tuple(np.array(k1, dtype=int))] = eval(func)
                    new_k = k1
                except Exception:
                    new_k = []
                    _k_n = 0
                    for k in k1:
                        if isinstance(k, np.integer):
                            new_k.append(k)
                        elif isinstance(k, dt.datetime):
                            new_k.append(cuts_dict[groups_order[_k_n]][np.datetime64(k, 'ns')])
                        elif isinstance(k, float):
                            new_k.append(int(k))
                        else:
                            new_k.append(cuts_dict[groups_order[_k_n]][k])
                        _k_n += 1

                if stat in ['sum', 'mean']:
                    # Take in account property measured only on a partial bins to computed weighted property
                    # e.g. S measure on 2 samples
                    # # 1 : 0-0.1, S = 10, w=1
                    # # 2 : 0-0.1, S = 8, w=0.5
                    # weighted mean : 0-0.1 = (10*1+8*0.5)/1.5*2
                    wtd_stat = eval(func)
                    w = eval(w_func)
                    n = eval(n_func)
                    stat_var[stat][tuple(np.array(new_k, dtype=int))] = wtd_stat * n / w
                else:
                    stat_var[stat][tuple(np.array(new_k, dtype=int))] = eval(func)
                # #
                # print(k1, groups)
                # print('\t %s' % ', '.join(list(kgroups.loc[~kgroups['wtd_' + prop].isna(), 'name'].unique())))
                # print('\t %s %s' %(new_k, int(np.prod(np.array(new_k) + 1) - 1) ))

                k1_int = []
                k1_int = tuple([int(k) for k in k1])

                core_var[k1_int] = ', '.join(list(kgroups.loc[~kgroups['wtd_' + prop].isna(), 'name'].unique()))

        core_stat = CoreStack()
        # run over ndim, minus the ice thickness
        if len(dim) == 1:
            headers = ['y_low', 'y_mid', 'y_sup']
            stats_data = (np.array(cuts_dict['y_mid'][:-1]) + np.array(cuts_dict['y_mid'][1:])) / 2

            # for continuous profile
            if prop_data['y_low'].notna().all():
                stats_data = np.vstack(
                    [np.array(cuts_dict['y_mid'][:-1]), stats_data, np.array(cuts_dict['y_mid'][1:])])
            # for discontinous profile:
            else:
                stats_data = np.vstack([[np.nan] * stats_data.__len__(), stats_data, [np.nan] * stats_data.__len__()])

            # stat data by prop
            headers.extend([prop + '_' + stat for stat in stats + ['collection']])
            stats_data = np.vstack([stats_data, [stat_var[stat] for stat in stats] + [core_var]])

            # assemble dataframe
            df = CoreStack(np.array(stats_data).transpose(), columns=headers)

            # number of sample
            df[prop + '_count'] = df[prop + '_collection'].apply(
                lambda x: x.split(', ').__len__() if x not in [None, ''] else 0)

            # define bins
            key_merge = ['y_low', 'y_mid', 'y_sup', 'v_ref', 'name']
            name = []

            n_index = 0
            if not groups_order[n_index] in 'y_mid':
                if groups_order[n_index] in cuts_dict:
                    df[groups_order[n_index]] = cuts_dict[groups_order[n_index]][index[n_index]]
                    # df[groups_order[n_index]] = inverse_dict(cuts_dict[groups_order[n_index]])[index[n_index]][0]
                    key_merge.append(groups_order[n_index])
                    _name = cuts_dict[groups_order[n_index]][index[n_index]]
                    # _name = inverse_dict(cuts_dict[groups_order[n_index]])[index[n_index]][0]
                    if isinstance(_name, str):
                        name.append(_name)
                    elif isinstance(_name, np.datetime64):
                        name.append(pd.to_datetime(np.datetime64(_name)).strftime('%Y%m%d'))
                    elif isinstance(_name, float):
                        name.append(str(_name))
                else:
                    df['bin_' + groups_order[n_index]] = index[n_index]
                    key_merge.append('bin_' + groups_order[n_index])

            # v_ref, variable
            df['v_ref'] = ic_stack.v_ref.unique()[0]
            df['name'] = '-'.join(name)
            df['variable'] = prop
            # assemble with existing core stat:
            if core_stat.empty:
                core_stat = CoreStack(df)
            else:
                core_stat = core_stat.append(df)

            core_stat = core_stat.apply(pd.to_numeric, errors='ignore')
            if 'date' in core_stat.keys():
                core_stat['date'] = pd.to_datetime(core_stat['date'])
        else:
            for index in indices(dim[:-1]):
                headers = ['y_low', 'y_mid', 'y_sup']
                stats_data = (np.array(cuts_dict['y_mid'][:-1]) + np.array(cuts_dict['y_mid'][1:])) / 2

                # for continuous profile
                if prop_data['y_low'].notna().all():
                    stats_data = np.vstack(
                        [np.array(cuts_dict['y_mid'][:-1]), stats_data, np.array(cuts_dict['y_mid'][1:])])
                # for discontinous profile:
                else:
                    stats_data = np.vstack(
                        [[np.nan] * stats_data.__len__(), stats_data, [np.nan] * stats_data.__len__()])

                # stat data by prop
                headers.extend([prop + '_' + stat for stat in stats + ['collection']])
                core_name = [None if c in ['0.0', ''] else c for c in core_var[index].tolist()]
                stats_data = np.vstack([stats_data, [stat_var[stat][index] for stat in stats] + [core_name]])
                # assemble dataframe
                df = CoreStack(np.array(stats_data).transpose(), columns=headers)

                # number of sample
                df[prop + '_count'] = df[prop + '_collection'].apply(
                    lambda x: x.split(', ').__len__() if x not in [None, ''] else 0)

                # define bins
                key_merge = ['y_low', 'y_mid', 'y_sup', 'v_ref', 'name']
                name = []
                for n_index in range(0, index.__len__()):
                    if groups_order[n_index] in cuts_dict:
                        df[groups_order[n_index]] = cuts_dict[groups_order[n_index]][index[n_index]]
                        key_merge.append(groups_order[n_index])
                        _name = cuts_dict[groups_order[n_index]][index[n_index]]
                        if isinstance(_name, str):
                            name.append(_name)
                        elif isinstance(_name, np.datetime64):
                            name.append(pd.to_datetime(np.datetime64(_name)).strftime('%Y%m%d'))
                        elif isinstance(_name, (float, int)):
                            name.append(str(_name))
                    else:
                        df['bin_' + groups_order[n_index]] = index[n_index]
                        key_merge.append('bin_' + groups_order[n_index])
                # v_ref, variable
                df['v_ref'] = ic_stack.v_ref.unique()[0]
                df['name'] = '-'.join(name)
                df['variable'] = prop

                # assemble with existing core stat:
                if core_stat.empty:
                    core_stat = CoreStack(df)
                else:
                    core_stat = core_stat.append(df)

                core_stat = core_stat.apply(pd.to_numeric, errors='ignore')
                if 'date' in core_stat.keys():
                    core_stat['date'] = pd.to_datetime(core_stat['date'])

        if all_stat.empty:
            all_stat = core_stat
        else:
            props = all_stat.get_property() + [prop]
            core_stat['variable'] = ', '.join(props)
            for key in key_merge:
                if all_stat[key].isna().all():
                    all_stat = all_stat.drop(columns=key, axis=1)
                if core_stat[key].isna().all():
                    core_stat = core_stat.drop(columns=key, axis=1)
            key_merge2 = [key for key in key_merge if
                          key in core_stat.columns and core_stat[key].notnull().any() and key in all_stat.columns]
            # key_2del = [key for key in key_merge if key not in key_merge2]
            # for key in key_2del:
            #    if key in core_stat.columns:
            #        core_stat = core_stat.drop(key_2del, axis=1)

            all_stat = all_stat.merge(core_stat, how='outer', on=key_merge2, sort=False)
            # update variable:
            variable_to_update = [[var if val is True else None for val in all_stat[var + '_mean'].notnull()] for var in
                                  props]
            all_stat['variable'] = [', '.join(filter(None, list)) for list in zip(*variable_to_update)]
            # all_stat[all_stat.variable_y.isna()] = all_stat[all_stat.variable_x.isna()]
            # all_stat = all_stat.rename(columns={'variable_y': 'variable'})
            all_stat = all_stat.drop(labels=['variable_x'], axis=1)
            all_stat = all_stat.drop(labels=['variable_y'], axis=1)
        if dropemptyrow:
            all_stat = all_stat[all_stat['variable'] != '']
        else:
            all_stat['variable'] = ', '.join(variables)
    return CoreStack(all_stat)


def grouped_ic(ics_stack, groups):
    """

    :param ics_stack:
    :param groups:
    :return:
    """

    logger = logging.getLogger(__name__)

    cuts = []
    cuts_dict = []
    dim = []
    groups_order = []
    _cut_y_mid = False
    for group in groups:
        if isinstance(group, dict):
            for key in group:
                if key is 'y_mid':
                    _cut_y_mid = pd.cut(ics_stack[key], group[key], labels=False)
                    _dim_y_mid = group[key].__len__() - 1
                    _dict_y_mid = {key:group[key]}
                else:
                    cuts.append(pd.cut(ics_stack[key], group[key], labels=False))
                    dim.append(group[key].__len__() - 1)
                    cuts_dict.append(None)
                    groups_order.append(key)
        else:
            cuts.append(group)
            _dict = {}
            n = 0
            for entry in ics_stack[group].unique():
                _dict[entry] = n
                n += 1
            dim.append(n)
            cuts_dict.append(_dict)
            groups_order.append(group)
    if _cut_y_mid.any():
        cuts.append(_cut_y_mid)
        dim.append(_dim_y_mid)
        cuts_dict.append(_dict_y_mid)
        groups_order.append('y_mid')
    del _cut_y_mid, _dim_y_mid, _dict_y_mid, _dict

    logger.info('grouping ice core by %s' % ", ".join(groups_order))

    data_grouped = ics_stack.groupby(cuts)

    core_var = [None for _ in range(int(np.prod(dim)))]
    for k1, kgroups in data_grouped:
        try:
            core_var[int(np.prod(np.array(k1, dtype=int) + 1) - 1)] = sorted(kgroups['name'].unique())
        except ValueError:
            new_k = []
            _k_n = 0
            for k in k1:
                if isinstance(k, np.integer):
                    new_k.append(k)
                else:
                    new_k.append(cuts_dict[_k_n][k])
                _k_n += 1
            core_var[int(np.prod(np.array(new_k, dtype=int) + 1) - 1)] = sorted(kgroups['name'].unique())

    core_var = np.reshape(core_var, dim)

    return core_var


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


def inverse_dict(map):
    """
    return the inverse of a dictionnary with non-unique values
    :param map: dictionnary
    :return inv_map: dictionnary
    """
    revdict = {}
    for k, v in map.items():
        revdict.setdefault(v, []).append(k)

    return revdict


