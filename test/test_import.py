import pysic

# try:
#     import pysic as si
# except ImportError:
#     import sys
#     if '/home/megavolts/git/pysic' in sys.path:
#         raise
#     sys.path.append('/')
#     import pysic as si
#
# # Core list directory
# ic_collection = '/home/megavolts/git/pysic/test/ice core'
# ic_event = '/home/megavolts/git/pysic/test/ice core/BRW_CS-20210519/'
ic_core = '/home/megavolts/git/pysic/test/ice core/BRW_CS-20210519/BRW_CS-20210519-85_SALO18.xlsx'
# ic_ext = '.xlsx'

# List all ice core data
# ic_dir = ic_event
# ics_list = si.core.list_folder(ic_dir, ic_ext, 2)
# si.core.list_corename(ic_dir, ic_ext, 2)
#
# # Import 1 core
ic_path = ic_core
#
ic = pysic.io.load.ic_from_path(ic_path)


import math

#pysic
import pickle
with open('/home/megavolts/Desktop/test.pkl', 'wb') as f:
    pickle.dump(ic, f)


# ic_dir = '/mnt/data/UAF-data/raw/MOSAiC-UTQ/ice core/'
# ics_list = pysic.core.list_folder(ic_dir, ic_ext, 2)
# ics_import = []
# for ic in ics_list:
#     if 'SALO18' in ic and 'EL' not in ic and 'bkp-ic' not in ic:
#         ics_import.append(ic)
#         print(ic)
#
#         # if not any(map(ic.__contains__, ['OPT', 'TEX', 'sackhole', 'DNA.xlsx'])):
#         #     if not any(map(ic.__contains__, ['MIS', 'AAA_BB', 'deprecated', 'SIMB', 'NARL'])):
#         #         # if any(map(ic.__contains__, ['SALO18.xlsx', 'RHO.xlsx', 'T.xlsx'])):
#
# ics_import = sorted(ics_import)
# PAR = []
# for ic_path in ics_import:
#     print(ic_path)
#     temp = pysic.core.import_ic_path(ic_path)
#     hi = np.nanmean(temp.ice_thickness)
#     hs = np.nanmean(temp.snow_depth)
#     hs_std = np.nanstd(temp.snow_depth)
#     try:
#         date = temp.date.date()
#     except AttributeError:
#         date = temp.date
#     else:
#         pass
#     par_2pi = temp.par_above
#     par_4pi = temp.par_below
#     PAR.append([date.toordinal(), par_2pi, par_4pi, hi, hs, hs_std ])
#
# import numpy as np
# PAR = np.array(PAR).astype(float)
# PAR.tofile('PAR.csv')
# np.savetxt("PAR.csv", PAR, delimiter=",")
#
# import matplotlib.pyplot as plt
#
# fig, ax1 = plt.subplots(1, 1)
# ax1.plot(PAR[:, 0], PAR[:, 1], label='PAR above')
# ax1.plot(PAR[:, 0], PAR[:, 2], label='PAR below')
# ax2 = ax1.twinx()
# ax2.plot(PAR[:, 0], PAR[:, 3]*100, color='k', label='hi (cm)')
# ax2.errorbar(PAR[:, 0], -PAR[:, 4]*100, PAR[:, 5]*100, color='k', ls=':', label='hs (cm)')
# ax2.set_ylim([120, -20])
# ax1.set_ylabel('PAR ($umols^{-1}m^{-2}$)')
# ax2.set_xlabel('snow/ice thickness (cm)')
# plt.legend()
# plt.show()

#
# ics_list = seaice.core.list_folder(ic_dir, ic_ext, 2)
# ics_import = []
#
# for ic in ics_list:
#     if 'raw_' not in ic:
#         if not any(map(ic.__contains__, ['OPT', 'TEX', 'sackhole', 'DNA.xlsx'])):
#             if not any(map(ic.__contains__, ['MIS', 'AAA_BB', 'deprecated', 'SIMB', 'NARL'])):
# #                if any(map(ic.__contains__, ['SALO18.xlsx', 'RHO.xlsx', 'T.xlsx'])):
#                 print(ic)
#                 ics_import.append(ic)
# ics_import = sorted(ics_import)
#
# # ic_path = '/mnt/data/UAF-data/raw/MOSAiC-UTQ/ice core/BRW_CS-20210527/BRW_CS-20210527-111_TM.xlsx'
# # ic_data = seaice.core.import_ic_path(ic_path)
#
# ics_dict = seaice.core.import_ic_list(ics_import)
# # TODO: ic_import show imported variables
# # Stack data
# ic_stack = seaice.core.corestack.stack_cores(ics_dict)
# ic_stack.date = ic_stack.date.apply(lambda x: x.date())
#
# ic_stack_t = ic_stack.set_vertical_reference('top')
# ic_stack_b = ic_stack.set_vertical_reference('bottom')
#
# dates = ic_stack.date.sort_values().unique()
#
# for date in dates:
#     print(date)
#     date_n = date.strftime('%Y%m%d')
#     core_t = [name for name in ic_stack.name.unique()
#               if date.strftime('%Y%m%d') in name and 'temperature' in ic_stack[ic_stack.name == name].variables()]
#     core_s = [name for name in ic_stack.name.unique()
#               if date.strftime('%Y%m%d') in name and 'salinity' in ic_stack[ic_stack.name == name].variables()]
#     core_d = [name for name in ic_stack.name.unique()
#               if date.strftime('%Y%m%d') in name and 'density' in ic_stack[ic_stack.name == name].variables()]
#
# # Plot
# inbottom = True
# NARL_plot = False
# BERG_plot = False
# RHO_cal = True
# variables = ['salinity', 'temperature', 'density', 'brine volume fraction']
# variables = ['salinity', 'temperature', 'density']
#
# #dates_plot = [d for d in dates if d >= dt.date(2021, 4, 21)]
# dates_plot = [dt.date(2021, 4, 21), dt.date(2021, 4, 26), dt.date(2021, 5, 12), dt.date(2021, 5, 27), dt.date(2021, 6, 2), dt.date(2021, 6, 9), dt.date(2021, 6, 11)]
# #dates_plot = [dt.date(2021, 5, 10), dt.date(2021, 5, 21), dt.date(2021, 5, 28)] + [d for d in dates if d >= dt.date(2021, 6, 1)]
# #dates_plot = [dt.date(2021, 4, 23), dt.date(2021, 5, 3), dt.date(2021, 5, 12), dt.date(2021, 5, 21), dt.date(2021, 5, 24)] + [d for d in dates if d >= dt.date(2021, 6, 1)]
# #dates_plot = [d for d in dates if d > dt.date(2021, 4, 29) and d < dt.date(2021, 5, 15)]
# # dates_plot = [dt.date(2021, 4, 21), dt.date(2021, 5, 5), dt.date(2021, 5, 12), dt.date(2021, 5, 21), dt.date(2021, 5 , 24), dt.date(2021, 5, 25), dt.date(2021, 5, 27)]
# #dates_plot = dates
# #dates_plot = [dt.date(2021, 5, 12), dt.date(2021, 5, 21), dt.date(2021, 5 , 24), dt.date(2021, 5, 25), dt.date(2021, 5, 27)]
#
# sites_plot = ['CS']
# dates_plot_dict = {'CS': dates_plot,
#                    'EL': dates}
# sites_title = {'EL': 'Elson Lagoon', 'CS': 'Chukchi Sea'}
#
# variables_dict = {var: ii for ii, var in enumerate(variables)}
# # for date in dates:
#
# if not NARL_plot:
#     ic_stack = ic_stack[~ic_stack.name.str.contains('NARL')]
#
# if not BERG_plot:
#     ic_stack = ic_stack[~ic_stack.name.str.contains('BERG')]
#
# for site in sites_plot:
#     # figures
#     ax_v = 1 + inbottom
#     ax_h = len(variables)
#     if inbottom:
#         ax_v = 2
#
#     flag_S_RHO = False
#     flag_S_TM = False
#     flag_S_NARL = False
#     flag_S_SF = False
#
#     fig = plt.figure(figsize=[11,  8.5])
#     fig_row = ax_v
#     fig_col = ax_h
#     ax_h_spec = [1]
#     if inbottom:
#         ax_v_spec = [1, 0.55]
#     else:
#         ax_v_spec = [1]
#     gs = gridspec.GridSpec(fig_row, fig_col, width_ratios=[1]*ax_h, height_ratios=ax_v_spec)
#
#     ax = [[fig.add_subplot(gs[0, 0])]]
#     ax[0].extend([fig.add_subplot(gs[0, ii], sharey=ax[0][0]) for ii in range(1, ax_h)])
#     if ax_v > 1:
#         ax.append([fig.add_subplot(gs[1, 0])])
#         ax[1].extend([fig.add_subplot(gs[1, ii], sharey=ax[1][0]) for ii in range(1, ax_h)])
#     ax = np.atleast_2d(ax)
#
#     date_legend = []
#     if all(map(dates_plot_dict.__contains__, ['EL', 'CS'])):
#         dates_fig = dates_plot_dict[site]
#     color_date = {st: cm.viridis(st_ii / len(dates_fig)) for st_ii, st in enumerate(dates_fig)}
#
#     for date in dates_fig:
#         color = color_date[date]
#
#         ic_stack_data = ic_stack[ic_stack.date == date]
#         ic_stack_data = ic_stack_data[ic_stack_data.name.str.contains(site)]
#         if not ic_stack_data.empty:
#             print(ic_stack_data.name.unique())
#
#         for variable in variables:
#             ax_n = variables_dict[variable]
#             # 0-reference at the ice surface, v_ref='top'
#             variable_dict = {'variable': variable, 'v_ref': 'top'}
#
#             # plot profile
#             core_list = ic_stack_data.name.unique()
#             core_list = [ic for ic in core_list if site in ic]
#             if len(core_list) > 0:
#                 if date not in date_legend:
#                     date_legend.append(date)
#             else:
#                 break
#             for core in core_list:
#                 core_data = ic_stack_data.loc[ic_stack_data.name == core]
#                 core_data = seaice.core.corestack.CoreStack(core_data)
#                 core_data_t = core_data.set_vertical_reference('top')
#                 core_data_t = core_data_t.sort_values('y_sup')
#                 core_data_t = core_data_t[core_data_t.matter == 'ice']
#
#                 if variable == 'salinity':
#                     core_data_t = core_data_t[core_data_t.salinity_value.notnull()]
#                     core_data_t = core_data_t[core_data_t.y_low.notnull()]
#                     core_data_t = core_data_t[core_data_t.y_low >= 0]
#
#                 if 'NARL' in core:
#                     param_dict = {'color': color, 'linewidth': 1, 'linestyle': '--'}
#                     flag_S_NARL = True
#                 elif variable == 'salinity' and any(map(core.__contains__, ['RHO'])):
#                     param_dict = {'color': color, 'linewidth': 1, 'linestyle': ':'}
#                     flag_S_RHO = True
#                     if RHO_cal:
#                         core_data_t.salinity_value = -0.02 * core_data_t.salinity_value**2 + 1.14 * core_data_t.salinity_value
#                         print('RHO CAL')
#                 elif variable == 'salinity' and any(map(core.__contains__, ['TM'])):
#                     param_dict = {'color': color, 'linewidth': 1, 'linestyle': '-.'}
#                     flag_S_TM = True
#                 elif variable == 'salinity' and any(map(core.__contains__, ['SF'])):
#                     param_dict = {'color': color, 'linewidth': 1, 'linestyle': (0, (1, 3))}
#                     flag_S_SF = True
#                 else:
#                     param_dict = {'color': color, 'linewidth': 1, 'linestyle': '-'}
#
#                 if date == dates_fig[-1]:
#                     param_dict.update({'color': color, 'linewidth': 2})
#
#                 if not (variable == 'salinity' and any(map(core.__contains__, (['TM', 'RHO'])))):
#                     ax[0, ax_n] = seaice.visualization.plot.plot_profile_variable(core_data_t, variable_dict, ax=ax[0, ax_n],
#                                                                              param_dict=param_dict)
#
#             ax[0, ax_n].xaxis.set_label_position('top')
#             ax[0, ax_n].xaxis.set_ticks_position('top')
#             ax[0, ax_n].spines['bottom'].set_visible(False)
#             ax[0, ax_n].spines['right'].set_visible(False)
#             ax[0, ax_n].set_xlabel(variable)
#             # # x_lim
#             # ax[0, ax_n].set_xlim([V_min[variable]['growth'], V_max[variable][season]])
#             # x_ticks = np.arange(V_min[variable][season], V_max[variable][season] + V_tick[variable][season] / 2,
#             #                     V_tick[variable][season])
#             # ax[0, ax_n].xaxis.set_ticks(x_ticks)
#             ax[0, 1].tick_params(top=True, bottom=False, left=True, right=False,
#                                  labeltop=True, labelbottom=False, labelleft=False, labelright=False)
#             ax[0, 1].yaxis.label.set_visible(False)
#
#             if inbottom:
#                 # 0-reference at the ice bottom, v_ref='bottom'
#                 variable_dict = {'variable': variable, 'v_ref': 'bottom'}
#                 for core in core_list:
#                     core_data = ic_stack_data.loc[ic_stack_data.name == core]
#                     core_data_b = core_data.set_vertical_reference('bottom')
#                     core_data_b = core_data_b.sort_values('y_sup')
#                     core_data_b = core_data_b[core_data_b.matter == 'ice']
#
#                     if variable == 'salinity':
#                         core_data_b = core_data_b[core_data_b.salinity_value.notnull()]
#                         core_data_b = core_data_b[core_data_b.y_low.notnull()]
#                         core_data_b = core_data_b[core_data_b.y_low >= 0]
#
#                     if 'NARL' in core:
#                         param_dict = {'color': color, 'linewidth': 1, 'linestyle': '--'}
#                         flag_S_NARL = True
#                     elif variable == 'salinity' and any(map(core.__contains__, ['RHO'])):
#                         param_dict = {'color': color, 'linewidth': 1, 'linestyle': ':'}
#                         flag_S_RHO = True
#                         if RHO_cal:
#                             core_data_b.salinity_value = -0.02 * core_data_b.salinity_value ** 2 + 1.14 * core_data_b.salinity_value
#                     elif variable == 'salinity' and any(map(core.__contains__, ['TM'])):
#                         param_dict = {'color': color, 'linewidth': 1, 'linestyle': '-.'}
#                         flag_S_TM = True
#                     elif variable == 'salinity' and any(map(core.__contains__, ['SF'])):
#                         param_dict = {'color': color, 'linewidth': 1, 'linestyle': (0, (1, 3))}
#                         flag_S_SF = True
#                     else:
#                         param_dict = {'color': color, 'linewidth': 1, 'linestyle': '-'}
#
#                     if date == dates_fig[-1]:
#                         param_dict.update({'color': color, 'linewidth': 2})
#                     if not (variable == 'salinity' and any(map(core.__contains__, (['TM', 'RHO', 'SF', 'NARL'])))):
#                         ax[1, ax_n] = seaice.visualization.plot.plot_profile_variable(core_data_b, variable_dict, ax=ax[1, ax_n],
#                                                                              param_dict=param_dict)
#                 ax[1, ax_n].spines['top'].set_visible(False)
#                 ax[1, ax_n].spines['right'].set_visible(False)
#                 ax[1, ax_n].xaxis.set_label_position('bottom')
#                 ax[1, ax_n].xaxis.set_ticks_position('bottom')
#                 ax[1, ax_n].spines['bottom'].set_visible(True)
#
#                 ax[1, 1].yaxis.label.set_visible(False)
#                 ax[1, 1].xaxis.label.set_visible(True)
#                 ax[1, 0].xaxis.label.set_visible(True)
#                 ax[1, 0].tick_params(top=False, bottom=True, left=True, right=False,
#                                      labelleft=True, labeltop=False, labelbottom=True)
#                 ax[1, 1].tick_params(top=False, bottom=True, left=True, right=False,
#                                      labelleft=False, labeltop=False, labelbottom=True)
#
#     # legend
#     from matplotlib import lines as mlines
#
#     legends = [d.strftime('%Y-%m-%d') for d in date_legend]
#     handles = [mlines.Line2D([], [], color=color_date[d], linewidth=2) for d in date_legend[:-1]]
#     handles += [mlines.Line2D([], [], color=color_date[date_legend[-1]], linewidth=4)]
#     #
#     # if site == 'CS':
#     #     legends += ['MBS']
#     #     handles += [mlines.Line2D([], [], color='k', linewidth=2, linestyle='-')]
#     #     if flag_S_RHO:
#     #         legends += ['S$_{RHO}$']
#     #         handles += [mlines.Line2D([], [], color='k', linewidth=2, linestyle=':')]
#     #     if flag_S_TM:
#     #         legends += ['S$_{TM}$']
#     #         handles += [mlines.Line2D([], [], color='k', linewidth=2, linestyle='-.')]
#     #     if flag_S_SF:
#     #         legends += ['S$_{frozen}$']
#     #         handles += [mlines.Line2D([], [], color='k', linewidth=2, linestyle=(0, (1, 3)))]
#     #     if flag_S_NARL:
#     #         legends += ['S$_{NARL}$']
#     #         handles += [mlines.Line2D([], [], color='k', linewidth=2, linestyle='--')]
#     # else:
#     #     legends += ['EL']
#     #     handles += [mlines.Line2D([], [], color='k', linewidth=2, linestyle='-')]
#
#     # y_lim
#     ax[0, 0].set_ylim([max(ax[0, 0].get_ylim()), 0])
#     ax[0, 0].set_xlim([0, 15])
#     ax[1, 0].set_xlim([0, 15])
#
#     if inbottom:
#         ax[1, 0].set_ylim([0, max(ax[0, 0].get_ylim())*0.55])
#
#     # title
#     fig.suptitle(sites_title[site] + ' (preliminary)')
#     fig.legend(handles, legends, ncol=7, frameon=False,  bbox_to_anchor=(0.5, 0), loc='lower center')
#
#     gs.set_height_ratios([1, 0.55])
#
#     # # saving fig
#     fig_name = dates_fig[0].strftime('%Y%m%d') + '_' + dates_fig[-1].strftime('%Y%m%d-') + site +'-priority2.pdf'
#     fig_path = os.path.join(fig_dir, daily_ST_subdir, fig_name)
#     plt.savefig(fig_path)
#
#     # if DISPLAY:
#     #     plt.show()
#     # else:
#     #     plt.close()
#
#     plt.show()