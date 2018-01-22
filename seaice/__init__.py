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
import pandas as pd

from seaice.io.icxl import *
from seaice.core.corestack import *
import seaice.core.plot
# import seaice.core.tool
# import seaice.core.plot
# import seaice.climatology
# import seaice.property.brine


TOL = 1e-6


class Core:
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
                 snow_depth=np.nan):
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
        self.length = np.array([])
        self.collection = [name]
        self.comment = None
        self.profile = pd.DataFrame([])
        self.t_air = np.nan
        self.t_snow_surface = np.nan
        self.t_ice_surface = np.nan
        self.t_water = np.nan
        self.protocol = None
        self.variables = None

    def add_length(self, length):
        """
        :param length:
        :return:
        """
        self.length = np.concatenate((self.length, [length]))

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

    def add_variable(self, variable):
        """
        :param variable:
        :return:
        """
        if self.variables is None:
            self.variables = [variable]
        elif variable not in self.variables:
            self.variables.append(variable)

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
        :param profile:
            pd.DataFrame, profile to add
        :return:
        """
        self.profile = self.profile.append(profile)
        self.profile.reset_index(inplace=True, drop=True)
        #
        # def plot_variables(self, variables=None, ax=None, param_dict=None):
        #     """
        #     :param ax:
        #     :param variables:
        #     :param param_dict:
        #     :return:
        #     """
        #     # check variables :
        #     if variables is None:
        #         variables = self.variables
        #     if not isinstance(variables, list):
        #         variables = [variables]
        #
        #     if ax is None:
        #         ax = [plt.subplot(1, variables.__len__(), ii) for ii in range(1, variables.__len__()+1)]
        #     elif not ax.__len__() == variables.__len__():
        #         module_logger.error("lenght of ax and variables should be identical")
        #
        #     plt.figure()
        #     n_ax = 0
        #     #TODO : automate color splitting according to the number of variable
        #     variable_color = ['r', 'b', 'g']
        #     for variable in variables:
        #         profile = self.profile[self.profile.variable == variable]
        #         if param_dict is None or 'color' not in param_dict:
        #             param_dict = {'color':variable_color[n_ax]}
        #         plot_profile(profile, ax=ax[n_ax], param_dict=param_dict)
        #         n_ax += 1
        #     return ax

        # # def calc_prop(self, property):
        # #     """
        # #     :param property:
        # #     :return:
        # #     """
        # #     # check properties variables
        # #     if property not in si_prop_list.keys():
        # #         logging.warning('property %s not defined in the ice core property module' % property)
        # #         return None
        # #     elif 'salinity' not in self.profiles:
        # #         logging.warning('ice core %s is missing salinity profile for further calculation' % self.name)
        # #         return None
        # #     elif 'temperature' not in self.profiles:
        # #         logging.warning('ice core %s is missing temperature profile for further calculation' % self.name)
        # #         return None
        # #     else:
        # #         import seaice.properties
        # #         variable = si_prop_list[property]
        # #         function = getattr(seaice.properties, variable.replace(" ", "_"))
        # #         profilet = self.profiles['temperature']
        # #         profiles = self.profiles['salinity']
        # #         y = np.sort(np.unique(np.concatenate((profilet.y, profiles.y))))
        # #         y = y[np.where(y <= max(max(profilet.y), max(profiles.y)))]
        # #         y = y[np.where(y >= max(min(profilet.y), min(profiles.y)))]
        # #         y_mid = y[0:-1] + np.diff(y) / 2
        # #         length = max(y) - min(y)
        # #
        # #         xt = np.interp(y_mid, profilet.y, profilet.x, left=np.nan, right=np.nan)
        # #         xs = np.interp(y_mid, profiles.y[:-1] + np.diff(profiles.y) / 2, profiles.x, left=np.nan, right=np.nan)
        # #         x = function(xt, xs)
        # #
        # #         note = 'computed from ' + self.profiles['temperature'].profile_label + ' temperature profile and ' + \
        # #                self.profiles['salinity'].profile_label + ' salinity profile'
        # #         profile_label = self.name
        # #         prop_profile = Profile(x, y, profile_label, variable, comment=None, note=note, length=length)
        # #         self.add_profile(prop_profile, variable)
        # #         self.add_comment('computed %s' % variable)

        # def plot_state_variable(self, flag_figure_number=None, param_dict=None):
        #     """
        #     :param flag_figure_number:
        #     :param param_dict:
        #     :return:
        #     """
        #     if flag_figure_number is None:
        #         fig = plt.figure()
        #         ax1 = fig.add_subplot(1, 2, 1)
        #         ax2 = fig.add_subplot(1, 2, 2, sharey=ax1)
        #     else:
        #         fig = plt.figure(flag_figure_number)
        #         ax1 = fig.add_subplot(1, 2, 1)
        #         ax2 = fig.add_subplot(1, 2, 2, sharey=ax1)
        #
        #     if 'salinity' in self.profiles.keys():
        #         self.plot_variable(ax1, 'salinity', param_dict)
        #         ax1.set_ylabel('depth [m]')
        #     else:
        #         logging.warning('salinity profile missing for %s' % self.name)
        #
        #     if 'temperature' in self.profiles.keys():
        #         self.plot_variable(ax2, 'temperature', param_dict)
        #     else:
        #         logging.warning('temperature profile missing for %s' % self.name)
        #
        #     ax_fig = [ax1, ax2]
        #     return fig, ax_fig
        #
        # def get_profile_variable(self):
        #     return sorted(self.profiles.keys())
        #
        # def rescale(self, variable=None, section_thickness=0.05):
        #     return make_section(self, variable, section_thickness)
