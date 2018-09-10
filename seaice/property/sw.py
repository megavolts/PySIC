#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property.sw.py contains function to compute physical property of sea water

rEFErENCES:
r.C. Millard and K. Yang 1992. "CTD Calibration and Processing Methods used by Woods Hole   Oceanographic Institution"
    Draft April 14, 1992 (Personal communication)
CSIrO MatLAB Seawater Library, Phil Morgan, CMr (maintained by Lindsay Pender), last updated December 2003

"""
import numpy as np
import logging
from scipy import optimize

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1.0"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "rC"
__date__ = "2018/8/16"
__name__ = "sw"

__all__ = ["freezingtemp", "salt", "salt_c", "conductivity2salinity", "salinity2conductivity"]

module_logger = logging.getLogger(__name__)


def freezingtemp(s, p=10.1325, validity=True):
    """
        Computes freezing temperature of seawater [degree C] for given salinity s and pressure p

        Validity if 4 < s < 40 [psu]. Estimated error at p = 500 [dbar] is 0.003 [degree C]

        :param s : array_like, float
            Salinity of seawater [PSU ]

        :param p : array_like, float
            Seawater pressure [dbar].
            Default is atmospheric pressure at sea level p = 10.1325 [dbar]

        :param validity: boolean
            For all data out of the validity, it returns np.nan if True and computed the value if False
            Default is True

        :return t_f: ndarray
            Freezing point of seawater [degree C]

        :reference:
            UNESCO (1978) Eighth report of the Joint Panel on Oceanographic Tables and Standards UNESCO Technical Papers
            in Marine Science 28. UNESCO, Paris.
            Annex 6 freezing point of seawater F.J. Millero pp.29-35.

        :check value:
            t_f=-2.588567 [degree C] for s=40.0 [PSU] and p=500 [dbar]
    """

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s)

    if isinstance(p, (int, float, list)):
        p = np.atleast_1d(p)

    if s.shape != p.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    if s[s < 4].any() or s[40 < s].any():
        if validity:
            module_logger.info('For element with salinity out of range 4 < s < 40,  s=np.nan')
            s[s < 4] = np.nan
            s[40 < s] = np.nan
        else:
            module_logger.warning('some s value re out of validity domain')

    a = [-0.0575, +1.710523e-3, -2.154996e-4]
    b = [-7.53e-4]

    t_f = (a[0] + a[1] * (np.sqrt(s)) + a[2]*s)*s + b[0]*p

    return t_f


def c3515():
    """
    returns conductivity of sea water at salinity s = 35 PSU, temperature t = 15 C and pressure p = 0 dbar in mS/cm

    :return: ndarray float
        Conductivity of sea water at s = 35 PSU, t = 15 C and p = 0 in mS/cm
    """
    return np.array(42.914)


def salrp(r, t, p):
    """
    Computes equation rp(s,t,p) = C(s,t,p)/C(s,t,0) used in calculating salinity in UNESCO 1983 polynomial

    :param r: array-like, float
        Conductivity ratio  r = C(s,t,p)/C(35,15,0) [no units]
    :param t: array-like, float
        Temperature [degree C (IPTS-68)]
    :param p: array-like, float
        Pressure [dbar]

    :return rrp: ndarray float
        Rp(s,t,p) = c(s,t,p)/c(s,t,0)

    :references:
        Equation 4 (p.8)
        Fofonoff, P. and Millard, r.C. Jr, Unesco 1983. Algorithms for computation of fundamental properties of seawater
            1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.
    """

    if isinstance(r, (int, float, list)):
        r = np.atleast_1d(r)
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)
    if isinstance(p, (int, float, list)):
        p = np.atleast_1d(p)

    if r.shape != t.shape or r.shape != p.shape or t.shape != p.shape:
        module_logger.error('s, p, t must all have the same dimensions')
        return 0

    d1 = 3.426e-2
    d2 = 4.464e-4
    d3 = 4.215e-1
    d4 = -3.107e-3

    e1 = 2.070e-5
    e2 = -6.370e-10
    e3 = 3.989e-15

    rrp = 1 + (p * (e1 + e2 * p + e3 * p**2))/(1 + d1 * t + d2 * t**2 + (d3 + d4 * t) * r)  # Rp

    return rrp


def salrp_c(c, t, p):
    """
    Computes equation rp(s,t,p) = c(s,t,p/c(s,t,0) used in calculating salinity in UNESCO 1983 polynomial

    :param c: array-like, float
        Conductivity C [mS/cm]
    :param t: array-like, float
        Temperature [degree C (IPTS-68)]
    :param p: array-like, float
        Pressure [dbar]

    :return rrp: ndarray float
        Rp(s,t,p) = c(s,t,p)/c(s,t,0)

    :references:
        Equation 4 (p.8)
        Fofonoff, P. and Millard, r.C. Jr, Unesco 1983. Algorithms for computation of fundamental properties of seawater
            1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.
    """

    if isinstance(c, (int, float, list)):
        c = np.atleast_1d(c)
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)
    if isinstance(p, (int, float, list)):
        p = np.atleast_1d(p)

    if c.shape != t.shape or c.shape != p.shape or t.shape != p.shape:
        module_logger.error('s, p, t must all have the same dimensions')
        return 0

    r = c/c3515()
    rrp = salrp(r, t, p)  # rrp
    return rrp


def salrt(t):
    """
    Computes equation rt(t) = C(35, t, 0)/(35,15,0) used in calculating salinity with UNESCO 1983 polynomial

    :param t: ndarray
        Temperature [degree C (ItS-90)]
    
    :return: ndarray
        Conductivity ratio rt(t) at S=35 and p=0

    :check value:
        rt = 1.0000000 for r = 1, t = 15 [degree C] and p = 0 [dbar]
        rt = 1.1164927 for r = 1.2, t = 20 [degree C] and p = 2000 [dbar]
        rt = 0.77956585for r = 0.65, t = 5 [degree C] and p = 1500 [dbar]

    """
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)

    c = [1.0031e-9, -6.9698e-7, 1.104259e-4, 2.00564e-2, 0.6766097]

    rt = np.polyval(c, t)
    return rt


def sals(rt, t, validity=True):
    """
    Computes salinity of sea water as a function of rt and t at constant pressure p = 0 dbar
    Validity domain is -2 <= t <= 35 [degree C] and 2 <= s <= 42 [PSU]

    :param rt: array-like, float
        Conductivity ratio, rt(s, t) = C(S, t, 0)/C(35, t, 0)
    :param t: array-like, float
        Temperature [degree C (IPTS-68)]
    :param validity: bool, Default True
        If True returns np.nan for all data out of the validity domain. If false, compute value anyway

    :return s:ndarray float
        salinity [PSU (PSS-78)]

    :references: ndarray
       Fofonoff, P. and Millard, r.C. Jr
       Unesco 1983. Algorithms for computation of fundamental properties of
       seawater, 1983. _Unesco tech. Pap. in Mar. Sci._, No. 44, 53 pp.
    """

    if isinstance(rt, (int, float, list)):
        rt = np.atleast_1d(rt)
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)

    if rt.shape != t.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    if t[t < -2].any() or t[35 < t].any():
        if validity:
            module_logger.info('For element with salinity out of range -2 < t < 35,  t = np.nan')
            t[t < -2] = np.nan
            t[35 < t] = np.nan
        else:
            module_logger.warning('Some temperature value are out of the validity domain: -2 < t < 35 [C]')

    a = [2.7081, -7.0261, 14.0941, 25.3851, -0.1692, 0.0080]
    b = [-0.0144, 0.0636, -0.0375, -0.0066, -0.0056, 0.0005]
    k = 0.0162

    rtx = np.sqrt(rt)
    del_t = t - 15
    del_s = (del_t / (1 + k * del_t)) * np.polyval(b, rtx)
    s = np.polyval(a, rtx)
    s = s + del_s

    if s[s < 2].any() or s[42 < s].any():
        if validity:
            module_logger.info('For element with salinity out of range 2 < s < 42,  s = np.nan')
            s[s < 2] = np.nan
            s[42 < s] = np.nan
        else:
            module_logger.warning('Some computed salinity value are out of the validity domain: 2 < s < 42 [PSU])')

    return s


def salt(r, t, p, validity=True):
    """
    Computes salinity from conductivity ratio. UNESCO 1983 polynomial.
    Validity domain is -2 <= t <= 35 [degree C] and 2 <= s <= 42 [PSU]

    :param r: array-like, float
       Conductivity ratio r = c(s,r,p)/c(35,15,0) [no units]
    :param t: array-like, float
        Temperature [degree C (IPTS-68)]
    :param p: array-like, float
        Pressure [dbar]
    :param validity: bool, Default True
        If True returns np.nan for all data out of the validity domain. If false, compute value anyway

    :return s: ndarray float
        Salinity [PSU (PSS-78)]

    :check value:
        s = 35.000000 [PSU] for r = 1, t = 15 [degree C] and p = 0 [dbar]
        s = 37.245628 [PSU] for r = 1.2, t = 20 [degree C] and p = 2000 [dbar]
        s = 29.995347 [PSU] for r = 0.65, t = 5 [degree C] and p = 1500 [dbar]
    """

    if isinstance(r, (int, float, list)):
        r = np.atleast_1d(r)
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)
    if isinstance(p, (int, float, list)):
        p = np.atleast_1d(p)

    if r.shape != t.shape or r.shape != p.shape or p.shape != t.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    rt = salrt(t)
    rp = salrp(r, t, p)
    rrt = r / (rp * rt)
    s = sals(rrt, t, validity=validity)

    return s


def salt_c(c, t, p=None, validity=True):
    """
    Computes salinity from conductivity ratio. UNESCO 1983 polynomial.
    Validity domain is -2 <= t <= 35 [degree C] and 2 <= s <= 42 [PSU]

    :param c: array-like, float
        Conductivity [mS/cm]
    :param t: array-like, float
        Temperature [degree C (IPTS-68)]
    :param p: array-like, float
        Pressure [dbar], default p=0
    :param validity: bool, Default True
        If True returns np.nan for all data out of the validity domain. If false, compute value anyway

    :return s: ndarray float
        Salinity [PSU (PSS-78)]

    :check value:
        s = 35.000000 [PSU] for c = 42.914, t = 15 [degree C] and p = 0 [dbar]
        s = 37.245628 [PSU] for c = 51.4968, t = 20 [degree C] and p = 2000 [dbar]
        s = 29.995347 [PSU] for c = 27.8941, t = 5 [degree C] and p = 1500 [dbar]
    """


    if isinstance(c, (int, float, list)):
        c = np.atleast_1d(c)
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t)
    if isinstance(p, (int, float, list)):
        p = np.atleast_1d(p)
    elif p is None:
        p = np.zeros_like(c)

    if c.shape != t.shape or c.shape != p.shape or p.shape != t.shape:
        module_logger.warning('c, p, t must all have the same dimensions')
        return 0

    r = c/c3515()

    s = salt(r, t, p, validity=validity)
    return s


def salinity2conductivity(s, t=15, p= 10.1325):
    """
    Returns the specific conductivity at 15 [degree C] as function of the salinity

    :param s: array-like, float
        Salinity [PSU] or [g / kg]
    :param t: array-like, float
        Temperature [degree C (IPTS-68)]. If undeclared, t = 15 [degree C] by default
    :param p: array-like, float
        Pressure [dbar]. If undeclared, p = 10.1325 [dbar] by default

    :return c: ndarray float
        Specific conductivity [mS/cm]
    """
    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)
    if t == 15:
        t = t * np.ones_like(s)
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if p == 10.1325:
        p = p * np.ones_like(s)
    elif isinstance(s, (int, float, list)):
        p = np.atleast_1d(p).astype(float)

    if (s <= 0).any() or (1000 < s).any():
        s[(s <= 0) | (1000 < s)] = np.nan
        module_logger.warning('salinity value must be 0 < s < 1000 [PSU]')

    if s.shape != t.shape or s.shape != p.shape or p.shape != t.shape:
        module_logger.warning('s, p, t must all have the same dimensions')
        return 0

    stp = np.vstack([s, t, p]).transpose()

    # initial condition
    s0 = 20

    # override validity domain for s out of validity domain 2 <= s <=42
    if (stp[:, 0] < 2).any() or (42 < stp[:, 0]).any():
        validity = False
    else:
        validity = True

    def f(cf, sf, pf, tf):
        return sf - conductivity2salinity(cf, pf, tf, validity=validity)

    c = [optimize.newton(f, s0, args=(x[0], x[1], x[2],))[0] if not np.isnan(x[0]) else np.nan for x in stp]

    return c


# aliases:
def conductivity2salinity(c, t, p=None, validity=True):
    """
    Computes salinity from electrical conductivity . UNESCO 1983 polynomial.
    Validity domain is -2 <= t <= 35 [degree C] and 2 <= s <= 42 [PSU]

    :param c: array-like, float
        Conductivity [mS/cm]
    :param t: array-like, float
        Temperature [degree C (IPTS-68)]
    :param p: array-like, float
        Pressure [dbar]
    :param validity: bool, Default True
        If True returns np.nan for all data out of the validity domain. If false, compute value anyway

    :return s: ndarray float
        Salinity [PSU (PSS-78)]
    """
    s = salt_c(c, t, p=p, validity=validity)
    return s
