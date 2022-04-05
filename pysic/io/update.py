#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    pysic.io.update.py : function to update ice core spreadsheet
"""

from pysic.core.core import __CoreVersion__
import logging
import os
import openpyxl

from openpyxl.styles import NamedStyle, Font, Alignment, PatternFill
from openpyxl.styles.borders import Border, Side

from pysic.tools import version2int

#ic_path = '/home/megavolts/git/pysic/pysic/ressources/AAA_BB-YYYYXXZZ-N_P-1.4.6.xlsx'

# Cell style
# unit
unit_style = Font(name='Geneva', charset=1, family=2.0, b=False, i=True, strike=None, outline=None,
                  shadow=None, condense=None, color=None, extend=None, sz=9.0, u=None, vertAlign=None,
                  scheme=None)
unit_alignment = Alignment(horizontal='right')

# Border style
# bottom border
b_border = Border(left=Side(border_style=None), right=Side(border_style=None),
                  top=Side(border_style=None), bottom=Side(border_style='hair', color='00000000'))
# bottom_left_border
bl_border = Border(left=Side(border_style='hair', color='00000000'), right=Side(border_style=None),
                   top=Side(border_style=None), bottom=Side(border_style='hair', color='00000000'))
# left_border
l_border = Border(left=Side(border_style='hair', color='00000000'), right=Side(border_style=None),
                  top=Side(border_style=None), bottom=Side(border_style=None))
# right border
r_border = Border(left=Side(border_style=None), right=Side(border_style='hair', color='00000000'),
                  top=Side(border_style=None), bottom=Side(border_style=None))
# no_border
no_border = Border(left=Side(border_style=None), right=Side(border_style=None),
                   top=Side(border_style=None), bottom=Side(border_style=None))

# Style
m_header_style = NamedStyle(name="m_header_style")
m_header_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=True, italic=False, color='FF000000')  # black
m_header_style.alignment = Alignment(horizontal='center', wrapText=True, vertical='top')
m_header_style.fill = PatternFill(start_color="FFDDDDDD", end_color="FFE0E0E0", fill_type="solid")

m_subheader_style = NamedStyle(name="m_subheader_style")
m_subheader_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=False, color='FF000000')
m_subheader_style.alignment = Alignment(horizontal='center', wrapText=True, vertical='center')
m_subheader_style.fill = PatternFill(start_color="FFDDDDDD", end_color="FFE0E0E0", fill_type="solid")

m_unit_style = NamedStyle(name="m_unit_style")
m_unit_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=True, color='FF000000')
m_unit_style.alignment = Alignment(horizontal='center', wrapText=True, vertical='center')
m_unit_style.fill = PatternFill(start_color="FFDDDDDD", end_color="FFE0E0E0", fill_type="solid")

m_subheader_style_coring = NamedStyle(name="m_subheader_style_coring")
m_subheader_style_coring.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=True, italic=False, color='FF000000')  # black
m_subheader_style_coring.alignment = Alignment(horizontal='left', wrapText=True, vertical='center')
m_subheader_style_coring.fill = PatternFill(start_color="FFCCCCCC", end_color="FFBFBFBF", fill_type="solid")

m_unit_style_coring = NamedStyle(name="m_unit_style_coring")
m_unit_style_coring.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=True, color='FF000000')
m_unit_style_coring.alignment = Alignment(horizontal='right', wrapText=True, vertical='center')
m_unit_style_coring.fill = PatternFill(start_color="FFCCCCCC", end_color="FFBFBFBF", fill_type="solid")

m_comment_style_coring = NamedStyle(name="m_comment_style_coring")
m_comment_style_coring.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=True, color='FF000000')
m_comment_style_coring.alignment = Alignment(horizontal='left', wrapText=False, vertical='center')
m_comment_style_coring.fill = PatternFill(start_color="FFCCCCCC", end_color="FFBFBFBF", fill_type="solid")

m_bkg_style = NamedStyle(name="m_bkp_style")
m_bkg_style.fill = PatternFill(start_color="FFB2B2B2", end_color="FFBFBFBF", fill_type="solid")

m_bottom_style = NamedStyle(name="m_bottom_style")
m_bottom_style.fill = PatternFill(start_color="FFB2B2B2", end_color="FFBFBFBF", fill_type="solid")

#TODO: find surname and given name form os
user = 'Marc Oggier'

def ice_core_data(ic_path, backup=True, user=user):
    """
    :param ic_path:
        path; Filepath to the data spreadsheet to update
    :param backup:
        boolean, default True; Make a backup copy in a subfolder
    """
    import shutil
    import datetime as dt
    logger = logging.getLogger(__name__)

    wb = openpyxl.load_workbook(filename=ic_path, keep_vba=False)  # load the xlsx spreadsheet
    try:
        ws_summary = wb['metadata-coring']  # load the data from the summary sheet
    except KeyError:
        ws_summary = wb['metadata-station']  # load the data from the summary sheet
    else:
        pass
    version = ws_summary['C1'].value
    version_int = version2int(version)

    flag_update = False
    if version_int[1] <= 4 and version_int[2] < 1:
        logger.error('%s\t\tversion update from %s not supported' % (wb['metadata-core']['C1'].value, str(version)))

    while version_int[1] <= 4 and version_int[2] < version2int(__CoreVersion__)[2]:
        if not flag_update:
            flag_update = True
            # Backup old version
            if backup:
                backup_dir = os.path.join(os.path.dirname(ic_path), 'bkp-ic_version_' + str(version))
                ic_bkp = os.path.join(backup_dir, os.path.basename(ic_path))
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                shutil.copy(ic_path, ic_bkp)

        # Update from 1.2 to 1.3:
        #
        #     if version_int[1] == 2:
        #         old_version = version
        #         version = '1.3'
        #         ws_summary['C1'] = version
        #
        #         if "TEMP" in wb.sheetnames:
        #             ws = wb["TEMP"]
        #
        #             # add reference row=4
        #             ws.insert_rows(3)
        #             ws['A3'] = 'value'
        #             ws['B3'] = 'value'
        #             ws['C3'] = '-'
        #
        #         if "Density-volume" in wb.sheetnames:
        #             ws = wb["Density-volume"]
        #
        #             # add reference row=4
        #             ws.insert_rows(3)
        #             ws['A3'] = 'value'
        #             ws['B3'] = 'value'
        #             ws['C2'] = 'field'
        #             ws['C3'] = 'sample ID'
        #             ws['D3'] = 'value'
        #             ws['E2'] = 'thickness'
        #             ws['E3'] = 'value1'
        #             ws['F2'] = 'thickness'
        #             ws['F3'] = 'value2'
        #             ws['G2'] = 'thickness'
        #             ws['G3'] = 'value3'
        #             ws['H2'] = 'thickness'
        #             ws['H3'] = 'value4'
        #             ws['I2'] = 'thickness'
        #             ws['I3'] = 'average'
        #             ws['J3'] = 'value'
        #             ws['K2'] = 'density'
        #             ws['K3'] = 'value'
        #             ws['L3'] = '-'
        #
        #         if "Density-densimetry" in wb.sheetnames:
        #             ws = wb["Density-densimetry"]
        #
        #             # add reference row=4
        #             ws.insert_rows(3)
        #             ws['A3'] = 'value'
        #             ws['B3'] = 'value'
        #             ws['C2'] = 'field'
        #             ws['C3'] = 'sample ID'
        #             ws['D3'] = 'value'
        #             ws['E3'] = 'value'
        #             ws['F3'] = 'value'
        #             ws['G3'] = 'value'
        #             ws['H3'] = '-'
        #
        #         if "TEX" in wb.sheetnames:
        #             ws = wb["TEX"]
        #
        #             # add reference row=4
        #             ws.insert_rows(3)
        #             ws['A3'] = 'value'
        #             ws['B3'] = 'value'
        #             ws['C2'] = 'depth center'
        #             ws['C3'] = 'value'
        #             ws['D3'] = 'value'
        #             ws['F3'] = '-'
        #
        #         if "snow" in wb.sheetnames:
        #             ws = wb["snow"]
        #
        #             # add reference row=4
        #             ws.insert_rows(1)
        #             ws['A1'] = 'Reference'
        #             ws['B1'] = 'zero vertical'
        #             ws['C1'] = 'ice surface'
        #             ws['C2'] = 'field'
        #             ws['C3'] = 'sample ID'
        #             ws['D1'] = 'direction'
        #             ws['E1'] = 'up'
        #
        #         if "metadata-core" in wb.sheetnames:
        #             ws = wb["metadata-core"]
        #
        #             max_row = ws.max_row
        #             n_row = 1
        #             while n_row <= max_row:
        #                 if ws.cell(n_row, 1).value != 'DATA VERSION':
        #                     n_row += 1
        #                 else:
        #                     break
        #
        #             if n_row-1 == max_row:
        #                 n_row = 12
        #                 while ws.cell(n_row, 1).value is not None:
        #                     n_row += 1
        #
        #                 ws.cell(n_row+1, 1).value = 'DATA VERSION'
        #                 ws.cell(n_row+2, 1).value = 1.0
        #                 ws.cell(n_row+2, 2).value = ws_summary['C12'].value
        #                 ws.cell(n_row+2, 3).value = 'initial data entry'
        #
        # # TODO: update to version 1.3.1
        #
        # if version == '2.3':
        #     new_version = '1.3.1'
        #     print('Update to future version ' + new_version)
        #     ws_summary['C1'] = new_version
        #
        #     if "metadata-core" in wb.sheetnames:
        #         ws = wb["metadata-core"]
        #
        #         max_row = ws.max_row
        #         n_row = 1
        #         while n_row <= max_row:
        #             if ws.cell(n_row, 1).value == 'DATA VERSION':
        #                 n_row += 1
        #             else:
        #                 break
        #
        #         if n_row-1 == max_row:
        #             n_row = 12
        #             while ws.cell(n_row, 1).value is not None:
        #                 n_row += 1
        #
        #             ws.cell(n_row+1, 1).value = 'DATA VERSION'
        #             ws.cell(n_row+2, 1).value = 2.0
        #             ws.cell(n_row+2, 2).value = datetime.date.today()
        #             ws.cell(n_row+2, 3).value = 'Typo in data corrected. Updated spreadsheet to v. 1.3.1'
        #
        #     if 'ECO' in wb.sheetnames:
        #         ws = wb["ECO"]
        #         if ws['F2'].value == 'Nutrient':
        #             ws['F2'] = 'nutrient'
        #
        #         # TODO: update nutrient with 5 nutrient
        #
        #     if 'snow' in wb.sheetnames:
        #         ws = wb["snow"]
        #         ws['L2'].value = 'snow'
        #         ws['L3'].value = 'weight'
        #         ws['M3'].value = 'density'
        #         ws['M3'].value = 'snow'
        #         ws['M3'].value = 'density'
        #         ws['N3'].value = 'comment'
        #         ws['N3'].value = '-'
        #         ws['N4'].value = '-'
        #         ws['O3'].value = 'temperature'
        #         ws['P3'].value = 'temperature'
        #         ws['P3'].value = 'value'

        # Update from 1.3 to 1.4.1 (MOSAiC Expedition PS122 was originally 1.3)
        # Update from MOSAiC ice core data use a different script.


        # Update to 1.4.1 to 1.4.2
        if version_int[2] < 2:
            version_int[2] = 2
            # Update sheet name from 'metadata-coring' to 'metadata-station'
            if 'metadata-coring' in wb.sheetnames:
                wb['metadata-coring'].title = 'metadata-station'
                logger.debut("%s\t\tupdate 'metadata-coring' sheet title to 'metadata-station'")
            wb['metadata-station']['C1'].value = '1.4.2'

        # Update to 1.4.2 to 1.4.3
        if version_int[2] < 3:
            version_int[2] = 3

            # In 'metadata-station' add entry for seawater salinity below seawater temperature
            wb['metadata-station'].insert_rows(33, 1)
            wb['metadata-station']['A33'].value = 'water salinity'
            wb['metadata-station']['B33'].value = 'PSU'
            wb['metadata-station']['D33'].value = 'under ice'
            wb['metadata-station']['D32'].value = 'under ice'

            # Update "wind orientation' to 'wind direction'
            wb['metadata-station']['A43'].value = 'wind direction'

            # Formatting
            wb['metadata-station'].unmerge_cells('A34:E34')
            wb['metadata-station'].merge_cells('A35:E35')
            wb['metadata-station'].unmerge_cells('A40:E40')
            wb['metadata-station'].merge_cells('A41:E41')

            wb['metadata-station']['A33'].style = m_subheader_style_coring
            wb['metadata-station']['B33'].style = m_unit_style_coring

            wb['metadata-station']['D33'].style = m_comment_style_coring
            wb['metadata-station']['E33'].style = m_comment_style_coring
            for col in range(openpyxl.utils.column_index_from_string('A'),
                             openpyxl.utils.column_index_from_string('E') + 1):
                wb['metadata-station'].cell(32, col).border = b_border
                wb['metadata-station'].cell(34, col).style = m_bkg_style  # repaint unmerged cell
                wb['metadata-station'].cell(40, col).style = m_bkg_style  # repaint unmerged cell

            for col in range(openpyxl.utils.column_index_from_string('F'), openpyxl.utils.column_index_from_string('Z') + 1):
                wb['metadata-station'].cell(33, col).style = m_bkg_style

            # add sackhole sheet after snow:
            sackhole_sheet_index = wb._sheets.index(wb['snow']) + 1
            wb.create_sheet("sackhole", sackhole_sheet_index)
            wb_source = openpyxl.load_workbook('pysic/ressources/AAA_BB-YYYYMMDD-P-1.4.3-sackhole_tab.xlsx', data_only=True)
            copy_cells(wb_source['sackhole'], wb['sackhole'])  # copy all the cel values and styles
            copy_sheet_attributes(wb_source['sackhole'], wb['sackhole'])
            wb['metadata-station']['C1'].value = '1.4.3'

        # Update to 1.4.4 ## does not exist
        # if version_int[2] < 4:
        #     continue

        # Update from 1.4.3 to 1.4.5
        if version_int[2] < 5:
            version_int[2] = 5
            wb['metadata-station']['D42'].value = None
            wb['metadata-station']['D43'].value = None
            wb['metadata-station']['D44'].value = None
            wb['metadata-station']['B42'].value = 'm/s'
            wb['metadata-station']['B43'].value = 'degree'
            wb['metadata-station']['B44'].value = '/8'
            wb['metadata-station']['B45'].value = 'μmol/m2s'
            wb['metadata-station']['B46'].value = 'μmol/m2s'

            # style B42:B46 not bold, align right
            _col = openpyxl.utils.cell.column_index_from_string('B')
            for ii_row in range(42, 46+1):
                wb['metadata-station'].cell(ii_row, _col).font = unit_style
                wb['metadata-station'].cell(ii_row, _col).alignment = unit_alignment

            # Border formatting
            # C9:H9, bottom border sytle: hair

            for _row in openpyxl.utils.cell.rows_from_range('C9:H9'):
                for _cell in _row:
                    wb['metadata-station'][_cell].border = b_border

            # C14:C16, bottom border sytle: hair
            for _row in openpyxl.utils.cell.rows_from_range('C14:C16'):
                for _cell in _row:
                    wb['metadata-station'][_cell].border = b_border
            # C16:D16, bottom border sytle: None
            for _row in openpyxl.utils.cell.rows_from_range('C16:D16'):
                for _cell in _row:
                    wb['metadata-station'][_cell].border = no_border

            # add specific vertical border
            wb['metadata-station']['F9'].border = bl_border
            wb['metadata-station']['D14'].border = bl_border
            wb['metadata-station']['D16'].border = l_border
            wb['metadata-station']['C1'].value = '1.4.5'

        # Update to 1.4.6
        if version_int[2] < 6:
            version_int[2] = 6

            # remove unit to water salinity
            wb['metadata-station']['B33'].value = '-'

            # rename water salinity to seawater salinity
            wb['metadata-station']['A33'].value = 'seawater salinity'
            wb['metadata-station']['D33'].value = 'under ice/seawater interface'

            # rename water temperature to seawater temperature
            wb['metadata-station']['A32'].value = 'seawater temperature'
            wb['metadata-station']['D32'].value = 'under ice/seawater interface'

            # 'temp'
            # T1. unmerge cell
            wb['temp'].unmerge_cells('B1:C1')  # salinity
            # T2. formatting
            for cell_rows in openpyxl.utils.cols_from_range('B1:C3'):
                wb['temp'][cell_rows[0]].style = m_header_style
                wb['temp'][cell_rows[0]].border = no_border
                try:
                    wb['temp'][cell_rows[1]].style = m_subheader_style
                except ValueError:
                    wb['temp'][cell_rows[1]].style = 'm_subheader_style'
                else:
                    continue
                wb['temp'][cell_rows[1]].border = no_border
                wb['temp'][cell_rows[2]].style = m_unit_style
                wb['temp'][cell_rows[2]].border = no_border
            for col in [2, 4]:
                for row in range(1, 4):
                    wb['temp'].cell(row, col).border = l_border

            # 'salo18'
            # Salinity
            # S1. unmerge cell
            wb['salo18'].unmerge_cells('C1:E1')  # salinity
            wb['salo18'].unmerge_cells('F1:G1')  # conductivty

            wb['salo18']['D1'].value = wb['salo18']['C1'].value
            wb['salo18']['C1'].value = None

            # S2. formatting
            for cell_rows in openpyxl.utils.cols_from_range('C1:H3'):
                wb['salo18'][cell_rows[0]].style = m_header_style
                wb['salo18'][cell_rows[0]].border = no_border
                try:
                    wb['salo18'][cell_rows[1]].style = m_subheader_style
                except ValueError:
                    wb['salo18'][cell_rows[1]].style = 'm_subheader_style'
                else:
                    continue
                wb['salo18'][cell_rows[1]].border = no_border
                wb['salo18'][cell_rows[2]].style = m_unit_style
                wb['salo18'][cell_rows[2]].border = no_border
            for row in openpyxl.utils.cols_from_range('C1:C3'):
                for c in row:
                    wb['salo18'][c].border = l_border
            for row in openpyxl.utils.cols_from_range('H1:H3'):
                for c in row:
                    wb['salo18'][c].border = r_border

            # I. Isotopes d18O and dD
            max_row = wb['salo18'].max_row
            col_num = openpyxl.utils.column_index_from_string('I')
            d18O_ID = [wb['salo18'].cell(row=ii, column=col_num).value for ii in range(4, max_row)]
            col_num = openpyxl.utils.column_index_from_string('L')
            dD_ID = [wb['salo18'].cell(row=ii, column=col_num).value for ii in range(4, max_row)]
            if dD_ID == d18O_ID:
                # I.1.a unmerge cell
                wb['salo18'].unmerge_cells('I1:K1')  # d18O
                wb['salo18'].unmerge_cells('L1:N1')  # dD
                wb['salo18']['J1'].value = wb['salo18']['I1'].value
                wb['salo18']['I1'].value = None
                wb['salo18']['M1'].value = wb['salo18']['L1'].value
                wb['salo18']['L1'].value = None

                # I.1.b delete column K (d18O quality) and L (dD ID)
                wb['salo18'].delete_cols(openpyxl.utils.column_index_from_string('K'), 2)  # remove column K and L

                # I.1.c insert column after dD
                wb['salo18'].insert_cols(openpyxl.utils.column_index_from_string('L'), 1)
                wb['salo18']['L1'].value = 'd_excess'
                wb['salo18']['L2'].value = 'value'
                wb['salo18']['L3'].value = '‰'

                # I.2 formatting
                for cell_rows in openpyxl.utils.cols_from_range('I1:M3'):
                    wb['salo18'][cell_rows[0]].style = m_header_style
                    wb['salo18'][cell_rows[0]].border = no_border
                    wb['salo18'][cell_rows[1]].style = m_subheader_style
                    wb['salo18'][cell_rows[1]].style = 'm_subheader_style'
                    wb['salo18'][cell_rows[1]].border = no_border
                    wb['salo18'][cell_rows[2]].style = m_unit_style
                    wb['salo18'][cell_rows[2]].border = no_border
                for row in openpyxl.utils.cols_from_range('I1:I3'):
                    for c in row:
                        wb['salo18'][c].border = l_border
                for row in openpyxl.utils.cols_from_range('M1:M3'):
                    for c in row:
                        wb['salo18'][c].border = r_border

                for row in openpyxl.utils.cols_from_range('I'+str(max_row)+':M'+str(max_row)):
                    wb['salo18'][row[0]].style = m_bottom_style
            else:
                logger.info('%s\t\td18O ID different from dD ID: merging not possible' % wb['metadata-core']['C1'].value)

            # # 'eco'
            for merged_range in wb['eco'].merged_cells.ranges:
                # check if value is in merged range
                col_value = None
                # Perform different action for chl-a and phaeo columns (cf. below)
                if wb['eco'].cell(1, merged_range.min_col).value in ['chl-a', 'phaeo']:
                    continue

                # Check if value is present in merge, this indicate properties different of depth, field sample or comment
                for _col in range(merged_range.min_col, merged_range.max_col+1):
                    if wb['eco'].cell(2, _col).value == 'value':
                        col_value = _col
                        break
                if col_value is not None:
                    # 1. unmerge
                    merged_range_str = str(merged_range)
                    wb['eco'].unmerge_cells(str(merged_range))  # salinity
                    wb['eco'].cell(merged_range.min_row, col_value).value = wb['eco'].cell(merged_range.min_row, merged_range.min_col).value
                    wb['eco'].cell(merged_range.min_row, merged_range.min_col).value = None

                    # 2. formatting
                    for _col in range(merged_range.min_col, merged_range.max_col+1):
                        wb['eco'].cell(1, _col).style = m_header_style
                        wb['eco'].cell(1, _col).border = no_border
                        try:
                            wb['eco'].cell(2, _col).style = m_subheader_style
                        except ValueError:
                            wb['eco'].cell(2, _col).style = 'm_subheader_style'
                        else:
                            continue
                        wb['eco'].cell(2, _col).border = no_border
                        wb['eco'].cell(3, _col).style = m_unit_style
                        wb['eco'].cell(3, _col).border = no_border
                    for _col in [merged_range.min_col, merged_range.max_col+1]:
                        for _row in range(1, 4):
                            wb['eco'].cell(_row, _col).border = l_border

            # correct 'eco. data sampe' with 'eco. data sample'
            for _col in range(1, wb['eco'].max_column):
                if wb['eco'].cell(1, _col).value == 'eco. data sampe':
                    wb['eco'].cell(1, _col).value == 'eco. data sample'

            # chl-a and phaeo
            # Look for chl-a and phaeo merged columns
            col_chla_ID = None
            col_phaeo_ID = None
            for merged_range in wb['eco'].merged_cells.ranges:
                # look for chl-a and phaeo range
                if wb['eco'].cell(1, merged_range.min_col).value == 'chl-a':
                    range_chla = merged_range
                    # find the chl-a ID column
                    for _col in range(merged_range.min_col, merged_range.max_col + 1):
                        name = wb['eco'].cell(2, _col).value
                        if name == 'ID':
                            col_chla_ID = _col
                        elif name == 'value':
                            col_chla_value = _col
                        elif name == 'volume':
                            col_chla_vol = _col
                        elif name == 'quality':
                            col_chla_qual = _col
                elif wb['eco'].cell(1, merged_range.min_col).value == 'phaeo':
                    range_phaeo = merged_range
                    for _col in range(merged_range.min_col, merged_range.max_col + 1):
                        name = wb['eco'].cell(2, _col).value
                        if name == 'ID':
                            col_phaeo_ID = _col
                        elif name == 'value':
                            col_phaeo_value = _col
                        elif name == 'volume':
                            col_phaeo_vol = _col

            if col_chla_ID is not None and col_phaeo_ID is not None:
                max_row = wb['eco'].max_row
                dchla = [wb['eco'].cell(row=ii, column=col_chla_ID).value for ii in range(4, max_row)]
                dphaeo = [wb['eco'].cell(row=ii, column=col_phaeo_ID).value for ii in range(4, max_row)]
                if dchla == dphaeo:
                    # unmerge cell
                    wb['eco'].unmerge_cells(str(range_chla))  # chl-a
                    wb['eco'].unmerge_cells(str(range_phaeo))  # phaeo
                    wb['eco'].cell(1, col_chla_value).value = wb['eco'].cell(1, range_chla.min_col).value
                    wb['eco'].cell(1, range_chla.min_col).value = None
                    wb['eco'].cell(1, col_phaeo_value).value = wb['eco'].cell(1, range_phaeo.min_col).value
                    wb['eco'].cell(1, range_phaeo.min_col).value = None

                    # rename volume to "filtered volume"
                    # look for chl-a, volume:

                    wb['eco'].cell(2, col_chla_vol).value = 'filtered volume'

                    # delete column phaeo_vol, phao_ID and chla_quality:
                    wb['eco'].delete_cols(col_phaeo_vol, 1)
                    wb['eco'].delete_cols(col_phaeo_ID, 1)
                    wb['eco'].delete_cols(col_chla_qual, 1)

                    # formatting
                    for col in range(range_chla.min_col, range_chla.min_col+5):
                        wb['eco'].cell(1, col).style = m_header_style
                        wb['eco'].cell(1, col).border = no_border
                        wb['eco'].cell(2, col).style = m_subheader_style
                        wb['eco'].cell(2, col).border = no_border
                        wb['eco'].cell(3, col).style = m_unit_style
                        wb['eco'].cell(3, col).border = no_border
                        wb['eco'].cell(max_row, col).style = m_bottom_style
                    for col in [range_chla.min_col, range_chla.min_col + 5]:
                        for row in range(1, 4):
                            wb['eco'].cell(row, col).border = l_border
                else:
                    logger.info('%s\t\tchl-a ID different from phaeo ID: merging not possible' % wb['metadata-core']['C1'].value)
            elif col_chla_ID is None and col_phaeo_ID is None:
                logger.info('%s\t\t chl-a/phaeo sanple does not exists.' %
                            wb['metadata-core']['C1'].value)
            else:
                logger.info('%s\t\t no ID for both chl-a and phaeo ID: merging not possible' % wb['metadata-core']['C1'].value)

    if flag_update:
        ### Add an update is the spreadsheet
        # Find where version entries are located
        row = 1
        version_row = 0
        while version_row == 0 and row <= wb['metadata-core'].max_row:
            if wb['metadata-core'].cell(row, 1).value == 'VERSION' and wb['metadata-core'].cell(row + 1, 1).value == 'number':
                version_row = row
                break
            row += 1

        # Find line number with  latest version entries
        row = version_row + 2
        new_line = 0
        while new_line == 0 and row <= wb['metadata-core'].max_row:
            if wb['metadata-core'].cell(row, 1).value is None:
                new_line = row
            row += 1

        # Add new line afterwards
        wb['metadata-core'].insert_rows(new_line)
        wb['metadata-core'].cell(new_line, 1).value = wb['metadata-core'].cell(new_line-1, 1).value + 1
        wb['metadata-core'].cell(new_line, 2).value = dt.date.today().isoformat()
        wb['metadata-core'].cell(new_line, 3).value = user
        wb['metadata-core'].cell(new_line, 5).value = 'Updated ice core data from ' + version + ' to ' + __CoreVersion__

        # formatting:
        for col in range(9, wb['metadata-core'].max_column+1):
            wb['metadata-core'].cell(new_line, col).style = m_bottom_style
        logger.debug('%s\t\tupdate from from %s to %s' %(wb['metadata-core']['A1'].value, version, __CoreVersion__))
        wb['metadata-station']['C1'] = __CoreVersion__
        wb.save(ic_path)
        wb.close()
    else:
        logger.debug('%s\t\talready at latest (%s) version' % (wb['metadata-core']['A1'].value, __CoreVersion__))

def formatting(ic_path, backup=True):
    pass


###############
## Copy a sheet with style, format, layout, ect. from one Excel file to another Excel file
## Please add the ..path\\+\\file..  and  ..sheet_name.. according to your desire.

from copy import copy

def copy_sheet(source_sheet, target_sheet):
    """
    :param source_sheet:
    :param target_sheet:
    :return:
    """
    copy_cells(source_sheet, target_sheet)  # copy all the cel values and styles
    copy_sheet_attributes(source_sheet, target_sheet)


def copy_sheet_attributes(source_sheet, target_sheet):
    if isinstance(source_sheet, openpyxl.worksheet._read_only.ReadOnlyWorksheet):
        return
    target_sheet.sheet_format = copy(source_sheet.sheet_format)
    target_sheet.sheet_properties = copy(source_sheet.sheet_properties)
    target_sheet.merged_cells = copy(source_sheet.merged_cells)
    target_sheet.page_margins = copy(source_sheet.page_margins)
    target_sheet.freeze_panes = copy(source_sheet.freeze_panes)

     # set row dimensions
     # So you cannot copy the row_dimensions attribute. Does not work (because of meta data in the attribute I think). So we copy every row's row_dimensions. That seems to work.
    for rn in range(1, source_sheet.max_row):
#        target_sheet.row_dimensions[rn].height = copy(source_sheet.row_dimensions[rn].height)
        target_sheet.row_dimensions[rn] = source_sheet.row_dimensions[rn]

    if source_sheet.sheet_format.defaultColWidth is None:
        print('Unable to copy default column wide')
    else:
        target_sheet.sheet_format.defaultColWidth = copy(source_sheet.sheet_format.defaultColWidth)

    # set specific column width and hidden property
    # we cannot copy the entire column_dimensions attribute so we copy selected attributes
    for key, value in source_sheet.column_dimensions.items():
        target_sheet.column_dimensions[key].min = copy(source_sheet.column_dimensions[key].min)   # Excel actually groups multiple columns under 1 key. Use the min max attribute to also group the columns in the targetSheet
        target_sheet.column_dimensions[key].max = copy(source_sheet.column_dimensions[key].max)  # https://stackoverflow.com/questions/36417278/openpyxl-can-not-read-consecutive-hidden-columns discussed the issue. Note that this is also the case for the width, not onl;y the hidden property
        target_sheet.column_dimensions[key].width = copy(source_sheet.column_dimensions[key].width) # set width for every column
        target_sheet.column_dimensions[key].hidden = copy(source_sheet.column_dimensions[key].hidden)

def copy_cells(source_sheet, target_sheet):
    for r, row in enumerate(source_sheet.iter_rows()):
        for c, cell in enumerate(row):
            source_cell = cell
            # skip empty cell
            if isinstance(source_cell, openpyxl.cell.read_only.EmptyCell):
                continue
            target_cell = target_sheet.cell(column=c+1, row=r+1)
            target_cell._value = source_cell._value
            target_cell.data_type = source_cell.data_type

            if source_cell.has_style:
                target_cell.font = copy(source_cell.font)
                target_cell.border = copy(source_cell.border)
                target_cell.fill = copy(source_cell.fill)
                target_cell.number_format = copy(source_cell.number_format)
                target_cell.protection = copy(source_cell.protection)
                target_cell.alignment = copy(source_cell.alignment)

            if not isinstance(source_cell, openpyxl.cell.ReadOnlyCell) and source_cell.hyperlink:
                target_cell._hyperlink = copy(source_cell.hyperlink)

            if not isinstance(source_cell, openpyxl.cell.ReadOnlyCell) and source_cell.comment:
                target_cell.comment = copy(source_cell.comment)
