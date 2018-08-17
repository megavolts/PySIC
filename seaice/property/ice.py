#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property/ice.py contains function to compute physical property relative to pure water ice
"""
import logging
import numpy as np

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "Final Version"
__date__ = "2018/08/15"
__name__ = "ice"

__all__ = ["density", "thermal_conductivity"]

module_logger = logging.getLogger(__name__)


def density(t):
    """
        Calculates the density of pure water ice

        :param t : array_like, float
            Temperature [degree °C]

        :return	rho_i: ndarray, float
            Calculated density of the ice [kg m^{-3}]

        :sources:
            Equation 2.7 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
            E.R. Pounder. The physics of ice. Oxford, etc., Pergamon Press, 1965. vii, 151 p., (The Commonwealth and
                International Library. Geophysics Division.)
    """

    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        module_logger.warning('For element with temperature T > 0°C, T=np.nan')
        t[t > 0] = np.nan

    # Physical constant
    a = [-0.1403, 916.7]

    rho_ice = np.polyval(a, t)

    return rho_ice


def thermal_conductivity(t):
    """
        Calculates thermal conductivity of ice [W/mK]

        :param t : array_like, float
            Temperature [degree °C]
            If t is an array, s, t must be the same length

        :return lambda_si: ndarray, float
            The calculated ice thermal conductivity [W/mK]

        :source:
        Equation 2.11 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth,
        microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London:
        Wiley-Blackwell
        From Yen, Y. C., Cheng, K. C., and Fukusako, s. (1991) Review of intrinsic thermophysical properties of snow,
        ice, sea ice, and frost. In: Proceedings 3rd International symposium on Cold Regions Heat transfer, Fairbanks,
        AK, June 11-14, 1991. (Ed. by J. P. Zarling & s. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
    """

    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        module_logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t[t > 0] = np.nan

    # Physical constant
    a = [2.97*1e-5, -8.66*1e-3, 1.91]
    b = 1.16

    lambda_i = b * np.polyval(a, t)

    return lambda_i
