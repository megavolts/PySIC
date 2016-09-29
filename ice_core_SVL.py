#! /usr/bin/python3
# -*- coding: UTF-8 -*-

__author__ = "Marc Oggier"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "marc.oggier@gi.alaska.edu"
__status__ = "development"
__date__ = "2015/04/21"
import os
import pickle

import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm



import sys
sys.path.extend(['/home/megavolts/Desktop/working/scripts/python/sea_ice'])

'''
    T, S profile for SVL

    core: SVL

'''
import seaice.coreV2
import seaice.properties
import seaice.mbs
import seaice.toolbox
import logging
import datetime as dt
# =====================================================================================================================#
# USER VARIABLE INPUT
# =====================================================================================================================#
myhost = os.uname()[1]

if myhost == 'arran': # work computer
    data_path = '/home/megavolts/data/'
    output_data_path = os.path.join('/home/megavolts/Desktop/', dt.datetime.today().strftime('%Y%m'))
elif myhost == 'islay': # laptop
    data_path = '/home/megavolts/Desktop/RSOI_working/data/'
    output_data_path = os.path.join('/home/megavolts/Desktop/', dt.datetime.today().strftime('%Y%m'))
else:
    data_path = '/home/megavolts/UAF/data/'
    output_data_path = '/home/megavolts/Desktop/'


# ice core data
location = 'svl'

# Ice core data
ic_datasrc = data_path + 'seaice/core/SVL/data-SVL.txt'
short_core = [] # no short core
ignore_core = [] # consider all core

# MBS data
mbs_datapath = None
mbs_year_start = None
mbs_year_end = None

# Weather data
weather_datapath = os.path.join(data_path, 'seaice/CICE/2014-0724Svalbard/JINforcing.txt')  # weather data file

# CICE model data (Meibing)
mod_datapath = None

# FREEZ-UP
freezup_hajo = {1997:300, 1998:300}

section_thickness = 0.05
missvalue = float('nan')

# FDD/TDD approach
time_growth_start = 260  # Sept 15 (normal year), August 14 (leap year) is define as the end of the summer season
FDD_interval = np.array([0, 10])
TDD_interval = np.array([-45, -47.5, -50])
Tfreeze = -1.8


# =====================================================================================================================#
# USER VARIABLE BACKUP DIR
# =====================================================================================================================#
# Ice core data
backup_datapkl = os.path.join(output_data_path + '/RSOI/pkl/')
fig_dir = os.path.join(output_data_path + '/RSOI/fig/')
out_dir = os.path.join(output_data_path + '/RSOI/data_output/')

# =====================================================================================================================#
# VARIABLE INITIALISATION
# do not modify below this lines
# =====================================================================================================================#
col_Tair = 13 - 1

# check input/output variable
if not os.path.isdir(fig_dir):  # create output directory if not present
    os.makedirs(fig_dir)
if not os.path.isdir(out_dir):  # create output directory if not present
    os.makedirs(out_dir)
if not os.path.isdir(backup_datapkl):  # create output directory if not present
    os.makedirs(backup_datapkl)

# close all figures
plt.close()
flag_plot_no = 0  # set first figure number to 0

# =====================================================================================================================#
# DATA IMPORTATION
# =====================================================================================================================#

LOG_FILENAME = 'log.log'
LOG_LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

# =====================================================================================================================#
# DATA IMPORTATION
# import and save data if pickle does not exist
# =====================================================================================================================#
# Ice Core Data
f_pkl =os.path.join(backup_datapkl+'ic_svl_data.pkl')
if os.path.isfile(f_pkl):
    with open(f_pkl, 'rb') as f:
        ic_data = pickle.load(f)
else:
    ic_data = seaice.coreV2.importsrc(ic_datasrc, 0.05, float('nan'), log_level='debug')
    with open(f_pkl, 'wb') as f:
        pickle.dump(ic_data, f)
print('Ice core data imported')

# MBS
if mbs_datapath :
    f_pkl =os.path.join(backup_datapkl+'mbs_svl_data.pkl')
    if os.path.isfile(backup_datapkl+''):
        with open(f_pkl, 'rb') as f:
            mbs_data = pickle.load(f)
    else:
        mbs_data = {}
        for ii in range(mbs_year_start, mbs_year_end + 1):
            mbs_name = 'BRW' + str(ii)[2:] + '_MBS.txt'
            if 2012 < ii:
                mbs_name = mbs_name[:-4] + '-all.csv'
            mbs_path = os.path.join(mbs_datapath, mbs_name)
            mbs_data[ii] = np.array(seaice.mbs.read(mbs_path))
        with open(f_pkl, 'wb') as f:
            pickle.dump(mbs_data, f)
    print('MBS data imported')

## Weather data
if os.path.isfile(backup_datapkl+'weather_svl_data.pkl'):
    with open(backup_datapkl+'weather_svl_data.pkl', 'rb') as f:
        data_weather = pickle.load(f)
else:
    data_weather = np.genfromtxt(weather_datapath)
    with open(backup_datapkl+'weather_svl_data.pkl', 'wb') as f:
        pickle.dump(data_weather, f)
print('weather data imported')


## CICE model
if mod_datapath:
    if os.path.isfile(backup_datapkl+'mod_data.pkl'):
        with open(backup_datapkl+'mod_data.pkl', 'rb') as f:
            data_mod = pickle.load(f)
    else:
        data_mod = np.genfromtxt(mod_datapath)
        with open(backup_datapkl+'mod_data.pkl', 'wb') as f:
           pickle.dump(data_mod, f)
    print('model data imported')

# =====================================================================================================================#
# DATA analysis
# import and save data if pickle does not exist
# =====================================================================================================================#
# years when ice core have been extracted
ic_day = {}
ic_year = {}
for ic in sorted(ic_data.keys()):
    ic_day[ic_data[ic].name] = ic_data[ic].date
    ic_year[ic_data[ic].name] = ic_data[ic].date.year
ics_years = sorted(seaice.toolbox.unique(ic_year.values()))
# DEGREE DAY APPROACyaoulH
# compute FDD and TDD for years when ice core have been extracted
# works for year after 1999 (included) as no early freeze-up day are recorded
# use Hajo's observation first, Joe Lewit second and
# TODO: add freeze up day from Alaska Atlas to extend range. Look at Becca's script

DD = {}
if os.path.isfile(backup_datapkl+'DD_svl_data.pkl'):
    with open(backup_datapkl+'DD_svl_data.pkl', 'rb') as f:
        DD = pickle.load(f)
else:
    for iiYear in range(ics_years[0], ics_years[-1] + 1):
        if isinstance(freezup_hajo[iiYear], (int, float)):  # use Hajo's obsevation f
            freezup_day = freezup_hajo[iiYear]
#            elif freezup_hajo[iiYear] == 'JL':
#                freezup_day = freezup_lewit[iiYear]
#            elif freezup_hajo[iiYear] == 'CG':
#                freezup_day = 330
        else:
            logging.info('Freezup day not defined. Removing winter ' + str('%4.0f' % iiYear) + ' from the season')
        freezup_day = datetime.datetime(iiYear-1, 1, 1) + datetime.timedelta(freezup_day)
        end_of_season_day = datetime.datetime(iiYear, 1, 1) + datetime.timedelta(time_growth_start-1)

        T_col = 7

        DD.update(seaice.toolbox.DegreeDayModel(data_weather, T_col, freezup_day, end_of_season_day, Tfreeze=Tfreeze, Tunit='K'))
    with open(backup_datapkl+'DD_svl_data.pkl', 'wb') as f:
        pickle.dump(DD, f)
print('DD computed for the season when ice core have been retrieved')

ic_FDD = []
ic_TDD = []

# extract F/TDD for days when ice core have been extracted
for iiDay in sorted(seaice.toolbox.unique(ic_day.values())):
    ic_FDD.append(DD[iiDay][0])
    ic_TDD.append(DD[iiDay][1])
ic_FDD = seaice.toolbox.unique(ic_FDD)
ic_TDD = seaice.toolbox.unique(ic_TDD)

# create legend and temporal class
n_period = len(FDD_interval)-1+len(TDD_interval)-1
plot_name = []
plot_interval_legend = []
for ii in range(0, len(FDD_interval)-1):
    plot_interval_legend.append(str(FDD_interval[ii]) + ' - ' + str(FDD_interval[ii + 1]) + ' [FDD]')
    plot_name.append('FDD-' + str('%04.0f' % FDD_interval[ii]) + '_' + str('%04.0f' % FDD_interval[ii + 1]))

for ii in range(0, len(TDD_interval)-1):
    plot_interval_legend.append(str(TDD_interval[ii]) + ' - ' + str(TDD_interval[ii + 1]) + ' [TDD]')
    plot_name.append('TDD-' + str('%04.0f' % TDD_interval[ii]) + '_' + str('%04.0f' % TDD_interval[ii + 1]))

print('FDD and TDD interval created')
# date.year not in ic_year_l:
#        ic_year_l.append(ic_data[ic].date.year)
# ic_year_l = sorted(ic_year_l)


# INITIALIZE TABLE
# (
s_matrix = np.nan*np.ones([1, 1, n_period])
t_matrix = np.nan*np.ones([1, 1, n_period])
ls_matrix = np.nan*np.ones([1, 1, n_period])

s_legend_matrix = [[] for ii in range(n_period)]
t_legend_matrix = [[] for ii in range(n_period)]
ls_legend_matrix = [[] for ii in range(n_period)]


# create ST core
ic_interval_d = {}
counter_core_in_interval = np.zeros([n_period, 1])

iiCore = 0
f_core_DD = [0, 0]  # f_core_DD[0] corresponds to FDD, f_core_DD[1] corresponds to TDD
# data importation
# if an ice core have salinity profile, looks at corresponding T profile
while iiCore < len(ic_data):
    core_data = ic_data[sorted(ic_data.keys())[iiCore]]
    print(core_data.name)

    # main core F/T classification
    if DD[core_data.date][1] == 0 or DD[core_data.date][1] is 'nan':
        f_core_DD[0] += 1
        core_interval = np.where(FDD_interval <= DD[core_data.date][0])[0][-1]
    else:
        f_core_DD[1] += 1
        core_interval = len(FDD_interval)-2+np.where(TDD_interval <= DD[core_data.date][1])[0][0]

    ic_interval_d[core_data.name] = [core_interval, ]

    # import S profile of the ice core
    if core_data.s is not None:
        s_data = np.atleast_2d(core_data.s).transpose()
        s_legend = [core_data.name]
        s_length = [core_data.lengths]

        # import T profile
        # T.1 import T profile from ice core belonging to the same set
        f_t_obs = 0
        for ii_core_name in core_data.corenames:
            if ii_core_name not in ignore_core and ic_data[ii_core_name].t is not None:
                f_t_obs = 1
                try:
                    t_data
                except NameError:
                    t_data = np.atleast_2d(ic_data[ii_core_name].t).transpose()
                    t_legend = [ic_data[ii_core_name].name]
                    t_length = [ic_data[ii_core_name].lengtht]

                else:
                    t_data = seaice.toolbox.vmerge2D(t_data, np.atleast_2d(ic_data[ii_core_name].t).transpose())
                    t_legend.append(ic_data[ii_core_name].name)
                    t_length.append(ic_data[ii_core_name].lengtht)

        # T.2 import T profile from MBS if MBS data exists (after 2005)
        f_t_mbs = 0
        if 2005 < core_data.date.year:
            if core_data.date.timetuple().tm_yday < core_data.date.timetuple().tm_yday:
                t_mbs_index = seaice.toolbox.index_from_day(mbs_data[core_data.date.year + 1], core_data.date)
            else:
                t_mbs_index = seaice.toolbox.index_from_day(mbs_data[core_data.date.year], core_data.date)

            if 0 < len(t_mbs_index):
                f_t_mbs = 2
                t_mbs_avg = seaice.mbs.ice_profile(mbs_data[core_data.date.year], t_mbs_index, core_data.lengths)
                try:
                    t_data
                except NameError:
                    t_data = np.atleast_2d(t_mbs_avg).transpose()
                    t_legend = ['MBS-' + core_data.date.strftime("%Y%m%d")]
                    t_length = [core_data.lengths]
                else:
                    t_data = seaice.toolbox.vmerge2D(t_data, np.atleast_2d(t_mbs_avg).transpose())
                    t_legend.append('MBS-' + core_data.date.strftime("%Y%m%d"))
                    t_length.append(core_data.lengths)

        f_t_lin = 0

        if f_t_obs+f_t_mbs+f_t_lin > 0:
            t_avg = np.atleast_2d(np.nanmean(t_data, axis=1)).transpose()
            if not np.isnan(t_avg).all():
                t_data = seaice.toolbox.vmerge2D(t_data, t_avg)
                if t_data.shape[1] < 3:
                    t_legend.append(t_legend[-1])
                else:
                    t_legend.append('T avg (MBS, obs)')
                t_length.append(np.nanmean(t_length))

                # concatenate S and Tavg in matrix
                position = [0, int(counter_core_in_interval[core_interval]), core_interval]
                s_matrix = seaice.toolbox.merge3D(s_data, s_matrix, position)
                t_matrix = seaice.toolbox.merge3D(t_avg, t_matrix, position)
                ls_matrix = seaice.toolbox.merge3D(s_length, ls_matrix, position)

                s_legend_matrix[core_interval].append(s_legend)
                t_legend_matrix[core_interval].append(t_legend[-1])
                ls_legend_matrix[core_interval].append(s_legend)

                counter_core_in_interval[core_interval] += 1
            del t_data, t_legend, t_length, t_avg
        else:
            print('no temperature profile, core %s rejected' % core_data.name)
        del s_data, s_legend, s_length

    else:
        print('no salinity record, %s is ignored' % core_data.name)
    iiCore += 1
print('ice core processing completed')




s_matrix_stat = seaice.toolbox.make_stat(s_matrix, axis=1)
t_matrix_stat = seaice.toolbox.make_stat(t_matrix, axis=1)
ls_matrix_stat = seaice.toolbox.make_stat(ls_matrix, axis =1)
print('stat processing completed')

#----------------------------------------------------------------------------------------------------------------------#
# EXPORTATION
#----------------------------------------------------------------------------------------------------------------------#

variableEx = [s_matrix_stat, t_matrix_stat, ls_matrix_stat]
nameEx = ['S', 'T']
for iiVariable in np.arange(0, len(variableEx)-1):
    f = open(os.path.join(out_dir, 'ic_'+location+'-'+nameEx[iiVariable]+'.txt'), 'w')
    # header
    f.write("degree day model approach\n")
    f.write("Depth [cm]")

    iiInterval = 0
    while iiInterval < len(FDD_interval)-1:
        f.write("\t" + str('%.0f' % FDD_interval[iiInterval]) + ' to ' + str('%.0f' % FDD_interval[iiInterval+1]) + "[FDD]\tStdDev\tmin\tmax\tNcore")
        iiInterval += 1
    while iiInterval < n_period:
        f.write("\t" + str('%.0f' % TDD_interval[iiInterval-len(FDD_interval)+1]) + ' to ' + str('%.0f' % TDD_interval[iiInterval-len(FDD_interval)+2]) + "[TDD]\tStdDev\tmin\tmax\tNcore")
        iiInterval += 1

    # data
    for iiDepth in range(0,variableEx[iiVariable].shape[0]):
        depth = section_thickness / 2 * 100 + iiDepth * section_thickness * 100
        f.write('\n'+str('%.1f' % depth))
        for iiInterval in range(0,n_period):
            f.write('\t'+str('%.1f' % variableEx[iiVariable][iiDepth, 0, iiInterval]) + '\t' + str('%.1f' % variableEx[iiVariable][iiDepth, 1, iiInterval]) + '\t' + str('%.1f' % variableEx[iiVariable][iiDepth, 2, iiInterval]) + '\t' + str('%.1f' % variableEx[iiVariable][iiDepth, 3, iiInterval]) + '\t' + str('%.0f' % variableEx[iiVariable][iiDepth, 4, iiInterval]))
    f.close()

## ice core length
f = open(os.path.join(out_dir, 'ic_'+location+'-l.txt'), 'w')
# header
f.write('ice core depth\n')
f.write('\n')
iiInterval = 0
while iiInterval < len(FDD_interval)-1:
    f.write("\t" + str('%.0f' % FDD_interval[iiInterval]) + ' to ' + str('%.0f' % FDD_interval[iiInterval+1]) + "[FDD]\tStdDev\tmin\tmax\tNcore")
    iiInterval += 1
while iiInterval < n_period:
    f.write("\t" + str('%.0f' % TDD_interval[iiInterval-len(FDD_interval)+1]) + ' to ' + str('%.0f' % TDD_interval[iiInterval-len(FDD_interval)+2]) + "[TDD]\tStdDev\tmin\tmax\tNcore")
    iiInterval += 1

# ice core legnth
iiVariable=2
for iiInterval in range(0,n_period):
    f.write('\t'+str('%.2f' % variableEx[iiVariable][0, 0, iiInterval]) + '\t' + str('%.2f' % variableEx[iiVariable][0, 1, iiInterval]) + '\t' + str('%.2f' % variableEx[iiVariable][0, 2, iiInterval]) + '\t' + str('%.2f' % variableEx[iiVariable][0, 3, iiInterval]) + '\t' + str('%.0f' % variableEx[iiVariable][0, 4, iiInterval]))
f.close()

print('Exportation completed')