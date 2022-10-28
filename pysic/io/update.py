#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    pysic.io.update.py : function to update ice core spreadsheet
"""

from pysic.core.core import __CoreVersion__
import logging
import os
import openpyxl
import numpy
import openpyxl as opxl

from openpyxl.styles import NamedStyle, Font, Alignment, PatternFill
from openpyxl.styles.borders import Border, Side

from pysic.tools import version2int
from pysic.property import prop_associated_tab

import pysic
pysic_fp = pysic.__path__[0]

#ic_path = '/home/megavolts/git/pysic/pysic/ressources/AAA_BB-YYYYXXZZ-N_P-1.4.6.xlsx'


data_row_n = 42

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
# bottom right border
br_border = Border(left=Side(border_style=None), right=Side(border_style='hair', color='00000000'),
                  top=Side(border_style=None), bottom=Side(border_style='hair', color='00000000'))
# no_border
no_border = Border(left=Side(border_style=None), right=Side(border_style=None),
                   top=Side(border_style=None), bottom=Side(border_style=None))
noBorder=no_border
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

m_unit_l_style = NamedStyle(name="m_unit_l_style")
m_unit_l_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=True, color='FF000000')
m_unit_l_style.alignment = Alignment(horizontal='left', wrapText=True, vertical='center')
m_unit_l_style.fill = PatternFill(start_color="FFDDDDDD", end_color="FFE0E0E0", fill_type="solid")

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

light_grey = "FFCCCCCC"
mid_grey = "FFDDDDDD"
dark_grey = "FFB2B2B2"
white = "ffFFFFFF"
noFill = PatternFill(fill_type=None)

# data right: black font, right aligned, white/no background
m_data_style = NamedStyle(name="m_data_style")
m_data_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=False, color='FF000000')  # black
m_data_style.alignment = Alignment(horizontal='right', wrapText=True, vertical='center')
#m_data_style.fill = PatternFill(fgColor=white, bgColor=white, fill_type="solid")
m_data_style.fill = PatternFill(fill_type=None)

# data entry style, left aligned: black font, left alignment, white/no background
m_data_l_style = NamedStyle(name="m_data_l_style")
m_data_l_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=False, color='FF000000')  # black
m_data_l_style.alignment = Alignment(horizontal='left', wrapText=True, vertical='center')
#m_data_l_style.fill = PatternFill(fgColor=white, bgColor=white, fill_type="solid")
m_data_l_style.fill = PatternFill(fill_type=None)

# background style: dark grey
m_bkg_style = NamedStyle(name="m_bkg_style")
m_bkg_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=False, color='FF000000')
m_bkg_style.alignment = Alignment(horizontal='left', wrapText=False, vertical='center')
m_bkg_style.fill = PatternFill(start_color=dark_grey, end_color=dark_grey, fill_type="solid")
m_bottom_style = m_bkg_style

# subheader right: black font, right aligned, light grey background
m_subheader_r_style = NamedStyle(name="m_subheader_r_style")
m_subheader_r_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=False, color='FF000000')
m_subheader_r_style.alignment = Alignment(horizontal='right', wrapText=True, vertical='center')
m_subheader_r_style.fill = PatternFill(start_color=mid_grey, end_color=mid_grey, fill_type="solid")

# subheader left: black font, left aligned, light grey background
m_subheader_l_style = NamedStyle(name="m_subheader_l_style")
m_subheader_l_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False, italic=False, color='FF000000')
m_subheader_l_style.alignment = Alignment(horizontal='left', wrapText=True, vertical='center')
m_subheader_l_style.fill = PatternFill(start_color=mid_grey, end_color=mid_grey, fill_type="solid")

# header right: black bold font, right aligned, light grey background
m_header_r_style = NamedStyle(name="m_header_r_style")
m_header_r_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=True, italic=False, color='FF000000')
m_header_r_style.alignment = Alignment(horizontal='right', wrapText=False, vertical='center')
m_header_r_style.fill = PatternFill(start_color=mid_grey, end_color=mid_grey, fill_type="solid")

# header left: black bold font, left aligned, light grey background
m_header_l_style = NamedStyle(name="m_header_l_style")
m_header_l_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=True, italic=False, color='FF000000')
m_header_l_style.alignment = Alignment(horizontal='left', wrapText=False, vertical='center')
m_header_l_style.fill = PatternFill(start_color=mid_grey, end_color=mid_grey, fill_type="solid")

# header title: black bold font, left aligned, dark grey background
m_header_title_style = NamedStyle(name="m_header_title_style")
m_header_title_style.font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=True, italic=False, color='FF000000')
m_header_title_style.alignment = Alignment(horizontal='left', wrapText=False, vertical='center')
m_header_title_style.fill = PatternFill(start_color=dark_grey, end_color=dark_grey, fill_type="solid")

# Data validation
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import quote_sheetname

vert_ref_list = DataValidation(type="list", formula1='"ice surface, ice/water interface, snow surface, water level"')
vert_dir_list = DataValidation(type="list", formula1='"up, down"')

texture_dv = DataValidation(type="list", formula1='{0}!$F$3:$F$27'.format(quote_sheetname('lists')), allow_blank=True)
inclusion_dv = DataValidation(type="list", formula1='{0}!$G$3:$G$27'.format(quote_sheetname('lists')), allow_blank=True)
description_dv = DataValidation(type="list", formula1='{0}!$H$3:$H$27'.format(quote_sheetname('lists')), allow_blank=True)

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
    if 'metadata-coring' in wb.sheetnames:
        ws_summary = wb['metadata-coring']  # load the data from the summary sheet
    else:
        ws_summary = wb['metadata-station']  # load the data from the summary sheet
    version = ws_summary['C1'].value
    version_int = version2int(version)

    flag_update = False
    if version_int[1] <= 4 and version_int[2] < 1:
        logger.error('%s\t\tversion update from %s not supported' % (wb['metadata-core']['C1'].value, str(version)))

    if not flag_update:
        flag_update = True
        # Backup old version
        if backup:
            backup_dir = os.path.join(os.path.dirname(ic_path), 'bkp-ic_version_' + str(version))
            ic_bkp = os.path.join(backup_dir, os.path.basename(ic_path))
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            if not os.path.exists(ic_bkp):
                shutil.copy(ic_path, ic_bkp)
                logger.info('%s\t\tsaving backup version to %s' % (wb['metadata-core']['C1'].value, backup_dir))

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
    if version_int[1] < 2:
        version_1_3_0_to_1_4_1(wb)
        version_int[1] = 4
        version_int[2] = 1

    # Update to 1.4.1 to 1.4.2
    if version_int[2] < 2:
        version_1_4_1_to_1_4_2(wb)
        version_int[2] = 2

    # Update to 1.4.2 to 1.4.3
    if version_int[2] < 3:
        # In 'metadata-station' add entry for seawater salinity below seawater temperature
        for merged_cell in wb['metadata-station'].merged_cells.ranges:
            if merged_cell.right[0][0] > 33:
                merged_cell.shift(0, 1)
        wb['metadata-station'].insert_rows(33, 1)
        wb['metadata-station']['A33'].value = 'water salinity'
        wb['metadata-station']['B33'].value = 'PSU'
        wb['metadata-station']['D33'].value = 'under ice'
        wb['metadata-station']['D32'].value = 'under ice'

        # Update "wind orientation' to 'wind direction'
        wb['metadata-station']['A43'].value = 'wind direction'

        # Formatting
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
        wb_source = openpyxl.load_workbook(os.path.join(pysic_fp, 'ressources/AAA_BB-YYYYMMDD-P-1.4.3-sackhole_tab.xlsx'), data_only=True)
        copy_cells(wb_source['sackhole'], wb['sackhole'])  # copy all the cel values and styles
        copy_sheet_attributes(wb_source['sackhole'], wb['sackhole'])
        wb['metadata-station']['C1'].value = '1.4.3'
        version_int[2] = 3

    # Update from 1.4.3 to  1.4.4 ## does not exist
    if version_int[2] < 4:
        # Add trace metal core sheet
        TM_sheet_idx = wb._sheets.index(wb['snow'])
        wb.create_sheet("TM", TM_sheet_idx)
        wb_source = openpyxl.load_workbook(os.path.join(pysic_fp, 'ressources/AAA_BB-YYYYXXZZ-N_P-1.4.4-TM_sheet.xlsx'), data_only=True)
        copy_cells(wb_source['TM'], wb['TM'])  # copy all the cel values and styles
        copy_sheet_attributes(wb_source['TM'], wb['TM'])

        # ECO
        # Add nutrient, DNA, chl-a
        flag_m = {'nutrient': 0, 'DNA': 0, 'chl-a': 0}
        for cell in openpyxl.utils.cols_from_range('A1:' + openpyxl.utils.get_column_letter(wb['eco'].max_column) + str(1)):
            if wb['eco'][cell[0]].value is not None:
                for key in flag_m.keys():
                    if key in wb['eco'][cell[0]].value:
                        flag_m[key] = 1

        for key in flag_m.keys():
            if flag_m[key] == 0:
                for cell in openpyxl.utils.cols_from_range(
                        'A1:' + openpyxl.utils.get_column_letter(wb['eco'].max_column) + str(1)):
                    if wb['eco'][cell[0]].value == 'comment':
                        break

                col_start = openpyxl.utils.coordinate_to_tuple(cell[0])[1]
                for merged_cell in wb['eco'].merged_cells.ranges:
                    if merged_cell.left[0][1] >= col_start:
                        merged_cell.shift(3, 0)
                wb['eco'].insert_cols(col_start, 3)
                new_merge = openpyxl.utils.get_column_letter(col_start) + '1:' + openpyxl.utils.get_column_letter(
                    col_start + 2) + '1'
                wb['eco'].merge_cells(new_merge)
                wb['eco'].cell(1, col_start).value = key
                wb['eco'].cell(2, col_start).value = 'ID'
                wb['eco'].cell(2, col_start + 1).value = 'value'
                wb['eco'].cell(2, col_start + 2).value = 'quality'
                wb['eco'].cell(3, col_start).value = '-'
                wb['eco'].cell(3, col_start + 1).value = '-'
                wb['eco'].cell(3, col_start + 2).value = '[0-9]'

                # formatting
                for col in range(col_start, col_start + 3):
                    wb['eco'].cell(1, col).style = m_header_style
                    wb['eco'].cell(1, col).border = no_border
                    wb['eco'].cell(2, col).style = m_subheader_style
                    wb['eco'].cell(2, col).border = no_border
                    wb['eco'].cell(3, col).style = m_unit_style
                    wb['eco'].cell(3, col).border = no_border
                    wb['eco'].cell(wb['eco'].max_row, col).style = m_bottom_style
                for col in [col_start, col_start + 3]:
                    for row in range(1, wb['eco'].max_row):
                        wb['eco'].cell(row, col).border = l_border
            else:
                logging.error('%s NOT IMPLEMENTED YET' % key)

        # SNOW
        sheetname = 'snow'
        # if density is not merge on 3 column, merge it
        for cell in openpyxl.utils.cols_from_range(
                'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
            if wb[sheetname][cell[0]].value == 'density':
                break
        col_idx = openpyxl.utils.coordinate_to_tuple(cell[0])[1]
        if wb[sheetname].cell(2, col_idx+2).value == 'quality':
            if cell[0] in wb[sheetname].merged_cells:
                # lookup the cell range:
                for merged_cell in wb[sheetname].merged_cells:
                    if cell[0] in merged_cell:
                        break
                if merged_cell.right[0][1] < col_idx + 2:
                    wb[sheetname].unmerge_cells(merged_cell.coord)
                    new_range = openpyxl.utils.get_column_letter(
                        col_idx) + '1:' + openpyxl.utils.get_column_letter(
                        col_idx + 2) + '1'
                    wb[sheetname].merge_cells(new_range)
                    # formatting
                    wb[sheetname].cell(1, col_idx).style = m_header_style
                    wb[sheetname].cell(1, col_idx).border = no_border
                    wb[sheetname].cell(1, col_idx).border = l_border
                    wb[sheetname].cell(1, col_idx+3).border = l_border

        # Add TM, TM Ligand
        flag_m = {'TM': 0, 'TM Ligand': 0}
        for cell in openpyxl.utils.cols_from_range('A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
            if wb[sheetname][cell[0]].value is not None:
                for key in flag_m.keys():
                    if key in wb[sheetname][cell[0]].value:
                        flag_m[key] = 1

        for key in flag_m.keys():
            if flag_m[key] == 0:
                for cell in openpyxl.utils.cols_from_range(
                        'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                    if wb[sheetname][cell[0]].value == 'comment':
                        break

                col_start = openpyxl.utils.coordinate_to_tuple(cell[0])[1]
                for merged_cell in wb[sheetname].merged_cells.ranges:
                    if merged_cell.left[0][1] >= col_start:
                        merged_cell.shift(3, 0)
                wb[sheetname].insert_cols(col_start, 3)
                new_merge = openpyxl.utils.get_column_letter(col_start) + '1:' + openpyxl.utils.get_column_letter(
                    col_start + 2) + '1'
                wb[sheetname].merge_cells(new_merge)
                wb[sheetname].cell(1, col_start).value = key
                wb[sheetname].cell(2, col_start).value = 'ID'
                wb[sheetname].cell(2, col_start + 1).value = 'value'
                wb[sheetname].cell(2, col_start + 2).value = 'quality'
                wb[sheetname].cell(3, col_start).value = '-'
                wb[sheetname].cell(3, col_start + 1).value = '-'
                wb[sheetname].cell(3, col_start + 2).value = '[0-9]'

                # formatting
                for col in range(col_start, col_start + 3):
                    wb[sheetname].cell(1, col).style = m_header_style
                    wb[sheetname].cell(1, col).border = no_border
                    wb[sheetname].cell(2, col).style = m_subheader_style
                    wb[sheetname].cell(2, col).border = no_border
                    wb[sheetname].cell(3, col).style = m_unit_style
                    wb[sheetname].cell(3, col).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style
                for col in [col_start, col_start + 3]:
                    for row in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row, col).border = l_border
            else:
                logging.error('%s NOT IMPLEMENTED YET' % key)

        # SACKHOLE
        sheetname = 'sackhole'
        header_after = 'nutrient'

        # add d18O and dD in front of nutrient
        flag_m = {'d18O': 0, 'dD': 0}
        for cell in openpyxl.utils.cols_from_range('A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
            if wb[sheetname][cell[0]].value is not None:
                for key in flag_m.keys():
                    if key in wb[sheetname][cell[0]].value:
                        flag_m[key] = 1

        for key in flag_m.keys():
            if flag_m[key] == 0:
                for cell in openpyxl.utils.cols_from_range(
                        'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                    if wb[sheetname][cell[0]].value == header_after:
                        break

                col_start = openpyxl.utils.coordinate_to_tuple(cell[0])[1]
                for merged_cell in wb[sheetname].merged_cells.ranges:
                    if merged_cell.left[0][1] >= col_start:
                        merged_cell.shift(3, 0)
                wb[sheetname].insert_cols(col_start, 3)
                new_merge = openpyxl.utils.get_column_letter(col_start) + '1:' + openpyxl.utils.get_column_letter(
                    col_start + 2) + '1'
                wb[sheetname].merge_cells(new_merge)
                wb[sheetname].cell(1, col_start).value = key
                wb[sheetname].cell(2, col_start).value = 'ID'
                wb[sheetname].cell(2, col_start + 1).value = 'value'
                wb[sheetname].cell(2, col_start + 2).value = 'quality'
                wb[sheetname].cell(3, col_start).value = '-'
                wb[sheetname].cell(3, col_start + 1).value = '-'
                wb[sheetname].cell(3, col_start + 2).value = '[0-9]'

                # formatting
                for col in range(col_start, col_start + 3):
                    wb[sheetname].cell(1, col).style = m_header_style
                    wb[sheetname].cell(1, col).border = no_border
                    wb[sheetname].cell(2, col).style = m_subheader_style
                    wb[sheetname].cell(2, col).border = no_border
                    wb[sheetname].cell(3, col).style = m_unit_style
                    wb[sheetname].cell(3, col).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style
                for col in [col_start, col_start + 3]:
                    for row in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row, col).border = l_border
            else:
                logging.error('%s NOT IMPLEMENTED YET' % key)

        # add TM, TM Ligand in front of comment
        flag_m = {'TM': 0, 'TM Ligand': 0}
        header_after = 'comment'

        for cell in openpyxl.utils.cols_from_range('A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
            if wb[sheetname][cell[0]].value is not None:
                for key in flag_m.keys():
                    if key in wb[sheetname][cell[0]].value:
                        flag_m[key] = 1
        for key in flag_m.keys():
            if flag_m[key] == 0:
                for cell in openpyxl.utils.cols_from_range(
                        'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                    if wb[sheetname][cell[0]].value == header_after:
                        break

                col_start = openpyxl.utils.coordinate_to_tuple(cell[0])[1]
                for merged_cell in wb[sheetname].merged_cells.ranges:
                    if merged_cell.left[0][1] >= col_start:
                        merged_cell.shift(3, 0)
                wb[sheetname].insert_cols(col_start, 3)
                new_merge = openpyxl.utils.get_column_letter(col_start) + '1:' + openpyxl.utils.get_column_letter(
                    col_start + 2) + '1'
                wb[sheetname].merge_cells(new_merge)
                wb[sheetname].cell(1, col_start).value = key
                wb[sheetname].cell(2, col_start).value = 'ID'
                wb[sheetname].cell(2, col_start + 1).value = 'value'
                wb[sheetname].cell(2, col_start + 2).value = 'quality'
                wb[sheetname].cell(3, col_start).value = '-'
                wb[sheetname].cell(3, col_start + 1).value = '-'
                wb[sheetname].cell(3, col_start + 2).value = '[0-9]'

                # formatting
                for col in range(col_start, col_start + 3):
                    wb[sheetname].cell(1, col).style = m_header_style
                    wb[sheetname].cell(1, col).border = no_border
                    wb[sheetname].cell(2, col).style = m_subheader_style
                    wb[sheetname].cell(2, col).border = no_border
                    wb[sheetname].cell(3, col).style = m_unit_style
                    wb[sheetname].cell(3, col).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style
                for col in [col_start, col_start + 3]:
                    for row in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row, col).border = l_border
            else:
                logging.error('%s NOT IMPLEMENTED YET' % key)

        # DENSITY-VOLUME
        sheetname = 'density-volume'
        flag_m = {'diameter': 0}
        header_after = 'mass'
        for cell in openpyxl.utils.cols_from_range('A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
            if wb[sheetname][cell[0]].value is not None:
                for key in flag_m.keys():
                    if key in wb[sheetname][cell[0]].value:
                        flag_m[key] = 1

        for key in flag_m.keys():
            if flag_m[key] == 0:
                col_number = 3
                for cell in openpyxl.utils.cols_from_range(
                        'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                    if wb[sheetname][cell[0]].value == header_after:
                        break

                col_start = openpyxl.utils.coordinate_to_tuple(cell[0])[1]
                for merged_cell in wb[sheetname].merged_cells.ranges:
                    if merged_cell.left[0][1] >= col_start:
                        merged_cell.shift(col_number, 0)
                wb[sheetname].insert_cols(col_start, col_number)
                new_merge = openpyxl.utils.get_column_letter(col_start) + '1:' + openpyxl.utils.get_column_letter(
                    col_start + col_number - 1) + '1'
                wb[sheetname].merge_cells(new_merge)

                #  Add diameter measurement in density-volume sheet:
                wb[sheetname].cell(1, col_start).value = 'diameter'
                wb[sheetname].cell(2, col_start).value = 'value1'
                wb[sheetname].cell(2, col_start + 1).value = 'value2'
                wb[sheetname].cell(2, col_start + 2).value = 'average'
                wb[sheetname].cell(3, col_start).value = 'm'
                wb[sheetname].cell(3, col_start + 1).value = 'm'
                wb[sheetname].cell(3, col_start + 2).value = 'm'

                # Formatting
                for col in range(col_start, col_start + 3):
                    wb[sheetname].cell(1, col).style = m_header_style
                    wb[sheetname].cell(1, col).border = no_border
                    wb[sheetname].cell(2, col).style = m_subheader_style
                    wb[sheetname].cell(2, col).border = no_border
                    wb[sheetname].cell(3, col).style = m_unit_style
                    wb[sheetname].cell(3, col).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style
                for col in [col_start, col_start+3]:
                    for row in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row, col).border = l_border

        # SEAWATER
        # add nutrient, TM, TM_Ligand in front of comment
        sheetname = 'seawater'
        flag_m = {'nutrient': 0, 'TM': 0, 'TM Ligand': 0}
        header_after = 'comment'

        for cell in openpyxl.utils.cols_from_range('A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
            if wb[sheetname][cell[0]].value is not None:
                for key in flag_m.keys():
                    if key in wb[sheetname][cell[0]].value:
                        flag_m[key] = 1
        for key in flag_m.keys():
            if flag_m[key] == 0:
                for cell in openpyxl.utils.cols_from_range(
                        'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                    if wb[sheetname][cell[0]].value == header_after:
                        break

                col_start = openpyxl.utils.coordinate_to_tuple(cell[0])[1]
                for merged_cell in wb[sheetname].merged_cells.ranges:
                    if merged_cell.left[0][1] >= col_start:
                        merged_cell.shift(3, 0)
                wb[sheetname].insert_cols(col_start, 3)
                new_merge = openpyxl.utils.get_column_letter(col_start) + '1:' + openpyxl.utils.get_column_letter(
                    col_start + 2) + '1'
                wb[sheetname].merge_cells(new_merge)
                wb[sheetname].cell(1, col_start).value = key
                wb[sheetname].cell(2, col_start).value = 'ID'
                wb[sheetname].cell(2, col_start + 1).value = 'value'
                wb[sheetname].cell(2, col_start + 2).value = 'quality'
                wb[sheetname].cell(3, col_start).value = '-'
                wb[sheetname].cell(3, col_start + 1).value = '-'
                wb[sheetname].cell(3, col_start + 2).value = '[0-9]'

                # formatting
                for col in range(col_start, col_start + 3):
                    wb[sheetname].cell(1, col).style = m_header_style
                    wb[sheetname].cell(1, col).border = no_border
                    wb[sheetname].cell(2, col).style = m_subheader_style
                    wb[sheetname].cell(2, col).border = no_border
                    wb[sheetname].cell(3, col).style = m_unit_style
                    wb[sheetname].cell(3, col).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style

                for col in [col_start, col_start + 3]:
                    for row in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row, col).border = l_border
            else:
                logging.error('%s NOT IMPLEMENTED YET' % key)
        del flag_m, col_start, col_number, col_idx

    # Update from 1.4.4 to 1.4.5
    if version_int[2] < 5:
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
        version_int[2] = 5

    # Update to 1.4.6
    if version_int[2] < 6:
        # METADATA-CORE
        # Formatting
        wb['metadata-core']['D1'].style = m_bkg_style  # repaint unmerged cell
        wb['metadata-core']['D2'] = None
        wb['metadata-core']['D2'].style = m_bkg_style  # repaint unmerged cell

        #  Cleaning
        # TODO: move to pysic.io.clean_spreadsheet
        # adding empty row before VERSION if instruments overlap
        row_w = 21
        while wb['metadata-core'].cell(row_w, 1).value != 'VERSION' and row_w <= wb['metadata-core'].max_row:
            row_w += 1
        if row_w == wb['metadata-core'].max_row:
            logging.error('REACHED END OF ROWS')
        row_insert_idx = row_w
        if wb['metadata-core'].cell(row_w-1, 1).value != None:
            for merged_cell in wb['metadata-core'].merged_cells.ranges:
                if merged_cell.right[0][0] >= row_insert_idx:
                    merged_cell.shift(0, 1)
            wb['metadata-core'].insert_rows(row_insert_idx, 1)
        # formatting
        for row_w in range(21, row_insert_idx):
            for col in range(1, 3):
                wb['metadata-core'].cell(row, 1).style = m_subheader_style
            new_range = 'C' + str(row_w) +':H' +str(row_w)
            wb['metadata-core'].merge_cells(new_range)
            wb['metadata-core'].cell(row, 1).style = m_comment_style_coring
            wb['metadata-core'].cell(row, 1).border = b_border
        wb['metadata-core'].cell(row, 1).border = no_border  # no bottom border on the last line

        # CLEANING VERSION NUMBER
        sheetname = 'metadata-core'
        # Find where 'VERSION' entries are located
        row = 1
        version_row = 0
        while version_row == 0 and row <= wb['metadata-core'].max_row:
            if wb['metadata-core'].cell(row, 1).value == 'VERSION' and wb['metadata-core'].cell(row + 1, 1).value == 'number':
                version_row = row
                break
            row += 1

        # Find line number with first version entries
        row = version_row + 2
        first_entry = row
        last_entry = 0
        while last_entry == 0 and row <= wb['metadata-core'].max_row:
            if wb['metadata-core'].cell(row, 1).value is None:
                last_entry = row - 1
            row += 1

        # check incremental number (col 0)
        incremental_number = []
        incremental_error = []
        date = []
        author = []
        modification = []
        for row_idx in range(first_entry, last_entry + 1):
            incremental_number += [int(wb[sheetname].cell(row_idx, 1).value)]
            date += [wb[sheetname].cell(row_idx, 2).value]
            _author = wb[sheetname].cell(row_idx, 3).value
            if _author is None and 'PS122' in wb['metadata-core']['C1'].value:
                _author = 'Marc Oggier'
            author += [_author]
            modification += [wb[sheetname].cell(row_idx, 5).value]
            if row_idx > int(first_entry) and incremental_number[-1] <= incremental_number[-2]:
                incremental_error += [row_idx]

        if len(incremental_error) > 0:
            if 'Initial data entry' in modification:
                if modification.index('Initial data entry') > 0 and len(incremental_number)<3:
                    # inverse row in incremental version
                    wb[sheetname].cell(first_entry, 2).value = date[1]
                    wb[sheetname].cell(first_entry, 3).value = author[1]
                    wb[sheetname].cell(first_entry, 5).value = modification[1]
                    wb[sheetname].cell(last_entry, 1).value = 2
                    wb[sheetname].cell(last_entry, 2).value = date[0]
                    wb[sheetname].cell(last_entry, 3).value = author[0]
                    wb[sheetname].cell(last_entry, 5).value = modification[0]
                else:
                    logging.error('%s - %s: error in incremental version' % (wb['metadata-core']['C1'].value, sheetname))
        # METADATA-STATION
        # rename water temperature to seawater temperature
        wb['metadata-station']['E45'].value = '2pi sensor'
        wb['metadata-station']['E46'].value = '4pi sensor'

        # 'SALO18'
        sheetname = 'salo18'

        # Unmerge header cell
        merged_cells = list(wb[sheetname].merged_cells)
        for merge_cell in merged_cells:
            if merge_cell.start_cell.row == 1:
                col_start = merge_cell.left[0][1]
                col_end = merge_cell.right[0][1]

                # unmerged cell
                header = merge_cell.start_cell.value
                wb[sheetname].unmerge_cells(merge_cell.coord)

                # find header
                value_idx = None
                id_idx = None
                for col_idx in range(col_start, col_end + 1):
                    if wb[sheetname].cell(2, col_idx).value == 'value':
                        value_idx = col_idx
                        # remember ID for d18O and dD
                        if header == 'd18O':
                            d18O_value_idx = col_idx
                        elif header == 'dD':
                            dD_value_idx = col_idx
                    elif wb[sheetname].cell(2, col_idx).value == 'ID':
                        id_idx = col_idx
                        # remember ID for d18O and dD
                        if header == 'd18O':
                            d18O_id_idx = col_idx
                        elif header == 'dD':
                            dD_id_idx = col_idx
                    elif wb[sheetname].cell(2, col_idx).value == 'quality':
                        id_idx = col_idx
                        # remember ID for d18O and dD
                        if header == 'd18O':
                            d18O_qual_idx = col_idx
                        elif header == 'dD':
                            dD_qual_idx = col_idx
                if value_idx is not None:
                    wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                    wb[sheetname].cell(1, value_idx).value = header
                elif value_idx is not None:
                    wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                    wb[sheetname].cell(1, id_idx).value = header

                # formatting
                for col_idx in range(col_start, col_end + 1):
                    wb[sheetname].cell(1, col_idx).style = m_header_style
                    wb[sheetname].cell(1, col_idx).border = no_border
                    wb[sheetname].cell(2, col_idx).style = m_subheader_style
                    wb[sheetname].cell(2, col_idx).border = no_border
                    wb[sheetname].cell(3, col_idx).style = m_unit_style
                    wb[sheetname].cell(3, col_idx).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                if header in ['conductivity', 'dD']:
                    pass
                elif header in ['d_excess', 'phaeo']:
                    for col in [col_end + 2]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border
                elif header in ['specific conductance']:
                    for col in [col_end + 1]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border
                elif header in ['salinity']:
                    for col in [col_start]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border
                else:
                    for col in [col_start, col_end + 1]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border

        # S2. Reorganize d18O, dD colums and add d_excess
        max_row = wb['salo18'].max_row

        # Check if d18O_ID match dD_ID:
        d18O_ID = [wb[sheetname].cell(row=ii, column=d18O_id_idx).value for ii in range(4, max_row)]
        dD_ID = [wb[sheetname].cell(row=ii, column=dD_id_idx).value for ii in range(4, max_row)]
        d18O_qual = [wb[sheetname].cell(row=ii, column=d18O_qual_idx).value for ii in range(4, max_row)]
        dD_qual = [wb[sheetname].cell(row=ii, column=dD_qual_idx).value for ii in range(4, max_row)]

        if dD_ID == d18O_ID:
            # Insert d_excess column after dD:
            wb[sheetname].insert_cols(dD_value_idx + 1, 1)
            wb[sheetname].cell(1, dD_value_idx + 1).value = 'd_excess'
            wb[sheetname].cell(2, dD_value_idx + 1).value = 'value'
            wb[sheetname].cell(3, dD_value_idx + 1).value = '‰'
            wb[sheetname].cell(1, dD_value_idx + 1).style = m_header_style
            wb[sheetname].cell(1, dD_value_idx + 1).border = no_border
            wb[sheetname].cell(2, dD_value_idx + 1).style = m_subheader_style
            # wb[sheetname].cell(2, dD_value_idx + 1).style = 'm_subheader_style'
            wb[sheetname].cell(2, dD_value_idx + 1).border = no_border
            wb[sheetname].cell(3, dD_value_idx + 1).style = m_unit_style
            wb[sheetname].cell(3, dD_value_idx + 1).border = no_border
            wb[sheetname].cell(max_row, dD_value_idx + 1).style = m_bottom_style

            # remove colum of dD_IDy
            wb[sheetname].delete_cols(dD_id_idx, 1)

            if d18O_qual != dD_qual:
                logging.error('NOT IMPLEMENTED: d18O_qual != dD_qual')
            else:
                # remove colum for d18O_qual
                wb[sheetname].delete_cols(d18O_qual_idx, 1)
        else:
            logger.info('%s\t\td18O ID different from dD ID: merging not possible' % wb['metadata-core']['C1'].value)

        # TEMP
        sheetname = 'temp'
        merged_cells = list(wb[sheetname].merged_cells)
        for merge_cell in merged_cells:
            if merge_cell.start_cell.row == 1:
                col_start = merge_cell.left[0][1]
                col_end = merge_cell.right[0][1]

                # unmerged cell
                header = merge_cell.start_cell.value
                wb[sheetname].unmerge_cells(merge_cell.coord)

                # find header
                value_idx = None
                id_idx = None
                for col_idx in range(col_start, col_end + 1):
                    if wb[sheetname].cell(2, col_idx).value == 'value':
                        value_idx = col_idx
                    elif wb[sheetname].cell(2, col_idx).value == 'ID':
                        id_idx = col_idx
                if value_idx is not None:
                    wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                    wb[sheetname].cell(1, value_idx).value = header
                elif value_idx is not None:
                    wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                    wb[sheetname].cell(1, id_idx).value = header

                # formatting
                for col_idx in range(col_start, col_end + 1):
                    wb[sheetname].cell(1, col_idx).style = m_header_style
                    wb[sheetname].cell(1, col_idx).border = no_border
                    wb[sheetname].cell(2, col_idx).style = m_subheader_style
                    wb[sheetname].cell(2, col_idx).border = no_border
                    wb[sheetname].cell(3, col_idx).style = m_unit_style
                    wb[sheetname].cell(3, col_idx).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                for col in [col_start, col_end + 1]:
                    for row in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row, col).border = l_border

        # TEX:
        sheetname = 'tex'
        merged_cells = list(wb[sheetname].merged_cells)
        for merge_cell in merged_cells:
            if merge_cell.start_cell.row == 1:
                col_start = merge_cell.left[0][1]
                col_end = merge_cell.right[0][1]

                # unmerged cell
                header = merge_cell.start_cell.value
                wb[sheetname].unmerge_cells(merge_cell.coord)

                # find header
                value_idx = None
                id_idx = None
                for col_idx in range(col_start, col_end + 1):
                    if wb[sheetname].cell(2, col_idx).value == 'value':
                        value_idx = col_idx
                    elif wb[sheetname].cell(2, col_idx).value == 'ID':
                        id_idx = col_idx
                if value_idx is not None:
                    wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                    wb[sheetname].cell(1, value_idx).value = header
                elif value_idx is not None:
                    wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                    wb[sheetname].cell(1, id_idx).value = header

                # formatting
                for col_idx in range(col_start, col_end + 1):
                    wb[sheetname].cell(1, col_idx).style = m_header_style
                    wb[sheetname].cell(1, col_idx).border = no_border
                    wb[sheetname].cell(2, col_idx).style = m_subheader_style
                    wb[sheetname].cell(2, col_idx).border = no_border
                    wb[sheetname].cell(3, col_idx).style = m_unit_style
                    wb[sheetname].cell(3, col_idx).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                if header not in ['texture']:
                    for col in [col_start]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border
                else:
                    for col in [col_start, col_end + 1]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border

        # Add `core section` column before the `comment` column:
        flag_m = {'Core': 0}
        header_after = 'comment'
        col_number = 1
        for cell in openpyxl.utils.cols_from_range('A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
            if wb[sheetname][cell[0]].value is not None:
                for key in flag_m.keys():
                    if key in wb[sheetname][cell[0]].value:
                        flag_m[key] = 1
        for key in flag_m.keys():
            if flag_m[key] == 0:
                for cell in openpyxl.utils.cols_from_range(
                        'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                    if wb[sheetname][cell[0]].value == header_after:
                        break

                col_start = openpyxl.utils.coordinate_to_tuple(cell[0])[1]
                for merged_cell in wb[sheetname].merged_cells.ranges:
                    if merged_cell.left[0][1] >= col_start:
                        merged_cell.shift(col_number, 0)
                wb[sheetname].insert_cols(col_start, col_number)
                if col_number > 1:
                    new_merge = openpyxl.utils.get_column_letter(col_start) + '1:' + openpyxl.utils.get_column_letter(
                        col_start + 2) + '1'
                    wb[sheetname].merge_cells(new_merge)
                wb[sheetname].cell(1, col_start).value = key
                wb[sheetname].cell(2, col_start).value = 'section'
                wb[sheetname].cell(3, col_start).value = '-'

                # formatting
                for col in range(col_start, col_start + col_number):
                    wb[sheetname].cell(1, col).style = m_header_style
                    wb[sheetname].cell(1, col).border = no_border
                    wb[sheetname].cell(2, col).style = m_subheader_style
                    wb[sheetname].cell(2, col).border = no_border
                    wb[sheetname].cell(3, col).style = m_unit_style
                    wb[sheetname].cell(3, col).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style
                for col in [col_start, col_start + col_number]:
                    for row in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row, col).border = l_border
            else:
                logging.error('%s NOT IMPLEMENTED YET' % key)


        # ECO
        sheetname = 'eco'
        merged_cells = list(wb[sheetname].merged_cells)

        # Store property range for later
        property_range = {}
        for merge_cell in merged_cells:
            if merge_cell.start_cell.value in ['chl-a', 'phaeo']:
                for prop in ['chl-a', 'phao']:
                    if merge_cell.start_cell.value == prop:
                        property_range[prop] = merge_cell

        # Unmerge header cells:
        for merge_cell in merged_cells:
            if merge_cell.start_cell.row == 1:
                col_start = merge_cell.left[0][1]
                col_end = merge_cell.right[0][1]

                # unmerged cell
                header = merge_cell.start_cell.value
                wb[sheetname].unmerge_cells(merge_cell.coord)

                # find header
                value_idx = None
                id_idx = None
                for col_idx in range(col_start, col_end + 1):
                    if wb[sheetname].cell(2, col_idx).value == 'value':
                        value_idx = col_idx
                    elif wb[sheetname].cell(2, col_idx).value == 'ID':
                        id_idx = col_idx
                if value_idx is not None:
                    wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                    wb[sheetname].cell(1, value_idx).value = header
                elif value_idx is not None:
                    wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                    wb[sheetname].cell(1, id_idx).value = header

                # formatting
                for col_idx in range(col_start, col_end + 1):
                    wb[sheetname].cell(1, col_idx).style = m_header_style
                    wb[sheetname].cell(1, col_idx).border = no_border
                    wb[sheetname].cell(2, col_idx).style = m_subheader_style
                    wb[sheetname].cell(2, col_idx).border = no_border
                    wb[sheetname].cell(3, col_idx).style = m_unit_style
                    wb[sheetname].cell(3, col_idx).border = no_border
                    wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                if sheetname in prop_associated_tab and header not in prop_associated_tab[sheetname]:
                    for col in [col_start]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border
                else:
                    for col in [col_start, col_end + 1]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border

        # correct 'eco. data sampe' with 'eco. data sample'
        for _col in range(1, wb[sheetname].max_column):
            if wb[sheetname].cell(1, _col).value == 'eco. data sampe':
                wb[sheetname].cell(1, _col).value == 'eco. data sample'

        # chl-a and phaeo
        if 'chl-a' in property_range and 'phaeo' in property_range:
            logging.error("NOT IMPLEMENTED: 'chl-a' in property_range and 'phaeo' in property_range")
            #
            # # Look for chl-a and phaeo merged columns
            # col_chla_ID = None
            # col_phaeo_ID = None
            # col_chla_value = None
            # col_phaeo_value = None
            # col_chla_qual = None
            # col_phaeo_qual = None
            # for col in range(5, wb[sheetname].max_column + 1):
            #     # look for chl-a and phaeo range
            #     if wb[sheetname].cell(1, col).value == 'chl-a':
            #         if wb[sheetname].cell(2, col - 1).value == 'ID':
            #             col_chla_ID = col
            #         if wb[sheetname].cell(2, col).value == 'value':
            #             col_chla_value = col
            #         if wb[sheetname].cell(2, col + 1).value == 'qual':
            #             col_chla_qual = col
            #     if wb[sheetname].cell(1, col).value == 'phaeo':
            #         if wb[sheetname].cell(2, col - 1).value == 'ID':
            #             col_phaeo_ID = col
            #         if wb[sheetname].cell(2, col).value == 'value':
            #             col_phaeo_value = col
            #         if wb[sheetname].cell(2, col + 1).value == 'qual':
            #             col_phaeo_qual = col
            #
            # max_row = wb['eco'].max_row
            # if col_chla_ID is not None and col_phaeo_ID is not None:
            #     logging.error('NOT IMPLEMENTED:  col_chla_ID is not None and col_phaeo_ID is not None')
            #     dchla_ID = [wb['eco'].cell(row=ii, column=col_chla_ID).value for ii in range(4, max_row)]
            #     dphaeo_ID = [wb['eco'].cell(row=ii, column=col_phaeo_ID).value for ii in range(4, max_row)]
            #     dchla_qual = [wb[sheetname].cell(row=ii, column=col_chla_qual).value for ii in range(4, max_row)]
            #     dphaeo_qual = [wb[sheetname].cell(row=ii, column=col_phaeo_qual).value for ii in range(4, max_row)]
            #
            #     if dchla_qual != dphaeo_qual:
            #         logging.error('NOT IMPLEMENTED: dchla_ID != dphaeo_ID')
            #     else:
            #         # move column of dphaeo_value after dchla_value and before dchla_qual
            #         # remove column of dphaeo_ID and dphaeo_qual
            #
            #         # rename volume to "filtered volume"
            #         # look for chl-a, volume:
            #
            # wb['eco'].cell(2, col_chla_vol).value = 'filtered volume'
            #
            #         # delete column phaeo_vol, phao_ID and chla_quality:
            #         wb['eco'].delete_cols(col_phaeo_vol, 1)
            #         wb['eco'].delete_cols(col_phaeo_ID, 1)
            #         wb['eco'].delete_cols(col_chla_qual, 1)
            #
            #         # formatting
            #         for col in range(range_chla.min_col, range_chla.min_col+5):
            #             wb['eco'].cell(1, col).style = m_header_style
            #             wb['eco'].cell(1, col).border = no_border
            #             wb['eco'].cell(2, col).style = m_subheader_style
            #             wb['eco'].cell(2, col).border = no_border
            #             wb['eco'].cell(3, col).style = m_unit_style
            #             wb['eco'].cell(3, col).border = no_border
            #             wb['eco'].cell(max_row, col).style = m_bottom_style
            #         for col in [range_chla.min_col, range_chla.min_col + 5]:
            #             for row in range(1, 4):
            #                 wb['eco'].cell(row, col).border = l_border
            # else:
            #     logger.info('%s\t\tchl-a ID different from phaeo ID: merging not possible' % wb['metadata-core']['C1'].value)
            #
        elif 'chl-a' in property_range:
            # look for chl-a value column
            for col in range(4, wb[sheetname].max_column):
                if wb[sheetname].cell(1, col).value == 'chl-a':
                    break
            # insert phaeo value column after chl-a value column
            wb[sheetname].insert_cols(col + 1, 1)
            wb[sheetname].cell(1, col + 1).value = 'phaeo'
            wb[sheetname].cell(2, col + 1).value = 'value'
            wb[sheetname].cell(3, col + 1).value = 'mg/m3'

            # insert 'filtered volume' column before chl-a value column
            wb[sheetname].insert_cols(col, 1)
            wb[sheetname].cell(2, col).value = 'filtered volume'
            wb[sheetname].cell(3, col).value = 'L'

            # formatting
            col_start = col
            col_end = col + 2
            for col_idx in range(col_start, col_end + 1):
                wb[sheetname].cell(1, col_idx).style = m_header_style
                wb[sheetname].cell(1, col_idx).border = no_border
                wb[sheetname].cell(2, col_idx).style = m_subheader_style
                wb[sheetname].cell(2, col_idx).border = no_border
                wb[sheetname].cell(3, col_idx).style = m_unit_style
                wb[sheetname].cell(3, col_idx).border = no_border
                wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

            for col in [col_start - 1, col_end + 2]:
                for row in range(1, wb[sheetname].max_row):
                    wb[sheetname].cell(row, col).border = l_border

        # SNOW
        sheetname = 'snow'
        merged_cells = list(wb[sheetname].merged_cells)

        for merged_cell in merged_cells:
            if merged_cell.start_cell.value == 'eco sample':
                break
                # unmerge cell
                wb[sheetname].unmerge_cells(merged_cell.coord)

                # add filtered 'volume' column:
                col_start = merged_cell.left[0][1]
                col_end = merged_cell.right[0][1]
                col_idx = col_start + 1
                for _mc in merged_cells:
                    if _mc.left[0][1] > col_end:
                        _mc.shift(1, 0)
                wb[sheetname].insert_cols(col_idx, 1)
                wb[sheetname].cell(2, col_idx).value = 'volume'
                wb[sheetname].cell(3, col_idx).value = 'L'
                # formatting
                wb[sheetname].cell(1, col_idx).style = m_header_style
                wb[sheetname].cell(1, col_idx).border = no_border
                wb[sheetname].cell(2, col_idx).style = m_subheader_style
                wb[sheetname].cell(2, col_idx).border = no_border
                wb[sheetname].cell(3, col_idx).style = m_unit_style
                wb[sheetname].cell(3, col_idx).border = no_border
                wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                # formatting
                for col in [col_start, col_end + 2]:
                    for row in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row, col).border = no_border

                # merge new range
                wb[sheetname].merge_cells(start_row=1, start_column=col_start, end_row=1, end_column=col_end + 1)
                break

            # rename 'eco sample' to 'eco. data example'
            for col_idx in range(1, wb[sheetname].max_column):
                if wb[sheetname].cell(1, col_idx).value in ['eco sample']:
                    wb[sheetname].cell(1, col_idx).value =  'eco. data example'

            # update version
            wb['metadata-station']['C1'].value = '1.4.6'
            version_int[2] = 6

        # Update to 1.4.7:
        if version_int[2] < 7:
            # TEX
            sheetname = 'tex'
            # rename 'Core' to 'core
            for col_idx in range(1, wb[sheetname].max_column):
                if wb[sheetname].cell(1, col_idx).value == 'Core':
                    wb[sheetname].cell(1, col_idx).value = 'core'

            # ECO-POOL
            # Insert 'eco-pool' tab
            eco_sheet_index = wb._sheets.index(wb['eco'])
            wb.create_sheet("eco-pool", eco_sheet_index+1)
            wb_source = openpyxl.load_workbook(os.path.join(pysic_fp, 'ressources/AAA_BB-YYYYXXZZ-N_P-1.4.7.xlsx'), data_only=True)
            copy_cells(wb_source["eco-pool"], wb['eco-pool'])  # copy all the cel values and styles
            copy_sheet_attributes(wb_source['eco-pool'], wb['eco-pool'])

            # SNOW
            sheetname = 'snow'
            # Unmerge headers
            merged_cells = list(wb[sheetname].merged_cells)

            # Store property range for d18O and dD
            stored_headers = ['d18O', 'dD', 'temperature']
            property_range = {}
            for merge_cell in merged_cells:
                if merge_cell.start_cell.value in stored_headers:
                    for prop in stored_headers:
                        if merge_cell.start_cell.value == prop:
                            property_range[prop] = merge_cell

            # Unmerge header cells:
            for merge_cell in merged_cells:
                if merge_cell.start_cell.row == 1:
                    col_start = merge_cell.left[0][1]
                    col_end = merge_cell.right[0][1]

                    # unmerged cell
                    header = merge_cell.start_cell.value
                    wb[sheetname].unmerge_cells(merge_cell.coord)

                    # find header
                    value_idx = None
                    id_idx = None
                    for col_idx in range(col_start, col_end + 1):
                        if wb[sheetname].cell(2, col_idx).value == 'value':
                            value_idx = col_idx
                        elif wb[sheetname].cell(2, col_idx).value == 'ID':
                            id_idx = col_idx
                    if value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, value_idx).value = header
                    elif value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, id_idx).value = header

                    # formatting
                    for col_idx in range(col_start, col_end + 1):
                        wb[sheetname].cell(1, col_idx).style = m_header_style
                        wb[sheetname].cell(1, col_idx).border = no_border
                        wb[sheetname].cell(2, col_idx).style = m_subheader_style
                        wb[sheetname].cell(2, col_idx).border = no_border
                        wb[sheetname].cell(3, col_idx).style = m_unit_style
                        wb[sheetname].cell(3, col_idx).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                    if header in ['conductivity', 'dD']:
                        continue
                    elif header in ['d_excess', 'phaeo']:
                        for col in [col_end + 2]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    elif header in ['specific conductance']:
                        for col in [col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    elif header in ['salinity']:
                        for col in [col_start]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border

            # S2. Reorganize d18O, dD colums and add d_excess
            max_row = wb[sheetname].max_row

            # found column id for ID and qual of d18O and dD
            sh_idx = {}
            for prop in property_range:
                if prop not in sh_idx:
                    sh_idx[prop] = {}
                merge_cell = property_range[prop]
                col_start = merge_cell.left[0][1]
                col_end = merge_cell.right[0][1]
                for col_idx in range(col_start, col_end + 1):
                    subheader = wb[sheetname].cell(2, col_idx).value
                    sh_idx[prop][subheader] = col_idx

            # Check if d18O_ID match dD_ID:
            d18O_ID = [wb[sheetname].cell(row=ii, column=sh_idx['d18O']['ID']).value for ii in range(4, max_row)]
            dD_ID = [wb[sheetname].cell(row=ii, column=sh_idx['dD']['ID']).value for ii in range(4, max_row)]
            d18O_qual = [wb[sheetname].cell(row=ii, column=sh_idx['d18O']['quality']).value for ii in range(4, max_row)]
            dD_qual = [wb[sheetname].cell(row=ii, column=sh_idx['dD']['quality']).value for ii in range(4, max_row)]

            if dD_ID == d18O_ID:
                # Insert d_excess column after dD:
                wb[sheetname].insert_cols(sh_idx['dD']['ID'] + 1, 1)
                wb[sheetname].cell(1, sh_idx['dD']['ID'] + 1).value = 'd_excess'
                wb[sheetname].cell(2, sh_idx['dD']['ID'] + 1).value = 'value'
                wb[sheetname].cell(3, sh_idx['dD']['ID'] + 1).value = '‰'
                wb[sheetname].cell(1, sh_idx['dD']['ID'] + 1).style = m_header_style
                wb[sheetname].cell(1, sh_idx['dD']['ID'] + 1).border = no_border
                wb[sheetname].cell(2, sh_idx['dD']['ID'] + 1).style = m_subheader_style
                wb[sheetname].cell(2, sh_idx['dD']['ID'] + 1).border = no_border
                wb[sheetname].cell(3, sh_idx['dD']['ID'] + 1).style = m_unit_style
                wb[sheetname].cell(3, sh_idx['dD']['ID'] + 1).border = no_border
                wb[sheetname].cell(max_row, sh_idx['dD']['ID'] + 1).style = m_bottom_style

                # remove colum of dD_IDy
                wb[sheetname].delete_cols(sh_idx['dD']['ID'], 1)

                if d18O_qual != dD_qual:
                    logging.error('NOT IMPLEMENTED: d18O_qual != dD_qual')
                else:
                    # remove colum for d18O_qual
                    wb[sheetname].delete_cols(sh_idx['d18O']['quality'], 1)
            else:
                logger.info(
                    '%s\t\td18O ID different from dD ID: merging not possible' % wb['metadata-core']['C1'].value)

            # for 'temperature' header, rename subheader 'temperature' to value
            for col_idx in range(2, wb[sheetname].max_column):
                if wb[sheetname].cell(2, col_idx).value == 'temperature':
                    if wb[sheetname].cell(1, col_idx - 1).value == 'temperature':
                        wb[sheetname].cell(1, col_idx).value = 'temperature'
                        wb[sheetname].cell(2, col_idx).value = 'value'
                        wb[sheetname].cell(1, col_idx - 1).value = ''

            # for 'eco sample' rename to 'eco property'
            for col_idx in range(1, wb[sheetname].max_column):
                if wb[sheetname].cell(1, col_idx).value in ['eco sample', 'eco. data example']:
                    wb[sheetname].cell(1, col_idx).value = 'eco property'

            # rename 'Snow micro pen SMP' to 'swow micropen'
            for col_idx in range(1, wb[sheetname].max_column):
                if wb[sheetname].cell(1, col_idx).value in ['Snow micro pen SMP']:
                    wb[sheetname].cell(1, col_idx).value = 'swow micropen'

            # SACKHOLE
            sheetname = 'sackhole'
            merged_cells = list(wb[sheetname].merged_cells)
            # Store property range for d18O and dD
            stored_headers = ['d18O', 'dD']
            property_range = {}
            for merge_cell in merged_cells:
                if merge_cell.start_cell.value in stored_headers:
                    for prop in stored_headers:
                        if merge_cell.start_cell.value == prop:
                            property_range[prop] = merge_cell

            # Unmerge header cells:
            merged_cells = list(wb[sheetname].merged_cells)
            for merge_cell in merged_cells:
                if merge_cell.start_cell.row == 1:
                    col_start = merge_cell.left[0][1]
                    col_end = merge_cell.right[0][1]

                    # unmerged cell
                    header = merge_cell.start_cell.value
                    wb[sheetname].unmerge_cells(merge_cell.coord)

                    # find header
                    value_idx = None
                    id_idx = None
                    for col_idx in range(col_start, col_end + 1):
                        if wb[sheetname].cell(2, col_idx).value == 'value':
                            value_idx = col_idx
                        elif wb[sheetname].cell(2, col_idx).value == 'ID':
                            id_idx = col_idx
                    if value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, value_idx).value = header
                    elif value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, id_idx).value = header

                    # formatting
                    for col_idx in range(col_start, col_end + 1):
                        wb[sheetname].cell(1, col_idx).style = m_header_style
                        wb[sheetname].cell(1, col_idx).border = no_border
                        wb[sheetname].cell(2, col_idx).style = m_subheader_style
                        wb[sheetname].cell(2, col_idx).border = no_border
                        wb[sheetname].cell(3, col_idx).style = m_unit_style
                        wb[sheetname].cell(3, col_idx).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                    if header not in ['conductivity', 'specific conductance', 'dD', 'd_excess', 'phaeo']:
                        for col in [col_start]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border

            # S2. Reorganize d18O, dD colums and add d_excess
            max_row = wb[sheetname].max_row
            # found column id for ID and qual of d18O and dD
            sh_idx = {}
            for prop in property_range:
                if prop not in sh_idx:
                    sh_idx[prop] = {}
                merge_cell = property_range[prop]
                col_start = merge_cell.left[0][1]
                col_end = merge_cell.right[0][1]
                for col_idx in range(col_start, col_end + 1):
                    subheader = wb[sheetname].cell(2, col_idx).value
                    sh_idx[prop][subheader] = col_idx

            # Check if d18O_ID match dD_ID:
            d18O_ID = [wb[sheetname].cell(row=ii, column=sh_idx['d18O']['ID']).value for ii in range(4, max_row)]
            dD_ID = [wb[sheetname].cell(row=ii, column=sh_idx['dD']['ID']).value for ii in range(4, max_row)]
            d18O_qual = [wb[sheetname].cell(row=ii, column=sh_idx['d18O']['quality']).value for ii in range(4, max_row)]
            dD_qual = [wb[sheetname].cell(row=ii, column=sh_idx['dD']['quality']).value for ii in range(4, max_row)]

            if dD_ID == d18O_ID:
                # Insert d_excess column after dD:
                wb[sheetname].insert_cols(sh_idx['dD']['ID'] + 1, 1)
                wb[sheetname].cell(1, sh_idx['dD']['ID'] + 1).value = 'd_excess'
                wb[sheetname].cell(2, sh_idx['dD']['ID'] + 1).value = 'value'
                wb[sheetname].cell(3, sh_idx['dD']['ID'] + 1).value = '‰'
                wb[sheetname].cell(1, sh_idx['dD']['ID'] + 1).style = m_header_style
                wb[sheetname].cell(1, sh_idx['dD']['ID'] + 1).border = no_border
                wb[sheetname].cell(2, sh_idx['dD']['ID'] + 1).style = m_subheader_style
                wb[sheetname].cell(2, sh_idx['dD']['ID'] + 1).border = no_border
                wb[sheetname].cell(3, sh_idx['dD']['ID'] + 1).style = m_unit_style
                wb[sheetname].cell(3, sh_idx['dD']['ID'] + 1).border = no_border
                wb[sheetname].cell(wb[sheetname].max_row, sh_idx['dD']['ID'] + 1).style = m_bottom_style

                # remove colum of dD_IDy
                wb[sheetname].delete_cols(sh_idx['dD']['ID'], 1)
                if d18O_qual != dD_qual:
                    logging.error('NOT IMPLEMENTED: d18O_qual != dD_qual')
                else:
                    # remove colum for d18O_qual
                    wb[sheetname].delete_cols(sh_idx['d18O']['quality'], 1)

             # Add eco property before TM
            flag_m = {'eco property': 0}
            header_after = 'TM'
            col_number = 4
            for col in openpyxl.utils.cols_from_range(
                    'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                if wb[sheetname][cell[0]].value is not None:
                    for key in flag_m.keys():
                        if key in wb[sheetname][cell[0]].value:
                            flag_m[key] = 1
            for key in flag_m.keys():
                if flag_m[key] == 0:
                    for col in range(4, wb[sheetname].max_column):
                        if wb[sheetname].cell(1, col).value == header_after:
                            break

                    # Before TM
                    col_start = col - 1
                    for merged_cell in wb[sheetname].merged_cells.ranges:
                        if merged_cell.left[0][1] >= col_start:
                            merged_cell.shift(col_number, 0)
                    wb[sheetname].insert_cols(col_start, col_number)

                    #  Add diameter measurement in density-volume sheet:
                    wb[sheetname].cell(1, col_start+2).value = 'eco property'
                    wb[sheetname].cell(2, col_start).value = 'ID'
                    wb[sheetname].cell(2, col_start + 1).value = 'volume'
                    wb[sheetname].cell(2, col_start + 2).value = 'value'
                    wb[sheetname].cell(2, col_start + 3).value = 'quality'
                    wb[sheetname].cell(3, col_start).value = '-'
                    wb[sheetname].cell(3, col_start + 1).value = 'L'
                    wb[sheetname].cell(3, col_start + 2).value = '-'
                    wb[sheetname].cell(3, col_start + 3).value = '[0-9]'

                    # Formatting
                    for col in range(col_start, col_start + col_number  ):
                        wb[sheetname].cell(1, col).style = m_header_style
                        wb[sheetname].cell(1, col).border = no_border
                        wb[sheetname].cell(2, col).style = m_subheader_style
                        wb[sheetname].cell(2, col).border = no_border
                        wb[sheetname].cell(3, col).style = m_unit_style
                        wb[sheetname].cell(3, col).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style
                    for col in [col_start, col_start + col_number]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border

            # SEAWATER
            sheetname = 'seawater'
            merged_cells = list(wb[sheetname].merged_cells)
            # Store property range for d18O and dD
            stored_headers = ['d18O', 'dD']
            property_range = {}
            for merge_cell in merged_cells:
                if merge_cell.start_cell.value in stored_headers:
                    for prop in stored_headers:
                        if merge_cell.start_cell.value == prop:
                            property_range[prop] = merge_cell

            # Unmerge header cells:
            merged_cells = list(wb[sheetname].merged_cells)
            for merge_cell in merged_cells:
                if merge_cell.start_cell.row == 1:
                    col_start = merge_cell.left[0][1]
                    col_end = merge_cell.right[0][1]

                    # unmerged cell
                    header = merge_cell.start_cell.value
                    wb[sheetname].unmerge_cells(merge_cell.coord)

                    # find header
                    value_idx = None
                    id_idx = None
                    for col_idx in range(col_start, col_end + 1):
                        if wb[sheetname].cell(2, col_idx).value == 'value':
                            value_idx = col_idx
                        elif wb[sheetname].cell(2, col_idx).value == 'ID':
                            id_idx = col_idx
                    if value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, value_idx).value = header
                    elif value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, id_idx).value = header

                    # formatting
                    for col_idx in range(col_start, col_end + 1):
                        wb[sheetname].cell(1, col_idx).style = m_header_style
                        wb[sheetname].cell(1, col_idx).border = no_border
                        wb[sheetname].cell(2, col_idx).style = m_subheader_style
                        wb[sheetname].cell(2, col_idx).border = no_border
                        wb[sheetname].cell(3, col_idx).style = m_unit_style
                        wb[sheetname].cell(3, col_idx).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                    if header in ['conductivity', 'dD']:
                        continue
                    elif header in ['d_excess', 'phaeo']:
                        for col in [col_end + 2]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    elif header in ['specific conductance']:
                        for col in [col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    elif header in ['salinity']:
                        for col in [col_start]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border


            # Reorganize d18O, dD colums and add d_excess
            max_row = wb[sheetname].max_row
            # found column id for ID and qual of d18O and dD
            sh_idx = {}
            for prop in property_range:
                if prop not in sh_idx:
                    sh_idx[prop] = {}
                merge_cell = property_range[prop]
                col_start = merge_cell.left[0][1]
                col_end = merge_cell.right[0][1]
                for col_idx in range(col_start, col_end + 1):
                    subheader = wb[sheetname].cell(2, col_idx).value
                    sh_idx[prop][subheader] = col_idx

            # Check if d18O_ID match dD_ID:
            d18O_ID = [wb[sheetname].cell(row=ii, column=sh_idx['d18O']['ID']).value for ii in range(4, max_row)]
            dD_ID = [wb[sheetname].cell(row=ii, column=sh_idx['dD']['ID']).value for ii in range(4, max_row)]
            d18O_qual = [wb[sheetname].cell(row=ii, column=sh_idx['d18O']['quality']).value for ii in range(4, max_row)]
            dD_qual = [wb[sheetname].cell(row=ii, column=sh_idx['dD']['quality']).value for ii in range(4, max_row)]

            if dD_ID == d18O_ID:
                # remove colum of dD_IDy
                wb[sheetname].delete_cols(sh_idx['dD']['ID'], 1)
                if d18O_qual != dD_qual:
                    logging.error('NOT IMPLEMENTED: d18O_qual != dD_qual')
                else:
                    # remove colum for d18O_qual
                    wb[sheetname].delete_cols(sh_idx['d18O']['quality'], 1)

             # Add eco property before TM
            flag_m = {'eco property': 0}
            header_after = 'TM'
            col_number = 4
            for col in openpyxl.utils.cols_from_range(
                    'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                if wb[sheetname][cell[0]].value is not None:
                    for key in flag_m.keys():
                        if key in wb[sheetname][cell[0]].value:
                            flag_m[key] = 1
            for key in flag_m.keys():
                if flag_m[key] == 0:
                    for col in range(4, wb[sheetname].max_column):
                        if wb[sheetname].cell(1, col).value == header_after:
                            break

                    # Before TM
                    col_start = col - 1
                    for merged_cell in wb[sheetname].merged_cells.ranges:
                        if merged_cell.left[0][1] >= col_start:
                            merged_cell.shift(col_number, 0)
                    wb[sheetname].insert_cols(col_start, col_number)

                    #  Add diameter measurement in density-volume sheet:
                    wb[sheetname].cell(1, col_start+2).value = 'eco property'
                    wb[sheetname].cell(2, col_start).value = 'ID'
                    wb[sheetname].cell(2, col_start + 1).value = 'volume'
                    wb[sheetname].cell(2, col_start + 2).value = 'value'
                    wb[sheetname].cell(2, col_start + 3).value = 'quality'
                    wb[sheetname].cell(3, col_start).value = '-'
                    wb[sheetname].cell(3, col_start + 1).value = 'L'
                    wb[sheetname].cell(3, col_start + 2).value = '-'
                    wb[sheetname].cell(3, col_start + 3).value = '[0-9]'

                    # Formatting
                    for col in range(col_start, col_start + col_number  ):
                        wb[sheetname].cell(1, col).style = m_header_style
                        wb[sheetname].cell(1, col).border = no_border
                        wb[sheetname].cell(2, col).style = m_subheader_style
                        wb[sheetname].cell(2, col).border = no_border
                        wb[sheetname].cell(3, col).style = m_unit_style
                        wb[sheetname].cell(3, col).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style

                    if header in ['conductivity', 'dD']:
                        continue
                    elif header in ['d_excess', 'phaeo']:
                        for col in [col_end + 2]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    elif header in ['specific conductance']:
                        for col in [col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    elif header in ['salinity']:
                        for col in [col_start]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border


            # add 'temperature' (value, quality) in front of d18O/dD/d_excess
            flag_m = {'temperature': 0}
            header_after = 'd18O'
            col_number = 2
            for col in openpyxl.utils.cols_from_range(
                    'A1:' + openpyxl.utils.get_column_letter(wb[sheetname].max_column) + str(1)):
                if wb[sheetname][cell[0]].value is not None:
                    for key in flag_m.keys():
                        if key in wb[sheetname][cell[0]].value:
                            flag_m[key] = 1
            for key in flag_m.keys():
                if flag_m[key] == 0:
                    for col in range(4, wb[sheetname].max_column):
                        if wb[sheetname].cell(1, col).value == header_after:
                            break

                    # Before TM
                    col_start = col - 1
                    for merged_cell in wb[sheetname].merged_cells.ranges:
                        if merged_cell.left[0][1] >= col_start:
                            merged_cell.shift(col_number, 0)
                    wb[sheetname].insert_cols(col_start, col_number)

                    #  Add diameter measurement in density-volume sheet:
                    wb[sheetname].cell(1, col_start).value = 'temperature'
                    wb[sheetname].cell(2, col_start).value = 'value'
                    wb[sheetname].cell(2, col_start + 1).value = 'quality'
                    wb[sheetname].cell(3, col_start).value = '˚C'
                    wb[sheetname].cell(3, col_start + 1).value = '[0-9]'

                    # Formatting
                    for col in range(col_start, col_start + col_number  ):
                        wb[sheetname].cell(1, col).style = m_header_style
                        wb[sheetname].cell(1, col).border = no_border
                        wb[sheetname].cell(2, col).style = m_subheader_style
                        wb[sheetname].cell(2, col).border = no_border
                        wb[sheetname].cell(3, col).style = m_unit_style
                        wb[sheetname].cell(3, col).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col).style = m_bottom_style
                    for col in [col_start, col_start + col_number]:
                        for row in range(1, wb[sheetname].max_row):
                            wb[sheetname].cell(row, col).border = l_border

            # move 'seawater' tab after 'sackhole'
            sackhole_sheet_idx = wb._sheets.index(wb['sackhole'])
            seawater_sheet_idx = wb._sheets.index(wb['seawater'])
            wb.active = seawater_sheet_idx
            wb.move_sheet(wb.active, offset=-(seawater_sheet_idx - sackhole_sheet_idx)+1)

            # DENSITY-VOLUME
            sheetname = 'density-volume'
            merged_cells = list(wb[sheetname].merged_cells)

            # Rename subheader for thickness
            for merge_cell in merged_cells:
                if merge_cell.start_cell.value == 'thickness':
                    col_idx = merge_cell.left[0][1]
                    wb[sheetname].cell(2, col_idx).value = 'measurement1'
                    wb[sheetname].cell(2, col_idx + 1).value = 'measurement2'
                    wb[sheetname].cell(2, col_idx + 2).value = 'measurement3'
                    wb[sheetname].cell(2, col_idx + 3).value = 'measurement4'
                    wb[sheetname].cell(2, col_idx + 4).value = 'value'
                if merge_cell.start_cell.value == 'diameter':
                    col_idx = merge_cell.left[0][1]
                    wb[sheetname].cell(2, col_idx).value = 'measurement1'
                    wb[sheetname].cell(2, col_idx + 1).value = 'measurement2'
                    wb[sheetname].cell(2, col_idx + 2).value = 'value'

            # Unmerge header cells:
            for merge_cell in merged_cells:
                if merge_cell.start_cell.row == 1:
                    col_start = merge_cell.left[0][1]
                    col_end = merge_cell.right[0][1]

                    # unmerged cell
                    header = merge_cell.start_cell.value
                    wb[sheetname].unmerge_cells(merge_cell.coord)

                    # find header
                    value_idx = None
                    id_idx = None
                    for col_idx in range(col_start, col_end + 1):
                        if wb[sheetname].cell(2, col_idx).value == 'value':
                            value_idx = col_idx
                        elif wb[sheetname].cell(2, col_idx).value == 'ID':
                            id_idx = col_idx
                    if value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, value_idx).value = header
                    elif value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, id_idx).value = header

                    # formatting
                    for col_idx in range(col_start, col_end + 1):
                        wb[sheetname].cell(1, col_idx).style = m_header_style
                        wb[sheetname].cell(1, col_idx).border = no_border
                        wb[sheetname].cell(2, col_idx).style = m_subheader_style
                        wb[sheetname].cell(2, col_idx).border = no_border
                        wb[sheetname].cell(3, col_idx).style = m_unit_style
                        wb[sheetname].cell(3, col_idx).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                    if header not in ['conductivity', 'specific conductance', 'dD', 'd_excess', 'phaeo']:
                        for col in [col_start]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border

            # formatting
            for col_idx in range(1, wb[sheetname].max_column):
                if wb[sheetname].cell(1, col_idx).value == 'mass':
                    for row_idx in range(1, wb[sheetname].max_row):
                        wb[sheetname].cell(row_idx, col_idx).border = l_border
                break

            # move density-volume behind density-densimetry:
            rho_v_sheet_idx = wb._sheets.index(wb['density-volume'])
            rho_d_sheet_idx = wb._sheets.index(wb['density-densimetry'])
            wb.active = rho_v_sheet_idx
            wb.move_sheet(wb.active, offset=-(rho_v_sheet_idx - rho_d_sheet_idx))

            # DENSITY-DENSIMETRY
            sheetname = 'density-densimetry'
            merged_cells = list(wb[sheetname].merged_cells)

            # Unmerge header cells:
            for merge_cell in merged_cells:
                if merge_cell.start_cell.row == 1:
                    col_start = merge_cell.left[0][1]
                    col_end = merge_cell.right[0][1]

                    # unmerged cell
                    header = merge_cell.start_cell.value
                    wb[sheetname].unmerge_cells(merge_cell.coord)

                    # find header
                    value_idx = None
                    id_idx = None
                    for col_idx in range(col_start, col_end + 1):
                        if wb[sheetname].cell(2, col_idx).value == 'value':
                            value_idx = col_idx
                        elif wb[sheetname].cell(2, col_idx).value == 'ID':
                            id_idx = col_idx
                    if value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, value_idx).value = header
                    elif value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, id_idx).value = header
                    else:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, col_start).value = header

                    # formatting
                    for col_idx in range(col_start, col_end + 1):
                        wb[sheetname].cell(1, col_idx).style = m_header_style
                        wb[sheetname].cell(1, col_idx).border = no_border
                        wb[sheetname].cell(2, col_idx).style = m_subheader_style
                        wb[sheetname].cell(2, col_idx).border = no_border
                        wb[sheetname].cell(3, col_idx).style = m_unit_style
                        wb[sheetname].cell(3, col_idx).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                    if header in ['conductivity', 'dD']:
                        continue
                    elif header in ['d_excess', 'phaeo']:
                        for col in [col_end + 2]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    elif header in ['specific conductance']:
                        for col in [col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    elif header in ['salinity']:
                        for col in [col_start]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border


            # SEDIMENT
            sheetname = 'sediment'
            merged_cells = list(wb[sheetname].merged_cells)

            # Store property range for later
            property_range = {}
            stored_header = ['sediment mass']
            for merge_cell in merged_cells:
                if merge_cell.start_cell.value in stored_header:
                    for prop in stored_header:
                        if merge_cell.start_cell.value == prop:
                            property_range[prop] = merge_cell

            # Unmerge header cells:
            for merge_cell in merged_cells:
                if merge_cell.start_cell.row == 1:
                    col_start = merge_cell.left[0][1]
                    col_end = merge_cell.right[0][1]

                    # unmerged cell
                    header = merge_cell.start_cell.value
                    wb[sheetname].unmerge_cells(merge_cell.coord)

                    # find header
                    value_idx = None
                    id_idx = None
                    for col_idx in range(col_start, col_end + 1):
                        if wb[sheetname].cell(2, col_idx).value == 'value':
                            value_idx = col_idx
                        elif wb[sheetname].cell(2, col_idx).value == 'ID':
                            id_idx = col_idx
                    if value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, value_idx).value = header
                    elif value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, id_idx).value = header
                    else:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, col_start).value = header

                    # formatting
                    for col_idx in range(col_start, col_end + 1):
                        wb[sheetname].cell(1, col_idx).style = m_header_style
                        wb[sheetname].cell(1, col_idx).border = no_border
                        wb[sheetname].cell(2, col_idx).style = m_subheader_style
                        wb[sheetname].cell(2, col_idx).border = no_border
                        wb[sheetname].cell(3, col_idx).style = m_unit_style
                        wb[sheetname].cell(3, col_idx).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                    if header not in ['conductivity', 'specific conductance', 'dD', 'd_excess', 'phaeo', 'mass']:
                        for col in [col_start]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border

            # remerged stored header
            for header in stored_header:
                wb[sheetname].merge_cells(property_range[header].coord)

            # CT
            sheetname = 'ct'

            # Unmerge header cells:
            merged_cells = list(wb[sheetname].merged_cells)
            for merge_cell in merged_cells:
                if merge_cell.start_cell.row == 1:
                    col_start = merge_cell.left[0][1]
                    col_end = merge_cell.right[0][1]

                    # unmerged cell
                    header = merge_cell.start_cell.value
                    wb[sheetname].unmerge_cells(merge_cell.coord)

                    # find header
                    value_idx = None
                    id_idx = None
                    for col_idx in range(col_start, col_end + 1):
                        if wb[sheetname].cell(2, col_idx).value == 'value':
                            value_idx = col_idx
                        elif wb[sheetname].cell(2, col_idx).value == 'ID':
                            id_idx = col_idx
                    if value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, value_idx).value = header
                    elif value_idx is not None:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, id_idx).value = header
                    else:
                        wb[sheetname].cell(1, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(1, col_start).value = header

                    # formatting
                    for col_idx in range(col_start, col_end + 1):
                        wb[sheetname].cell(1, col_idx).style = m_header_style
                        wb[sheetname].cell(1, col_idx).border = no_border
                        wb[sheetname].cell(2, col_idx).style = m_subheader_style
                        wb[sheetname].cell(2, col_idx).border = no_border
                        wb[sheetname].cell(3, col_idx).style = m_unit_style
                        wb[sheetname].cell(3, col_idx).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                    if header not in ['tar', 'ice', 'brine']:
                        for col in [col_start]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(1, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border

            # Unmerge subheader cells:
            ref_row_idx = 2
            for merge_cell in merged_cells:
                if merge_cell.start_cell.row == ref_row_idx:
                    col_start = merge_cell.left[0][1]
                    col_end = merge_cell.right[0][1]

                    # unmerged cell
                    header = merge_cell.start_cell.value
                    wb[sheetname].unmerge_cells(merge_cell.coord)

                    # find header
                    value_idx = None
                    id_idx = None
                    for col_idx in range(col_start, col_end + 1):
                        if wb[sheetname].cell(ref_row_idx + 1, col_idx).value == 'value':
                            value_idx = col_idx
                        elif wb[sheetname].cell(ref_row_idx + 1, col_idx).value == 'ID':
                            id_idx = col_idx
                    if value_idx is not None:
                        wb[sheetname].cell(ref_row_idx, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(ref_row_idx, value_idx).value = header
                    elif value_idx is not None:
                        wb[sheetname].cell(ref_row_idx, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(ref_row_idx, id_idx).value = header
                    else:
                        col_idx = col_start
                        wb[sheetname].cell(ref_row_idx, merge_cell.left[0][1]).value = None
                        wb[sheetname].cell(ref_row_idx, col_idx).value = header

                    # formatting
                    for col_idx in range(col_start, col_end + 1):
                        wb[sheetname].cell(ref_row_idx, col_idx).style = m_header_style
                        wb[sheetname].cell(ref_row_idx, col_idx).border = no_border
                        wb[sheetname].cell(ref_row_idx + 1, col_idx).style = m_subheader_style
                        wb[sheetname].cell(ref_row_idx + 1, col_idx).border = no_border
                        wb[sheetname].cell(ref_row_idx + 2, col_idx).style = m_unit_style
                        wb[sheetname].cell(ref_row_idx + 2, col_idx).border = no_border
                        wb[sheetname].cell(wb[sheetname].max_row, col_idx).style = m_bottom_style

                    if header not in ['conductivity', 'specific conductance', 'dD', 'd_excess', 'phaeo', 'mass']:
                        for col in [col_start]:
                            for row in range(ref_row_idx, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border
                    else:
                        for col in [col_start, col_end + 1]:
                            for row in range(ref_row_idx, wb[sheetname].max_row):
                                wb[sheetname].cell(row, col).border = l_border

            # LISTS
            # Override latest `list` sheet
            list_sheet_index = wb._sheets.index(wb['lists'])
            del wb['lists']
            wb.create_sheet("lists", list_sheet_index)
            wb_source = openpyxl.load_workbook(os.path.join(pysic_fp, 'ressources/AAA_BB-YYYYXXZZ-N_P-1.4.7.xlsx'), data_only=True)
            copy_cells(wb_source['lists'], wb['lists'])  # copy all the cel values and styles
            copy_sheet_attributes(wb_source['lists'], wb['lists'])

            # update version
            wb['metadata-station']['C1'].value = '1.4.7'
            version_int[2] = 7
    wb.save('/home/megavolts/test.xlsx')

    # # TODO update to version 8
    # if version_int[2] < 8:
    #     TODO: metadata-station: B33: remove salinity unit: PSU >> -
    #     TODO: eco: unmerged "melted volume"
    #     TODO: tex: rename 'core' to 'core section'
    #                # rename water salinity to seawater salinity
    #                 wb['metadata-station']['A33'].value = 'seawater salinity'
    #                 wb['metadata-station']['D33'].value = 'under ice/seawater interface'
    #     TODO: salo18: B1: remove capitalizaton: Depth 2 >> depth 2
    #     TODO: snow: add d_excess column
    #     TODO: snow: correct typo in header from 'swow micropen' to 'snow micropen'
    #     TODO: sediment: unmerge 'sediment mass' header
    #     TODO: seawater: add d_excess in isotope
    #     TODO: snow and other: rename 'volume' into 'filtered volume'
    #     TODO: cf. github/wiki

    if flag_update:
        ### Add an update is the 'metadata-core'
        # Find where 'VERSION' entries are located
        row = 1
        version_row = 0
        while version_row == 0 and row <= wb['metadata-core'].max_row:
            if wb['metadata-core'].cell(row, 1).value == 'VERSION' and wb['metadata-core'].cell(row + 1, 1).value == 'number':
                version_row = row
                break
            row += 1

        # Find line number with latest version entries
        row = version_row + 2
        new_line = 0
        while new_line == 0 and row <= wb['metadata-core'].max_row:
            if wb['metadata-core'].cell(row, 1).value is None:
                new_line = row
            row += 1

        # Add new line afterwards
        for merged_cell in wb['metadata-core'].merged_cells.ranges:
            if merged_cell.right[0][0] > new_line:
                merged_cell.shift(0, 1)
        wb['metadata-core'].insert_rows(new_line, 1)
        wb['metadata-core'].cell(new_line, 1).value = wb['metadata-core'].cell(new_line-1, 1).value + 1
        wb['metadata-core'].cell(new_line, 2).value = dt.date.today().isoformat()
        wb['metadata-core'].cell(new_line, 3).value = user
        wb['metadata-core'].cell(new_line, 5).value = 'Updated ice core data from ' + version + ' to ' + __CoreVersion__

        # formatting:
        for col in range(9, wb['metadata-core'].max_column+1):
            wb['metadata-core'].cell(new_line, col).style = m_bottom_style
        logger.debug('%s\t\tupdate from from %s to %s' % (wb['metadata-core']['A1'].value, version, __CoreVersion__))
        wb['metadata-station']['C1'] = __CoreVersion__
        logger.info('%s\t\tsaving updated ice core to version %s' % (wb['metadata-core']['A1'].value, __CoreVersion__))
        wb.save(ic_path)
        wb.close()
    else:
        logger.debug('%s\t\talready at latest (%s) version' % (wb['metadata-core']['A1'].value, __CoreVersion__))


## Update scripts:
def version_1_3_0_to_1_4_1(wb):
    import openpyxl as opxl
    import numpy as np
    logger = logging.getLogger(__name__)

    # Update from 1.3 to 1.4.1
    # METADATA-CORE
    sheetname = 'metadata-core'
    wb[sheetname]['A1'].value = 'core name'
    wb[sheetname]['A2'].value = 'date'
    wb[sheetname]['A3'].value = 'time'
    wb[sheetname]['A4'].value = 'note'
    wb[sheetname]['A7'].value = 'ice thickness'
    wb[sheetname]['A8'].value = 'draft'
    wb[sheetname]['A9'].value = 'freeboard'
    wb[sheetname]['A10'].value = 'core length'

    # formatting
    wb[sheetname]['E1'].style = m_bkg_style
    for row in range(1, 4):
        for col in range(1, opxl.utils.column_index_from_string('D') + 1):
            wb[sheetname].cell(row, col).border = b_border
    for col in range(1, opxl.utils.column_index_from_string('C') + 1):
        wb[sheetname].cell(7, col).border = b_border
        wb[sheetname].cell(10, col).border = no_border
        wb[sheetname].cell(9, col).border = b_border

    # - Add REFERENCE BLOCK
    row_n = 8
    row_insert_idx = 12
    # move merged cells downwards below row_insert_idx row
    for merged_cell in wb[sheetname].merged_cells.ranges:
        if merged_cell.right[0][0] > row_insert_idx:
            merged_cell.shift(0, row_n)
    # insert row_n rows starting at row_insert_idx row
    wb[sheetname].insert_rows(row_insert_idx, row_n)

    # insert text
    wb[sheetname]['A12'].value = 'REFERENCE'
    wb[sheetname]['A13'].value = 'ICE'
    wb[sheetname]['A15'].value = 'SNOW'
    wb[sheetname]['A17'].value = 'SEAWATER'
    wb[sheetname]['B13'].value = 'zero vertical'
    wb[sheetname]['B14'].value = 'direction'
    wb[sheetname]['C13'].value = '(0m @)'
    wb[sheetname]['E14'].value = 'down: positive away from the sky; up: positive toward the sky'
    wb[sheetname]['B15'].value = 'zero vertical'
    wb[sheetname]['B16'].value = 'direction'
    wb[sheetname]['C15'].value = '(0m @)'
    wb[sheetname]['E16'].value = 'down: positive away from the sky; up: positive toward the sky'
    wb[sheetname]['B17'].value = 'zero vertical'
    wb[sheetname]['B18'].value = 'direction'
    wb[sheetname]['C17'].value = '(0m @)'
    wb[sheetname]['E18'].value = 'down: positive away from the sky; up: positive toward the sky'

    # add data validation to worksheet
    from pysic.io.update import vert_ref_list, vert_dir_list
    wb[sheetname].add_data_validation(vert_ref_list)
    wb[sheetname].add_data_validation(vert_dir_list)
    vert_ref_list.add('D13')
    vert_ref_list.add('D15')
    vert_ref_list.add('D17')
    vert_dir_list.add('D14')
    vert_dir_list.add('D16')
    vert_dir_list.add('D18')
    wb.save('/home/megavolts/test.xlsx')

    # formatting
    max_col = 26
    for row in range(row_insert_idx, row_insert_idx + row_n + 1):
        for col in range(1, max_col + 1):
            wb[sheetname].cell(row, col).style = m_bkg_style
    # paint upper right cell into bkg
    for row in range(1, row_insert_idx):
        for col in range(7, max_col + 1):
            wb[sheetname].cell(row, col).style = m_bkg_style

    wb[sheetname]['A12'].style = m_header_title_style
    for row in range(row_insert_idx + 1, row_insert_idx + 6 + 1):
        # A header
        wb[sheetname].cell(row, 1).style = m_header_l_style
        wb[sheetname].cell(row, 2).style = m_subheader_l_style
        wb[sheetname].cell(row, 3).style = m_subheader_r_style
        wb[sheetname].cell(row, 4).style = m_data_style

    # cell line
    for row in np.arange(row_insert_idx + 2, row_insert_idx + row_n - 2, 2):
        for col in range(1, openpyxl.utils.column_index_from_string('H') + 1):
            wb[sheetname].cell(row, col).border = b_border

    # - format INSTRUMENTS and VERSION block
    # look for INSTRUMENTS and VERSION block
    row = row_insert_idx + row_n
    flag_instrument = True
    flag_version = True
    while flag_instrument or flag_version:
        if isinstance(wb[sheetname].cell(row, 1).value, str) and 'INSTRUMENT' in wb[sheetname].cell(row, 1).value:
            flag_instrument = False
            row_instrument_idx = row
        elif isinstance(wb[sheetname].cell(row, 1).value, str) and 'DATA VERSION' in wb[sheetname].cell(row,
                                                                                                        1).value:
            flag_version = False
            row_version_idx = row
        row += 1

    # add header line in VERSION block
    row_n = 1
    row_insert_idx = row_version_idx + 1
    # move merged cells downwards below row_insert_idx row
    for merged_cell in wb[sheetname].merged_cells.ranges:
        if merged_cell.right[0][0] > row_insert_idx:
            merged_cell.shift(0, row_n)
    # insert row_n rows starting at row_insert_idx row
    wb[sheetname].insert_rows(row_insert_idx, row_n)

    # insert text
    wb[sheetname].cell(row_version_idx + 1, 1).value = 'number'
    wb[sheetname].cell(row_version_idx + 1, 2).value = 'date'
    wb[sheetname].cell(row_version_idx + 1, 3).value = 'author'
    wb[sheetname].cell(row_version_idx + 1, 5).value = 'modification'

    # move modification data from col C to col E
    for row in range(row_version_idx + 2, wb[sheetname].max_row + 1):
        wb[sheetname].cell(row, 5).value = wb[sheetname].cell(row, 3).value
        wb[sheetname].cell(row, 3).value = None

    # formatting
    for row in range(row_instrument_idx - 1, wb[sheetname].max_row + 1 + 1):
        for col in range(1, max_col + 1):
            wb[sheetname].cell(row, col).style = m_bkg_style

    wb[sheetname].cell(row_instrument_idx, 1).style = m_header_title_style
    for row in range(row_instrument_idx + 1, row_version_idx - 1):

        # A header
        wb[sheetname].cell(row, 1).style = m_header_l_style
        wb[sheetname].cell(row, 2).style = m_header_l_style
        wb[sheetname].cell(row, 3).style = m_data_l_style
        # merge cell from col C (3) to col H (8)
        for merge_cells in wb[sheetname].merged_cells.ranges:
            if merge_cells.start_cell.row == row and merge_cells.start_cell.column == 3:
                wb[sheetname].unmerge_cells(merge_cells.coord)
            # make sure that unmerged cell are correctly painted
            for col in range(9, max_col + 1):
                wb[sheetname].cell(row, col).style = m_bkg_style
        new_range = 'C' + str(row) + ':H' + str(row)
        wb[sheetname].merge_cells(new_range)
        if row < row_version_idx - 2:
            for col in range(1, 8 + 1):
                wb[sheetname].cell(row, col).border = b_border

    wb[sheetname].cell(row_version_idx, 1).style = m_header_title_style
    row = row_version_idx + 1
    for col in range(1, 8 + 1):
        wb[sheetname].cell(row, col).style = m_subheader_l_style
    for row in range(row_version_idx + 2, wb[sheetname].max_row):
        for col in range(1, 8 + 1):
            wb[sheetname].cell(row, col).style = m_data_l_style
            if col >= 3:
                wb[sheetname].cell(row, col).alignment = Alignment(horizontal='left', wrapText=False,
                                                                   vertical='center')
            if col == 2:
                wb[sheetname].cell(row, col).number_format = 'mm-dd-yy'

    # METADATA-STATION
    sheetname = 'metadata-station'
    # rename metadata-coring sheetname to metadata-station
    if 'metadata-coring' in wb.sheetnames:
        wb['metadata-coring'].title = sheetname

    wb[sheetname]['A1'].value = 'ICE CORE DATA SHEET'
    wb[sheetname]['B1'].value = 'version'
    # wb[sheetname]['C1'].value = '1.4.1'  # moved at the end of the function
    wb[sheetname]['D1'].value = 'to be used with PySIC python module'

    # Formatting
    for col in range(1, 5):
        wb[sheetname].cell(1, col).style = m_header_title_style
        if col == 3:
            wb[sheetname].cell(1, col).font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False,
                                                   italic=True, color='FF000000')
        if col == 4:
            wb[sheetname].cell(1, col).font = Font(name='Geneva', charset=1, family=2.0, sz=9.0, bold=False,
                                                   italic=False, color='FF000000')
    # - POSITION
    # add line below sampling name
    row_n = 1
    row_insert_idx = 5
    for merged_cell in wb[sheetname].merged_cells.ranges:  # move merged cells downwards below row_insert_idx row
        if merged_cell.right[0][0] >= row_insert_idx:
            merged_cell.shift(0, row_n)
    wb[sheetname].insert_rows(row_insert_idx, row_n)  # insert row_n rows starting at row_insert_idx row
    for row in range(row_insert_idx, row_insert_idx + row_n):
        for col in range(1, wb[sheetname].max_column):
            wb[sheetname].cell(row, col).style = m_bkg_style

    wb[sheetname]['A6'].value = 'position'
    wb[sheetname]['C7'].value = 'start'
    wb[sheetname]['F7'].value = 'end'
    wb[sheetname]['C8'].value = 'degree'
    wb[sheetname]['D8'].value = 'minute'
    wb[sheetname]['E8'].value = 'second'
    wb[sheetname]['F8'].value = 'degree'
    wb[sheetname]['G8'].value = 'minute'
    wb[sheetname]['H8'].value = 'second'
    wb[sheetname]['A9'].value = 'latitude'
    wb[sheetname]['A10'].value = 'longitude'

    # Formatting
    for col in range(1, 8 + 1):
        wb[sheetname].cell(9, col).border = b_border
        if col > 2:
            wb[sheetname].style = m_data_style
    for row in range(7, 10 + 1):
        wb[sheetname].cell(row, 5).border = r_border
        wb[sheetname].cell(row, 6).border = l_border
        if row == 9:
            wb[sheetname].cell(row, 5).border = br_border
            wb[sheetname].cell(row, 6).border = bl_border

    # - DATE AND TIME
    # add line below sampling name
    row_n = 1
    row_insert_idx = 11
    for merged_cell in wb[sheetname].merged_cells.ranges:  # move merged cells downwards below row_insert_idx row
        if merged_cell.right[0][0] >= row_insert_idx:
            merged_cell.shift(0, row_n)
    wb[sheetname].insert_rows(row_insert_idx, row_n)  # insert row_n rows starting at row_insert_idx row
    for row in range(row_insert_idx, row_insert_idx + row_n):
        for col in range(1, wb[sheetname].max_column):
            wb[sheetname].cell(row, col).style = m_bkg_style

    wb[sheetname]['A12'].value = 'date and time'
    wb[sheetname]['C13'].value = 'start'
    wb[sheetname]['D13'].value = 'end'
    wb[sheetname]['A14'].value = 'date'
    wb[sheetname]['A15'].value = 'time'
    wb[sheetname]['A16'].value = 'timezone'

    # Formatting
    for row in [14, 15]:
        for col in range(1, 4 + 1):
            wb[sheetname].cell(row, col).border = b_border
    for row in range(13, 16 + 1):
        col = 4
        wb[sheetname].cell(row, col).border = l_border
        if row in [14, 15]:
            wb[sheetname].cell(row, col).border = bl_border

    # - ICE GEOMETRY
    # add line below sampling name
    row_n = 1
    row_insert_idx = 17
    for merged_cell in wb[sheetname].merged_cells.ranges:  # move merged cells downwards below row_insert_idx row
        if merged_cell.right[0][0] >= row_insert_idx:
            merged_cell.shift(0, row_n)
    wb[sheetname].insert_rows(row_insert_idx, row_n)  # insert row_n rows starting at row_insert_idx row
    for row in range(row_insert_idx, row_insert_idx + row_n):
        for col in range(1, wb[sheetname].max_column):
            wb[sheetname].cell(row, col).style = m_bkg_style

    value_entry = ['snow depth', 'average freeboard', 'average ice thickness', 'water depth', 'age', 'topography',
                   'environment', 'surface condition']
    for ii, row in enumerate(range(19, 27)):
        col = 1
        wb[sheetname].cell(row, col).value = value_entry[ii]

    # - ICE TEMPERATURE
    # add line below sampling name
    row_n = 1
    row_insert_idx = 27
    for merged_cell in wb[sheetname].merged_cells.ranges:  # move merged cells downwards below row_insert_idx row
        if merged_cell.right[0][0] >= row_insert_idx:
            merged_cell.shift(0, row_n)
    wb[sheetname].insert_rows(row_insert_idx, row_n)  # insert row_n rows starting at row_insert_idx row
    for row in range(row_insert_idx, row_insert_idx + row_n):
        for col in range(1, wb[sheetname].max_column):
            wb[sheetname].cell(row, col).style = m_bkg_style

    # - SAMPLING EVENT
    # add line below sampling name
    row_n = 1
    row_insert_idx = 33
    for merged_cell in wb[sheetname].merged_cells.ranges:  # move merged cells downwards below row_insert_idx row
        if merged_cell.right[0][0] >= row_insert_idx:
            merged_cell.shift(0, row_n)
    wb[sheetname].insert_rows(row_insert_idx, row_n)  # insert row_n rows starting at row_insert_idx row
    for row in range(row_insert_idx, row_insert_idx + row_n):
        for col in range(1, wb[sheetname].max_column):
            wb[sheetname].cell(row, col).style = m_bkg_style

    wb[sheetname]['A34'].value = 'sampling event'

    # - WEATHER INFORMATION
    wb[sheetname]['A40'].value = 'weather information'

    # - SAMPLING EVENT
    # add line below sampling name
    row_n = 1
    row_insert_idx = 46
    for merged_cell in wb[sheetname].merged_cells.ranges:  # move merged cells downwards below row_insert_idx row
        if merged_cell.right[0][0] >= row_insert_idx:
            merged_cell.shift(0, row_n)
    wb[sheetname].insert_rows(row_insert_idx, row_n)  # insert row_n rows starting at row_insert_idx row
    for row in range(row_insert_idx, row_insert_idx + row_n):
        for col in range(1, wb[sheetname].max_column):
            wb[sheetname].cell(row, col).style = m_bkg_style

    wb[sheetname]['A47'].value = 'general comments'

    # set cell geometry
    max_row = wb[sheetname].max_row
    for row in range(1, max_row + 1):
        wb[sheetname].row_dimensions[row].height = 12.75
        wb[sheetname].cell(row, wb['metadata-station'].max_column).style = m_bkg_style
    wb[sheetname].column_dimensions['A'].width = 1.76 * 14  # 1.76 in, fudge_factor = 13.97

    # - PROFILE ORIENTATION
    # -- ICE
    # Look for orientation of ice data
    data_sheetnames = wb.sheetnames
    for element in ['metadata-core', 'metadata-station', 'lists', 'snow', 'seawater']:
        if element in data_sheetnames:
            data_sheetnames.remove(element)
    # find sheetname with data
    data_sheet = {}
    for sheetname in data_sheetnames:
        depth_columns = []
        for row in range(1, 4):
            for col in range(1, wb[sheetname].max_column):
                str_condition = isinstance(wb[sheetname].cell(row, col).value, str)
                # For column with potential depth entry
                if str_condition and 'depth' in wb[sheetname].cell(row, col).value:
                    for drow in range(row, wb[sheetname].max_row):
                        if isinstance(wb[sheetname].cell(drow, col).value, (int, float)):
                            start_row = drow
                            depth_data = []
                            for drow in range(start_row, wb[sheetname].max_row):
                                depth_data.append(wb[sheetname].cell(drow, col).value)
                            depth_data = np.array(depth_data).astype(float)
                            depth_data = depth_data[np.where(~np.isnan(depth_data))]
                            if len(depth_data) > 0:
                                # read vertical reference if existing
                                if sheetname.lower() == 'salo18':
                                    data_sheet[sheetname] = [wb[sheetname]['C1'].value, wb[sheetname]['F1'].value]
                                else:
                                    data_sheet[sheetname] = [wb[sheetname]['C1'].value, wb[sheetname]['E1'].value]
                                break
                        if sheetname in data_sheet:
                            break
                if sheetname in data_sheet:
                    break
    # check orientation consistency:
    for ii, sheet in enumerate(data_sheet.keys()):
        if data_sheet[sheet][0] is None:
            logger.warning('%s - %s vertical reference is None' % (wb['metadata-core']['C1'].value, sheet))
        if data_sheet[sheet][1] is None:
            logger.warning('%s - %s vertical direction is None' % (wb['metadata-core']['C1'].value, sheet))

        if ii == 0 or vert_ref is None:
            vert_ref = data_sheet[sheet][0]
        if ii == 0 or vert_dir is None:
            vert_dir = data_sheet[sheet][1]
        else:
            if data_sheet[sheet][0] is not None and data_sheet[sheet][0] != vert_ref:
                logger.error(
                    '%s - vertical references are not consistant' % (wb['metadata-core']['C1'].value, sheet))
            if data_sheet[sheet][1] is not None and data_sheet[sheet][1] != vert_dir:
                logger.error(
                    '%s - vertical direction are not consistant' % (wb['metadata-core']['C1'].value, sheet))
    # update ice direction in metadata-core
    if vert_ref in vert_ref_list.formula1:
        wb['metadata-core']['D13'] = vert_ref
    if vert_dir in vert_dir_list.formula1:
        wb['metadata-core']['D14'] = vert_dir

    # -- SNOW
    sheetname = 'snow'
    data_sheet = {}
    for row in range(1, 4):
        for col in range(1, wb[sheetname].max_column):
            str_condition = isinstance(wb[sheetname].cell(row, col).value, str)
            # For column with potential depth entry
            if str_condition and 'depth' in wb[sheetname].cell(row, col).value:
                for drow in range(row, wb[sheetname].max_row):
                    if isinstance(wb[sheetname].cell(drow, col).value, (int, float)):
                        start_row = drow
                        depth_data = []
                        for drow in range(start_row, wb[sheetname].max_row):
                            depth_data.append(wb[sheetname].cell(drow, col).value)
                        depth_data = np.array(depth_data).astype(float)
                        depth_data = depth_data[np.where(~np.isnan(depth_data))]
                        if len(depth_data) > 0:
                            # read vertical reference if existing
                            data_sheet[sheetname] = [wb[sheetname]['C1'].value, wb[sheetname]['E1'].value]
                        break
                    if sheetname in data_sheet:
                        break
            if sheetname in data_sheet:
                break
    if len(data_sheet.keys()) > 1:
        # update ice direction in metadata-core
        if vert_ref in vert_ref_list.formula1:
            wb['metadata-core']['D15'] = vert_ref
        if vert_dir in vert_dir_list.formula1:
            wb['metadata-core']['D16'] = vert_dir

    # -- SEAWATER
    sheetname = 'seawater'
    data_sheet = {}
    for row in range(1, 4):
        for col in range(1, wb[sheetname].max_column):
            str_condition = isinstance(wb[sheetname].cell(row, col).value, str)
            # For column with potential depth entry
            if str_condition and 'depth' in wb[sheetname].cell(row, col).value:
                for drow in range(row, wb[sheetname].max_row):
                    if isinstance(wb[sheetname].cell(drow, col).value, (int, float)):
                        start_row = drow
                        depth_data = []
                        for drow in range(start_row, wb[sheetname].max_row):
                            depth_data.append(wb[sheetname].cell(drow, col).value)
                        depth_data = np.array(depth_data).astype(float)
                        depth_data = depth_data[np.where(~np.isnan(depth_data))]
                        if len(depth_data) > 0:
                            # read vertical reference if existing
                            data_sheet[sheetname] = [wb[sheetname]['C1'].value, wb[sheetname]['E1'].value]
                        break
                    if sheetname in data_sheet:
                        break
            if sheetname in data_sheet:
                break
    if len(data_sheet.keys()) > 1:
        # update ice direction in metadata-core
        if vert_ref in vert_ref_list.formula1:
            wb['metadata-core']['D17'] = vert_ref
        if vert_dir in vert_dir_list.formula1:
            wb['metadata-core']['D18'] = vert_dir

    # DATA UPDATE
    # - LISTS
    # Override latest `list` sheet
    if 'lists' in wb.sheetnames:
        list_sheet_index = wb._sheets.index(wb['lists'])
        del wb['lists']
    wb.create_sheet("lists", list_sheet_index)
    wb_source = openpyxl.load_workbook(os.path.join(pysic_fp, 'ressources/AAA_BB-YYYYMMDD-P-1.4.1-lists.xlsx'),
                                       data_only=True)
    copy_cells(wb_source['lists'], wb['lists'])  # copy all the cel values and styles
    copy_sheet_attributes(wb_source['lists'], wb['lists'])

    # - SALO18
    sheetname = 'salo18'
    if 'SALO18' in wb.sheetnames:
        wb['SALO18'].title = sheetname
        wb['salo181'].title = sheetname
    if 'salo18' in wb.sheetnames:
        # unmerge all cells
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)
        # remove all data validation
        row_idx = wb[sheetname].max_row
        for col in range(1, wb[sheetname].max_column):
            removeExistingCellDataValidation(wb[sheetname], wb[sheetname].cell(row_idx, col))

        # remove first line
        delete_row_with_merge(wb[sheetname], 1, 1)

        # remove depth center (C) if empty
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('C')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)
        wb[sheetname]['C1'].value = 'salinity'
        wb[sheetname]['D1'].value = None
        wb[sheetname]['C2'].value = 'ID'
        wb[sheetname]['G2'].value = 'temperature'

        # insert quality column for salinity,
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('E')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('C1:E1')
        wb[sheetname].merge_cells('F1:G1')

        # insert quality column for d18O,
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('K')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('I1:K1')
        wb[sheetname]['I2'].value = 'ID'

        # insert quality column for dD,
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('N')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('L1:N1')
        wb[sheetname]['L2'].value = 'ID'

        # delete column O (density)
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('O')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['C', 'I', 'L', 'O']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

    # - TEMP
    sheetname = 'temp'
    if 'TEMP' in wb.sheetnames:
        wb['TEMP'].title = sheetname
        if 'temp1' in wb.sheetnames:
            wb['temp1'].title = sheetname
    if sheetname in wb.sheetnames:
        # unmerge all cells
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)
        # remove first line
        row_n = 1
        row_delete_idx = 1
        delete_row_with_merge(wb[sheetname], row_delete_idx, row_n)
        removeExistingCellDataValidation(wb[sheetname], 'C1')
        removeExistingCellDataValidation(wb[sheetname], 'E1')

        # insert 1 column to move comment column to the right
        col_n = 1
        col_insert_idx = 3
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)

        wb[sheetname]['D1'].value = 'comment'
        wb[sheetname]['C2'].value = 'quality'
        wb[sheetname]['D2'].value = 'value'
        wb[sheetname]['C3'].value = '[0-9]'
        wb[sheetname]['D3'].value = '-'

        # formating
        max_row = 3 + data_row_n + 1
        l_border_col = ['B', 'D']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

    # - TEX
    sheetname = 'tex'
    if 'TEX' in wb.sheetnames:
        wb['TEX'].title = sheetname
        if 'tex1' in wb.sheetnames:
            wb['tex1'].title = sheetname
    if sheetname in wb.sheetnames:
        # unmerge all cell
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)

        # remove first line
        row_n = 1
        row_delete_idx = 1
        delete_row_with_merge(wb[sheetname], row_delete_idx, row_n)
        removeExistingCellDataValidation(wb[sheetname], 'C1')
        removeExistingCellDataValidation(wb[sheetname], 'E1')

        # remove data validation for the last line
        row_idx = wb[sheetname].max_row
        for col in range(1, wb[sheetname].max_column):
            removeExistingCellDataValidation(wb[sheetname], wb[sheetname].cell(row_idx, col))

        # remove column C to move texture column to the left
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('C')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # insert column to move comment column to the right
        col_n = 6
        col_insert_idx = openpyxl.utils.column_index_from_string('E')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)

        wb[sheetname]['C1'].value = 'texture'
        wb[sheetname]['E1'].value = 'inclusion'
        wb[sheetname]['F1'].value = 'description'
        wb[sheetname]['G1'].value = 'stratigraphy'
        wb[sheetname]['K1'].value = 'comment'
        subheader_list = ['value', 'quality', 'value', 'value', 'ID', 'type', 'quality', 'section', 'value']
        unit_list = ['-', '[0-9]', '-', '-', '-', '-', '[0-9]', '-', '-']
        for ii, col_idx in enumerate(range(openpyxl.utils.column_index_from_string('C'),
                                           openpyxl.utils.column_index_from_string('K') + 1)):
            wb[sheetname].cell(2, col_idx).value = subheader_list[ii]
            wb[sheetname].cell(3, col_idx).value = unit_list[ii]
        wb[sheetname].merge_cells('C1:D1')
        wb[sheetname].merge_cells('G1:J1')

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['C', 'G', 'K']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

        # remove data validation
        for row in range(3, max_row):
            removeExistingCellDataValidation(wb[sheetname], 'C' + str(row))
        dv_range = 'C3:C' + str(max_row - 1)
        wb[sheetname].add_data_validation(texture_dv)
        texture_dv.add(dv_range)
        dv_range = 'E3:E' + str(max_row - 1)
        wb[sheetname].add_data_validation(inclusion_dv)
        inclusion_dv.add(dv_range)
        dv_range = 'F3:F' + str(max_row - 1)
        wb[sheetname].add_data_validation(description_dv)
        description_dv.add(dv_range)

    # - ECO
    sheetname = 'eco'
    if 'ECO' in wb.sheetnames:
        wb['ECO'].title = sheetname
        if 'eco1' in wb.sheetnames:
            wb['eco1'].title = sheetname
    if sheetname in wb.sheetnames:
        # unmerge all cell
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)

        # remove first line
        row_n = 1
        row_delete_idx = 1
        delete_row_with_merge(wb[sheetname], row_delete_idx, row_n)
        removeExistingCellDataValidation(wb[sheetname], 'C1')
        removeExistingCellDataValidation(wb[sheetname], 'E1')

        # add column for field sample quality
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('C')
        wb[sheetname].insert_cols(col_insert_idx, col_n)

        wb[sheetname]['C1'] = 'field sample'
        wb[sheetname]['C2'] = 'ID'
        wb[sheetname]['D2'] = 'quality'
        wb[sheetname]['D3'] = '-'
        wb[sheetname]['D3'] = '[0-9]'
        wb[sheetname].merge_cells('C1:D1')

        # -- melted volume
        # add 2 column to the left of total volume:
        col_n = 2
        col_insert_idx = openpyxl.utils.column_index_from_string('E')
        wb[sheetname].insert_cols(col_insert_idx, col_n)

        # move added seawater column to the left of total volume
        wb[sheetname].move_range('H1:H' + str(wb[sheetname].max_row), rows=0, cols=-2, translate=True)

        wb[sheetname]['E1'] = 'melted volume'
        wb[sheetname]['E2'] = 'ID'
        wb[sheetname]['F2'] = 'added seawater volume'
        wb[sheetname]['G2'] = 'total volume'
        wb[sheetname]['H2'] = 'value'
        wb[sheetname]['E3'] = '-'
        wb[sheetname]['F3'] = 'L'
        wb[sheetname]['G3'] = 'L'
        wb[sheetname]['H3'] = 'L'
        wb[sheetname].merge_cells('E1:H1')

        # -- 'eco. data example'
        # insert 4 column
        col_n = 4
        col_insert_idx = openpyxl.utils.column_index_from_string('I')
        wb[sheetname].insert_cols(col_insert_idx, col_n)

        wb[sheetname]['I1'] = 'eco. data example'
        wb[sheetname]['I2'] = 'ID'
        wb[sheetname]['J2'] = 'volume'
        wb[sheetname]['K2'] = 'value'
        wb[sheetname]['L2'] = 'quality'
        wb[sheetname]['I3'] = '-'
        wb[sheetname]['J3'] = 'L'
        wb[sheetname]['K3'] = 'μg/l'
        wb[sheetname]['L3'] = '[0-9]'
        wb[sheetname].merge_cells('I1:L1')

        # modified nutrient entry:
        wb[sheetname]['M1'] = 'nutrient'
        wb[sheetname]['M2'] = 'ID'
        wb[sheetname]['N2'] = 'value'
        wb[sheetname]['M3'] = '-'
        wb[sheetname]['N3'] = '-'

        # remove extra column
        col_n = 24
        col_delete_idx = openpyxl.utils.column_index_from_string('O')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['E', 'M', 'O']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

    # - SNOW
    sheetname = 'snow'
    if 'SNOW' in wb.sheetnames:
        wb['SNOW'].title = sheetname + '_temp'
        wb[sheetname + '_temp'].title = sheetname
    if sheetname in wb.sheetnames:
        # unmerge all cell
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)
        # remove first line
        delete_row_with_merge(wb[sheetname], 1, 1)
        removeExistingCellDataValidation(wb[sheetname], 'C1')
        removeExistingCellDataValidation(wb[sheetname], 'E1')

        wb[sheetname]['C1'].value = 'salinity'
        wb[sheetname]['C2'].value = 'ID'
        wb[sheetname]['C3'].value = '-'

        # insert quality column for salinity,
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('E')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('C1:E1')
        wb[sheetname]['G1'].value = None
        wb[sheetname].merge_cells('F1:G1')
        wb[sheetname]['H2'].value = 'value'

        # insert quality column for d18O,
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('K')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('I1:K1')
        wb[sheetname]['I2'].value = 'ID'

        # insert quality column for dD,
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('N')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('L1:N1')
        wb[sheetname]['L2'].value = 'ID'

        # insert quality column for density,
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('Q')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(1, col_insert_idx - 2).value = 'density'
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(2, col_insert_idx + 1).value = 'value'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('O1:P1')

        # insert quality column for comment
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('R')
        insert_col_with_merge(wb[sheetname], col_insert_idx + 1, col_n)
        wb[sheetname].cell(1, col_insert_idx).value = 'comment'
        wb[sheetname].cell(2, col_insert_idx).value = 'value'
        wb[sheetname].cell(3, col_insert_idx).value = '-'

        # insert quality column for temperature_quality
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('V')
        col_tmp_idx = col_insert_idx - 2
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(1, col_insert_idx - 2).value = 'temperature'
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('T1:V1')

        # if nutrient
        delta_nuts = 0
        for col_idx in range(1, wb[sheetname].max_column):
            if wb[sheetname].cell(1, col_idx).value in ['Nutrient', 'nutrient']:
                col_nuts = col_idx
                delta_nuts = 3
                # insert quality column for nutrient_quality
                col_n = 1
                col_insert_idx = openpyxl.utils.column_index_from_string('Z')
                insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
                wb[sheetname].cell(1, col_nuts).value = 'nutrient'
                wb[sheetname].cell(2, col_nuts).value = 'ID'
                wb[sheetname].cell(2, col_nuts + 1).value = 'value'
                wb[sheetname].cell(3, col_nuts + 1).value = '-'
                wb[sheetname].cell(2, col_insert_idx).value = 'quality'
                wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
                wb[sheetname].merge_cells('X1:Z1')
                break
            else:
                pass

        # - eco sample: insert 3 column
        col_n = 4
        col_eco_n = col_n
        col_idx = openpyxl.utils.column_index_from_string('X') + delta_nuts + 1
        col_eco_idx = col_idx
        insert_col_with_merge(wb[sheetname], col_idx, col_n)
        wb[sheetname].cell(1, col_idx).value = 'eco sample'
        wb[sheetname].cell(2, col_idx).value = 'ID'
        wb[sheetname].cell(2, col_idx + 1).value = 'value'
        wb[sheetname].cell(2, col_idx + 2).value = 'quality'
        wb[sheetname].cell(3, col_idx).value = '-'
        wb[sheetname].cell(3, col_idx + 1).value = '-'
        wb[sheetname].cell(3, col_idx + 2).value = '[0-9]'
        merge_range = openpyxl.utils.get_column_letter(col_idx) + '1:' + openpyxl.utils.get_column_letter(
            col_idx + 2) + '1'
        wb[sheetname].merge_cells(merge_range)

        # - extra sample
        col_idx = openpyxl.utils.column_index_from_string('X') + delta_nuts + 1 + col_eco_n
        col_exs_idx = col_idx
        wb[sheetname].cell(1, col_idx + 2).value = 'extra sample'
        wb[sheetname].cell(2, col_idx + 2).value = 'ID'

        # - snow micropen
        col_idx = openpyxl.utils.column_index_from_string('X') + delta_nuts + 1 + col_eco_n + 4
        col_smp_idx = col_idx
        wb[sheetname].cell(1, col_idx).value = 'Snow micro pen SMP'
        wb[sheetname].cell(2, col_idx + 2).value = 'ID'
        wb[sheetname].cell(3, col_idx).value = '-'
        wb[sheetname].cell(3, col_idx + 1).value = '-'
        wb[sheetname].cell(3, col_idx + 2).value = '-'

        # - snow water equivalent
        col_n = 3
        col_idx = openpyxl.utils.column_index_from_string('X') + delta_nuts + 1 + col_eco_n + 4 + 4
        col_swe_idx = col_idx
        wb[sheetname].insert_cols(col_idx + 1, col_n)
        wb[sheetname].cell(1, col_idx).value = 'SWE'
        wb[sheetname].cell(2, col_idx).value = 'value'
        wb[sheetname].cell(2, col_idx + 1).value = 'snow depth'
        wb[sheetname].cell(2, col_idx + 2).value = 'quality'
        wb[sheetname].cell(2, col_idx + 3).value = 'comment'
        wb[sheetname].cell(3, col_idx).value = 'g'
        wb[sheetname].cell(3, col_idx + 1).value = 'cm'
        wb[sheetname].cell(3, col_idx + 2).value = '[0-9]'
        wb[sheetname].cell(3, col_idx + 3).value = '-'
        merge_range = openpyxl.utils.get_column_letter(col_idx) + '1:' + openpyxl.utils.get_column_letter(
            col_idx + col_n) + '1'
        wb[sheetname].merge_cells(merge_range)

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['C', 'I', 'L', 'O' 'R']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

        # extra formatting for snow
        bkg_col = [col_tmp_idx -1, col_nuts - 1, col_eco_idx - 1, col_exs_idx - 1, col_smp_idx - 1, col_swe_idx - 1]
        for row_idx in range(1, max_row):
            for col_idx in bkg_col:
                col = openpyxl.utils.get_column_letter(col_idx)
                wb[sheetname].cell(row_idx, col_idx).style = m_bkg_style
                # wb[sheetname].column_dimensions[col].width = 0.25 * 14  # 1.76 in, fudge_factor = 13.97

        for row_idx in range(5, max_row):
            for col_idx in range(col_swe_idx, col_swe_idx + 4):
                wb[sheetname].cell(row_idx, col_idx).style = m_bkg_style

        for row_idx in range(10, max_row):
            for col_idx in range(col_smp_idx, col_smp_idx + 3):
                wb[sheetname].cell(row_idx, col_idx).style = m_bkg_style

    # - DENSITY-VOLUME
    sheetname = 'density-volume'
    if 'Density-volume' in wb.sheetnames:
        wb['Density-volume'].title = sheetname
        if 'density-volume1' in wb.sheetnames:
            wb['density-volume1'].title = sheetname
    if sheetname in wb.sheetnames:
        # unmerge all cell
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)

        # remove first line
        row_n = 1
        row_delete_idx = 1
        delete_row_with_merge(wb[sheetname], row_delete_idx, row_n)
        removeExistingCellDataValidation(wb[sheetname], 'C1')
        removeExistingCellDataValidation(wb[sheetname], 'E1')

        # remove field column (C) if empty
        col_n = 1
        col_delete_idx = 3
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # insert 2 column to the right of C
        col_n = 2
        col_insert_idx = 4
        wb[sheetname].insert_cols(col_insert_idx, col_n)

        # move density column L, 8 to the left
        wb[sheetname].move_range('L1:L' + str(wb[sheetname].max_row), rows=0, cols=-8, translate=True)

        wb[sheetname]['C1'].value = 'density'
        wb[sheetname]['C2'].value = 'ID'
        wb[sheetname]['D2'].value = 'value'
        wb[sheetname]['E2'].value = 'quality'
        wb[sheetname]['C3'].value = 'value'
        wb[sheetname]['D3'].value = 'kg / m3'
        wb[sheetname]['E3'].value = '[0-9]'
        wb[sheetname].merge_cells('C1:E1')

        # -- thickness
        wb[sheetname].merge_cells('F1:J1')

        # remove column K:
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('K')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # -- mass
        wb[sheetname]['K1'].value = 'mass'
        wb[sheetname]['K2'].value = 'value'
        wb[sheetname]['K3'].value = 'kg'

        wb[sheetname]['L1'].value = 'comment'
        wb[sheetname]['L2'].value = 'value'
        wb[sheetname]['L3'].value = '-'

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['C', 'F', 'K', 'L']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

    # - DENSITY-DENSIMETRY
    sheetname = 'density-densimetry'
    if 'Density-densimetry' in wb.sheetnames:
        wb['Density-densimetry'].title = sheetname
        if 'density-densimetry1' in wb.sheetnames:
            wb['density-densimetry1'].title = sheetname
    if sheetname in wb.sheetnames:
        # remove all data validation
        row_idx = wb[sheetname].max_row
        for col in range(1, wb[sheetname].max_column):
            removeExistingCellDataValidation(wb[sheetname], wb[sheetname].cell(row_idx, col))
        # unmerge all cell
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)
        # remove first line
        delete_row_with_merge(wb[sheetname], 1, 1)

        # remove field column (C) if empty
        col_n = 1
        col_delete_idx = 3
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # insert 2 column to the right of C
        col_n = 2
        col_insert_idx = 4
        wb[sheetname].insert_cols(col_insert_idx, col_n)

        # move density column L, 8 to the left
        wb[sheetname].move_range('H1:H' + str(wb[sheetname].max_row), rows=0, cols=-4, translate=True)
        wb[sheetname]['C1'].value = 'density'
        wb[sheetname]['C2'].value = 'ID'
        wb[sheetname]['D2'].value = 'value'
        wb[sheetname]['E2'].value = 'quality'
        wb[sheetname]['C3'].value = 'value'
        wb[sheetname]['D3'].value = 'kg / m3'
        wb[sheetname]['E3'].value = '[0-9]'
        wb[sheetname].merge_cells('C1:E1')

        wb[sheetname]['F1'].value = 'mass'
        wb[sheetname]['F2'].value = 'air'
        wb[sheetname]['G2'].value = 'liquid'
        wb[sheetname]['F3'].value = 'kg / m3'
        wb[sheetname]['G3'].value = 'kg / m3'
        wb[sheetname].merge_cells('F1:G1')

        # remove column H:
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('H')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n)

        # - comment
        wb[sheetname]['H1'].value = 'comment'
        wb[sheetname]['H2'].value = 'value'
        wb[sheetname]['H3'].value = '-'

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['C', 'F', 'H']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

    # - SEAWATER
    sheetname = 'seawater'
    if sheetname in wb.sheetnames:
        # unmerge all cells
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)
        # remove all data validation
        row_idx = wb[sheetname].max_row
        for col in range(1, wb[sheetname].max_column):
            removeExistingCellDataValidation(wb[sheetname], wb[sheetname].cell(row_idx, col))
        # remove first line
        delete_row_with_merge(wb[sheetname], 1, 1)

        # if column C is empty, use it for ID
        col_delete_idx = openpyxl.utils.column_index_from_string('C')
        flag_empty = True
        for row_idx in range(4, wb[sheetname].max_row):
            for col_idx in range(col_delete_idx, col_delete_idx + col_n):
                if wb[sheetname].cell(row_idx, col_idx).value not in [None, '']:
                    cell = openpyxl.utils.get_column_letter(col_idx) + str(row_idx)
                    logger.error('%s - %s: cell %s is not empty impossible to delete column' % (
                    wb['metadata-core']['C1'].value, sheetname, cell))
                    flag_empty = False
                    break
                else:
                    pass
        if flag_empty:
            wb[sheetname]['C1'].value = 'salinity'
            wb[sheetname]['D1'].value = None
            wb[sheetname]['C2'].value = 'ID'
            wb[sheetname]['D2'].value = 'value'

        # if column E is empty, use it for salinity quality
        col_delete_idx = openpyxl.utils.column_index_from_string('E')
        flag_empty = True
        for row_idx in range(4, wb[sheetname].max_row):
            for col_idx in range(col_delete_idx, col_delete_idx + col_n):
                if wb[sheetname].cell(row_idx, col_idx).value not in [None, '']:
                    cell = openpyxl.utils.get_column_letter(col_idx) + str(row_idx)
                    logger.error('%s - %s: cell %s is not empty impossible to delete column' % (
                    wb['metadata-core']['C1'].value, sheetname, cell))
                    flag_empty = False
                    break
                else:
                    pass
        if flag_empty:
            wb[sheetname].cell(1, col_insert_idx).value = None
            wb[sheetname].cell(2, col_insert_idx).value = 'quality'
            wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'

        wb[sheetname]['G1'].value = None
        wb[sheetname]['G2'].value = 'sample temp'
        wb[sheetname].merge_cells('F1:G1')

        # insert ID and quality column for d18O, respectively before and after:
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('I')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(1, col_insert_idx).value = 'd18O'
        wb[sheetname].cell(2, col_insert_idx).value = 'ID'
        wb[sheetname].cell(3, col_insert_idx).value = '-'
        col_insert_idx = openpyxl.utils.column_index_from_string('K')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('I1:K1')

        # insert ID and quality column for d18O, respectively before and after:
        col_n = 1
        col_insert_idx = openpyxl.utils.column_index_from_string('L')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(1, col_insert_idx).value = 'dD'
        wb[sheetname].cell(2, col_insert_idx).value = 'ID'
        wb[sheetname].cell(3, col_insert_idx).value = '-'
        col_insert_idx = openpyxl.utils.column_index_from_string('N')
        insert_col_with_merge(wb[sheetname], col_insert_idx, col_n)
        wb[sheetname].cell(2, col_insert_idx).value = 'quality'
        wb[sheetname].cell(3, col_insert_idx).value = '[0-9]'
        wb[sheetname].merge_cells('L1:N1')

        # remove density column if empty
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('O')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # remove sample ID column if empty
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('O')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # - comment
        col_idx = openpyxl.utils.column_index_from_string('O')
        wb[sheetname].cell(2, col_idx).value = 'value'
        wb[sheetname].cell(3, col_idx).value = '-'

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['C', 'I', 'L', 'O']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

    # - SEDIMENT
    sheetname = 'sediment'
    if sheetname in wb.sheetnames:
        # remove all data validation
        row_idx = wb[sheetname].max_row
        for col in range(1, wb[sheetname].max_column):
            removeExistingCellDataValidation(wb[sheetname], wb[sheetname].cell(row_idx, col))

        # remove first line
        delete_row_with_merge(wb[sheetname], 1, 1)

        # insert row for subheader
        wb[sheetname].insert_rows(2, 1)
        wb[sheetname]['A2'].value = 'value'
        wb[sheetname]['B2'].value = 'value'

        # remove depth center (C) if empty
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('C')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # remove salinity if empty
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('C')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 4)

        # - melted volume: add 2 columns
        col_n = 1
        col_idx = openpyxl.utils.column_index_from_string('C')
        wb[sheetname].insert_cols(col_idx, col_n)
        wb[sheetname].cell(1, col_idx).value = 'melted volume'
        wb[sheetname].cell(1, col_idx + 1).value = None
        wb[sheetname].cell(2, col_idx).value = 'ID'
        wb[sheetname].cell(2, col_idx + 1).value = 'value'
        wb[sheetname].cell(3, col_idx).value = '-'
        wb[sheetname].cell(3, col_idx + 1).value = 'l'

        # - sediment mass: add 1 column
        col_n = 1
        col_idx = openpyxl.utils.column_index_from_string('E')
        wb[sheetname].insert_cols(col_idx, col_n)
        wb[sheetname].cell(1, col_idx).value = 'sediment mass'
        wb[sheetname].cell(1, col_idx + 1).value = None
        wb[sheetname].cell(2, col_idx).value = 'value'
        wb[sheetname].cell(2, col_idx + 1).value = 'quality'
        wb[sheetname].cell(3, col_idx).value = 'g'
        wb[sheetname].cell(3, col_idx + 1).value = '[0-9]'
        cell_range = openpyxl.utils.get_column_letter(col_idx) + '1:' + openpyxl.utils.get_column_letter(
            col_idx + 1) + '1'
        wb[sheetname].merge_cells(cell_range)

        # - particulate mass: add 1 column
        col_n = 1
        col_idx = openpyxl.utils.column_index_from_string('G')
        wb[sheetname].insert_cols(col_idx, col_n)
        wb[sheetname].cell(1, col_idx).value = 'particulate mass'
        wb[sheetname].cell(1, col_idx + 1).value = None
        wb[sheetname].cell(2, col_idx).value = 'value'
        wb[sheetname].cell(2, col_idx + 1).value = 'quality'
        wb[sheetname].cell(3, col_idx).value = 'g'
        wb[sheetname].cell(3, col_idx + 1).value = '[0-9]'
        cell_range = openpyxl.utils.get_column_letter(col_idx) + '1:' + openpyxl.utils.get_column_letter(
            col_idx + 1) + '1'
        wb[sheetname].merge_cells(cell_range)

        # - comment
        wb[sheetname]['I2'].value = 'value'
        wb[sheetname]['I3'].value = '-'

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['C', 'E', 'G', 'I']
        worksheetFormatting(wb[sheetname], max_row, l_border_col)

    # - CT
    sheetname = 'ct'
    if 'CT' in wb.sheetnames:
        wb['CT'].title = '_temp'
        wb['_temp'].title = sheetname
    if sheetname in wb.sheetnames:
        # unmerge all cells
        while len(wb[sheetname].merged_cells.ranges) > 0:
            merged_cells = wb[sheetname].merged_cells.ranges[0].coord
            wb[sheetname].unmerge_cells(merged_cells)
        # remove all data validation
        row_idx = wb[sheetname].max_row
        for col in range(1, wb[sheetname].max_column):
            removeExistingCellDataValidation(wb[sheetname], wb[sheetname].cell(row_idx, col))
        # remove first line
        delete_row_with_merge(wb[sheetname], 1, 1)

        # insert topheader row
        wb[sheetname].insert_rows(1, 1)

        # remove depth center (C) if empty
        col_n = 1
        col_delete_idx = openpyxl.utils.column_index_from_string('C')
        delete_col_with_merge(wb[sheetname], col_delete_idx, col_n, True, 5)

        # -
        topheader_list = ['', 'tar', 'sample', 'sample', 'ice', 'brine']
        header_list = ['ID', 'mass', 'mass with tar', 'mass', 'mass', 'mass']
        subheader_list = ['value', 'value', 'value', 'value', 'value', 'value']
        unit_list = ['-', 'kg', 'kg', 'kg', 'kg', 'kg']
        for ii, col_idx in enumerate(range(3, 9)):
            wb[sheetname].cell(1, col_idx).value = topheader_list[ii]
            wb[sheetname].cell(2, col_idx).value = header_list[ii]
            wb[sheetname].cell(3, col_idx).value = subheader_list[ii]
            wb[sheetname].cell(4, col_idx).value = unit_list[ii]

        # - ice: add column after salinity_value
        col_n = 1
        col_idx = openpyxl.utils.column_index_from_string('K')
        wb[sheetname]['I1'].value = 'ice'
        wb[sheetname]['I2'].value = 'salinity'
        wb[sheetname]['I3'].value = 'ID'
        wb[sheetname]['J3'].value = 'value'
        wb[sheetname]['K3'].value = 'quality'
        wb[sheetname]['K4'].value = '[0-9]'
        wb[sheetname]['L2'].value = 'conductivity'
        wb[sheetname]['L3'].value = 'value'
        wb[sheetname]['M3'].value = 'sample temperature'
        wb[sheetname]['N2'].value = 'specific conductance'
        wb[sheetname]['N3'].value = 'value'
        wb[sheetname].merge_cells('I1:N1')
        wb[sheetname].merge_cells('I2:K2')
        wb[sheetname].merge_cells('L2:M2')

        # - brine
        col_n = 1
        col_idx = openpyxl.utils.column_index_from_string('Q')
        wb[sheetname]['O1'].value = 'ice'
        wb[sheetname]['O2'].value = 'salinity'
        wb[sheetname]['O3'].value = 'ID'
        wb[sheetname]['P3'].value = 'value'
        wb[sheetname]['Q3'].value = 'quality'
        wb[sheetname]['Q4'].value = '[0-9]'
        wb[sheetname]['R2'].value = 'conductivity'
        wb[sheetname]['R3'].value = 'value'
        wb[sheetname]['S3'].value = 'sample temperature'
        wb[sheetname]['T2'].value = 'specific conductance'
        wb[sheetname]['T3'].value = 'value'
        wb[sheetname].merge_cells('O1:T1')
        wb[sheetname].merge_cells('O2:Q2')
        wb[sheetname].merge_cells('R2:S2')

        # - comment
        wb[sheetname]['U1'].value = 'comment'
        wb[sheetname]['U3'].value = 'comments'
        wb[sheetname]['U4'].value = '-'

        # formatting
        max_row = 3 + data_row_n + 1
        l_border_col = ['F', 'I', 'O', 'U']
        styleDict = {1: m_header_style, 2: m_header_style, 3: m_subheader_l_style, 4: m_unit_style}
        worksheetFormatting(wb[sheetname], max_row, l_border_col, styleDict)

    # - LOCATIONS
    sheetname = 'locations'
    if sheetname in wb.sheetnames:
        list_sheet_index = wb._sheets.index(wb[sheetname])
        del wb[sheetname]
    else:
        list_sheet_index = len(wb._sheets)
    wb.create_sheet(sheetname, list_sheet_index)
    wb_source = openpyxl.load_workbook(os.path.join(pysic_fp, 'ressources/AAA_BB-YYYYMMDD-P-1.4.1-lists.xlsx'),
                                       data_only=True)
    copy_cells(wb_source[sheetname], wb[sheetname])  # copy all the cel values and styles
    copy_sheet_attributes(wb_source[sheetname], wb[sheetname])

    wb['metadata-station']['C1'] = '1.4.1'
    wb.active = wb['metadata-station']


def version_1_4_1_to_1_4_2(wb):
    # Update ice core version from 1.4.1 to 1.4.2
    # Update sheet name from 'metadata-coring' to 'metadata-station'
    if 'metadata-coring' in wb.sheetnames:
        wb['metadata-coring'].title = 'metadata-station'
        logger.info("%s\t\tupdate 'metadata-coring' sheet title to 'metadata-station'")
    wb['metadata-station']['C1'].value = '1.4.2'


def formatting(ic_path, backup=True):
    pass


###############
## Copy a sheet with style, format, layout, ect. from one Excel file to another Excel file
## Please add the ..path\\+\\file..  and  ..sheet_name.. according to your desire.

def insert_row_with_merge(worksheet, row_insert_idx, row_n=1):
    # move merged cells downwards below row_insert_idx row
    for merged_cell in worksheet.merged_cells.ranges:
        if merged_cell.right[0][0] > row_insert_idx:
            merged_cell.shift(0, row_n)
    # insert row_n rows starting at row_insert_idx row
    worksheet.insert_rows(row_insert_idx, row_n)

def delete_row_with_merge(worksheet, row_insert_idx, row_n=1):
    # move merged cells downwards below row_insert_idx row
    for merged_cell in worksheet.merged_cells.ranges:
        if merged_cell.right[0][0] > row_insert_idx:
            merged_cell.shift(0, row_n)
    # remove data validation
    for row_idx in range(row_insert_idx, row_insert_idx + row_n):
        for col_idx in range(1, worksheet.max_column):
            removeExistingCellDataValidation(worksheet, worksheet.cell(row_idx, col_idx))
    # insert row_n rows starting at row_insert_idx row
    worksheet.delete_rows(row_idx, row_n)
def insert_col_with_merge(worksheet, col_insert_idx, col_n=1):
    for merged_cell in worksheet.merged_cells.ranges:
        if merged_cell.left[0][1] >= col_insert_idx:
            merged_cell.shift(col_n, 0)
    worksheet.insert_cols(col_insert_idx, col_n)


def delete_col_with_merge(worksheet, col_delete_idx, col_n=1, check_empty=False, check_row_start=1):
    flag_empty = True
    if check_empty:
        for row_idx in range(check_row_start, worksheet.max_row):
            for col_idx in range(col_delete_idx, col_delete_idx + col_n):
                if worksheet.cell(row_idx, col_idx).value not in [None, '']:
                    cell = openpyxl.utils.get_column_letter(col_idx) + str(row_idx)
                    logging.error('\t\t-%s: cell %s is not empty impossible to delete column' %(worksheet.title, cell))
                    flag_empty = False
                    break
                else:
                    pass
    else:
        pass
    if flag_empty:
        for merged_cell in worksheet.merged_cells.ranges:
            if merged_cell.left[0][1] >= col_delete_idx:
                merged_cell.shift(-col_n, 0)
        worksheet.delete_cols(col_delete_idx, col_n)

def correctDataRowNumber(worksheet, max_row):
    """"
    Add or remove rows  for data entry to match the target number. Only remove row if empty
    """

    # add or remove extra data row as needed
    row_n = max_row - worksheet.max_row
    if row_n > 0:
        row_insert_idx = worksheet.max_row
        insert_row_with_merge(worksheet, row_insert_idx, row_n)
    elif row_n < 0:
        row_n = -row_n
        row_insert_idx = max_row
        flag_empty = True
        # only if no data are present:
        for row_idx in range(row_insert_idx, row_insert_idx + row_n):
            for col_idx in range(1, worksheet.max_column):
                if worksheet.cell(row_idx, col_idx).value not in [None, '']:
                    print(openpyxl.utils.get_column_letter(col_idx)+str(row_idx))
                    flag_empty = False
                else:
                    pass
        if flag_empty:
            delete_row_with_merge(worksheet, row_insert_idx, row_n)


def stylePainter(worksheet, col_comment_idx, max_col, max_row, styleDict={1:m_header_style, 2:m_subheader_l_style, 3:m_unit_style}):
    for row in range(1, worksheet.max_row):
        for col in range(1, col_comment_idx + 1):
            if row in styleDict.keys():
                worksheet.cell(row, col).style = styleDict[row]
            else:
                worksheet.cell(row, col).style = m_data_style
        for col in range(col_comment_idx + 1, max_col + 1):
            worksheet.cell(row, col).style = m_bkg_style

    for col in range(1, max_col + 1):
        worksheet.cell(max_row, col).style = m_bkg_style

    # set row height
    worksheet.row_dimensions[1].height = worksheet.row_dimensions[2].height
    for row in range(2, max_row + 1):
        worksheet.row_dimensions[row].height = 12.75


def cleanWorksheet(worksheet, col_comment_idx, max_col, max_row, clear_all=False):
    if clear_all:
        for row in range(1, worksheet.max_row + 1):
            for col in range(max_col + 1, worksheet.max_column):
                worksheet.cell(row, col).value = None
                worksheet.cell(row, col).fill = noFill
                worksheet.cell(row, col).border = noBorder
        for row in range(max_row, worksheet.max_row + 1):
            for col in range(1, max_col + 26):
                worksheet.cell(row, col).value = None
                worksheet.cell(row, col).fill = noFill
                worksheet.cell(row, col).border = noBorder
    else:
        for row in range(1, worksheet.max_row + 1):
            for col in range(col_comment_idx + 4, max_col + 26):
                try:
                    worksheet.cell(row, col).value = None
                except AttributeError:
                    pass
                worksheet.cell(row, col).fill = noFill
                worksheet.cell(row, col).border = noBorder
        for row in range(max_row+1, worksheet.max_row + 1):
            for col in range(1, max_col + 26):
                try:
                    worksheet.cell(row, col).value = None
                except AttributeError:
                    pass
                worksheet.cell(row, col).fill = noFill
                worksheet.cell(row, col).border = noBorder

def worksheetFormatting(worksheet, max_row, l_border_col=[], styleDict={1:m_header_style, 2:m_subheader_l_style, 3:m_unit_style}):
    import numpy as np
    # find last column with header
    for col in list(range(1, worksheet.max_column))[::-1]:
        if worksheet.cell(1, col).value not in [None, '']:
            col_comment_idx = col
            cell = worksheet.cell(1, col)
            for mergedCell in worksheet.merged_cells.ranges:
                if cell.coordinate in mergedCell:
                    col_comment_idx = mergedCell.max_col
            break
    max_col = int(np.ceil(col_comment_idx / 26)) * 26

    # add or remove extra data row as needed
    correctDataRowNumber(worksheet, max_row)

    # style and fill
    stylePainter(worksheet, col_comment_idx, max_col, max_row, styleDict=styleDict)

    # border
    for row_idx in range(1, max_row):
        for col in l_border_col:
            col_idx = openpyxl.utils.column_index_from_string(col)
            worksheet.cell(row_idx, col_idx).border = l_border

    # clear empty cell out of data
    cleanWorksheet(worksheet, col_comment_idx, max_col, max_row)


from copy import copy

def removeExistingCellDataValidation(worksheet, cell):
    toRemove = []

    # Append all validation rules for cell to be removed.
    for validation in worksheet.data_validations.dataValidation:
        if validation.__contains__(cell):
            toRemove.append(validation)

    # Process all data validation rules set for removal.
    for rmValidation in toRemove:
        worksheet.data_validations.dataValidation.remove(rmValidation)

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
