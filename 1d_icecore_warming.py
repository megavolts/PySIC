# MOSAiC
# Where shall we measure temperature first

#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
2019-03-08
Paper: property variability in sea ice

# module:
"""
import configparser
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

import pandas as pd
import datetime as dt
import sys

import seaice


# =====================================================================================================================#
# USER VARIABLE INPUT
# =====================================================================================================================#
location = 'BRW'
ice_thickness_section = 0.05  # thickness of ice section / vertical bin in m
#MONTH = ['01-January', '02-March', '03-June']
MONTH = ['02-March']
TEMPERATURE = [-20]
h_levels = [0.05, 0.1, 0.2]
mesh = 'fine'
core_diameter = 0.1  # m

# =====================================================================================================================#
# LOAD CONFIG
# =====================================================================================================================#
myhost = os.uname()[1]
config_path = os.path.join(os.getcwd(), 'data', location + '.ini')
if myhost == 'islay':
    fig_dir = '/home/megavolts/Desktop/'
elif myhost == 'arran':
    fig_dir = '/home/megavolts/Desktop/'
elif myhost == 'adak':
    fig_dir = '/home/megavolts/Desktop/'

config = configparser.ConfigParser()
config.read(config_path)

# =====================================================================================================================#
# LOAD DATA
# =====================================================================================================================#
# ice core from observation
path = os.path.join(config['DEFAULT']['data_dir'], config['OUTPUT']['output_dir'], config['OUTPUT']['obs core'])
with open(path, 'rb') as f:
    ic_obs_stack = seaice.core.corestack.CoreStack(pickle.load(f))

if mesh == 'fine':
    dx = 0.001  # m
    dy = 0.001  # m
else:
    dx = 0.01  # m
    dy = 0.01  # m

all_data = {}

for month in MONTH:

    if month == '01-January':
        core = 'BRW_CS-20130116B'
    elif month == '02-March':
        core = 'BRW_CS-20130328'
    elif month == '03-June':
        core = 'BRW_CS-20130609'
    else:
        core = 'BRW_CS-20130116B'

    ic = ic_obs_stack[ic_obs_stack.name == core]

    # plot profile (using seaice toolbox)
    fig = seaice.core.plot.plot_all_profile_variable(ic, display_figure=False)
    plt.show()

    core_length = ic.length.unique()[0]

    # coarse grid base on profile section
    nx, ny = int(core_diameter/2/dx), int(core_length/dy)
    x = np.linspace(0, core_diameter/2, nx)
    y = np.linspace(0, core_length, ny)
    xv, yv = np.meshgrid(x, y)


    # stretch T profile to match S profile
    ic_d = seaice.core.profile.discretize_profile(ic, y, display_figure=False)
    S = ic_d.salinity
    x_mid = x[:-1] + np.diff(x)/2
    y_mid = ic_d.y_mid
    T = np.interp(y_mid,
                  ic.dropna(subset=['temperature'])['y_mid'] * core_length/ ic.dropna(subset=['temperature'])['y_mid'].max(),
                  ic.dropna(subset=['temperature'])['temperature'])
    xv, yv = np.meshgrid(x_mid, y_mid)

    # ice core before collection
    T_field = np.array([T] * (len(x)-1)).transpose()
    S_field = np.array([S] * (len(x)-1)).transpose()

    T_field_ref = T_field.copy()

    for T_atm in TEMPERATURE:
        T_field = T_field_ref.copy()
        # initial condition of warming
        t0_field = np.nan*np.ones_like(T_field)
        t0_field[:, -1] = T_atm
        t0_field[0, :] = T_atm
        t0_field[-1, :] = T_atm

        # initial conditon of ice core after extraction
        T0_field = T_field.copy()
        T0_field[~np.isnan(t0_field)] = t0_field[~np.isnan(t0_field)]
        D0_field = seaice.property.si.thermal_diffusivity(S_field.copy(), T_field)
        T_field = T0_field
        dx2, dy2 = dx*dx, dy*dy
        dt = dx2 * dy2 / (2 * np.nanmax(D0_field) * (dx2 + dy2))

        plt.figure()
        plt.imshow(T0_field)
        plt.show()

        def do_timestep_only(u0, u, k, dt):
            u[1:-1, 1:-1] = u0[1:-1, 1:-1] + k[1:-1, 1:-1] * dt * (
                (u0[2:, 1:-1] - 2 * u0[1:-1, 1:-1] + u0[:-2, 1:-1]) / dx2
                + (u0[1:-1, 2:] - 2 * u0[1:-1, 1:-1] + u0[1:-1, :-2]) / dy2)

            u0 = u.copy()
            return u0, u


        # Number of timesteps
        nsteps = 4000
        tmax = 60*10  # in seconds

        if mesh == 'fine':
            t_fig = 10
        else:
            t_fig = 60
        mt = 1
        t = 0

        Tmin = int(min(ic_d.temperature.min(), T_atm))-1
        Tmax = int(max(ic_d.temperature.max(), T_atm))+1

        xv, yv = np.meshgrid(np.concatenate([-x_mid[::-1], x_mid]), y_mid)

        Tt_field = []
        Vbft_field = []
        t_time = []
        levels = h_levels + [y_mid.max()/2] + sorted(y_mid.max() -h_levels)
        color_levels = plt.cm.jet(np.linspace(0, 1, len(levels)))
        x0 = len(x_mid)
        for m in range(nsteps):
            if t >= mt*t_fig:
                T_plot = np.concatenate([np.fliplr(T0_field.copy()), T0_field.copy()], axis=1)

                # brine volume fraction along the center
                Vbf_c = seaice.property.si.brine_volume_fraction(S_field[:, 0], T0_field[:, 0])

                t_time.append(t)
                if mt == 1:
                    Tt_field = np.array([T_plot])
                    Vbft_field = np.array([Vbf_c])
                else:
                    Tt_field = np.concatenate([Tt_field, [T_plot]])
                    Vbft_field = np.concatenate([Vbft_field, [Vbf_c]])

                # error on brine volume fraction as the core cool down
                dr_Vbft = np.abs(Vbft_field - Vbft_field[0])*100 / Vbft_field[0]
                d_Vbft = np.abs(Vbft_field - Vbft_field[0])*100


                # Relative Error
                fig, (ax, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 3]}, figsize=(6, 5))

                cax = ax.pcolor(xv, yv, np.ma.masked_invalid(T_plot), cmap=plt.get_cmap('Blues'), vmin=Tmin, vmax=Tmax)
                ax.patch.set(hatch='x', edgecolor='black')
                import matplotlib as mpl
                cbar = fig.colorbar(cax, ax=ax, ticks=[Tmin, Tmax], norm=mpl.colors.Normalize(vmin=Tmin-0.01, vmax=Tmax+0.01))
                cbar.set_clim(vmin=Tmin-0.01, vmax=Tmax+0.01)

                cbar.set_label('temperature ($^\circ$C)')
                ax.set_aspect('equal')
                ax.set_title('elapsed time\n{:.0f} s'.format(t))
                ax.set_ylabel('ice thickness (m)')
                ax.set_ylim([max(ax.get_ylim()), min(ax.get_ylim())])
                ax.set_xticks([0])

                # Add error in brine volume fraction whith temperature change on second vertical axis
                ax3 = ax2.twinx()

                ii_level = 0
                for level in levels:
                    ax2.plot(t_time, Tt_field[:, int(level/dy), x0], label='h_i = 0.05 m', color=color_levels[ii_level])
                    ax3.plot(t_time, dr_Vbft[:, int(level/dy)], label='h_i = 0.05 m', color=color_levels[ii_level], linestyle=':')
                    ax.plot([-x_mid[-1], x_mid[-1]], [y_mid.values[int(level/dy)]]*2, color=color_levels[ii_level])
                    ii_level += 1
                ax2.set_xlabel('time (s)')
                ax2.set_xlim([0, tmax])
                ax2.set_ylim([Tmin, Tmax])
                ax2.set_xticks(np.arange(0, tmax+1, 120))
                ax2.set_title("%s\nT$_{surface}$ = %s $^\circ$C" %(month, str("%.0f" % T_atm)))
                ax3.set_ylabel('relative porosity error %')
                ax3.set_ylim(0, 20)

                plt.subplots_adjust(left=0.05, wspace=0.6, right=.9, bottom=0.21)

                ic_dir = os.path.join('/home/megavolts/Desktop/ic_warming/', month + '-T_' + str("%2.0f" % T_atm))
                if not os.path.exists(ic_dir):
                    os.makedirs(ic_dir)

                # create legend
                labels = ['temperature',
                          'porosity'] + ['h_i = ' + str("%.2f" % levels[ii]) +' m' for ii in range(0, len(levels))]
                handles = [mlines.Line2D([], [], color='k'),
                           mlines.Line2D([], [], color='k', linestyle=':')] +\
                          [mlines.Line2D([], [], color=color_levels[ii]) for ii in range(0, len(levels))]
                plt.legend(labels=labels, handles=handles, ncol=4, frameon=False, loc='center bottom',
                           bbox_to_anchor=(0.24, -0.61, 1, 0.5))

                fig.savefig(os.path.join(ic_dir, str("rel-%04.0f" % t) +'.png'))

                # Absolute error
                fig2, (ax, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 3]}, figsize=(6, 5))

                cax = ax.pcolor(xv, yv, np.ma.masked_invalid(T_plot), cmap=plt.get_cmap('Blues'), vmin=Tmin, vmax=Tmax)
                ax.patch.set(hatch='x', edgecolor='black')
                import matplotlib as mpl

                cbar = fig2.colorbar(cax, ax=ax, ticks=[Tmin, Tmax],
                                    norm=mpl.colors.Normalize(vmin=Tmin - 0.01, vmax=Tmax + 0.01))
                cbar.set_clim(vmin=Tmin - 0.01, vmax=Tmax + 0.01)

                cbar.set_label('temperature ($^\circ$C)')
                ax.set_aspect('equal')
                ax.set_title('elapsed time\n{:.0f} s'.format(t))
                ax.set_ylabel('ice thickness (m)')
                ax.set_ylim([max(ax.get_ylim()), min(ax.get_ylim())])
                ax.set_xticks([0])

                # Add error in brine volume fraction whith temperature change on second vertical axis
                ax3 = ax2.twinx()

                ii_level = 0
                for level in levels:
                    ax2.plot(t_time, Tt_field[:, int(level / dy), x0], label='h_i = 0.05 m',
                             color=color_levels[ii_level])
                    ax3.plot(t_time, d_Vbft[:, int(level / dy)], label='h_i = 0.05 m', color=color_levels[ii_level],
                             linestyle=':')
                    ax.plot([-x_mid[-1], x_mid[-1]], [y_mid.values[int(level / dy)]] * 2, color=color_levels[ii_level])
                    ii_level += 1
                ax2.set_xlabel('time (s)')
                ax2.set_xlim([0, tmax])
                ax2.set_ylim([Tmin, Tmax])
                ax2.set_xticks(np.arange(0, tmax + 1, 120))
                ax2.set_title("%s\nT$_{surface}$ = %s $^\circ$C" % (month, str("%.0f" % T_atm)))
                ax3.set_ylabel('absolute porosity  error %')
                ax3.set_ylim(0, 10)

                plt.subplots_adjust(left=0.05, wspace=0.6, right=.9, bottom=0.21)

                ic_dir = os.path.join('/home/megavolts/Desktop/ic_warming/', month + '-T_' + str("%2.0f" % T_atm))
                if not os.path.exists(ic_dir):
                    os.makedirs(ic_dir)

                # create legend
                labels = ['temperature',
                          'porosity'] + ['h_i = ' + str("%.2f" % levels[ii]) + ' m' for ii in range(0, len(levels))]
                handles = [mlines.Line2D([], [], color='k'),
                           mlines.Line2D([], [], color='k', linestyle=':')] + \
                          [mlines.Line2D([], [], color=color_levels[ii]) for ii in range(0, len(levels))]
                plt.legend(labels=labels, handles=handles, ncol=4, frameon=False, loc='center bottom',
                           bbox_to_anchor=(0.24, -0.61, 1, 0.5))

                fig2.savefig(os.path.join(ic_dir, str("abs-%04.0f" % t) + '.png'))

                mt += 1

                if mesh == 'coarse':
                    plt.show()

            T0_field, T_field = do_timestep_only(u0=T0_field, u=T_field, k=D0_field, dt=dt)

            D0_field = seaice.property.si.thermal_diffusivity(S_field.copy(), T0_field)
            dt = dx2 * dy2 / (2 * np.nanmax(D0_field) * (dx2 + dy2))

            # fixed T at all interface:
            T0_field[~np.isnan(t0_field)] = t0_field[~np.isnan(t0_field)]

            # neumann condition on the core center
            T0_field[:, 0] = T0_field[:, 1]

            if t > tmax:
                ic_dir = os.path.join('/home/megavolts/Desktop/ic_warming/', )
                fig.savefig(os.path.join(ic_dir, month + '-T_' + str("%2.0f" % T_atm) + '-' + str("rel-%04.0f" % t) + '.png'))
                fig2.savefig(os.path.join(ic_dir, month + '-T_' + str("%2.0f" % T_atm) + '-' + str("abs-%04.0f" % t) + '.png'))
                break
            t += dt
        print('processed %s T= %s' % (month, str("%2.0f" % T_atm)))
        all_data[T_atm] = [Tt_field, t_time]
with open('/home/megavolts/Desktop/ic_warming/data.pickle', 'wb') as f:
    pickle.dump(all_data, f)
