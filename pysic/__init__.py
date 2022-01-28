#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    pysic is a module to handle sea ice core data
"""

__author__ = "Marc Oggier"
__license__ = "GPL"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "development"
__date__ = "2017/09/13"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]
__name__ = "pysic"

from .__version__ import __version__

import logging
import numpy as np
#import pysic.core.corestack
import pysic.core.Core
#import pysic.core.plot
import pysic.core.Profile
import pysic.property
#import pysic.visualization.plot

#import pysic.property.brine
#import pysic.property.ice
#import pysic.property.si
#import pysic.property.sw
#import pysic.property.nacl_ice

TOL = 1e-6
subvariable_dict = {'conductivity': ['conductivity measurement temperature']}

# TODO: add test function
# TODO: add function Core.check() to check the integrity of the ice core and profiles


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
        elif isinstance(v, dict):
            for _v in v:
                revdict[_v] = k
        else:
            revdict.setdefault(v, k)

    return revdict