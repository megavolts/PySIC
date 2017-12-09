# ! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
seaice.core.coreset.py : Core and CoreStack class

"""
import logging
import numpy as np
import pandas as pd

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

__all__ = ["set_profile_orientation"]

module_logger = logging.getLogger(__name__)
