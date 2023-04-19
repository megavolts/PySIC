#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    pysic.core.core.py : toolbox to work on sea ice core data
"""

import numpy as np
import logging as logging

from pysic.core.profile import Profile

__CoreVersion__ = "1.4.9"
__comment__ = "core.py contains class Core() to store an sea ice core, and a collection of functions to handle ice core" \
              "data"

logger = logging.getLogger(__name__)

# TODO: add test function
# TODO: add function Core.check() to check the integrity of the ice core and profiles

class Core:
    def __init__(self, name, date, origin=np.nan, lat=np.nan, lon=np.nan, length=np.nan, ice_thickness=np.nan, freeboard=np.nan,
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
        self.length = length
        self.collection = [name]
        self.comment = None
        self.profile = Profile()
        self.t_air = np.nan
        self.t_snow_surface = np.nan
        self.t_ice_surface = np.nan
        self.t_water = np.nan
        self.s_water = np.nan
        self.instrument = {}
        self.reference = {}
        self.protocol = None
        self.unit = {}
        self.par_incoming = np.nan
        self.par_transmitted = np.nan
    # @property
    # def ice_thickness(self):
    #     return self._ice_thickness
    #
    # @property
    # def snow_depth(self):
    #     return self._snow_depth
    #
    # @snow_depth.setter
    # def snow_depth(self, value):
    #     value = np.array(value)
    #     if value.size == 1:
    #         try:
    #             self._snow_depth.append(value)
    #         except AttributeError:
    #             self._snow_depth = [value]
    #     else:
    #         for v_ in value:
    #             try:
    #                 self._snow_depth = np.concatenate((self.snow_depth, np.array([v_])))
    #             except AttributeError:
    #                 self._snow_depth = np.array([v_])
    #
    # @ice_thickness.setter
    # def ice_thickness(self, value):
    #     value = np.array(value)
    #     if value.size == 1:
    #         try:
    #             self._ice_thickness.append(value)
    #         except AttributeError:
    #             self._ice_thickness = value
    #     else:
    #         for v_ in value:
    #             try:
    #                 self._ice_thickness.append(v_)
    #             except AttributeError:
    #                 self._ice_thickness = [v_]
    #
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
    #
    # def remove_core(self, core):
    #     """
    #     :param core:
    #         string, core to remove from the collection
    #     :return:
    #     """
    #     self.del_from_collection(core)
    #     self.del_profile(core)
    #
    # def del_from_collection(self, core_list):
    #     """
    #     :param core_list: string, list of string
    #     :return:
    #     """
    #     if isinstance(core_list, list):
    #         for core in core_list:
    #             if core in self.collection:
    #                 self.collection.remove(core)
    #     else:
    #         if core_list in self.collection:
    #             self.collection.remove(core_list)
    #     self.collection = sorted(self.collection)

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

    #
    # def del_variable(self, variable):
    #     """
    #     :param variable:
    #         str, variable to delete
    #     :return:
    #     """
    #     self.variables.remove(variable)
    #     self.profile = self.profile[~self.profile.variable.str.contains(variable)]
    #
    # def del_profile(self, core):
    #     """
    #     Delete all profile belonging to the core CORE
    #     :param core:
    #         string, name of the core to delete the profile
    #     :return:
    #     """
    #     self.profile = self.profile[~self.profile.name.str.contains(core)]

    # def get_variables(self, variable):
    #     """
    #     :param variable:
    #     :return:
    #     """
    #     if variable in inverse_dict(subvariable_dict):
    #         sup_variable = inverse_dict(subvariable_dict)[variable]
    #         group = [group for group in self.profile.variable.unique() if sup_variable in group][0]
    #         data = self.profile[self.profile.variable == group].copy()
    #         del_variable = [var for var in group.split(', ') if not var == variable]
    #         del_variable += [subvar for var in del_variable if var in subvariable_dict
    #                          for subvar in subvariable_dict[var] if not subvar == variable]
    #     elif variable in self.variables():
    #         group = [group for group in self.profile.variable.unique() if variable in group][0]
    #         data = self.profile[self.profile.variable == group].copy()
    #         del_variable = [var for var in group.split(', ') if not var == variable]
    #         del_variable += [subvar for var in del_variable if var in subvariable_dict for subvar in subvariable_dict[var]]
    #
    #     del_keys = list(set([key for key in data.columns[data.isna().all()].tolist() if key is not variable]))
    #     data = data.drop(axis=1, labels=del_keys)
    #     data['variable'] = variable
    #     return data
    #
    # def summary(self):
    #     """
    #     :return:
    #     """
    #     print("#---------------------------------------------------------------#")
    #     print("# SUMMARY FOR ICE CORE : %s" % self.name)
    #     print("#---------------------------------------------------------------#")
    #     print('date:\t %s' % self.date.strftime('%y-%b-%d %H:%S (UTC%z)'))
    #     print('ice thickness\t\th_i = %.2f m' % self.ice_thickness[0])
    #     if self.ice_thickness.__len__() > 1:
    #         print('\t\t\taverage\t\t   %.2f ± %.2f m (n = %d)' % (self.ice_thickness.mean(), self.ice_thickness.mean(),
    #                                                               self.ice_thickness.__len__()))
    #     if self.length.__len__() > 1:
    #         print('average ice core length\th_c = %.2f ± %.2f m (n = %d)' % (self.length.mean(), self.length.mean(),
    #                                                                          self.length.__len__()))
    #     elif self.snow_depth.__len__() == 1:
    #         print('ice core length\t\th_c = %.2f m' % self.length.mean())
    #
    #     print('freeboard\t\t\th_f = %.2f m' % self.freeboard[0])
    #     if self.freeboard.__len__() > 1:
    #         print('\t\t\taverage\t\t   %.2f ± %.2f m (n = %d)' % (self.freeboard.mean(), self.freeboard.mean(),
    #                                                               self.freeboard.__len__()))
    #     if self.snow_depth.__len__() > 1:
    #         print('average snow depth\th_s = %.2f ± %.2f m (n = %d)' % (self.snow_depth.mean(), self.snow_depth.mean(),
    #                                                                     self.snow_depth.__len__()))
    #     elif self.snow_depth.__len__() == 1:
    #         print('snow depth\t\t\th_s = %.2f m' % self.snow_depth.mean())
    #
    #     print('variables:')
    #     if self.variables is not None:
    #         for variable in self.variables:
    #             print('\t%s' % variable)
    #     else:
    #         print('\tNO VARIABLE')
    #
    #     print('comment: %s' % self.comment)
    #
    def add_profile(self, profile, unit=None):
        """
        Add new profile to core.
        Profile name should match core name
        :param profile:
            pd.DataFrame, profile to add
        :param unit:
            dict, profile units
        """
        if self.profile.empty:
            self.profile = profile
        else:
            self.profile = self.profile.add(profile)

    @property
    def variable(self):
        return self.profile.variable

    # def variables(self):
    #     return self.profile.get_property()


# class Station:
#     import datetime as dt
#
#     def __init__(self, name, date, lat, long, date_end=dt.date(), lat_end=np.nan, lon_end=np.nan, *args, **kwargs):
#         self.name = name
#         self.date = date
#         self.lat = lat
#         self.lon = long
#         self.date_end = date_end
#         self.lat_end = lat_end
#         self.lon_end = lon_end
#
#     pass
