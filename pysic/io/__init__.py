__comment__ = "loadxl.py contained function to import ice core data from xlsx spreadsheet"
__all__ = ['load', 'update', 'clean']

import os
import logging

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