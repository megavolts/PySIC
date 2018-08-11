#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property.sw.py contains function to compute physical property of sea water
"""
import numpy as np
import logging

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "final"
__date__ = "2017/09/13"
__name__ = "sw"

__all__ = ["freezingtemp", "salinity_from_conductivity"]

module_logger = logging.getLogger(__name__)


def freezingtemp(s, p=10.1325):
    """
        Computes freezing temperature of seawater [degree C]

        Validity if 2 < s < 42 [psu]. Estimated error at p = 500 [dbar] is 0.003 [degree C]

        :param s : array_like, float
            Salinity of seawater [PsU]
        :param p : array_like, float
            Seawater pressure [dbar].
            Default is atmospheric pressure at sea level p = 10.1325

        :return t_f: ndarray
            Freezing point of seawater [degree C]

        :reference:
            UNESCO (1978) Eighth Report of the Joint Panel on Oceanographic Tables and Standards UNESCO Technical Papers
            in Marine Science 28. UNESCO, Paris.
            Annex 6 freezing point of seawater F.J. Millero pp.29-35.

        :check value:
            t_f=-2.588567 [degree C] for s=40.0 [PSU] and p=500 [dbar]
    """

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d([s]).astype(float)

    if isinstance(p, (int, float, list)):
        p = np.atleast_1d([p]).astype(float)

    if s.shape != p.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    if s[4 < s].any() or s[s < 40].any():
        module_logger.warning('s must be 4 < s < 40. Replacing erronous value with nan-value')
        s[4 < s] = np.nan
        s[s < 40] = np.nan

    a = [-0.0575, +1.710523e-3, -2.154996e-4]
    b = [-7.53e-4]

    t_f = a[0]*s + a[1] * (s*(3 / 2)) + a[2]*(s ** 2) + b[0]*p

    return t_f


def salinity_from_conductivity(t, c):
    """
    Calculates the salinity of sea water from specifc conductance

    :param t: array_like, float
        Temperature [degree C]
        If t is an array, c should be an array of same dimension
    :param c: array_like, float
        conductivity in microSievert by centimeters [uS/cm]
        If c is an array, t should be an array of same dimension

    :return sigma_sw: ndarray
        seawater salinity [PSU]

    :source :
    Standard Methods for the Examination of Water and Wastewater, 20th edition, 1999.
    http://www.chemiasoft.com/chemd/salinity_calculator

    :validity:
    2 < s < 42
    """

    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)

    if isinstance(c, (int, float, list)):
        c = np.atleast_1d([c])  # from S/m in uS/cm

    if t.shape != c.shape:
        module_logger.warning('t, s, rho_si, vf_a must all have the same dimensions')
        return 0

    # Physical constant
    a = np.empty((6, 2))
    a[0, :] = [0.0080, 0.0005]
    a[1, :] = [-0.1692, -0.0056]
    a[2, :] = [25.3851, -0.0066]
    a[3, :] = [14.0941, -0.0375]
    a[4, :] = [-7.0261, 0.0636]
    a[5, :] = [2.7081, -0.0144]

    b = [-0.0267243, 4.6636947, 861.3027640, 29035.1640851]

    c_kcl = np.polyval(b, t)
    rc = c / c_kcl

    rc_x = np.sqrt(rc)

    ds = (t - 15) / (1 + 0.0162 * (t - 15)) * np.polyval(a[:, 1], rc_x)
    s = np.polyval(a[:, 0], rc_x) + ds

    s = s+ds

    if s[s > 42].__len__() > 0 or s[s < 2].__len__() > 0:
        module_logger.warning("%s some salinites are out of the validity domain" % __name__)
        s[s > 42] = np.nan
        s[s < 2] = np.nan

    return s

