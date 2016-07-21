#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
seaice.py: seaice.py is a library providing function to calculate physical properties of sea ice.
"""

import numpy as np
from seaice import icdtools as icdt

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2014/11/25"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]

si_state_variable = {'temperature': 'temperature', 'temp': 'temperature', 't': 'temperature',
                     'salinity': 'salinity', 's': 'salinity'}
si_prop_list = {'brine volume fraction': 'brine volume fraction', 'brine volume fraction': 'brine volume fraction',
                'vbf': 'brine volume fraction', 'vb': 'brine volume fraction'}
si_prop_unit = {'salinity': '[PSU]', 'temperature': '[°C]', 'vb': '[-]', 'brine volume fraction': '[-]', 'brine volume fraction': '[-]'}


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
        density of the ice in gram per cubic centimeter [g cm^{-3}]. Defautl is calculated for t,s value with a default air volume fraction set to 0.5‰.
        If rho_si is an array, t should be an array of the same length
    flag_comment : option, string
        toggle comment on/off

    Returns
    ----------
    vf_b: ndarray
        Volume fraction of brine in the ice

    sources
    ----------
    thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
    from equation 5 and 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).
    """
    # check array lengths
    t = icdt.make_array(t)
    s = icdt.make_array(s)

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
                # todo: interpolation is a good idea, but does not work as I wish it works.
                lent = len(t)
                t = t[0:len(s)]
                t[len(s):lent] = np.nan
                s[len(s):lent] = np.nan
        else:
            t = t[0:len(s)]

    if rho_si == 'default':
        rho_si = seaice_density(t, s, flag_comment='n')
    else:
        rho_si = icdt.make_array(rho_si)
        if len(rho_si) != len(s) or len(rho_si) != 1:
            if flag_comment == 'y':
                print('rho_si should be the same length as t and s')
            rho_si = np.ones(len(s))[:] * rho_si

    a = np.empty((4, 4, 2))

    # coefficient for -2<t<=0
    a[0, 0, :] = [-0.041221, 0.090312]
    a[0, 1, :] = [-18.407, -0.016111]
    a[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
    a[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

    # coefficient for -22.9<t<=-2
    a[1, 0, :] = [-4.732, 0.08903]
    a[1, 1, :] = [-22.45, -0.01763]
    a[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
    a[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

    # coefficient for t<=-22.9
    a[2, 0, :] = [9899, 8.547]
    a[2, 1, :] = [1309, 1.089]
    a[2, 2, :] = [55.27, 0.04518]
    a[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

    ii_max = len(t)
    vf_b = np.empty(ii_max)
    vf_b[:] = np.nan

    vf_a = air_volumefraction(t, s, rho_si, flag_comment='n')

    for ii in np.arange(0, ii_max):
        t_temp = t[ii]
        s_temp = s[ii]
        vf_a_temp = vf_a[ii]
        if np.isnan(t_temp):
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : temperature not defined')
        elif np.isnan(s_temp):
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : salinity not defined')
        elif t_temp < -30:
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : t=' + str(t_temp) + '<-30 : ice temperature is out of validity')
        elif 0 <= t_temp:
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : t=' + str(t_temp) + '>0 : ice has alreay melt')
        else:
            if (-30 <= t_temp) & (t_temp <= -22.9):
                mm = 2
            elif (-22.9 < t_temp) & (t_temp <= -2):
                mm = 1
            elif (-2 < t_temp) & (t_temp <= 0):
                mm = 0

            p1 = [a[mm, 3, 0], a[mm, 2, 0], a[mm, 1, 0], a[mm, 0, 0]]
            p2 = [a[mm, 3, 1], a[mm, 2, 1], a[mm, 1, 1], a[mm, 0, 1]]

            f1 = np.polyval(p1, t_temp)
            f2 = np.polyval(p2, t_temp)

            rho_i = ice_density(t_temp, 'n')  # [0]

            vf_b[ii] = ((1 - vf_a_temp) * rho_i * s_temp / (f1 - rho_i * s_temp * f2))
    return vf_b


def air_volumefraction(t, s, rho_si=0.9, flag_comment='y'):
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
    t = icdt.make_array(t)
    s = icdt.make_array(s)

    if len(t) > 1:
        if len(t) != len(s):
            print('rho sI t and s profile should be the same length')
            delta_t = len(t) - len(s)
            if delta_t < 0:
                delta_t = len(t) - len(s)
                temp = np.empty((-delta_t))
                temp[:] = np.nan
                t = np.append(t, temp)
            elif delta_t > 0:
                # todo: interpolation is a good idea, but does not work as I wish it works.
                lent = len(t)
                t = t[0:len(s)]
                t[len(s):lent] = np.nan
                s[len(s):lent] = np.nan

    rho_si = icdt.make_array(rho_si)
    if len(rho_si) != len(s) & len(rho_si) != 1:
        print('rho_si should be the same length as t and s')
        return 0

    ii_max = len(t)
    vf_a = np.empty(ii_max)
    vf_a[:] = np.nan

    # Physical constant
    A = np.empty((4, 4, 2))

    # coefficient for -2<t<=0
    A[0, 0, :] = [-0.041221, 0.090312]
    A[0, 1, :] = [-18.407, -0.016111]
    A[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
    A[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

    # coefficient for -22.9<t<=-2
    A[1, 0, :] = [-4.732, 0.08903]
    A[1, 1, :] = [-22.45, -0.01763]
    A[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
    A[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

    # coefficient for t<=-22.9
    A[2, 0, :] = [9899, 8.547]
    A[2, 1, :] = [1309, 1.089]
    A[2, 2, :] = [55.27, 0.04518]
    A[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

    rho_i = ice_density(t, 'n')

    for ii in np.arange(0, ii_max):
        t_temp = t[ii];
        s_temp = s[ii];

        if len(rho_si) > 1:
            rho_si_temp = rho_si[ii]
        else:
            rho_si_temp = rho_si[0]

        if np.isnan(t_temp):
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : temperature not defined')
        elif np.isnan(s_temp):
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : salintiy not defined')
        elif t_temp < -30:
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : t=' + str(t_temp) + '<-30 : ice temperature is out of validity')
        elif 0 <= t_temp:
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : t=' + str(t_temp) + '>0 : ice has alreay melt')
        else:
            if (-30 <= t_temp) & (t_temp <= -22.9):
                mm = 2
            elif (-22.9 < t_temp) & (t_temp <= -2):
                mm = 1
            elif (-2 < t_temp) & (t_temp <= 0):
                mm = 0
            P1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
            P2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

            F1 = np.polyval(P1, t_temp)
            F2 = np.polyval(P2, t_temp)

            vf_a[ii] = ((1 - rho_si_temp / rho_i[ii] + rho_si_temp * s_temp * F2 / F1))
    return vf_a


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
			density of the ice in gram per cubic centimeters [g cm^{-3}]

		sources
		----------
		Equation 2.7 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		from Pounder. E. R. 1965. the physics of ice. Oxford. etc .. Pergamon Press. (the Commonwealth and International Library. Geophysics Division.) Ringer.

	"""
    import numpy as np

    # Physical constant
    A = [-0.000117, 1]
    B = 0.917

    t = np.atleast_1d(t)
    t = icdt.make_array(t)
    ii_max = len(t)
    rho_ice = np.empty((ii_max))
    rho_ice[:] = np.nan

    rho_ice[np.where(t < 0)] = B * np.polyval(A, t[np.where(t < 0)])

    if flag_comment == 'y':
        if t > 0:
            print('temperature above 0°C : ice has melt')
        for ii in np.where(t >= 0)[0]:
            print('layer ' + str(ii + 1) + ' : t=' + str(t[ii]) + '°C')

    return rho_ice


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
			density of the brine in gram per cubic centimeters [g cm^{-3}]

		sources
		----------
		Equation 2.9 in thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		from equation (3) in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice samples during shipping and storage. J. Glaciol, 32(112)

		from Zubov, N.N. (1945), L'dy Arktiki [Arctic ice]. Moscow, Izdatel'stvo Glavsevmorputi.

	"""
    # Physical constant
    A = [8 * 10 ** (-4), 1]
    t = icdt.make_array(t)

    s_b = brine_salinity(t)
    rho_b = (A[1] + A[0] * s_b)

    return rho_b


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
			density of the brine in gram per cubic centimeters [g cm^{-3}]

		sources
		----------
		Equation 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).

		Coefficient form Cox & Weeks (1983)  and Leppäranta & Manninen (1988) [Leppäranta, M. & Manninen, t. (1988), the brine an gas content of sea ice with attention to low salinities and high temperatures. Finnish Institute of Marien Research Internal Report 88-2, Helsinki.
	"""
    import numpy as np
    import warnings

    # check parameters
    t = icdt.make_array(t)
    s = icdt.make_array(s)

    if len(t) > 1:
        if len(t) != len(s):
            print('rho sI t and s profile should be the same length')
            delta_t = len(t) - len(s)
            if delta_t < 0:
                delta_t = len(t) - len(s)
                temp = np.empty((-delta_t))
                temp[:] = np.nan
                t = np.append(t, temp)
            elif delta_t > 0:
                lent = len(t)
                t = t[0:len(s)]
                t[len(s):lent] = np.nan
                s[len(s):lent] = np.nan

    if vf_a == 'default':
        vf_a = np.array([0.0005])
        warnings.warn('Air volume fraction is set to default value: Vf_a=0.5 ‰', UserWarning)
    else:
        vf_a = icdt.make_array(vf_a)
        if len(vf_a) != len(s) & len(vf_a) != 1:
            print('Vf_a should be the same length as t and s')
            return 0

    ii_max = len(t)
    rho_seaice = np.empty(ii_max)
    rho_seaice[:] = np.nan

    # Physical constant
    A = np.empty((4, 4, 2))

    # coefficient for t<=-22.9
    A[0, 0, :] = [-0.041221, 0.090312]
    A[0, 1, :] = [-18.407, -0.016111]
    A[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
    A[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

    # coefficient for -22.9<t<=-2
    A[1, 0, :] = [-4.732, 0.08903]
    A[1, 1, :] = [-22.45, -0.01763]
    A[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
    A[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

    # coefficient for -2<t<=0
    A[2, 0, :] = [9899, 8.547]
    A[2, 1, :] = [1309, 1.089]
    A[2, 2, :] = [55.27, 0.04518]
    A[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

    rho_i = ice_density(t, 'n')
    rho_seaice = np.empty(ii_max)
    rho_seaice[:] = np.nan

    for ii in range(0, ii_max):
        t_temp = t[ii];
        s_temp = s[ii];
        if np.isnan(t_temp):
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : temperature not defined')
            rho_seaice[ii] = (np.nan)
        elif np.isnan(s_temp):
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : salinity not defined')
            rho_seaice[ii] = (np.nan)
        elif t_temp < -30:
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : t=' + str(t_temp) + '<-30 : ice temperature is out of validity')
        elif 0 <= t_temp:
            if flag_comment == 'y':
                print('layer ' + str(ii) + ' : t=' + str(t_temp) + '>0 : ice has alreay melt')
        else:
            if (-30 <= t_temp) & (t_temp <= -22.9):
                mm = 0
            elif (-22.9 < t_temp) & (t_temp <= -2):
                mm = 1
            elif (-2 < t_temp) & (t_temp <= 0):
                mm = 2

            P1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
            P2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

            F1 = np.polyval(P1, t_temp)
            F2 = np.polyval(P2, t_temp)

            rho_seaice[ii] = ((1 - vf_a) * (rho_i[ii] * F1 / (F1 - rho_i[ii] * s_temp * F2)));
    return rho_seaice


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

    t = icdt.make_array(t)

    ii_max = len(t)
    s_b = np.empty(ii_max)
    s_b[:] = np.nan

    if method == 'As':
        if t.all > -23:
            s_b = ((1 - 54.11 / t) ** (-1)) * 1000
        else:
            print('At least one temperature is inferior to -23[°C]. Cox & Weeks equation is used instead')
            brine_salinity(t, 'CW')
    else:
        # Physical constant
        A = np.empty((3, 4))
        # coefficient for -54<t<=-44
        A[0, :] = [-4442.1, -277.86, -5.501, -0.03669];

        # coefficient for -44<t<=-22.9
        A[1, :] = [206.24, -1.8907, -0.060868, -0.0010247];

        # coefficient for -22.9<t<=-2
        A[2, :] = [-3.9921, -22.700, -1.0015, -0.019956];

        for ii in range(0, ii_max):
            if np.isnan(t[ii]):
                if flag_comment == 'y':
                    print('layer ' + str(ii) + ' : temperature not defined')
            elif t[ii] < -54:
                if flag_comment == 'y':
                    print('layer ' + str(ii) + ' : t=' + str(t[ii]) + '<-54 : ice temperature is out of validity')
            elif 0 <= t[ii]:
                if flag_comment == 'y':
                    print('layer ' + str(ii) + ' : t=' + str(t[ii]) + '>0 : ice has alreay melt')
            else:
                if (-54 < t[ii]) & (t[ii] <= -44):
                    mm = 0
                elif (-44 < t[ii]) & (t[ii] <= -22.9):
                    mm = 1
                elif (-22.9 < t[ii]) & (t[ii] <= 0):
                    mm = 2

                P1 = [A[mm, 3], A[mm, 2], A[mm, 1], A[mm, 0]]

                s_b[ii] = (np.polyval(P1, t[ii]))
    return s_b


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
			Volume fraction of brine in the ice

		sources
		----------
		Equation 2.12 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		From Yen, Y. C., Cheng, K. C., and Fukusako, s. (1991) Review of intrinsic thermophysical properties of snow, ice, sea ice, and frost. In: Proceedings 3rd International symposium on Cold Regions Heat transfer, Fairbanks, AK, June 11-14, 1991. (Ed. by J. P. Zarling & s. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
	"""
    import numpy as np

    # Physical constant
    A = [0.00014, 0.030, 1.25]
    B = 0.4184
    t = icdt.make_array(t)

    ii_max = len(t)
    lambda_b = np.empty((ii_max))
    lambda_b[:] = np.nan

    lambda_b[np.where(t < 0)] = B * np.polyval(A, t[np.where(t < 0)])

    if flag_comment == 'y':
        for ii in np.where(t >= 0)[0]:
            print('layer ' + str(ii + 1) + ' : t=' + str(t[ii]) + '°C, ice has melt')
    for ii in np.where(lambda_b < 0)[0]:
        lambda_b[ii] = np.nan
        if flag_comment == 'y':
            print('layer ' + str(ii + 1) + ' : conductivity not defined')
    return lambda_b


def ice_thermalConductivity(t, flag_comment='y'):
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
			Volume fraction of brine in the ice

		sources
		----------
		Equation 2.11 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		From Yen, Y. C., Cheng, K. C., and Fukusako, s. (1991) Review of intrinsic thermophysical properties of snow, ice, sea ice, and frost. In: Proceedings 3rd International symposium on Cold Regions Heat transfer, Fairbanks, AK, June 11-14, 1991. (Ed. by J. P. Zarling & s. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
	"""
    import numpy as np

    # Physical constant
    A = [2.97 * 10 ** (-5), -8.66 * 10 ** (-3), 1.91]
    B = 1.16

    t = icdt.make_array(t)

    ii_max = len(t)
    lambda_i = np.empty((ii_max))
    lambda_i[:] = np.nan

    lambda_i[np.where(t < 0)] = B * np.polyval(A, t[np.where(t < 0)])

    if flag_comment == 'y':
        for ii in np.where(t >= 0)[0]:
            print('layer ' + str(ii + 1) + ' : t=' + str(t[ii]) + '°C, ice has melt')
    return lambda_i


def seaice_thermalConductivity(t, s, method='Maykut', flag_comment='y'):
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
			Volume fraction of brine in the ice

		sources
		----------
		Equation 2.14 and 2.16 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell

		Pringle method is describe in Pringle, D. J., Eicken, H., trodahl, H. J., & Backstrom, L. G. E. (2007). thermal conductivity of landfast Antarctic and Arctic sea ice. Journal of Geophysical Research, 112(C4), C04017. doi:10.1029/2006JC003641

		Maykut method is describe in Maykut, G. A. (1986). the surface heat and mass balance. In N. Understeiner (Ed.), the geophysics of sea ice (pp. 395–463). Dordrecht (NAtO AsI B146): Martinus Nijhoff Publishers.
	"""
    import numpy as np

    t = icdt.make_array(t)
    s = icdt.make_array(s)

    if len(t) > 1:
        if len(t) != len(s):
            print('t and s profile should be the same length')
            return 0

    ii_max = len(t)
    lambda_si = np.empty((ii_max))
    lambda_si[:] = np.nan

    if method == 'Maykut':
        # Physical constant
        A = 0.13

        lambda_si[np.where(t < 0)] = (
            ice_thermalConductivity(t[np.where(t < 0)]) + A * s[np.where(t < 0)] / t[np.where(t < 0)])

    elif method == 'Pringle':
        rho_si = seaice_density(t, s, flag_comment='n')
        rho_i = ice_density(t, flag_comment='n')

        lambda_si[np.where(t < 0)] = rho_si[np.where(t < 0)] / rho_i[np.where(t < 0)] * (
            2.11 - 0.011 * t[np.where(t < 0)] + 0.09 * s[np.where(t < 0)] / t[np.where(t < 0)] - (
                rho_si[np.where(t < 0)] - rho_i[np.where(t < 0)]) / 1000)

    if flag_comment == 'y':
        for ii in np.where(t >= 0)[0]:
            print('layer ' + str(ii + 1) + ' : t=' + str(t[ii]) + '°C, ice has melt')
    for ii in np.where(lambda_si < 0)[0]:
        lambda_si[ii] = np.nan
        if flag_comment == 'y':
            print('layer ' + str(ii + 1) + ' : conductivity not defined')

    return lambda_si


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
    t = icdt.make_array(t)
    s = icdt.make_array(s)

    if len(t) > 1:
        if len(t) != len(s):
            print('t and s profile should be the same length')
            return 0

    # Pysical Constant
    L = 333.4  # [kJ kg^{-1}] latent heat of fusion of freshwater
    m_m = -0.05411  # [K]  slope of the liquid
    c_i = 2.11  # [kJ kg^{-1}K^{-1}] specific heat cpacity of ice @ 0°C
    c_w = 4.179  # [kJ kg^{-1}K^{-1}] specific heat cpacity of freshwater @ 0°C
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
			density of the ice in gram per cubic centimeter [g cm^{-3}]. Defautl is calculated for t,s value with a default air volume fraction set to 0.5‰.
			If rho_si is an array, t should be an array of the same length
		flag_comment : option, string
			toggle comment on/off

		Returns
		----------
		vf_b: ndarray
			Volume fraction of brine in the ice

		sources
		----------
		thomas, D. & G. s. Dieckmann, eds. (2010) sea ice. London: Wiley-Blackwell
		from equation 5 and 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).

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

    if rho_si == 'default':
        rho_si = seaice_density(t, s, flag_comment='n')
    else:
        rho_si = icdt.make_array(rho_si)
        if len(rho_si) != len(s) or len(rho_si) != 1:
            print('rho_si should be the same length as t and s')
            rho_si = np.ones(len(s))[:] * rho_si

    Vf_b = brine_volume_fraction(t, s, rho_si=rho_si, flag_comment='n')
    k = 3 * Vf_b ** 2 * 10 ** (-10)
    return k
