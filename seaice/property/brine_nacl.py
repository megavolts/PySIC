#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property/brine.py contains function to compute physical property relative to the sea ice brine
"""

import numpy as np
import logging

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "RC"
__date__ = "2020/09/30"
__credits__ = ["Hajo Eicken", "Sonke Maus"]
__name__ = "brine"

__all__ = ["dynamic_viscosity"]

module_logger = logging.getLogger(__name__)


def dynamic_viscosity(s, t, override_t=False, override_s=False):
    """
    Returns the dynamic viscosity of NaCl solution as function of temperature and salinity (g/ kg)
    Combines the fit to pure supercooled water from Hallett (1993) with a fit to data from Stakelbeck and Plank (1929)

    :param s: array-like, float
        Salinity [g / kg], s = 0-1700
    :param t: array-like, float
        Temperature [degree C (IPTS-68)], t = -21 - 10.
    :param override_t: boolean, Default False
        Override validity domain for temperature. Use at your own risk. Cf. References
    :param override_s: boolean, Default True
        Override validity domain for salinity. Use at your own risk. Cf. References

    :return: array-like, float
        Dynamic viscosity, mu [Pa s] or [kg m^-1 s^-1]

    :reference:
    Maus, S. (2007). On Brine Entrapment in Sea Ice: Morphological Stability, Microstructure and Convection.
        University of Bergen, Norway. Eq. A.36 and A.37, p. 352-353
    """

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)

    if s.shape != t.shape:
        module_logger.error('s, t must all have the same dimensions')
        return 0

    if ((s <= 0).any() or (170 < s).any()) and not override_s:
        s[(s <= 0) | (170 < s)] = np.nan
        module_logger.warning('salinity value must be 0 < s < 1000 [PSU]')

    if ((t <= -21).any() or (10 <= t).any()) and not override_t:
        t[(t <= -21) | (10 <= t)] = np.nan
        module_logger.warning('salinity value must be 0 < s < 1000 [PSU]')

    # Eq. A36: Viscosity of pure water
    p4 = 0.000004415
    p3 = 0.00009472
    p2 = 0.0019855
    p1 = -0.03370
    p0 = 0.001792
    mu_w = p0 * (1 + p1 * t + p2 * t**2 + p3 * t**3 + p4 * t**4)  #  pure water

    # Eq. A37 Viscosity of NaCl brine
    s3 = 2.037e-8
    s2 = 8.954e-6
    s1 = -4.104e-5
    s0 = 1
    mu_b = mu_w * (s0 + s1 * s + s2 * s**2 + s3 * s**3)

    return mu_b


def dynamic_viscosity_liquidus(s, t, override_t=False, override_s=False):
    """
    Returns the dynamic viscosity of NaCl soluion at their freezing point
    Combines the fit to pure supercooled water from Hallett (1993) with a fit to data from Stakelbeck and Plank (1929)

    :param s: array-like, float
        Salinity [PSU] or [g / kg], s = 0-1700
    :param t: array-like, float
        Temperature [degree C (IPTS-68)], t = -21 - 0.
    :param override_t: boolean, Default False
        Override validity domain for temperature. Use at your own risk. Cf. References
    :param override_s: boolean, Default True
        Override validity domain for salinity. Use at your own risk. Cf. References

    :return: array-like, float
        Dynamic viscosity, mu [Pa s] or [kg m^-1 s^-1]

    :reference:
    Maus, S. (2007). On Brine Entrapment in Sea Ice: Morphological Stability, Microstructure and Convection.
        University of Bergen, Norway. Eq. A.36 and A.37, p. 352-353
    """

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)

    if s.shape != t.shape:
        module_logger.error('s, t must all have the same dimensions')
        return 0

    if ((s <= 0).any() or (170 < s).any()) and not override_s:
        s[(s <= 0) | (170 < s)] = np.nan
        module_logger.warning('salinity value must be 0 < s < 1000 [PSU]')

    if ((t <= -21).any() or (0 <= t).any()) and not override_t:
        t[(t <= -21) | (0 <= t)] = np.nan
        module_logger.warning('salinity value must be 0 < s < 1000 [PSU]')

    # Eq. A36: Viscosity of pure water
    p4 = 0.000004415
    p3 = 0.00009472
    p2 = 0.0019855
    p1 = -0.03370
    p0 = 0.001792
    mu_w = p0 * (1 + p1 * t + p2 * t**2 + p3 * t**3 + p4 * t**4)  #  pure water

    # # Eq. A38 Viscosity of NaCl brine
    b3 = 0.0000552
    b2 = 0.002772
    b1 = -0.0002001
    mu_r = 1 + b1 * t + b2 * t**2 + b3 * t**3

    mu_fp = mu_w * mu_r
    return mu_fp

