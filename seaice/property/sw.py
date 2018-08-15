#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property.sw.py contains function to compute physical property of sea water

REFERENCES:
R.C. Millard and K. Yang 1992. "CTD Calibration and Processing Methods used by Woods Hole   Oceanographic Institution"
    Draft April 14, 1992 (Personal communication)
CSIRO MatLAB Seawater Library, Phil Morgan, CMR (maintained by Lindsay Pender), last updated December 2003

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


def freezingtemp(s, p=10.1325, range=True):
    """
        Computes freezing temperature of seawater [degree C]

        Validity if 4 < s < 40 [psu]. Estimated error at p = 500 [dbar] is 0.003 [degree C]

        :param s : array_like, float
            Salinity of seawater [PsU]

        :param p : array_like, float
            Seawater pressure [dbar].
            Default is atmospheric pressure at sea level p = 10.1325

        :param range: boolean
            For all data out of the validity, it returns np.nan if True and computed value if False
            Default is True

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

    if s[s < 2].any() or s[42 < s].any():
        if range:
            module_logger.info('s must be 2 < s < 42. Replacing erronous value with nan-value')
            s[s < 2] = np.nan
            s[42 < s] = np.nan
        else:
            module_logger.warning('some s value re out of validity domain')

    a = [-0.0575, +1.710523e-3, -2.154996e-4]
    b = [-7.53e-4]

    t_f = (a[0] + a[1] * (np.sqrt(s)) + a[2]*s)*s + b[0]*p

    return t_f


def c3515():
    """
    Returns conductivity of sea water at salinity s=35 PSU, temperature T=15 C and pressure p=0 dbar in mS/cm

    :return: ndarray
        Conductivity of sea water at s=35 PSU, T=15 C and p=0 in mS/cm

    :references:
        R.C. Millard and K. Yang 1992. "CTD Calibration and Processing Methods used by Woods Hole Oceanographic
        Institution" Draft April 14, 1992 (Personal communication)
        CSIRO MatLAB Seawater Library, Phil Morgan, CMR (maintained by Lindsay Pender), last updated December 2003
    """
    return np.array(42.914)


def salrt(T):
    """
    Computes conductivity ratio rt(T) = C(35, T, 0)/(35,15,0) at constant pressure p = 0 dbar and salinity s = 35 PSU

    :param T: ndarray
        temperature [℃ (ITS-90)]
    :return: ndarray
        conductivity ratio rt(T) at S=35 and p=0
    """
    if isinstance(T, (int, float, list)):
        T = np.atleast_1d([T]).astype(float)

    c = [1.0031e-9, -6.9698e-7, 1.104259e-4, 2.00564e-2, 0.6766097]

    rt = np.polyval(c, T)
    return rt


def sals(Rt, T):
    '''
    Computes salinity of sea water as a function of Rt and T at constant pressure p = 0 dbar

    :param Rt: ndarray
        Conductivity ratio, Rt(S, T) = C(S, T, 0)/C(35, T, 0)
    :param T: ndarray
        temperature [degree C (IPTS-68)]
    :return S:ndarray
        salinity [PSU (PSS-78)]

    :References: ndarray
       Fofonoff, P. and Millard, R.C. Jr
       Unesco 1983. Algorithms for computation of fundamental properties of
       seawater, 1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.
    '''

    if isinstance(Rt, (int, float, list)):
        Rt = np.atleast_1d([Rt]).astype(float)

    if isinstance(T, (int, float, list)):
        T = np.atleast_1d([T]).astype(float)

    if Rt.shape != T.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    a = [2.7081, -7.0261, 14.0941, 25.3851, -0.1692, 0.0080]
    b = [-0.0144, 0.0636, -0.0375, -0.0066, -0.0056, 0.0005]
    k = 0.0162

    Rtx = np.sqrt(Rt)
    del_T = T - 15
    del_S = (del_T / (1 + k * del_T)) * np.polyval(b, Rtx)
    S = np.polyval(a, Rtx)
    S = S + del_S

    return S


def salrp(R, T, P):
    '''
    Computes equation Rp(S,T,P) = C(S,T,P)/C(S,T,0) used in calculating salinity in UNESCO 1983 polynomial

    :param R:
        Conductivity ratio, Rt(S, T) = C(S, T, 0)/C(35, T, 0) [no units]

    :param T:
        temperature [degree C (IPTS-68)]

    :return P:
        pressure [dbar]

    :references:
        Equation 4 (p.8)
        Fofonoff, P. and Millard, R.C. Jr, Unesco 1983. Algorithms for computation of fundamental properties of seawater,
        1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.

    '''

    d1 = 3.426e-2
    d2 = 4.464e-4
    d3 = 4.215e-1
    d4 = -3.107e-3

    e1 = 2.070e-5
    e2 = -6.370e-10
    e3 = 3.989e-15

    Rp = 1 + (P * (e1 + e2 * P + e3 * P**2))/(1 + d1 * T + d2 * T**2 + (d3 + d4 * T) * R)

    return Rp



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
    k = 0.0162

    c_kcl = np.polyval(b, t)
    rc = c / c_kcl

    rc_x = np.sqrt(rc)

    del_t = t - 15
    ds = del_t / (1 + k * del_t) * np.polyval(a[:, 1], rc_x)
    s = np.polyval(a[:, 0], rc_x) + ds

    s = s+ds

    if s[s > 42].__len__() > 0 or s[s < 2].__len__() > 0:
        module_logger.warning("%s some salinites are out of the validity domain" % __name__)
        s[s > 42] = np.nan
        s[s < 2] = np.nan

    return s


