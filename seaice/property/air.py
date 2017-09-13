#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property/air.py contains function to compute physical property relative to the air content of the seaice
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


def volumefraction(t, s, rho_si='Default'):
    """
    Calculate the volume fraction of air in function of the temperature and salinity

    Parameters
    ----------
    :param t : array_like, number
        temperature in degree Celsius [°C]
        If t is an array, s should be an array of the same length
    :param s : array_like, number
        salinity in practical salinity unit [PsU]
        If s is an array, t should be an array of the same length
    :param rho_si : optional, array_like, number
        density of the ice in gram per cubic centimeter [g cm^{-3}]. Defautl value is 0.9.
        If rho_si is an array, t should be an array of the same length
    :param flag_comment:


    Returns
    ----------
    vf_a: ndarray
        Volume fraction of air in the ice

    sources
    ----------
    Equation 14 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).

	"""
    import numpy as np

    # check array lengths
    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s = np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print('temperature and salinity array should be the same shape')
        return 0

    if isinstance(rho_si, (int, float)):
        rho_si = np.array([rho_si]) / 10 ** 3  # ice density in g cm^{-3}
    elif isinstance(rho_si, str) and rho_si == 'Default':
        print('default rho si')
        rho_si = seaice_density(t, s, flag_comment='n') / 10 ** 3  # ice density in g cm^{-3}
    elif rho_si.__len__() > 2 and t.shape != rho_si.shape:
        print('sea ice density array should be the same shape as temperature and salinity')
        return 0

    # Physical constant
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

    rho_i = ice_density(t, 'n') / 10 ** 3  # ice density in g cm^{-3}

    F1 = np.nan * t
    F2 = np.nan * t
    for mm in range(0, 3):
        p1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
        p2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

        F1[(B[mm, 0] <= t) & (t <= B[mm, 1])] = np.polyval(p1, t[(B[mm, 0] <= t) & (t <= B[mm, 1])])
        F2[(B[mm, 0] <= t) & (t <= B[mm, 1])] = np.polyval(p2, t[(B[mm, 0] <= t) & (t <= B[mm, 1])])

    vf_a = ((1 - rho_si / rho_i + rho_si * s * F2 / F1))

    return vf_a
