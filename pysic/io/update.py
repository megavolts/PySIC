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

m_bottom_style = NamedStyle(name="m_bottom_style")
m_bottom_style.fill = PatternFill(start_color="FFB2B2B2", end_color="FFBFBFBF", fill_type="solid")


def ice_core_data(ic_path, backup=True):
    """
    :param ic_path:
        path; Filepath to the data spreadsheet to update
    :param backup:
        boolean, default True; Make a backup copy in a subfolder
    """
    import shutil
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

    # Backup old version
    if backup:
        backup_dir = os.path.join(os.path.dirname(ic_path), 'bkp-ic_version_' + str(version))
        ic_bkp = os.path.join(backup_dir, os.path.basename(ic_path))
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        shutil.copy(ic_path, ic_bkp)

    while version_int[1] <= 4 and version_int[2] < version2int(__CoreVersion__)[2]:
        # Update to 1.4.5
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

        # Update to 1.4.6
        if version_int[2] < 6:
            version_int[2] = 6
            # 'salo18'
            max_row = wb['salo18'].max_row
            col_num = openpyxl.utils.column_index_from_string('I')
            d18O_ID = [wb['salo18'].cell(row=ii, column=col_num).value for ii in range(4,max_row)]
            col_num = openpyxl.utils.column_index_from_string('L')
            dD_ID = [wb['salo18'].cell(row=ii, column=col_num).value for ii in range(4,max_row)]
            if dD_ID == d18O_ID:
                # unmerge cell
                wb['salo18'].unmerge_cells('I1:K1')  # d18O
                wb['salo18'].unmerge_cells('L1:N1')  # dD
                wb['salo18']['J1'].value = wb['salo18']['I1'].value
                wb['salo18']['I1'].value = None
                wb['salo18']['M1'].value = wb['salo18']['L1'].value
                wb['salo18']['L1'].value = None

                # delete column K (d18O quality) and L (dD ID)
                wb['salo18'].delete_cols(openpyxl.utils.column_index_from_string('K'), 2)  # remove column K and L

                # insert column after dD
                wb['salo18'].insert_cols(openpyxl.utils.column_index_from_string('L'), 1)
                wb['salo18']['L1'].value = 'd_excess'
                wb['salo18']['L2'].value = 'value'
                wb['salo18']['L3'].value = '‰'

                # formatting
                for cell_rows in openpyxl.utils.cols_from_range('I1:M3'):
                    wb['salo18'][cell_rows[0]].style = m_header_style
                    wb['salo18'][cell_rows[0]].border = no_border
                    wb['salo18'][cell_rows[1]].style = m_subheader_style
                    wb['salo18'][cell_rows[1]].border = no_border
                    wb['salo18'][cell_rows[2]].style = m_unit_style
                    wb['salo18'][cell_rows[2]].border = no_border
                for row in openpyxl.utils.cols_from_range('I1:I3'):
                    for c in row:
                        wb['salo18'][c].border = l_border
                for row in openpyxl.utils.cols_from_range('N1:N3'):
                    for c in row:
                        wb['salo18'][c].border = l_border
                for row in openpyxl.utils.cols_from_range('I'+str(max_row)+':M'+str(max_row)):
                    wb['salo18'][row[0]].style = m_bottom_style
            else:
                logger.info('%s\t\td18O ID different from dD ID: merging not possible' % wb['metadata-core']['C1'].value)

            # 'eco'
            max_row = wb['eco'].max_row
            col_num = openpyxl.utils.column_index_from_string('I')
            dchla = [wb['eco'].cell(row=ii, column=col_num).value for ii in range(4, max_row)]
            col_num = openpyxl.utils.column_index_from_string('M')
            dphaeo = [wb['eco'].cell(row=ii, column=col_num).value for ii in range(4, max_row)]
            if dchla == dphaeo:
                # unmerge cell
                wb['eco'].unmerge_cells('I1:L1')  # chl-a
                wb['eco'].unmerge_cells('M1:P1')  # phaeo
                wb['eco']['K1'].value = wb['eco']['I1'].value
                wb['eco']['I1'].value = None
                wb['eco']['O1'].value = wb['eco']['M1'].value
                wb['eco']['M1'].value = None

                # rename volume to "filtered volume"
                wb['eco']['J2'].value = 'filtered volume'

                # delete column K (d18O quality) and L (dD ID)
                wb['eco'].delete_cols(openpyxl.utils.column_index_from_string('L'), 3)  # remove column K and L

                # formatting
                for cell_rows in openpyxl.utils.cols_from_range('I1:M3'):
                    wb['eco'][cell_rows[0]].style = m_header_style
                    wb['eco'][cell_rows[0]].border = no_border
                    wb['eco'][cell_rows[1]].style = m_subheader_style
                    wb['eco'][cell_rows[1]].border = no_border
                    wb['eco'][cell_rows[2]].style = m_unit_style
                    wb['eco'][cell_rows[2]].border = no_border
                for row in openpyxl.utils.cols_from_range('I1:I3'):
                    for c in row:
                        wb['eco'][c].border = l_border
                for row in openpyxl.utils.cols_from_range('N1:N3'):
                    for c in row:
                        wb['eco'][c].border = l_border
                # for row in openpyxl.utils.cols_from_range('H1:H3'):
                #     wb['eco'][row[0]].border = r_border
                # for row in openpyxl.utils.cols_from_range('M1:M3'):
                #     wb['eco'][row[0]].border = r_border
                for row in openpyxl.utils.cols_from_range('I'+str(max_row)+':M'+str(max_row)):
                    wb['eco'][row[0]].style = m_bottom_style
            else:
                logger.info('%s\t\td18O ID different from dD ID: merging not possible' % wb['metadata-core']['C1'].value)

    # useful to debug and avoid overriding

    # ic_path_test = ic_path.split('.xlsx')[0]+'-test.xlsx'
    # wb.save(ic_path_test)
    wb['metadata-station']['C1'] = __CoreVersion__
    wb.save(ic_path)
    wb.close()

    # while version_int[1] < 3 and version[2] == 0 :
    #     # backup old version
    #     if backup:
    #         backup_dir = os.path.join(os.path.dirname(ic_path), 'bkp-ic_version_' + str(version))
    #         ic_bkp = os.path.join(backup_dir, os.path.basename(ic_path))
    #
    #         if not os.path.exists(backup_dir):
    #             os.makedirs(backup_dir)
    #         shutil.move(ic_path, ic_bkp)
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


def all_style(ic_path, backup=True):
    pass