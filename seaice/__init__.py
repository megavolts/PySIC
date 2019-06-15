#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    seaice is a module to handle sea ice core data
"""

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "development"
__date__ = "2017/09/13"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]
__name__ = "seaice"

import logging
import numpy as np
import seaice.core.corestack
import seaice.core.plot
import seaice.core.profile
import seaice.property

import seaice.property.brine
import seaice.property.ice
import seaice.property.si
import seaice.property.sw
import seaice.property.nacl_ice

TOL = 1e-6
subvariable_dict = {'conductivity': ['conductivity measurement temperature']}


# TODO: add function Core.check() to check the integrity of the ice core and profiles

class Core():
    """
    Core
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

    def __init__(self, name, date, origin=np.nan, lat=np.nan, lon=np.nan, ice_thickness=np.nan, freeboard=np.nan,
                 snow_depth=np.nan, *args, **kwargs):
        super(Core, self).__init__(*args, **kwargs)

        """
        :param name:
            string, name of the ice core
        :param date:
            datetime.datetime, date of coring YYYY-mm-dd hh:mm
        :param origin:
            string, location name of the sampling
        :param lat:
            float, latitude of sampling
        :param lon:
            float, longitude of sampling
        :param ice_thickness:
            np.array, ice thickness as measured in the core hole, following elements are ice thickness
            measured in the vicinity of the core hole.
        :param snow_depth:
            np.array, ice thickness measured at the location of coring
        :return:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug('(%s) instance of Core created' % name)
        self.name = name
        self.date = date
        self.origin = origin
        self.lat = lat
        self.lon = lon
        self.snow_depth = snow_depth
        self.freeboard = freeboard
        self.ice_thickness = ice_thickness
        self.collection = [name]
        self.comment = None
        self.profile = seaice.core.profile.Profile()
        self.t_air = np.nan
        self.t_snow_surface = np.nan
        self.t_ice_surface = np.nan
        self.t_water = np.nan
        self.protocol = None

    def add_to_collection(self, core_list):
        """
        :param core_list:
        :return:
        """
        if isinstance(core_list, list):
            for core in core_list:
                if core not in self.collection:
                    self.collection.append(core)
        else:
            if core_list not in self.collection:
                self.collection.append(core_list)
        self.collection = sorted(self.collection)

    def remove_core(self, core):
        """
        :param core:
            string, core to remove from the collection
        :return:
        """
        self.del_from_collection(core)
        self.del_profile(core)

    def del_from_collection(self, core_list):
        """
        :param core_list: string, list of string
        :return:
        """
        if isinstance(core_list, list):
            for core in core_list:
                if core in self.collection:
                    self.collection.remove(core)
        else:
            if core_list in self.collection:
                self.collection.remove(core_list)
        self.collection = sorted(self.collection)

    def add_comment(self, comment):
        """
        :param comment:
        :return:
        """
        if comment is not None:
            if self.comment is None:
                self.comment = comment
            # add comment only if the comment is different to any other comment
            elif comment not in self.comment.split('; '):
                self.comment += '; ' + comment

    def length(self):
        if 'length' in self.profile:
            return self.profile.length.unique()
        else:
            return np.array([]).astype(str)

    def variables(self):
        variables = []
        if 'variable' in self.profile:
            for group in self.profile.variable.unique():
                for variable in group.split(', '):
                    if variable not in variables:
                        variables += [variable]
            return variables
        else:
            return []

    def del_variable(self, variable):
        """
        :param variable:
            str, variable to delete
        :return:
        """
        self.variables.remove(variable)
        self.profile = self.profile[~self.profile.variable.str.contains(variable)]

    def del_profile(self, core):
        """
        Delete all profile belonging to the core CORE
        :param core:
            string, name of the core to delete the profile
        :return:
        """
        self.profile = self.profile[~self.profile.name.str.contains(core)]

    def get_variables(self, variable):
        """
        :param variable:
        :return:
        """
        if variable in inverse_dict(subvariable_dict):
            sup_variable = inverse_dict(subvariable_dict)[variable]
            group = [group for group in self.profile.variable.unique() if sup_variable in group][0]
            data = self.profile[self.profile.variable == group].copy()
            del_variable = [var for var in group.split(', ') if not var == variable]
            del_variable += [subvar for var in del_variable if var in subvariable_dict
                             for subvar in subvariable_dict[var] if not subvar == variable]
        elif variable in self.variables():
            group = [group for group in self.profile.variable.unique() if variable in group][0]
            data = self.profile[self.profile.variable == group].copy()
            del_variable = [var for var in group.split(', ') if not var == variable]
            del_variable += [subvar for var in del_variable if var in subvariable_dict for subvar in subvariable_dict[var]]

        del_keys = list(set([key for key in data.columns[data.isna().all()].tolist() if key is not variable]))
        data = data.drop(axis=1, labels=del_keys)
        data['variable'] = variable
        return data

    def summary(self):
        """
        :return:
        """
        print("#---------------------------------------------------------------#")
        print("# SUMMARY FOR ICE CORE : %s" % self.name)
        print("#---------------------------------------------------------------#")
        print('date:\t %s' % self.date.strftime('%y-%b-%d %H:%S (UTC%z)'))
        print('ice thickness\t\th_i = %.2f m' % self.ice_thickness[0])
        if self.ice_thickness.__len__() > 1:
            print('\t\t\taverage\t\t   %.2f ± %.2f m (n = %d)' % (self.ice_thickness.mean(), self.ice_thickness.mean(),
                                                                  self.ice_thickness.__len__()))
        if self.length.__len__() > 1:
            print('average ice core length\th_c = %.2f ± %.2f m (n = %d)' % (self.length.mean(), self.length.mean(),
                                                                             self.length.__len__()))
        elif self.snow_depth.__len__() == 1:
            print('ice core length\t\th_c = %.2f m' % self.length.mean())

        print('freeboard\t\t\th_f = %.2f m' % self.freeboard[0])
        if self.freeboard.__len__() > 1:
            print('\t\t\taverage\t\t   %.2f ± %.2f m (n = %d)' % (self.freeboard.mean(), self.freeboard.mean(),
                                                                  self.freeboard.__len__()))
        if self.snow_depth.__len__() > 1:
            print('average snow depth\th_s = %.2f ± %.2f m (n = %d)' % (self.snow_depth.mean(), self.snow_depth.mean(),
                                                                        self.snow_depth.__len__()))
        elif self.snow_depth.__len__() == 1:
            print('snow depth\t\t\th_s = %.2f m' % self.snow_depth.mean())

        print('variables:')
        if self.variables is not None:
            for variable in self.variables:
                print('\t%s' % variable)
        else:
            print('\tNO VARIABLE')

        print('comment: %s' % self.comment)

    def add_snow_depth(self, snow_depth):
        """
        :param snow_depth:
        :return:
        """
        self.snow_depth = np.concatenate(self.snow_depth, [snow_depth])

    def add_profile(self, profile):
        """
        Add new profile to core.
        Profile name should match core name
        :param profile:
            pd.DataFrame, profile to add
        """
        if self.profile.empty:
            self.profile = profile
        else:
            self.profile = self.profile.add_profile(profile)

    def get_property(self):
        return self.profile.get_property()

    # property
    def ice_thickenss(self):
        """
            return the average ice thickenss
        :return:
        """
        if 'ice_thickenss' in self.profile:
            return np.nanmean(self.profile.length.unique())
        else:
            return np.array([]).astype(str)

# class ProfileV0(pd.DataFrame):

#
#     def delete_variable(self, variable):
#         new_variables = self.get_variable()
#         if variable in self.get_variable():
#             print(variable)
#             self.drop(variable, axis=1, inplace=True)
#             new_variables.remove(variable)
#             if variable in subvariable_dict.keys():
#                 for _subvar in subvariable_dict[variable]:
#                     self.drop(_subvar, axis=1, inplace=True)
#
#                 # write variable
#         self['variable'] = ', '.join(new_variables)
# #
#     def delete_variables(self, variables):
#         if not isinstance(variables, list):
#             variables = [variables]
#
#         new_variables = self.get_variable()
#         for variable in variables:
#             if variable in self.get_variable():
#                 print(variable)
#                 self.drop(variable, axis=1, inplace=True)
#                 new_variables.remove(variable)
#                 if variable in subvariable_dict.keys():
#                     for _subvar in subvariable_dict[variable]:
#                         self.drop(_subvar, axis=1, inplace=True)
#
#                 # write variable
#         self['variable'] = ', '.join(new_variables)
#
#     def select_variable(self, variables):
#         select_data = pd.DataFrame()
#         if not isinstance(variables, list):
#             variables = [variables]
#         for variable in variables:
#             for group in self.variable.unique():
#                 if variable in group.split(', '):
#                     data = self[self.variable == group]
#                     # check if other variable should be conserved:
#                     del_var = [_var for _var in data.get_variable() if _var not in variables]
#                     data.delete_variable(del_var)
#                     data.clean()
#                     variables.remove(variable)
#                     select_data = select_data.append(data)


def inverse_dict(map):
    """
    return the inverse of a dictionnary with non-unique values
    :param map: dictionnary
    :return inv_map: dictionnary
    """
    revdict = {}
    for k, v in map.items():
        if isinstance(v, list):
            for _v in v:
                revdict.setdefault(_v, k)
        else:
            revdict.setdefault(v, k)
    return revdict