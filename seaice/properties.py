#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.py: seaice.py is a library providing function to calculate physical properties of sea ice.
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
si_prop_list = {'brine volume fraction': 'brine volume fraction', 'brine volume fraction': 'brine volume fraction',
                'vbf': 'brine volume fraction', 'vb': 'brine volume fraction',
                'seaice permeability': 'seaice permeability', 'k': 'seaice permeability'}
si_prop_unit = {'salinity': '-',
                'temperature': '°C',
                'vb': '-', 'brine volume fraction': '-', 'brine volume fraction': '-',
                'seaice permeability': 'm$^{-2}$'}
si_prop_latex = {'salinity': 'S',
                 'temperature': 'T',
                 'brine volume fraction': '\phi_{B}',
                 'ice thickness': 'h_{i}',
                 'snow thickness': 'h_{s}',
                 'seaice permeability': '\kappa'
                 }

# updated for array, SI
def brine_volume_fraction(t, s, rho_si='default', flag_comment='n'):
    """
    Calculate the volume fraction of brine in function of the temperature and salinity

    Parameters
    ----------
    t : array_like, number
        temperature in degree Celsius [°C]
        If t is an array, s should be an array of the same length
    s : array_like, number
        salinity in practical salinity unit [PsU]
        If s is an array, t should be an array of the same length
    rho_si : optional, array_like, number
        density of the ice in gram per cubic centimeter [g cm^{-3}]. Default is calculated for t,s value with a default air volume fraction set to 0.5‰.
        If rho_si is an array, t should be an array of the same length
    flag_comment : option, string
        toggle comment on/off

    Returns
    ----------
    vf_b: ndarray
        Volume fraction of brine in the ice [-]

    sources
    ----------
    thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
    from equation 5 and 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).
    """
    # check parameters
    if isinstance(t, (int, float)):
        t = np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s = np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print('temperature and salinity array should be the same dimension')
        return 0

    if rho_si == 'default':
        rho_si = seaice_density(t, s, flag_comment='n')/10**3  # ice density in g cm^{-3}
    else:
        if isinstance(rho_si, (int, float)):
            rho_si = np.array([rho_si])/10**3  # ice density in g cm^{-3}
        else:
            if t.shape != rho_si.shape:
                print('sea ice density array should be the same dimension as temperature and salinity')
                return 0

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

    vf_a = air_volumefraction(t, s, rho_si, flag_comment='n')
    rho_i = ice_density(t, 'n')/10**3  # ice density in g cm^{-3}

    F1 = np.nan*t
    F2 = np.nan*t
    for mm in np.arange(0, 3):
        P1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
        P2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

        F1[(B[mm, 0]<=t) & (t<=B[mm, 1])] = np.polyval(P1, t[(B[mm, 0]<=t) & (t<=B[mm, 1])])
        F2[(B[mm, 0]<=t) & (t<=B[mm, 1])] = np.polyval(P2, t[(B[mm, 0]<=t) & (t<=B[mm, 1])])

    vf_b = ((1 - vf_a) * rho_i * s / (F1 - rho_i * s * F2))
    return vf_b

# updated for array, SI

def air_volumefraction(t, s, rho_si='Default', flag_comment='y'):
    """
    Calculate the volume fraction of air in function of the temperature and salinity

    Parameters
    ----------
    t : array_like, number
        temperature in degree Celsius [°C]
        If t is an array, s should be an array of the same length
    s : array_like, number
        salinity in practical salinity unit [PsU]
        If s is an array, t should be an array of the same length
    rho_si : optional, array_like, number
        density of the ice in gram per cubic centimeter [g cm^{-3}]. Defautl value is 0.9.
        If rho_si is an array, t should be an array of the same length
    flag_comment:


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
        t =np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s =np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print('temperature and salinity array should be the same shape')
        return 0

    if isinstance(rho_si, (int, float)):
        rho_si = np.array([rho_si]) / 10 ** 3  # ice density in g cm^{-3}
    elif isinstance(rho_si, str) and rho_si == 'Default':
        print('default rho si')
        rho_si = seaice_density(t, s, flag_comment='n')/10**3  # ice density in g cm^{-3}
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

    rho_i = ice_density(t, 'n')/10**3  # ice density in g cm^{-3}

    F1 = np.nan*t
    F2 = np.nan*t
    for mm in range(0, 3):
        p1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
        p2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

        F1[(B[mm, 0] <= t) & (t <= B[mm, 1])] = np.polyval(p1, t[(B[mm, 0] <= t) & (t <= B[mm, 1])])
        F2[(B[mm, 0] <= t) & (t <= B[mm, 1])] = np.polyval(p2, t[(B[mm, 0] <= t) & (t <= B[mm, 1])])


    vf_a = ((1 - rho_si / rho_i + rho_si * s * F2 / F1))

    return vf_a


# updated for array, SI
def ice_density(t, flag_comment='y'):
    """
		Calculate the density of the pure water ice in function of the temperature

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
		flag_comment : {'y','n'}, optional
			Whether to display the commet or not. Default is 'y'

		Returns
		----------
		rho_i: ndarray
			density of the ice in gram per cubic centimeters [kg m^{-3}]

		sources
		----------
		Equation 2.7 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		from Pounder. E. R. 1965. the physics of ice. Oxford. etc .. Pergamon Press. (the Commonwealth and International Library. Geophysics Division.) Ringer.

	"""
    import numpy as np

    # Physical constant
    A = [-0.000117, 1]
    B = 0.917  # density in kg m^{-3}

    if isinstance(t, (int, float)):
        t =np.array([t])
    else:
        t = np.array(t)
    rho_ice = np.nan*t

    rho_ice[np.where(t < 0)] = B * np.polyval(A, t[np.where(t < 0)])

    if flag_comment == 'y':
        if np.count_nonzero(np.where(t>0)):
            print('Element with temperature above 0°C : ice has melt in some case')
    return rho_ice*10**3


# updated for array, SI
def brine_density(t):
    """
		Calculate the density of the brine in function of the temperature.

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]

		Returns
		----------
		rho_b: ndarray
			density of the brine in gram per cubic centimeters [kg m^{-3}]

		sources
		----------
		Equation 2.9 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		from equation (3) in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice samples during shipping and storage. J. Glaciol, 32(112)

		from Zubov, N.N. (1945), L'dy Arktiki [Arctic ice]. Moscow, Izdatel'stvo Glavsevmorputi.

	"""
    # Physical constant
    A = [8 * 10 ** (-4), 1]
    if isinstance(t, (int, float)):
        t =np.array([t])
    else:
        t = np.array(t)

    s_b = brine_salinity(t)
    rho_b = (A[1] + A[0] * s_b)

    return rho_b*10**3

# updated for array, SI
def seaice_density(t, s, vf_a='default', flag_comment='y'):
    """
		Calculate the density of seaice in function of the temperature and salinity

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
			If t is an array, s must be an array of the same length
		s : array_like, number
			salinity in practical salinity unit [PsU]
			If s is an array, t must be an array of the same length
		vf_a : optional, array_like, number
			Air volume fraction, unitless [-].
			If air volume fraction is not defined, defaults value is set to 0.5‰. Usual value for first year sea ice, before spring warming.
			If Vf_a is an array, it tmust be the same length as t and s

		Returns
		----------
		rho_si: ndarray
			density of the brine in gram per cubic centimeters [kg m^{-3}]

		sources
		----------
		Equation 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).

		Coefficient form Cox & Weeks (1983)  and Leppäranta & Manninen (1988) [Leppäranta, M. & Manninen, t. (1988), the brine an gas content of sea ice with attention to low salinities and high temperatures. Finnish Institute of Marien Research Internal Report 88-2, Helsinki.
	"""
    import numpy as np
    import warnings

    # check parameters
    if isinstance(t, (int, float)):
        t =np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s =np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print('temperature and salinity profile should be same size array')
        return 0

    if vf_a == 'default':
        vf_a = np.array([0.0005])
        warnings.warn('Air volume fraction is set to default value: Vf_a=0.5 ‰', UserWarning)
    else:
        vf_a = np.array(vf_a)
        if t.shape != vf_a.shape:
            print('air volume fraction array should be the same size as temperature and salinity')
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


    rho_i = ice_density(t, 'n')/10**3  # ice density in g cm^{-3}

    F1 = np.nan*t
    F2 = np.nan*t
    for mm in range(0, 3):
        P1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
        P2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

        F1[(B[mm,0]<=t) & (t<=B[mm,1])] = np.polyval(P1, t[(B[mm,0]<=t) & (t<=B[mm,1])])
        F2[(B[mm,0]<=t) & (t<=B[mm,1])] = np.polyval(P2, t[(B[mm,0]<=t) & (t<=B[mm,1])])


    rho_seaice = ((1 - vf_a) * (rho_i * F1 / (F1 - rho_i * s * F2)));

    return rho_seaice*10**3


# updated for array
def brine_salinity(t, method='CW', flag_comment='y'):
    """
    Calculate the salinity of the brine in function of the temperature at equilibrium.

    Parameters
    ----------
    t : array_like, number
        temperature in degree Celsius [°C]
    method : {'As','CW'}, optional
        Whether to calculate the salinity with Assur model ('As') or with the equation of Cox & Weeks (1983) ('CW'). Default is 'CW'
    flag_comment:

    Returns
    ----------
    s_b: ndarray
        salinity of the brine in Practical salinity Unit [PsU]

    sources
    ----------
    'As' : Equation 2.8 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
    'CW' : Equation 25 in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice samples during shipping and storage. J. Glaciol, 32(112), 371–375
"""
    import numpy as np

    if isinstance(t, (int, float)):
        t =np.array([t])
    else:
        t = np.array(t)

    s_b = np.nan*t

    if method == 'As':
        if t.all > -23:
            s_b = ((1 - 54.11 / t) ** (-1)) * 1000
        else:
            print('At least one temperature is inferior to -23[°C]. Cox & Weeks equation is used instead')
            brine_salinity(t, 'CW')
    else:
        # Physical constant
        A = np.empty((3, 4))
        B = np.empty((3, 2))

        # coefficient for -54<t<=-44
        A[0, :] = [-4442.1, -277.86, -5.501, -0.03669];
        B[0] = [-54, -44]
        # coefficient for -44<t<=-22.9
        A[1, :] = [206.24, -1.8907, -0.060868, -0.0010247];
        B[1] = [-44, -22.9]
        # coefficient for -22.9<t<=-2
        A[2, :] = [-3.9921, -22.700, -1.0015, -0.019956];
        B[2] = [-22.9, -2]

        for mm in range(0, 3):
            P1 = [A[mm, 3], A[mm, 2], A[mm, 1], A[mm, 0]]

            s_b[(B[mm,0]<=t) & (t<=B[mm,1])] = (np.polyval(P1, t[(B[mm, 0]<=t) & (t<=B[mm, 1])]))
    return s_b

# updated for array, SI
def brine_thermal_conductivity(t, flag_comment='y'):
    """
		Calculate thermal conductivity of brine

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
			If t is an array, s should be an array of the same length

		Returns
		----------
		lambda_si ndarray
			brine thermal conductivity in W m^{-1]K^{-1]

		sources
		----------
		Equation 2.12 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		From Yen, Y. C., Cheng, K. C., and Fukusako, s. (1991) Review of intrinsic thermophysical properties of snow, ice, sea ice, and frost. In: Proceedings 3rd International symposium on Cold Regions Heat transfer, Fairbanks, AK, June 11-14, 1991. (Ed. by J. P. Zarling & s. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
	"""
    import numpy as np

    if isinstance(t, (int, float)):
        t =np.array([t])
    else:
        t = np.array(t)

    # Physical constant
    A = [0.00014, 0.030, 1.25]
    B = 0.4184

    lambda_b = np.nan*t

    lambda_b[(t < 0)] = B * np.polyval(A, t[(t < 0)])

    if flag_comment == 'y':
        if np.count_nonzero(np.where(t>0)):
            print('Element with temperature above 0°C : ice has melt in some case')

    return lambda_b

# updated for array, SI
def ice_thermal_conductivity(t, flag_comment='y'):
    """
		Calculate thermal conductivity of ice

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]
			If t is an array, s should be an array of the same length

		Returns
		----------
		lambda_si ndarray
			ice thermal conductivity W m^{-1] K^{-1]

		sources
		----------
		Equation 2.11 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		From Yen, Y. C., Cheng, K. C., and Fukusako, s. (1991) Review of intrinsic thermophysical properties of snow, ice, sea ice, and frost. In: Proceedings 3rd International symposium on Cold Regions Heat transfer, Fairbanks, AK, June 11-14, 1991. (Ed. by J. P. Zarling & s. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
	"""
    import numpy as np

    if isinstance(t, (int, float)):
        t =np.array([t])
    else:
        t = np.array(t)

    # Physical constant
    A = [2.97 * 10 ** (-5), -8.66 * 10 ** (-3), 1.91]
    B = 1.16

    lambda_i = np.nan*t

    lambda_i[np.where(t < 0)] = B * np.polyval(A, t[np.where(t < 0)])

    if flag_comment == 'y':
        if np.count_nonzero(np.where(t>0)):
            print('Element with temperature above 0°C : ice has melt in some case')
    return lambda_i

# updated for array, SI
def seaice_thermal_conductivity(t, s, method='pringle', flag_comment='y'):
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
        t =np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s =np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print('t and s profile should be the same size')

    lambda_si = np.nan*t

    if method == 'maykut':
        # Physical constant
        A = 0.13

        lambda_si[np.where(t < 0)] = (
            ice_thermal_conductivity(t[np.where(t < 0)]) + A * s[np.where(t < 0)] / t[np.where(t < 0)])

    elif method == 'pringle':
        rho_si = seaice_density(t, s, flag_comment='n')/10**3  # density in g cm^{-3}
        rho_i = ice_density(t, flag_comment='n')/10**3  # density in g cm^{-3}

        lambda_si[(t < 0)] = rho_si[(t < 0)] / rho_i[(t < 0)] * (
            2.11 - 0.011 * t[(t < 0)] + 0.09 * s[(t < 0)] / t[(t < 0)] - (
                rho_si[(t < 0)] - rho_i[(t < 0)]) / 1000)

    if flag_comment == 'y':
        if flag_comment == 'y':
            if np.count_nonzero(np.where(t > 0)):
                print('Some conductivity value are not define. Temperature above 0°C')
    return lambda_si

# updated for array, SI
def seaice_specific_heat_capacity(t, s, method = 'Untersteiner', flag_comment='y'):
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
        t =np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s =np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print("Salinity and temperature array should be the same size")

    # Pysical Constant
    c_i = 2.11  # [kJ kg^{-1}K^{-1}] specific heat capacity of ice @ 0°C

    c_si = np.nan*np.array(t)

    if method == 'Untersteiner':
        A = 17.2  # [kJ kg^{-1}K^{-1}]
        c_si[t<0] = c_i + A*s[t<0]/t[t<0]**2

    elif method == 'Ono':
        beta = 7.5*10**-3  # (kJ kg^{-1}K^{-2})
        L = 333.4 # (J kg^{-1}) latent heat of fusion of freshwater
        m_m = -0.05411  # (K)  slope of the liquid

        c_si[t<0] = c_i + beta*t[t<0]-m_m*L*s[t<0]/t[t<0]**2

    return c_si*10**3


def seaice_thermal_diffusivity(t, s, method='default', flag_comment='y'):
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
        t =np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s =np.array([s])
    else:
        s = np.array(s)

    if t.shape != s.shape:
        print("Salinity and temperature array should be the same size")

    sigma_si = seaice_thermal_conductivity(t, s)/(seaice_specific_heat_capacity(t, s)*seaice_density(t, s))

    return sigma_si


def seaice_latentheat(t, s, transformation='fusion'):
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
        t =np.array([t])
    else:
        t = np.array(t)
    if isinstance(s, (int, float)):
        s =np.array([s])
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


def seawater_freezingpoint(sW, p=10.1325):
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


def brine_electricconductivity(t, flag_comment='n'):
    """
		Calculate the electric conductivity of brine for a given temperature

		Parameters
		----------
		t : array_like, number
			temperature in degree Celsius [°C]

		Returns
		----------
		sigma: ndarray
			conductivity of the brine in microsiemens/meter [ms/m]

		Equation
		_________
			Fofonoff, Nick P., and Robert C. Millard. "Algorithms for computation of fundamental properties of seawater." (1983).
	"""
    import numpy as np

    t = icdt.make_array(t)
    ii_max = len(t)

    # Physical constant
    A = [0.08755, 0.5193]

    sigma_b = []
    for ii in range(0, ii_max):
        sigma_b.append(-t[ii] * np.exp(np.polyval(A, t[ii])))
    return np.array(sigma_b)


def seaice_electricconductivity(t, s, rho_si=0.917, flag_comment='n'):
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


def seaice_resistivity(t, s, rho_si=0.917):
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


def seaice_permeability(t, s, rho_si='default', flag_comment='n'):
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

    k = 3*brine_volume_fraction(t, s, rho_si, flag_comment='n')**3*1e-8
    return k

#TODO: update array to SI
def seawater_salinity_from_conductivity(t, c):
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
        t =np.array([t])
    else:
        t = np.array(t)
    if isinstance(c, (int, float)):
        c =np.array([c])
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
    R = c/cKCL

    Rx = np.sqrt(R)

    dS = (t-15)/(1+0.0162*(t-15))*np.polyval(A[:, 1], Rx)
    S = np.polyval(A[:, 0], Rx) + dS

    return S


# def seawater_salinity_from_conductance(sigma):
#     """
#     Calculate the specifc conductance of sea water from temperature and conductivity measurement
#     :param sigma: array_like, number
#         specific conductance in degree Celsius []
#     :return S_sw: ndarray
#         sea water salinity
#     """
#
#     if isinstance(sigma, (int, float)):
#         sigma = np.array([sigma])
#     else:
#         sigma = np.array(sigma)
#
#
#     return S

