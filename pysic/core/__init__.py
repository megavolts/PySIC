#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
pysic.io.icxl.py : function to import import ice core data from xlsx spreadsheet
"""

__name__ = "core"
__author__ = "Marc Oggier"
__license__ = "GPL"

__maintainer__ = "Marc Oggier"
__contact__ = "Marc Oggier"
__email__ = "moggier@alaska.edu"
__status__ = "dev"
__date__ = "2017/09/13"
__comment__ = "loadxl.py contained function to import ice core data from xlsx spreadsheet"
__CoreVersion__ = 1.1

import datetime
import logging
import os

import dateutil
import numpy as np
import openpyxl
import pandas as pd

import pysic
import pysic.core.corestack as cs

__all__ = ["import_ic_path", "import_ic_list", "import_ic_sourcefile", "list_ic", "list_ic_path", "make_ic_sourcefile"]

TOL =1e-6
subvariable_dict = {'conductivity': ['conductivity measurement temperature']}

variable_2_sheet = {'temperature': 'T_ice',
                    'salinity': 'S_ice',
                    'conductivity': 'S_ice',
                    'specific conductance': 'S_ice',
                    'd18O': 'S_ice',
                    'dD': 'S_ice',
                    'Vf_oil': 'Vf_oil', 'oil volume fraction': 'Vf_oil',  # MOSIDEO project
                    'Wf_oil': 'Wf_oil', 'oil weight fraction': 'Vf_oil',  # MOSIDEO project
                    'oil content': 'oil_content',  # CMI project
                    'oil mass': 'Vf_oil', 'm_oil': 'Vf_oil'
                    # 'seawater': 'seawater',
                    # 'sediment': 'sediment',
                    # 'Chla': 'algal_pigment',
                    # 'chlorophyl a': 'algal_pigment',
                    # 'Phae': 'algal_pigment'
                    }

## Default values:
variables = None
v_ref = 'top'
verbose = False
drop_empty = False


def import_ic_path_MOSAiC(ic_path, variables = variables, drop_empty=drop_empty):
    """
    :param wb:
    :param variables:
    :param v_ref:
    :param drop_empty:
    :return:
    """

    logger = logging.getLogger(__name__)

    wb = openpyxl.load_workbook(filename=ic_path, keep_vba=False)  # load the xlsx spreadsheet
    ws_name = wb.sheetnames

    ws_summary = wb['metadata-coring']
    ws_metadata_core = wb['metadata-core']

    name = ws_metadata_core['C1'].value
    if ws_summary['C1'].value:
        version = ws_summary['C1'].value
    else:
        logger.error("(%s) ice core spreadsheet version not unavailable" % name)
        wb.close()

    logger.info("importing data for %s" % name)

    # DateTime
    if isinstance(ws_metadata_core['C2'].value, datetime.datetime):
        if isinstance(ws_metadata_core['C3'].value, datetime.time):
            date = datetime.datetime.combine(ws_metadata_core['C2'].value, ws_metadata_core['C3'].value)
            if ws_metadata_core['D2'].value is not None and dateutil.tz.gettz(ws_metadata_core['D2'].value):
                tz = dateutil.tz.gettz(ws_metadata_core['D2'].value)
                date = date.replace(tzinfo=tz)
            else:
                logger.info("\t(%s) timezone unavailable." % name)
        else:
            date = ws_metadata_core['C2'].value
            if ws_metadata_core['D2'].value is not None and dateutil.tz.gettz(ws_metadata_core['D2'].value):
                tz = dateutil.tz.gettz(ws_metadata_core['D2'].value)
                date = date.replace(tzinfo=tz)
            else:
                logger.info("\t(%s) timezone unavailable." % name)
    else:
        logger.warning("\t(%s) date unavailable" % name)
        date = None

    # project
    origin = ws_summary['C3'].value

    # start coordinate
    lat_origin = ws_summary['B8'].value
    lon_origin = ws_summary['B9'].value
    # start latitude:
    if isinstance(ws_summary['C8'].value, (float, int)):
        lat_start_deg = ws_summary['C8'].value
        if isinstance(ws_summary['D8'].value, (float, int)) and np.isnan(ws_summary['D8'].value):
            lat_start_min = ws_summary['D8'].value
            if isinstance(ws_summary['E8'].value, (float, int)) and np.isnan(ws_summary['E8'].value):
                lat_start_sec = ws_summary['E8'].value
            else:
                lat_start_sec = 0
        else:
            lat_start_min = 0
            lat_start_sec = 0
        lat_start_deg = lat_start_deg + lat_start_min/60 + lat_start_sec/3600
    else:
        lat_start_deg = np.nan

    # start longitude
    if isinstance(ws_summary['C9'].value, (float, int)):
        lon_start_deg = ws_summary['C9'].value
        if isinstance(ws_summary['D9'].value, (float, int)) and np.isnan(ws_summary['D9'].value):
            lon_start_min = ws_summary['D9'].value
            if isinstance(ws_summary['E9'].value, (float, int)) and np.isnan(ws_summary['E9'].value):
                lon_start_sec = ws_summary['E9'].value
            else:
                lon_start_sec = 0
        else:
            lon_start_min = 0
            lon_start_sec = 0
        lon_start_deg = lon_start_deg + lon_start_min/60 + lon_start_sec/3600
    else:
        lon_start_deg = np.nan

    # end latitude:
    if isinstance(ws_summary['F8'].value, (float, int)):
        lat_end_deg = ws_summary['F8'].value
        if isinstance(ws_summary['G8'].value, (float, int)) and np.isnan(ws_summary['G8'].value):
            lat_end_min = ws_summary['G8'].value
            if isinstance(ws_summary['H8'].value, (float, int)) and np.isnan(ws_summary['H8'].value):
                lat_end_sec = ws_summary['H8'].value
            else:
                lat_end_sec = 0
        else:
            lat_end_min = 0
            lat_end_sec = 0
        lat_end_deg = lat_end_deg + lat_end_min/60 + lat_end_sec/3600
    else:
        lat_end_deg = np.nan

    # end longitude
    if isinstance(ws_summary['F9'].value, (float, int)):
        lon_end_deg = ws_summary['F9'].value
        if isinstance(ws_summary['G9'].value, (float, int)) and np.isnan(ws_summary['G9'].value):
            lon_end_min = ws_summary['G9'].value
            if isinstance(ws_summary['H9'].value, (float, int)) and np.isnan(ws_summary['H9'].value):
                lon_end_sec = ws_summary['H9'].value
            else:
                lon_end_sec = 0
        else:
            lon_end_min = 0
            lon_end_sec = 0
        lon_end_deg = lon_end_deg + lon_end_min/60 + lon_end_sec/3600
    else:
        lon_end_deg = np.nan

    # Station time
    # TODO
    comments = []

    # Snow Depth
    n_snow = 1
    snow_depth = []
    while ws_summary.cell(row=16, column=3+n_snow).value is not None:
        snow_depth.append(ws_summary.cell(row=16, column=3+n_snow).value)
        n_snow += 1
    snow_depth = np.array(snow_depth)

    if isinstance(snow_depth[-1], str):
        comments.append(snow_depth[-1])
        snow_depth = pd.to_numeric(snow_depth[:-1], errors='coerce')
    else:
        snow_depth = pd.to_numeric(snow_depth, errors='coerce')

    # Average
    if isinstance(ws_summary['C16'].value, (float, int)):
        snow_depth_avg = ws_summary['C16'].value
    elif np.isnan(snow_depth).any():
        snow_depth_avg = np.nanmean(snow_depth)
    else:
        snow_depth_avg = np.nan

    # Ice Thickness
    try:
        h_i = ws_metadata_core['C7'].value
    except:
        logger.info('(%s) no ice thickness information ' % name)
        h_i = np.nan
    else:
        if h_i == 'n/a':
            comments.append('ice thickness not available')
            logger.info('(%s) ice thickness is not available (n/a)' % name)
            h_i = np.nan
        elif not isinstance(h_i, (int, float)):
            logger.info('%s ice thickness is not a number' % name)
            comments.append('ice thickness not available')
            h_i = np.nan

    # Ice Draft
    try:
        h_d = ws_metadata_core['C8'].value
    except:
        logger.info('(%s) no ice draft information ' % name)
        h_d = np.nan
    else:
        if h_d == 'n/a':
            comments.append('ice draft not available')
            logger.info('(%s) ice draft is not available (n/a)' % name)
            h_d = np.nan
        elif not isinstance(h_d, (int, float)):
            logger.info('%s ice draft is not a number' % name)
            comments.append('ice draft not available')
            h_d = np.nan

    # Ice freeboard
    if not (np.isnan(h_d) and np.isnan(h_i)):
        h_f = h_i - h_d
    else:
        try:
            h_f = ws_metadata_core['C9'].value
        except:
            logger.info('(%s) no ice draft information ' % name)
            h_f = np.nan
        else:
            if h_f == 'n/a':
                comments.append('ice draft not available')
                logger.info('(%s) ice draft is not available (n/a)' % name)
                h_f = np.nan
            elif not isinstance(h_f, (int, float)):
                logger.info('%s ice draft is not a number' % name)
                comments.append('ice draft not available')
                h_f = np.nan

    # Core Length l_c (measured in with ruler)
    try:
        l_c = ws_metadata_core['C10'].value
    except:
        logger.info('(%s) no ice core length' % name)
        l_c = np.nan
    else:
        if l_c == 'n/a':
            comments.append('ice core length not available')
            logger.info('(%s) ice core length is not available (n/a)' % name)
            l_c = np.nan
        elif not isinstance(l_c, (int, float)):
            logger.info('%s ice core length is not a number' % name)
            comments.append('ice core length not available')
            l_c = np.nan

    core = pysic.Core(name, date, origin, lat_start_deg, lon_start_deg, h_i, h_f, snow_depth_avg)
    core.length = l_c

    # Temperature
    if ws_summary['C25'].value:
        core.t_air = ws_summary['C25'].value
    if ws_summary['C26'].value:
        core.t_snow_surface = ws_summary['C26'].value
    if ws_summary['C27'].value:
        core.t_ice_surface = ws_summary['C27'].value
    if ws_summary['C28'].value:
        core.t_water = ws_summary['C28'].value

    # Sampling event
    if ws_summary['C30'].value:
        core.station = ws_summary['C30'].value

    # Sampling protocol
    if ws_summary.cell(3, 33).value:
        core.protocol = ws_summary.cell(3, 33).value
    else:
        core.protocol = 'N/A'

    # Sampling instrument
    instrument_d = {}
    m_row = 13
    while ws_metadata_core.cell(m_row, 1).value is not None:
        instrument_d[ws_metadata_core.cell(m_row, 1).value] = ws_metadata_core.cell(m_row, 3).value
        m_row += 1
    core.instrument = instrument_d

    # Core collection
    m_col = 3
    while ws_summary.cell(31, m_col).value:
        core.add_to_collection(ws_summary.cell(31, m_col).value)
        m_col += 1

    # comment
    if ws_summary['A42'].value is not None:
        comments.append(ws_summary['A42'].value)
    core.add_comment('; '.join(comments))

    # weather
    # TODO: read weather information

    # import all variables
    if variables is None:
        # TODO: special import for TEX, snow
        sheets = [sheet for sheet in ws_name if (sheet not in ['TEX', 'snow', 'summary', 'abreviation', 'locations', 'lists',
                                                               'Vf_oil_calculation', 'metadata-core', 'metadata-coring']) and
                     (sheet.lower().find('fig') == -1)]
        for sheet in sheets:
            ws_variable = wb[sheet]
            profile = read_profile_MOSAiC(ws_variable, variables=None, version=version, v_ref=v_ref)
            profile['name'] = name
            if drop_empty:
                profile.drop_empty_property()

            if not profile.empty:
                core.add_profile(profile)
                logger.info('(%s) data imported with success: %s' % (core.name, ", ".join(profile.get_property())))
            else:
                logger.info('(%s) no data to import from %s ' % (core.name, sheet))
    else:
        if not isinstance(variables, list):
            if variables.lower().find('state variable')+1:
                variables = ['temperature', 'salinity']
            else:
                variables = [variables]

        _imported_variables = []
        for variable in variables:
            if variable_2_sheet[variable] in ws_name and variable not in _imported_variables:
                sheet = variable_2_sheet[variable]
                ws_variable = wb[sheet]

                variable2import = [var for var in variables if var in inverse_dict(variable_2_sheet)[sheet]]

                profile = read_profile(ws_variable, variables=variable2import, version=version, v_ref=v_ref)

                if profile.get_name() is not core.name:
                    logger.error('\t(%s) core name %s and profile name %s does not match'
                                 % (ic_path, core.name, profile.name()))
                elif not profile.empty:
                    core.add_profile(profile)
                    logger.info(' (%s) data imported with success: %s' % (profile.get_name(), profile.get_property()))
                else:
                    _temp = [variable for variable in profile.get_variable() if profile[variable].isnull().all()]
                    if _temp.__len__() > 1:
                        logger.info(' (%s) no data to import: %s ' % (profile.get_name(), ", ".join(_temp)))
                    else:
                        logger.info('(%s) no variable to import' % name)

                _imported_variables +=variable2import
    return core


def import_ic_path(ic_path, variables=variables, v_ref=v_ref, drop_empty=drop_empty):
    """
    :param ic_path:
        string, path to the xlsx ice core spreadsheet
    :param variables:
        list of string, variables to import. If not defined, all variable will be imported.
    :param v_ref:
        'top' or 'bottom', vertical reference. top for ice/snow or ice/air surface, bottom for ice/water interface
    :return:
    """
    logger = logging.getLogger(__name__)

    if not os.path.exists(ic_path):
        logger.error("%s does not exists in core directory" % ic_path.split('/')[-1])

    wb = openpyxl.load_workbook(filename=ic_path, keep_vba=False)  # load the xlsx spreadsheet
    ws_name = wb.sheetnames

    try:
        print(ic_path)
        ws_summary = wb['summary']  # load the data from the summary sheet
    except KeyError:
        core = import_ic_path_MOSAiC(ic_path, variables = variables, drop_empty=drop_empty)
        return core
    else:
        print('Not in MOSAiC format')
        name = ws_summary['C21'].value
        pass

    if isinstance(ws_summary['C3'].value, (float, int)):
        version = ws_summary['C3'].value
    else:
        logger.error("(%s) ice core spreadsheet version not unavailable" % name)
    wb.close()

    # convert ice core spreadsheet to last version
    if version < __CoreVersion__:
        wb.close()
        update_spreadsheet(ic_path, v_ref=v_ref)
        logger.info("Updating ice core spreadsheet %s to last version (%s)" % (name, str(__CoreVersion__)))
        wb = openpyxl.load_workbook(filename=ic_path, keep_vba=True)  # load the xlsx spreadsheet
        ws_name = wb.sheetnames
        ws_summary = wb['summary']  # load the data from the summary sheet
        version = ws_summary['C3'].value

    n_row_collection = 22
    logger.info("importing data for %s" % name)

    if isinstance(ws_summary['C2'].value, datetime.datetime):
        if isinstance(ws_summary['D2'].value, datetime.time):
            date = datetime.datetime.combine(ws_summary['C2'].value, ws_summary['D2'].value)
            if ws_summary['E2'].value is not None and dateutil.tz.gettz(ws_summary['E2'].value):
                tz = dateutil.tz.gettz(ws_summary['E2'].value)
                date = date.replace(tzinfo=tz)
            else:
                logger.info("\t(%s) timezone unavailable." % name)
        else:
            date = ws_summary['C2'].value
            if ws_summary['D2'].value is not None and dateutil.tz.gettz(ws_summary['D2'].value):
                tz = dateutil.tz.gettz(ws_summary['D2'].value)
                date = date.replace(tzinfo=tz)
            else:
                logger.info("\t(%s) timezone unavailable." % name)
    else:
        logger.warning("\t(%s) date unavailable" % name)
        date = None

    origin = ws_summary['C5'].value

    if isinstance(ws_summary['C6'].value, (float, int)) or isinstance(ws_summary['D6'], (float, int)):
        lat = ws_summary['C6'].value
        lon = ws_summary['D6'].value
    elif ws_summary['C6'].value and ws_summary['D6'].value:
        logger.info("\t(%s) lat/lon not defined in decimal degree" % name)
        lat = np.nan
        lon = np.nan
    else:
        logger.info("\t(%s) lat/lon unknown" % name)
        lat = np.nan
        lon = np.nan

    comments = []
    if isinstance(ws_summary['C9'].value, (float, int)):
        snow_depth = np.array([ws_summary['C9'].value]).astype(float)
        n_snow = 1
        while ws_summary.cell(row=9, column=3+n_snow).value is not None:
            snow_depth = np.concatenate((snow_depth, np.array([ws_summary.cell(row=9, column=3+n_snow).value])))
            n_snow += 1
        if isinstance(snow_depth[-1], str):
            comments.append(snow_depth[-1])
            snow_depth = pd.to_numeric(snow_depth[:-1], errors='coerce')
        else:
            snow_depth = pd.to_numeric(snow_depth, errors='coerce')
    else:
        snow_depth = np.array([np.nan])

    # freeboard
    if isinstance(ws_summary['C10'].value, (float, int)):
        freeboard = np.array([ws_summary['C10'].value])
        n_temp = 1
        while ws_summary.cell(row=10, column=3+n_temp).value is not None:
            freeboard = np.concatenate((freeboard, np.array([ws_summary.cell(row=10, column=3 + n_temp).value])))
            if not isinstance(ws_summary.cell(row=10, column=3+n_temp).value, (float, int)):
                logger.info("(%s)\tfreeboard cell %s not a float" % (name, openpyxl.utils.get_column_letter(3 + n_temp)+str(9)))
            n_temp += 1

        if isinstance(freeboard[-1], str):
            comments.append(freeboard[-1])
            freeboard = pd.to_numeric(freeboard[:-1], errors='coerce')
        else:
            freeboard = pd.to_numeric(freeboard, errors='coerce')
    else:
        freeboard = np.array([np.nan])

    # ice thickness
    if isinstance(ws_summary['C11'].value, (float, int)):
        ice_thickness = np.array([ws_summary['C11'].value])
        n_temp = 1
        while ws_summary.cell(row=11, column=3+n_temp).value:
            ice_thickness = np.concatenate(
                (ice_thickness, np.array([ws_summary.cell(row=11, column=3 + n_temp).value])))
            if not isinstance(ws_summary.cell(row=11, column=3+n_temp).value, (float, int)):
                logger.info("\t(%s) ice_thickness cell %s not a float" % (name, openpyxl.utils.get_column_letter(3+n_temp)+str(9)))
            n_temp += 1
        if isinstance(freeboard[-1], str):
            comments.append(freeboard[-1])
            ice_thickness = pd.to_numeric(ice_thickness[:-1], errors='coerce')
        else:
            ice_thickness = pd.to_numeric(ice_thickness, errors='coerce')
    else:
        ice_thickness = np.array([np.nan])

    core = pysic.Core(name, date, origin, lat, lon, ice_thickness, freeboard, snow_depth)

    # temperature
    if ws_summary['C15'].value:
        core.t_air = ws_summary['C15'].value
    if ws_summary['C16'].value:
        core.t_snow_surface = ws_summary['C16'].value
    if ws_summary['C17'].value:
        core.t_ice_surface = ws_summary['C17'].value
    if ws_summary['C18'].value:
        core.t_water = ws_summary['C18'].value

    # sampling protocol
    m_col = 3
    if ws_summary[openpyxl.utils.cell.get_column_letter(m_col) + str('%.0i' %(n_row_collection+2))].value is not None:
        core.protocol = ws_summary[openpyxl.utils.cell.get_column_letter(m_col) + str('%.0i' %(n_row_collection+2))].value
    else:
        core.protocol = 'N/A'

    # core collection
    while (ws_summary[openpyxl.utils.cell.get_column_letter(m_col) + str('%.0f' % n_row_collection)] is not None and
           ws_summary[openpyxl.utils.cell.get_column_letter(m_col) + str('%.0f' % n_row_collection)].value is not None):
        core.add_to_collection(ws_summary[openpyxl.utils.cell.get_column_letter(m_col) + str('%.0f' % n_row_collection)].value)
        m_col += 1

    # comment
    if ws_summary['A33'].value is not None:
        comments.append(ws_summary['A33'].value)
    core.add_comment('; '.join(comments))


    # import all variables
    if variables is None:
        sheets = [sheet for sheet in ws_name if (sheet not in ['summary', 'abreviation', 'locations', 'lists', 'Vf_oil_calculation']) and
                     (sheet.lower().find('fig') == -1)]
        for sheet in sheets:
            ws_variable = wb[sheet]
            profile = read_profile(ws_variable, variables=None, version=version)
            profile.name = name
            if drop_empty:
                profile.drop_empty_property()

            # 20190615 - read_profile should return an empty profile if there is no variables
            # if profile.variables() is None:
            #     profile = pd.DataFrame()

            if not profile.empty:
                if profile.get_name() is not core.name:
                    logger.error('\t(%s) core name %s and profile name %s does not match'
                                 % (ic_path, core.name, profile.get_name()))
                else:
                    core.add_profile(profile)
                    logger.info('(%s) data imported with success: %s' % (core.name, ", ".join(profile.get_property())))
            else:
                logger.info('(%s) no data to import from %s ' % (core.name, sheet))
    else:
        if not isinstance(variables, list):
            if variables.lower().find('state variable')+1:
                variables = ['temperature', 'salinity']
            else:
                variables = [variables]

        _imported_variables = []
        for variable in variables:
            if variable_2_sheet[variable] in ws_name and variable not in _imported_variables:
                sheet = variable_2_sheet[variable]
                ws_variable = wb[sheet]

                variable2import = [var for var in variables if var in inverse_dict(variable_2_sheet)[sheet]]

                profile = read_profile(ws_variable, variables=variable2import, version=version, v_ref=v_ref)

                if profile.get_name() is not core.name:
                    logger.error('\t(%s) core name %s and profile name %s does not match'
                                 % (ic_path, core.name, profile.name()))
                elif not profile.empty:
                    core.add_profile(profile)
                    logger.info(' (%s) data imported with success: %s' % (profile.get_name(), profile.get_property()))
                else:
                    _temp = [variable for variable in profile.get_variable() if profile[variable].isnull().all()]
                    if _temp.__len__() > 1:
                        logger.info(' (%s) no data to import: %s ' % (profile.get_name(), ", ".join(_temp)))
                    else:
                        logger.info('(%s) no variable to import' % name)

                _imported_variables +=variable2import

    return core


def import_ic_list(ic_list, variables=variables, v_ref=v_ref, verbose=verbose, drop_empty=drop_empty):
    """
    :param ic_list:
            array, array contains absolute filepath for the cores
    :param variables:
    :param v_ref:
        top, or bottom
    """
    logger = logging.getLogger(__name__)

    ic_dict = {}
    inexisting_ic_list = []
    for ic_path in ic_list:
        if verbose:
            print('Importing data from %s' % ic_path)
        if not os.path.exists(ic_path):
            logger.warning("%s does not exists in core directory" % ic_path.split('/')[-1])
            inexisting_ic_list.append(ic_path.split('/')[-1].split('.')[0])
        else:
            ic_data = import_ic_path(ic_path, variables=variables, v_ref=v_ref, drop_empty=drop_empty)
            if not ic_data.variables():
                inexisting_ic_list.append(ic_path.split('/')[-1].split('.')[0])
                logger.warning("%s have no properties profile" % (ic_data.name))
            else:
                ic_dict[ic_data.name] = ic_data

    logging.info("Import ice core lists completed")
    if inexisting_ic_list.__len__() > 0:
        logger.info("%s core does not exits. Removing from collection" % ', '.join(inexisting_ic_list))

    for ic in inexisting_ic_list:
        for ic2 in ic_dict.keys():
            if ic in ic_dict[ic2].collection:
                ic_dict[ic2].del_from_collection(ic)
                logger.info("remove %s from %s collection" % (ic, ic2))
    return ic_dict


def import_ic_sourcefile(f_path, variables=None, ic_dir=None, v_ref='top', drop_empty=False):
    """
    :param filepath:
            string, absolute path to the file containing either the absolute path of the cores (1 path by line) or the
            core names (1 core by line). In this last case if core_dir is None core_dir is the directory contianing the
            file.
    :param variables:

    :param v_ref:
        top, or bottom
    """
    logger = logging.getLogger(__name__)
    logger.info('Import ice core from source file: %s' % f_path)

    if ic_dir is not None:
        with open(f_path) as f:
            ics = sorted([os.path.join(ic_dir, line.strip()) for line in f if not line.strip().startswith('#')])
    else:
        with open(f_path) as f:
            ics = sorted([line.strip() for line in f if not line.strip().startswith('#')])

    print(ics)

    return import_ic_list(ics, variables=variables, v_ref=v_ref, drop_empty=drop_empty)


# read profile

def read_profile(ws_variable, variables=None, version=__CoreVersion__, v_ref='top'):
    """
    :param ws_variable:
        openpyxl.worksheet
    :param variables:
    :param version:
    :param v_ref:
        top, or bottom
    """
    logger = logging.getLogger(__name__)

    if version == 1:
        row_data_start = 6
        row_header = 4
    elif version == 1.1:
        row_data_start = 8
        row_header = 5
        if ws_variable['C4'].value:
            v_ref = ws_variable['C4'].value
    else:
        logger.error("ice core spreadsheet version not defined")

    sheet_2_data = {'S_ice': [row_data_start, 'ABC', 'DEFG', 'J'],
                    'T_ice': [row_data_start, 'A', 'B', 'C'],
                    'Vf_oil': [row_data_start, 'ABC', 'DEFG', 'H']}
    # TODO: add other sheets for seawater, sediment, CHla, Phae, stratigraphy
    #                'stratigraphy': [row_data_start, 'AB', 'C', 'D'],
    #                'seawater': [row_data_start, 'A', 'DEFGF', 'G']}

    # define section
    headers_depth = ['y_low', 'y_mid', 'y_sup']

    if not ws_variable.title in sheet_2_data:  # if the sheet does not exist, return an empty profile
        profile = pysic.core.profile.Profile()
    else:
        name = ws_variable['C1'].value
        # Continuous profile
        if sheet_2_data[ws_variable.title][1].__len__() == 1:
            y_mid = np.array([ws_variable[sheet_2_data[ws_variable.title][1] + str(row)].value
                              for row in range(sheet_2_data[ws_variable.title][0], ws_variable.max_row + 1)]).astype(float)
            y_low = np.nan * np.ones(y_mid.__len__())
            y_sup = np.nan * np.ones(y_mid.__len__())

        # Step profile
        elif sheet_2_data[ws_variable.title][1].__len__() >= 2:
            y_low = np.array([ws_variable[sheet_2_data[ws_variable.title][1][0] + str(row)].value
                              for row in range(sheet_2_data[ws_variable.title][0], ws_variable.max_row+1)]).astype(float)
            y_sup = np.array([ws_variable[sheet_2_data[ws_variable.title][1][1] + str(row)].value
                              for row in range(sheet_2_data[ws_variable.title][0], ws_variable.max_row+1)]).astype(float)
            y_mid = np.array([ws_variable[sheet_2_data[ws_variable.title][1][2] + str(row)].value
                              for row in range(sheet_2_data[ws_variable.title][0], ws_variable.max_row+1)]).astype(float)

            # check if y_mid are not nan:
            if np.isnan(y_mid).any():
                y_mid = (y_low + y_sup) / 2
                logger.info('(%s - %s ) not all y_mid exits, calculating y_mid = (y_low+y_sup)/2'
                            % (name, ws_variable.title))
            elif np.any(np.abs(((y_low + y_sup)/ 2) - y_mid > 1e-12)):
                    logger.error('(%s - %s ) y_mid are not mid point between y_low and y_sup. \\'
                                 'Replacing with y_mid = (y_low+y_sup)/2'
                                 % (name, ws_variable.title))
            else:
                logger.info('(%s - %s ) y_low, y_mid and y_sup read with success'
                            % (name, ws_variable.title))


        # read data
        min_col = sheet_2_data[ws_variable.title][2][0]
        min_col = openpyxl.utils.column_index_from_string(min_col)

        max_col = ws_variable.max_column

        min_row = sheet_2_data[ws_variable.title][0]
        max_row = min_row + y_mid.__len__()-1

        # _data = [[cell.value if isinstance(cell.value, (float, int)) else np.nan for cell in row]
        #          for row in ws_variable.iter_cols(min_col, max_col, min_row, max_row)]
        _data = [[cell.value if isinstance(cell.value, (float, int, str)) else np.nan for cell in row]
                 for row in ws_variable.iter_cols(min_col, max_col, min_row, max_row)]

        data = np.array([y_low, y_mid, y_sup])
        data = np.vstack([data, np.array(_data)])

        variable_headers = [ws_variable.cell(row_header, col).value for col in range(min_col, max_col+1)]

        # # fill missing section with np.nan
        # if fill_missing:
        #     idx = np.where(np.abs(y_low[1:-1]-y_sup[0:-2]) > TOL)[0]
        #     for ii_idx in idx:
        #         empty = [y_sup[ii_idx], (y_sup[ii_idx]+y_low[ii_idx+1])/2, y_low[ii_idx+1]]
        #         empty += [np.nan] * (variable_headers.__len__()+1)
        #     data = np.vstack([data, empty])

        # assemble profile dataframe
        profile = pd.DataFrame(data.transpose(), columns=headers_depth + variable_headers)

        # drop empty variable header
        if None in profile.columns:
            profile = profile.drop(labels=[None], axis=1)

        # # convert string to float:
        # float_header = [h for h in profile.columns if h not in ['comments']]
        # profile[float_header] = profile[float_header].apply(pd.to_numeric, errors='coerce')

        # drop property with all nan value
        profile = profile.dropna(axis=1, how='all')

        # remove empty line if all element of depth are nan:
        subset = [col for col in ['y_low', 'y_mid', 'y_sup'] if col in profile.columns]
        profile = profile.dropna(axis=0, subset=subset, how='all')

        # singularize comments
        if 'comments' in profile.columns:
            profile.rename(columns={'comments': "comment"}, inplace=True)
        # add comment column if it does not exist
        if 'comment' not in profile.columns:
            profile['comment'] = None
        else:
            profile['comment'] = profile['comment'].astype(str).replace({'nan': None})

        # get all property variable (e.g. salinity, temperature, ...)
        property = [var for var in profile.columns if var not in ['comment'] + headers_depth]

        # remove subvariable (e.g. conductivity temperature measurement for conductivity
        property = [prop for prop in property if prop not in inverse_dict(subvariable_dict)]

        # set variable to string of property
        profile['variable'] = [', '.join(property)]*len(profile.index)

        # ice core length
        try:
            length = float(ws_variable['C2'].value)
        except:
            logger.info('(%s) no ice core length' % name)
            length = np.nan
        else:
            if length == 'n/a':
                profile['comment'] = 'ice core length not available'
                logger.info('(%s) ice core length is not available (n/a)' % name)
                length = np.nan
            elif not isinstance(length, (int, float)):
                logger.info('%s ice core length is not a number' % name)
                profile['comment'] = 'ice core length not available'
                length = np.nan
        profile['length'] = [length]*len(profile.index)

        # set vertical references
        profile['v_ref'] = [v_ref]*len(profile.index)

        # set ice core name for profile
        profile['name'] = [name]*len(profile.index)

        # set columns type
        col_string = ['comment', 'v_ref', 'name', 'profile', 'variable']
        col_date = ['date']
        col_float = [h for h in profile.columns if h not in col_string and h not in col_date]
        profile[col_float] = profile[col_float].apply(pd.to_numeric, errors='coerce')
        c_string = [h for h in col_string if h in profile.columns]
        profile[c_string] = profile[c_string].astype(str).replace({'nan': None})

        profile = pysic.core.profile.Profile(profile)
        # remove variable not in variables
        if variables is not None:
            for property in profile.properties():
                if property not in variables:
                    profile.delete_property(property)

    return profile


def read_profile_MOSAiC(ws_variable, variables=None, version=__CoreVersion__, v_ref='top'):
    """
    :param ws_variable:
        openpyxl.worksheet
    :param variables:
    :param version:
    :param v_ref:
        top, or bottom
    """
    logger = logging.getLogger(__name__)

    # read headers:
    n_row = 2
    n_col = 1
    cell_flag = 2
    headers = []
    subheaders = []
    units = []
    while cell_flag:
        if isinstance(ws_variable.cell(n_row, n_col).value, str):
            headers.append(ws_variable.cell(n_row, n_col).value)
            subheaders.append(ws_variable.cell(n_row+1, n_col).value)
            units.append(ws_variable.cell(n_row+2, n_col).value)
        else:
            cell_flag -= 1
        n_col += 1
    n_col_max = n_col-2


    # Check for step or continuous profiles:
    if 'depth center' in headers:
        loc1 = [ii for ii, h in enumerate(headers) if h == 'depth center'][0] + 1
        headers[loc1-1] = 'y_mid'
        y_mid = np.array(
            [ws_variable.cell(row, loc1).value for row in range(5, ws_variable.max_row + 1)]).astype(float)

        # discard trailing nan value from the end up
        # find nan value in y_low and y_sup
        y_nan_loc = np.where(np.isnan(y_mid))[0]
        # discard trailing nan value starting at the end
        if len(y_mid) > 1 and y_nan_loc[-1] == len(y_mid)-1:
            y_nan_loc = [len(y_mid)-1] + [val for ii, val in enumerate(y_nan_loc[-2::-1]) if val == y_nan_loc[::-1][ii]-1]
            y_nan_loc = y_nan_loc[::-1]

            y_mid = [y for ii, y in enumerate(y_mid) if ii not in y_nan_loc]

    if 'depth 1' in headers and 'depth 2' in headers:
        step_flag = 1

        # find column with depth 1
        # TODO find a better way to find the location
        loc1 = [ii for ii, h in enumerate(headers) if h == 'depth 1'][0]+1
        headers[loc1 - 1] = 'y_low'
        loc2 = [ii for ii, h in enumerate(headers) if h == 'depth 2'][0]+1
        headers[loc2 - 1] = 'y_sup'
        # TODO: remove 'depth center'
        y_low = np.array([ws_variable.cell(row, loc1).value for row in range(5, ws_variable.max_row + 1)]).astype(float)
        y_sup = np.array([ws_variable.cell(row, loc2).value for row in range(5, ws_variable.max_row + 1)]).astype(float)

        # discard trailing nan value from the end up
        # find nan value in y_low and y_sup
        y_nan_loc = [ii for ii in np.where(np.isnan(y_sup))[0] if ii in np.where(np.isnan(y_low))[0]]

        # discard trailing nan value starting at the end
        if len(y_sup) > 0 and len(y_nan_loc) > 0 and y_nan_loc[-1] == len(y_sup)-1:
            y_nan_loc = [len(y_sup)-1] + [val for ii, val in enumerate(y_nan_loc[-2::-1]) if val == y_nan_loc[::-1][ii]-1]
            y_nan_loc = y_nan_loc[::-1]
            y_low = np.array([y for ii, y in enumerate(y_low) if ii not in y_nan_loc])
            y_sup = np.array([y for ii, y in enumerate(y_sup) if ii not in y_nan_loc])

            # TODO: replace missing y_low and y_sup with y_mid if possible

        if len(y_low) == 0:
            return pysic.core.profile.Profile()
        elif 'y_mid' in headers:
            if np.isnan(y_mid).any() or len(y_mid) == 0:
                y_mid = (y_low + y_sup) / 2
                logger.info('(%s ) not all y_mid exits, calculating y_mid = (y_low+y_sup)/2'
                            % (ws_variable.title))
            elif np.any(np.abs(((y_low + y_sup) / 2) - y_mid > 1e-12)):
                logger.error('(%s ) y_mid are not mid point between y_low and y_sup. \\'
                             'Replacing with y_mid = (y_low+y_sup)/2'
                             % (ws_variable.title))
                y_mid = (y_low + y_sup) / 2
            else:
                logger.info('(%s ) y_low, y_mid and y_sup read with success'
                            % (ws_variable.title))
        else:
            y_mid = (y_low + y_sup) / 2
    elif 'depth 1' in headers:
        loc1 = [ii for ii, h in enumerate(headers) if h == 'depth 1'][0]+1
        headers[loc1 - 1] = 'y_low'
        # TODO : fill y_sup
    elif 'depth 2' in headers:
        loc1 = [ii for ii, h in enumerate(headers) if h == 'depth 2'][0]+1
        headers[loc1 - 1] = 'y_sup'
        # TODO : fill y_low
    # Continuous profile
    else:
        y_low = np.nan * np.ones(y_mid.__len__())
        y_sup = np.nan * np.ones(y_mid.__len__())

    # Read data:
    n_row_min = 5
    n_row_max = n_row_min + len(y_mid)-1

    n_col_min = 1
    n_col_max = n_col_max - n_col_min

    # Drop column with depth:
    # _data = [[cell.value if isinstance(cell.value, (float, int)) else np.nan for cell in row]
    #                   for row in ws_variable.iter_rows(n_row_min, n_row_max, n_col_min, n_col_max)]
    _data = [[cell.value for cell in row] for row in ws_variable.iter_rows(n_row_min, n_row_max, n_col_min, n_col_max)]

    # TODO:  fill missing section with np.nan
    # if fill_missing:
    #     idx = np.where(np.abs(y_low[1:-1]-y_sup[0:-2]) > TOL)[0]
    #     for ii_idx in idx:
    #         empty = [y_sup[ii_idx], (y_sup[ii_idx]+y_low[ii_idx+1])/2, y_low[ii_idx+1]]
    #         empty += [np.nan] * (variable_headers.__len__()+1)
    #     data = np.vstack([data, empty])

    # concatenate header and subheader
    subheaders = [sh if sh is not None else '' for sh in subheaders]
    profile_headers = [h + '_' + subheaders[ii] if (len(subheaders[ii]) > 1 and h not in ['y_low', 'y_sup', 'y_mid']) else h
                       for ii, h in enumerate(headers)]
    # TODO: double header for dataframe with header and subheader

    profile = pd.DataFrame(_data, columns = profile_headers)

    # drop empty variable header
    if None in profile.columns:
        profile = profile.drop(labels=[None], axis=1)

    # sample ID columns is string:
    string_header = ['comment'] + [h for h in profile.columns if 'sample ID' in h or 'ID' in h]

    # convert string to float:
    float_header = [h for h in profile.columns if h not in string_header]
    profile[float_header] = profile[float_header].apply(pd.to_numeric, errors='coerce')

    # drop property with all nan value
    profile = profile.dropna(axis=1, how='all')

    # remove empty line if all element of depth are nan:
    subset = [col for col in ['y_low', 'y_sup', 'y_mid'] if col in profile.columns]
    profile = profile.dropna(axis=0, subset=subset, how='all')

    # singularize comments
    if 'comments' in profile.columns:
        profile.rename(columns={'comments': "comment"}, inplace=True)
    # add comment column if it does not exist
    if 'comment' not in profile.columns:
        profile['comment'] = None
    else:
        profile['comment'] = profile['comment'].astype(str).replace({'nan': None})

    # get all property variable (e.g. salinity, temperature, ...)
    property = [var for var in profile.columns if var not in ['comment', 'y_low', 'y_sup', 'y_mid']]
    property = [prop.split('_')[0] for prop in property]

    # remove subvariable (e.g. conductivity temperature measurement for conductivity
    property = [prop for prop in property if prop not in inverse_dict(subvariable_dict)]

    # set variable to string of property
    profile['variable'] = [', '.join(property)] * len(profile.index)

    # set vertical references
    v_ref_read = ws_variable['C1'].value
    if v_ref_read == 'ice surface':
        v_ref = 'top'
    elif v_ref_read == 'ice/water interface':
        v_ref = 'bottom'
    else:
        logger.error(ws_variable.title + ' - Vertical references not set')
    profile['v_ref'] = [v_ref] * len(profile.index)

    # set columns type
    col_string = ['comment', 'v_ref', 'name', 'profile', 'variable']
    col_date = ['date']
    col_float = [h for h in profile.columns if h not in col_string and h not in col_date]
    profile[col_float] = profile[col_float].apply(pd.to_numeric, errors='coerce')
    c_string = [h for h in col_string if h in profile.columns]
    profile[c_string] = profile[c_string].astype(str).replace({'nan': None})

    profile = pysic.core.profile.Profile(profile)
    # remove variable not in variables
    if variables is not None:
        for property in profile.properties():
            if property not in variables:
                profile.delete_property(property)

    return profile


# create list or source
def list_folder(dirpath, fileext='.xlsx', level=0):
    """
    list all files with specific extension in a directory

    :param dirpath: str; directory to scan for ice core
    :param fileext: str, default .xlsx; file extension for ice core data
    :param level: numeric, default 0; level of recursitivy in directory search
    :return ic_list: list
        list of ice core path
    """
    _ics = []

    logger = logging.getLogger(__name__)

    def walklevel(some_dir, level=level):
        some_dir = some_dir.rstrip(os.path.sep)
        assert os.path.isdir(some_dir)
        num_sep = some_dir.count(os.path.sep)
        for root, dirs, files in os.walk(some_dir):
            yield root, dirs, files
            num_sep_this = root.count(os.path.sep)
            if num_sep + level <= num_sep_this:
                del dirs[:]

    for dirName, subdirList, fileList in walklevel(dirpath, level=level):
        _ics.extend([dirName + '/' + f for f in fileList if f.endswith(fileext)])

    ics_set = set(_ics)
    logger.info("Found %i ice core datafile in %s" % (ics_set.__len__(), dirpath))

    return ics_set


def list_ic_path(dirpath, fileext):
    """
    list all files with specific extension in a directory

    :param dirpath: str
    :param fileext: str
    :return ic_list: list
        list of ice core path
    """
    logger = logging.getLogger(__name__)

    ics_set = list_folder(dirpath=dirpath, fileext=fileext)
    ic_paths_set = set([os.path.join(os.path.realpath(dirpath), f) for f in ics_set])
    return ic_paths_set


def make_ic_sourcefile(dirpath, fileext, source_filepath=None):
    """
    list all files with specific extension in a directory

    :param dirpath: str
    :param fileext: str
    :return source_file: str
        filepath to the text file containing ice core filepath with absolute path.
    """
    logger = logging.getLogger(__name__)

    ic_paths_set = list_ic_path(dirpath, fileext)

    if source_filepath is None:
        source_filepath = os.path.join(os.path.realpath(dirpath), 'ic_list.txt')

    with open(source_filepath, 'w') as f:
        for ic_path in ic_paths_set:
            f.write(ic_path + "\n")

    return source_filepath

#
# def read_ic_list(file_path):
#     """
#
#     :param file_path:
#     :return:
#     """
#
#     with open(file_path) as f:
#         data = [list(map(int, row.split())) for row in f.read().split('\n\n')]
#
#     return ic_list

# updater
def update_spreadsheet(ic_path, v_ref='top', backup=True):
    """
    update_spreadsheet update an ice core file to the latest ice core file version (__CoreVersion__).

    :param ic_path: str
        Path to the ice core file to update
    :param v_ref: int, 'top' or 'bottom', Default 'top'
        Set the zero vertical reference of the core. If 'top, zero vertical reference is set at the ice/snow or ice/air
        interface. If 'bottom, zero vertical reference is set at the ice/water interface
    :param verbose: int
        verbosity of the function.
    :param backup: bool, default True
        If True, backup the previous file version in the subdirectory 'folder-COREVERSION'
    :return nothing:

    USAGE:
        update_spreadhseet(ic_path)
    """
    logger = logging.getLogger(__name__)

    import shutil
    if not os.path.exists(ic_path):
        logger.error("%s does not exists in core directory" % ic_path.split('/')[-1])
        return 0
    else:
        logger.info("\t ice core file path %s" % ic_path)

    wb = openpyxl.load_workbook(filename=ic_path, keep_vba=False)  # load the xlsx spreadsheet
    ws_summary = wb['summary']  # load the data from the summary sheet

    if isinstance(ws_summary['C3'].value, (float, int)):
        version = ws_summary['C3'].value
        if version < __CoreVersion__:
            logger.info("Updating core data to latest version %.1f" % __CoreVersion__)
    else:
        logger.error("\t%s ice core file version not unavailable" % ic_path)

    while version < __CoreVersion__:

        # backup old version
        if backup:
            backup_dir = os.path.join(os.path.dirname(ic_path), 'version-' + str(version))
            ic_bkp = os.path.join(backup_dir, os.path.basename(ic_path))

            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            shutil.move(ic_path, ic_bkp)

         # update from 1.0 to 1.1
        if version == 1:
            # update from 1.0 to 1.1
            version = 1.1
            ws_summary['C3'] = version
            # remove rows "core number in series"
            ws_summary.delete_rows(22, 1)

            if "S_ice" in wb.sheetnames:
                ws = wb['S_ice']

                # add reference row=4
                ws.insert_rows(4)
                ws['A4'] = 'vertical reference'
                ws['C4'] = v_ref

                # remove "sample number" column
                if ws['M5'].value == 'sample number':
                    ws.delete_cols(openpyxl.utils.cell.column_index_from_string('M'))

                # remove salinity for temperature
                range = "F5:" + openpyxl.utils.cell.get_column_letter(ws.max_column) + str(ws.max_row)
                ws.move_range(range, rows=0, cols=-1)

                # move d180 dD after conductance with T_sigma (conductivity) suppresion
                range = "E5:G" + str(ws.max_row)
                ws.move_range(range, rows=0, cols=6)
                range = "H5:" + openpyxl.utils.cell.get_column_letter(ws.max_column) + str(ws.max_row)
                ws.move_range(range, rows=0, cols=-3)

                # add notation row=6
                ws.insert_rows(6)

                ws['A6'] = 'd_1'
                ws['B6'] = 'd_2'
                ws['C6'] = 'd'
                ws['D5'] = 'salinity'
                ws['D6'] = 'S'
                ws['E5'] = 'conductivity'
                ws['E6'] = 'σ'
                ws['E7'] = 'mS/cm'
                ws['F5'] = 'conductivity measurement temperature'
                ws['F6'] = 'T_σ'
                ws['G5'] = 'specific conductance'
                ws['G6'] = 'κ'
                ws['G7'] = 'mS/cm'
                ws['H6'] = 'd180'
                ws['I6'] = 'dD'
                ws['J6'] = ''

            if "T_ice" in wb.sheetnames:
                ws = wb["T_ice"]

                # add reference row=4
                ws.insert_rows(4)
                ws['A4'] = 'vertical reference'
                ws['C4'] = v_ref

                # add notation row=6
                ws.insert_rows(6)
                ws['A6'] = 'd'
                ws['B6'] = 'T'

            if "oil_content" in wb.sheetnames:
                ws = wb["oil_content"]
                # add reference row=4
                ws.insert_rows(4)
                ws['A4'] = 'vertical reference'
                ws['C4'] = v_ref

                # add notation row=6
                ws.insert_rows(6)
                ws['A6'] = 'd_1'
                ws['B6'] = 'd_2'
                ws['C6'] = 'd'
                ws['D6'] = 'V_i'
                ws['E6'] = 'h_menisc'
                ws['F6'] = 'd_menisc'
                ws['G6'] = 'd_center'

            if "S-figure" in wb.sheetnames:
                ws = wb['S-figure']
                wb.remove_sheet(ws)

            if "T-figure" in wb.sheetnames:
                ws = wb['T-figure']
                wb.remove_sheet(ws)

    wb.save(ic_path)
    wb.close()

# TODO: cleaner function to (1) remove trailing and heading space in instrument

def update_spreadsheet_MOSAiC(ic_path, backup = True):
    logger = logging.getLogger(__name__)

    import shutil
    if not os.path.exists(ic_path):
        logger.error("%s does not exists in core directory" % ic_path.split('/')[-1])
        return 0
    else:
        logger.info("\t ice core file path %s" % ic_path)

    wb = openpyxl.load_workbook(filename=ic_path, keep_vba=False)  # load the xlsx spreadsheet
    ws_summary = wb['metadata-coring']  # load the data from the summary sheet

    # TODO update version number to X.Y.Z
    # release X
    # major Y
    # minor Z

    try:
        version = float(ws_summary['C1'].value[:-1])
    except TypeError:
        version = ws_summary['C1'].value
    #
    #
    # try:
    #     version = float(ws_summary['C1'].value[:-1])
    # except TypeError:
    #     version = str(ws_summary['C1'].value)

    while version < 1.3:
        # backup old version
        if backup:
            backup_dir = os.path.join(os.path.dirname(ic_path), 'bkp-ic_version_' + str(version))
            ic_bkp = os.path.join(backup_dir, os.path.basename(ic_path))

            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            shutil.move(ic_path, ic_bkp)

        if version == 1.2:
            old_version = version
            version = 1.3
            ws_summary['C1'] = version

            if "TEMP" in wb.sheetnames:
                ws = wb["TEMP"]

                # add reference row=4
                ws.insert_rows(3)
                ws['A3'] = 'value'
                ws['B3'] = 'value'
                ws['C3'] = '-'

            if "Density-volume" in wb.sheetnames:
                ws = wb["Density-volume"]

                # add reference row=4
                ws.insert_rows(3)
                ws['A3'] = 'value'
                ws['B3'] = 'value'
                ws['C2'] = 'field'
                ws['C3'] = 'sample ID'
                ws['D3'] = 'value'
                ws['E2'] = 'thickness'
                ws['E3'] = 'value1'
                ws['F2'] = 'thickness'
                ws['F3'] = 'value2'
                ws['G2'] = 'thickness'
                ws['G3'] = 'value3'
                ws['H2'] = 'thickness'
                ws['H3'] = 'value4'
                ws['I2'] = 'thickness'
                ws['I3'] = 'average'
                ws['J3'] = 'value'
                ws['K2'] = 'density'
                ws['K3'] = 'value'
                ws['L3'] = '-'

            if "Density-densimetry" in wb.sheetnames:
                ws = wb["Density-densimetry"]

                # add reference row=4
                ws.insert_rows(3)
                ws['A3'] = 'value'
                ws['B3'] = 'value'
                ws['C2'] = 'field'
                ws['C3'] = 'sample ID'
                ws['D3'] = 'value'
                ws['E3'] = 'value'
                ws['F3'] = 'value'
                ws['G3'] = 'value'
                ws['H3'] = '-'

            if "TEX" in wb.sheetnames:
                ws = wb["TEX"]

                # add reference row=4
                ws.insert_rows(3)
                ws['A3'] = 'value'
                ws['B3'] = 'value'
                ws['C2'] = 'depth center'
                ws['C3'] = 'value'
                ws['D3'] = 'value'
                ws['F3'] = '-'

            if "snow" in wb.sheetnames:
                ws = wb["snow"]

                # add reference row=4
                ws.insert_rows(1)
                ws['A1'] = 'Reference'
                ws['B1'] = 'zero vertical'
                ws['C1'] = 'ice surface'
                ws['C2'] = 'field'
                ws['C3'] = 'sample ID'
                ws['D1'] = 'direction'
                ws['E1'] = 'up'


            if "metadata-core" in wb.sheetnames:
                ws = wb["metadata-core"]

                max_row = ws.max_row
                n_row = 1
                while n_row <= max_row:
                    if ws.cell(n_row, 1).value != 'DATA VERSION':
                        n_row += 1
                    else:
                        break

                if n_row-1 == max_row:
                    n_row = 12
                    while ws.cell(n_row, 1).value is not None:
                        n_row += 1

                    ws.cell(n_row+1, 1).value = 'DATA VERSION'
                    ws.cell(n_row+2, 1).value = 1.0
                    ws.cell(n_row+2, 2).value = ws_summary['C12'].value
                    ws.cell(n_row+2, 3).value = 'initial data entry'

    # TODO: update to version 1.3.1

    if version == 2.3:
        new_version = '1.3.1'
        print('Update to future version ' + new_version)
        ws_summary['C1'] = new_version

        if "metadata-core" in wb.sheetnames:
            ws = wb["metadata-core"]

            max_row = ws.max_row
            n_row = 1
            while n_row <= max_row:
                if ws.cell(n_row, 1).value == 'DATA VERSION':
                    n_row += 1
                else:
                    break

            if n_row-1 == max_row:
                n_row = 12
                while ws.cell(n_row, 1).value is not None:
                    n_row += 1

                ws.cell(n_row+1, 1).value = 'DATA VERSION'
                ws.cell(n_row+2, 1).value = 2.0
                ws.cell(n_row+2, 2).value = datetime.date.today()
                ws.cell(n_row+2, 3).value = 'Typo in data corrected. Updated spreadsheet to v. 1.3.1'

        if 'ECO' in wb.sheetnames:
            ws = wb["ECO"]
            if ws['F2'].value == 'Nutrient':
                ws['F2'] = 'nutrient'

            # TODO: update nutrient with 5 nutrient

        if 'snow' in wb.sheetnames:
            ws = wb["snow"]
            ws['L2'].value = 'snow'
            ws['L3'].value = 'weight'
            ws['M3'].value = 'density'
            ws['M3'].value = 'snow'
            ws['M3'].value = 'density'
            ws['N3'].value = 'comment'
            ws['N3'].value = '-'
            ws['N4'].value = '-'
            ws['O3'].value = 'temperature'
            ws['P3'].value = 'temperature'
            ws['P3'].value = 'value'

        # TODO: add column after N, before O


    #
    # if v_release == 1:
    #     if v_major == 3:
    #         if v_minor == 1:
    #             print('Latest version')
    #         else:
    #             print('Future version does not exist.')
    #     else:
    #         print('Future version does not exist')
    # else:
    #     print('Future version does not exist.')

    wb.save(ic_path)
    wb.close()

def inverse_dict(map):
    """
    return the inverse of a dictionnary with non-unique values
    :param map: dictionnary
    :return inv_map: dictionnary
    """
    revdict = {}
    for k, v in map.items():
        if isinstance(v, list):
            for vi in v:
                revdict[vi] = revdict.get(vi, [])
                revdict[vi].append(k)
        else:
            revdict[v] = revdict.get(v, [])
            revdict[v].append(k)
    return revdict