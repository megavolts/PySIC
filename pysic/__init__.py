#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    pysic is a module to handle sea ice core data
"""

__author__ = "Marc Oggier"
__license__ = "GPL"

__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2021/02/01"

__credits__ = ["Hajo Eicken", "Andy Mahoney", "Josh Jones"]


import pysic.core
import pysic.io
import pysic.io.load
import pysic.io.update
import pysic.io.clean
import pysic.tools
import pysic.tools.plot
from .__version__ import __version__
from pysic.core.event import Event
from pysic.core.core import Core
from pysic.core.profile import Profile

TOL = 1e-12

#import pysic.core.corestack
# import pysic.core.corestack
# import pysic.core
# import pysic.core.Core
#import pysic.core.plot
#import pysic.core.Profile
#from pysic.core import Profile
#import pysic.property
#import pysic.visualization.plot

#import pysic.property.brine
#import pysic.property.ice
#import pysic.property.si
#import pysic.property.sw
#import pysic.property.nacl_ice

# TODO: add test function
# TODO: add function Core.check() to check the integrity of the ice core and profiles


#pysic_fp = os.path.getfile('pysic/__init__.py')
#print(pysic_fp)
# from inspect import getfile
# from os.path import dirname
# pysic_fp = dirname(getfile(pysic))
