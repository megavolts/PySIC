__comment__ = "loadxl.py contained function to import ice core data from xlsx spreadsheet"
__all__ = ['load', 'update', 'clean']

import os
import logging


__all__ = ['find_str_in_row', 'find_str_in_col']

logging.basicConfig(level=logging.DEBUG)

subvariable_dict = {'conductivity': ['conductivity measurement temperature']}

property2sheet = {'temperature': 'temp',
                    'salinity': 'salo18',
                    'conductivity': 'salo18',
                    'specific conductance': 'salo18',
                    'd18O': 'salo18',
                    'dD': 'salo18',
                    'Vf_oil': 'Vf_oil', 'oil volume fraction': 'Vf_oil',  # MOSIDEO project
                    'Wf_oil': 'Wf_oil', 'oil weight fraction': 'Vf_oil',  # MOSIDEO project
                    'oil content': 'oil_content',  # CMI project
                    'oil mass': 'Vf_oil', 'm_oil': 'Vf_oil',
                    'brine': 'sackhole',
                    'sackhole': 'sackhole',
                    'seawater': 'seawater',
                    'snow': 'snow',
                    'eco': 'eco',
                    'sediment': 'sediment',
                    'Chla': 'eco',
                    'chlorophyl a': 'eco',
                    'Phae': 'eco'
                    }



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

    if not fileext.startswith('.'):
        fileext = '.' + fileext

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


# Helper function
def find_str_in_row(ws, header, row_idx=1):
    """
    find column index for a given header at a specific row
    :param ws: worksheet to search in
    :param header: header to look for
    :param row_idx: row index to look in, default 1
    :return: int, column index where header is found in row_idx row
    """
    from numpy import array
    col_idx_list = []
    for col_idx in range(1, ws.max_column):
        if header in str(ws.cell(row_idx, col_idx).value):
            col_idx_list.append(col_idx)
    return array(col_idx_list)


def find_str_in_col(ws, string, col_idx=1):
    """
    find row index with a given string in a specific column
    :param ws: worksheet to search in
    :param string: string to search for
    :param col_idx: index of column to search in
    :return:
    """
    import numpy as np
    row_idx_list = []
    for row_idx in range(1, ws.max_row):
        if ws.cell(row_idx, col_idx).value is not None and string in str(ws.cell(row_idx, col_idx).value):
            row_idx_list.append(row_idx)
    return np.array(row_idx_list)
