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
__version__ = "1.1.0"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "RC"
__date__ = "2018/8/16"
__name__ = "sw"

__all__ = ["freezingtemp", "salt", "salt_c", "conductivity2salinity"]

module_logger = logging.getLogger(__name__)

# TODO: inverse salinity2conductiviy
# TODO: uniformisation of variable name
def freezingtemp(s, p=10.1325, validity=True):
    """
        Computes freezing temperature of seawater [degree C]

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
            UNESCO (1978) Eighth Report of the Joint Panel on Oceanographic Tables and Standards UNESCO Technical Papers
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
    Returns conductivity of sea water at salinity s = 35 PSU, temperature T = 15 C and pressure p = 0 dbar in mS/cm

    :return: ndarray
        Conductivity of sea water at s = 35 PSU, T = 15 C and p = 0 in mS/cm
    """
    return np.array(42.914)


def salrp(R, T, P):
    """
    Computes equation Rp(S,T,P) = C(S,T,P)/C(S,T,0) used in calculating salinity in UNESCO 1983 polynomial

    :param R:
        Conductivity ratio  R = C(S,T,P)/C(35,15,0) [no units]

    :param T:
        temperature [degree C (IPTS-68)]

    :return P:
        pressure [dbar]

    :references:
        Equation 4 (p.8)
        Fofonoff, P. and Millard, R.C. Jr, Unesco 1983. Algorithms for computation of fundamental properties of seawater,
            1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.
    """

    if isinstance(R, (int, float, list)):
        R = np.atleast_1d(R)
    if isinstance(T, (int, float, list)):
        T = np.atleast_1d(T)
    if isinstance(P, (int, float, list)):
        P = np.atleast_1d(P)

    if R.shape != T.shape or R.shape != P.shape or T.shape != P.shape:
        module_logger.error('s, p, t must all have the same dimensions')
        return 0

    d1 = 3.426e-2
    d2 = 4.464e-4
    d3 = 4.215e-1
    d4 = -3.107e-3

    e1 = 2.070e-5
    e2 = -6.370e-10
    e3 = 3.989e-15

    Rp = 1 + (P * (e1 + e2 * P + e3 * P**2))/(1 + d1 * T + d2 * T**2 + (d3 + d4 * T) * R)

    return Rp


def salrp_c(C, T, P):
    """
    Computes equation Rp(S,T,P) = C(S,T,P)/C(S,T,0) used in calculating salinity in UNESCO 1983 polynomial

    :param R:
        Conductivity C [mS/cm]

    :param T:
        temperature [degree C (IPTS-68)]

    :return P:
        pressure [dbar]

    :references:
        Equation 4 (p.8)
        Fofonoff, P. and Millard, R.C. Jr, Unesco 1983. Algorithms for computation of fundamental properties of seawater,
            1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.
    """

    if isinstance(C, (int, float, list)):
        C = np.atleast_1d(C)
    if isinstance(T, (int, float, list)):
        T = np.atleast_1d(T)
    if isinstance(P, (int, float, list)):
        P = np.atleast_1d(P)

    if C.shape != T.shape or C.shape != P.shape or T.shape != P.shape:
        module_logger.error('s, p, t must all have the same dimensions')
        return 0

    R = C/c3515()
    Rp = salrp(R, T, P)
    return Rp


def salrt(T):
    """
    Computes equation rt(T) = C(35, T, 0)/(35,15,0) used in calculating salinity with UNESCO 1983 polynomial

    :param T: ndarray
        temperature [degree C (ITS-90)]
    :return: ndarray
        conductivity ratio rt(T) at S=35 and p=0

    :check value:
        rt = 1.0000000 for R = 1, T = 15 [degree C] and p = 0 [dbar]
        rt = 1.1164927 for R = 1.2, T = 20 [degree C] and p = 2000 [dbar]
        rt = 0.77956585for R = 0.65, T = 5 [degree C] and p = 1500 [dbar]

    """
    if isinstance(T, (int, float, list)):
        T = np.atleast_1d(T)

    c = [1.0031e-9, -6.9698e-7, 1.104259e-4, 2.00564e-2, 0.6766097]

    rt = np.polyval(c, T)
    return rt


def sals(Rt, T, validity=True):
    """
    Computes salinity of sea water as a function of Rt and T at constant pressure p = 0 dbar
    Validity domain is -2 <= T <= 35 [degree C] and 2 <= S <= 42 [PSU]

    :param Rt: array-like, float
        Conductivity ratio, Rt(S, T) = C(S, T, 0)/C(35, T, 0)
    :param T: array-like, float
        Temperature [degree C (IPTS-68)]
    :param validity: bool
        Validity
    :return S:ndarray float
        salinity [PSU (PSS-78)]

    :References: ndarray
       Fofonoff, P. and Millard, R.C. Jr
       Unesco 1983. Algorithms for computation of fundamental properties of
       seawater, 1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.
    """

    if isinstance(Rt, (int, float, list)):
        Rt = np.atleast_1d(Rt)
    if isinstance(T, (int, float, list)):
        T = np.atleast_1d(T)

    if Rt.shape != T.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    if T[T < -2].any() or T[35 < T].any():
        if validity:
            module_logger.info('For element with salinity out of range -2 < T < 35,  T = np.nan')
            T[T < -2] = np.nan
            T[35 < T] = np.nan
        else:
            module_logger.warning('Some temperature value are out of the validity domain: -2 < T < 35 [C]')

    a = [2.7081, -7.0261, 14.0941, 25.3851, -0.1692, 0.0080]
    b = [-0.0144, 0.0636, -0.0375, -0.0066, -0.0056, 0.0005]
    k = 0.0162

    Rtx = np.sqrt(Rt)
    del_T = T - 15
    del_S = (del_T / (1 + k * del_T)) * np.polyval(b, Rtx)
    S = np.polyval(a, Rtx)
    S = S + del_S

    if S[S < 2].any() or S[42 < S].any():
        if validity:
            module_logger.info('For element with salinity out of range 2 < S < 42,  S = np.nan')
            S[S < 2] = np.nan
            S[42 < S] = np.nan
        else:
            module_logger.warning('Some computed salinity value are out of the validity domain: 2 < S < 42 [PSU])')

    return S


def salt(R, T, P, validity=True):
    """
    Computes salinity from conductivity ratio. UNESCO 1983 polynomial.
    Validity domain is -2 <= T <= 35 [degree C] and 2 <= S <= 42 [PSU]

    :param R: array-like, float
       Conductivity ratio     R =  C(S,T,P)/C(35,15,0) [no units]
    :param T: array-like, float
        temperature [degree C (IPTS-68)]
    :param P: array-like, float
        pressure [dbar]
    :param validity: boolean, Default True
        For all data out of the validity, it returns np.nan if True, value are not overriden if False

    :return S:ndarray float
        salinity [PSU (PSS-78)]

    :check value:
        S = 35.000000 [PSU] for R = 1, T = 15 [degree C] and p = 0 [dbar]
        S = 37.245628 [PSU] for R = 1.2, T = 20 [degree C] and p = 2000 [dbar]
        S = 29.995347 [PSU] for R = 0.65, T = 5 [degree C] and p = 1500 [dbar]
    """

    if isinstance(R, (int, float, list)):
        R = np.atleast_1d(R)
    if isinstance(T, (int, float, list)):
        T = np.atleast_1d(T)
    if isinstance(P, (int, float, list)):
        P = np.atleast_1d(P)

    if R.shape != T.shape or R.shape != P.shape or P.shape != T.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    rt = salrt(T)
    Rp = salrp(R, T, P)
    Rt = R / (Rp * rt)
    S = sals(Rt, T, validity=validity)

    return S


def salt_c(C, T, P, validity=True):
    """
    Computes salinity from conductivity ratio. UNESCO 1983 polynomial.
    Validity domain is -2 <= T <= 35 [degree C] and 2 <= S <= 42 [PSU]

    :param C: array-like, float
        Conductivity [mS/cm]
    :param T: array-like, float
        temperature [degree C (IPTS-68)]
    :param P: array-like, float
        pressure [dbar]
    :param validity: boolean, Default True
        For all data out of the validity, it returns np.nan if True, value are not overriden if False

    :return S:ndarray float
        salinity [PSU (PSS-78)]

    :check value:
        S = 35.000000 [PSU] for C = 42.914, T = 15 [degree C] and p = 0 [dbar]
        S = 37.245628 [PSU] for C = 51.4968, T = 20 [degree C] and p = 2000 [dbar]
        S = 29.995347 [PSU] for C = 27.8941, T = 5 [degree C] and p = 1500 [dbar]
    """

    if isinstance(C, (int, float, list)):
        C = np.atleast_1d(C)
    if isinstance(T, (int, float, list)):
        T = np.atleast_1d(T)
    if isinstance(P, (int, float, list)):
        P = np.atleast_1d(P)

    if C.shape != T.shape or C.shape != P.shape or P.shape != T.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    R = C/c3515()
    rt = salrt(T)
    Rp = salrp(R, T, P)
    Rt = R / (Rp * rt)
    S = sals(Rt, T, validity=validity)

    return S


# aliases:
def conductivity2salinity(C, T, P, validity=True):
    """
    Computes salinity from electrical conductivity . UNESCO 1983 polynomial.
    Validity domain is -2 <= T <= 35 [degree C] and 2 <= S <= 42 [PSU]

    :param C: array-like, float
        Conductivity [mS/cm]
    :param T: array-like, float
        temperature [degree C (IPTS-68)]
    :param P: array-like, float
        pressure [dbar]
    :param validity: boolean, Default True
        For all data out of the validity, it returns np.nan if True, value are not overriden if False

    :return S:ndarray float
        salinity [PSU (PSS-78)]
    """
    if isinstance(C, (int, float, list)):
        C = np.atleast_1d(C)
    if isinstance(T, (int, float, list)):
        T = np.atleast_1d(T)
    if isinstance(P, (int, float, list)):
        P = np.atleast_1d(P)

    if C.shape != T.shape or C.shape != P.shape or P.shape != T.shape:
        module_logger.warning('s, p must all have the same dimensions')
        return 0

    S = salt_c(C, T, P, validity=validity)
    return S


def salinity2conductivity(s):

    # R = C/c3515()
    # rt = salrt(T)
    # Rp = salrp(R, T, P)
    # Rt = R / (Rp * rt)
    # S = sals(Rt, T, validity=validity)

    #sals()
    # a = [2.7081, -7.0261, 14.0941, 25.3851, -0.1692, 0.0080]
    # b = [-0.0144, 0.0636, -0.0375, -0.0066, -0.0056, 0.0005]
    # k = 0.0162
    #
    # Rtx = np.sqrt(Rt)
    # del_T = T - 15
    # del_S = (del_T / (1 + k * del_T)) * np.polyval(b, Rtx)
    # S = np.polyval(a, Rtx)
    # S = S + del_S


    from pynverse import inversefunc

    f = (lambda x : conductivity2salinity(x, 25, 0))

    inversefunc(f, y_values=18.57)

    return S
