


#                             # Modify filename in case of ECO core does not follow the short name convention
#                             corename_dict = {'CHLA': 'ECO1A',
#                                          'PROD': 'ECO1B',
#                                          'PIGS': 'ECO1C',
#                                          'ALGAE': 'ECO1D',
#                                          'DNA1': 'ECO2A',
#                                          'DNA2':'ECO2B',
#                                          'RNA': 'ECO2C'}
#                             org_ic_name = ic_name
#                             for type in corename_dict.keys():
#                                 if type in ic_name:
#                                     ic_name = org_ic_name.replace(type, corename_dict[type])
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(org_ic_name + '\tName ' + org_ic_name + 'updated to ' + ic_name +'\n')
#                                     with open(update_file, 'a') as f:
#                                         f.writelines(org_ic_name + '\tName ' + org_ic_name + 'updated to ' + ic_name +'\n')
#
#                                     # add major update in the update list of the metadata-core
#                                     major_update.append(['Core name updated from ' + org_ic_name + ' to ' + ic_name])
#
#
#                             # ice thickness C7 > D7
#                             if ic_data['metadata-core']['C7'].value == None:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-core\tMissing ice thickness')
#                             elif isinstance(ic_data['metadata-core']['C7'].value, (float, int)):
#                                 if ic_data['metadata-core']['C7'].value > m_unit:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-core\tCheck unit for ice thickness\n')
#                                     with open(update_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-core\tIce thickness likely in cm, change to m\n')
#                                     ic_new['metadata-core']['D7'].value = ic_data['metadata-core']['C7'].value/100
#                                 else:
#                                     ic_new['metadata-core']['D7'].value = ic_data['metadata-core']['C7'].value
#                             else:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-core\tIce thickness is not a number\n')
#                                 ic_new['metadata-core']['D7'].value = ic_data['metadata-core']['C7'].value
#
#                             # Ice draft C8 > D8
#                             if ic_data['metadata-core']['C8'].value is None:
#                                 with open(error_file, 'a') as f:
#                                     f.write(ic_name + '\tmetadata-core\tMissing ice draft\n')
#                                 if ic_data['metadata-core']['C9'].value is not None:
#                                     if isinstance(ic_data['metadata-core']['C9'].value, (float, int)):
#                                         with open(update_file, 'a') as f:
#                                             f.writelines(ic_name + '\tmetadata-core\tIce draft computed with Hi - Hf\n')
#                                         with open(update_file, 'a') as f:
#                                             f.writelines(ic_name + '\tmetadata-core\tSet measured for ice freeboard\n')
#                                             f.writelines(ic_name + '\tmetadata-core\tSet computed for ice draft\n')
#
#                                         ic_new['metadata-core']['E8'].value = 'computed from ice thickness and freeboard'
#                                         ic_new['metadata-core']['C8'].value = ic_data['metadata-core']['C7'].value - \
#                                                                                   ic_data['metadata-core']['C9'].value
#                                         ic_new['metadata-core']['D8'].fill.start_color.value = ic_new['metadata-core']['D9'].fill.start_color.value
#
#                                         ic_new['metadata-core']['E9'].value = 'measured'
#                                         ic_new['metadata-core']['D9'].fill.start_color.value = ic_new['metadata-core']['D7'].fill.start_color.value
#
#                                     elif isinstance(ic_data['metadata-core']['C9'].value, str):
#                                         # TODO: create evaulate simple function
#
#                                         # ice thickness C7 > D7
#                                         if ic_data['metadata-core']['C7'].value == None:
#                                             with open(error_file, 'a') as f:
#                                                 f.write(ic_name + '\tmetadata-core\tMissing ice thickness\n')
#                                         elif ic_data['metadata-core']['C7'].value > m_unit:
#                                             with open(error_file, 'a') as f:
#                                                 f.write(ic_name + '\tmetadata-core\tCheck unit for ice thickness\n')
#                                             with open(update_file, 'a') as f:
#                                                 f.write(ic_name + '\tmetadata-core\tIce thickness likely in cm, change to m\n')
#                                         ic_new['metadata-core']['D7'].value = ic_data['metadata-core']['C7'].value / 100
#                                     else:
#                                         ic_new['metadata-core']['D7'].value = ic_data['metadata-core']['C7'].value
#                         elif isinstance(ic_data['metadata-core']['C8'], (float, int)):
#                             if ic_data['metadata-core']['C8'].value > m_unit:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-core\tCheck unit for ice thickness\n')
#                                 with open(update_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-core\tIce draft likely in cm, change to m\n')
#                                 ic_new['metadata-core']['D8'].value = ic_data['metadata-core']['C8'].value / 100
#                             else:
#                                 ic_new['metadata-core']['D8'].value = ic_data['metadata-core']['C8'].value
#                         else:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-core\tIce thickness is not a number\n')
#                             ic_new['metadata-core']['D8'].value = ic_data['metadata-core']['C8'].value
#
#                         # Ice freeboard D9 = D7-D8 or C9 > D9:
#                         if ic_data['metadata-core']['C9'].value is None:
#                             if ic_new['metadata-core']['D9'].value is None:
#                                 if not isinstance(ic_new['metadata-core']['D8'].value, str) and ic_new['metadata-core']['D8'].value is not None and ic_new['metadata-core']['D7'].value is not None:
#                                     ic_new['metadata-core']['D9'].value = ic_new['metadata-core']['D7'].value - ic_new['metadata-core'][
#                                         'D8'].value
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-core\tUnable to compute ice freeboard\n')
#                             elif isinstance(ic_new['metadata-core']['D9'].value, (float, int)):
#                                 if ic_new['metadata-core']['D8'].value is not None and ic_new['metadata-core']['D7'].value is not None:
#                                     hf = ic_new['metadata-core']['D7'].value - ic_new['metadata-core']['D8'].value
#                                     if hf != ic_new['metadata-core']['D9'].value:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tmetadata-core\tExisting freeboard hf does not match with hi-hd\n')
#                         elif isinstance(ic_data['metadata-core']['C9'].value, (float, int)):
#                             if ic_new['metadata-core']['D8'].value is not None and ic_new['metadata-core']['D7'].value is not None:
#                                 hf = ic_new['metadata-core']['D7'].value - ic_new['metadata-core']['D8'].value
#                                 if hf != ic_new['metadata-core']['D9'].value:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-core\tExisting freeboard hf does not match with hi-hd\n')
#                         elif isinstance(ic_data['metadata-core']['C9'].value, (str)):
#                             if ic_data['metadata-core']['C9'].value == '=C7-C8':
#                                 if ic_new['metadata-core']['D8'].value is not None and ic_new['metadata-core']['D7'].value is not None:
#                                     ic_new['metadata-core']['D9'].value = ic_new['metadata-core']['D7'].value - ic_new['metadata-core']['D8'].value
#                                     with open(update_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-core\tFreeboard computed as hi-hd\n')
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-core\tUnable to compute ice freeboard\n')
#                             else:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-core\tFreeboard is not a number\n')
#
#                         ## Instrument
#                         # Look for row index with "INSTRUMENTS" in new file
#                         ii_row = 1
#                         while ii_row < ic_new['metadata-core'].max_row:
#                             cell = str('A%.0f' %ii_row)
#                             cell_value = ic_new['metadata-core'][cell].value
#                             if isinstance(cell_value, str) and cell_value.startswith('INSTRUMENTS'):
#                                 ver_row = ii_row + 1
#                                 break
#                             ii_row += 1
#
#                         # Look for row index with "INSTRUMENTS" in original
#                         ii_row = 1
#                         while ii_row < ic_data['metadata-core'].max_row:
#                             cell = str('A%.0f' %ii_row)
#                             cell_value = ic_data['metadata-core'][cell].value
#                             if isinstance(cell_value, str) and cell_value.startswith('INSTRUMENTS'):
#                                 inst_row_start = ii_row + 1
#                             if isinstance(cell_value, str) and cell_value.startswith('DATA VERSION'):
#                                 inst_row_end = ii_row - 2
#                             ii_row += 1
#
#                         for ii_row, row in enumerate(range(inst_row_start, inst_row_end+1)):
#                             if ii_row > 1 and row < inst_row_end:
#                                 ic_new['metadata-core'].insert_rows(ver_row + ii_row)
#                                 for col in opxl.utils.get_column_interval('I', 'Z'):
#                                     ic_new['metadata-core'][col + str('%.0f' % (ver_row + ii_row))].fill = blankFILL
#                                 for col in opxl.utils.get_column_interval('A', 'B'):
#                                     ic_new['metadata-core'][col + str('%.0f' % (ver_row + ii_row))].fill = lightgFILL
#                                 ic_new['metadata-core'].merge_cells(str('C%.0f:H%.0f' %(ver_row + ii_row, ver_row + ii_row)))
#                                 for col in opxl.utils.get_column_interval('A', 'H'):
#                                     ic_new['metadata-core'][col + str('%.0f' % (ver_row + ii_row))].border = opxl.styles.Border(bottom=opxl.styles.Side(border_style='thin', color='000000'))
#                                 ic_new['metadata-core'].merge_cells(str('C%.0f:H%.0f' %(ver_row + ii_row + 1, ver_row + ii_row + 1)))
#                                 ic_new['metadata-core'][str('C%.0f' %(ver_row + ii_row + 1))].alignment = opxl.styles.Alignment(horizontal='left', vertical='center')
#                             ic_new['metadata-core']['A' + str('%.0f' % (ver_row + ii_row))].value = ic_data['metadata-core']['A' + str('%.0f' % (row ))].value
#                             ic_new['metadata-core']['C' + str('%.0f' % (ver_row + ii_row))].value = ic_data['metadata-core']['C' + str('%.0f' % (row))].value
#
#                         # DataVersion
#                         # Look for row index of data entry version in new_ic
#                         ii_row = 1
#                         while ii_row < ic_new['metadata-core'].max_row:
#                             cell = str('A%.0f' %ii_row)
#                             if ic_new['metadata-core'][cell].value == 'VERSION':
#                                 ver_row = ii_row+2
#                                 break
#                             ii_row += 1
#
#                         # Look for row index of data entry version in data_ic
#                         ii_row = 1
#                         max_row = ic_data['metadata-core'].max_row
#                         while ii_row < max_row:
#                             cell = str('A%.0f' %ii_row)
#                             if ic_data['metadata-core'][cell].value == 'DATA VERSION':
#                                 jj_row = ii_row
#                                 break
#                             ii_row +=1
#
#                         # copy information:
#                         drow = 0
#                         while ii_row + drow <= max_row:
#                             new_row = str('%.0f' % (ver_row + drow))
#                             row = str('%.0f' % (ii_row + 1 + drow))
#
#                             # version number, date and modification (A, B, C > A, B, E)
#                             #TODO: need to process versionning x.y.z
#
#                             # author
#                             author = 'Marc Oggier'
#                             if drow == 0:
#                                 if ic_leg == 2:
#                                     author = 'Dmitry V. Divine'
#                                 elif ic_leg == 3:
#                                     author = 'Stevens Fons'
#
#                             if ic_data['metadata-core']['A' + row].value is not None:
#                                 ic_new['metadata-core']['A'+new_row].value = ic_data['metadata-core']['A'+row].value
#                                 try:
#                                     entry_date = ic_data['metadata-core']['B'+row].value
#                                 except AttributeError:
#                                     entry_date = dt.datetime.strptime(ic_data['metadata-core']['B'+row].value, '%d-%b-%Y %H:%M:%S')
#                                 else:
#                                     pass
#                                 ic_new['metadata-core']['B' + new_row].value = entry_date
#                                 ic_new['metadata-core']['B' + new_row].value = ic_data['metadata-core']['B' + row].value
#                                 temp_val = ic_data['metadata-core']['C'+row].value
#                                 if isinstance(temp_val, str):
#                                     ic_new['metadata-core']['E' + new_row].value = temp_val.capitalize()
#                                 else:
#                                     ic_new['metadata-core']['E' + new_row].value = temp_val
#                                 ic_new['metadata-core']['C'+new_row].value = author
#                             else:
#                                 # Add latest modification
#                                 ic_new['metadata-core'].insert_rows(int(new_row))
#                                 ic_new['metadata-core']['A' + new_row].value = drow + 1
#                                 ic_new['metadata-core']['B' + new_row].value = dt.datetime.now().date()
#                                 ic_new['metadata-core']['C' + new_row].value = author
#                                 ic_new['metadata-core']['E' + new_row].value = 'Updating to version 1.4.1'
#
#                                 for col in opxl.utils.get_column_interval('I', 'Z'):
#                                     ic_new['metadata-core'][col + new_row].fill = blankFILL
#
#                             ic_new['metadata-core']['B' + new_row].number_format = 'YYYY-MM-DD'
#                             drow += 1
#
#                         # METADATA-STATION
#                         # metatdata_coring > metadata-station
#                         # station
#                         ic_station = ic_data['metadata-coring']['C3'].value
#                         if 'PS_122' in ic_station:
#                             ic_station = ic_station.replace('PS_122', 'PS122')
#                             with open(update_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tStation replace PS_122 by PS122\n')
#
#                         if ic_station.endswith('-'.join(ic_name.split('-')[1:3])):
#                             ic_new['metadata-station']['C3'].value = ic_data['metadata-coring']['C3'].value
#                         else:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tStation name does not match core name\n')
#
#                         ic_site = ic_data['metadata-coring']['C4'].value
#                         for site in site_names:
#                             if site in ic_site:
#                                 for date in sorted(site_names[site].keys()):
#                                     if ic_date < date:
#                                         new_site = site_names[site][date]
#                                         break
#                                 break
#
#                         # site
#                         ic_new['metadata-station']['C4'].value = new_site
#                         with open(update_file, 'a') as f:
#                             f.writelines(ic_name + '\tmetadata-station\tSite "' + ic_site + '" replaced by "' + new_site + '"\n')
#
#                         # Position
#                         # Lat Start
#                         deg = ic_data['metadata-coring']['C8'].value
#                         if deg is not None:
#                             deg = float(deg)
#                             min = ic_data['metadata-coring']['D8'].value
#                             if min is not None:
#                                 min = float(min)
#                             sec = ic_data['metadata-coring']['E8'].value
#                             if sec is not None:
#                                 sec = float(sec)
#                                 if 0 <= sec < 60:
#                                     min = min + sec/60
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tPosition Lat Start: SEC < 0 or SEC > 60\n')
#                             if min is not None:
#                                 if 0 <= min < 60:
#                                     if deg >= 0:
#                                         deg = deg + min / 60
#                                     if deg < 0:
#                                         deg = -(-deg + min)
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tPosition Lat Start: MIN < 0 or MIN > 60\n')
#                             if not (-90 <= deg <= 90):
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tPosition Lat Start: |DEG| > 90\n')
#                             ic_new['metadata-station']['C9'].value = deg
#                             ic_new['metadata-station']['D9'].value = 0
#                             ic_new['metadata-station']['E9'].value = 0
#                             if positionFORMAT == 'DegMin':
#                                 ic_new['metadata-station']['C9'].value = np.sign(deg)*np.floor(np.abs(deg))
#                                 min = np.abs((deg - np.sign(deg)*np.floor(np.abs(deg))) * 60)
#                                 ic_new['metadata-station']['D9'].value = min
#                                 if positionFORMAT == 'DegMinSec':
#                                     ic_new['metadata-coring']['D9'].value = np.floor(min)
#                                     sec = (min - np.floor(min)) * 60
#                                     ic_new['metadata-coring']['E9'].value = sec
#                         else:
#                             ic_new['metadata-station']['C9'].value = deg
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tPosition Lat Start is undetermined\n')
#
#                         # Lat End
#                         deg = ic_data['metadata-coring']['F8'].value
#                         if deg is not None:
#                             deg = float(deg)
#                             min = ic_data['metadata-coring']['G8'].value
#                             if min is not None:
#                                 min = float(min)
#                             sec = ic_data['metadata-coring']['H8'].value
#                             if sec is not None:
#                                 sec = float(sec)
#                             if sec is not None:
#                                 if 0 <= sec < 60:
#                                     min = min + sec / 60
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tPosition Lat End: SEC < 0 or SEC > 60\n')
#                             if min is not None:
#                                 if 0 <= min < 60:
#                                     if deg >= 0:
#                                         deg = deg + min / 60
#                                     if deg < 0:
#                                         deg = -(-deg + min)
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tPosition Lat End: MIN < 0 or MIN > 60\n')
#                             if not(-90 <= deg <= 90):
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tPosition Lat End: |DEG| > 90\n')
#
#                             ic_new['metadata-station']['F9'].value = deg
#                             ic_new['metadata-station']['G9'].value = 0
#                             ic_new['metadata-station']['H9'].value = 0
#                             if positionFORMAT == 'DegMin':
#                                 ic_new['metadata-station']['F9'].value = np.sign(deg)*np.floor(np.abs(deg))
#                                 min = np.abs((deg - np.sign(deg)*np.floor(np.abs(deg))) * 60)
#                                 ic_new['metadata-station']['G9'].value = min
#                                 if positionFORMAT == 'DegMinSec':
#                                     ic_new['metadata-coring']['G9'].value = np.floor(min)
#                                     sec = (min - np.floor(min)) * 60
#                                     ic_new['metadata-coring']['H9'].value = sec
#                         else:
#                             ic_new['metadata-station']['F9'].value = deg
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tPosition is undetermined\n')
#
#                         # Lon Start
#                         deg = ic_data['metadata-coring']['C9'].value
#                         if deg is not None:
#                             deg = float(deg)
#                             min = ic_data['metadata-coring']['D9'].value
#                             if min is not None:
#                                 min = float(min)
#                             sec = ic_data['metadata-coring']['E9'].value
#                             if sec is not None:
#                                 sec = float(sec)
#                             if sec is not None:
#                                 if 0 <= sec < 60:
#                                     min = min + sec / 60
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tPosition Lon Start: SEC < 0 or SEC > 60\n')
#                             if min is not None:
#                                 if 0 <= min < 60:
#                                     if deg >= 0:
#                                         deg = deg + min / 60
#                                     if deg < 0:
#                                         deg = -(-deg + min)
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tPosition Lon Start: MIN < 0 or MIN > 60\n')
#                             if not (-180 <= deg <= 180):
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tPosition Lon Start: Longitude |DEG| > 180\n')
#                             ic_new['metadata-station']['C10'].value = deg
#                             ic_new['metadata-station']['D10'].value = 0
#                             ic_new['metadata-station']['E10'].value = 0
#                             if positionFORMAT == 'DegMin':
#                                 ic_new['metadata-station']['C10'].value = np.sign(deg)*np.floor(np.abs(deg))
#                                 min = np.abs((deg - np.sign(deg)*np.floor(np.abs(deg))) * 60)
#                                 ic_new['metadata-station']['D10'].value = min
#                                 if positionFORMAT == 'DegMinSec':
#                                     ic_new['metadata-coring']['D10'].value = np.floor(min)
#                                     sec = (min - np.floor(min)) * 60
#                                     ic_new['metadata-coring']['E10'].value = sec
#                         else:
#                             ic_new['metadata-station']['C10'].value = deg
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tPosition Lon Start is undetermined\n')
#
#                         # Lon End
#                         deg = ic_data['metadata-coring']['F9'].value
#                         if deg is not None:
#                             deg = float(deg)
#                             min = ic_data['metadata-coring']['G9'].value
#                             if min is not None:
#                                 min = float(min)
#                             sec = ic_data['metadata-coring']['H9'].value
#                             if sec is not None:
#                                 sec = float(sec)
#                             if sec is not None:
#                                 if 0 <= sec < 60:
#                                     min = min + sec / 60
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tPosition Lon End: SEC < 0 or SEC > 60\n')
#                             if min is not None:
#                                 if 0 <= min < 60:
#                                     if deg >= 0:
#                                         deg = deg + min / 60
#                                     if deg < 0:
#                                         deg = -(-deg + min)
#                                 else:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tPosition Lon End: MIN < 0 or MIN > 60\n')
#                             if not (-180 <= deg <= 180):
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tPosition Lon End: Longitude |DEG| > 180\n')
#
#                             ic_new['metadata-station']['F10'].value = deg
#                             ic_new['metadata-station']['G10'].value = 0
#                             ic_new['metadata-station']['H10'].value = 0
#                             if positionFORMAT == 'DegMin':
#                                 ic_new['metadata-station']['F10'].value = np.sign(deg)*np.floor(np.abs(deg))
#                                 min = np.abs((deg - np.sign(deg)*np.floor(np.abs(deg))) * 60)
#                                 ic_new['metadata-station']['G10'].value = min
#                                 if positionFORMAT == 'DegMinSec':
#                                     ic_new['metadata-coring']['G10'].value = np.floor(min)
#                                     sec = (min - np.floor(min)) * 60
#                                     ic_new['metadata-coring']['H9'].value = sec
#                         else:
#                             ic_new['metadata-station']['F10'].value = deg
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tPosition is undetermined\n')
#
#                         # Datetime
#                         # Start
#                         try:
#                             entry_date = ic_data['metadata-coring']['C12'].value.date()
#                         except AttributeError:
#                             entry_date = dt.datetime.strptime(ic_data['metadata-coring']['C12'].value, '%Y-%m-%d').date()
#                         ic_new['metadata-station']['C14'].value = entry_date
#                         if ic_date != ic_new['metadata-station']['C14'].value:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tStart date inconsistent with core date\n')
#                         ic_new['metadata-station']['C14'].number_format = 'YYYY-MM-DD'
#                         if ic_data['metadata-coring']['C13'].value is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tTime undefined\n')
#                             ic_new['metadata-station']['C15'].value = None
#                         elif isinstance(ic_data['metadata-coring']['C13'].value, dt.time):
#                             entry_time = ic_data['metadata-coring']['C13'].value
#                             ic_new['metadata-station']['C15'].value = opxl.utils.datetime.time_to_days(entry_time)
#                             ic_new['metadata-station']['C15'].number_format = 'HH:MM'
#                         else:
#                             try:
#                                 entry_time = ic_data['metadata-coring']['C13'].value.time()
#                             except AttributeError:
#                                 entry_time = dt.datetime.strptime(ic_data['metadata-coring']['C13'].value, '%H:%M:%S').time()
#                             else:
#                                 pass
#                             ic_new['metadata-station']['C15'].value = opxl.utils.datetime.time_to_days(entry_time)
#                             ic_new['metadata-station']['C15'].number_format = 'HH:MM'
#                         if ic_data['metadata-coring']['C14'].value == 'UTC':
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tCheck date TimeZone\n')
#                         ic_new['metadata-station']['C16'].value = ic_data['metadata-coring']['C14'].value
#
#                         # End
#                         if ic_data['metadata-coring']['D12'].value is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tDate End undefined\n')
#                             ic_new['metadata-station']['D14'].value = None
#                         else:
#                             try:
#                                 entry_date = ic_data['metadata-coring']['D12'].value.date()
#                             except AttributeError:
#                                 entry_date = dt.datetime.strptime(ic_data['metadata-coring']['D12'].value, '%Y-%m-%d').date()
#                             else:
#                                 pass
#                             ic_new['metadata-station']['D14'].value = entry_date
#                             if ic_date != ic_new['metadata-station']['D14'].value:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tEnd date inconsistent with core date\n')
#                             ic_new['metadata-station']['D14'].number_format = 'YYYY-MM-DD'
#
#                         if ic_data['metadata-coring']['D13'].value is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tTime undefined\n')
#                             ic_new['metadata-station']['D15'].value = None
#                         elif isinstance(ic_data['metadata-coring']['D13'].value, dt.time):
#                             entry_time = ic_data['metadata-coring']['C13'].value
#                             ic_new['metadata-station']['D15'].value = opxl.utils.datetime.time_to_days(entry_time)
#                             ic_new['metadata-station']['D15'].number_format = 'HH:MM'
#                         else:
#                             try:
#                                 entry_time = ic_data['metadata-coring']['D13'].value.time()
#                             except AttributeError:
#                                 entry_time = dt.datetime.strptime(ic_data['metadata-coring']['D13'].value, '%H:%M:%S').time()
#                             else:
#                                 pass
#                             ic_new['metadata-station']['D15'].value = opxl.utils.datetime.time_to_days(entry_time)
#                             ic_new['metadata-station']['D15'].number_format = 'HH:MM'
#
#                         if ic_data['metadata-coring']['D14'].value == 'UTC':
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tCheck date TimeZone\n')
#                         ic_new['metadata-station']['D16'].value = ic_data['metadata-coring']['D14'].value
#
#                         # Ice geometry
#                         # Snow depth
#                         ii_col = 3
#                         hs_list = []
#                         while ic_data['metadata-coring'][opxl.utils.get_column_letter(ii_col)+'16'].value is not None:
#                             hs = ic_data['metadata-coring'][opxl.utils.get_column_letter(ii_col)+'16'].value
#                             if hs is not None:
#                                 hs = float(hs)
#                             if hs > m_unit:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tCheck unit for snow depth\n')
#                                 with open(update_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tCore length likely in cm, change to m\n')
#                                 hs = hs / 100
#                             hs_list.append(hs)
#                             ii_col += 1
#
#                         if len(hs_list) < 1:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tNo snow depth measurement\n')
#                         else:
#                             # Snow reference:
#                             ic_new['metadata-core']['C15'].value = 'ice surface'
#                             ic_new['metadata-core']['D16'].value = 'up'
#
#                             if isclose(hs_list[0], np.mean(hs_list[1:])):
#                                 if len(hs_list) > 5:
#                                     ic_new['metadata-station']['C19'].value = np.mean(hs_list[1:])
#                                     for ii_col in range(1, len(hs_list)):
#                                         ic_new['metadata-station'][opxl.utils.get_column_letter(3+ii_col)+'19'].value = hs_list[ii_col]
#                                         if ii_col >= 5:
#                                             ic_new['metadata-station'][opxl.utils.get_column_letter(3 + ii_col) + '19'].fill = prcdtFILL
#                                     if len(hs_list) >= 6:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tmetadata-station\tCheck for supernumerary snow depth measurement\n')
#                                 else:
#                                     ic_new['metadata-station']['C19'].value = np.mean(hs_list)
#                                     for ii_col in range(0, len(hs_list)):
#                                         ic_new['metadata-station'][opxl.utils.get_column_letter(3+ii_col)+'19'].value = hs_list[ii_col]
#                                     if len(hs_list) < 6:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tmetadata-station\tCheck for missing snow depth measurement\n')
#                             else:
#                                 ic_new['metadata-station']['C19'].value = np.mean(hs_list)
#                                 for ii_col in range(0, len(hs_list)):
#                                     ic_new['metadata-station'][opxl.utils.get_column_letter(4 + ii_col) + '19'].value = hs_list[ii_col]
#                                     if ii_col >= 5:
#                                         ic_new['metadata-station'][opxl.utils.get_column_letter(4 + ii_col) + '19'].fill = prcdtFILL
#                                 if len(hs_list) >= 5:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tCheck for supernumerary snow depth measurement\n')
#                                 elif len(hs_list) < 5:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tmetadata-station\tCheck for missing snow depth measurement\n')
#
#                         # Average freeboard
#                         ic_new['metadata-station']['C20'].value = ic_data['metadata-coring']['C17'].value
#                         if ic_new['metadata-station']['C20'].value is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tNeed to compute average freeboard\n')
#
#                         # Average ice thickness
#                         ic_new['metadata-station']['C21'].value = ic_data['metadata-coring']['C18'].value
#                         if ic_new['metadata-station']['C21'].value is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tNeed to compute average ice thickness\n')
#
#                         # Water depth
#                         ic_new['metadata-station']['C22'].value = ic_data['metadata-coring']['C19'].value
#                         if ic_new['metadata-station']['C22'].value is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tNeed to add water depth\n')
#
#                         # Age
#                         age_list = [ic_new['lists']['C'+str('%.0f' % row)].value for row in range(2, 7)]
#                         ic_age = ic_data['metadata-coring']['C20'].value
#                         if ic_age not in age_list:
#                             ic_age = None
#                             for age in age_list:
#                                 if age.startswith(ic_site[:2]):
#                                     ic_age = age
#                                     break
#                             if ic_age is None:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tNeed ice age information\n')
#                         ic_new['metadata-station']['C23'].value = ic_age
#
#                         # topography
#                         topography_list = [ic_new['lists']['D'+str('%.0f' % row)].value for row in range(2, 27) if ic_new['lists']['D'+str('%.0f' % row)].value is not None]
#                         ic_topo_val = ic_data['metadata-coring']['C21'].value
#                         if ic_topo_val not in topography_list:
#                             ic_topo = None
#                             for topo in topography_list:
#                                 if topo.startswith(ic_topo_val.lower()):
#                                     ic_topo = topo
#                                     break
#                             if ic_topo is None:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tNeed ice topography information\n')
#                         else:
#                             ic_topo = ic_topo_val
#                         ic_new['metadata-station']['C24'].value = ic_topo
#
#                         # Environment:
#                         environment_list = [ic_new['lists']['E'+str('%.0f' % row)].value for row in range(2, 27) if ic_new['lists']['E'+str('%.0f' % row)].value is not None]
#                         ic_env_data = ic_data['metadata-coring']['C22'].value
#                         if ic_env_data not in environment_list:
#                             ic_env = None
#                             for env in environment_list:
#                                 if env.startswith(ic_env_data.lower()):
#                                     ic_env = env
#                                     break
#                             if ic_env is None:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tNeed ice environment information\n')
#                         else:
#                             ic_env = ic_env_data
#                         ic_new['metadata-station']['C25'].value = ic_env
#
#                         # Surface condition
#                         surface_list = [ic_new['lists']['B'+str('%.0f' % row)].value for row in range(2, 27) if ic_new['lists']['B'+str('%.0f' % row)].value is not None]
#                         ic_surface_data = ic_data['metadata-coring']['C23'].value
#                         if ic_surface_data not in surface_list:
#                             ic_surface = None
#                             for surface in surface_list:
#                                 if surface.startswith(ic_surface_data.lower()):
#                                     ic_surface = surface
#                                     break
#                             if ic_surface is None:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tNeed ice environment information\n')
#                         else:
#                             ic_surface = ic_surface_data
#                         ic_new['metadata-station']['C26'].value = ic_surface
#
#                         # Ice temperature
#                         # Air temperature
#                         T = ic_data['metadata-coring']['C25'].value
#                         if T == '':
#                             T = None
#                         if T is None or T == 'N/A':
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tMissing air temperature information\n')
#                         else:
#                             T = float(T)
#                         ic_new['metadata-station']['C29'].value = T
#
#                         # Snow surface
#                         T = ic_data['metadata-coring']['C26'].value
#                         if T == '':
#                             T = None
#                         if T is None or T == 'N/A':
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tMissing snow surface temperature information\n')
#                         else:
#                             T = float(T)
#                         ic_new['metadata-station']['C30'].value = T
#
#                         # Ice surface
#                         T = ic_data['metadata-coring']['C27'].value
#                         if T == '':
#                             T = None
#                         if T is None or T == 'N/A':
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tMissing ice surface temperature information\n')
#                         else:
#                             T = float(T)
#                         ic_new['metadata-station']['C31'].value = T
#
#                         # Water temperature
#                         T = ic_data['metadata-coring']['C28'].value
#                         if T == '':
#                             T = None
#                         if T is None or T == 'N/A':
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tMissing water temperature information\n')
#                         else:
#                             T = float(T)
#                         ic_new['metadata-station']['C32'].value = T
#                         del T
#
#                         # Sampling event:
#                         # Sampling station
#                         ic_new['metadata-station']['C35'].value = ic_data['metadata-coring']['C30'].value
#                         ic_new['metadata-station']['D35'].value = None
#
#                         # Associated cores
#                         ii_col = 3
#                         while ic_data['metadata-coring'][opxl.utils.get_column_letter(ii_col)+'31'].value is not None:
#                             aic_name = ic_data['metadata-coring'][opxl.utils.get_column_letter(ii_col)+'31'].value
#                             ic_new['metadata-station'][opxl.utils.get_column_letter(ii_col) + '36'].value = aic_name
#                             if ii_col >=9:
#                                 ic_new['metadata-station'][opxl.utils.get_column_letter(ii_col) + '36'].fill = prcdtFILL
#                             ii_col += 1
#
#                         # Observers
#                         ii_col = 3
#                         obs_list = []
#                         ic_obs = []
#                         while ic_data['metadata-coring'][opxl.utils.get_column_letter(ii_col)+'32'].value is not None:
#                             obs_list.append(ic_data['metadata-coring'][opxl.utils.get_column_letter(ii_col)+'32'].value)
#                             ii_col += 1
#                         for obs_flt in obs_list:
#                             obs_fl = obs_flt.split('(')[0].strip()
#                             if obs_fl not in obs_names[ic_leg]:
#                                 for obs in obs_fl.split(' '):
#                                     obs_flag = 0
#                                     for name in obs_names[ic_leg]:
#                                         # Correct for Suzanne to Susanne for Susanne Spahic
#                                         if ic_leg == 3 and obs == 'Suzanne':
#                                             obs = 'Susanne'
#                                         if obs in name and obs not in ic_obs:
#                                             ic_obs.append(name)
#                                             obs_flag = 1
#                                             with open(update_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tmetadata-station\tObserver name ' + obs_fl + ' changed to ' + name +'\n')
#                                         else:
#                                             obs_flag =1
#                                     if obs_flag == 0:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tmetadata-station\tObserver ' + obs_fl +' not in observer list\n')
#                             else:
#                                 if obs_fl not in ic_obs:
#                                     ic_obs.append(obs_flt)
#
#                         for ii_col in range(0, len(ic_obs)):
#                             ic_new['metadata-station'][opxl.utils.get_column_letter(3+ii_col)+'37'].value = ic_obs[ii_col]
#
#                         # Weather information
#                         ws = ic_data['metadata-coring']['C36'].value
#                         if ws is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tMissing wind speed information\n')
#                         else:
#                             ws = float(ws)
#                         ic_new['metadata-station']['C41'].value = ws
#                         del ws
#
#                         wd = ic_data['metadata-coring']['C37'].value
#                         if wd is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tMissing wind orientation information\n')
#                         else:
#                             wd = float(wd)
#                         ic_new['metadata-station']['C42'].value = wd
#                         del wd
#
#                         ic_cloud_val = ic_data['metadata-coring']['C38'].value
#                         cloud_list = [ic_new['lists']['P'+str('%.0f' % row)].value for row in range(2, 27) if ic_new['lists']['P'+str('%.0f' % row)].value is not None]
#                         if ic_cloud_val is None:
#                             with open(error_file, 'a') as f:
#                                 f.writelines(ic_name + '\tmetadata-station\tMissing cloud cover information\n')
#                             ic_cloud = None
#                         elif ic_cloud_val not in cloud_list:
#                             ic_cloud = None
#                             for cloud in cloud_list:
#                                 if cloud.startswith(ic_cloud_val.lower()):
#                                     ic_cloud = cloud
#                                     break
#                             if ic_cloud is None:
#                                 with open(error_file, 'a') as f:
#                                     f.writelines(ic_name + '\tmetadata-station\tNeed cloud cover information\n')
#                         else:
#                             ic_cloud = ic_cloud_val
#                         ic_new['metadata-station']['C43'].value = ic_cloud
#                         del ic_cloud
#
#                         ic_new['metadata-station']['C44'].value = 'N/M'
#                         ic_new['metadata-station']['C45'].value = 'N/M'
#
#                         # General comment
#                         comment = ic_data['metadata-coring']['A42'].value
#                         if site == 'SYI':
#                             comment = comment.replace('Refrozen melt pond', '')
#                             if comment.startswith('\n'):
#                                 comment = comment[1:].capitalize()
#                         ic_new['metadata-station']['A48'].value = comment
#                         # Modify height of line to fit comment
#                         h_row = ic_new['metadata-station'].row_dimensions[47].height
#                         # count number of line in comment
#                         if comment is not None:
#                             n_line = comment.count('\n') + 1
#                             ic_new['metadata-station'].row_dimensions[48].height = n_line * h_row
#
#                         vert_ref_list = ['ice surface', 'ice/water interface', 'snow surface', 'water level']
#                         vert_dir_list = ['up', 'down']
#
#                         ## TEMP
#                         if 'TEMP' in ic_data.get_sheet_names():
#                             # Check for value
#                             if ic_ver == '1.2M':
#                                 start_row = 4
#                             else:
#                                 start_row = 5
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['TEMP']['A' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             # If there is depth entry
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['TEMP']['C1'].value
#                                 vert_dir = ic_data['TEMP']['E1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\ttemp\tVertical reference unknown')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\ttemp\tVertical direction unknown')
#
#                                 if ic_new['metadata-core']['D13'].value is None:
#                                     ic_new['metadata-core']['D13'].value = vert_ref
#                                     ic_new['metadata-core']['D14'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D13'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\ttemp\tVertical reference not consistent with metadata-core\n')
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\ttemp\tVertical direction not consistent with metadata-core\n')
#
#                                 # Data (depth, ID,  salinity...)
#                                 unit_flag = 0
#                                 if data_flag == 1:
#                                     for jj_row, row in enumerate(range(start_row, ii_row)):
#                                         if jj_row <= ii_row - 45 - (start_row - 1):
#                                             ic_new['temp'].insert_rows(4 + jj_row)
#                                             for col in opxl.utils.get_column_interval('E', 'Z'):
#                                                 ic_new['temp'][col + str('%.0f' % (4 + jj_row))].fill = blankFILL
#                                             ic_new['temp']['A' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['temp']['C' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         d1 = ic_data['TEMP']['A'+str('%.0f' %(row))].value
#                                         if d1 is None or isinstance(d1, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\ttemp\tDepth 1 are not number\n')
#                                         elif isinstance(d1, (float, int)):
#                                             if d1 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\ttemp\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(ic_name + '\ttemp\tDepth 1 ' + str('%.2f' % d1) + ' likely in cm, change to m\n')
#                                                 d1 = d1/100
#                                         ic_new['temp']['A' + str('%.0f' % (4+jj_row))].value = d1
#
#                                         # Temperature value
#                                         t = ic_data['TEMP']['B'+str('%.0f' %(row))].value
#                                         ic_new['temp']['B'+str('%.0f' % (4+jj_row))].value = t
#                                         # Comment
#                                         ic_new['temp']['D'+str('%.0f' % (4+jj_row))].value = ic_data['TEMP']['C'+str('%.0f' %(row))].value
#
#                                         if d1 is not None and t is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\ttemp\tDepth 1 ' + str('%.0f' % d1) + ' has no temperature\n')
#                         unit_flag = 0
#
#                         ## SALO18
#                         if 'SALO18' in ic_data.get_sheet_names():
#                             # Check for value
#                             start_row = 5
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['SALO18']['A' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             # if no depth entry are present, check existence of mid-center value
#                             if data_flag == 0:
#                                 row_flag = 0
#                                 while row_flag < 2:
#                                     if ic_data['SALO18']['C' + str('%.0f' % ii_row)].value is None:
#                                         row_flag += 1
#                                     else:
#                                         row_flag = 0
#                                         data_flag = 2
#                                     ii_row += 1
#                                 if data_flag == 2:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsalo18\tOnly depth entry for section center\n')
#
#                             # If there is depth entry
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['SALO18']['C1'].value
#                                 vert_dir = ic_data['SALO18']['F1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsalo18\tVertical reference unknown\n')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsalo18\tVertical direction unknown\n')
#
#                                 if ic_new['metadata-core']['D13'].value is None:
#                                     ic_new['metadata-core']['D13'].value = vert_ref
#                                     ic_new['metadata-core']['D14'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D13'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsalo18\tVertical reference not consistent with metadata-core\n')
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsalo18\tVertical direction not consistent with metadata-core\n')
#
#                                 # Data (depth, ID,  salinity...)
#                                 unit_flag = 0
#                                 if data_flag == 1:
#                                     for jj_row, row in enumerate(range(start_row, ii_row)):
#                                         if jj_row <= ii_row - 46 - (start_row - 1):
#                                             ic_new['salo18'].insert_rows(4 + jj_row)
#                                             for col in opxl.utils.get_column_interval('P', 'Z'):
#                                                 ic_new['salo18'][col + str('%.0f' % (4 + jj_row))].fill = blankFILL
#                                             ic_new['salo18']['B' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['salo18']['H' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['salo18']['K' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['salo18']['N' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#
#                                         d1 = ic_data['SALO18']['A'+str('%.0f' %(row))].value
#                                         if d1 is None or isinstance(d1, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsalo18\tDepth 1 are not number\n')
#                                         elif isinstance(d1, (float, int)):
#                                             if d1 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tsalo18\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tsalo18\tDepth 1 ' + str('%.2f' % d1) + ' likely in cm, change to m\n')
#                                                 d1 = d1/100
#                                         ic_new['salo18']['A'+str('%.0f' %(4+jj_row))].value = d1
#
#                                         d2 = ic_data['SALO18']['B'+str('%.0f' %(row))].value
#                                         if d2 is None  or isinstance(d2, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsalo18\tDepth 2 are not number\n')
#                                         elif isinstance(d2, (float, int)):
#                                             if d2 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tsalo18\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tsalo18\tDepth 2 ' + str('%.2f' % d2) + ' likely in cm, change to m\n')
#                                                 d2 = d2/100
#                                         ic_new['salo18']['B'+str('%.0f' % (4+jj_row))].value = d2
#
#                                         # ID
#                                         id = ic_data['SALO18']['D'+str('%.0f' %(row))].value
#                                         if d1 is not None and id is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsalo18\tDepth 1 ' + str('%.0f' % d1) + ' has no id\n')
#                                         ic_new['salo18']['C'+str('%.0f' %(4+jj_row))].value = id
#
#                                         # Salinity value
#                                         s = ic_data['SALO18']['E'+str('%.0f' %(row))].value
#                                         ic_new['salo18']['D'+str('%.0f' %(4+jj_row))].value = s
#                                         if d1 is not None and s is None:
#                                             with open(error_file, 'a') as f:
#                                                 try:
#                                                     f.writelines(ic_name + '\tsalo18\tDepth 1 ' + str('%.0f' % d1) + ' has no salinity value\n')
#                                                 except TypeError:
#                                                     f.writelines(ic_name + '\tsalo18\tDepth 1 ' + d1 + ' has no salinity value\n')
#                                                 else:
#                                                     pass
#
#                                         ic_new['salo18']['F'+str('%.0f' %(4+jj_row))].value = ic_data['SALO18']['F'+str('%.0f' %(row))].value
#                                         ic_new['salo18']['G' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['G' + str('%.0f' % (row))].value
#                                         ic_new['salo18']['H' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['H' + str('%.0f' % (row))].value
#                                         ic_new['salo18']['I' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['I' + str('%.0f' % (row))].value
#                                         ic_new['salo18']['L' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['K' + str('%.0f' % (row))].value
#                                         ic_new['salo18']['O' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['N' + str('%.0f' % (row))].value
#                                 elif data_flag == 2:
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(update_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsalo18\tGenerate depth 1 and depth2 value based on mid center depth\n')
#                                     for jj_row, row in enumerate(range(start_row, ii_row)):
#                                         if jj_row <= ii_row - 46 - (start_row - 1):
#                                             ic_new['salo18'].insert_rows(4 + jj_row)
#                                             for col in opxl.utils.get_column_interval('P', 'Z'):
#                                                 ic_new['salo18'][col + str('%.0f' % (4 + jj_row))].fill = blankFILL
#                                             ic_new['salo18']['B' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['salo18']['H' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['salo18']['K' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['salo18']['N' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         d_mid = ic_data['SALO18']['C'+str('%.0f' %(row))].value
#                                         if d_mid is None or isinstance(d_mid, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsalo18\tDepth mid are not number\n')
#                                         elif isinstance(d_mid(float, int)):
#                                             if row < ii_row - 1:
#                                                 d_mid_sup = ic_data['SALO18']['C' + str('%.0f' % (row + 1))].value
#                                             else:
#                                                 d_mid_sup = ic_data['SALO18']['C' + str('%.0f' % (row - 1))].value
#                                             h_mid = np.abs(d_mid_sup - d_mid)
#
#                                             if d_mid > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tsalo18\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(
#                                                         ic_name + '\tsalo18\tMid depth ' + str('%.2f' % d_mid) + ' likely in cm, change to m\n')
#                                                 d_mid = d_mid / 100
#                                                 h_mid = h_mid / 100
#                                             ic_new['salo18']['A' + str('%.0f' % (4 + jj_row))].value = d_mid - h_mid
#                                             ic_new['salo18']['B' + str('%.0f' % (4 + jj_row))].value = d_mid + h_mid
#
#                                         # ID
#                                         id = ic_data['SALO18']['D'+str('%.0f' %(row))].value
#                                         if d_mid is not None and id is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsalo18\tDepth 1 ' + str('%.0f' % d1) + ' has no id\n')
#                                         ic_new['salo18']['C'+str('%.0f' %(4+jj_row))].value = id
#                                         # Salinity value
#                                         s = ic_data['SALO18']['E'+str('%.0f' %(row))].value
#                                         ic_new['salo18']['D'+str('%.0f' %(4+jj_row))].value = s
#                                         if d_mid is not None and s is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\ttemp\tDepth 1 ' + str('%.0f' % d1) + ' has no salinity value\n')
#                                         ic_new['salo18']['F'+str('%.0f' %(4+jj_row))].value = ic_data['SALO18']['F'+str('%.0f' %(row))].value
#                                         ic_new['salo18']['G' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['G' + str('%.0f' % (row))].value
#                                         ic_new['salo18']['H' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['H' + str('%.0f' % (row))].value
#                                         ic_new['salo18']['I' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['I' + str('%.0f' % (row))].value
#                                         ic_new['salo18']['L' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['K' + str('%.0f' % (row))].value
#                                         ic_new['salo18']['O' + str('%.0f' % (4 + jj_row))].value = ic_data['SALO18']['N' + str('%.0f' % (row))].value
#                         unit_flag = 0
#
#                         # Texture
#                         if 'TEX' in ic_data.get_sheet_names():
#                             # Check for value
#                             if ic_ver == '1.2M':
#                                 start_row = 5  # 4
#                             else:
#                                 start_row = 5
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 cond0 = ic_data['TEX']['A' + str('%.0f' % ii_row)].value is not None
#                                 cond1 = ic_data['TEX']['B' + str('%.0f' % ii_row)].value is not None
#                                 cond2 = ic_data['TEX']['C' + str('%.0f' % ii_row)].value is not None
#
#                                 if not any([cond0, cond1, cond2]):
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             # If there is data:
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['TEX']['C1'].value
#                                 vert_dir = ic_data['TEX']['E1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tTEX\tVertical reference unknown\n')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tTEX\tVertical direction unknown\n')
#
#                                 if ic_new['metadata-core']['D13'].value is None:
#                                     ic_new['metadata-core']['D13'].value = vert_ref
#                                     ic_new['metadata-core']['D14'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D13'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tTEX\tVertical reference not consistent with metadata-core\n')
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tTEX\tVertical direction not consistent with metadata-core\n')
#
#                                 #TODO: Add cm and m check
#                                 for ii_row, row in enumerate(range(start_row, start_row+ii_row)):
#                                     if jj_row <= ii_row - 46 - (start_row - 1):
#                                         ic_new['tex'].insert_rows(4 + jj_row)
#                                         for col in opxl.utils.get_column_interval('L', 'Z'):
#                                             ic_new['tex'][col + str('%.0f' % (4 + jj_row))].fill = blankFILL
#                                         ic_new['tex']['B' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                             right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         ic_new['tex']['F' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                             right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         ic_new['tex']['J' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                             right=opxl.styles.Side(border_style='thin', color='000000'))
#                                     d1 = ic_data['TEX']['A' + str('%.0f' % (row))].value
#                                     d2 = ic_data['TEX']['B' + str('%.0f' % (row))].value
#
#                                     if d1 is not None and d2 is not None:
#                                         if isinstance(d1, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\ttex\tDepth 1 is not a number\n')
#                                         elif isinstance(d1, (float, int)):
#                                             if d1 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\ttex\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(ic_name + '\ttex\tDepth 1' + str(
#                                                         '%.2f' % d1) + ' likely in cm, change to m\n')
#                                                 d1 = d1 / 100
#                                         ic_new['tex']['A' + str('%.0f' % (4 + ii_row))].value = d1
#
#                                         if isinstance(d2, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\ttex\tDepth 2 is not a number\n')
#                                         elif isinstance(d2, (float, int)):
#                                             if d2 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\ttex\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(ic_name + '\ttex\tDepth 2' + str(
#                                                         '%.2f' % d2) + ' likely in cm, change to m\n')
#                                                 d2 = d2 / 100
#                                         ic_new['tex']['B' + str('%.0f' % (4 + ii_row))].value = d2
#
#                                     d_mid = ic_data['TEX']['C' + str('%.0f' % (row))].value
#                                     if d_mid is not None:
#                                         if isinstance(d_mid, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\ttex\tDepth mid is not a number\n')
#                                         elif isinstance(d_mid, (float, int)):
#                                             if d_mid > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\ttex\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(ic_name + '\ttex\tDepth mid' + str(
#                                                         '%.2f' % d_mid) + ' likely in cm, change to m\n')
#
#                                         if d1 is None:
#                                             ic_new['tex']['A' + str('%.0f' % (4 + ii_row))].value = d_mid
#                                         else:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\ttex\tdepth 1 already exist for mid depth' + str('%.2f' % d_mid))
#                                         if d2 is None:
#                                             ic_new['tex']['B' + str('%.0f' % (4 + ii_row))].value = d_mid
#                                         else:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\ttex\tdepth 1 already exist for mid depth' + str('%.2f' % d_mid))
#
#                                     # Check description
#                                     layer = ic_data['TEX']['D' + str('%.0f' % row)].value
#                                     if layer is not None:
#                                         layer = layer.lower()
#                                         if 'break' in layer:
#                                             ic_new['tex']['F' + str('%.0f' % (4 +ii_row))].value = 'break'
#                                             layer = layer.replace('break', '')
#                                         if 'granular' in layer.lower():
#                                             ic_new['tex']['C' + str('%.0f' % (4 +ii_row))].value = 'granular'
#                                             ic_new['tex']['H' + str('%.0f' % (4 +ii_row))].value = 'sea ice'
#                                             layer = layer.replace('granular', '')
#                                         if 'columnar' in layer.lower():
#                                             ic_new['tex']['C' + str('%.0f' % (4 +ii_row))].value = 'columnar'
#                                             ic_new['tex']['H' + str('%.0f' % (4 +ii_row))].value = 'sea ice'
#                                             layer = layer.replace('columnar', '')
#                                         if 'snow' in layer.lower():
#                                             ic_new['tex']['H' + str('%.0f' % (4 +ii_row))].value = 'snow'
#                                             layer = layer.replace('snow', '')
#                                         if 'skeletal' in layer.lower() or 'skeletal layer' in layer.lower():
#                                             ic_new['tex']['C' + str('%.0f' % (4 +ii_row))].value = 'lamellar'
#                                             ic_new['tex']['H' + str('%.0f' % (4 +ii_row))].value = 'skeletal'
#                                             layer = layer.replace('skeletal', '')
#                                         if 'milky' in layer.lower():
#                                             ic_new['tex']['F' + str('%.0f' % (4 +ii_row))].value = 'milky'
#                                             layer = layer.replace('milky', '')
#                                         if 'clear' in layer.lower():
#                                             ic_new['tex']['F' + str('%.0f' % (4 +ii_row))].value = 'clear'
#                                             ic_new['tex']['E' + str('%.0f' % (4 +ii_row))].value = 'none'
#                                             layer = layer.replace('clear', '')
#                                         if 'opaque' in layer.lower():
#                                             ic_new['tex']['F' + str('%.0f' % (4 +ii_row))].value = 'opaque'
#                                             layer = layer.replace('opaque', '')
#                                         if 'bubble-free' in layer.lower():
#                                             ic_new['tex']['E' + str('%.0f' % (4 +ii_row))].value = 'bubble-free'
#                                             layer = layer.replace('bubble-free', '')
#                                         if 'sediment' in layer.lower():
#                                             ic_new['tex']['E' + str('%.0f' % (4 +ii_row))].value = 'sediment'
#                                             layer = layer.replace('sediment', '')
#                                         if 'bubble' in layer.lower():
#                                             ic_new['tex']['E' + str('%.0f' % (4 +ii_row))].value = 'bubbles'
#                                             layer = layer.replace('bubble', '')
#                                         if 'brine cluster' in layer.lower():
#                                             ic_new['tex']['E' + str('%.0f' % (4 +ii_row))].value = 'brine cluster'
#                                             layer = layer.replace('brine cluster', '')
#                                         if 'MY/FY' in layer.lower():
#                                             ic_new['tex']['F' + str('%.0f' % (4 +ii_row))].value = 'transition FY/MY'
#                                             layer = layer.replace('MY/FY', '')
#
#                                         layer_list = layer.split(',')
#                                         layer_list = [l.strip() for l in filter(None, layer_list)]
#                                         layer_list = list(filter(None, layer_list))
#
#                                         if len(layer_list) > 0:
#                                             if d1 is not None:
#                                                 d_layer = d1
#                                             elif d_mid is not None:
#                                                 d_layer = d_mid
#                                             else:
#                                                 d_layer = np.nan
#                                             if isinstance(d_layer, (float, int)):
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\ttex\tdepth ' + str('%.2f' %d_layer) + 'has still unclassifed descriptors\n')
#                                             else:
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\ttex\tdepth ' + d_layer + 'has still unclassifed descriptors\n')
#
#                                     comment = ic_data['TEX']['F' + str('%.0f' % row)].value
#                                     if site == 'SYI' and comment is not None and 'refrozen melt pond' in comment:
#                                         comment = comment.replace('refrozen melt pond', '')
#                                         comment = comment.split(', ')
#                                         comment = ', '.join(filter(None, comment))
#                                     if comment is not None:
#                                         ic_new['tex']['K' + str('%.0f' % (4 + ii_row))].value = comment
#                         unit_flag = 0
#
#                         # ECO
#                         if 'ECO' in ic_data.get_sheet_names():
#                             # Check for value
#                             start_row = 5
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['ECO']['A' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             # If there is depth entry
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['ECO']['C1'].value
#                                 vert_dir = ic_data['ECO']['E1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\teco\tVertical reference unknown\n')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\teco\tVertical direction unknown\n')
#
#                                 if ic_new['metadata-core']['D13'].value is None:
#                                     ic_new['metadata-core']['D13'].value = vert_ref
#                                     ic_new['metadata-core']['D14'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D13'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\teco\tVertical reference not consistent with metadata-core\n')
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\teco\tVertical direction not consistent with metadata-core\n')
#
#                                 # Data (depth, ID,  salinity...)
#                                 unit_flag = 0
#                                 for jj_row, row in enumerate(range(start_row, ii_row)):
#                                     if jj_row <= ii_row - 46 - (start_row - 1):
#                                         ic_new['eco'].insert_rows(4 + jj_row)
#                                         for col in opxl.utils.get_column_interval('P', 'Z'):
#                                             ic_new['eco'][col + str('%.0f' % (4 + jj_row))].fill = blankFILL
#                                         ic_new['eco']['D' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                             right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         ic_new['eco']['H' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                             right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         ic_new['eco']['L' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                             right=opxl.styles.Side(border_style='thin', color='000000'))
#                                     d1 = ic_data['ECO']['A'+str('%.0f' %(row))].value
#                                     if d1 is None or isinstance(d1, str):
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\teco\tDepth 1 are not number\n')
#                                     elif isinstance(d1, (float, int)):
#                                         if d1 > m_unit:
#                                             if unit_flag == 0:
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\teco\tCheck unit for depth\n')
#                                                 unit_flag = 1
#                                             with open(update_file, 'a') as f:
#                                                 f.writelines(ic_name + '\teco\tDepth 1 ' + str('%.2f' % d1) + ' likely in cm, change to m\n')
#                                             d1 = d1/100
#                                     ic_new['eco']['A'+str('%.0f' %(4+jj_row))].value = d1
#
#                                     d2 = ic_data['ECO']['B'+str('%.0f' %(row))].value
#                                     if d2 is None or isinstance(d2, str):
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\teco\tDepth 2 are not number\n')
#                                     elif isinstance(d2, (float, int)):
#                                         if d2 > m_unit:
#                                             if unit_flag == 0:
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\teco\tCheck unit for depth\n')
#                                                 unit_flag = 1
#                                             with open(update_file, 'a') as f:
#                                                 f.writelines(ic_name + '\teco\tDepth 2 ' + str('%.2f' % d2) + ' likely in cm, change to m\n')
#                                             d2 = d2/100
#                                     ic_new['eco']['B'+str('%.0f' % (4+jj_row))].value = d2
#
#                                     # field ID
#                                     id = ic_data['ECO']['C'+str('%.0f' %(row))].value
#                                     if d1 is not None and id is None:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\teco\tDepth 1 ' + str('%.0f' % d1) + ' has no id\n')
#                                     ic_new['eco']['C'+str('%.0f' %(4+jj_row))].value = id
#
#                                     # melted volume (total)
#                                     ic_new['eco']['G'+str('%.0f' %(4+jj_row))].value = ic_data['ECO']['D'+str('%.0f' %(row))].value
#                                     # metled volume: added sea water
#                                     ic_new['eco']['F' + str('%.0f' % (4 + jj_row))].value = ic_data['ECO']['E' + str('%.0f' % (row))].value
#
#                                     # TODO IMPROVE NUTRIENT
#                                     # nutrient ID
#                                     ic_new['eco']['I' + str('%.0f' % (4 + jj_row))].value = ic_data['ECO']['F' + str('%.0f' % (row))].value
#                         unit_flag = 0
#
#                         # CT
#                         if 'CT' in ic_data.get_sheet_names():
#                             # Check for value
#                             if ic_ver == '1.2M':
#                                 start_row = 5
#                             else:
#                                 start_row = 5
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['CT']['A' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             # if no depth entry are present, check existence of mid-center value
#                             if data_flag == 0:
#                                 row_flag = 0
#                                 while row_flag < 2:
#                                     if ic_data['CT']['C' + str('%.0f' % ii_row)].value is None:
#                                         row_flag += 1
#                                     else:
#                                         row_flag = 0
#                                         data_flag = 2
#                                     ii_row += 1
#                                 if data_flag == 2:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tct\tOnly depth entry for section center\n')
#
#                             # If there is depth entry
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['CT']['C1'].value
#                                 vert_dir = ic_data['CT']['E1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tct\tVertical reference unknown\n')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tct\tVertical direction unknown\n')
#
#                                 if ic_new['metadata-core']['D13'].value is None:
#                                     ic_new['metadata-core']['D13'].value = vert_ref
#                                     ic_new['metadata-core']['D14'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D13'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tct\tVertical reference not consistent with metadata-core\n')
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tct\tVertical direction not consistent with metadata-core\n')
#
#                                 # Data copy
#                                 unit_flag = 0
#                                 if data_flag == 1:
#                                     for jj_row, row in enumerate(range(start_row, ii_row)):
#                                         if jj_row <= ii_row - 46 - (start_row - 1):
#                                             ic_new['ct'].insert_rows(4 + jj_row)
#                                             for col in opxl.utils.get_column_interval('V', 'Z'):
#                                                 ic_new['ct'][col + str('%.0f' % (4 + jj_row))].fill = blankFILL
#                                             ic_new['ct']['E' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['ct']['H' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['ct']['N' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['ct']['T' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         d1 = ic_data['CT']['A'+str('%.0f' %(row))].value
#                                         if isinstance(d1, str) or d1 is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tct\tDepth 1 are not number\n')
#                                         elif isinstance(d1, (float, int)):
#                                             if d1 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tct\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tct\tDepth 1 ' + str('%.2f' % d1) + ' likely in cm, change to m\n')
#                                                 d1 = d1/100
#                                         ic_new['ct']['A'+str('%.0f' %(5+jj_row))].value = d1
#
#                                         d2 = ic_data['CT']['B'+str('%.0f' %(row))].value
#                                         if isinstance(d2, str) or d2 is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tct\tDepth 2 are not number\n')
#                                         elif isinstance(d2, (float, int)):
#                                             if d2 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tct\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tct\tDepth 2 ' + str('%.2f' % d2) + ' likely in cm, change to m\n')
#                                                 d2 = d2/100
#                                         ic_new['ct']['A'+str('%.0f' %(5+jj_row))].value = d2
#
#                                         # ID
#                                         id = ic_data['CT'][ 'D' + str('%.0f' % (row))].value
#                                         if d1 is not None and id is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tct\tDepth 1 ' + str('%.0f' % d1) + ' has no id\n')
#                                         ic_new['ct']['C' + str('%.0f' % (5 + jj_row))].value = id
#                                         # tar mass
#                                         ic_new['ct']['D' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'E' + str('%.0f' % (row))].value
#                                         # sample mass with tar
#                                         ic_new['ct']['E' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'F' + str('%.0f' % (row))].value
#                                         # sample mass
#                                         ic_new['ct']['F' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'G' + str('%.0f' % (row))].value
#                                         # ice mass
#                                         ic_new['ct']['G' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'H' + str('%.0f' % (row))].value
#                                         # brine mass
#                                         ic_new['ct']['H' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'I' + str('%.0f' % (row))].value
#                                         # ice salinity id
#                                         ic_new['ct']['I' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'J' + str('%.0f' % (row))].value
#                                         # ice salinity value
#                                         ic_new['ct']['J' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'K' + str('%.0f' % (row))].value
#                                         # ice conductivity value
#                                         ic_new['ct']['L' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'L' + str('%.0f' % (row))].value
#                                         # Copy conductivity unit
#                                         c_unit = ic_data['CT']['L4'].value
#                                         if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                             c_unit = str('\u03BCS/cm')
#                                         elif c_unit != 'mS/cm':
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                         ic_new['ct']['L4'].value = c_unit
#
#                                         # ice conductivity sample temperature
#                                         ic_new['ct']['M' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'M' + str('%.0f' % (row))].value
#                                         # ice specific conductance
#                                         ic_new['ct']['N' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'N' + str('%.0f' % (row))].value
#                                         # Copy conductance unit
#                                         c_unit = ic_data['CT']['N4'].value
#                                         if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                             c_unit = str('\u03BCS/cm')
#                                         elif c_unit != 'mS/cm':
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                         ic_new['ct']['N4'].value = c_unit
#
#                                         # brine salinity id
#                                         ic_new['ct']['O' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'O' + str('%.0f' % (row))].value
#                                         # brine salinity value
#                                         ic_new['ct']['P' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'P' + str('%.0f' % (row))].value
#                                         # brine conductivity value
#                                         ic_new['ct']['R' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'Q' + str('%.0f' % (row))].value
#                                         c_unit = ic_data['CT']['Q4'].value
#                                         if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                             c_unit = str('\u03BCS/cm')
#                                         elif c_unit != 'mS/cm':
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                         ic_new['ct']['R4'].value = c_unit
#
#                                         # brine conductivity sample temperature
#                                         ic_new['ct']['S' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'R' + str('%.0f' % (row))].value
#                                         # brine specific conductance
#                                         ic_new['ct']['T' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'S' + str('%.0f' % (row))].value
#                                         c_unit = ic_data['CT']['S4'].value
#                                         if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                             c_unit = str('\u03BCS/cm')
#                                         elif c_unit != 'mS/cm':
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                         ic_new['ct']['T4'].value = c_unit
#
#                                         # comment
#                                         ic_new['ct']['U' + str('%.0f' % (5 + jj_row))].value = ic_data['CT'][
#                                             'T' + str('%.0f' % (row))].value
#
#                                 elif data_flag == 2:
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(update_file, 'a') as f:
#                                             f.writelines(ic_name + '\tct\tGenerate depth 1 and depth2 value based on mid center depth')
#                                     for jj_row, row in enumerate(range(start_row, ii_row)):
#                                         if jj_row <= ii_row - 46 - (start_row - 1):
#                                             ic_new['ct'].insert_rows(4 + jj_row)
#                                             for col in opxl.utils.get_column_interval('V', 'Z'):
#                                                 ic_new['ct'][col + str('%.0f' % (4 + jj_row))].fill = blankFILL
#                                             ic_new['ct']['E' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['ct']['H' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['ct']['N' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['ct']['T' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         d_mid = ic_data['CT']['C'+str('%.0f' %(row))].value
#                                         if d_mid is None or isinstance(d_mid, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tct\tDepth mid are not numbers\n')
#                                             ic_new['ct']['A' + str('%.0f' % (4 + jj_row))].value = 'N/A'
#                                             ic_new['ct']['B' + str('%.0f' % (4 + jj_row))].value = 'N/A'
#                                         elif isinstance(d_mid(float, int)):
#                                             if row < ii_row - 1:
#                                                 d_mid_sup = ic_data['CT']['C' + str('%.0f' % (row + 1))].value
#                                             else:
#                                                 d_mid_sup = ic_data['CT']['C' + str('%.0f' % (row - 1))].value
#                                             h_mid = np.abs(d_mid_sup - d_mid)
#
#                                             if d_mid > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tct\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(
#                                                         ic_name + '\tct\tMid depth ' + str('%.2f' % d_mid) + ' likely in cm, change to m\n')
#                                                 d_mid = d_mid / 100
#                                                 h_mid = h_mid / 100
#
#                                             ic_new['ct']['A' + str('%.0f' % (4 + jj_row))].value = d_mid - h_mid
#                                             ic_new['ct']['B' + str('%.0f' % (4 + jj_row))].value = d_mid + h_mid
#
#                                         # ID
#                                         id = ic_data['CT'][ 'D' + str('%.0f' % (row))].value
#                                         if d_mid is not None and id is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tct\tDepth 1 ' + str('%.0f' % d_mid) + ' has no id\n')
#                                         ic_new['ct']['C' + str('%.0f' % (5 + jj_row))].value = id
#                                         # tar mass
#                                         ic_new['ct']['D'+str('%.0f' %(5+jj_row))].value = ic_data['CT']['E'+str('%.0f' %(row))].value
#                                         # sample mass with tar
#                                         ic_new['ct']['E'+str('%.0f' %(5+jj_row))].value = ic_data['CT']['F'+str('%.0f' %(row))].value
#                                         # sample mass
#                                         ic_new['ct']['F'+str('%.0f' %(5+jj_row))].value = ic_data['CT']['G'+str('%.0f' %(row))].value
#                                         # ice mass
#                                         ic_new['ct']['G'+str('%.0f' %(5+jj_row))].value = ic_data['CT']['H'+str('%.0f' %(row))].value
#                                         # brine mass
#                                         ic_new['ct']['H'+str('%.0f' %(5+jj_row))].value = ic_data['CT']['I'+str('%.0f' %(row))].value
#                                         # ice salinity id
#                                         ic_new['ct']['I' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['J' + str('%.0f' % (row))].value
#                                         # ice salinity value
#                                         ic_new['ct']['J' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['K' + str('%.0f' % (row))].value
#                                         # ice conductivity value
#                                         ic_new['ct']['L' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['L' + str('%.0f' % (row))].value
#                                         c_unit = ic_data['CT']['L4'].value
#                                         if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                             c_unit = str('\u03BCS/cm')
#                                         elif c_unit != 'mS/cm':
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                         ic_new['ct']['L4'].value = c_unit
#
#                                         # ice conductivity sample temperature
#                                         ic_new['ct']['M' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['M' + str('%.0f' % (row))].value
#                                         # ice specific conductance
#                                         ic_new['ct']['N' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['N' + str('%.0f' % (row))].value
#                                         c_unit = ic_data['CT']['N4'].value
#                                         if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                             c_unit = str('\u03BCS/cm')
#                                         elif c_unit != 'mS/cm':
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                         ic_new['ct']['N4'].value = c_unit
#                                         # brine salinity id
#                                         ic_new['ct']['O' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['O' + str('%.0f' % (row))].value
#                                         # brine salinity value
#                                         ic_new['ct']['P' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['P' + str('%.0f' % (row))].value
#                                         # brine conductivity value
#                                         ic_new['ct']['R' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['Q' + str('%.0f' % (row))].value
#                                         ic_unit = ic_data['CT']['Q4'].value
#                                         if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                             c_unit = str('\u03BCS/cm')
#                                         elif c_unit != 'mS/cm':
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                         ic_new['ct']['R4'].value = c_unit
#                                         # brine conductivity sample temperature
#                                         ic_new['ct']['S' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['R' + str('%.0f' % (row))].value
#                                         # brine specific conductance
#                                         ic_new['ct']['T' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['S' + str('%.0f' % (row))].value
#                                         c_unit = ic_data['CT']['S4'].value
#                                         if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                             c_unit = str('\u03BCS/cm')
#                                         elif c_unit != 'mS/cm':
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                         ic_new['ct']['T4'].value = c_unit
#                                         # comment
#                                         ic_new['ct']['U' + str('%.0f' % (5 + jj_row))].value = ic_data['CT']['T' + str('%.0f' % (row))].value
#                         unit_flag = 0
#
#                         # RHO-densimetry
#                         if 'Density-densimetry' in ic_data.get_sheet_names():
#                             # Check for value
#                             if ic_ver == '1.2M':
#                                 start_row = 4
#                             else:
#                                 start_row = 5
#
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['Density-densimetry']['A' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             # if no depth entry are present, check existence of mid-center value
#                             if data_flag == 0:
#                                 row_flag = 0
#                                 while row_flag < 2:
#                                     if ic_data['Density-densimetry']['C' + str('%.0f' % ii_row)].value is None:
#                                         row_flag += 1
#                                     else:
#                                         row_flag = 0
#                                         data_flag = 2
#                                     ii_row += 1
#                                 if data_flag == 2:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tDensity-densimetry\tOnly depth entry for section center\n')
#
#                             # If there is depth entry
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['Density-densimetry']['C1'].value
#                                 vert_dir = ic_data['Density-densimetry']['E1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tDensity-densimetry\tVertical reference unknown\n')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tDensity-densimetry\tVertical direction unknown\n')
#
#                                 if ic_new['metadata-core']['D13'].value is None:
#                                     ic_new['metadata-core']['D13'].value = vert_ref
#                                     ic_new['metadata-core']['D14'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D13'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tDensity-densimetry\tVertical reference not consistent with metadata-core\n')
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tDensity-densimetry\tVertical direction not consistent with metadata-core\n')
#
#                                 # Data (depth, ID,  salinity...)
#                                 if data_flag == 1:
#                                     depth1_str_flag = 0
#                                     depth2_str_flag = 0
#                                     for jj_row, row in enumerate(range(start_row, ii_row)):
#                                         if jj_row <= ii_row - 46 - (start_row - 1):
#                                             ic_new['density-densimetry'].insert_rows(4 + jj_row)
#                                             for col in opxl.utils.get_column_interval('I', 'Z'):
#                                                 ic_new['density-densimetry'][col + str('%.0f' % (4 + jj_row))].fill = blankFILL
#                                             ic_new['density-densimetry']['B' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['density-densimetry']['E' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                             ic_new['density-densimetry']['G' + str('%.0f' % (4 + jj_row))].border = opxl.styles.Border(
#                                                 right=opxl.styles.Side(border_style='thin', color='000000'))
#                                         d1 = ic_data['Density-densimetry']['A'+str('%.0f' %(row))].value
#                                         if d1 is None or isinstance(d1, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tDensity-densimetry\tDepth 1 are not number\n')
#                                         elif isinstance(d1, (float, int)):
#                                             if d1 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tDensity-densimetry\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(
#                                                         ic_name + '\tDensity-densimetry\tDepth 1 ' + str('%.2f' % d1) + ' likely in cm, change to m\n')
#                                                 d1 = d1 / 100
#                                         ic_new['density-densimetry']['A' + str('%.0f' % (4 + jj_row))].value = d1
#
#                                         d2 = ic_data['Density-densimetry']['B'+str('%.0f' %(row))].value
#                                         if d2 is None or isinstance(d2, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tDensity-densimetry\tDepth 2 are not number\n')
#                                         elif isinstance(d2, (float, int)):
#                                             if d2 > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tDensity-densimetry\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(
#                                                         ic_name + '\tDensity-densimetry\tDepth 2 ' + str('%.2f' % d2) + ' likely in cm, change to m\n')
#                                                 d2 = d2 / 100
#                                         ic_new['density-densimetry']['B'+str('%.0f' %(4+jj_row))].value = d2
#
#                                         # density ID
#                                         id = ic_data['Density-densimetry']['D'+str('%.0f' %(row))].value
#                                         if d1 is not None and id is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tdensity-densimetry\tDepth 1 ' + str('%.0f' % d1) + ' has no id\n')
#                                         ic_new['density-densimetry']['C'+str('%.0f' %(4+jj_row))].value = id
#
#                                         # density value
#                                         rho = ic_data['Density-densimetry']['G'+str('%.0f' %(row))].value
#                                         ic_new['density-densimetry']['D'+str('%.0f' %(4+jj_row))].value = rho
#                                         if d1 is not None and rho is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tdensity-densimetry\tDepth 1 ' + str('%.0f' % d1) + ' has no density value\n')
#                                         # mass (air)
#                                         ic_new['density-densimetry']['F'+str('%.0f' %(4+jj_row))].value = ic_data['Density-densimetry']['E'+str('%.0f' %(row))].value
#                                         # mass (liquid)
#                                         ic_new['density-densimetry']['G'+str('%.0f' %(4+jj_row))].value = ic_data['Density-densimetry']['F'+str('%.0f' %(row))].value
#                                         # comment
#                                         ic_new['density-densimetry']['H'+str('%.0f' %(4+jj_row))].value = ic_data['Density-densimetry']['H'+str('%.0f' %(row))].value
#
#                                 elif data_flag == 2:
#                                     if ic_new['metadata-core']['D14'].value != vert_dir:
#                                         with open(update_file, 'a') as f:
#                                             f.writelines(ic_name + '\tdensity-densimetry\tGenerate depth 1 and depth2 value based on mid center depth\n')
#                                     for jj_row, row in enumerate(range(start_row, ii_row)):
#                                         d_mid = ic_data['Density-densimetry']['C' + str('%.0f' % (row))].value
#
#                                         if d_mid is None or isinstance(d_mid, str):
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tDensity-densimetry\tDepth mid are not numbers\n')
#                                             ic_new['density-densimetry']['A' + str('%.0f' % (4 + jj_row))].value = 'N/A'
#                                             ic_new['density-densimetry']['B' + str('%.0f' % (4 + jj_row))].value = 'N/A'
#                                         elif isinstance(d_mid(float, int)):
#                                             if row < ii_row - 1:
#                                                 d_mid_sup = ic_data['Density-densimetry']['C' + str('%.0f' % (row + 1))].value
#                                             else:
#                                                 d_mid_sup = ic_data['Density-densimetry']['C' + str('%.0f' % (row - 1))].value
#                                             h_mid = np.abs(d_mid_sup - d_mid)
#
#                                             if d_mid > m_unit:
#                                                 if unit_flag == 0:
#                                                     with open(error_file, 'a') as f:
#                                                         f.writelines(ic_name + '\tdensity-densimetry\tCheck unit for depth\n')
#                                                     unit_flag = 1
#                                                 with open(update_file, 'a') as f:
#                                                     f.writelines(
#                                                         ic_name + '\tdensity-densimetry\tMid depth ' + str('%.2f' % d_mid) + ' likely in cm, change to m\n')
#                                                 d_mid = d_mid / 100
#                                                 h_mid = h_mid / 100
#
#                                             ic_new['density-densimetry']['A' + str('%.0f' % (4 + jj_row))].value = d_mid - h_mid
#                                             ic_new['density-densimetry']['B' + str('%.0f' % (4 + jj_row))].value = d_mid + h_mid
#
#                                         # density ID
#                                         id = ic_data['Density-densimetry']['D'+str('%.0f' %(row))].value
#                                         if d_mid is not None and id is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tdensity-densimetry\tDepth 1 ' + str('%.0f' % d_mid) + ' has no id\n')
#                                         ic_new['density-densimetry']['C'+str('%.0f' %(4+jj_row))].value = id
#
#                                         # density value
#                                         rho = ic_data['Density-densimetry']['G'+str('%.0f' %(row))].value
#                                         ic_new['density-densimetry']['D'+str('%.0f' %(4+jj_row))].value = rho
#                                         if d_mid is not None and rho is None:
#                                             with open(error_file, 'a') as f:
#                                                 f.writelines(ic_name + '\tdensity-densimetry\tDepth 1 ' + str('%.0f' % d_mid) + ' has no density value\n')
#                                         # mass (air)
#                                         ic_new['density-densimetry']['F'+str('%.0f' %(4+jj_row))].value = ic_data['Density-densimetry']['E'+str('%.0f' %(row))].value
#                                         # mass (liquid)
#                                         ic_new['density-densimetry']['G'+str('%.0f' %(4+jj_row))].value = ic_data['Density-densimetry']['F'+str('%.0f' %(row))].value
#                                         # comment
#                                         ic_new['density-densimetry']['H'+str('%.0f' %(4+jj_row))].value = ic_data['Density-densimetry']['H'+str('%.0f' %(row))].value
#                         unit_flag = 0
#
#                         if 'snow' in ic_data.get_sheet_names():
#                             # Check for salinity data:
#                             if ic_ver == '1.2M':
#                                 start_row = 4
#                             else:
#                                 start_row = 5
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['snow']['A' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['snow']['C1'].value
#                                 vert_dir = ic_data['snow']['E1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsnow\tVertical reference unknown\n')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsnow\tVertical direction unknown\n')
#
#                                 if ic_new['metadata-core']['D15'].value is None:
#                                     ic_new['metadata-core']['D15'].value = vert_ref
#                                     ic_new['metadata-core']['D16'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D15'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tVertical reference not consistent with snow metadata-core\n')
#                                     if ic_new['metadata-core']['D16'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tVertical direction not consistent with snow metadata-core\n')
#
#                                 # Data
#                                 for jj_row, row in enumerate(range(start_row, ii_row)):
#                                     d1 = ic_data['snow']['A' + str('%.0f' % (row))].value
#                                     if d1 is None or isinstance(d1, str):
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tDepth 1 are not number\n')
#                                     elif isinstance(d1, (float, int)):
#                                         if d1 > m_unit:
#                                             if unit_flag == 0:
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tsnow\tCheck unit for depth\n')
#                                                 unit_flag = 1
#                                             with open(update_file, 'a') as f:
#                                                 f.writelines(
#                                                     ic_name + '\tsnow\tDepth 1 ' + str('%.2f' % d1) + ' likely in cm, change to m\n')
#                                             d1 = d1 / 100
#                                     ic_new['snow']['A' + str('%.0f' % (4 + jj_row))].value = d1
#
#                                     d2 = ic_data['snow']['B' + str('%.0f' % (row))].value
#                                     if d2 is None or isinstance(d1, str):
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tDepth 2 are not number\n')
#                                     elif isinstance(d1, (float, int)):
#                                         if d2 > m_unit:
#                                             if unit_flag == 0:
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tsnow\tCheck unit for depth\n')
#                                                 unit_flag = 1
#                                             with open(update_file, 'a') as f:
#                                                 f.writelines(
#                                                     ic_name + '\tsnow\tDepth 2 ' + str('%.2f' % d2) + ' likely in cm, change to m\n')
#                                             d2 = d2 / 100
#                                     ic_new['snow']['B' + str('%.0f' % (4 + jj_row))].value = d2
#
#                                     # ID
#                                     id = ic_data['snow']['C' + str('%.0f' % (row))].value
#                                     if d1 is not None and id is None:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tDepth 1 ' + str('%.0f' % d1) + ' has no id\n')
#                                     ic_new['snow']['C' + str('%.0f' % (4 + jj_row))].value = id
#
#                                     # Salinity
#
#                                     # Salinity value
#                                     s = ic_data['snow']['D' + str('%.0f' % (row))].value
#                                     ic_new['snow']['D' + str('%.0f' % (4 + jj_row))].value = s
#
#                                     # Conductivity
#                                     c = ic_data['snow']['E' + str('%.0f' % (row))].value
#                                     ic_new['snow']['F' + str('%.0f' % (4 + jj_row))].value = c
#                                     ic_new['snow']['G' + str('%.0f' % (4 + jj_row))].value = ic_data['snow']['F' + str('%.0f' % (row))].value
#                                     # Copy conductivity unit
#                                     c_unit = ic_data['snow']['E4'].value
#                                     if c_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                         c_unit = str('\u03BCS/cm')
#                                     elif c_unit != 'mS/cm':
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tUnknown conductivity unit\n')
#                                     ic_data['snow']['F3'].value = c_unit
#
#                                     # Specific conductance
#                                     cs = ic_data['snow']['G' + str('%.0f' % (row))].value
#                                     ic_new['snow']['H' + str('%.0f' % (4 + jj_row))].value = c
#                                     # Copy conductivity unit
#                                     cs_unit = ic_data['snow']['E4'].value
#                                     if cs_unit == 'uS/cm' or c_unit == '\u03BCS/cm':
#                                         cs_unit = str('\u03BCS/cm')
#                                     elif cs_unit != 'mS/cm':
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tUnknown specific conductance unit\n')
#                                     ic_data['snow']['F3'].value = c_unit
#                                     if d1 is not None and (s is None or c is None or cs is None):
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tDepth 1 ' + str('%.0f' % d1) + ' has no salinity value\n')
#                                     del s, c, cs
#
#                                     # Isotope dO18
#                                     ic_new['snow']['I' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'H' + str('%.0f' % (row))].value
#                                     ic_new['snow']['J' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'I' + str('%.0f' % (row))].value
#                                     # Isotope DD
#                                     ic_new['snow']['L' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'J' + str('%.0f' % (row))].value
#                                     ic_new['snow']['M' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'K' + str('%.0f' % (row))].value
#                                     # Density
#                                     ic_new['snow']['O' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'L' + str('%.0f' % (row))].value
#                                     ic_new['snow']['P' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'M' + str('%.0f' % (row))].value
#                                     # Comment
#                                     ic_new['snow']['R' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'N' + str('%.0f' % (row))].value
#
#                                     # ECO sample
#                                     ic_new['snow']['X' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'R' + str('%.0f' % (row))].value
#                                     ic_new['snow']['Y' + str('%.0f' % (4 + jj_row))].value = ic_data['snow'][
#                                         'S' + str('%.0f' % (row))].value
#                                     ic_new['snow']['Y' + str('%.0f' % (4 + jj_row))].number_format = '@'
#                             # Check for temperature data:
#                             ii_row = 5
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['snow']['O' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['snow']['C1'].value
#                                 vert_dir = ic_data['snow']['E1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsnow\tVertical reference unknown\n')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsnow\tVertical direction unknown\n')
#
#                                 if ic_new['metadata-core']['D15'].value is None:
#                                     ic_new['metadata-core']['D15'].value = vert_ref
#                                     ic_new['metadata-core']['D16'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D15'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tVertical reference not consistent with metadata-core\n')
#                                     if ic_new['metadata-core']['D16'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tVertical direction not consistent with metadata-core\n')
#
#                                 # Data
#                                 for jj_row, row in enumerate(range(start_row, ii_row)):
#                                     d1 = ic_data['snow']['O' + str('%.0f' % (row))].value
#                                     if d1 is None or isinstance(d1, str):
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tTemperature Depth 1 are not number\n')
#                                     elif isinstance(d1, (float, int)):
#                                         if d1 > m_unit:
#                                             if unit_flag == 0:
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tsnow\tCheck unit for Temperature depth\n')
#                                                 unit_flag = 1
#                                             with open(update_file, 'a') as f:
#                                                 f.writelines(
#                                                     ic_name + '\tsnow\tTemperature depth 1 ' + str('%.2f' % d1) + ' likely in cm, change to m\n')
#                                             d1 = d1 / 100
#                                     ic_new['snow']['T' + str('%.0f' % (4 + jj_row))].value = d1
#
#                                     # Temperature value
#                                     t = ic_data['snow']['P' + str('%.0f' % (row))].value
#                                     ic_new['snow']['U' + str('%.0f' % (4 + jj_row))].value = t
#
#                                     if d1 is not None and t is None:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tDepth 1 ' + str('%.0f' % d1) + ' has no salinity value\n')
#                                     del t
#
#                             # Check for extra sample:
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['snow']['U' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#
#                             if data_flag > 0:
#                                 # Vertical reference and direction
#                                 vert_ref = ic_data['snow']['C1'].value
#                                 vert_dir = ic_data['snow']['E1'].value
#
#                                 if vert_ref not in vert_ref_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsnow\tVertical reference unknown\n')
#                                 if vert_dir not in vert_dir_list:
#                                     with open(error_file, 'a') as f:
#                                         f.writelines(ic_name + '\tsnow\tVertical direction unknown\n')
#
#                                 if ic_new['metadata-core']['D15'].value is None:
#                                     ic_new['metadata-core']['D15'].value = vert_ref
#                                     ic_new['metadata-core']['D16'].value = vert_dir
#                                 else:
#                                     if ic_new['metadata-core']['D15'].value != vert_ref:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tVertical reference not consistent with metadata-core\n')
#                                     if ic_new['metadata-core']['D16'].value != vert_dir:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tVertical direction not consistent with metadata-core\n')
#
#                                 # Data
#                                 for jj_row, row in enumerate(range(start_row, ii_row)):
#                                     d1 = ic_data['snow']['U' + str('%.0f' % (row))].value
#                                     if d1 is None or isinstance(d1, str):
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tExtra sample Depth 1 are not number\n')
#                                     elif isinstance(d1, (float, int)):
#                                         if d1 > m_unit:
#                                             if unit_flag == 0:
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tsnow\tCheck unit for Extra sample  depth\n')
#                                                 unit_flag = 1
#                                             with open(update_file, 'a') as f:
#                                                 f.writelines(
#                                                     ic_name + '\tsnow\tDepth 1 ' + str('%.2f' % d1) + ' likely in cm, change to m\n')
#                                             d1 = d1 / 100
#                                     ic_new['snow']['AB' + str('%.0f' % (4 + jj_row))].value = d1
#
#                                     d2 = ic_data['snow']['V' + str('%.0f' % (row))].value
#                                     if d2 is None or isinstance(d1, str):
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tExtra sample Depth 2 are not number\n')
#                                     elif isinstance(d1, (float, int)):
#                                         if d2 > m_unit:
#                                             if unit_flag == 0:
#                                                 with open(error_file, 'a') as f:
#                                                     f.writelines(ic_name + '\tsnow\tCheck unit for Extra sample depth\n')
#                                                 unit_flag = 1
#                                             with open(update_file, 'a') as f:
#                                                 f.writelines(
#                                                     ic_name + '\tsnow\tDepth 2 ' + str('%.2f' % d2) + ' likely in cm, change to m\n')
#                                             d2 = d2 / 100
#                                     ic_new['snow']['AC' + str('%.0f' % (4 + jj_row))].value = d2
#
#                                     # ID
#                                     id = ic_data['snow']['W' + str('%.0f' % (row))].value
#                                     if d1 is not None and id is None:
#                                         with open(error_file, 'a') as f:
#                                             f.writelines(ic_name + '\tsnow\tExtra sample Depth 1 ' + str('%.0f' % d1) + ' has no id\n')
#                                     ic_new['snow']['AD' + str('%.0f' % (4 + jj_row))].value = id
#
#                             # Check for snow micropen data:
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             while row_flag < 2:
#                                 if ic_data['snow']['Y' + str('%.0f' % ii_row)].value is None and ic_data['snow']['Z' + str('%.0f' % ii_row)].value is None:
#                                     row_flag += 1
#                                 else:
#                                     row_flag = 0
#                                     data_flag = 1
#                                 ii_row += 1
#                             if data_flag > 0:
#                                 # Data
#                                 for jj_row, row in enumerate(range(start_row, ii_row)):
#                                     # reading number
#                                     ic_new['snow']['AF' + str('%.0f' % (4 + jj_row))].value = ic_data['snow']['Y' + str('%.0f' % (row))].value
#
#                                     # action type
#                                     ic_new['snow']['AG' + str('%.0f' % (4 + jj_row))].value = ic_data['snow']['Z' + str('%.0f' % (row))].value
#
#                                     # ID
#                                     ic_new['snow']['AH' + str('%.0f' % (4 + jj_row))].value = ic_data['snow']['AA' + str('%.0f' % (row))].value
#                                     ic_new['snow']['AH' + str('%.0f' % (4 + jj_row))].number_format = '00'
#
#                             # Check for SWE data
#                             ii_row = start_row
#                             row_flag = 0
#                             data_flag = 0
#                             if ic_data['snow']['AC' + str('%.0f' % ii_row)].value is not None:
#                                 # SWE weight
#                                 ic_new['snow']['AJ' + str('%.0f' % (ii_row))].value = ic_data['snow']['AC' + str('%.0f' % (ii_row))].value
#                                 # SWE height
#                                 ic_new['snow']['AK' + str('%.0f' % (ii_row))].value = ic_data['snow']['AD' + str('%.0f' % (ii_row))].value
#
#                         ## SAVE
#                         ic_new.save(temp_core_fp)
#                         shutil.copy(temp_core_fp, trg_core_fp)
#                         os.remove(temp_core_fp)