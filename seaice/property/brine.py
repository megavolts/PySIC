#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property/brine.py contains function to compute physical property relative to the sea ice brine
"""

import logging

import numpy as np

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "RC"
__date__ = "2018/08/15"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]
__name__ = "brine"

__all__ = ["density", "electric_conductivity", "salinity", "thermal_conductivity"]

module_logger = logging.getLogger(__name__)

def density(t):
    """
        Calculates the density of the brine in [kg/m3]

        :param t : array_like, float
            Temperature [degree C]

        :return rho_b: ndarray
            The calculated density of the brine [kg/m3]

        :reference:
            Equation 2.9 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
            Equation (3) in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice
                samples during shipping and storage. J. Glaciol, 32(112)
            Zubov, N.N. (1945), L'dy Arktiki [Arctic ice]. Moscow, Izdatel'stvo Glavsevmorputi.
    """
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)
    if (t > 0).any():
        module_logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t[t > 0] = np.nan

    # Physical constant
    a = [0.8, 1000]

    s_b = salinity(t)
    rho_b = (a[1] + a[0] * s_b)

    return rho_b


def thermal_conductivity(t):
    """
        Calculates thermal conductivity of brine/sea water [W/mK]

       :param t : array_like, float
            Temperature [degree C]
            If t is an array, s should be an array of the same length

        :return lambda_b: ndarray
            The calculated brine thermal conductivity in [W/mK]

        :sources :
        Equation 2.12 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth,
        microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London:
        Wiley-Blackwell

        Yen, Y. C., Cheng, K. C., and Fukusako, s. (1991) Review of intrinsic thermophysical properties of snow,
        ice, sea ice, and frost. In: Proceedings 3rd International symposium on Cold Regions Heat transfer, Fairbanks,
        AK, June 11-14, 1991. (Ed. by J. P. Zarling & s. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
    """
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)

    if (t > 0).any():
        module_logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t[t > 0] = np.nan

    # Physical constant
    a = [0.00014, 0.030, 1.25]
    b = 0.4184

    lambda_b = b * np.polyval(a, t)

    return lambda_b


def salinity(t, method='cw'):
    """
    Calculates the salinity of the brine at a given temperature according to either Assur's model or Cox & Weeks equation.

    :param t : array_like, float
        Temperature [degree C]
    :param method : 'as', 'cw', Default 'cw'
        'cw' : calculate with the equation of Cox & Weeks (1983)
        'as' : calculate with Assur's model, valid if t => -23 [degree C]. If t < -23, 'cw' is used by default

    :return s_b: ndarray
        The computed salinity of the brine [PsU]

    :references:
        'as' : Equation 2.8 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
        'cw' : Equation 25 in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice
            samples during shipping and storage. J. Glaciol, 32(112), 371–375
    """

    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)

    if (t > 0).any():
        module_logger.warning('For element with temperature T > 0°C: T = np.nan')
        t[t > 0] = np.nan

    if method == 'as':
        if (t >= -23).all():
            s_b = ((1 - 54.11 / t) ** (-1)) * 1000
        else:
            module_logger.warning('T must be superior to -23[°C]. Use Cox & Weeks equation instead')
            return 0

    elif method == 'cw':
        # physical constant
        a = np.empty((3, 4))
        b = np.empty((3, 2))

        # coefficient for -54 < t <= -44
        a[0, :] = [-4442.1, -277.86, -5.501, -0.03669]
        b[0] = [-54, -44]
        # coefficient for -44 < t <= -22.9
        a[1, :] = [206.24, -1.8907, -0.060868, -0.0010247]
        b[1] = [-44, -22.9]
        # coefficient for -22.9 < t <= -2
        a[2, :] = [-3.9921, -22.700, -1.0015, -0.019956]
        b[2] = [-22.9, -2]

        s_b = np.nan*np.ones_like(t)
        for mm in range(0, 3):
            p1 = [a[mm, 3], a[mm, 2], a[mm, 1], a[mm, 0]]
            s_b[(b[mm, 0] <= t) & (t <= b[mm, 1])] = (np.polyval(p1, t[(b[mm, 0] <= t) & (t <= b[mm, 1])]))
    else:
        module_logger.warning("%s method unknown" % method)
        return 0
    return s_b


def electric_conductivity(t):
    """
        Calculates the electric conductivity of brine

        :param t : array_like, float
            Temperature in degree Celsius [°C]

        :return sigma: ndarray
            The conductivity of the brine in [S/m]

        :source :
            Stogryn, A., Desargant, G.J., 1985. The dielectric properties of brine in sea ice at microwave frequencies.
                IEEE Trans. Antennas Propagat. AP-33, 523–532.
    """
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)

    # Physical constant
    a = [[0.08755, 0.5193], [0.1100, 1.0334]]

    sigma_b = np.nan*np.ones_like(t)

    sigma_b[-22.9 <= t] = np.exp(np.polyval(a[0], t[-22.9 <= t]))
    sigma_b[t < -22.9] = np.exp(np.polyval(a[1], t[t < -22.9]))

    return sigma_b


def viscosity(s, t):
    impo