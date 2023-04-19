# ! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    pysic.core.profile.py : toolbox to work on property measurement profile
"""
import logging
import pandas as pd

__comment__ = "profile.py contains class Profile() to store measurement profile of sea ice core, and collection " \
              "of function to handle profile"

logger = logging.getLogger(__name__)

class Profile(pd.DataFrame):
    """

    """
    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    @property
    def variable(self, string=False):
        """
        Return properties stored in the profiles
        :return: str or array
            List of property or None if there is no property stored in the profile
        """

        if 'property' not in self.columns:
            self.logger.error('\t\t No variable in profile')
            if string:
                return ''
            else:
                return [None]
        else:
            _variable = []
            for prop_grp in self.property.unique():
                if prop_grp is not None:
                    if ',' in prop_grp:
                        _variable += list(filter(None, prop_grp.split(', ')))
                    else:
                        _variable += [prop_grp]
        if string:
            return ', '.join(_variable)
        else:
            return list(set(_variable))


    @variable.deleter
    def variable(self, variable2del, string=False):
        self.logger.error('\t\t @variable.deleter not implemented yet')
        return self

    def get_name(self):
        """
        Return the name of the profile, or an array of string if there is several
        :return name: string
        """
        self.logger = logging.getLogger(__name__)
        try:
            name = self.name.unique()
        except AttributeError:
            return None
        else:
            if name.__len__() > 1:
                self.logger.warning(' %s more than one name in the profile: %s ' % (name[0], ', '.join(name)))
                self.name.unique()
            else:
                return self.name.unique()[0]









    #
    #
    # def clean(self, inplace=True):
    #     """
    #     Clean profile by removing all empty property
    #     :return:
    #     """
    #     self.logger = logging.getLogger(__name__)
    #
    #     variable = self.get_property()
    #     null_property = self.columns[self.isnull().all(axis=0)].tolist()
    #     kept_property = [prop for prop in variable if prop not in null_property]
    #
    #     if null_property:
    #         self.logger.info('Property are empty, deleting: %s' % ', '.join(null_property))
    #         if kept_property:
    #             self['variable'] = None
    #         else:
    #             self['variable'] = ', '.join(kept_property)
    #
    #     if inplace:
    #         self.dropna(axis=1, how='all', inplace=True)
    #     else:
    #         return self.dropna(axis=1, how='all')

    def add(self, profile):
        """
        Add new profile to existing profile.
        For consistency, profile name should match
        :param profile: pysic.Profile()
        """
        if profile.get_name() is self.get_name():
            column_merge = [c for c in profile.columns if c in self.columns]
            new_profile = self.merge(profile, how='outer', sort=False, on=column_merge).reset_index(drop=True)

            if 'property_x' in new_profile.columns:
                new_profile['property'] = new_profile[['property_x', 'property_x']].apply(lambda x: '{}, {}'.format(x[0], x[1]), axis=1)
                new_profile['property'] = new_profile['property'].apply(lambda x: ', '.join(list(set(x.split(', ')))))
                new_profile.drop(['property_x', 'property_x'], axis=1, inplace=True)
            if 'comment_x' in new_profile.columns:
                new_profile['comment'] = new_profile[['comment_x', 'comment_y']].apply(lambda x: '{}, {}'.format(x[0], x[1]), axis=1)
                new_profile['comment'] = new_profile['comment'].apply(lambda x: ', '.join(list(set(x.split(', ')))))
                new_profile.drop(['comment_x', 'comment_y'], axis=1, inplace=True)
            return new_profile
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.warning('Try to add profile from %s to %s profile: profile name does not match' % (profile.get_name(), self.get_name()))
    #
    # def delete_property(self, property):
    #     """
    #     Remove property
    #
    #     :param property:
    #     :return:
    #     """
    #     if not isinstance(property, list):
    #         property = [property]
    #
    #     new_property = self.get_property()
    #     for prop in property:
    #         if prop in self.get_property():
    #             self.drop(prop, axis=1, inplace=True)
    #             new_property.remove(prop)
    #
    #             if prop in subvariable_dict.keys():
    #                 for _subprop in subvariable_dict[prop]:
    #                     if _subprop in self.columns:
    #                         self.drop(_subprop, axis=1, inplace=True)
    #
    #      # write variable
    #     self['variable'] = ', '.join(new_property)
    #
    # def select_property(self, vg_property=None, extra_keys=[]):
    #     # TODO hard code sea ice property
    #     # TODO merge with profile.select_variable
    #     if vg_property is None:
    #         vg_property = self.get_property()
    #     elif not isinstance(vg_property, list):
    #         vg_property = [vg_property]
    #
    #     vg_group = [vg_group for vg_group in self.variable.unique() for vg_prop in vg_group.split(', ') if vg_prop in vg_property]
    #
    #     # add property weight if it was discretized
    #     keys = essential_property + [prop for prop in vg_property] + ['w_'+prop for prop in vg_property]
    #
    #     # add extra keys if define
    #     keys = list(set([key for key in keys if key in self.keys()]+extra_keys))
    #
    #     # select profile
    #     data_prop = self[self.variable.isin(vg_group)][keys]
    #
    #     # change variable:
    #     for vg in vg_group:
    #         new_vg = ', '.join([prop for prop in vg_property if prop in vg])
    #         data_prop.loc[data_prop.variable == vg, 'variable'] = new_vg
    #
    #     return data_prop
    #
    #
    # def discretize(self, y_bins=None, y_mid=None, display_figure=False, fill_gap=False, fill_extremity=False):
    #     logger.error('Method not implemented yet')
    #     return 'nothing'
    #
    #
    # def set_vertical_reference(profile, h_ref=None, new_v_ref=None, inplace=True):
    #     """
    #
    #     :param profile:
    #     :param h_ref:
    #     :param new_v_ref: default, same as profile origin
    #     :return:
    #     """
    #     logger = logging.getLogger(__name__)
    #     if new_v_ref is None:
    #         if profile.v_ref.unique().__len__() > 1:
    #             logger.error("vertical reference for profile are not consistent")
    #         else:
    #             new_v_ref = profile.v_ref.unique()[0]
    #
    #     if inplace:
    #         new_profile = set_profile_orientation(profile, new_v_ref)
    #     else:
    #         new_profile = set_profile_orientation(profile.copy(), new_v_ref)
    #
    #     if h_ref is not None:
    #         new_df = new_profile['y_low'].apply(lambda x: x - h_ref)
    #         new_df = pd.concat([new_df, new_profile['y_mid'].apply(lambda x: x - h_ref)], axis=1, sort=False)
    #         new_df = pd.concat([new_df, new_profile['y_sup'].apply(lambda x: x - h_ref)], axis=1, sort=False)
    #         new_profile.update(new_df)
    #     return new_profile
    #
    #
    # def set_profile_vertical_reference(profile, h_ref=None, new_v_ref=None, inplace=True):
    #     """
    #
    #     :param profile:
    #     :param h_ref: depth of reference in the new reference system. If the new_reference system is not defined, return an error
    #     :param new_v_ref: default, same as profile origin
    #     :return:
    #     """
    #     logger = logging.getLogger(__name__)
    #     if new_v_ref is None:
    #         if profile.v_ref.unique().__len__() > 1:
    #             logger.error("vertical reference for profile are not consistent")
    #         else:
    #             new_v_ref = profile.v_ref.unique()[0]
    #
    #     if inplace:
    #         new_profile = set_profile_orientation(profile, new_v_ref)
    #     else:
    #         new_profile = set_profile_orientation(profile.copy(), new_v_ref)
    #
    #     if h_ref is not None:
    #         new_df = new_profile['y_low'].apply(lambda x: x - h_ref)
    #         new_df = pd.concat([new_df, new_profile['y_mid'].apply(lambda x: x - h_ref)], axis=1, sort=False)
    #         new_df = pd.concat([new_df, new_profile['y_sup'].apply(lambda x: x - h_ref)], axis=1, sort=False)
    #         new_profile.update(new_df)
    #     if all(new_profile.y_mid.isna()):
    #         new_profile = new_profile.sort_values('y_mid')
    #     else:
    #         new_profile = new_profile.sort_values('y_low')
    #     return new_profile
    #
    #
    # def drop_empty_property(self):
    #     empty = [prop for prop in self.get_property() if self[prop].isnull().all()]
    #     self.variable = ', '.join([prop for prop in self.get_property() if prop not in empty])
    #     self.drop(columns=empty, axis=1, inplace=True)
    #
    #
    # def variables(self, notnan=False):
    #     """
    #     :param notnan: boolean, default False
    #     if True, return only variable with at least one not-nan value
    #     :return:
    #     """
    #     variables = []
    #     for var_group in self.variable.unique():
    #         variables += var_group.split(', ')
    #
    #     # list of unique variables
    #     variables = list(set(variables))
    #
    #     # remove empty variables
    #     if notnan:
    #         for variable in variables:
    #             if variable not in self.columns:
    #                 # remove variable from variables
    #                 for vg in [vg for vg in self.variable.unique() if variable in vg]:
    #                     vg_new = vg.split(', ')
    #                     vg_new.remove(variable)
    #                     self.loc[self.variable == vg, 'variable'] = (', ').join(filter(None, vg_new))
    #                     variables.remove(variable)
    #             elif self[variable].isna().all():
    #                 variables.remove(variable)
    #
    #     if len(variables) == 1 and variables[0] == '':
    #         variables = None
    #
    #     return variables
    #
    #
    # def keep_variable(self, variables2keep):
    #     """
    #
    #     :param variables2keep:
    #     :return:
    #     """
    #     # variables2keep = _variable
    #     if not isinstance(variables2keep, list):
    #         variables2keep = [variables2keep]
    #
    #     # list variables to delete
    #     variables2remove = [var for var in self.variables() if var not in variables2keep]
    #
    #     # delete variables
    #     self.remove_variable(variables2remove)
    #
    #
    # def remove_variable(self, variables2remove):
    #     """
    #     :param variables2del:
    #     :return:
    #     """
    #
    #     # TODO merge with profile.delete_variables
    #     if not isinstance(variables2remove, list):
    #         variables = [variables2remove]
    #     else:
    #         variables = variables2remove
    #
    #     for variable in variables:
    #         if variable in self.variables():
    #             # delete variable column
    #             if variable in self.columns:
    #                 self.drop(variable, axis=1, inplace=True)
    #
    #             # delete associated subvariable column
    #             if variable in pysic.subvariable_dict:
    #                 for subvariable in pysic.subvariable_dict[variable]:
    #                     self.drop(subvariable, axis=1, inplace=True)
    #
    #             # delete variable from variable
    #             for group in self.variable.unique():
    #                 new_group = group.split(', ')
    #                 if variable in new_group:
    #                     while variable in new_group:
    #                         new_group.remove(variable)
    #
    #                     # if the group is empty, remove the row
    #                     if len(new_group) == 0:
    #                         self.drop(self[self.variable == group].index.values, inplace=True)
    #                     else:
    #                         self.loc[self.variable == group, 'variable'] = ', '.join(new_group)
    #
    #     # clean profile by removing empty column
    #     self.clean()
    #
    #
    # def clean(self):
    #     """
    #
    #     :return:
    #     """
    #     # remove all-nan variable
    #     for variable in self.variables():
    #         if self[variable].isna().all():
    #             self.remove_variable(variable)
    #     # clean profile by removing all-nan column
    #     col = [c for c in self.columns if c not in ['y_low', 'y_mid', 'y_sup']]
    #
    #     y_var = [var for var in ['y_low', 'y_mid', 'y_sup'] if var in self.columns]
    #
    #     self = pd.concat([self[y_var], self[col].dropna(axis=1, how='all')], sort=False, axis=1)
    #     return self
    #
    # @property
    # def _constructor(self):
    #     return Profile
    #
    # # DEPRECATED
    # def get_variable(self):
    #     self.logger = logging.getLogger(__name__)
    #     self.logger.warning('get_variable is deprecated. Use get_property')
    #     return self.get_property()
    #
    #
