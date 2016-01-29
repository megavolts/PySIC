#! /usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import pickle
import matplotlib.pyplot as plt
import seaice.coreV2_1
import seaice.properties
import seaice.mbs
import seaice.icdtools

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2015/04/21"

# =====================================================================================================================#
# USER VARIABLE INPUT
# =====================================================================================================================#
data_dir = './data_sample/'
ics_subdir = 'ice_cores'

# Ice core data
ics_dir = os.path.join(data_dir, ics_subdir)
ics_list = seaice.coreV2_1.getfilepath(ics_dir, '.xlsx')

ics_data = {}
for ic_path in ics_list:
    ic = seaice.coreV2_1.importcore(ic_path)
    ics_data[ic.name] = ic


f_pkl = os.path.join(ics_dir, 'ics_data.pkl')
with open(f_pkl, 'wb') as f:
    pickle.dump(ics_data, f)

ic.calc_prop('vb')


fig, (ax1, ax2) = ic.plot_state_variable({'color': 'r'})
plt.show()