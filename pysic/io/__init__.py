__comment__ = "loadxl.py contained function to import ice core data from xlsx spreadsheet"
__all__ = ['load']
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