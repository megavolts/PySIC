# seaice extent spiralling raph
# inspired by global temperature change of Ed Hawkin: https://twitter.com/ed_hawkins/status/729753441459945474
#
#
#

import os
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.cm
data_dir = '/mnt/data_lvm/seaice/cover/NSIDC/DATASETS/NOAA/G02135/south/daily/data/'
file_name = 'SH_seaice_extent_final.csv'

data_path = os.path.join(data_dir, file_name)
data_out = '/home/megavolts/Desktop/AntarcticIce100'
os.makedirs(data_out, exist_ok=True)

data = pd.read_csv(data_path, delimiter=',', skipinitialspace=True)
data = data.drop(data.index[[0]])
data = data[(data != 'Source Data') ].apply(lambda x: pd.to_numeric(x, errors='coerce'))
data['datesource'] = pd.to_datetime(data.Year*10000+data.Month*100+data.Day, format='%Y%m%d')

df = data.set_index('datesource')
df.head()

df2 = df.reindex(pd.date_range(min(df.index), max(df.index), freq='D'))
df2 = df2.interpolate().reset_index()
df2 = df2.rename(columns={'index':'Date'})

def f(df):
    df = df.copy()
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    return df

data = f(df2)
def year_frac2(row):
    y = int(row['Year'])
    m = int(row['Month'])
    d = int(row['Day'])
    if np.isnan([y, m, d]).any():
        return np.nan
    else:
        return dt.datetime(y, m, d).timetuple().tm_yday/dt.datetime(y, 12, 31).timetuple().tm_yday*2*np.pi

data['degree'] = data.apply(year_frac2, axis=1)
data = data.reset_index()
data.head()

cm = plt.get_cmap('jet')
NPOINTS = data.degree.__len__()
color = [cm(ii/(NPOINTS-1)) for ii in range(NPOINTS-1)]

ax = plt.subplot(111, projection='polar')
freq = 100
for ii in range(int(NPOINTS/freq-1)):
    print(dt.datetime(data.Year[ii*freq], data.Month[ii*freq], data.Day[ii*freq]).strftime("%Y %b %d"), ii)
    ax.plot(data.degree[ii*freq:((ii+1)*freq+1)], data.Extent[ii*freq:((ii+1)*freq+1)], color = color[ii*freq])
    ax.set_thetagrids(np.linspace(360/24, 360*23/24, 12))
    ax.set_theta_direction('clockwise')
    ax.set_theta_offset(np.pi/2)
    ax.xaxis.set_ticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.set_rmin(1)
    ax.set_rmax(max(data.Extent)*1.1)
    ax.text(4.5, 14, dt.datetime(2022, 12, 29).strftime("%Y %b %d"), fontsize=15, color='w', bbox={'facecolor':'w', 'alpha':1, 'pad':5, 'edgecolor':'w'})
    ax.text(4.5, 14, dt.datetime(data.Year[ii*freq], data.Month[ii*freq], data.Day[ii*freq]).strftime("%Y %b %d"), fontsize = 15 )
    plt.savefig(os.path.join(data_out, dt.datetime(data.Year[ii*freq], data.Month[ii*freq], data.Day[ii*freq]).strftime("%Y%m%d")+'.png'), dpi=75)