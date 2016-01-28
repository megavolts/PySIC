#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2014/11/25"
__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]

seaice.py: seaice.py is a library providing function to calculate physical properties of sea ice.
"""

import numpy as np
from seaice import icdtools as icdt


def brine_volumefraction(T, S, rho_si='default', flag_comment='n'):
	"""
		Calculate the volume fraction of brine in function of the temperature and salinity

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
			If T is an array, S should be an array of the same length
		S : array_like, number
			Salinity in practical salinity unit [PSU]
			If S is an array, T should be an array of the same length
		rho_si : optional, array_like, number
			density of the ice in gram per cubic centimeter [g cm^{-3}]. Defautl is calculated for T,S value with a default air volume fraction set to 0.5‰.
			If rho_si is an array, T should be an array of the same length
		flag_comment : option, string
			toggle comment on/off

		Returns
		----------
		vf_b: ndarray
			Volume fraction of brine in the ice

		Sources
		----------
		Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell
		from equation 5 and 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).
	"""
	# check array lengths
	T = icdt.make_array(T)
	S = icdt.make_array(S)

	# todo improve this method by getting the length of the ice core
	if len(T) > 1:
		if len(T) != len(S):
			if flag_comment == 'y':
				print('Vb T and S profile should be the same length')
			deltaT = len(T) - len(S)
			if deltaT < 0:
				temp = np.empty((-deltaT))
				temp[:] = np.nan
				T = np.append(T, temp)
			elif deltaT > 0:
				# reinterpolation of T for the length of S
				# xS = np.linspace(0,1,len(S))
				# xT = np.linspace(0,1,len(T))
				# T = np.interp(xS, xT, T)
				# T = np.interp(xS, xT, T)
				# todo: interpolation is a good idea, but does not work as I wish it works.
				lenT = len(T)
				T = T[0:len(S)]
				T[len(S):lenT] = np.nan
				S[len(S):lenT] = np.nan
		else:
			T = T[0:len(S)]

	if rho_si == 'default':
		rho_si = seaice_density(T, S, flag_comment='n')
	else:
		rho_si = icdt.make_array(rho_si)
		if len(rho_si) != len(S) or len(rho_si) != 1:
			if flag_comment == 'y':
				print('rho_si should be the same length as T and S')
			rho_si = np.ones(len(S))[:] * rho_si

	A = np.empty((4, 4, 2))

	# coefficient for -2<T<=0
	A[0, 0, :] = [-0.041221, 0.090312]
	A[0, 1, :] = [-18.407, -0.016111]
	A[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
	A[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

	# coefficient for -22.9<T<=-2
	A[1, 0, :] = [-4.732, 0.08903]
	A[1, 1, :] = [-22.45, -0.01763]
	A[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
	A[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

	# coefficient for T<=-22.9
	A[2, 0, :] = [9899, 8.547]
	A[2, 1, :] = [1309, 1.089]
	A[2, 2, :] = [55.27, 0.04518]
	A[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

	iimax = len(T)
	vf_b = np.empty(iimax)
	vf_b[:] = np.nan

	vf_a = air_volumefraction(T, S, rho_si, flag_comment='n')

	for ii in np.arange(0, iimax):
		Ttemp = T[ii]
		Stemp = S[ii]
		vf_a_temp = vf_a[ii]
		if np.isnan(Ttemp):
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : Temperature not defined')
		elif np.isnan(Stemp):
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : Salinity not defined')
		elif Ttemp < -30:
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : T=' + str(Ttemp) + '<-30 : ice temperature is out of validity')
		elif 0 <= Ttemp:
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : T=' + str(Ttemp) + '>0 : ice has alreay melt')
		else:
			if (-30 <= Ttemp) & (Ttemp <= -22.9):
				mm = 2
			elif (-22.9 < Ttemp) & (Ttemp <= -2):
				mm = 1
			elif (-2 < Ttemp) & (Ttemp <= 0):
				mm = 0

			P1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
			P2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

			F1 = np.polyval(P1, Ttemp)
			F2 = np.polyval(P2, Ttemp)

			rho_i = ice_density(Ttemp, 'n') #[0]

			vf_b[ii] = ((1 - vf_a_temp) * rho_i * Stemp / (F1 - rho_i * Stemp * F2))
	return vf_b


def air_volumefraction(T, S, rho_si=0.9, flag_comment='y'):
	"""
		Calculate the volume fraction of air in function of the temperature and salinity

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
			If T is an array, S should be an array of the same length
		S : array_like, number
			Salinity in practical salinity unit [PSU]
			If S is an array, T should be an array of the same length
		rho_si : optional, array_like, number
			density of the ice in gram per cubic centimeter [g cm^{-3}]. Defautl value is 0.9.
			If rho_si is an array, T should be an array of the same length

		Returns
		----------
		vf_a: ndarray
			Volume fraction of air in the ice

		Sources
		----------
		Equation 14 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).

	"""
	import numpy as np

	# check array lengths
	T = icdt.make_array(T)
	S = icdt.make_array(S)

	if len(T) > 1:
		if len(T) != len(S):
			print('rho SI T and S profile should be the same length')
			deltaT = len(T) - len(S)
			if deltaT < 0:
				deltaT = len(T) - len(S)
				temp = np.empty((-deltaT))
				temp[:] = np.nan
				T = np.append(T, temp)
			elif deltaT > 0:
				# todo: interpolation is a good idea, but does not work as I wish it works.
				lenT = len(T)
				T = T[0:len(S)]
				T[len(S):lenT] = np.nan
				S[len(S):lenT] = np.nan

	rho_si = icdt.make_array(rho_si)
	if len(rho_si) != len(S) & len(rho_si) != 1:
		print('rho_si should be the same length as T and S')
		return 0

	iimax = len(T)
	vf_a = np.empty(iimax)
	vf_a[:] = np.nan


	# Physical constant
	A = np.empty((4, 4, 2))

	# coefficient for -2<T<=0
	A[0, 0, :] = [-0.041221, 0.090312]
	A[0, 1, :] = [-18.407, -0.016111]
	A[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
	A[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

	# coefficient for -22.9<T<=-2
	A[1, 0, :] = [-4.732, 0.08903]
	A[1, 1, :] = [-22.45, -0.01763]
	A[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
	A[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

	# coefficient for T<=-22.9
	A[2, 0, :] = [9899, 8.547]
	A[2, 1, :] = [1309, 1.089]
	A[2, 2, :] = [55.27, 0.04518]
	A[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

	rho_i = ice_density(T, 'n')

	for ii in np.arange(0, iimax):
		Ttemp = T[ii];
		Stemp = S[ii];

		if len(rho_si) > 1:
			rho_si_temp = rho_si[ii]
		else:
			rho_si_temp = rho_si[0]

		if np.isnan(Ttemp):
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : Temperature not defined')
		elif np.isnan(Stemp):
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : Salintiy not defined')
		elif Ttemp < -30:
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : T=' + str(Ttemp) + '<-30 : ice temperature is out of validity')
		elif 0 <= Ttemp:
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : T=' + str(Ttemp) + '>0 : ice has alreay melt')
		else:
			if (-30 <= Ttemp) & (Ttemp <= -22.9):
				mm = 2
			elif (-22.9 < Ttemp) & (Ttemp <= -2):
				mm = 1
			elif (-2 < Ttemp) & (Ttemp <= 0):
				mm = 0
			P1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
			P2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

			F1 = np.polyval(P1, Ttemp)
			F2 = np.polyval(P2, Ttemp)

			vf_a[ii] = ((1 - rho_si_temp / rho_i[ii] + rho_si_temp * Stemp * F2 / F1))
	return vf_a


def ice_density(T, flag_comment='y'):
	"""
		Calculate the density of the pure water ice in function of the temperature

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
		flag_comment : {'y','n'}, optional
			Whether to display the commet or not. Default is 'y'

		Returns
		----------
		rho_i: ndarray
			density of the ice in gram per cubic centimeters [g cm^{-3}]

		Sources
		----------
		Equation 2.7 in Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell

		from Pounder. E. R. 1965. The physics of ice. Oxford. etc .. Pergamon Press. (The Commonwealth and International Library. Geophysics Division.) Ringer.

	"""
	import numpy as np

	# Physical constant
	A = [-0.000117, 1]
	B = 0.917

	T = np.atleast_1d(T)
	T = icdt.make_array(T)
	iimax = len(T)
	rho_ice = np.empty((iimax))
	rho_ice[:] = np.nan

	rho_ice[np.where(T < 0)] = B * np.polyval(A, T[np.where(T < 0)])

	if flag_comment == 'y':
		if T > 0 :
			print('Temperature above 0°C : ice has melt')
		for ii in np.where(T >= 0)[0]:
			print('layer ' + str(ii + 1) + ' : T=' + str(T[ii]) + '°C')

	return rho_ice


def brine_density(T):
	"""
		Calculate the density of the brine in function of the temperature.

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]

		Returns
		----------
		rho_b: ndarray
			density of the brine in gram per cubic centimeters [g cm^{-3}]

		Sources
		----------
		Equation 2.9 in Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell

		from equation (3) in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice samples during shipping and storage. J. Glaciol, 32(112)

		from Zubov, N.N. (1945), L'dy Arktiki [Arctic ice]. Moscow, Izdatel'stvo Glavsevmorputi.

	"""
	# Physical constant
	A = [8 * 10 ** (-4), 1]
	T = icdt.make_array(T)

	S_b = brine_salinity(T)
	rho_b = (A[1] + A[0] * S_b)

	return rho_b


def seaice_density(T, S, vf_a='default', flag_comment='y'):
	"""
		Calculate the density of seaice in function of the temperature and salinity

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
			If T is an array, S must be an array of the same length
		S : array_like, number
			Salinity in practical salinity unit [PSU]
			If S is an array, T must be an array of the same length
		vf_a : optional, array_like, number
			Air volume fraction, unitless [-].
			If air volume fraction is not defined, defaults value is set to 0.5‰. Usual value for first year sea ice, before spring warming.
			If Vf_a is an array, it tmust be the same length as T and S

		Returns
		----------
		rho_si: ndarray
			density of the brine in gram per cubic centimeters [g cm^{-3}]

		Sources
		----------
		Equation 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).

		Coefficient form Cox & Weeks (1983)  and Leppäranta & Manninen (1988) [Leppäranta, M. & Manninen, T. (1988), The brine an gas content of sea ice with attention to low salinities and high temperatures. Finnish Institute of Marien Research Internal Report 88-2, Helsinki.
	"""
	import numpy as np
	import warnings

	# check parameters
	T = icdt.make_array(T)
	S = icdt.make_array(S)

	if len(T) > 1:
		if len(T) != len(S):
			print('rho SI T and S profile should be the same length')
			deltaT = len(T) - len(S)
			if deltaT < 0:
				deltaT = len(T) - len(S)
				temp = np.empty((-deltaT))
				temp[:] = np.nan
				T = np.append(T, temp)
			elif deltaT > 0:
				lenT = len(T)
				T = T[0:len(S)]
				T[len(S):lenT] = np.nan
				S[len(S):lenT] = np.nan

	if vf_a == 'default':
		vf_a = np.array([0.0005])
		warnings.warn('Air volume fraction is set to default value: Vf_a=0.5 ‰', UserWarning)
	else:
		vf_a = icdt.make_array(vf_a)
		if len(vf_a) != len(S) & len(vf_a) != 1:
			print('Vf_a should be the same length as T and S')
			return 0

	iimax = len(T)
	rho_seaice = np.empty(iimax)
	rho_seaice[:] = np.nan

	# Physical constant
	A = np.empty((4, 4, 2))

	# coefficient for T<=-22.9
	A[0, 0, :] = [-0.041221, 0.090312]
	A[0, 1, :] = [-18.407, -0.016111]
	A[0, 2, :] = [0.58402, 1.2291 * 10 ** (-4)]
	A[0, 3, :] = [0.21454, 1.3603 * 10 ** (-4)]

	# coefficient for -22.9<T<=-2
	A[1, 0, :] = [-4.732, 0.08903]
	A[1, 1, :] = [-22.45, -0.01763]
	A[1, 2, :] = [-0.6397, -5.330 * 10 ** (-4)]
	A[1, 3, :] = [-0.01074, -8.801 * 10 ** (-6)]

	# coefficient for -2<T<=0
	A[2, 0, :] = [9899, 8.547]
	A[2, 1, :] = [1309, 1.089]
	A[2, 2, :] = [55.27, 0.04518]
	A[2, 3, :] = [0.7160, 5.819 * 10 ** (-4)]

	rho_i = ice_density(T, 'n')
	rho_seaice = np.empty(iimax)
	rho_seaice[:] = np.nan

	for ii in range(0, iimax):
		Ttemp = T[ii];
		Stemp = S[ii];
		if np.isnan(Ttemp):
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : Temperature not defined')
			rho_seaice[ii] = (np.nan)
		elif np.isnan(Stemp):
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : Salinity not defined')
			rho_seaice[ii] = (np.nan)
		elif Ttemp < -30:
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : T=' + str(Ttemp) + '<-30 : ice temperature is out of validity')
		elif 0 <= Ttemp:
			if flag_comment == 'y':
				print('layer ' + str(ii) + ' : T=' + str(Ttemp) + '>0 : ice has alreay melt')
		else:
			if (-30 <= Ttemp) & (Ttemp <= -22.9):
				mm = 0
			elif (-22.9 < Ttemp) & (Ttemp <= -2):
				mm = 1
			elif (-2 < Ttemp) & (Ttemp <= 0):
				mm = 2

			P1 = [A[mm, 3, 0], A[mm, 2, 0], A[mm, 1, 0], A[mm, 0, 0]]
			P2 = [A[mm, 3, 1], A[mm, 2, 1], A[mm, 1, 1], A[mm, 0, 1]]

			F1 = np.polyval(P1, Ttemp)
			F2 = np.polyval(P2, Ttemp)

			rho_seaice[ii] = ((1 - vf_a) * (rho_i[ii] * F1 / (F1 - rho_i[ii] * Stemp * F2)));
	return rho_seaice


def brine_salinity(T, method='CW', flag_comment='y'):
	"""
		Calculate the salinity of the brine in function of the temperature at equilibrium.

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
		method : {'AS','CW'}, optional
			Whether to calculate the salinity with Assur model ('AS') or with the equation of Cox & Weeks (1983) ('CW'). Default is 'CW'

		Returns
		----------
		S_b: ndarray
			salinity of the brine in Practical Salinity Unit [PSU]

		Sources
		----------
		'AS' : Equation 2.8 in Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell
		'CW' : Equation 25 in Cox, G. F. N., & Weeks, W. F. (1986). Changes in the salinity and porosity of sea-ice samples during shipping and storage. J. Glaciol, 32(112), 371–375
	"""
	import numpy as np

	T = icdt.make_array(T)

	iimax = len(T)
	S_b = np.empty(iimax)
	S_b[:] = np.nan

	if method == 'AS':
		if T.all > -23:
			S_b = ((1 - 54.11 / T) ** (-1)) * 1000
		else:
			print('At least one temperature is inferior to -23[°C]. Cox & Weeks equation is used instead')
			brine_salinity(T, 'CW')
	else:
		# Physical constant
		A = np.empty((3, 4))
		# coefficient for -54<T<=-44
		A[0, :] = [-4442.1, -277.86, -5.501, -0.03669];

		# coefficient for -44<T<=-22.9
		A[1, :] = [206.24, -1.8907, -0.060868, -0.0010247];

		# coefficient for -22.9<T<=-2
		A[2, :] = [-3.9921, -22.700, -1.0015, -0.019956];

		for ii in range(0, iimax):
			if np.isnan(T[ii]):
				if flag_comment == 'y':
					print('layer ' + str(ii) + ' : Temperature not defined')
			elif T[ii] < -54:
				if flag_comment == 'y':
					print('layer ' + str(ii) + ' : T=' + str(T[ii]) + '<-54 : ice temperature is out of validity')
			elif 0 <= T[ii]:
				if flag_comment == 'y':
					print('layer ' + str(ii) + ' : T=' + str(T[ii]) + '>0 : ice has alreay melt')
			else:
				if (-54 < T[ii]) & (T[ii] <= -44):
					mm = 0
				elif (-44 < T[ii]) & (T[ii] <= -22.9):
					mm = 1
				elif (-22.9 < T[ii]) & (T[ii] <= 0):
					mm = 2

				P1 = [A[mm, 3], A[mm, 2], A[mm, 1], A[mm, 0]]

				S_b[ii] = (np.polyval(P1, T[ii]))
	return S_b


def brine_thermalConductivity(T, flag_comment='y'):
	"""
		Calculate thermal conductivity of brine

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
			If T is an array, S should be an array of the same length

		Returns
		----------
		lambda_si ndarray
			Volume fraction of brine in the ice

		Sources
		----------
		Equation 2.12 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell

		From Yen, Y. C., Cheng, K. C., and Fukusako, S. (1991) Review of intrinsic thermophysical properties of snow, ice, sea ice, and frost. In: Proceedings 3rd International Symposium on Cold Regions Heat Transfer, Fairbanks, AK, June 11-14, 1991. (Ed. by J. P. Zarling & S. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
	"""
	import numpy as np

	# Physical constant
	A = [0.00014, 0.030, 1.25]
	B = 0.4184
	T = icdt.make_array(T)

	iimax = len(T)
	lambda_b = np.empty((iimax))
	lambda_b[:] = np.nan

	lambda_b[np.where(T < 0)] = B * np.polyval(A, T[np.where(T < 0)])

	if flag_comment == 'y':
		for ii in np.where(T >= 0)[0]:
			print('layer ' + str(ii + 1) + ' : T=' + str(T[ii]) + '°C, ice has melt')
	for ii in np.where(lambda_b < 0)[0]:
		lambda_b[ii] = np.nan
		if flag_comment == 'y':
			print('layer ' + str(ii + 1) + ' : conductivity not defined')
	return lambda_b


def ice_thermalConductivity(T, flag_comment='y'):
	"""
		Calculate thermal conductivity of ice

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
			If T is an array, S should be an array of the same length

		Returns
		----------
		lambda_si ndarray
			Volume fraction of brine in the ice

		Sources
		----------
		Equation 2.11 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell

		From Yen, Y. C., Cheng, K. C., and Fukusako, S. (1991) Review of intrinsic thermophysical properties of snow, ice, sea ice, and frost. In: Proceedings 3rd International Symposium on Cold Regions Heat Transfer, Fairbanks, AK, June 11-14, 1991. (Ed. by J. P. Zarling & S. L. Faussett), pp. 187-218, University of Alaska, Fairbanks
	"""
	import numpy as np

	# Physical constant
	A = [2.97 * 10 ** (-5), -8.66 * 10 ** (-3), 1.91]
	B = 1.16

	T = icdt.make_array(T)

	iimax = len(T)
	lambda_i = np.empty((iimax))
	lambda_i[:] = np.nan

	lambda_i[np.where(T < 0)] = B * np.polyval(A, T[np.where(T < 0)])

	if flag_comment == 'y':
		for ii in np.where(T >= 0)[0]:
			print('layer ' + str(ii + 1) + ' : T=' + str(T[ii]) + '°C, ice has melt')
	return lambda_i


def seaice_thermalConductivity(T, S, method='Maykut', flag_comment='y'):
	"""
		Calculate bulk thermal conductivity of sea ice

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
			If T is an array, S should be an array of the same length
		S : array_like, number
			Salinity in practical salinity unit [PSU]
			If S is an array, T should be an array of the same length
		method : optional, string
			thermal conductivity could be either calculated with Maykut or Pringle equation

		Returns
		----------
		lambda_si ndarray
			Volume fraction of brine in the ice

		Sources
		----------
		Equation 2.14 and 2.16 in Eicken, H. (2003). From the microscopic, to the macroscopic, to the regional scale: growth, microstructure and properties of sea ice. In Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell

		Pringle method is describe in Pringle, D. J., Eicken, H., Trodahl, H. J., & Backstrom, L. G. E. (2007). Thermal conductivity of landfast Antarctic and Arctic sea ice. Journal of Geophysical Research, 112(C4), C04017. doi:10.1029/2006JC003641

		Maykut method is describe in Maykut, G. A. (1986). The surface heat and mass balance. In N. Understeiner (Ed.), The geophysics of sea ice (pp. 395–463). Dordrecht (NATO ASI B146): Martinus Nijhoff Publishers.
	"""
	import numpy as np

	T = icdt.make_array(T)
	S = icdt.make_array(S)

	if len(T) > 1:
		if len(T) != len(S):
			print('T and S profile should be the same length')
			return 0

	iimax = len(T)
	lambda_si = np.empty((iimax))
	lambda_si[:] = np.nan

	if method == 'Maykut':
		# Physical constant
		A = 0.13

		lambda_si[np.where(T < 0)] = (
		ice_thermalConductivity(T[np.where(T < 0)]) + A * S[np.where(T < 0)] / T[np.where(T < 0)])

	elif method == 'Pringle':
		rho_si = seaice_density(T, S, flag_comment='n')
		rho_i = ice_density(T, flag_comment='n')

		lambda_si[np.where(T < 0)] = rho_si[np.where(T < 0)] / rho_i[np.where(T < 0)] * (
		2.11 - 0.011 * T[np.where(T < 0)] + 0.09 * S[np.where(T < 0)] / T[np.where(T < 0)] - (
		rho_si[np.where(T < 0)] - rho_i[np.where(T < 0)]) / 1000)

	if flag_comment == 'y':
		for ii in np.where(T >= 0)[0]:
			print('layer ' + str(ii + 1) + ' : T=' + str(T[ii]) + '°C, ice has melt')
	for ii in np.where(lambda_si < 0)[0]:
		lambda_si[ii] = np.nan
		if flag_comment == 'y':
			print('layer ' + str(ii + 1) + ' : conductivity not defined')

	return lambda_si


def seaice_latentheat(T, S, transformation='fusion'):
	"""
		Calculate bulk latent heat from temperature and salinity during freezing ('f') or melting ('m')

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
			If T is an array, S should be an array of the same length
		S : array_like, number
			Salinity in practical salinity unit [PSU]
			If S is an array, T should be an array of the same length
		transformation : optional, string
			direction of the phase transformation: solidification ('freezing') or fusion ('melting')
			default phase transformation is solidification

		Returns
		----------
		L_si: ndarray
			Sea Ice latent heat of fusion

		Sources
		----------
		Equation 2.28 and 2.29 in Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell

		from Equation (16) Ono, N. (1967). Specific heat and heat of fusion of sea ice. In Physic of Snow and Ice (H. Oura., Vol. 1, pp. 599–610).

	"""
	T = icdt.make_array(T)
	S = icdt.make_array(S)

	if len(T) > 1:
		if len(T) != len(S):
			print('T and S profile should be the same length')
			return 0


	# Pysical Constant
	L = 333.4  # [kJ kg^{-1}] latent heat of fusion of freshwater
	m_m = -0.05411  # [K]  slope of the liquid
	c_i = 2.11  # [kJ kg^{-1}K^{-1}] specific heat cpacity of ice @ 0°C
	c_w = 4.179  # [kJ kg^{-1}K^{-1}] specific heat cpacity of freshwater @ 0°C
	S_0 = 35  # [PSU] Standard Seawater Salinity

	s00 = 'freezing'
	s01 = 'solidification'
	s10 = 'fusion'
	s11 = 'melting'

	if s00.startswith(transformation) or s01.startswith(transformation):
		L_si = L - c_i * T + c_i * m_m * S - m_m * L * (S / T) + c_w * m_m * (S_0 - S)
	elif s10.startswith(transformation) or s11.startswith(transformation):
		L_si = L - c_i * T + c_i * m_m * S - m_m * L * (S / T)
	return L_si


def seawater_freezingpoint(SW, p=10.1325):
	"""
	Parameters
	----------
		SW : array_like, number
			salinity of sea water in [PSU]
		p : array_like, number
			atmospheric pressure in [dbar]. atmospheric pressure at sea level by default p = 10.1325

	Returns
	----------
		sigma: ndarray
			conductivity of the brine in microsiemens/meter [mS/m]

		Valid for SW 4-40, and p up to 500
	"""
	p  = icdt.make_array(p)
	SW = icdt.make_array(SW)

	iimax = len(SW)

	T_fsw = []

	A = [-0.0575, +1.710523e-3, -2.154996e-4]
	B = [-7.53e-4]

	for ii in range(0, iimax):
		T_fsw.append(A[0]*SW[ii]+A[1]*(SW[ii]*(3/2))+A[2]*(SW[ii]**2)+B[0]*p)
	return T_fsw


def brine_electricconductivity(T, flag_comment='n'):
	"""
		Calculate the electric conductivity of brine for a given temperature

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]

		Returns
		----------
		sigma: ndarray
			conductivity of the brine in microsiemens/meter [mS/m]

		Equation
		_________
			Fofonoff, Nick P., and Robert C. Millard. "Algorithms for computation of fundamental properties of seawater." (1983).
	"""
	import numpy as np

	T = icdt.make_array(T)
	iimax = len(T)

	# Physical constant
	A = [0.08755, 0.5193]

	sigma_b = []
	for ii in range(0, iimax):
		sigma_b.append(-T[ii] * np.exp(np.polyval(A, T[ii])))
	return np.array(sigma_b)


def seaice_electricconductivity(T, S, rho_si=0.917, flag_comment='n'):
	"""
		Calculate the electric conductivity of sea ice for a given temperature and salinity

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
		S : array_like, number
			Salinity in practical salinity unit [PSU]
		rho_si : optional, array_like, number
			density of the ice in gram per cubic centimeter [g cm^{-3}]. Defaults 0.917.

		Returns
		----------
		sigma_si: ndarray
			conductivity of seaice in microsiemens/meter [S/m]
	"""
	T = icdt.make_array(T)
	S = icdt.make_array(S)
	rho_si = icdt.make_array(rho_si)

	# todo improve this method by getting the length of the ice core
	if len(T) > 1:
		if len(T) != len(S):
			if flag_comment == 'y':
				print('Vb T and S profile should be the same length')
			deltaT = len(T) - len(S)
			if deltaT < 0:
				temp = np.empty((-deltaT))
				temp[:] = np.nan
				T = np.append(T, temp)
			elif deltaT > 0:
				# reinterpolation of T for the length of S
				# xS = np.linspace(0,1,len(S))
				# xT = np.linspace(0,1,len(T))
				# T = np.interp(xS, xT, T)
				# todo: interpolation is a good idea, but does not work as I wish it works better to add a marker for short core in the data.
				lenT = len(T)
				T = T[0:len(S)]
				T[len(S):lenT] = np.nan
				S[len(S):lenT] = np.nan

	sigma_b = brine_electricconductivity(T, flag_comment='n')
	vf_b = brine_volumefraction(T, S, rho_si, flag_comment='n')

	sigma_si = sigma_b * (vf_b) ** 2

	return sigma_si


def seaice_resistivity(T, S, rho_si=0.917):
	"""
		Calculate the electric resistivity of sea ice for a given temperature and salinity

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
		S : array_like, number
			Salinity in practical salinity unit [PSU]
		rho_si : optional, array_like, number
			density of the ice in gram per cubic centimeter [g cm^{-3}]. Defaults 0.917.

		Returns
		----------
		rhoel_si: ndarray
			resistiviy of seaice in microsiemens/meter [S/m]
	"""
	T = icdt.make_array(T)
	S = icdt.make_array(S)
	# Need to check if array is the same length as T and S otherway return error message
	rho_si = icdt.make_array(rho_si)

	sigma_b = brine_electricconductivity(T)
	vf_b = brine_volumefraction(T, S, rho_si)

	rhoel_si = (sigma_b * (vf_b) ** 2) ** (-1)

	return rhoel_si


def seaice_permeability(T, S, rho_si='default', flag_comment='n'):
	"""
		Calculate the volume fraction of brine in function of the temperature and salinity

		Parameters
		----------
		T : array_like, number
			Temperature in degree Celsius [°C]
			If T is an array, S should be an array of the same length
		S : array_like, number
			Salinity in practical salinity unit [PSU]
			If S is an array, T should be an array of the same length
		rho_si : optional, array_like, number
			density of the ice in gram per cubic centimeter [g cm^{-3}]. Defautl is calculated for T,S value with a default air volume fraction set to 0.5‰.
			If rho_si is an array, T should be an array of the same length
		flag_comment : option, string
			toggle comment on/off

		Returns
		----------
		vf_b: ndarray
			Volume fraction of brine in the ice

		Sources
		----------
		Thomas, D. & G. S. Dieckmann, eds. (2010) Sea ice. London: Wiley-Blackwell
		from equation 5 and 15 in Cox, G. F. N., & Weeks, W. F. (1983). Equations for determining the gas and brine volumes in sea ice samples. Journal of Glaciology (Vol. 29, pp. 306–316).

	"""
	# check array lengths
	T = icdt.make_array(T)
	S = icdt.make_array(S)

	# todo improve this method by getting the length of the ice core
	if len(T) > 1:
		if len(T) != len(S):
			print('Vb T and S profile should be the same length')
			deltaT = len(T) - len(S)
			if deltaT < 0:
				temp = np.empty((-deltaT))
				temp[:] = np.nan
				T = np.append(T, temp)
			elif deltaT > 0:
				# reinterpolation of T for the length of S
				# xS = np.linspace(0,1,len(S))
				# xT = np.linspace(0,1,len(T))
				# T = np.interp(xS, xT, T)
				# T = np.interp(xS, xT, T)
				# todo: interpolation is a good idea, but does not work as I wish it works.
				lenT = len(T)
				T = T[0:len(S)]
				T[len(S):lenT] = np.nan
				S[len(S):lenT] = np.nan
		else:
			T = T[0:len(S)]

	if rho_si == 'default':
		rho_si = seaice_density(T, S, flag_comment='n')
	else:
		rho_si = icdt.make_array(rho_si)
		if len(rho_si) != len(S) or len(rho_si) != 1:
			print('rho_si should be the same length as T and S')
			rho_si = np.ones(len(S))[:] * rho_si

	Vf_b = brine_volumefraction(T, S, rho_si='default', flag_comment='n')
	k = 3 * Vf_b ** 2 * 10 ** (-10)
	return k
