#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property.seaice.py contains function to compute physical property relative to the seaice
"""
import logging

import numpy as np

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "0.5"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "RC"
__date__ = "2017/09/13"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]
__name__ = "si"
__all__ = ["air_volume_fraction", 'brine_volume_fraction', "density", "electric_conductivity", "latentheat",
           "permeability", "", "resistivity", "specific_heat_capacity", "thermal_conductivity", "thermal_diffusivity"]

logger = logging.getLogger(__name__)

from seaice.property import ice
from seaice.property import brine


def air_volume_fraction(s, t, rho_si='default'):
    """
    Calculates air volume fraction in sea ice [-, unitless]
    If no sea ice density value are given, it will return 0.005, the air volume fraction expected in 1st year sea ice,
    before warming.
    s, t, rho_si must have the same dimension

    :param s : array_like, float
        Salinity [PsU]
    :param t : array_like, float
        Temperature [degree C]
    :param rho_si : float, array_like, 'default', optional
        Density of the ice [kg/m3]. By default, rho_si computed from s, t.

    :return vf_a: ndarray float
        The calculated air volume fraction array [-, unitless]

    :references :
    Equation 14 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice
        samples. Journal of Glaciology (Vol. 29, pp. 306–316).
    """

    # check array lengths
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = 999

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)

    if rho_si is 'default':
        logger.info('rho_si computed from t and s')
        rho_si = density(s, t)
    elif isinstance(rho_si, (int, float, list)):
        rho_si = np.atleast_1d(rho_si).astype(float)
    if rho_si.size == 1:
        rho_si = rho_si*np.ones_like(s)

    if t.shape != s.shape or t.shape != rho_si.shape or s.shape != rho_si.shape:
        logger.warning('s, t, rho_si must all have the same dimensions')
        return 0

    # Physical constant
    a = np.empty((4, 4, 2))

    # coefficient for -2t<=0
    a[0, 0, :] = [-0.041221, 0.090312]
    a[0, 1, :] = [-18.407, -0.016111]
    a[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
    a[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

    # coefficient for -22.9<t<=-2
    a[1, 0, :] = [-4.732, 0.08903]
    a[1, 1, :] = [-22.45, -0.01763]
    a[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
    a[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

    # coefficient for -30<t<=-22.9
    a[2, 0, :] = [9899, 8.547]
    a[2, 1, :] = [1309, 1.089]
    a[2, 2, :] = [55.27, 0.04518]
    a[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

    b = np.empty((3, 2))
    b[0] = [-2, 0]
    b[1] = [-22.9, -2]
    b[2] = [-30, -22.9]

    rho_i = ice.density(t)

    f1 = np.nan * t
    f2 = np.nan * t
    for mm in range(0, 3):
        p1 = [a[mm, 3, 0], a[mm, 2, 0], a[mm, 1, 0], a[mm, 0, 0]]
        p2 = [a[mm, 3, 1], a[mm, 2, 1], a[mm, 1, 1], a[mm, 0, 1]]

        f1[(b[mm, 0] <= t) & (t <= b[mm, 1])] = np.polyval(p1, t[(b[mm, 0] <= t) & (t <= b[mm, 1])])
        f2[(b[mm, 0] <= t) & (t <= b[mm, 1])] = np.polyval(p2, t[(b[mm, 0] <= t) & (t <= b[mm, 1])])

    vf_a = 1 - rho_si/rho_i + rho_si*s*f2 / f1*1e-3

    return vf_a


def brine_volume_fraction(s, t, rho_si='default', vf_a=0.0005, method='cw'):
    """
    Calculate the volume fraction of brine [-, unitless]

    Parameters
    ----------
    :param t : array_like, float
        Temperature [degree C]
        If t is an array, s float be an array of the same length.
    :param s : array_like, number
        Salinity [PsU]
        If s is an array, t should be an array of the same length.
    :param rho_si : float, array_like, 'default', optional
        Density of the ice [kg/m3]. The default is calculated from s, t.
        If rho_si is an array, rho_si, s, t must have the same length.
    :param vf_a: float, array_like, optional
        Air volume fraction content of sea ice.
        Default is 0.5‰, representative of 1st year sea ice before spring warming.
        If vf_a is an array, vf_a, s, t must have the same length.
    :param method: 'cw', 'fg', 'fg-simplified', default 'cw'
        Brine volume fraction can be computed with Cox and Weeks ('cw'), with Frankenstein-Garner full or simplified method
        ('fg', 'fg-simplified'). Cf. sources

    :return vf_b: ndarray
        The calculated volume fraction of brine in the sea ice [-, unitless]

    :sources:
    thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
    Equation 5 and 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes
        in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).
    Frankenstein, G., Garner, R., 1967. Equations for determining the brine volume of sea ice from −0.5 to −22.9 C,
        Journal of Glaciology (Vol. 6, pp. 943–944).
    """
    # check parameters
    if isinstance(t, (int, float, list, np.ndarray)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = 999

    if isinstance(s, (int, float, list, np.ndarray)):
        s = np.atleast_1d(s).astype(float)

    if isinstance(vf_a, (int, float, list, np.ndarray)):
        vf_a = np.atleast_1d(vf_a).astype(float)
    if vf_a.size == 1:
        logger.info('Air volume fraction set to 0.0005')
        vf_a = vf_a * np.ones_like(s).astype(float)

    if rho_si is 'default':
        logger.info('rho_si computed from t and s')
        rho_si = density(s, t)
    elif isinstance(rho_si, (int, float)):
        rho_si = rho_si * np.ones_like(s)
    elif isinstance(rho_si, (list, np.ndarray)):
        rho_si = rho_si.astype(float)

    ## Check for rho_si, t, S --> vf_a
    if t.shape != s.shape or t.shape != vf_a.shape or t.shape != rho_si.shape or s.shape != rho_si.shape or \
                    s.shape != vf_a.shape or rho_si.shape != vf_a.shape:
        logger.warning('s, t, rho_si, vf_a must all have the same dimensions')
        return 0

    if method == 'fg':
        tlim = [-0.5, -2.06, -8.2, -22.9]
        a = [[52.56, -2.28], [45.917, 0.930], [43.795, 1.189]]
        vf_b = np.nan*np.ones_like(t)

        vf_b[(tlim[1] < t) & (t <= tlim[0])] = s[(tlim[1] < t) & (t <= tlim[0])] * (a[0][0] / np.abs(t[(tlim[1] < t) & (t <= tlim[0])]) + a[0][1])
        vf_b[(tlim[2] < t) & (t <= tlim[1])] = s[(tlim[2] < t) & (t <= tlim[1])] * (a[1][0] / np.abs(t[(tlim[2] < t) & (t <= tlim[1])]) + a[1][1])
        vf_b[(tlim[3] <= t) & (t <= tlim[2])] = s[(tlim[3] <= t) & (t <= tlim[2])] * (a[2][0] / np.abs(t[(tlim[3] <= t) & (t <= tlim[2])]) + a[2][1])
        vf_b = vf_b/1000

    elif method == 'fg-simplified':
        tlim = [-0.5, -22.9]
        a = [49.18, 0.53]
        vf_b = np.nan*np.ones_like(t)
        vf_b[(tlim[1] < t) & (t <= tlim[0])] = s[(tlim[1] < t) & (t <= tlim[0])] * (a[0] / np.abs(t[(tlim[1] < t) & (t <= tlim[0])]) + a[1])
        vf_b = vf_b/1000

    else:
        # Physical constant
        a = np.empty((4, 4, 2))

        # coefficient for -2t<=0
        a[0, 0, :] = [-0.041221, 0.090312]
        a[0, 1, :] = [-18.407, -0.016111]
        a[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
        a[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

        # coefficient for -22.9<t<=-2
        a[1, 0, :] = [-4.732, 0.08903]
        a[1, 1, :] = [-22.45, -0.01763]
        a[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
        a[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

        # coefficient for -30<t<=-22.9
        a[2, 0, :] = [9899, 8.547]
        a[2, 1, :] = [1309, 1.089]
        a[2, 2, :] = [55.27, 0.04518]
        a[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

        b = np.empty((3, 2))
        b[0] = [-2, 0]
        b[1] = [-22.9, -2]
        b[2] = [-30, -22.9]

        vf_a = air_volume_fraction(s, t, rho_si)
        rho_i = ice.density(t)

        f1 = np.nan * t
        f2 = np.nan * t
        for mm in range(0, 3):
            p1 = [a[mm, 3, 0], a[mm, 2, 0], a[mm, 1, 0], a[mm, 0, 0]]
            p2 = [a[mm, 3, 1], a[mm, 2, 1], a[mm, 1, 1], a[mm, 0, 1]]

            f1[(b[mm, 0] <= t) & (t <= b[mm, 1])] = np.polyval(p1, t[(b[mm, 0] <= t) & (t <= b[mm, 1])])
            f2[(b[mm, 0] <= t) & (t <= b[mm, 1])] = np.polyval(p2, t[(b[mm, 0] <= t) & (t <= b[mm, 1])])

        vf_b = ((1 - vf_a) * rho_i * s * 1e-3 / (f1 - rho_i * s * f2 * 1e-3))

    return vf_b


def density(s, t, vf_a=0.005):
    """
        Calculates density of sea water [kg/m3]

        :param t : array_like, float
            Temperature [degree °C]
            If t is an array, s, t must be the same length
        :param s : array_like, float
            Salinity [PSU]
            If s is an array, s, t must be the same length
        :param vf_a : optional, array_like, float. Default 0.005
            Air volume fraction [-, unitless]
            Default value is 0.5‰, representative of 1st year sea ice before spring warming. If Vf_a is an array, vf_a,
            t and s must be the same length.

        :return rho_si: ndarray
            density of the brine [kg/m3]

        :source :
        Equation 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea
        ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).
        Coefficient form Cox & Weeks (1983)  and Leppäranta & Manninen (1988) [Leppäranta, M. & Manninen, t. (1988), the
        brine an gas content of sea ice with attention to low salinities and high temperatures. Finnish Institute of
        Marien Research Internal Report 88-2, Helsinki.
    """

    # check parameters
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d([t]).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = 999  # use 999 rather np.nan

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)

    if isinstance(vf_a, (int, float, list)):
        vf_a = np.atleast_1d(vf_a).astype(float)
    if vf_a.size == 1:
        vf_a = vf_a * np.ones_like(t)

    if t.shape != s.shape or t.shape != vf_a.shape or s.shape != vf_a.shape:
        logger.warning('s, t, vf_a must all have the same dimensions unless vf_a is a singleton')
        return 0

    # Physical constant
    a = np.empty((4, 4, 2))

    # coefficient for -2t<=0
    a[0, 0, :] = [-0.041221, 0.090312]
    a[0, 1, :] = [-18.407, -0.016111]
    a[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
    a[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

    # coefficient for -22.9<t<=-2
    a[1, 0, :] = [-4.732, 0.08903]
    a[1, 1, :] = [-22.45, -0.01763]
    a[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
    a[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

    # coefficient for -30<t<=-22.9
    a[2, 0, :] = [9899, 8.547]
    a[2, 1, :] = [1309, 1.089]
    a[2, 2, :] = [55.27, 0.04518]
    a[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

    b = np.empty((3, 2))
    b[0] = [-2, 0]
    b[1] = [-22.9, -2]
    b[2] = [-30, -22.9]

    rho_i = ice.density(t) * 1e-3

    f1 = np.nan * t
    f2 = np.nan * t
    for mm in range(0, 3):
        p1 = [a[mm, 3, 0], a[mm, 2, 0], a[mm, 1, 0], a[mm, 0, 0]]
        p2 = [a[mm, 3, 1], a[mm, 2, 1], a[mm, 1, 1], a[mm, 0, 1]]

        f1[(b[mm, 0] <= t) & (t <= b[mm, 1])] = np.polyval(p1, t[(b[mm, 0] <= t) & (t <= b[mm, 1])])
        f2[(b[mm, 0] <= t) & (t <= b[mm, 1])] = np.polyval(p2, t[(b[mm, 0] <= t) & (t <= b[mm, 1])])

    rho_si = ((1 - vf_a) * (rho_i*f1 / (f1 - rho_i*s*f2)))

    return rho_si * 10 ** 3  # rho_si in SI, kg m^{-3}


def electric_conductivity(s, t, rho_si='default', vf_a=0.005):
    """
    Calculate the electric conductivity of sea ice for a given temperature and salinity

    :param t: array_like, float
        temperature of the sea ice in degree Celsius [°C]
    :param s: array_like, float
        bulk salinity of the sea ice in practical salinity unit [PsU]
    :param rho_si: optional, array_like, float, 'default'. Default: 'default
        density of the ice in gram per cubic centimeter [g cm^{-3}]. Default value is computed from t and s
        If rho_si is an array, rho_si, s, t must have the same length.
    :param vf_a: float, array_like, optional, float
        Air volume fraction content of sea ice.
        The default is 0.005, representative of 1st year sea ice before spring warming.
        If vf_a is an array, vf_a, s, t must have the same length.

    :return sigma_si: ndarray
        conductivity of seaice in microsiemens/meter [S/m]

    :source :
    Ingham, M., Pringle, D. J., & Eicken, H. (2008). Cross-borehole resistivity tomography of sea ice. Cold Regions
    Science and Technology, 52(3), 263–277. http://doi.org/10.1016/j.coldregions.2007.05.002
    """
    # check array lengths
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = np.nan

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)

    if rho_si is 'default':
        logger.info('rho_si computed from t and s')
        rho_si = density(s, t)
    elif isinstance(rho_si, (int, float, list)):
        rho_si = np.atleast_1d(rho_si).astype(float)
    if rho_si.size == 1:
        rho_si = rho_si*np.ones_like(s)

    if isinstance(vf_a, (int, float, list)):
        vf_a = np.atleast_1d(vf_a).astype(float)
    if vf_a.size == 1:
        vf_a = vf_a * np.ones_like(s)

    if t.shape != s.shape or t.shape != vf_a.shape or t.shape != rho_si.shape or s.shape != rho_si.shape or \
                    s.shape != vf_a.shape or rho_si.shape != vf_a.shape:
        logger.warning('s, t, rho_si, vf_a must all have the same dimensions')
        return 0

    sigma_b = brine.electric_conductivity(t)
    vf_b = brine_volume_fraction(s, t, rho_si=rho_si, vf=vf_a)

    sigma_si = sigma_b*vf_b**2.88

    return sigma_si


def latentheat(s, t, transformation='solidification', s0=35.):
    """
        Calculates latent heat of sea ice during solidification (freezing, f) or melting (m).

        :param t : float array_like, float
            temperature [degree C]
            If t is an array, s should be an array of the same length
        :param s : array_like, float
            salinity [PSU]
            If s is an array, t should be an array of the same length
        :param transformation : optional, 'solidification' or 'fusion'. Default: 'solidification'
            Phase transformation solidification ('freezing') or fusion ('melting').
        :param s0 : optional, float
            Initial salinity of the liquid [PSU].
            Only use to calculate the latent heat of solidification, if we assume T_f = m_m*s0. Default is 35 [PSU]
        :return l_si: ndarray
            latent heat of sea ice [J/g]

        :source :
        Equation 2.27 and 2.29 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

    """

    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = np.nan

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)

    if isinstance(s0, (int, float, list)):
        s0 = np.atleast_1d(s0).astype(float)
    if s0.size == 1:
        s0 = s0 * np.ones_like(s)

    if t.shape != s.shape or t.shape != s0.shape or s.shape != s0.shape:
        logger.warning('s, t, s0 must all have the same dimensions, unless s0 is a singleton')
        return 0

    # Pysical Constant
    lwater = 333.4  # [kJ/kg] latent heat of fusion of freshwater
    m_m = -0.05411  # [K]  slope of the liquid
    c_i = 2.11  # [kJ/kgK] specific heat capacity of ice @ 0°C
    c_w = 4.179  # [kJ/kgK] specific heat capacity of freshwater @ 0°C

    if transformation in ['freezing', 'solidificaiton']:
        l_si = lwater - c_i * t + c_i * m_m * s - m_m * lwater * (s / t) + c_w * m_m * (s0 - s)
    elif transformation in ['fusion', 'melting']:
        l_si = lwater - c_i * t + c_i * m_m * s - m_m * lwater * (s / t)
    else:
        logger.warning('Phase transformation undefined')
        return 0

    return l_si


def permeability_from_porosity(p):
    """
        Calculate sea ice permeability k in function of sea ice porosoty (-), according to Golden et al. hierarchical
        model for columnar sea ice.

        :param p : array_like, float
            sea ice porosity (-)

        :return k: ndarray
            permeability [m2, unitless]

        :source :
            Equation 5  in K. Golden, H. Eicken, A.L. Heaton, J.Miner, D.J. Pringle, J. Zhu (2007) Thermal Evolution of
            Permeability, Geophysical Research Letters, 34, doi:10.1029/2007GL030447

    """
    if isinstance(p, (int, float, list)):
        p = np.atleast_1d(p).astype(float)

    k = 3 * p**3*1e-8

    return k


def permeability(s, t, rho_si='default', vf_a=0.005):
    """
        Calculate sea ice permeability k in function of temperature (°C) and salinity (PSU), according to Golden et al.
        hierarchical model for columnar sea ice.

        :param t : array_like, float
            temperature [degree °C]
            If t is an array, s, t must be of same length
        :param s : array_like, float
            salinity in practical salinity unit [PsU]
            If s is an array, s, t must be of same length
        :param rho_si : optional, array_like, float or 'default'. Default: 'default'
            denstiy of sea ice [kg/m3].
            If default, rho_si is computed from t and s. If rho_si is an array, rho_si, s, t must be of same length
        :param vf_a: optional, float, Default: 0.005
            air volume fraction of sea ice. Default value is 0.5‰, representative of 1st year sea ice before spring
            warming. If rho_si is an array, vf_a, s, t must have the same length.

        :return k: ndarray
            permeability [m2, unitless]

        :source :
            Equation 5  in K. Golden, H. Eicken, A.L. Heaton, J.Miner, D.J. Pringle, J. Zhu (2007) Thermal Evolution of
            Permeability, Geophysical Research Letters, 34, doi:10.1029/2007GL030447

    """
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = 999

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)

    if rho_si is 'default':
        logger.info('rho_si computed from t and s')
        rho_si = density(s, t)
    elif isinstance(rho_si, (int, float, list)):
        rho_si = np.atleast_1d(rho_si).astype(float)
    if rho_si.size == 1:
        rho_si = rho_si*np.ones_like(s)

    if isinstance(vf_a, (int, float, list)):
        vf_a = np.atleast_1d(vf_a).astype(float)
    if vf_a.size == 1:
        vf_a = vf_a * np.ones_like(s)

    if t.shape != s.shape or t.shape != vf_a.shape or t.shape != rho_si.shape or s.shape != rho_si.shape or \
                    s.shape != vf_a.shape or rho_si.shape != vf_a.shape:
        logger.warning('s, t, rho_si, vf_a must all have the same dimensions')
        return 0

    k = permeability_from_porosity(brine_volume_fraction(s, t, rho_si, vf_a=vf_a))

    return k


def resistivity(s, t, rho_si='default', vf_a=0.005):
    """
    Return electric resistivity of sea ice at a given temperature and salinity [s/m == us/m]

    :param t : array_like, float
        temperature in degree Celsius [°C]
    :param s : array_like, float
        salinity in practical salinity unit [PsU]
    :param rho_si : optional, array_like, float or 'default'. Default: 'default'
        denstiy of sea ice [kg/m3].
        If default, rho_si is computed from t and s. If rho_si is an array, rho_si, s, t must be of same length
    :param vf_a: float, array_like, optional, float
        Air volume fraction content of sea ice.
        The default is 0.005, representative of 1st year sea ice before spring
        warming.
        If vf_a is an array, vf_a, s, t must have the same length.

    :return rhoel_si: ndarray
        resistiviy of seaice in microsiemens/meter [s/m]


    :source :
    Ingham, M., Pringle, D. J., & Eicken, H. (2008). Cross-borehole resistivity tomography of sea ice. Cold Regions
    Science and Technology, 52(3), 263–277. http://doi.org/10.1016/j.coldregions.2007.05.002
    """

    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = np.nan

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)

    if rho_si is 'default':
        logger.info('rho_si computed from t and s')
        rho_si = density(s, t)
    elif isinstance(rho_si, (int, float, list)):
        rho_si = np.atleast_1d(rho_si).astype(float)
    if rho_si.size == 1:
        rho_si = rho_si*np.ones_like(s)

    if isinstance(vf_a, (int, float, list)):
        vf_a = np.atleast_1d(vf_a).astype(float)
    if vf_a.size == 1:
        vf_a = vf_a * np.ones_like(s)

    if t.shape != s.shape or t.shape != vf_a.shape or t.shape != rho_si.shape or s.shape != rho_si.shape or \
                    s.shape != vf_a.shape or rho_si.shape != vf_a.shape:
        logger.warning('s, t, rho_si, vf_a must all have the same dimensions')
        return 0

    rhoel_si = 1/electric_conductivity(s, t, rho_si=rho_si, vf_a=vf_a)

    return rhoel_si


def heat_capacity(s, t, method='untersteiner'):
    """
        Calculate heat capacity of sea ice in function of temperature and salinity

        :param t : array_like, float
            temperature [degree C]
            If t is an array, s, tmust be of same length
        :param s : array_like, float
            salinity [PsU]
            If s is an array, s, t must be of same length
        :param method : optional, 'untersteiner' or 'ono, Default:'untersteiner'
            Thermal conductivity can be calculate either from 'untersteiner' or 'ono' approach

        :return c_si: ndarray
            sea ice heat capacity [J/kgK]

        :references:
            Equation 2.18 and 2.19 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional
            scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea
            ice. London:
            Wiley-Blackwell
            Understeiner, N. (1961) Natural desalination and equilibrium salinity profile
            of perennial sea ice. Journal of Geophysical Research, 73, 1251-1257
            Equation (16) Ono, N. (1967). specific heat and heat of fusion of sea ice. In Physic of snow and Ice (H.
            Oura., Vol. 1, pp. 599–610).
    """

    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = np.nan

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)

    if t.shape != s.shape:
        logger.warning('s, t must all have the same dimensions')
        return 0

    # Pysical Constant
    c_i = 2.11  # [kJ/kgK] specific heat capacity of ice @ 0°C

    c_si = np.nan * np.ones_like(t)

    if method == 'untersteiner':
        a = 17.2  # [kJ/kgK]
        c_si = c_i + a * s / (t ** 2)

    elif method == 'ono':
        beta = 7.5 * 1e-3  # [kJ/kgK^2]
        lice = 333.4  # [kJ/kg] latent heat of fusion of freshwater
        m_m = -0.05411  # [K]  slope of the liquid

        c_si = c_i + beta * t - m_m * lice * s / (t ** 2)

    return c_si * 10 ** 3  # return [J/gK]


def specific_heat_capacity(s, t, method='untersteiner'):
    """
        Calculate specific heat capacity of sea ice in function of temperature and salinity

        :param t : array_like, float
            temperature [degree C]
            If t is an array, s, tmust be of same length
        :param s : array_like, float
            salinity [PsU]
            If s is an array, s, t must be of same length
        :param method : optional, 'untersteiner' or 'ono, Default:'untersteiner'
            Thermal conductivity can be calculate either from 'untersteiner' or 'ono' approach

        :return c_si: ndarray
            sea ice heat capacity [J/kgK^2]

        :references:
            Equation 2.18 and 2.19 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional
            scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea
            ice. London:
            Wiley-Blackwell
            Understeiner, N. (1961) Natural desalination and equilibrium salinity profile
            of perennial sea ice. Journal of Geophysical Research, 73, 1251-1257
            Equation (16) Ono, N. (1967). specific heat and heat of fusion of sea ice. In Physic of snow and Ice (H.
            Oura., Vol. 1, pp. 599–610).
    """

    c = heat_capacity(s, t, method=method)  # [J/kgK]
    rho = density(s, t)  # kg/m3

    return c * rho  # J/Km3


def thermal_conductivity(s, t, method='pringle', vf_a=0.005):
    """
        Calculates bulk thermal conductivity of sea ice in function of temperautre and salinity.s

        :param t : array_like, float
            Temperature [degree C]
            If t is an array, s should be an array of the same length
        :param s : array_like, float
            Salinity [PsU]
            If s is an array, t should be an array of the same length
        :param method : 'pringle' or 'maykut'.
            * 'pringle' :
            * 'maykut' :
            Default is 'pringle'
        :param vf_a: float, array_like, optional, float
            Air volume fraction content of sea ice. The default is 0.005, representative of 1st year sea ice before spring
            warming.
            If vf_a is an array, vf_a, s, t must have the same length.

        :return lambda_si ndarray
            seaice thermal conductivity [W/mK]

        :sources:
        Equation 2.14 and 2.16 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale:
        growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London:
        Wiley-Blackwell
        Pringle method is describe in Pringle, D. J., Eicken, H., trodahl, H. J., & Backstrom, L. G. E. (2007). thermal
        conductivity of landfast Antarctic and Arctic sea ice. Journal of Geophysical Research, 112(C4), C04017.
        doi:10.1029/2006JC003641
        Maykut method is describe in Maykut, G. A. (1986). the surface heat and mass balance. In N. Understeiner (Ed.),
        the geophysics of sea ice (pp. 395–463). Dordrecht (NAtO AsI B146): Martinus Nijhoff Publishers.
    """

    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = np.nan

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s)

    if isinstance(vf_a, (int, float, list)):
        vf_a = np.atleast_1d(vf_a).astype(float)
    if vf_a.size == 1:
        vf_a = vf_a * np.ones_like(s)

    if t.shape != s.shape or t.shape != vf_a.shape or s.shape != vf_a.shape:
        logger.warning('s, t, vf_a must all have the same dimensions unless vf_a is a singleton')
        return 0

    if method == 'maykut':
        # Physical constant
        a = 0.13
        lambda_si = ice.thermal_conductivity(t) + a * s / t
        return lambda_si

    elif method == 'pringle':
        rho_si = density(s, t, vf_a=vf_a)
        rho_i = ice.density(t)
        lambda_si = rho_si / rho_i * (2.11 - 0.011*t + 0.09*s/t - (rho_si - rho_i)*1e-3)
        return lambda_si


def thermal_diffusivity(s, t, method_l='pringle', method_cp='untersteiner', rho_si='default', vf_a=0.005):
    """
        Calculates the thermal diffusivity of sea ice in function of temperature or salinity. 'prindle' (default) or
        'ono' method could be chosen to compute latent heat and 'untersteiner' or 'maykut' method could be chosen to
        compute specific heat capacity.

        :param t : array_like, float
            temperature [degree C]
            If t is an array, s should be an array of the same length
        :param s : array_like, float
            salinity [PsU]
            If s is an array, t should be an array of the same length
        :param method_l : 'pringle', 'maykut'. Default: prindle
            Compute thermal conductivity according to 'pringle' or 'maykut'
        :param method_cp : 'untersteiner', 'ono'. Default:'untersteiner'
            Compute specific heat capacity according to 'unterseiner' or 'ono'
        :param vf_a: optional, float, Default: 0.005
            air volume fraction of sea ice. Default value is 0.5‰, representative of 1st year sea ice before spring
            warming. If rho_si is an array, vf_a, s, t must have the same length.
        :param rho_si : optional, array_like, float, Default
            density of the ice in gram per cubic centimeter [kg/m3]. Defautl value is computed from t and s..
            If rho_si is an array, rho_si, s, t must have the same length.

        :return sigma_si:
            thermal diffusivity of sea ice [m2/s]

        :source :
            material thermal diffusivity is given by sigma = lambda/(rho c_p)

    """
    if isinstance(t, (int, float, list)):
        t = np.atleast_1d(t).astype(float)
    if (t > 0).any():
        logger.warning('Some element of t > 0°C. Replacing them with nan-value')
        t = t.copy()
        t.loc[t > 0] = np.nan

    if isinstance(s, (int, float, list)):
        s = np.atleast_1d(s).astype(float)

    if rho_si is 'default':
        logger.info('rho_si computed from t and s')
        rho_si = density(s, t)
    elif isinstance(rho_si, (int, float, list)):
        rho_si = np.atleast_1d(rho_si).astype(float)
    if rho_si.size == 1:
        rho_si = rho_si*np.ones_like(s)

    if isinstance(vf_a, (int, float, list)):
        vf_a = np.atleast_1d(vf_a).astype(float)
    if vf_a.size == 1:
        vf_a = vf_a * np.ones_like(s)

    if t.shape != s.shape or t.shape != vf_a.shape or t.shape != rho_si.shape or s.shape != rho_si.shape or \
                    s.shape != vf_a.shape or rho_si.shape != vf_a.shape:
        logger.warning('s, t, rho_si, vf_a must all have the same dimensions')
        return 0

    sigma_si = thermal_conductivity(s, t, method=method_l, vf_a=vf_a) /\
               (specific_heat_capacity(s, t, method=method_cp) * density(s, t, vf_a=vf_a))

    return sigma_si


