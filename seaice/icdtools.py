#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
icdtools.py: icdtools provide several function use by icecoredata.py and seaice.py.
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

import numpy as np

__all__ = ['make_array', 'column_merge', 'discretized']


def make_array(data):
    """
        make_array convert data in an array
    """
    temp = []
    if isinstance(data, (int, float)):
        temp.append(data)
        data = np.array(temp)
    return data


def make_stat(data, axis=1):
    stat = np.empty((data.shape[0], 5, data.shape[2]))

    for ii in range(0, data.shape[2]):
        stat[:, 0, ii] = np.nanmean(data[:, :, ii], axis)
        stat[:, 1, ii] = np.nanstd(data[:, :, ii], axis)
        stat[:, 2, ii] = np.nanmin(data[:, :, ii], axis)
        stat[:, 3, ii] = np.nanmax(data[:, :, ii], axis)
        stat[:, 4, ii] = np.sum(~np.isnan(data[:, :, ii]), axis)  # number of sample for every stat
    return stat


def nan_mat(shape, dtype=float):
    a = np.empty(shape, dtype)
    a.fill(np.nan)
    return a


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def index_from_day(data, start_day, end_day='False', lcomment='n'):
    import datetime as dt

    if end_day == 'False':
        end_day = start_day
    day = start_day
    index = np.array([])

    while day <= end_day:
        index_year = np.where(data[:, 0] == day.year)[0]
        index_month = np.where(data[index_year, 1] == day.month)[0]
        index_day = np.where(data[index_year[index_month], 2] == day.day)[0]

        if index.size == 0:
            index = index_year[index_month[index_day]]
        else:
            index = np.concatenate((index, index_year[index_month[index_day]]))
        day += dt.timedelta(1)

    if lcomment == 'y':
        if len(index[0]) == 0:
            print('no data present in the dataset')

    return index


def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True


def discretized(xp, yp, section_thickness=0.05, core_length=None):
    if core_length is None:
        core_length = max(xp)
    x = np.arange(section_thickness / 2, core_length, section_thickness)
    if section_thickness / 2 <= core_length - x[-1]:
        x = np.concatenate((x, [core_length]))

    if np.all(np.diff(xp) <= 0):
        xp = np.fliplr(np.atleast_2d(xp))[0]
        yp = np.fliplr(np.atleast_2d(yp))[0]
    if np.all(np.diff(xp) >= 0):
        y = np.interp(x, xp, yp)
        return y
    else:
        print('X array is not increasing')


def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices), to convert logical indices of NaNs to
          'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """
    return np.isnan(y), lambda z: z.nonzero()[0]


def day_from_index(data, index, lcomment='n'):
    import datetime as datetime

    event_day = []
    for ii in index:
        event_day.append(datetime.datetime(int(data[ii][0]), int(data[ii][1]), int(data[ii][2])))

    return unique(event_day)


def T_ice_profile(ts_data, ts_data_index, ice_thickness, ts_position, ts_index, ts_ice_surface, section_thickness=0.05, lcomment='n'):
    """
    :param ts_data: matrix containing the temperature date-time and temperature data in the following form YYYY MM DD HH MM (SS) ts_0 ts_1 ...; ts_x being the temperature at the sensor x
    :param ts_data_index: array containing the rows number corresponding to the date-time of interest
    :param ice_thickness:
    :param ts_position: position of the thermistor relatively to the ice surface (negative is above ice, positive is below ice)
    :param ts_index: column at which the temperature measurement stat
    :param ts_ice_surface: thermistor number at the ice surface
    :param section_thickness:
    :param lcomment:
    :return:

    read a T file where the columna are the following
    1: year
    2: month
    3: day
    ...
    t0 : ts_index: corresponds to the column of the 1st thermistor (could be above ice surface)
    ...
    tn: t_no_ice_surface +t_index, corresponds to the column on the ice surface
    ...
    """

    t_data = np.nanmean(ts_data[ts_data_index], axis=0)

    # select T data within ice and correct profile orientation
    if np.diff(ts_position).all() : # bottom up orientation
        t_data = t_data[ts_index:ts_index + ts_ice_surface]
        t_data = t_data[::-1]
        ts_y = np.array(ts_position[:ts_ice_surface])
        ts_y = ts_y[::-1]
    else: # top bottom orientation
        t_data = t_data[-ts_ice_surface:]
        ts_y = np.array(ts_position[ts_ice_surface:])

    # t_avg : top bottom oriented temperature data measurement
    # ts_y  : top bottom oriented temperature sensor position

    # create discretized position vector according to designated section_thickness
    ytavg = np.arange(section_thickness / 2, ice_thickness, section_thickness)
    tavg = np.interp(ytavg, ts_y[~np.isnan(t_data)], t_data[~np.isnan(t_data)])

    return tavg


def ice_profile(mbs_data_yr, Tmbs_index, ice_thickness, t_no_ice_surface, section_thickness=0.05, lcomment='n'):
    """
	:param mbs_data_yr:
	:param Tmbs_index:
	:param ice_thickness:
	:param t_no_ice_surface: thermistor number at the ice surface
	:param section_thickness:
	:param lcomment:
	:return:
	"""

    import math

    Tmbs_avg = np.nanmean(mbs_data_yr[Tmbs_index], axis=0)
    Tmbs_avg = Tmbs_avg[15 + t_no_ice_surface - 1:]

    hI = np.nanmax(mbs_data_yr[
                       Tmbs_index, 5])  # TODO: detect automatically the bottom of the ice if their is no ice thickness data
    if math.isnan(hI):
        hI = ice_thickness
    xTmbs = np.arange(0, hI, 0.1)
    if xTmbs[-1] < hI:
        xTmbs = np.append(xTmbs, xTmbs[-1] + 0.1)
    Tavg = Tmbs_avg[0:len(xTmbs)]

    if ((hI - xTmbs[-1]) > section_thickness):
        yTmbs = np.arange(section_thickness / 2, xTmbs[-1] + section_thickness / 2, section_thickness)
    else:
        yTmbs = np.arange(section_thickness / 2, hI, section_thickness)
    Tmbs_avg = np.interp(yTmbs, xTmbs[~np.isnan(Tavg)], Tavg[~np.isnan(Tavg)])

    return Tmbs_avg


def align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1 - y2))
    miny, maxy = ax2.get_ylim()
    ax2.set_ylim(miny + dy, maxy + dy)


def column_merge(tup):
    """
    Stack 1-D arrays as columns into a 2-D array. Take a sequence of 1-D arrays and stack them as columns to make a
    single 2-D array. 2-D arrays are stacked  as is. 1-D arrays are turned into 2-D columns first.

    Parameters
    ----------
    tup : sequence of 1-D or 2-D arrays.
        Arrays to stack. Their first dimension could be different. They will be stacked at the top, trailing nan values
        are added to fill the column.

    Returns
    -------
    stacked : 2-D array
        The array formed by stacking the given arrays.
    See Also
    --------

    Examples
    --------
    >>> a = np.array((1,2,3))
    >>> b = np.array((2,3,4,5))
    >>> np.column_stack((a,b))
    array([[1, 2],
           [2, 3],
           [3, 4],
           [nan, 5]])
    """

    for v in tup:
        arr = np.array(v, copy=False, subok=True)
        if arr.ndim < 2:
            arr = np.array(arr, copy=False, subok=True, ndmin=2).T
        try:
            ddim = arr.shape[0] - arrays.shape[0]
        except NameError:
            arrays = arr
        else:
            if ddim > 0:
                arrays = np.concatenate([arrays, np.nan * np.ones([ddim, arrays.shape[1]])])
                arrays = np.concatenate([arrays, arr], axis=1)
            elif ddim < 0:
                arr = np.concatenate([arr, np.nan * np.ones([-ddim, arr.shape[1]])])
                arrays = np.concatenate([arrays, arr], axis=1)
            else:
                arrays = np.concatenate([arrays, arr], axis=1)

    return arrays


def vmerge2D(A, B):
    A=np.atleast_2d(A)
    B=np.atleast_2d(B)
    mat_temp = np.nan * np.ones([max(A.shape[0], B.shape[0]), A.shape[1] + B.shape[1]])
    mat_temp[0:A.shape[0], 0:A.shape[1]] = A
    mat_temp[0:B.shape[0], A.shape[1]:A.shape[1] + B.shape[1]] = B
    return mat_temp


def merge3D(A, B, position):
    A = np.atleast_3d(A)
    B = np.atleast_3d(B)

    mat_temp = np.nan * np.ones([max(A.shape[0] + position[0], B.shape[0]), max(position[1] + A.shape[1], B.shape[1]),
                                 max(position[2] + A.shape[2], B.shape[2])])
    mat_temp[0:B.shape[0], 0:B.shape[1], 0:B.shape[2]] = B
    mat_temp[position[0]:position[0] + A.shape[0], position[1]:position[1] + A.shape[1],
    position[2]:position[2] + A.shape[2]] = A

    return mat_temp

def vstack_mat(A, B, index_period, n_core):
    """
	:param A:
	:param B:
	:param index_period:
	:param index_core:
	:param ncore:
	:return:
	"""

    # look for the first nan row in the array
    f0 = 0
    dim2s = B.shape[1]
    for ii in range(0, B.shape[1]):
        if np.isnan(B[index_period][ii][:]).all() and f0 == 0:
            dim2s = ii
            f0 += 1

    try:
        A.shape[1]
    except IndexError:
        dim3 = A.size - B.shape[2]
        dim2 = 1 - (B.shape[1] - dim2s)
        if dim3 >= 0:
            temp = np.empty((B.shape[0], B.shape[1], dim3))
            temp.fill(np.nan)
            B = np.concatenate((B, temp), axis=2)
        elif dim3 < 0:
            temp = np.empty(-dim3)
            temp.fill(np.nan)
            A = np.concatenate((A, temp), axis=1)
    else:
        dim3 = A.shape[1] - B.shape[2]
        dim2 = A.shape[0] - (B.shape[1] - dim2s)
        if dim3 >= 0:
            temp = np.empty((B.shape[0], B.shape[1], dim3))
            temp.fill(np.nan)
            B = np.concatenate((B, temp), axis=2)
        elif dim3 < 0:
            temp = np.empty((A.shape[0], -dim3))
            temp.fill(np.nan)
            A = np.concatenate((A, temp), axis=1)

    if dim2 > 0:
        temp = np.empty((B.shape[0], dim2, B.shape[2]))
        temp.fill(np.nan)
        B = np.concatenate((B, temp), axis=1)

    B[index_period][dim2s:dim2s + n_core][:] = A[:][:]

    return B


def DegreeDayModel(data, T_col, freezup_day, end_day, Tfreeze=0, Tunit='C'):
    """
    Calculate the number of freezing degree days between the freezup day until a certain day (end_day)
    Number of thawing degree day (FDD) for the day 'day' is given by the following code
        import datetime as dt
        PDD=(day-freezup_day).days-FDD[day]+1

    Parameters
    ----------
    data :
        File path, included filename, to the file containing the data to import
    feezup_day :
        File path, included filename, to the file containing the data to import
    end_day :
        File path, included filename, to the file containing the data to import
    Tfreeze: float, optional
        File path, included filename, to the file containing the data to import
    Hdawn: int, optional
        File path, included filename, to the file containing the data to import
    Hdusk: int, optional
        File path, included filename, to the file containing the data to import

    Returns
    ----------
    DD: dict
        contains day and numbers of freezing and thawing degree days until this day
        day : [FDD, TDD]
    """

    import datetime

    current_day = freezup_day
    DD = {}
    n_FDD = 0
    n_TDD = 0
    if Tunit == 'K':
        T_offset = 0
    elif Tunit == 'C':
        T_offset = -273
    elif Tunit == 'F':
        print("You're kidding, just use scientific unit!")

    while current_day <= end_day:
        day_index = index_from_day(data, current_day)
        T_current_day = []
        for ii in day_index:
            T_current_day.append(data[ii, T_col - 1] + T_offset)  # temperature given in K
        T_mean_current_day = np.nanmean(T_current_day)
        DD_value = (Tfreeze - T_mean_current_day)#* 24
        if 0 < DD_value:
            n_FDD += DD_value
        else:
            n_TDD += DD_value
        DD[current_day] = [n_FDD, n_TDD]
        current_day += datetime.timedelta(1)
    return DD


def reverseDD(data, T_col, start_day, end_day, Tfreeze=0, Tunit='C'):
    """
    Calculate the number of freezing degree days between from a given date in the future to a present day.
    Number of thawing degree day (FDD) for the day 'day' is given by the following code
        import datetime as dt
        PDD=(day-freezup_day).days-FDD[day]+1

    Parameters
    ----------
    data :
        File path, included filename, to the file containing the data to import
    feezup_day :
        File path, included filename, to the file containing the data to import
    end_day :
        File path, included filename, to the file containing the data to import
    Tfreeze: float, optional
        File path, included filename, to the file containing the data to import
    Hdawn: int, optional
        File path, included filename, to the file containing the data to import
    Hdusk: int, optional
        File path, included filename, to the file containing the data to import

    Returns
    ----------
    DD: dict
        contains day and numbers of freezing and thawing degree days until this day
        day : [FDD, TDD]
    """

    import datetime
    DD = {}
    n_FDD = 0
    n_TDD = 0
    if Tunit == 'K':
        T_offset = -273
    elif Tunit == 'C':
        T_offset = 0
    elif Tunit == 'F':
        print("You're kidding, just use standardize unit!")

    ii_day = start_day
    if end_day < start_day:
        # freezing degree days
        while end_day <= ii_day:
            day_index = index_from_day(data, ii_day)
            T_ii_day = []
            for ii in day_index:
                T_ii_day.append(data[ii, T_col - 1] + T_offset)  # temperature given in K
            T_mean_ii_day = np.nanmean(T_ii_day)
            DD_value = (Tfreeze - T_mean_ii_day)#* 24
            if 0 < DD_value:
                n_FDD += DD_value
            else:
                 n_TDD = 0 # +=DD_value
            DD[ii_day] = [n_FDD, n_TDD]
            ii_day -= datetime.timedelta(1)
        # thawing degree days
        ii_day = start_day
        while ii_day <= datetime.datetime(start_day.year, 9, 15):
            day_index = index_from_day(data, ii_day)
            T_ii_day = []
            for ii in day_index:
                T_ii_day.append(data[ii, T_col - 1] + T_offset)  # temperature given in K
            T_mean_ii_day = np.nanmean(T_ii_day)
            DD_value = (Tfreeze - T_mean_ii_day)#* 24
            if 0 < DD_value:
                if ii_day in DD.keys():
                    n_FDD = DD[ii_day][0]
                else:
                    n_FDD += DD_value
            else:
                n_TDD += DD_value
            DD[ii_day] = [n_FDD, n_TDD]
            ii_day += datetime.timedelta(1)
    else:
        while ii_day <= end_day:
            day_index = index_from_day(data, ii_day)
            T_ii_day = []
            for ii in day_index:
                T_ii_day.append(data[ii, T_col - 1] + T_offset)  # temperature given in K
            T_mean_ii_day = np.nanmean(T_ii_day)
            DD_value = (Tfreeze - T_mean_ii_day)#* 24
            if 0 < DD_value:
                n_FDD += DD_value
            else:
                n_TDD += DD_value
            DD[ii_day] = [n_FDD, n_TDD]
            ii_day += datetime.timedelta(1)
    return DD

def day_from_index(data, index, lcomment='n'):
    import datetime as dt

    event_day = []
    for ii in index:
        event_day.append(dt.datetime(int(data[ii][0]), int(data[ii][1]), int(data[ii][2])))

    return unique(event_day)
