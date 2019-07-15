# ! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.profile.py : toolbox to work on property profile

"""
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import seaice

__name__ = "profile"
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/09/13"
__comment__ = "profile.py contained function to handle property profile"
__CoreVersion__ = 1.1

__all__ = ["Profile", "discretize_profile", "select_profile", "delete_profile", "uniformize_section"]

TOL = 1e-6
subvariable_dict = {'conductivity': ['conductivity measurement temperature']}
continuous_variable_list = ['temperature']
DEBUG = False


fill_gap = False
y_mid = None
fill_extremity=False
save_fig = False

essential_property = ['y_low', 'y_mid', 'y_sup', 'name', 'collection', 'comment', 'date', 'freeboard',
                      'ice_thickness', 'length', 'snow_depth', 'v_ref', 'variable', 'weight']

class Profile(pd.DataFrame):
    """

    """
    def __getstate__(self):
        d = self.__dict__.copy()
        if 'logger' in d.keys():
            d['logger'] = d['logger'].name
        return d

    def __setstate__(self, d):
        if 'logger' in d.keys():
            d['logger'] = logging.getLogger(d['logger'])

    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def get_property(self):
        """
        Return physical properties stored in the profiles

        :return: str, list
            List of property or None if there is no property stored in the profile
        """

        return self.properties()

    def properties(self):
        """

        :return:
        """
        if 'variable' not in self.keys():
            return None
        else:
            property = []
            for var_group in self.variable.unique():
                property += list(filter(None, var_group.split(', ')))
            return list(set(property))


    def get_name(self):
        """
        Return the core name of the profile

        :return name: string
        """
        self.logger = logging.getLogger(__name__)
        name = self.name.unique()
        if name.__len__() > 1:
            self.logger.warning(' %s more than one name in the profile: %s ' % (name[0], ', '.join(name)))
        return self.name.unique()[0]

    def clean(self, inplace=True):
        """
        Clean profile by removing all empty property
        :return:
        """
        self.logger = logging.getLogger(__name__)

        variable = self.get_property()
        null_property = self.columns[self.isnull().all(axis=0)].tolist()
        kept_property = [prop for prop in variable if prop not in null_property]

        if null_property:
            self.logger.info('Property are empty, deleting: %s' % ', '.join(null_property))
            if kept_property:
                self['variable'] = None
            else:
                self['variable'] = ', '.join(kept_property)

        if inplace:
            self.dropna(axis=1, how='all', inplace=True)
        else:
            return self.dropna(axis=1, how='all')

    def add_profile(self, profile):
        """
        Add new profile to existing profile.
        Profile name should match.
        :param profile: seaice.Profile()
        """
        if profile.get_name() is self.get_name() or profile.get_name() == self.get_name():
            var_merge = [var for var in profile.columns if var in self.columns]
            if 'comment' in var_merge:
                var_merge.remove('comment')
                f_comment = True
            else:
                f_comment = False
            if 'variable' in var_merge:
                var_merge.remove('variable')
                f_variable = True
            else:
                f_variable = False

            self = self.merge(profile, how='outer', sort=False, on=var_merge).reset_index(drop=True)

            if f_variable:
                self['variable'] = self[['variable_x', 'variable_y']].apply(lambda x: '{}, {}'.format(x[0], x[1]), axis=1)
                self['variable'] = self['variable'].apply(lambda x: ', '.join(filter(lambda y: y not in [None, 'nan'], x.split(', '))))
                self.drop(['variable_x', 'variable_y'], axis=1, inplace=True)
            if f_comment:
                self['comment'] = self[['comment_x', 'comment_y']].apply(lambda x: '{}, {}'.format(x[0], x[1]), axis=1)
                self['comment'] = self['comment'].apply(lambda x: ', '.join(filter(lambda y: y not in [None, 'nan'], x.split(', '))))
                self.drop(['comment_x', 'comment_y'], axis=1, inplace=True)

            return self
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.warning('Profile name does not match %s, %s' % ( profile.get_name(), self.get_name()))

    def delete_property(self, property):
        """
        Remove property

        :param property:
        :return:
        """
        if not isinstance(property, list):
            property = [property]

        new_property = self.get_property()
        for prop in property:
            if prop in self.get_property():
                self.drop(prop, axis=1, inplace=True)
                new_property.remove(prop)

                if prop in subvariable_dict.keys():
                    for _subprop in subvariable_dict[prop]:
                        if _subprop in self.columns:
                            self.drop(_subprop, axis=1, inplace=True)

         # write variable
        self['variable'] = ', '.join(new_property)

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


    def discretize(self, y_bins=None, y_mid=None, display_figure=False, fill_gap=False, fill_extremity=False):
        logger.error('Method not implemented yet')
        return 'nothing'

    def set_vertical_reference(profile, h_ref=None, new_v_ref=None, inplace=True):
        """

        :param profile:
        :param h_ref:
        :param new_v_ref: default, same as profile origin
        :return:
        """
        logger = logging.getLogger(__name__)
        if new_v_ref is None:
            if profile.v_ref.unique().__len__() > 1:
                logger.error("vertical reference for profile are not consistent")
            else:
                new_v_ref = profile.v_ref.unique()[0]

        if inplace:
            new_profile = set_profile_orientation(profile, new_v_ref)
        else:
            new_profile = set_profile_orientation(profile.copy(), new_v_ref)

        if h_ref is not None:
            new_df = new_profile['y_low'].apply(lambda x: x - h_ref)
            new_df = pd.concat([new_df, new_profile['y_mid'].apply(lambda x: x - h_ref)], axis=1, sort=False)
            new_df = pd.concat([new_df, new_profile['y_sup'].apply(lambda x: x - h_ref)], axis=1, sort=False)
            new_profile.update(new_df)
        return new_profile

    def drop_empty_property(self):
        empty = [prop for prop in self.get_property() if self[prop].isnull().all()]
        self.variable = ', '.join([prop for prop in self.get_property() if prop not in empty])
        self.drop(columns=empty, axis=1, inplace=True)

    def variables(self, notnan=False):
        """
        :param notnan: boolean, default False
        if True, return only variable with at least one not-nan value
        :return:
        """
        variables = []
        for var_group in self.variable.unique():
            variables += var_group.split(', ')

        # list of unique variables
        variables = list(set(variables))

        # remove empty variables
        if notnan:
            for variable in variables:
                if variable not in self.columns:
                    # remove variable from variables
                    for vg in [vg for vg in self.variable.unique() if variable in vg]:
                        vg_new = vg.split(', ')
                        vg_new.remove(variable)
                        self.loc[self.variable == vg, 'variable'] = (', ').join(filter(None, vg_new))
                        variables.remove(variable)
                elif self[variable].isna().all():
                    variables.remove(variable)

        if len(variables) == 1 and variables[0] is '':
            variables = None

        return variables

    def keep_variable(self, variables2keep):
        """

        :param variables2keep:
        :return:
        """
        if not isinstance(variables2keep, list):
            variables2keep = [variables2keep]

        # list variables to delete
        variables2remove = [var for var in self.variables() if var not in variables2keep]

        # delete variables
        self.remove_variable(variables2remove)


    def remove_variable(self, variables2remove):
        """
        :param variables2del:
        :return:
        """

        # TODO merge with profile.delete_variables
        if not isinstance(variables2remove, list):
            variables = [variables2remove]
        else:
            variables = variables2remove

        for variable in variables:
            if variable in self.variables():
                # delete variable column
                self.drop(variable, axis=1, inplace=True)

                # delete associated subvariable column
                if variable in seaice.subvariable_dict:
                    for subvariable in seaice.subvariable_dict[variable]:
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
        self.clean()

    def clean(self):
        """

        :return:
        """
        # remove all-nan variable
        for variable in self.variables():
            if self[variable].isna().all():
                self.remove_variable(variable)
        # clean profile by removing all-nan column
        col = [c for c in self.columns if c not in ['y_low', 'y_mid', 'y_sup']]

        y_var = [var for var in ['y_low', 'y_mid', 'y_sup'] if var in self.columns]

        self = pd.concat([self[y_var], self[col].dropna(axis=1, how='all')], sort=False, axis=1)
        return self

    @property
    def _constructor(self):
        return Profile

    # DEPRECATED
    def get_variable(self):
        self.logger = logging.getLogger(__name__)
        self.logger.warning('get_variable is deprecated. Use get_property')
        return self.get_property()


def discretize_profile(profile, y_bins=None, y_mid=y_mid, display_figure=False, fill_gap=fill_gap,
                       fill_extremity=fill_extremity, save_fig=save_fig, dropemptyrow=True):
    """
    :param profile:
    :param y_bins:
    :param y_mid:
    :param display_figure: boolean, default False
    :param fill_gap: boolean, default True

    :param fill_extremity: boolean, default False
    :return:
        profile
    """
    # TODO conductivity cannot be discretized as it's temperature non linearly dependant of the measurement temperature,
    # unless temperature profile of measurement temperature is isotherm.

    profile = Profile(profile)

    logger = logging.getLogger(__name__)

    if profile.empty:
        logger.warning("Discretization impossible, empty profile")
    else:
        if 'name' in profile.keys():
            logger.info("Processing %s" % profile.name.unique()[0])
        else:
            logger.info("Processing core")

    v_ref = profile.v_ref.unique()[0]

    # VARIABLES CHECK
    if y_bins is None and y_mid is None:
        y_bins = pd.Series(profile.y_low.dropna().tolist() + profile.y_sup.dropna().tolist()).sort_values().unique()
        y_mid = profile.y_mid.dropna().sort_values().unique()
        logger.info("y_bins and y_mid are empty, creating from profile")
    elif y_bins is None and y_mid is not None:
            logger.info("y_bins is empty, creating from given y_mid")
            y_mid = y_mid.sort_values().values
            dy = np.diff(y_mid) / 2
            y_bins = np.concatenate([[y_mid[0] - dy[0]], y_mid[:-1] + dy, [y_mid[-1] + dy[-1]]])
            if y_bins[0] < 0:
                y_bins[0] = 0
    else:
            y_mid = np.diff(y_bins) / 2 + y_bins[:-1]
            logger.info("y_mid is empty, creating from given y_bins")

    y_bins = np.array(y_bins)
    y_mid = np.array(y_mid)

    # Discretized Profile:
    discretized_profile = Profile()

    #TODO : discretization for temperature by interpolation
    # 2019-03-08: loop over the variable not the variable groups
    for _variable in profile.variables():
        var0 = [_variable]
        # select variable
        _profile = Profile(profile.loc[profile.variable.str.contains(_variable)])

        if not isinstance(_variable, list):
            _variable = [_variable]

        # check if _variable have dependent variable
        if _variable[0] in subvariable_dict:
            _variable.extend(subvariable_dict[_variable[0]])

        _del_variables = [var for var in _profile.variables() if var not in _variable]
        # drop all variables which are not _variable
        _profile.keep_variable(_variable)

        # TODO if 'temperature' goes to continue
        if _profile.empty:
            temp = pd.DataFrame()

        elif is_continuous(_profile):
            yx = _profile[['y_mid'] + _variable].set_index('y_mid').sort_index()
            y2 = y_mid

            # drop all np.nan columns
            # yx = yx.dropna(axis=1, how='all').astype(float)
            # _variables_notna = yx.keys().tolist()
            # yx = yx.dropna(axis=0, subset=['y_low', 'y_sup'], thresh=2).values

            x2 = np.array([np.interp(y2, yx.index, yx[_var], left=np.nan, right=np.nan) for _var in _variable])

            y2x = pd.DataFrame(x2.transpose(), columns=_variable, index=y2)
            yx = yx.drop_duplicates()

            # 'BRW_CS-20030224A' : if aligned at the bottom, double value for 0 : np.nan, -1.86
            yx = yx.dropna(axis=0)
            for index in yx.index.unique():
                y2x.loc[abs(y2x.index - index) < 1e-6, _variable] = yx.loc[yx.index == index, _variable].values

            # compute weight, if y_mid is in min(yx) < y_mid < max(yx)
            w = [1 if yx.index[0] - TOL <= y <= yx.index[-1] + TOL else 0 for y in y_mid ]

            # add the temperature profile extremum value
            if not any(abs(yx.index[0]-y2) < TOL):
                y2x.loc[yx.index[0], _variable] = yx.loc[yx.index == yx.index[0], _variable[0]].values
                w = w + [0]
            if not any(abs(yx.index[-1]-y2) < TOL):
                y2x.loc[yx.index[-1], _variable] = yx.loc[yx.index == yx.index[-1], _variable[0]].values
                w = w + [0]

            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(y2x.__len__()))
            temp.update(y2x.reset_index().rename(columns={'index': 'y_mid'}))
            temp['w_'+_variable[0]] = pd.Series(w, index=temp.index)
            temp = temp.sort_values('y_mid').reset_index(drop=True)
            profile_prop = _profile.loc[_profile.variable == _variable[0]].head(1)
            profile_prop = profile_prop.drop(_variable, 1)
            profile_prop['variable'] = ', '.join(_variable)
            if 'y_low' in profile_prop:
                profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            if 'y_sup' in profile_prop:
                profile_prop = profile_prop.drop('y_sup', 1)

            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))

        # elif 'mass' in _variable: TODO: add step profile type mass
        else:  # step profile (salinity-like)
            n_var = _variable.__len__()
            n_s0 = 2
            n_s1 = n_s0 + n_var

            if v_ref == 'bottom':
                yx = _profile[['y_sup', 'y_low'] + _variable].sort_values(by='y_low')
                if (yx.y_sup.head(1) > yx.y_low.head(1)).all():
                    yx = _profile[['y_low', 'y_sup'] + _variable].sort_values(by='y_low')
            else:
                yx = _profile[['y_low', 'y_sup'] + _variable].sort_values(by='y_low').astype(float)

            mass_variable = [_var for _var in _variable if 'mass' in _var]
            cont_variable = [_var for _var in _variable if _var in continuous_variable_list]

            _ii = 0
            _variable_dict = {}
            for _var in _variable:
                _variable_dict[_var] = _ii
                _ii += 1

            # drop all np.nan value
            col = yx.columns
            yx = yx.values

            # if missing section, add an emtpy section with np.nan as property value
            yx_new = []
            for row in range(yx[:, 0].__len__()-1):
                yx_new.append(yx[row])
                if abs(yx[row, 1]-yx[row+1, 0]) > TOL:
                    yx_new.append([yx[row, 1], yx[row + 1, 0]] + [np.nan] * _variable.__len__())
            yx_new.append(yx[row+1, :])
            yx = np.array(yx_new)
            del yx_new

            if fill_gap:
                value = pd.Series(yx[:, 2])
                value_low = value.fillna(method='ffill')
                value_sup = value.fillna(method='bfill')

                ymid = pd.Series(yx[:, 0]+(yx[:, 1]-yx[:, 0])/2)
                ymid2 = pd.Series(None, index=value.index)
                ymid2[np.isnan(value)] = ymid[np.isnan(value)]

                dy = pd.DataFrame(yx[:, 0:2], columns=['y_low', 'y_sup'])
                dy2 = pd.DataFrame([[None, None]], index=value.index, columns=['y_low', 'y_sup'])
                dy2[~np.isnan(value)] = dy[~np.isnan(value)]
                dy2w = dy2['y_low'].fillna(method='bfill') - dy2['y_sup'].fillna(method='ffill')
                new_value = value_low + (ymid2 - dy2['y_sup'].fillna(method='ffill'))*(value_sup-value_low)/dy2w
                value.update(new_value)

                yx[:, 2] = value

            # yx and y_bins should be ascendent suit
            if (np.diff(y_bins) < 0).all():
                logger.info("y_bins is descending reverting the list")
                y_bins = y_bins[::-1]
            elif (np.diff(y_bins) > 0).all():
                logger.debug("y_bins is ascending")
            else:
                logger.info("y_bins is not sorted")
            if (np.diff(yx[:, 0]) < 0).all():
                logger.info("yx is descending reverting the list")
                yx = yx[::-1, :]
            elif (np.diff(yx[:, 0]) > 0).all():
                logger.debug("yx is ascending")
            else:
                logger.info("yx is not sorted")

            # save yx for mass variable
            yx_mass = yx[:, [0, 1] + [np.where(_mvar == col)[0][0] for _mvar in mass_variable]].copy()
            yx_cont = yx[:, [0, 1] + [np.where(_cvar == col)[0][0] for _cvar in cont_variable]].copy()

            x_step = []
            y_step = []
            w_step = []  # weight of the bin, defined as the portion on which the property is define

            for ii_bin in range(y_bins.__len__()-1):
                a = np.flatnonzero((yx[:, 0] - y_bins[ii_bin] < -TOL) & ( y_bins[ii_bin] - yx[:, 1] < -TOL))
                a = np.concatenate((a, np.flatnonzero((y_bins[ii_bin] - yx[:, 0] <= TOL) & (yx[:, 1] - y_bins[ii_bin+1] <= TOL))))
                a = np.concatenate((a, np.flatnonzero((yx[:, 0] - y_bins[ii_bin+1] < -TOL) & ( y_bins[ii_bin+1] - yx[:, 1] < -TOL))))
                a = np.unique(a)

                if DEBUG:
                    print('target section %.4f - %.4f' % (y_bins[ii_bin], y_bins[ii_bin + 1]))
                    print('- original section %s' % ', '.join(a.astype(str)))

                if a.size != 0:
                    S = [np.nan]*n_var
                    L = np.zeros_like(S)
                    L_nan = np.zeros_like(S)
                    a_ii = 0

                    if yx[a[a_ii], 0] - y_bins[ii_bin] < -TOL:
                        S_temp = yx[a[a_ii], n_s0:n_s1]*(yx[a[a_ii], 1] - y_bins[ii_bin])
                        S = np.nansum([S, S_temp], axis=0)
                        l = yx[a[a_ii], 1] - y_bins[ii_bin]
                        L = np.nansum([L, l * ~np.isnan(S_temp)], axis=0)
                        L_nan = np.nansum([L, l * np.isnan(S_temp)], axis=0)
                        if DEBUG:
                            print('\t\t %.3f - %.3f : %.4f - %.4f :S_bin = %.3f (%.1f)' % (
                            y_bins[ii_bin], y_bins[ii_bin + 1], yx[a[a_ii], 0], yx[a[a_ii], 1], S_temp,
                            100 * l / (y_bins[ii_bin + 1] - y_bins[ii_bin])))
                        a_ii += 1
                    while ii_bin+1 <= y_bins.shape[0]-1 and a_ii < a.shape[0]-1 and yx[a[a_ii], 1] - y_bins[ii_bin+1] < -TOL:
                        S_temp = yx[a[a_ii], n_s0:n_s1] * (yx[a[a_ii], 1]-yx[a[a_ii], 0])
                        S = np.nansum([S, S_temp], axis=0)
                        l = yx[a[a_ii], 1]-yx[a[a_ii], 0]
                        L = np.nansum([L, l * ~np.isnan(S_temp)], axis=0)
                        L_nan = np.nansum([L_nan, l * np.isnan(S_temp)], axis=0)
                        if DEBUG:
                            print('\t\t %.3f - %.3f : %.4f - %.4f :S_bin = %.3f (%.3f)' % (
                            y_bins[ii_bin], y_bins[ii_bin + 1], yx[a[a_ii], 0], yx[a[a_ii], 1], S_temp,
                            100 * l / (y_bins[ii_bin + 1] - y_bins[ii_bin])))
                            # print('\t\t %.3f - %.3f : S_bin = %.3f' % (yx[a[a_ii], 0], yx[a[a_ii], 1], S_temp))
                        a_ii += 1

                    # check if a_ii-1 was not the last element of a
                    if a_ii < a.size:
                        if yx[a[a_ii], 1] - y_bins[ii_bin+1] > -TOL:
                            l = y_bins[ii_bin+1] - yx[a[a_ii], 0]  # length of the suction
                            S_temp = yx[a[a_ii], n_s0:n_s1] * l
                            S = np.nansum([S, S_temp], axis=0)
                            L = np.nansum([L, l * ~np.isnan(S_temp)], axis=0)
                            L_nan = np.nansum([L_nan, l * np.isnan(S_temp)], axis=0)
                            if DEBUG:
                                print('\t\t %.3f - %.3f : %.4f - %.4f :S_bin = %.3f (%.1f)' % (
                                y_bins[ii_bin], y_bins[ii_bin + 1], yx[a[a_ii], 0], yx[a[a_ii], 1], S_temp,
                                100 * l / (y_bins[ii_bin + 1] - y_bins[ii_bin])))
                        elif yx[a[a_ii], 1] - y_bins[ii_bin + 1] < -TOL:
                            S_temp = yx[a[a_ii], n_s0:n_s1] * (yx[a[a_ii], 1] -yx[a[a_ii], 0])
                            S = np.nansum([S, S_temp], axis=0)
                            l = yx[a[a_ii], 1] -yx[a[a_ii], 0]
                            L = np.nansum([L, l * ~np.isnan(S_temp)], axis=0)
                            L_nan = np.nansum([L_nan, l * np.isnan(S_temp)], axis=0)
                            if DEBUG:
                                print('\t\t %.3f - %.3f : %.4f - %.4f :S_bin = %.3f (%.3f)' % (
                                y_bins[ii_bin], y_bins[ii_bin + 1], yx[a[a_ii], 0], yx[a[a_ii], 1], S_temp,
                                100 * l / (y_bins[ii_bin + 1] - y_bins[ii_bin])))

                    w = L / (y_bins[ii_bin + 1]-y_bins[ii_bin])
                    L[L == 0] = np.nan
                    S = S / L
                    if yx[a[0], 0] - y_bins[ii_bin] > TOL and not fill_extremity:
                        y_step.append(yx[a[0], 0])
                        y_step.append(y_bins[ii_bin + 1])
                    elif yx[a[-1], 1] - y_bins[ii_bin + 1] < -TOL and not fill_extremity:
                        y_step.append(y_bins[ii_bin])
                        y_step.append(yx[a[-1], 1])
                    else:
                        y_step.append(y_bins[ii_bin])
                        y_step.append(y_bins[ii_bin + 1])
                else:
                    S = np.array([np.nan] * n_var)
                    w = np.array([0] * n_var)
                    y_step.append(y_bins[ii_bin])
                    y_step.append(y_bins[ii_bin + 1])
                x_step.append(S)
                w_step.append(w)

                if DEBUG:
                    x_plot = []
                    for x in x_step:
                        x_plot.extend(x)
                        x_plot.extend(x)
                    x_xy_plot = []
                    y_xy_plot = []
                    for ii in range(0, len(yx[:, 0])):
                        x_xy_plot.extend([yx[ii, 2]])
                        x_xy_plot.extend([yx[ii, 2]])
                        y_xy_plot.extend([yx[ii, 0]])
                        y_xy_plot.extend([yx[ii, 1]])
                    plt.figure()
                    plt.step(x_xy_plot, y_xy_plot)
                    plt.step(x_plot, y_step, 'x')
                    plt.title(profile.get_name())
                    plt.show()
            # for end

            W = np.array(w_step)
            X = np.array(x_step)

            if mass_variable.__len__() > 0:
                x_step = []
                y_step = []
                w_step = []  # weight of the bin, defined as the portion on which the property is define
                yx_bkp = yx.copy()
                yx = yx_mass

                n_s0 = 2
                n_var = mass_variable.__len__()
                n_s1 = n_s0 + n_var
                for ii_bin in range(y_bins.__len__() - 1):
                    a = np.flatnonzero((yx[:, 0] - y_bins[ii_bin] < -TOL) & (y_bins[ii_bin] - yx[:, 1] < -TOL))
                    a = np.concatenate((a, np.flatnonzero(
                        (y_bins[ii_bin] - yx[:, 0] <= TOL) & (yx[:, 1] - y_bins[ii_bin + 1] <= TOL))))
                    a = np.concatenate((a, np.flatnonzero(
                        (yx[:, 0] - y_bins[ii_bin + 1] < -TOL) & (y_bins[ii_bin + 1] - yx[:, 1] < -TOL))))
                    a = np.unique(a)

                    if DEBUG:
                        print('target section %.4f - %.4f' % (y_bins[ii_bin], y_bins[ii_bin + 1]))
                        print('- original section %s' % ', '.join(a.astype(str)))

                    if a.size != 0:
                        M = [np.nan] * (n_var)
                        L = np.zeros_like(M)
                        L_nan = np.zeros_like(M)
                        a_ii = 0

                        # section yx_0 < y_bins_0 < yx_1 < y_bins_1
                        if yx[a[a_ii], 0] - y_bins[ii_bin] < -TOL:
                            l = yx[a[a_ii], 1] - y_bins[ii_bin]
                            M_temp = yx[a[a_ii], n_s0:n_s1] * l / (yx[a[a_ii], 1] - yx[a[a_ii], 0])
                            M = np.nansum([M, M_temp], axis=0)
                            L = np.nansum([L, l * ~np.isnan(M_temp)], axis=0)
                            L_nan = np.nansum([L, l * np.isnan(M_temp)], axis=0)
                            if DEBUG:
                                print('\t\t %.3f - %.3f : %.4f - %.4f :S_bin = %.3f (%.1f)' % (
                                    y_bins[ii_bin], y_bins[ii_bin + 1],
                                    yx[a[a_ii], 0], yx[a[a_ii], 1],
                                    M_temp, 100 * l / (y_bins[ii_bin + 1] - y_bins[ii_bin])))
                            a_ii += 1

                        while ii_bin + 1 <= y_bins.shape[0] - 1 and a_ii < a.shape[0] - 1 and yx[a[a_ii], 1] - y_bins[
                            ii_bin + 1] < -TOL:
                            M_temp = yx[a[a_ii], n_s0:n_s1]
                            M = np.nansum([M, M_temp], axis=0)
                            l = yx[a[a_ii], 1] - yx[a[a_ii], 0]
                            L = np.nansum([L, l * ~np.isnan(M_temp)], axis=0)
                            L_nan = np.nansum([L_nan, l * np.isnan(M_temp)], axis=0)
                            if DEBUG:
                                print('\t\t %.3f - %.3f : %.4f - %.4f :S_bin = %.3f (%.3f)' % (
                                    y_bins[ii_bin], y_bins[ii_bin + 1], yx[a[a_ii], 0], yx[a[a_ii], 1], M_temp,
                                    100 * l / (y_bins[ii_bin + 1] - y_bins[ii_bin])))
                            a_ii += 1

                        # check if a_ii-1 was not the last element of a
                        if a_ii < a.size:
                            # section of the next y_bins_0 < bin yx_0 < y_bins_1 < yx_1
                            if yx[a[a_ii], 1] - y_bins[ii_bin + 1] > -TOL:
                                l = y_bins[ii_bin + 1] - yx[a[a_ii], 0]
                                M_temp = yx[a[a_ii], n_s0:n_s1] * l / (yx[a[a_ii], 1] - yx[a[a_ii], 0])
                                M = np.nansum([M, M_temp], axis=0)
                                L = np.nansum([L, l * ~np.isnan(M_temp)], axis=0)
                                L_nan = np.nansum([L_nan, l * np.isnan(M_temp)], axis=0)
                                # print(yx[a[a_ii], 0], y_bins[ii_bin+1], M_temp)
                            # section of the next y_bins_0 = bin yx_0 < y_bins_1 < yx_1
                            elif yx[a[a_ii], 1] - y_bins[ii_bin + 1] < -TOL:
                                l = yx[a[a_ii], 1] - yx[a[a_ii], 0]
                                M_temp = yx[a[a_ii], n_s0:n_s1]
                                M = np.nansum([M, M_temp], axis=0)
                                L = np.nansum([L, l * ~np.isnan(M_temp)], axis=0)
                                L_nan = np.nansum([L_nan, l * np.isnan(M_temp)], axis=0)
                                # print(yx[a[a_ii], 0], yx[a[a_ii], 1], M_temp)

                        w = L / (y_bins[ii_bin + 1] - y_bins[ii_bin])
                        L[L == 0] = np.nan

                        if yx[a[0], 0] - y_bins[ii_bin] > TOL and not fill_extremity:
                            y_step.append(yx[a[0], 0])
                            y_step.append(y_bins[ii_bin + 1])
                        elif yx[a[-1], 1] - y_bins[ii_bin + 1] < -TOL and not fill_extremity:
                            y_step.append(y_bins[ii_bin])
                            y_step.append(yx[a[-1], 1])
                        else:
                            y_step.append(y_bins[ii_bin])
                            y_step.append(y_bins[ii_bin + 1])
                    else:
                        M = np.array([np.nan] * n_var)
                        w = np.array([0] * n_var)
                        y_step.append(y_bins[ii_bin])
                        y_step.append(y_bins[ii_bin + 1])
                    x_step.append(M)
                    w_step.append(w)

                X[:, [_variable_dict[_mvar] for _mvar in mass_variable]] = np.array(x_step)
                W[:, [_variable_dict[_mvar] for _mvar in mass_variable]] = np.array(w_step)

            if cont_variable.__len__() > 0:
                y = (yx_cont[:, 0]+yx_cont[:, 1]) / 2
                x = yx_cont[:, 2:]
                yc_mid = y_mid[0:X.shape[0]]
                xc_step = np.array([np.interp(yc_mid, y, x[:, ii], left=np.nan, right=np.nan)
                                  for ii in range(0, len(cont_variable))])

                wc_step = [1 if yx_cont[0, 0] - TOL <= y <= yx_cont[-1, 1] + TOL else 0 for y in yc_mid]
                wc_step = [wc_step]*xc_step.shape[0]

                X[:, [_variable_dict[_cvar] for _cvar in cont_variable]] = np.array(xc_step).transpose()
                W[:, [_variable_dict[_cvar] for _cvar in cont_variable]] = np.array(wc_step).transpose()

            x_step = X.transpose()
            w_step = W.transpose()

            Y = y_bins[:np.unique(y_step).__len__()]
            y_step = np.array([Y[:-1], Y[:-1] + np.diff(Y) / 2, Y[1:]])

            w_variables = ['w_' + _var for _var in _variable]

            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(len(Y) - 1))
            for w in w_variables:
                temp[w] = [np.nan]*temp.__len__()

            # set the y_step equal to y_bins
            _updated_df = pd.DataFrame(np.vstack((y_step, w_step, x_step)).transpose(),
                                       columns=['y_low', 'y_mid', 'y_sup'] + w_variables + _variable,
                                       index=temp.index[0:np.unique(y_step).__len__() - 1])
            temp.update(_updated_df)

            # core attribute
            profile_prop = _profile.head(1).copy()
            profile_prop['variable'] = var0
            profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            profile_prop = profile_prop.drop('y_sup', 1)
            profile_prop = profile_prop.drop(_variable, axis=1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))

        if not temp.empty:
            temp.reset_index(drop=True, inplace=True)
            temp.loc[temp[_variable[0]].isna(), 'w_'+_variable[0]] = 0

            # keep only ice core length by entry
            # TODO: remove all np.nan entry for the variable, this implies better merging function for pandas
            l_c = temp.length.unique()[0]
            if not np.isnan(temp.length.unique()[0]):
                if l_c > 0 and temp.v_ref.unique()[0] == 'top':
                    try:
                        n_y_mid_max = np.where(l_c <= temp.y_mid)[0][0]
                    except IndexError:
                        n_y_mid_max = temp.y_mid.max()
                    if dropemptyrow:
                        temp = temp.loc[temp.index <= n_y_mid_max]
                    else:
                        temp.loc[n_y_mid_max < temp.index, 'w_'+_variable[0]] = 0
                        temp.loc[n_y_mid_max < temp.index, _variable[0]] = np.nan
                elif l_c > 0 and temp.v_ref.unique()[0] == 'bottom':
                    h_i = temp.ice_thickness.mean()
                    if np.isnan(h_i):
                        h_i = - l_c
                    try:
                        n_y_mid_min = np.where(temp.y_mid <= h_i-l_c)[0][-1]
                    except IndexError:
                        n_y_mid_min = 0
                    try:
                        n_y_mid_max = np.where(temp.y_mid <= h_i)[0][-1]
                    except IndexError:
                        n_y_mid_max = temp.y_mid.max()
                    if dropemptyrow:
                        temp = temp.loc[(n_y_mid_min <= temp.index) & (temp.index <= n_y_mid_max)]
                    else:
                        temp.loc[temp.index < n_y_mid_min, 'w_'+_variable[0]] = 0
                        temp.loc[temp.index < n_y_mid_min, _variable[0]] = np.nan
                        temp.loc[n_y_mid_max < temp.index, 'w_'+_variable[0]] = 0
                        temp.loc[n_y_mid_max < temp.index, _variable[0]] = np.nan
                    # temp = temp[(h_i + l_c <= temp.y_mid) & (temp.y_mid <= h_i)]
                elif l_c < 0 and temp.v_ref.unique()[0] == 'bottom':
                    h_i = temp.ice_thickness.mean()
                    if np.isnan(h_i):
                        h_i = - l_c
                    n_y_mid_max = np.where(temp.y_mid <= h_i+l_c & h_i <= temp.y_mid)
                    if dropemptyrow:
                        temp = temp.loc[temp.index <= n_y_mid_max]
                    else:
                        temp.loc[n_y_mid_max < temp.index, 'w_'+_variable[0]] = 0
                        temp.loc[n_y_mid_max < temp.index, _variable[0]] = np.nan
                    # temp = temp[(h_i + l_c <= temp.y_mid) & (temp.y_mid <= h_i)]
                else:
                    logger.error('ERROR PROFILE.DISCRETIZED_PROFILE')
            elif not np.isnan(temp.ice_thickness.unique()[0]):
                n_y_mid_max = np.where(temp.ice_thickness.unique()[0] <= temp.y_mid)[0][0]
                if dropemptyrow:
                    temp = temp.loc[temp.index <= n_y_mid_max]
                else:
                    temp.loc[n_y_mid_max < temp.index, 'w_' + _variable[0]] = 0
                    temp.loc[n_y_mid_max < temp.index, _variable[0]] = np.nan
                # temp = temp[(temp.y_mid <= temp.ice_thickness.unique()[0])]
            else:
                # TODO : check if it works from bottom too
                y_in_ice = [y for y in temp.y_mid[::-1] if not temp.loc[temp.y_mid > y, _variable[0]].isna().all()]
                if dropemptyrow:
                    temp = temp[temp.y_mid.isin(y_in_ice)]
                else:
                    temp.loc[~temp.y_mid.notin(y_in_ice), 'w_' + _variable[0]] = 0
                    temp.loc[~temp.y_mid.notin(y_in_ice), _variable[0]] = np.nan

            # drop all nan columns, but variable:
            temp = temp.dropna(axis=1, how='all')

            # convert column to correct format
            temp = temp.apply(pd.to_numeric, errors='ignore')
            if 'date' in temp:
                temp['date'] = pd.to_datetime(temp['date'])
            if 'comment' in temp:
                temp['comment'] = temp['comment'].astype(str).replace('nan', None)

            if discretized_profile.empty:
                discretized_profile = temp
            else:
                if 'variable' in temp.columns:
                    temp = temp.drop('variable', axis=1)
                temp = temp.rename(columns={'comment': 'comment_temp'})

                col = [col for col in discretized_profile.columns if col in temp.columns]

                not_matching_col = [c for c in col if not discretized_profile.iloc[0][c] == temp.iloc[0][c]]

                if len(not_matching_col) == 0:
                    discretized_profile = pd.merge(discretized_profile, temp, on=col, sort=False)
                    for vg in discretized_profile.variable.unique():
                        new_vg = vg.split(', ')
                        new_vg += var0
                        discretized_profile.loc[discretized_profile.variable == vg, 'variable'] = ', '.join(new_vg)
                else:
                    #TODO: check if not matching 'y_mid' is extrmum point for continuous profile
                    if not_matching_col == ['length']:
                        logger.warning('%s - (%s) %s length not matching between profile' % (__package__ + '.' + __name__,
                                                                                      profile.name.unique()[0],
                                                                                      ', '.join(not_matching_col)))
                        l_c_p = discretized_profile.length.unique()[0]
                        # merge profile up to maximum common depth
                        if l_c < l_c_p:
                            temp.length = l_c_p
                            discretized_profile_extra = discretized_profile.loc[l_c < discretized_profile.y_mid].copy()
                            discretized_profile = pd.merge(discretized_profile, temp, on=col, sort=False)
                            for vg in discretized_profile.variable.unique():
                                new_vg = vg.split(', ')
                                new_vg += var0
                                discretized_profile.loc[discretized_profile.variable == vg, 'variable'] = ', '.join(list(set(filter(None, new_vg))))
                            discretized_profile = pd.concat([discretized_profile, discretized_profile_extra])
                        else:
                            discretized_profile.length = l_c
                            temp_extra = temp.loc[l_c_p < temp.y_mid].copy()
                            temp_extra['variable'] = var0[0]
                            discretized_profile = pd.merge(discretized_profile, temp, on=col, sort=False)
                            for vg in discretized_profile.variable.unique():
                                new_vg = vg.split(', ')
                                new_vg += var0
                                discretized_profile.loc[discretized_profile.variable == vg, 'variable'] = ', '.join(list(set(filter(None, new_vg))))
                            discretized_profile = pd.concat([discretized_profile, temp_extra])
                    else:
                        temp['variable'] = var0[0]
                        discretized_profile = pd.concat([discretized_profile, temp])

                # add comment
                if 'comment_temp' in discretized_profile.columns:
                    discretized_profile['comment'] = discretized_profile[['comment', 'comment_temp']].astype(str).replace('nan', '').apply(lambda x: ', '.join(filter(None, x)), axis=1)
                    discretized_profile = discretized_profile.drop('comment_temp', axis=1)
    discretized_profile = Profile(discretized_profile)

    # clean up:
    discretized_profile.reset_index(drop=True, inplace=True)
    discretized_profile.sort_values(by='y_mid', inplace=True)

    if display_figure:
        if profile.v_ref.unique()[0] == 'top':
            profile.sort_values(by='y_mid', inplace=True)
        else:
            profile.sort_values(by='y_mid', inplace=True, ascending=False)
        ax, ax_dict = seaice.core.plot.plot_all_profile_variable(profile, ax=None, display_figure=False,
                                                                 param_dict={'linestyle': ':', 'color': 'k'})
        seaice.core.plot.plot_all_profile_variable(discretized_profile, ax=ax, ax_dict=ax_dict,
                                                   display_figure=display_figure,
                                                   param_dict={'linestyle': ':', 'marker': 'x', 'color': 'r'})
    return Profile(discretized_profile)


def set_profile_orientation(profile, v_ref):
    """

    :param profile:
    :param v_ref: new reference 'top', 'bottom'
    :return:
    """
    logger = logging.getLogger(__name__)

    for vg in profile.variable.unique():
        # look for ice thickness:
        if profile[profile.variable == vg].v_ref.unique().__len__() > 1:
            logger.error("vertical reference for profile are not consistent")
        if not profile[profile.variable == vg].v_ref.unique().tolist()[0] == v_ref:
            # search ice core length, and ice thickness
            if 'ice_thickness' in profile.keys() and \
                    not np.isnan(profile[profile.variable == vg].ice_thickness.astype(float)).all():
                    hi = profile[profile.variable == vg].ice_thickness.astype(float).unique()[-1]
            else:
                hi = np.nan

            if 'length' in profile.keys() and \
                    not np.isnan(profile[profile.variable == vg].length.astype(float)).all():
                    lc = profile[profile.variable == vg].length.astype(float).unique()[-1]
            else:
                lc = np.nan

            if lc is np.nan and hi is np.nan:
                if 'name' in profile.keys():
                    logger.warning("Mising core length or ice thickness, impossible to set profile orientation to %s.\
                    Deleting profile (%s)" %(v_ref, profile.name.unique()[0]))
                else:
                    logger.warning("Mising core length or ice thickness, impossible to set profile orientation to %s.\
                    Deleting profile" % v_ref)
                profile = delete_profile(profile, {'variable': vg})
            else:
                print(profile.name.unique()[0])
                if np.abs(lc - hi) < 0.1*hi:
                    href = lc
                    logger.info("Bottom reference set to ice core length:\
                    as ice core length is within 10% of the ice thickness")
                elif hi is not None:
                    href = hi
                    logger.info("Bottom reference set to ice thickness")
                elif lc is not None:
                    href = lc
                    logger.info("Bottom reference set to ice core length in absence of ice thickness")

                new_df = profile.loc[profile.variable == vg, 'y_low'].apply(lambda x: href - x)
                new_df = pd.concat([new_df, profile.loc[profile.variable == vg, 'y_mid'].apply(lambda x: href - x)],
                                   axis=1, sort=False)
                new_df = pd.concat([new_df, profile.loc[profile.variable == vg, 'y_sup'].apply(lambda x: href - x)],
                                   axis=1, sort=False)
                new_df['v_ref'] = 'bottom'
                profile.update(new_df)
        else:
            logger.info('profile orientiation already set')

    if v_ref == ' bottom':
        profile.length = -np.abs(profile.length)
    else:
        profile.length = np.abs(profile.length)

    return profile


def delete_variables(ics_stack, variables2del):
    """

    :param ics_stack:
    :param variables2del:
    :return:
    """
    if not isinstance(variables2del, list):
        variables2del = [variables2del]

    __temp = Profile()
    __removed_columns = []
    if len(variables2del) == 0:
        __temp = ics_stack
    else:
        for variable in variables2del:
            # delete all columns which are related to variaibles, i.e. column name contains variable or variable_ or_variable
            columns2del = [col for col in ics_stack.columns if any(v in col for v in [variable, '_'+variable, variable+'_'])]
            __removed_columns.extend(columns2del)
            for col in columns2del:
                # delete variable column
                ics_stack.drop(col, axis=1, inplace=True)

            # delete associated subvariable column
            if variable in subvariable_dict:
                for subvariable in subvariable_dict[col]:
                    ics_stack.drop(subvariable, axis=1, inplace=True)

            # remove variable from variable groups, remove rows if the variable group is empty
            for group in ics_stack.variable.unique():
                new_group = group.split(', ')
                if variable in new_group:
                    new_group.remove(variable)
                    if len(new_group) > 0:
                        _temp = ics_stack.loc[ics_stack.variable == group]
                        _temp['variable'] = ', '.join(new_group)
                    else:
                        _temp = Profile()
                else:
                    _temp = ics_stack[ics_stack.variable == group]

                _temp = Profile(_temp)
                if not _temp.empty:
                    if __temp.empty:
                        __temp = _temp
                    else:
                        __temp = __temp.add_profile(_temp)
    if __temp.empty:
        headers = [c for c in ics_stack if c not in __removed_columns]
        __temp = seaice.core.corestack.CoreStack(pd.DataFrame(columns=headers))
    return __temp


def select_variables(ics_stack, variables):
    """
    Return an excerpt of the profile or dataframe with only the selected variable
    :param ics_stack: Profile, CoreStack
    :param variables: list of variable to return in the DataFrame
    :return:
    :updated: 2009-04-18
    """

    from seaice.core.corestack import CoreStack
    from seaice.core.profile import Profile

    logger = logging.getLogger(__name__)

    new_stack = ics_stack.copy()

    # check input:
    if not isinstance(variables, list):
        variables = [variables]
    stack_type = None
    if isinstance(new_stack, Profile):
        stack_type = 'Profile'
    elif isinstance(new_stack, CoreStack):
        stack_type = 'CoreStack'
    else:
        logger.error('stack should be of class Profile or CoreStack')

    for variable in variables:
        if variable not in new_stack.variables():
            variables.remove(variable)
            logger.warning('Variable %s not in stack variables, removing %s' % (variable, variable))

    # create list of variable to remove from the stack:
    variables2del = [var for var in new_stack.variables() if not var in variables]

    # new stack is ics_stack without variables2del
    new_stack = delete_variables(new_stack, variables2del)

    if stack_type == 'Profile':
        return seaice.core.profile.Profile(new_stack)
    elif stack_type == 'CoreStack':
        return seaice.core.corestack.CoreStack(new_stack)
    else:
        logger.warning('Stack class undefined, returning DataFrame')
        return new_stack

#
#
# def select_variable(ics_stack, variable):
#     profile = Profile()
#     for group in ics_stack.variable.unique():
#         variable_group = group.split(', ')
#         if variable in variable_group:
#             # TODO: convert data to Profile rather than CoreStack, REQUIRE: Profile should inherit Profile
#             # property (@property _constructor)
#             temp_profile = ics_stack[ics_stack.variable == group]
#
#             # delete other variable
#             variables2del = [_var for _var in temp_profile.get_property() if not _var == variable]
#
#             temp_profile = delete_variables(temp_profile, variables2del)
#         if profile.empty:
#             profile = temp_profile
#         else:
#             profile = profile.add_profile(temp_profile)
#     return profile


def select_profile(ics_stack, variable_dict):
    """

    :param ics_stack:
    :param variable_dict:
    :return:
    """
    for ii_key in variable_dict.keys():
        if ii_key is 'variable':
            if variable_dict[ii_key] in ics_stack.get_property():
                ics_stack = select_variables(ics_stack, variable_dict[ii_key])
            else:
                ics_stack = delete_variables(ics_stack, ics_stack.get_property())
        elif ii_key in ics_stack.keys():
            ics_stack = ics_stack[ics_stack[ii_key] == variable_dict[ii_key]]

    if 'y_mid'  in ics_stack.columns:
        ics_stack.sort_values(by=['y_mid'], inplace=True)
    elif 'y_low' in ics_stack.columns:
        ics_stack.sort_values(by=['y_low'], inplace=True)

    return ics_stack


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
        if ii_key in ics_stack.keys():
            ii_var.append(variable_dict[ii_key])
            str_select = str_select + 'ics_stack.' + ii_key + '!=ii_var[' + str('%d' % ii) + ']) | ('
            ii += 1
    str_select = str_select[:-4]
    return ics_stack.loc[eval(str_select)]


# s_nan is deprecated function
def s_nan(yx, ii_yx, fill_gap=True):
    """
    :param yx:
    :param ii_yx:
    :param fill_gap:
    :return:
    """
    if np.isnan(yx[ii_yx, 2]) and fill_gap:
        ii_yx_l = ii_yx - 1
        while ii_yx_l > 0 and np.isnan(yx[ii_yx_l, 2]):
            ii_yx_l -= 1
        if ii_yx_l > 0:
            s_l = yx[ii_yx_l, 2]
        else:
            s_l = np.nan

        ii_yx_s = ii_yx
        while ii_yx_s < yx.shape[0] - 1 and np.isnan(yx[ii_yx_s, 2]):
            ii_yx_s += 1
        s_s = yx[ii_yx_s, 2]

        s = (s_s + s_l) / 2
    else:
        s = yx[ii_yx, 2]
    return s


def is_continuous(profile):
    if ('y_low' in profile and profile.y_low.isnull().all() and not profile.y_low.empty):
        return 1
    elif len(profile.variables()) == 1 and profile.variables()[0] == 'temperature':
        return 1
    elif 'y_low' not in profile:
        return 1
    else:
        return 0


def uniformize_section(profile, profile_target):
    """

    :param profile: seaice.core.profile
        Profile with section bin to be match to target profile
    :param profile_target: seaice.core.profile
        Profile with section bin to match
    :return: seaice.core.profile
        Profile with section bin matched to target profile
    """

    if not is_continuous(profile_target):
        if not profile_target.y_mid.isna().all():
            y_mid = profile_target.y_mid.dropna().values
        else:
            y_mid = (profile_target.y_low +profile_target.y_sup/2).dropna().values

    else:
        y_mid = profile_target.y_mid.dropna().values

    if is_continuous(profile):
        profile = profile.sort_values(by='y_mid').reindex()
    else:
        profile = profile.sort_values(by='y_low')
        if profile.y_mid.isna().any():
            profile['y_mid'] = (profile.y_low +profile.y_sup/2).dropna().values


    # replace the 2 following lines
    variable = profile.variable.unique()[0]
    interp_data = np.interp(y_mid, profile['y_mid'].values, profile[variable].values, left=np.nan, right=np.nan)
    profile_new = pd.DataFrame(np.transpose([interp_data, y_mid, [variable]*y_mid.__len__()]), columns=[variable, 'y_mid', 'variable'])

    # copy attribute from profile to new_profile:
    not_target_attribute = list(profile.variable.unique()) + ['y_mid']
    attribute = [atr for atr in profile.keys() if atr not in not_target_attribute]
    _attribute = profile_target[attribute].head(1)
    profile_new[attribute] = _attribute
    profile_new[variable] = profile_new[variable].astype(float)
    return profile_new