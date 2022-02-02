#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from distutils.util import convert_path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

sys.path.append(os.getcwd())

# Load version from pysic/__version__.py
about = {}
ver_path = convert_path('pysic/__version__.py')
with open(ver_path) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, about)

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# OR...
# with open('README.rst') as f:
#     readme = f.read()

# Alread in requirements.txt
requirements = [
    "numpy>=1.10.0",
    "scipy>=0.18.0",
    "pandas>=0.18.1",
    "matplotlib>=2.2.2",
    "openpyxl",
]

packages = ['pysic',
            'pysic.core',
            'pysic.property',
            'pysic.tools']

setup(
    name='PySIC',
    description='A set of tools for analyzing sea-ice core',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=about['__version__'],
    zip_safe=False,
    classifiers=['Development Status :: 0.6 - alpha',
                 'Natural Language :: English',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Physics'],
    packages=packages,
    install_requires=requirements,
    author='Marc Oggier',
    author_email='moggier@alaska.edu',
    download_url='https://github.com/megavolts/pysic',
    url='https://github.com/megavolts/pysic',
    project_urls={
        'Documentation': 'https://github.com/megavolts/pysic/wiki',
        'Source': 'https://github.com/megavolts/pysic',
        'Tracker': 'https://github.com/megavolts/pysic/issues',
    }
)


with open('LICENSE') as f:
    license = f.read()