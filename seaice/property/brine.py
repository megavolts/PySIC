#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property/brine.py contains function to compute physical property relative to the brine
"""

import warnings

import numpy as np

from seaice import toolbox as icdt

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


def volume_fraction(t, s, rho_si='default', flag_comment='n'):
    """
    Calculate the volume fraction of brine in function of the temperature and salinity

    Parameters
    ----------
    t : array_like, number
        temperature in degree Celsius [°C]
        If t is an array, s should be an array of the same length
    s : array_like, number
        salinity in practical salinity unit [PsU]
        If s is an array, t should be an array of the same length
    rho_si : optional, array_like, number
        density of the ice in gram per cubic centimeter [g cm^{-3}]. Default is calculated for t,s value with a default air volume fraction set to 0.5‰.
        If rho_si is an array, t should be an array of the same length
    flag_comment : option, string
        toggle comment on/off

    Returns
    ----------
    vf_b: ndarray
        Volume fraction of brine in the ice [-]

    sources
    ----------
    thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
    from equation 5 and 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).
    """
    # check parameters
    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s = np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print('temperature and salinity array should be the same dimension')
        return 0

    if rho_si == 'default':
        rho_si = seaice_density(t, s, flag_comment='n') / 10 ** 3  # ice density in g cm^{-3}
    else:
        if isinstance(rho_si, (int, float)):
            rho_si = np.array([rho_si]) / 10 ** 3  # ice density in g cm^{-3}
        else:
            if t.shape != rho_si.shape:
                print('sea ice density array should be the same dimension as temperature and salinity')
                return 0

    A = np.empty((4, 4, 2))

    # coefficient for -2t<=0
    A[0, 0, :] = [-0.041221, 0.090312]
    A[0, 1, :] = [-18.407, -0.016111]
    A[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
    A[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

    # coefficient for -22.9<t<=-2
    A[1, 0, :] = [-4.732, 0.08903]
    A[1, 1, :] = [-22.45, -0.01763]
    A[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
    A[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

    # coefficient for -30<t<=-22.9
    A[2, 0, :] = [9899, 8.547]
    A[2, 1, :] = [1309, 1.089]
    A[2, 2, :] = [55.27, 0.04518]
    A[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

    B = np.empty((3, 2))
    B[0] = [-2, 0]
    B[1] = [-22.9, -2]
    B[2] = [-30, -22.9]

    vf_a = air_volumefraction(t, s, rho_si, flag_comment='n')
    rho_i = ice_density(t, 'n') / 10 ** 3  # ice density in g cm^{-3}

    F1 = np.nan * t
    F2 = np.nan * t
    for mm in np.arange(0, 3):
        P1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
        P2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

        F1[(B[mm, 0] <= t) & (t <= B[mm, 1])] = np.polyval(P1, t[(B[mm, 0] <= t) & (t <= B[mm, 1])])
        F2[(B[mm, 0] <= t) & (t <= B[mm, 1])] = np.polyval(P2, t[(B[mm, 0] <= t) & (t <= B[mm, 1])])

    vf_b = ((1 - vf_a) * rho_i * s / (F1 - rho_i * s * F2))
    return vf_b


def density(t):
    """
		Calculate the density of the brine in function of the temperature.

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]

		Returns
		----------
		rho_b: ndarray
			density of the brine in gram per cubic centimeters [kg m^{-3}]

		sources
		----------
		Equation 2.9 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		from equation (3) in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice samples during shipping and storage. J. Glaciol, 32(112)

		from Zubov, N.N. (1945), L'dy Arktiki [Arctic ice]. Moscow, Izdatel'stvo Glavsevmorputi.

	"""
    # Physical constant
    A = [8 * 10 ** (-4), 1]
    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)

    s_b = brine_salinity(t)
    rho_b = (A[1] + A[0] * s_b)

    return rho_b * 10 ** 3


def salinity(t, method='CW', flag_comment='y'):
    """
    Calculate the salinity of the brine in function of the temperature at equilibrium.

    Parameters
    ----------
    t : array_like, number
        temperature in degree Celsius [°C]
    method : {'As','CW'}, optional
        Whether to calculate the salinity with Assur model ('As') or with the equation of Cox & Weeks (1983) ('CW'). Default is 'CW'
    flag_comment:

    Returns
    ----------
    s_b: ndarray
        salinity of the brine in Practical salinity Unit [PsU]

    sources
    ----------
    'As' : Equation 2.8 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
    'CW' : Equation 25 in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice samples during shipping and storage. J. Glaciol, 32(112), 371–375
"""
    import numpy as np

    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)

    s_b = np.nan * t

    if method == 'As':
        if t.all > -23:
            s_b = ((1 - 54.11 / t) ** (-1)) * 1000
        else:
            print('At least one temperature is inferior to -23[°C]. Cox & Weeks equation is used instead')
            brine_salinity(t, 'CW')
    else:
        # Physical constant
        A = np.empty((3, 4))
        B = np.empty((3, 2))

        # coefficient for -54<t<=-44
        A[0, :] = [-4442.1, -277.86, -5.501, -0.03669];
        B[0] = [-54, -44]
        # coefficient for -44<t<=-22.9
        A[1, :] = [206.24, -1.8907, -0.060868, -0.0010247];
        B[1] = [-44, -22.9]
        # coefficient for -22.9<t<=-2
        A[2, :] = [-3.9921, -22.700, -1.0015, -0.019956];
        B[2] = [-22.9, -2]

        for mm in range(0, 3):
            P1 = [A[mm, 3], A[mm, 2], A[mm, 1], A[mm, 0]]

            s_b[(B[mm, 0] <= t) & (t <= B[mm, 1])] = (np.polyval(P1, t[(B[mm, 0] <= t) & (t <= B[mm, 1])]))
    return s_b


def thermal_conductivity(t, flag_comment='y'):
    """
		Calculate thermal conductivity of brine

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
			If t is an array, s should be an array of the same length

		Returns
		----------
		lambda_si ndarray
			brine thermal conductivity in W m^{-1]K^{-1]

		sources
		----------
		Equation 2.12 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		From Yen, Y. C., Cheng, K. C., and Fukusako, s. (1991) Review of intrinsic thermophysical properties of snow, ice, sea ice, and frost. In: Proceedings 3rd International symposium on Cold Regions Heat transfer, Fairbanks, AK, June 11-14, 1991. (Ed. by J. P. Zarling & s. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
	"""
    import numpy as np

    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)

    # Physical constant
    A = [0.00014, 0.030, 1.25]
    B = 0.4184

    lambda_b = np.nan * t

    lambda_b[(t < 0)] = B * np.polyval(A, t[(t < 0)])

    if flag_comment == 'y':
        if np.count_nonzero(np.where(t > 0)):
            print('Element with temperature above 0°C : ice has melt in some case')

    return lambda_b


def electricconductivity(t, flag_comment='n'):
    """
		Calculate the electric conductivity of brine for a given temperature

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]

		Returns
		----------
		sigma: ndarray
			conductivity of the brine in microsiemens/meter [ms/m]

		Equation
		_________
			Fofonoff, Nick P., and Robert C. Millard. "Algorithms for computation of fundamental properties of seawater." (1983).
	"""
    import numpy as np

    t = icdt.make_array(t)
    ii_max = len(t)

    # Physical constant
    A = [0.08755, 0.5193]

    sigma_b = []
    for ii in range(0, ii_max):
        sigma_b.append(-t[ii] * np.exp(np.polyval(A, t[ii])))
    return np.array(sigma_b)
