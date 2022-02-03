#!/usr/bin/python3
# -*- coding: utf-8 -*-

# # ## Default values:
# # v_ref = 'top'
# # verbose = False
#
# # DEBUG:
#
# ic_path = '/home/megavolts/git/pysic/test/ice core/BRW_CS-20210519/BRW_CS-20210519-85_SALO18.xlsx'
#
#

# #
# #
# #
# # def import_ic_list(ic_list, variables=variables, v_ref=v_ref, verbose=verbose, drop_empty=drop_empty):
# #     """
# #     :param ic_list:
# #             array, array contains absolute filepath for the cores
# #     :param variables:
# #     :param v_ref:
# #         top, or bottom
# #     """
# #     logger = logging.getLogger(__name__)
# #
# #     ic_dict = {}
# #     inexisting_ic_list = []
# #     for ic_path in ic_list:
# #         if verbose:
# #             print('Importing data from %s' % ic_path)
# #         if not os.path.exists(ic_path):
# #             logger.warning("%s does not exists in core directory" % ic_path.split('/')[-1])
# #             inexisting_ic_list.append(ic_path.split('/')[-1].split('.')[0])
# #         else:
# #             ic_data = import_ic_path(ic_path, variables=variables, v_ref=v_ref, drop_empty=drop_empty)
# #             if not ic_data.variables():
# #                 inexisting_ic_list.append(ic_path.split('/')[-1].split('.')[0])
# #                 logger.warning("%s have no properties profile" % (ic_data.name))
# #             else:
# #                 ic_dict[ic_data.name] = ic_data
# #
# #     logging.info("Import ice core lists completed")
# #     if inexisting_ic_list.__len__() > 0:
# #         logger.info("%s core does not exits. Removing from collection" % ', '.join(inexisting_ic_list))
# #
# #     for ic in inexisting_ic_list:
# #         for ic2 in ic_dict.keys():
# #             if ic in ic_dict[ic2].collection:
# #                 ic_dict[ic2].del_from_collection(ic)
# #                 logger.info("remove %s from %s collection" % (ic, ic2))
# #     return ic_dict
# #
# #
# # def import_ic_sourcefile(f_path, variables=None, ic_dir=None, v_ref='top', drop_empty=False):
# #     """
# #     :param filepath:
# #             string, absolute path to the file containing either the absolute path of the cores (1 path by line) or the
# #             core names (1 core by line). In this last case if core_dir is None core_dir is the directory contianing the
# #             file.
# #     :param variables:
# #
# #     :param v_ref:
# #         top, or bottom
# #     """
# #     logger = logging.getLogger(__name__)
# #     logger.info('Import ice core from source file: %s' % f_path)
# #
# #     if ic_dir is not None:
# #         with open(f_path) as f:
# #             ics = sorted([os.path.join(ic_dir, line.strip()) for line in f if not line.strip().startswith('#')])
# #     else:
# #         with open(f_path) as f:
# #             ics = sorted([line.strip() for line in f if not line.strip().startswith('#')])
# #
# #     print(ics)
# #
# #     return import_ic_list(ics, variables=variables, v_ref=v_ref, drop_empty=drop_empty)
# #
# #
# # # read profile
# #
# # def read_profile(ws_property, variables=None, version=__CoreVersion__, v_ref='top'):
# #     """
# #     :param ws_property:
# #         openpyxl.worksheet
# #     :param variables:
# #     :param version:
# #     :param v_ref:
# #         top, or bottom
# #     """
# #     logger = logging.getLogger(__name__)
# #
# #     if version == 1:
# #         row_data_start = 6
# #         row_header = 4
# #     elif version == 1.1:
# #         row_data_start = 8
# #         row_header = 5
# #         if ws_property['C4'].value:
# #             v_ref = ws_property['C4'].value
# #     else:
# #         logger.error("ice core spreadsheet version not defined")
# #
# #     sheet_2_data = {'S_ice': [row_data_start, 'ABC', 'DEFG', 'J'],
# #                     'T_ice': [row_data_start, 'A', 'B', 'C'],
# #                     'Vf_oil': [row_data_start, 'ABC', 'DEFG', 'H']}
# #     # TODO: add other sheets for seawater, sediment, CHla, Phae, stratigraphy
# #     #                'stratigraphy': [row_data_start, 'AB', 'C', 'D'],
# #     #                'seawater': [row_data_start, 'A', 'DEFGF', 'G']}
# #
# #     # define section
# #     headers_depth = ['y_low', 'y_mid', 'y_sup']
# #
# #     if not ws_property.title in sheet_2_data:  # if the sheet does not exist, return an empty profile
# #         profile = pysic.core.profile.Profile()
# #     else:
# #         name = ws_property['C1'].value
# #         # Continuous profile
# #         if sheet_2_data[ws_property.title][1].__len__() == 1:
# #             y_mid = np.array([ws_property[sheet_2_data[ws_property.title][1] + str(row)].value
# #                               for row in range(sheet_2_data[ws_property.title][0], ws_property.max_row + 1)]).astype(float)
# #             y_low = np.nan * np.ones(y_mid.__len__())
# #             y_sup = np.nan * np.ones(y_mid.__len__())
# #
# #         # Step profile
# #         elif sheet_2_data[ws_property.title][1].__len__() >= 2:
# #             y_low = np.array([ws_property[sheet_2_data[ws_property.title][1][0] + str(row)].value
# #                               for row in range(sheet_2_data[ws_property.title][0], ws_property.max_row+1)]).astype(float)
# #             y_sup = np.array([ws_property[sheet_2_data[ws_property.title][1][1] + str(row)].value
# #                               for row in range(sheet_2_data[ws_property.title][0], ws_property.max_row+1)]).astype(float)
# #             y_mid = np.array([ws_property[sheet_2_data[ws_property.title][1][2] + str(row)].value
# #                               for row in range(sheet_2_data[ws_property.title][0], ws_property.max_row+1)]).astype(float)
# #
# #             # check if y_mid are not nan:
# #             if np.isnan(y_mid).any():
# #                 y_mid = (y_low + y_sup) / 2
# #                 logger.info('(%s - %s ) not all y_mid exits, calculating y_mid = (y_low+y_sup)/2'
# #                             % (name, ws_property.title))
# #             elif np.any(np.abs(((y_low + y_sup)/ 2) - y_mid > 1e-12)):
# #                     logger.error('(%s - %s ) y_mid are not mid point between y_low and y_sup. \\'
# #                                  'Replacing with y_mid = (y_low+y_sup)/2'
# #                                  % (name, ws_property.title))
# #             else:
# #                 logger.info('(%s - %s ) y_low, y_mid and y_sup read with success'
# #                             % (name, ws_property.title))
# #
# #
# #         # read data
# #         min_col = sheet_2_data[ws_property.title][2][0]
# #         min_col = openpyxl.utils.column_index_from_string(min_col)
# #
# #         max_col = ws_property.max_column
# #
# #         min_row = sheet_2_data[ws_property.title][0]
# #         max_row = min_row + y_mid.__len__()-1
# #
# #         # _data = [[cell.value if isinstance(cell.value, (float, int)) else np.nan for cell in row]
# #         #          for row in ws_property.iter_cols(min_col, max_col, min_row, max_row)]
# #         _data = [[cell.value if isinstance(cell.value, (float, int, str)) else np.nan for cell in row]
# #                  for row in ws_property.iter_cols(min_col, max_col, min_row, max_row)]
# #
# #         data = np.array([y_low, y_mid, y_sup])
# #         data = np.vstack([data, np.array(_data)])
# #
# #         variable_headers = [ws_property.cell(row_header, col).value for col in range(min_col, max_col+1)]
# #
# #         # # fill missing section with np.nan
# #         # if fill_missing:
# #         #     idx = np.where(np.abs(y_low[1:-1]-y_sup[0:-2]) > TOL)[0]
# #         #     for ii_idx in idx:
# #         #         empty = [y_sup[ii_idx], (y_sup[ii_idx]+y_low[ii_idx+1])/2, y_low[ii_idx+1]]
# #         #         empty += [np.nan] * (variable_headers.__len__()+1)
# #         #     data = np.vstack([data, empty])
# #
# #         # assemble profile dataframe
# #         profile = pd.DataFrame(data.transpose(), columns=headers_depth + variable_headers)
# #
# #         # drop empty variable header
# #         if None in profile.columns:
# #             profile = profile.drop(labels=[None], axis=1)
# #
# #         # # convert string to float:
# #         # float_header = [h for h in profile.columns if h not in ['comments']]
# #         # profile[float_header] = profile[float_header].apply(pd.to_numeric, errors='coerce')
# #
# #         # drop property with all nan value
# #         profile = profile.dropna(axis=1, how='all')
# #
# #         # remove empty line if all element of depth are nan:
# #         subset = [col for col in ['y_low', 'y_mid', 'y_sup'] if col in profile.columns]
# #         profile = profile.dropna(axis=0, subset=subset, how='all')
# #
# #         # singularize comments
# #         if 'comments' in profile.columns:
# #             profile.rename(columns={'comments': "comment"}, inplace=True)
# #         # add comment column if it does not exist
# #         if 'comment' not in profile.columns:
# #             profile['comment'] = None
# #         else:
# #             profile['comment'] = profile['comment'].astype(str).replace({'nan': None})
# #
# #         # get all property variable (e.g. salinity, temperature, ...)
# #         property = [var for var in profile.columns if var not in ['comment'] + headers_depth]
# #
# #         # remove subvariable (e.g. conductivity temperature measurement for conductivity
# #         property = [prop for prop in property if prop not in inverse_dict(subvariable_dict)]
# #
# #         # set variable to string of property
# #         profile['variable'] = [', '.join(property)]*len(profile.index)
# #
# #         # ice core length
# #         try:
# #             length = float(ws_property['C2'].value)
# #         except:
# #             logger.info('(%s) no ice core length' % name)
# #             length = np.nan
# #         else:
# #             if length == 'n/a':
# #                 profile['comment'] = 'ice core length not available'
# #                 logger.info('(%s) ice core length is not available (n/a)' % name)
# #                 length = np.nan
# #             elif not isinstance(length, (int, float)):
# #                 logger.info('%s ice core length is not a number' % name)
# #                 profile['comment'] = 'ice core length not available'
# #                 length = np.nan
# #         profile['length'] = [length]*len(profile.index)
# #
# #         # set vertical references
# #         profile['v_ref'] = [v_ref]*len(profile.index)
# #
# #         # set ice core name for profile
# #         profile['name'] = [name]*len(profile.index)
# #
# #         # set columns type
# #         col_string = ['comment', 'v_ref', 'name', 'profile', 'variable']
# #         col_date = ['date']
# #         col_float = [h for h in profile.columns if h not in col_string and h not in col_date]
# #         profile[col_float] = profile[col_float].apply(pd.to_numeric, errors='coerce')
# #         c_string = [h for h in col_string if h in profile.columns]
# #         profile[c_string] = profile[c_string].astype(str).replace({'nan': None})
# #
# #         profile = pysic.core.profile.Profile(profile)
# #         # remove variable not in variables
# #         if variables is not None:
# #             for property in profile.properties():
# #                 if property not in variables:
# #                     profile.delete_property(property)
# #
# #     return profile
# #
# #
#
# # create list or source
# def list_folder(dirpath, fileext='.xlsx', level=0):
#     """
#     list all files with specific extension in a directory
#
#     :param dirpath: str; directory to scan for ice core
#     :param fileext: str, default .xlsx; file extension for ice core data
#     :param level: numeric, default 0; level of recursitivy in directory search
#     :return ic_list: list
#         list of ice core path
#     """
#
#     if not fileext.startswith('.'):
#         fileext = '.' + fileext
#
#     _ics = []
#
#     logger = logging.getLogger(__name__)
#
#     def walklevel(some_dir, level=level):
#         some_dir = some_dir.rstrip(os.path.sep)
#         assert os.path.isdir(some_dir)
#         num_sep = some_dir.count(os.path.sep)
#         for root, dirs, files in os.walk(some_dir):
#             yield root, dirs, files
#             num_sep_this = root.count(os.path.sep)
#             if num_sep + level <= num_sep_this:
#                 del dirs[:]
#
#     for dirName, subdirList, fileList in walklevel(dirpath, level=level):
#         _ics.extend([dirName + '/' + f for f in fileList if f.endswith(fileext)])
#
#     ics_set = set(_ics)
#     logger.info("Found %i ice core datafile in %s" % (ics_set.__len__(), dirpath))
#
#     return ics_set
#
#
# def list_corename(dirpath, fileext='.xlsx', level=0):
#     """
#     list all files with specific extension in a directory
#
#     :param dirpath: str; directory to scan for ice core
#     :param fileext: str, default .xlsx; file extension for ice core data
#     :param level: numeric, default 0; level of recursitivy in directory search
#     :return ic_list: list
#         list of ice core path
#     """
#     _ics = []
#
#     if not fileext.startswith('.'):
#         fileext = '.' + fileext
#
#     logger = logging.getLogger(__name__)
#
#     ics_set = list_folder(dirpath, fileext, level)
#     ics_name = []
#     for ic in sorted(ics_set):
#         name = ic.split('/')[-1].split(fileext)[0]
#         print(name)
#         ics_name.append(name)
#     return ics_name
# #
# #
# # def list_ic_path(dirpath, fileext):
# #     """
# #     list all files with specific extension in a directory
# #
# #     :param dirpath: str
# #     :param fileext: str
# #     :return ic_list: list
# #         list of ice core path
# #     """
# #     logger = logging.getLogger(__name__)
# #
# #     ics_set = list_folder(dirpath=dirpath, fileext=fileext)
# #     ic_paths_set = set([os.path.join(os.path.realpath(dirpath), f) for f in ics_set])
# #     return ic_paths_set
# #
# #
# # def make_ic_sourcefile(dirpath, fileext, source_filepath=None):
# #     """
# #     list all files with specific extension in a directory
# #
# #     :param dirpath: str
# #     :param fileext: str
# #     :return source_file: str
# #         filepath to the text file containing ice core filepath with absolute path.
# #     """
# #     logger = logging.getLogger(__name__)
# #
# #     ic_paths_set = list_ic_path(dirpath, fileext)
# #
# #     if source_filepath is None:
# #         source_filepath = os.path.join(os.path.realpath(dirpath), 'ic_list.txt')
# #
# #     with open(source_filepath, 'w') as f:
# #         for ic_path in ic_paths_set:
# #             f.write(ic_path + "\n")
# #
# #     return source_filepath
# #
# # #
# # # def read_ic_list(file_path):
# # #     """
# # #
# # #     :param file_path:
# # #     :return:
# # #     """
# # #
# # #     with open(file_path) as f:
# # #         data = [list(map(int, row.split())) for row in f.read().split('\n\n')]
# # #
# # #     return ic_list
# #
# # TODO: cleaner function to (1) remove trailing and heading space in instrument
#

#
#

