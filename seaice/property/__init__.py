#! /usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "development"
__date__ = "2017/09/13"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]
__name__ = "property"


state_variable = {'temperature': 'temperature', 'temp': 'temperature', 't': 'temperature',
                     'salinity': 'salinity', 's': 'salinity'}
prop_list = {'brine volume fraction': 'brine volume fraction',
                'vbf': 'brine volume fraction', 'vb': 'brine volume fraction',
                'seaice permeability': 'seaice permeability', 'k': 'seaice permeability'}
prop_unit = {'salinity': '-',
                'temperature': '°C',
                'vb': '-', 'brine volume fraction': '-',
                'seaice permeability': 'm$^{-2}$'}
prop_latex = {'salinity': 'S',
                 'temperature': 'T',
                 'brine volume fraction': '\phi_{B}',
                 'ice thickness': 'h_{i}',
                 'snow thickness': 'h_{s}',
                 'seaice permeability': '\kappa'
                 }

