#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    TODO: fill up
"""

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


__author__ = "Marc Oggier"
__license__ = "GPL"

__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "development"
__date__ = "2017/09/13"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]
__name__ = "property"
#
# __all__ = ["compute_phys_prop_from_core", "scale_profile"]
#
# state_variable = {'temperature': 'temperature', 'temp': 'temperature', 't': 'temperature',
#                   'salinity': 'salinity', 's': 'salinity'}
# prop_list = {'brine volume fraction': 'brine volume fraction',
#              'brine porosity': 'brine porosity',
#              'vbf': 'brine volume fraction', 'vb': 'brine volume fraction',
#              'permeability': 'permeability', 'k': 'permeability',
#              'sea ice permeability': 'permeability'}
# prop_unit = {'salinity': '‰',
#              'temperature': '°C',
#              'vb': '-', 'brine volume fraction': '-',
#              'pysic permeability': 'm$^{-2}$'}
# prop_latex = {'salinity': 'S',
#               'temperature': 'T',
#               'brine volume fraction': '\phi_{B}',
#               'ice thickness': 'h_{i}',
#               'snow thickness': 'h_{s}',
#               'pysic permeability': '\kappa'
#               }
prop_parameter_dict = {'conductivity': ['conductivity measurement temperature']}
prop_associated = {'salinity': ['conductivity', 'specific conductance'], 'texture': ['inclusion', 'description']}
prop_associated_tab = {'salo18': ['conductivity', 'specific conductance', 'dD', 'd_excess'],
                       'tex': ['inclusion', 'description'],
                       'eco': ['phaeo'],
                       'ct': ['conductivity', 'specific conductance', 'dD', 'd_excess'],
                       'seawater': ['conductivity', 'specific conductance', 'dD', 'd_excess'],
                       'snow': ['conductivity', 'specific conductance', 'dD', 'd_excess']}
prop_associated_list = [['d18O', 'dD', 'd_excess'],
                        ['salinity', 'conductivity', 'specific conductance'],
                        ['texture', 'inclusion', 'description']]

#
#
# def scale_profile(profile, h_ice_f):
#     """
#     :param profile:
#         CoreStack profile, ice core profile to scale to a target ice thickness
#     :param h_ice_f:
#         scalar, target ice thickness
#     :return:
#     """
#     profile = profile.copy()
#
#     if profile.length.unique().size == 1 and ~np.isnan(profile.length.unique()[0]):
#         h_ice = profile.length.unique()[0]
#     elif profile.ice_thickness.unique().size and ~np.isnan(profile.ice_thickness.unique()[0]):
#         h_ice = profile.ice_thickness.unique()[0]
#     else:
#         logging.error("Scale: no core length or ice thickness given for %s" % profile.core_name.unique()[0])
#         return 0
#
#     r = h_ice_f / h_ice
#     if r == 1:
#         return profile
#     else:
#         profile.loc[:, ['y_low', 'y_mid', 'y_sup']] = r * profile[['y_low', 'y_mid', 'y_sup']]
#         profile.loc[:, 'length'] = h_ice_f
#         return profile
#
#
# # TODO: add kwarg in arguments
# def compute_phys_prop_from_core(s_profile, t_profile, si_prop, resize_core=False,
#                                 display_figure=True, ice_type='sw'):
#     """
#     :param s_profile:
#     :param t_profile:
#     :param si_prop:
#     :param si_prop_dict: dictionary containing additional data
#     :param si_prop_format: 'linear' or 'step' (default)
#     :param resize_core: 'salinity', 'temperature', 'None' (default)
#     :param attribut_core: 'salinity' (default), 'temperature'
#     :param display_figure:
#     :param ice_type:
#     :return:
#     """
#
#     if not isinstance(si_prop, list):
#         si_prop = [si_prop]
#
#     logger = logging.getLogger(__name__)
#
#     # check parameters
#     if 'salinity' not in s_profile.keys() or not s_profile['salinity'].notnull().any():
#         logger.error("salinity profile does not have salinity data")
#     else:
#         S_core_name = s_profile.name.values[0]
#         s_profile.loc[:, 'salinity'] = pd.to_numeric(s_profile['salinity']).values
#
#     if 'temperature' not in t_profile.keys() or not t_profile['temperature'].notnull().any():
#         logger.error("temperature profile does not have temperature data")
#     else:
#         t_profile.loc[:, 'temperature'] = pd.to_numeric(t_profile['temperature']).values
#
#     # sort profile by y_mid
#     s_profile.sort_values(by='y_mid', inplace=True)
#     t_profile.sort_values(by='y_mid', inplace=True)
#
#     # check if orientation have same direction:
#     if s_profile.v_ref.unique() != t_profile.v_ref.unique():
#         if not s_profile.ice_thickness.empty:
#             hi = s_profile.ice_thickness.unique()[0]
#
#             # if hi is not present in t_profile, interp temperature at hi
#             if not np.isin(hi, t_profile.y_mid):
#                 t_temp = t_profile.head(1).reset_index()
#                 t_temp.temperature = np.nan
#                 t_temp.y_mid = hi
#                 t_profile = t_profile.append(t_temp).sort_values('y_mid').reset_index(drop=True)
#                 t_profile = t_profile.interpolate(method='linear', axis=0, sort=True)
#
#             # discard all temperature data longer than salinity core
#             t_profile = t_profile[t_profile.y_mid <= hi]
#             t_profile.ice_thickness = t_profile.y_mid.max()
#
#             # change direction of t_profile to match s_profile
#             direction = s_profile.v_ref.unique()[0]
#             t_profile = pysic.core.profile.set_profile_orientation(t_profile, direction)
#
#         else:
#             logger.error("%s has no ice thickness; impossible to correct direction", s_profile.name.unique())
#
#     if resize_core in ['salinity']:
#         if s_profile.length.notnull().all():
#             profile_length = s_profile.length.unique()[0]
#         elif s_profile.ice_thickness.notnull().all():
#             profile_length = s_profile.ice_thickness.unique()[0]
#             print("%s: ice core length unknown, using ice thickness instead" % S_core_name)
#         else:
#             profile_length = max(s_profile.y_low.min(), s_profile.y_sup.max())
#             print("todo: need warning text")
#         if not t_profile.length.unique() == profile_length:
#             t_profile = scale_profile(t_profile, profile_length)
#         keep_index = True
#     elif resize_core in ['temperature']:
#         if t_profile.length.notnull().all():
#             profile_length = t_profile.length.unique()[0]
#         elif t_profile.ice_thickness.notnull().all():
#             profile_length = t_profile.ice_thickness.unique()[0]
#             print("ice core length unknown, using ice thickness instead")
#         else:
#             profile_length = max(t_profile.y_low.min(), t_profile.y_sup.max())
#             print("todo: need warning text")
#         if not t_profile.length.unique() == profile_length:
#             s_profile = scale_profile(s_profile, profile_length)
#     elif resize_core is False:
#         keep_index = True
#
#     # interpolate temperature profile to match salinity profile
#     y_mid = s_profile.y_mid.dropna().values
#     if y_mid.__len__() < 1:
#         y_mid = (s_profile.y_low / 2. + s_profile.y_sup / 2).dropna().astype(float)
#
#     if 'temperature' in s_profile.keys():
#         s_profile = s_profile.drop('temperature', axis=1)
#
#     # replace the 2 following lines
#     t_profile = t_profile.sort_values(by='y_mid')
#     interp_data = np.interp(y_mid, t_profile['y_mid'].values, t_profile['temperature'].values, left=np.nan, right=np.nan)
#
#     if keep_index:
#         t_profile2 = pd.DataFrame(np.transpose([interp_data, y_mid]), columns=['temperature', 'y_mid'], index=s_profile.index)
#         s_profile = s_profile.join(t_profile2.temperature, how='outer')
#     else:
#         t_profile2 = pd.DataFrame(np.transpose([interp_data]), columns=['temperature', 'y_mid'])
#         s_profile = pd.merge(s_profile, t_profile2, on=['y_mid'])
#
#     # add name of t_profile
#     s_profile['t_name'] = t_profile.get_name()[0]
#
#     # compute properties
#     for f_prop in si_prop:
#         if f_prop not in prop_list.keys():
#             print('property %s not defined in the ice core property module' % property)
#
#         prop = prop_list[f_prop]
#         if ice_type is 'nacl':
#             function = getattr(pysic.property.nacl_ice, prop.replace(" ", "_"))
#             #TODO: check if prop exist, if prop does not exist use si
#         else:
#             function = getattr(pysic.property.si, prop.replace(" ", "_"))
#
#         # TODO: WIKI always add to salinity, properties is always a step
#         s_profile[f_prop] = function(np.array(s_profile['salinity']), np.array(s_profile['temperature']))
#
#         # update variable:
#         new_var = s_profile.get_variable() + ['temperature', f_prop]
#         new_var = list(set(new_var))
#         s_profile['variable'] = ', '.join(new_var)
#
#         if display_figure:
#             ax = pysic.core.plot.plot_profile_variable(s_profile.copy(), variable_dict={'variable': prop},
#                                                         ax=None, param_dict=None)
#             ax.set_xlabel(prop)
#             ax.set_ylabel('ice thickness)')
#             ax.set_title(S_core_name)
#             plt.show()
#     # TODO: replace corestack by profile, REQUIRE: Profile should inherit Profile property (@property _constructor)
#     return s_profile
#
#
# def compute_phys_prop_from_core_STrho(s_profile, t_profile, d_profile, si_prop, resize_core=False,
#                                       display_figure=True, ice_type='sw'):
#     """
#     :param s_profile:
#     :param t_profile:
#     :param d_profile:
#     :param si_prop:
#     :param si_prop_dict: dictionary containing additional data
#     :param si_prop_format: 'linear' or 'step' (default)
#     :param resize_core: 'S', 'T', 'None' (default)
#     :param attribut_core: 'salinity' (default), 'temperature'
#     :param display_figure:
#     :param ice_type:
#     :return:
#     """
#
#     if not isinstance(si_prop, list):
#         si_prop = [si_prop]
#
#     logger = logging.getLogger(__name__)
#
#     # check parameters
#     if 'salinity' not in s_profile.keys() or not s_profile['salinity'].notnull().any():
#         logger.error("salinity profile does not have salinity data")
#     else:
#         S_core_name = s_profile.name.values[0]
#         s_profile.loc[:, 'salinity'] = pd.to_numeric(s_profile['salinity']).values
#
#     if 'temperature' not in t_profile.keys() or not t_profile['temperature'].notnull().any():
#         logger.error("temperature profile does not have temperature data")
#     else:
#         t_profile.loc[:, 'temperature'] = pd.to_numeric(t_profile['temperature']).values
#
#     if 'density' not in d_profile.keys() or not d_profile['density'].notnull().any():
#         D_core_name = d_profile.name.values[0]
#         logger.error(str("%s: density profile does not have density data" % D_core_name))
#     else:
#         d_profile.loc[:, 'density'] = pd.to_numeric(d_profile['density']).values
#
#     # sort profile by y_mid
#     s_profile.sort_values(by='y_mid', inplace=True)
#     t_profile.sort_values(by='y_mid', inplace=True)
#     d_profile.sort_values(by='y_mid', inplace=True)
#
#     # check if profiles have same orientation
#     if s_profile.v_ref.unique() != t_profile.v_ref.unique():
#         v_ref = s_profile.v_ref.unique()[0]
#         t_profile = t_profile.set_orientation(v_ref)
#
#     if s_profile.v_ref.unique() != d_profile.v_ref.unique():
#         v_ref = s_profile.v_ref.unique()[0]
#         d_profile = d_profile.set_orientation(v_ref)
#
#     if resize_core in ['salinity']:
#         if s_profile.length.notnull().all():
#             profile_length = s_profile.length.unique()[0]
#         elif s_profile.ice_thickness.notnull().all():
#             profile_length = s_profile.ice_thickness.unique()[0]
#             S_core_name = s_profile.name.unique()[0]
#             print(str("%s: ice core length unknown, using ice thickness instead" %S_core_name))
#         else:
#             profile_length = max(s_profile.y_low.min(), s_profile.y_sup.max())
#             print("todo: need warning text")
#         if not t_profile.length.unique() == profile_length:
#             t_profile = scale_profile(t_profile, profile_length)
#             d_profile = scale_profile(d_profile, profile_length)
#         keep_index = True
#     elif resize_core in ['temperature']:
#         if t_profile.length.notnull().all():
#             profile_length = t_profile.length.unique()[0]
#         elif t_profile.ice_thickness.notnull().all():
#             profile_length = t_profile.ice_thickness.unique()[0]
#             print("ice core length unknown, using ice thickness instead")
#         else:
#             profile_length = max(t_profile.y_low.min(), t_profile.y_sup.max())
#             print("todo: need warning text")
#         if not t_profile.length.unique() == profile_length:
#             s_profile = scale_profile(s_profile, profile_length)
#             d_profile = scale_profile(d_profile, profile_length)
#     elif resize_core in ['density']:
#         if d_profile.length.notnull().all():
#             profile_length = d_profile.length.unique()[0]
#         elif d_profile.ice_thickness.notnull().all():
#             profile_length = d_profile.ice_thickness.unique()[0]
#             print("ice core length unknown, using ice thickness instead")
#         else:
#             profile_length = max(d_profile.y_low.min(), d_profile.y_sup.max())
#             print("todo: need warning text")
#         if not d_profile.length.unique() == profile_length:
#             s_profile = scale_profile(s_profile, profile_length)
#             t_profile = scale_profile(t_profile, profile_length)
#     elif resize_core is False:
#         keep_index = True
#
#     # interpolate temperature profile to match salinity profile
#     y_mid = s_profile.y_mid.dropna().values
#     if y_mid.__len__() < 1:
#         y_mid = (s_profile.y_low / 2. + s_profile.y_sup / 2).dropna().astype(float)
#
#     if 'temperature' in s_profile.keys():
#         s_profile = s_profile.drop('temperature', axis=1)
#
#     # replace the 2 following lines
#     t_profile = t_profile.sort_values(by='y_mid')
#     interp_data = np.interp(y_mid, t_profile['y_mid'].values, t_profile['temperature'].values, left=np.nan, right=np.nan)
#
#     # Discretize density core according to salinity sections:
#     y_bins = np.unique(s_profile.y_low.to_list() + s_profile.y_sup.to_list())
#     d_profile_d = pysic.core.profile.discretize_profile(d_profile, y_bins)
#     # TODO check density sections correspond to salinity section
#
#     if keep_index:
#         t_profile2 = pd.DataFrame(np.transpose([interp_data, y_mid]), columns=['temperature', 'y_mid'], index=s_profile.index)
#         s_profile = s_profile.join(t_profile2.temperature, how='outer')
#         d_profile_d = pd.DataFrame(np.transpose([d_profile_d.density, y_mid]), columns=['density', 'y_mid'], index=s_profile.index)
#         s_profile = s_profile.join(d_profile_d.density, how='outer')
#     else:
#         t_profile2 = pd.DataFrame(np.transpose([interp_data, y_mid]), columns=['temperature', 'y_mid'])
#         s_profile = pd.merge(s_profile, t_profile2, on=['y_mid'])
#         s_profile = pd.merge(s_profile, d_profile, on=['y_mid'])
#         d_profile_d = pd.DataFrame(np.transpose([d_profile_d.density, y_mid]), columns=['density', 'y_mid'])
#         d_profile = pd.merge(s_profile, d_profile_d, on=['y_mid'])
#
#     # add name of t_profile
#     s_profile['t_name'] = t_profile.get_name()[0]
#     s_profile['d_name'] = d_profile.get_name()[0]
#
#     # compute properties
#     for f_prop in si_prop:
#         if f_prop not in prop_list.keys():
#             print('property %s not defined in the ice core property module' % property)
#
#         prop = prop_list[f_prop]
#         if ice_type is 'nacl':
#             function = getattr(pysic.property.nacl_ice, prop.replace(" ", "_"))
#             #TODO: check if prop exist, if prop does not exist use si
#         else:
#             function = getattr(pysic.property.si, prop.replace(" ", "_"))
#
#         # TODO: WIKI always add to salinity, properties is always a step
#         s_profile[f_prop] = function(np.array(s_profile['salinity']),
#                                      np.array(s_profile['temperature']),
#                                      np.array(s_profile['density']))
#
#         # update variable:
#         new_var = s_profile.get_variable() + ['temperature', 'density', f_prop]
#         new_var = list(set(new_var))
#         s_profile['variable'] = ', '.join(new_var)
#
#         if display_figure:
#             ax = pysic.core.plot.plot_profile_variable(s_profile.copy(), variable_dict={'variable': prop},
#                                                         ax=None, param_dict=None)
#             ax.set_xlabel(prop)
#             ax.set_ylabel('ice thickness)')
#             ax.set_title(S_core_name)
#             plt.show()
#     # TODO: replace corestack by profile, REQUIRE: Profile should inherit Profile property (@property _constructor)
#     return s_profile
#
#
# def compute_phys_prop_from_core_name(ics_stack, S_core_name, T_core_name, si_prop, si_prop_format='step',
#                                      resize_core=None, attribut_core='S', inplace=True, display_figure=False):
#     """
#     :param ics_stack:
#     :param S_core_name:
#     :param T_core_name:
#     :param si_prop:
#     :param si_prop_format: 'linear' or 'step':
#     :param resize_core: 'S', 'T', default 'None':
#     :param display_figure:
#     :param inplace:
#     :return:
#     """
#
#     # check parameters
#     if S_core_name not in ics_stack.name.unique():
#         print("%s core not present in data" % S_core_name)
#         return pd.DataFrame();
#     elif 'salinity' not in ics_stack.loc[ics_stack.name == S_core_name, 'variable'].unique():
#         print("salinity data not existing for %s " % S_core_name)
#         return pd.DataFrame();
#     else:
#         s_profile = ics_stack[(ics_stack.name == S_core_name) & (ics_stack.variable == 'salinity')]
#
#     if T_core_name not in ics_stack.name.unique():
#         print("%s core not present in data" % T_core_name)
#         return pd.DataFrame();
#     elif 'temperature' not in ics_stack.loc[ics_stack.name == T_core_name, 'variable'].unique():
#         print("temperature data not existing for %s " % T_core_name)
#         return pd.DataFrame();
#     else:
#         t_profile = ics_stack[(ics_stack.name == T_core_name) & (ics_stack.variable == 'temperature')]
#
#     prop_profile = compute_phys_prop_from_core(s_profile, t_profile, si_prop=si_prop,
#                                                si_prop_format=si_prop_format, resize_core=resize_core,
#                                                display_figure=display_figure, attribut_core=attribut_core)
#
#     if inplace is True:
#         for f_prop in prop_profile.variable.unique():
#             if not ics_stack[(ics_stack.name == S_core_name) & (ics_stack.variable == f_prop)].empty:
#                 ics_stack = ics_stack[(ics_stack.name != S_core_name) | (ics_stack.variable != f_prop)]
#             ics_stack = ics_stack.append(prop_profile, ignore_index=True)
#         return pysic.core.corestack.CoreStack(ics_stack)
#     else:
#         return prop_profile
#
