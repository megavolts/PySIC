#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers

import seaice.climatology
from seaice.io.icxl import *
from seaice.core.core import *
from seaice.core.corestack import *
import seaice.core.plot
import seaice.property
import seaice.property.brine
import seaice.property.si
logger = logging.getLogger(__name__)


TOL = 1e-6

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

