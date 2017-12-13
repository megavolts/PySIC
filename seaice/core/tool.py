# ! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.coreset.py : Core and CoreStack class

"""
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

__name__ = "load"
__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/09/13"
__comment__ = "core.py contained classes to handle ice core data"
__CoreVersion__ = 1.1

__all__ = ["select_profile", "delete_profile"]

module_logger = logging.getLogger(__name__)
TOL = 1e-6


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
        s_l = yx[ii_yx_l, 2]

        ii_yx_s = ii_yx
        while ii_yx_s < yx.shape[0] - 1 and np.isnan(yx[ii_yx_s, 2]):
            ii_yx_s += 1
        s_s = yx[ii_yx_s, 2]

        s = (s_s + s_l) / 2
    else:
        s = yx[ii_yx, 2]
    return s


def indices(dim):
    """
    :param dim:
    :return:
    """
    for d in range(dim[0]):
        if dim.__len__() == 1:
            yield (d,)
        else:
            for n in indices(dim[1:]):
                yield (d,) + n


def plt_step(x, y):
    # step function
    xy = np.array([x[0], y[0]])
    for ii in range(x.__len__()-1):
        xy = np.vstack((xy, [x[ii], y[ii+1]]))
        xy = np.vstack((xy, [x[ii+1], y[ii+1]]))
    return xy
