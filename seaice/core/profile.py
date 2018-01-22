# ! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.profile.py : toolbox to work on property profile

"""
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

__name__ = "profile"
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/09/13"
__comment__ = "profile.py contained function to handle property profile"
__CoreVersion__ = 1.1

__all__ = ["discretize_profile", "set_vertical_reference", "select_profile", "set_profile_orientation",
           "delete_profile"]

TOL = 1e-6

# TODO create a function to fill gap within a profile
# this version fo discretize_profile is deprecated
# def discretize_profile(profile, y_bins=None, y_mid=None, variables=None, display_figure=False, fill_gap=True):
#     """
#     :param profile:
#     :param y_bins:
#     :param y_mid:
#     :param variables:
#     :param display_figure:
#     :param fill_gap:
#     :return:
#     """
#     logger = logging.getLogger(__name__)
#
#     if profile.empty:
#         logger.warning("Discretization impossible, empty profile")
#         return profile
#     else:
#         if 'name' in profile.keys():
#             logger.info("Processing %s" % profile.name.unique()[0])
#         else:
#             logger.info("Processing")
#
#     v_ref = profile.v_ref.unique()[0]
#
#     # VARIABLES CHECK
#     if y_bins is None and y_mid is None:
#         y_bins = pd.Series(profile.y_low.dropna().tolist() + profile.y_sup.dropna().tolist()).sort_values().unique()
#         y_mid = profile.y_mid.dropna().sort_values().unique()
#         logger.info("y_bins and y_mid are empty, creating from profile")
#     elif y_bins is None:
#         if y_mid is not None:
#             logger.info("y_bins is empty, creating from given y_mid")
#             y_mid = y_mid.sort_values().values
#             dy = np.diff(y_mid) / 2
#             y_bins = np.concatenate([[y_mid[0] - dy[0]], y_mid[:-1] + dy, [y_mid[-1] + dy[-1]]])
#             if y_bins[0] < 0:
#                 y_bins[0] = 0
#     elif y_mid is None:
#         if y_bins is not None:
#             y_mid = np.diff(y_bins) / 2 + y_bins[:-1]
#             logger.info("y_mid is empty, creating from given y_bins")
#
#     y_bins = np.array(y_bins)
#     y_mid = np.array(y_mid)
#
#     if variables is None:
#         variables = [variable for variable in profile.variable.unique().tolist() if variable in profile.keys()]
#
#     if not isinstance(variables, list):
#         variables = [variables]
#
#     discretized_profile = pd.DataFrame()
#
#     for variable in variables:
#         temp = pd.DataFrame()
#
#         if profile[profile.variable == variable].empty:
#             logger.debug("\t %s profile is missing" % variable)
#         else:
#             logger.debug("\t %s profile is discretized" % variable)
#
#         # continuous profile (temperature-like)
#         if is_continuous_profile(profile[profile.variable == variable]):
#             yx = profile[profile.variable == variable].set_index('y_mid').sort_index()[[variable]]
#             yx = yx.dropna(how='all')  # drop row with all NA value
#
#             y2x = yx.reindex(y_mid)
#             for index in yx.index:
#                 y2x.loc[abs(y2x.index - index) < 1e-6, variable] = yx.loc[yx.index == index, variable].values
#             dat_temp = np.interp(y2x.index, yx.index, yx[variable].astype(float), left=np.nan, right=np.nan)
#             y2x = pd.DataFrame(dat_temp, index=y2x.index, columns=[variable])
#             temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(y_mid.__len__()))
#             temp.update(y2x.reset_index())
#
#             profile_prop = profile.head(1)
#             profile_prop = profile_prop.drop(variable, 1)
#             profile_prop['variable'] = variable
#             if 'y_low' in profile_prop:
#                 profile_prop = profile_prop.drop('y_low', 1)
#             profile_prop = profile_prop.drop('y_mid', 1)
#             if 'y_sup' in profile_prop:
#                 profile_prop = profile_prop.drop('y_sup', 1)
#             temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
#                                      index=temp.index.tolist()))
#             if 'date' in temp:
#                 temp['date'] = temp['date'].astype('datetime64[ns]')
#
#             if display_figure:
#                 plt.figure()
#                 yx = yx.reset_index()
#                 plt.plot(yx[variable], yx['y_mid'], 'k')
#                 plt.plot(temp[variable], temp['y_mid'], 'xr')
#                 if 'name' in profile_prop.keys():
#                     plt.title(profile_prop.name.unique()[0] + ' - ' + variable)
#
#         # step profile (salinity-like)
#         elif ('y_low' in profile and not profile[profile.variable == variable].y_low.isnull().all() and
#                       profile[profile.variable == variable].y_low.__len__() > 0):
#             if v_ref == 'bottom':
#                 yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
#                     ['y_sup', 'y_low', variable])
#                 if yx[0, 0] > yx[0, 1]:
#                     yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
#                         ['y_low', 'y_sup', variable])
#             else:
#                 yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
#                     ['y_low', 'y_sup', variable])
#
#             x_step = []
#             y_step = []
#             ii_bin = 0
#
#             if yx[0, 0] - y_bins[0] <= TOL:
#                 ii_yx = np.where(yx[:, 0] - y_bins[0] <= TOL)[0][-1]
#             else:
#                 ii_bin = np.where(y_bins - yx[0, 0] <= TOL)[0][-1]
#                 ii_yx = 0
#                 ii = 0
#                 while ii < ii_bin:
#                     y_step.append(y_bins[ii])
#                     y_step.append(y_bins[ii + 1])
#                     x_step.append(np.nan)
#                     x_step.append(np.nan)
#                     ii += 1
#
#             # skip first bin, if value not completely in:
#             if yx[ii_yx, 0] - y_bins[ii_bin] >= TOL:
#                 y_step.append(y_bins[ii])
#                 y_step.append(y_bins[ii + 1])
#                 x_step.append(np.nan)
#                 x_step.append(np.nan)
#                 ii_bin  +=1
#                 while yx[ii_yx, 1] - y_bins[ii_bin] <= TOL:
#                     ii_yx += 1
#
#             while ii_bin < y_bins.__len__() - 1:
#
#                 while ii_bin + 1 < y_bins.__len__() and y_bins[ii_bin + 1] - yx[ii_yx, 1] <= TOL and ii_yx < yx.__len__():
#                     sy = s_nan(yx, ii_yx, fill_gap)
#                     y_step.append(y_bins[ii_bin])
#                     y_step.append(y_bins[ii_bin + 1])
#                     x_step.append(sy)
#                     x_step.append(sy)
#                     ii_bin += 1
#                     ii_yx += 1
#
#                 if not yx[-1, 1] - y_bins[ii_bin] <= TOL:
#                     ly = 0
#                     sy = 0
#                     if ii_yx < yx[:, 0].__len__() - 1:
#                         while ii_yx < yx[:, 0].__len__() - 1 and yx[ii_yx, 1] - y_bins[ii_bin + 1] <= TOL:
#                             ly += (yx[ii_yx, 1] - y_bins[ii_bin])
#                             sy += (yx[ii_yx, 1] - y_bins[ii_bin]) * s_nan(yx, ii_yx, fill_gap)
#                             ii_yx += 1
#
#                         if yx[ii_yx, 0] - y_bins[ii_bin + 1] <= TOL:
#                             sy += (y_bins[ii_bin + 1] - yx[ii_yx, 0]) * s_nan(yx, ii_yx, fill_gap)
#                             ly += y_bins[ii_bin + 1] - yx[ii_yx, 0]
#                         if ly > TOL:
#                             sy = sy / ly
#                         else:
#                             sy = np.nan
#
#                     else:
#                         sy = yx[-1, -1]
#                     y_step.append(y_bins[ii_bin])
#                     y_step.append(y_bins[ii_bin + 1])
#                     x_step.append(sy)
#                     x_step.append(sy)
#                     ii_bin += 1
#
#                 else:
#                     while ii_bin + 1 < y_bins.__len__():
#                         y_step.append(y_bins[ii_bin])
#                         y_step.append(y_bins[ii_bin + 1])
#                         x_step.append(np.nan)
#                         x_step.append(np.nan)
#                         ii_bin += 1
#
#             temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(np.unique(y_step).__len__() - 1))
#             temp.update(pd.DataFrame(np.vstack(
#                 (np.unique(y_step)[:-1], np.unique(y_step)[:-1] + np.diff(np.unique(y_step)) / 2, np.unique(y_step)[1:],
#                  [x_step[2 * ii] for ii in
#                   range(int(x_step.__len__() / 2))])).transpose(),
#                                      columns=['y_low', 'y_mid', 'y_sup', variable],
#                                      index=temp.index[0:np.unique(y_step).__len__() - 1]))
#
#             # properties
#             profile_prop = profile.head(1)
#             profile_prop = profile_prop.drop(variable, 1)
#             profile_prop['variable'] = variable
#             profile_prop = profile_prop.drop('y_low', 1)
#             profile_prop = profile_prop.drop('y_mid', 1)
#             profile_prop = profile_prop.drop('y_sup', 1)
#             temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
#                                      index=temp.index.tolist()))
#             if 'date' in temp:
#                 temp['date'] = temp['date'].astype('datetime64[ns]')
#
#             if display_figure:
#                 plt.figure()
#                 x = []
#                 y = []
#                 for ii in range(yx[:, 0].__len__()):
#                     y.append(yx[ii, 0])
#                     y.append(yx[ii, 1])
#                     x.append(yx[ii, 2])
#                     x.append(yx[ii, 2])
#                 plt.step(x, y, 'bx')
#                 plt.step(x_step, y_step, 'ro')
#                 if 'name' in profile_prop.keys():
#                     plt.title(profile_prop.name.unique()[0] + ' - ' + variable)
#
#         discretized_profile = discretized_profile.append(temp)
#
#     return discretized_profile
#

def discretize_profile(profile, y_bins=None, y_mid=None, variables=None, display_figure=False, fill_gap=False, fill_extremity=False):
    """
    :param profile:
    :param y_bins:
    :param y_mid:
    :param variables:
    :param display_figure: boolean, default False
    :param fill_gap: boolean, default True

    :param fill_extremity: boolean, default False
    :return:
        profile
    """
    logger = logging.getLogger(__name__)

    if profile.empty:
        logger.warning("Discretization impossible, empty profile")
        return profile
    else:
        if 'name' in profile.keys():
            logger.info("Processing %s" % profile.name.unique()[0])
        else:
            logger.info("Processing core")

    v_ref = profile.v_ref.unique()[0]

    # VARIABLES CHECK
    if y_bins is None and y_mid is None:
        y_bins = pd.Series(profile.y_low.dropna().tolist() + profile.y_sup.dropna().tolist()).sort_values().unique()
        y_mid = profile.y_mid.dropna().sort_values().unique()
        logger.info("y_bins and y_mid are empty, creating from profile")
    elif y_bins is None:
        if y_mid is not None:
            logger.info("y_bins is empty, creating from given y_mid")
            y_mid = y_mid.sort_values().values
            dy = np.diff(y_mid) / 2
            y_bins = np.concatenate([[y_mid[0] - dy[0]], y_mid[:-1] + dy, [y_mid[-1] + dy[-1]]])
            if y_bins[0] < 0:
                y_bins[0] = 0
    elif y_mid is None:
        if y_bins is not None:
            y_mid = np.diff(y_bins) / 2 + y_bins[:-1]
            logger.info("y_mid is empty, creating from given y_bins")

    y_bins = np.array(y_bins)
    y_mid = np.array(y_mid)

    if variables is None:
        variables = [variable for variable in profile.variable.unique().tolist() if variable in profile.keys()]

    if not isinstance(variables, list):
        variables = [variables]

    discretized_profile = pd.DataFrame()

    for variable in variables:
        if profile[profile.variable == variable].empty:
            logger.debug("\t %s profile is missing" % variable)
        else:
            logger.debug("\t %s profile is discretized" % variable)

        # continuous profile (temperature-like)
        if is_continuous_profile(profile[profile.variable == variable]):
            yx = profile[profile.variable == variable].set_index('y_mid').sort_index()[[variable]]
            yx = yx.dropna(how='all')  # drop row with all NA value

            y2x = yx.reindex(y_mid)
            for index in yx.index:
                y2x.loc[abs(y2x.index - index) < 1e-6, variable] = yx.loc[yx.index == index, variable].values
            dat_temp = np.interp(y2x.index, yx.index, yx[variable].astype(float), left=np.nan, right=np.nan)
            y2x = pd.DataFrame(dat_temp, index=y2x.index, columns=[variable])
            temp = pd.DataFrame(columns=profile.columns.tolist(), index=range(y_mid.__len__()))
            temp.update(y2x.reset_index())

            profile_prop = profile.head(1)
            profile_prop = profile_prop.drop(variable, 1)
            profile_prop['variable'] = variable
            if 'y_low' in profile_prop:
                profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            if 'y_sup' in profile_prop:
                profile_prop = profile_prop.drop('y_sup', 1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))
            if 'date' in temp:
                temp['date'] = temp['date'].astype('datetime64[ns]')

            if display_figure:
                plt.figure()
                yx = yx.reset_index()
                plt.plot(yx[variable], yx['y_mid'], 'k')
                plt.plot(temp[variable], temp['y_mid'], 'xr')
                if 'name' in profile_prop.keys():
                    plt.title(profile_prop.name.unique()[0] + ' - ' + variable)

        # step profile (salinity-like)
        else:
            if v_ref == 'bottom':
                yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                    ['y_sup', 'y_low', variable])
                if yx[0, 0] > yx[0, 1]:
                    yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                        ['y_low', 'y_sup', variable])
            else:
                yx = profile[profile.variable == variable].set_index('y_mid', drop=False).sort_index().as_matrix(
                    ['y_low', 'y_sup', variable])
            # for testing purpose only, inverse profile
            # y_bins = -y_bins
            # yx = -yx
            # yx = np.vstack(([yx[:, 1]], [yx[:, 0]], [yx[:, 2]])).transpose()

            # if missing section, add an emtpy section with np.nan as property value
            yx_new = []
            for row in range(yx[:, 0].__len__()-1):
                yx_new.append(yx[row])
                if abs(yx[row, 1]-yx[row+1, 0]) > TOL:
                    yx_new.append([yx[row, 1], yx[row+1, 0], np.nan])
            yx_new.append(yx[row+1, :])
            yx = np.array(yx_new)
            del yx_new

            if fill_gap:
                value = pd.Series(yx[:, 2])
                value_low = value.fillna(method='ffill')
                value_sup = value.fillna(method='bfill')

                ymid = pd.Series(yx[:, 0]+(yx[:, 1]-yx[:, 0])/2)
                ymid2 = pd.Series(None, index=value.index)
                ymid2[np.isnan(value)] = ymid[np.isnan(value)]

                dy = pd.DataFrame(yx[:, 0:2], columns=['y_low', 'y_sup'])
                dy2 = pd.DataFrame([[None, None]], index=value.index, columns=['y_low', 'y_sup'])
                dy2[~np.isnan(value)] = dy[~np.isnan(value)]
                dy2w = dy2['y_low'].fillna(method='bfill') - dy2['y_sup'].fillna(method='ffill')
                new_value = value_low + (ymid2 - dy2['y_sup'].fillna(method='ffill'))*(value_sup-value_low)/dy2w
                value.update(new_value)

                yx[:, 2] = value

            x_step = []
            y_step = []
            w_step = []  # weight of the bin, defined as the portion on which the property is define
            # yx and y_bins should be ascendent suit
            if (np.diff(y_bins) < 0).all():
                logger.info("y_bins is descending reverting the list")
                y_bins = y_bins[::-1]
            elif (np.diff(y_bins) > 0).all():
                logger.debug("y_bins is ascending")
            else:
                logger.info("y_bins is not sorted")
            if (np.diff(yx[:, 0]) < 0).all():
                logger.info("yx is descending reverting the list")
                yx = yx[::-1, :]
            elif (np.diff(yx[:, 0]) > 0).all():
                logger.debug("yx is ascending")
            else:
                logger.info("yx is not sorted")

            for ii_bin in range(y_bins.__len__()-1):
                a = np.flatnonzero((yx[:, 0] - y_bins[ii_bin] < -TOL) & ( y_bins[ii_bin] - yx[:, 1] < -TOL))
                a = np.concatenate((a, np.flatnonzero((y_bins[ii_bin] - yx[:, 0] <= TOL) & (yx[:, 1] - y_bins[ii_bin+1] <= TOL))))
                a = np.concatenate((a, np.flatnonzero((yx[:, 0] - y_bins[ii_bin+1] < -TOL) & ( y_bins[ii_bin+1] - yx[:, 1] < -TOL))))
                a = np.unique(a)
                #print(y_bins[ii_bin], y_bins[ii_bin+1])
                #print(a, yx[a])
                #print()

                if a.size != 0:
                    S = np.nan
                    L = 0
                    L_nan = 0
                    a_ii = 0
                    if yx[a[a_ii], 0] - y_bins[ii_bin] < -TOL:
                        S_temp = yx[a[a_ii], 2]*(yx[a[a_ii], 1] - y_bins[ii_bin])
                        if not np.isnan(S_temp):
                            if np.isnan(S):
                                S = S_temp
                            else:
                                S += S_temp
                            L += (yx[a[a_ii], 1] - y_bins[ii_bin])
                        else:
                            L_nan += (yx[a[a_ii], 1] - y_bins[ii_bin])
                        #print(y_bins[ii_bin], yx[a[a_ii], 1], S_temp)
                        a_ii +=1
                    while ii_bin+1 <= y_bins.shape[0]-1 and a_ii < a.shape[0]-1 and yx[a[a_ii], 1] - y_bins[ii_bin+1] < -TOL:
                        S_temp = yx[a[a_ii], 2] * (yx[a[a_ii], 1]-yx[a[a_ii], 0])
                        if not np.isnan(S_temp):
                            if np.isnan(S):
                                S = S_temp
                            else:
                                S += S_temp
                            L += yx[a[a_ii], 1]-yx[a[a_ii], 0]
                        else:
                            L_nan += yx[a[a_ii], 1]-yx[a[a_ii], 0]
                        #print(yx[a[a_ii], 0], yx[a[a_ii], 1], S_temp)
                        a_ii += 1

                    if yx[a[a_ii], 1] - y_bins[ii_bin+1] > -TOL:
                        S_temp = yx[a[a_ii], 2] * (y_bins[ii_bin+1] -yx[a[a_ii], 0])
                        if not np.isnan(S_temp):
                            if np.isnan(S):
                                S = S_temp
                            else:
                                S += S_temp
                            L += (y_bins[ii_bin+1] - yx[a[a_ii], 0])
                        else:
                            L_nan += (y_bins[ii_bin+1] - yx[a[a_ii], 0])
                        #print(yx[a[a_ii], 0], y_bins[ii_bin+1], S_temp)
                    elif yx[a[a_ii], 1] - y_bins[ii_bin + 1] < -TOL:
                        S_temp = yx[a[a_ii], 2] * (yx[a[a_ii], 1] -yx[a[a_ii], 0])
                        if not np.isnan(S_temp):
                            if np.isnan(S):
                                S = S_temp
                            else:
                                S += S_temp
                            L += (yx[a[a_ii], 1] -yx[a[a_ii], 0])
                        else:
                            L_nan += (yx[a[a_ii], 1] -yx[a[a_ii], 0])
                        # print(yx[a[a_ii], 0], yx[a[a_ii], 1], S_temp)

                    if L !=0:
                        S = S/L
                        w = L/(y_bins[ii_bin + 1]-y_bins[ii_bin])
                    elif L_nan != 0:
                        S = np.nan
                        w = 0
                    #print(L)
                    #print(S)
                    #print(w)
                    if yx[a[0], 0] - y_bins[ii_bin] > TOL and not fill_extremity:
                        y_step.append(yx[a[0], 0])
                        y_step.append(y_bins[ii_bin + 1])
                    elif yx[a[-1], 1] - y_bins[ii_bin + 1] < -TOL and not fill_extremity:
                        y_step.append(y_bins[ii_bin])
                        y_step.append(yx[a[-1], 1])
                    else:
                        y_step.append(y_bins[ii_bin])
                        y_step.append(y_bins[ii_bin + 1])
                    x_step.append(S)
                    x_step.append(S)
                    w_step.append(w)

            temp = pd.DataFrame(columns=profile.columns.tolist()+['weight'], index=range(np.unique(y_step).__len__() - 1))
            temp.update(pd.DataFrame(np.vstack(
                (np.unique(y_step)[:-1], np.unique(y_step)[:-1] + np.diff(np.unique(y_step)) / 2, np.unique(y_step)[1:],
                 [x_step[2 * ii] for ii in
                  range(int(x_step.__len__() / 2))], w_step)).transpose(),
                                     columns=['y_low', 'y_mid', 'y_sup', variable, 'weight'],
                                     index=temp.index[0:np.unique(y_step).__len__() - 1]))

            # properties
            profile_prop = profile.head(1)
            profile_prop = profile_prop.drop(variable, 1)
            profile_prop['variable'] = variable
            profile_prop = profile_prop.drop('y_low', 1)
            profile_prop = profile_prop.drop('y_mid', 1)
            profile_prop = profile_prop.drop('y_sup', 1)
            temp.update(pd.DataFrame([profile_prop.iloc[0].tolist()], columns=profile_prop.columns.tolist(),
                                     index=temp.index.tolist()))
            if 'date' in temp:
                temp['date'] = temp['date'].astype('datetime64[ns]')

            if display_figure:
                plt.figure()
                x = []
                y = []
                for ii in range(yx[:, 0].__len__()):
                    y.append(yx[ii, 0])
                    y.append(yx[ii, 1])
                    x.append(yx[ii, 2])
                    x.append(yx[ii, 2])
                plt.step(x, y, 'bx')
                plt.step(x_step, y_step, 'ro')
                if 'name' in profile_prop.keys():
                    plt.title(profile_prop.name.unique()[0] + ' - ' + variable)

        discretized_profile = discretized_profile.append(temp)

    return discretized_profile


def set_profile_orientation(profile, v_ref, hi=None, comment=False):
    """

    :param profile:
    :param v_ref:
    :param hi:
    :param comment:
    :return:
    """

    logger = logging.getLogger(__name__)

    for variable in profile.variable.unique():
        data = profile[profile.variable == variable]
        # look for ice thickness:
        if hi is None:
            if not np.isnan(profile.ice_thickness.astype(float)).all():
                hi = profile.ice_thickness.astype(float).dropna().unique()
            elif not np.isnan(profile.length.astype(float)).all():
                hi = profile.length.astype(float).dropna().unique()
            else:
                logger.error(
                    "%s ice core length and ice thickness missing" % profile.name.unique())
                return pd.DataFrame()
        if comment is True:
            print(profile.name.unique()[0], variable, hi)
        if data.v_ref.unique().__len__() > 1:
            logger.error("vertical reference for profile are not consistent")
            return pd.DataFrame()
        elif not data.v_ref.unique()[0] == v_ref:
            data['y_low'] = hi - data['y_low']
            data['y_mid'] = hi - data['y_mid']
            data['y_sup'] = hi - data['y_sup']
            data['v_ref'] = v_ref
        profile = profile.delete_profile({'name': profile.name.unique()[0], 'variable': variable})
        profile = profile.append(data)
    return profile


def set_vertical_reference(profile, h_ref=0, new_v_ref=None):
    """

    :param profile:
    :param h_ref:
    :param new_v_ref: default, same as profile origin
    :return:
    """
    logger = logging.getLogger(__name__)
    if new_v_ref is None:
        if profile.v_ref.unique().__len__() > 1:
            logger.error("vertical reference for profile are not consistent")
            return pd.DataFrame()
        else:
            new_v_ref = profile.v_ref.unique()[0]

    # look for ice thickness:
    if not np.isnan(profile.ice_thickness.astype(float)).all():
        hi = profile.ice_thickness.astype(float).dropna().unique()
    elif not np.isnan(profile.length.astype(float)).all():
        hi = profile.length.astype(float).dropna().unique()
    else:
        logger.warning("ice core length and ice thickness not available for the profile")
        return pd.DataFrame()

    if not new_v_ref == profile.v_ref.unique()[0]:
        profile['y_low'] = hi - profile['y_low']
        profile['y_mid'] = hi - profile['y_mid']
        profile['y_sup'] = hi - profile['y_sup']

    if not h_ref == 0:
        profile['y_low'] = profile['y_low'] - h_ref
        profile['y_mid'] = profile['y_mid'] - h_ref
        profile['y_sup'] = profile['y_sup'] - h_ref

    return profile


def select_profile(ics_stack, variable_dict):
    """

    :param ics_stack:
    :param variable_dict:
    :return:
    """
    str_select = '('
    ii_var = []
    ii = 0
    for ii_key in variable_dict.keys():
        if ii_key in ics_stack.columns.values:
            ii_var.append(variable_dict[ii_key])
            str_select = str_select + 'ics_stack.' + ii_key + '==ii_var[' + str('%d' % ii) + ']) & ('
            ii += 1
    str_select = str_select[:-4]
    return ics_stack.loc[eval(str_select)]


def delete_profile(ics_stack, variable_dict):
    """
    :param ics_stack:
    :param variable_dict:
    :return:
    """
    str_select = '('
    ii_var = []
    ii = 0
    for ii_key in variable_dict.keys():
        if ii_key in ics_stack.columns.values:
            ii_var.append(variable_dict[ii_key])
            str_select = str_select + 'ics_stack.' + ii_key + '!=ii_var[' + str('%d' % ii) + ']) | ('
            ii += 1
    str_select = str_select[:-4]
    return ics_stack.loc[eval(str_select)]


# s_nan is deprecated function
def s_nan(yx, ii_yx, fill_gap=True):
    """
    :param yx:
    :param ii_yx:
    :param fill_gap:
    :return:
    """
    if np.isnan(yx[ii_yx, 2]) and fill_gap:
        ii_yx_l = ii_yx - 1
        while ii_yx_l > 0 and np.isnan(yx[ii_yx_l, 2]):
            ii_yx_l -= 1
        if ii_yx_l > 0:
            s_l = yx[ii_yx_l, 2]
        else:
            s_l = np.nan

        ii_yx_s = ii_yx
        while ii_yx_s < yx.shape[0] - 1 and np.isnan(yx[ii_yx_s, 2]):
            ii_yx_s += 1
        s_s = yx[ii_yx_s, 2]

        s = (s_s + s_l) / 2
    else:
        s = yx[ii_yx, 2]
    return s


def is_continuous_profile(profile):
    if ('y_low' in profile and profile.y_low.isnull().all() and
                profile.y_low.__len__() > 0):
        return 1
    elif 'y_low' not in profile:
        return 1

    else:
        return 0