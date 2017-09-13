#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
property/seaice.py contains function to compute physical property relative to the seaice
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
si_prop_list = {'brine volume fraction': 'brine volume fraction',
                'vbf': 'brine volume fraction', 'vb': 'brine volume fraction',
                'seaice permeability': 'seaice permeability', 'k': 'seaice permeability'}
si_prop_unit = {'salinity': '-',
                'temperature': '°C',
                'vb': '-', 'brine volume fraction': '-',
                'seaice permeability': 'm$^{-2}$'}
si_prop_latex = {'salinity': 'S',
                 'temperature': 'T',
                 'brine volume fraction': '\phi_{B}',
                 'ice thickness': 'h_{i}',
                 'snow thickness': 'h_{s}',
                 'seaice permeability': '\kappa'
                 }

def thermal_conductivity(t, s, method='pringle', flag_comment='y'):
    """
		Calculate bulk thermal conductivity of sea ice

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
			If t is an array, s should be an array of the same length
		s : array_like, number
			salinity in practical salinity unit [PsU]
			If s is an array, t should be an array of the same length
		method : optional, string
			thermal conductivity could be either calculated with Maykut or Pringle equation

		Returns
		----------
		lambda_si ndarray
		    seaice thermal conductivity W m^{-1] K^{-1]

		sources
		----------
		Equation 2.14 and 2.16 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		Pringle method is describe in Pringle, D. J., Eicken, H., trodahl, H. J., & Backstrom, L. G. E. (2007). thermal conductivity of landfast Antarctic and Arctic sea ice. Journal of Geophysical Research, 112(C4), C04017. doi:10.1029/2006JC003641

		Maykut method is describe in Maykut, G. A. (1986). the surface heat and mass balance. In N. Understeiner (Ed.), the geophysics of sea ice (pp. 395–463). Dordrecht (NAtO AsI B146): Martinus Nijhoff Publishers.
	"""
    import numpy as np

    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s = np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print('t and s profile should be the same size')

    lambda_si = np.nan * t

    if method == 'maykut':
        # Physical constant
        A = 0.13

        lambda_si[np.where(t < 0)] = (
            ice_thermal_conductivity(t[np.where(t < 0)]) + A * s[np.where(t < 0)] / t[np.where(t < 0)])

    elif method == 'pringle':
        rho_si = seaice_density(t, s, flag_comment='n') / 10 ** 3  # density in g cm^{-3}
        rho_i = ice_density(t, flag_comment='n') / 10 ** 3  # density in g cm^{-3}

        lambda_si[(t < 0)] = rho_si[(t < 0)] / rho_i[(t < 0)] * (
            2.11 - 0.011 * t[(t < 0)] + 0.09 * s[(t < 0)] / t[(t < 0)] - (
                rho_si[(t < 0)] - rho_i[(t < 0)]) / 1000)

    if flag_comment == 'y':
        if flag_comment == 'y':
            if np.count_nonzero(np.where(t > 0)):
                print('Some conductivity value are not define. Temperature above 0°C')
    return lambda_si


def specific_heat_capacity(t, s, method='Untersteiner', flag_comment='y'):
    """
        Calculate specific heat capacity of sea ice

        Parameters
        ----------
        t : array_like, number
            temperature in degree Celsius [°C]
            If t is an array, s should be an array of the same length
        s : array_like, number
            salinity in practical salinity unit [PsU]
            If s is an array, t should be an array of the same length
        method : optional, string
            thermal conductivity could be either calculated with Maykut or Pringle equation

        Returns
        ----------
        c_si ndarray
            sea ice specific heat capacity (J kg^{-1}K^{-1})

        sources
        ----------
        Equation 2.18 and 2.19 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

        Untersteiner method is describe in Understeiner, N. (1961) Natural desalination and equilibrium salinity profile of perennial sea ice. Journal of Geophysical Research, 73, 1251-1257

        Maykut method is describe in Maykut, G. A. (1986). the surface heat and mass balance. In N. Understeiner (Ed.), the geophysics of sea ice (pp. 395–463). Dordrecht (NAtO AsI B146): Martinus Nijhoff Publishers.
    """
    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s = np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print("Salinity and temperature array should be the same size")

    # Pysical Constant
    c_i = 2.11  # [kJ kg^{-1}K^{-1}] specific heat capacity of ice @ 0°C

    c_si = np.nan * np.array(t)

    if method == 'Untersteiner':
        A = 17.2  # [kJ kg^{-1}K^{-1}]
        c_si[t < 0] = c_i + A * s[t < 0] / t[t < 0] ** 2

    elif method == 'Ono':
        beta = 7.5 * 10 ** -3  # (kJ kg^{-1}K^{-2})
        L = 333.4  # (J kg^{-1}) latent heat of fusion of freshwater
        m_m = -0.05411  # (K)  slope of the liquid

        c_si[t < 0] = c_i + beta * t[t < 0] - m_m * L * s[t < 0] / t[t < 0] ** 2

    return c_si * 10 ** 3


def thermal_diffusivity(t, s, method='default', flag_comment='y'):
    """
        Calculate specific heat capacity of sea ice

        Parameters
        ----------
        t : array_like, number
            temperature in degree Celsius [°C]
            If t is an array, s should be an array of the same length
        s : array_like, number
            salinity in practical salinity unit [PsU]
            If s is an array, t should be an array of the same length
        method : optional, string
            both sea ice specitic heat capacity and thermal conductivity
            default use Understeiner method for specific heat capacity and Pringle method for thermal conductivity

        Returns
        ----------
        sigma_si ndarray
            sea ice specific heat capacity m^{2} s^{-1}

        sources
        ----------
            material thermal diffusivity is given by sigma = lambda/(rho c_p)
    """
    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s = np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print("Salinity and temperature array should be the same size")

    sigma_si = seaice_thermal_conductivity(t, s) / (seaice_specific_heat_capacity(t, s) * seaice_density(t, s))

    return sigma_si


def latentheat(t, s, transformation='fusion'):
    """
		Calculate bulk latent heat from temperature and salinity during freezing ('f') or melting ('m')

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
			If t is an array, s should be an array of the same length
		s : array_like, number
			salinity in practical salinity unit [PsU]
			If s is an array, t should be an array of the same length
		transformation : optional, string
			direction of the phase transformation: solidification ('freezing') or fusion ('melting')
			default phase transformation is solidification

		Returns
		----------
		L_si: ndarray
			sea Ice latent heat of fusion

		sources
		----------
		Equation 2.28 and 2.29 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		from Equation (16) Ono, N. (1967). specific heat and heat of fusion of sea ice. In Physic of snow and Ice (H. Oura., Vol. 1, pp. 599–610).

	"""
    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s = np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print("Salinity and temperature array should be the same size")

    # Pysical Constant
    L = 333.4  # [kJ kg^{-1}] latent heat of fusion of freshwater
    m_m = -0.05411  # [K]  slope of the liquid
    c_i = 2.11  # [kJ kg^{-1}K^{-1}] specific heat capacity of ice @ 0°C
    c_w = 4.179  # [kJ kg^{-1}K^{-1}] specific heat capacity of freshwater @ 0°C
    s_0 = 35  # [PsU] standard seawater salinity

    s00 = 'freezing'
    s01 = 'solidification'
    s10 = 'fusion'
    s11 = 'melting'

    if s00.startswith(transformation) or s01.startswith(transformation):
        L_si = L - c_i * t + c_i * m_m * s - m_m * L * (s / t) + c_w * m_m * (s_0 - s)
    elif s10.startswith(transformation) or s11.startswith(transformation):
        L_si = L - c_i * t + c_i * m_m * s - m_m * L * (s / t)
    return L_si


def freezingpoint(sW, p=10.1325):
    """
	Parameters
	----------
		sW : array_like, number
			salinity of sea water in [PsU]
		p : array_like, number
			atmospheric pressure in [dbar]. atmospheric pressure at sea level by default p = 10.1325

	Returns
	----------
		sigma: ndarray
			conductivity of the brine in microsiemens/meter [ms/m]

		Valid for sW 4-40, and p up to 500
	"""
    p = icdt.make_array(p)
    sW = icdt.make_array(sW)

    ii_max = len(sW)

    t_fsw = []

    A = [-0.0575, +1.710523e-3, -2.154996e-4]
    B = [-7.53e-4]

    for ii in range(0, ii_max):
        t_fsw.append(A[0] * sW[ii] + A[1] * (sW[ii] * (3 / 2)) + A[2] * (sW[ii] ** 2) + B[0] * p)
    return t_fsw


def electricconductivity(t, s, rho_si=0.917, flag_comment='n'):
    """
		Calculate the electric conductivity of sea ice for a given temperature and salinity

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
		s : array_like, number
			salinity in practical salinity unit [PsU]
		rho_si : optional, array_like, number
			density of the ice in gram per cubic centimeter [g cm^{-3}]. Defaults 0.917.

		Returns
		----------
		sigma_si: ndarray
			conductivity of seaice in microsiemens/meter [s/m]
	"""
    t = icdt.make_array(t)
    s = icdt.make_array(s)
    rho_si = icdt.make_array(rho_si)

    # todo improve this method by getting the length of the ice core
    if len(t) > 1:
        if len(t) != len(s):
            if flag_comment == 'y':
                print('Vb t and s profile should be the same length')
            delta_t = len(t) - len(s)
            if delta_t < 0:
                temp = np.empty((-delta_t))
                temp[:] = np.nan
                t = np.append(t, temp)
            elif delta_t > 0:
                # reinterpolation of t for the length of s
                # xs = np.linspace(0,1,len(s))
                # xt = np.linspace(0,1,len(t))
                # t = np.interp(xs, xt, t)
                # todo: interpolation is a good idea, but does not work as I wish it works better to add a marker for short core in the data.
                lent = len(t)
                t = t[0:len(s)]
                t[len(s):lent] = np.nan
                s[len(s):lent] = np.nan

    sigma_b = brine_electricconductivity(t, flag_comment='n')
    vf_b = brine_volume_fraction(t, s, rho_si, flag_comment='n')

    sigma_si = sigma_b * (vf_b) ** 2

    return sigma_si


def resistivity(t, s, rho_si=0.917):
    """
		Calculate the electric resistivity of sea ice for a given temperature and salinity

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
		s : array_like, number
			salinity in practical salinity unit [PsU]
		rho_si : optional, array_like, number
			density of the ice in gram per cubic centimeter [g cm^{-3}]. Defaults 0.917.

		Returns
		----------
		rhoel_si: ndarray
			resistiviy of seaice in microsiemens/meter [s/m]
	"""
    t = icdt.make_array(t)
    s = icdt.make_array(s)
    # Need to check if array is the same length as t and s otherway return error message
    rho_si = icdt.make_array(rho_si)

    sigma_b = brine_electricconductivity(t)
    vf_b = brine_volume_fraction(t, s, rho_si)

    rhoel_si = (sigma_b * (vf_b) ** 2) ** (-1)

    return rhoel_si


def permeability(t, s, rho_si='default', flag_comment='n'):
    """
		Calculate the sea ice permeability in function of the temperature and salinity

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
			If t is an array, s should be an array of the same length
		s : array_like, number
			salinity in practical salinity unit [PsU]
			If s is an array, t should be an array of the same length
		rho_si : optional, array_like, number
			density of the ice in kilogram per cubic meter [kg m^{-3}]. Defautl is calculated for t,s value with a default air volume fraction set to 0.5‰.
			If rho_si is an array, t should be an array of the same length
		flag_comment : option, string
			toggle comment on/off

		Returns
		----------
		vf_b: ndarray
			Volume fraction of brine in the ice

		sources
		----------
		from equation 5  in K. Golden, H. Eicken, A.L. Heaton, J.Miner, D.J. Pringle, J. Zhu (2007) Thermal Evolution of Permeability, Geophysical Research Letters, 34, doi:10.1029/2007GL030447

	"""
    # check array lengths
    t = icdt.make_array(t)
    s = icdt.make_array(s)

    # todo improve this method by getting the length of the ice core
    if len(t) > 1:
        if len(t) != len(s):
            print('Vb t and s profile should be the same length')
            delta_t = len(t) - len(s)
            if delta_t < 0:
                temp = np.empty((-delta_t))
                temp[:] = np.nan
                t = np.append(t, temp)
            elif delta_t > 0:
                # reinterpolation of t for the length of s
                # xs = np.linspace(0,1,len(s))
                # xt = np.linspace(0,1,len(t))
                # t = np.interp(xs, xt, t)
                # t = np.interp(xs, xt, t)
                # todo: interpolation is a good idea, but does not work as I wish it works.
                lent = len(t)
                t = t[0:len(s)]
                t[len(s):lent] = np.nan
                s[len(s):lent] = np.nan
        else:
            t = t[0:len(s)]

    k = 3 * brine_volume_fraction(t, s, rho_si, flag_comment='n') ** 3 * 1e-8
    return k


# TODO: update array to SI
def salinity_from_conductivity(t, c):
    """
    Calculate the specifc conductance of sea water from temperature and conductivity measurement
    :param t: array_like, number
        temperature in degree Celsius [°C]
        If t is an array, c should be an array of same dimension
    :param c: array_like, number
        conductivity in microSievert by centimeters [uS/cm]
        If c is an array, t should be an array of same dimension
    :return sigma_sw: ndarray
        sea water salinity

    Reference
    http://www.chemiasoft.com/chemd/salinity_calculator
    Standard Methods for the Examination of Water and Wastewater, 20th edition, 1999.
    """

    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    if isinstance(c, (int, float)):
        c = np.array([c])
    else:
        c = np.array(c)

    # Physical constant
    A = np.empty((6, 2))
    A[0, :] = [0.0080, 0.0005]
    A[1, :] = [-0.1692, -0.0056]
    A[2, :] = [25.3851, -0.0066]
    A[3, :] = [14.0941, -0.0375]
    A[4, :] = [-7.0261, 0.0636]
    A[5, :] = [2.7081, -0.0144]

    B = [-0.0267243, 4.6636947, 861.3027640, 29035.1640851]

    cKCL = np.polyval(B, t)  # in uS/cm
    R = c / cKCL

    Rx = np.sqrt(R)

    dS = (t - 15) / (1 + 0.0162 * (t - 15)) * np.polyval(A[:, 1], Rx)
    S = np.polyval(A[:, 0], Rx) + dS

    return S


