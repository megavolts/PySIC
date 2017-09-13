#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property/ice.py contains function to compute physical property relative to pure water ice
"""

import warnings

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

warnings.filterwarnings('ignore')

si_state_variable = {'temperature': 'temperature', 'temp': 'temperature', 't': 'temperature',
                     'salinity': 'salinity', 's': 'salinity'}
si_prop_list = {'brine volume fraction': 'brine volume fraction', 'brine volume fraction': 'brine volume fraction',
                'vbf': 'brine volume fraction', 'vb': 'brine volume fraction',
                'seaice permeability': 'seaice permeability', 'k': 'seaice permeability'}
si_prop_unit = {'salinity': '-',
                'temperature': '°C',
                'vb': '-', 'brine volume fraction': '-', 'brine volume fraction': '-',
                'seaice permeability': 'm$^{-2}$'}
si_prop_latex = {'salinity': 'S',
                 'temperature': 'T',
                 'brine volume fraction': '\phi_{B}',
                 'ice thickness': 'h_{i}',
                 'snow thickness': 'h_{s}',
                 'seaice permeability': '\kappa'
                 }


def density(t, flag_comment='y'):
    """
		Calculate the density of the pure water ice in function of the temperature

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
		flag_comment : {'y','n'}, optional
			Whether to display the commet or not. Default is 'y'

		Returns
		----------
		rho_i: ndarray
			density of the ice in gram per cubic centimeters [kg m^{-3}]

		sources
		----------
		Equation 2.7 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		from Pounder. E. R. 1965. the physics of ice. Oxford. etc .. Pergamon Press. (the Commonwealth and International Library. Geophysics Division.) Ringer.

	"""
    import numpy as np

    # Physical constant
    A = [-0.000117, 1]
    B = 0.917  # density in kg m^{-3}

    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    rho_ice = np.nan * t

    rho_ice[np.where(t < 0)] = B * np.polyval(A, t[np.where(t < 0)])

    if flag_comment == 'y':
        if np.count_nonzero(np.where(t > 0)):
            print('Element with temperature above 0°C : ice has melt in some case')
    return rho_ice * 10 ** 3


def thermal_conductivity(t, flag_comment='y'):

    """
		Calculate thermal conductivity of ice

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
			If t is an array, s should be an array of the same length

		Returns
		----------
		lambda_si ndarray
			ice thermal conductivity W m^{-1] K^{-1]

		sources
		----------
		Equation 2.11 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		From Yen, Y. C., Cheng, K. C., and Fukusako, s. (1991) Review of intrinsic thermophysical properties of snow, ice, sea ice, and frost. In: Proceedings 3rd International symposium on Cold Regions Heat transfer, Fairbanks, AK, June 11-14, 1991. (Ed. by J. P. Zarling & s. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
	"""
    import numpy as np

    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)

    # Physical constant
    A = [2.97 * 10 ** (-5), -8.66 * 10 ** (-3), 1.91]
    B = 1.16

    lambda_i = np.nan * t

    lambda_i[np.where(t < 0)] = B * np.polyval(A, t[np.where(t < 0)])

    if flag_comment == 'y':
        if np.count_nonzero(np.where(t > 0)):
            print('Element with temperature above 0°C : ice has melt in some case')
    return lambda_i
