import pandas as pd
import numpy as np
import os
import datetime
from shutil import copyfile
import glob
from datetime import date


smerge_as_string = "SMERGE.INP      2.1             Hour Start and End Times with Seconds"+"\n"+\
"-------------------------------------------------------------------------------"+"\n"+\
"\n"+\
"                     SMERGE PROCESSOR CONTROL FILE"+"\n"+\
"                 --------------------------------------"+"\n"+\
"\n"+\
"    CALMET accepts data for a number of 'surface meteorology stations'"+"\n"+\
"    in a single SURF.DAT file.  SMERGE creates this file from several"+"\n"+\
"    single-station files of hourly data.  Use SMERGE one or more times"+"\n"+\
"    to build the SURF.DAT file."+"\n"+\
"\n"+\
"-------------------------------------------------------------------------------"+"\n"+\
"\n"+\
"INPUT GROUP: 0 -- Input and Output File Names"+"\n"+\
"-----------------------------------------------------"+"\n"+\
"\n"+\
"--------------"+"\n"+\
"Subgroup (0a)"+"\n"+\
"--------------"+"\n"+\
"\n"+\
"    Number of formatted Surface Station files provided"+"\n"+\
"    in Subgroup 0b.  Up to MXFF are allowed in 1 application,"+"\n"+\
"    although this may be limited by your operating system."+"\n"+\
"    MXFF is set in PARAMS.SMG, which is compiled into SMERGE.EXE."+"\n"+\
"    (NFF)          No Default         ! NFF = NUMFILES TO CHANGE !"+"\n"+\
"\n"+\
"Other Input and Output Files:"+"\n"+\
"-----------------------------"+"\n"+\
"\n"+\
"Default Name  Type          File Name"+"\n"+\
"------------  ----          ---------"+"\n"+\
"    PREV.DAT       input    ! PREVDAT = prev.dat !"+"\n"+\
"    SURF.DAT       output   ! SURFDAT = SURF.dat !"+"\n"+\
"    SMERGE.LST     output   ! RUNLST = SURF.lst !"+"\n"+\
"\n"+\
"\n"+\
"    All file names will be converted to lower case if LCFILES = T"+"\n"+\
"    Otherwise, if LCFILES = F, file names will be converted to UPPER CASE"+"\n"+\
"    (LCFILES)       Default: T       ! LCFILES = F !"+"\n"+\
"             T = lower case"+"\n"+\
"             F = UPPER CASE"+"\n"+\
"    NOTE: File/path names can be up to 70 characters in length"+"\n"+\
"\n"+\
"!END!"+"\n"+\
"\n"+\
"-------------"+"\n"+\
"Subgroup (0b)"+"\n"+\
"-------------"+"\n"+\
"\n"+\
"    The following NFF formatted Surface Station files are processed."+"\n"+\
"    Enter NFF 4-line groups identifying the file name (SFCMET), the"+"\n"+\
"    station number (IFSTN), the station elevation (optional) in meters"+"\n"+\
"    (XELEV), and the time zone of the data (ASTZ) for each file,"+"\n"+\
"    followed by a group terminator."+"\n"+\
"\n"+\
"    NOTE:  ASTZ identifies the time zone used in the dataset.  The"+"\n"+\
"           TD3505 and TD9956 data are prepared in UTC time rather than"+"\n"+\
"           local time, so ASTZ = UTC+0000. is expected for these."+"\n"+\
"\n"+\
"    The optional station elevation is a default value used to calculate"+"\n"+\
"    a station pressure from altimeter or sea-level pressure if the"+"\n"+\
"    station presure is missing and the station elevation is missing in"+"\n"+\
"    the file.  If XELEV is not assigned a value (i.e. XELEV does not"+"\n"+\
"    appear in this control file), then no default elevation is available"+"\n"+\
"    and station pressure remains missing."+"\n"+\
"\n"+\
"\n"+\
"PUT STATION DETAILS IN HERE"+"\n"+\
"\n"+\
"-----------------------------------------------------------------------------"+"\n"+\
"INPUT GROUP: 1 -- Run control parameters"+"\n"+\
"---------------"+"\n"+\
"\n"+\
"   --- Processing Period ---"+"\n"+\
"\n"+\
"       Starting date:  Year (IBYR) -- No default   ! IBYR = YYYY !"+"\n"+\
"                      Month (IBMO) -- No default   ! IBMO = MM !"+"\n"+\
"                        Day (IBDY) -- No default   ! IBDY = DD !"+"\n"+\
"                       Hour (IBHR) -- No default   ! IBHR = HH !"+"\n"+\
"                    Second (IBSEC) -- No default   ! IBSEC = 0 !"+"\n"+\
"\n"+\
"       Ending date:    Year (IEYR) -- No default   ! IEYR = YYYY !"+"\n"+\
"                      Month (IEMO) -- No default   ! IEMO = MM !"+"\n"+\
"                        Day (IEDY) -- No default   ! IEDY = DD !"+"\n"+\
"                       Hour (IEHR) -- No default   ! IEHR = HH !"+"\n"+\
"                    Second (IESEC) -- No default   ! IESEC = 0 !"+"\n"+\
"\n"+\
"      UTC time zone (char*8)(ABTZ) -- No default   ! ABTZ = UTC--TIME !"+"\n"+\
"         PST = UTC-0800, MST = UTC-0700"+"\n"+\
"         CST = UTC-0600, EST = UTC-0500"+"\n"+\
"         GMT = UTC+0000"+"\n"+\
"\n"+\
"   -----------------------"+"\n"+\
"   NOTE:  Use explicit times in hours and seconds in time zone ABTZ."+"\n"+\
"\n"+\
"   --- File Options ---"+"\n"+\
"\n"+\
"       Previous SURF.DAT file is used in this run?"+"\n"+\
"       (LPREV)          No Default        ! LPREV = F !"+"\n"+\
"             T = Surface data from a previous SURF.DAT file are used"+"\n"+\
"             F = Previous SURF.DAT file is not used"+"\n"+\
"\n"+\
"       Number of stations to use from previous SURF.DAT file"+"\n"+\
"       (NBSTN)          Default: 0        ! NBSTN = 0 !"+"\n"+\
"             0 = Use ALL stations"+"\n"+\
"            >0 = Use only those NBSTN stations listed in Input Group 2"+"\n"+\
"\n"+\
"   --- File Formats ---"+"\n"+\
"\n"+\
"       Format of previous SURF.DAT file"+"\n"+\
"       (Used only if LPREV = T"+"\n"+\
"       (INFORM)          Default: 2        ! INFORM = 2 !"+"\n"+\
"             1 = Unformatted"+"\n"+\
"             2 = Formatted"+"\n"+\
"\n"+\
"       Format of output SURF.DAT FILE"+"\n"+\
"       (IOFORM)          Default: 2        ! IOFORM = 2 !"+"\n"+\
"             1 = Unformatted"+"\n"+\
"             2 = Formatted"+"\n"+\
"       (IOPACK)          Default: 0        ! IOPACK = 0 !"+"\n"+\
"             0 = NOT packed"+"\n"+\
"             1 = Packed (used only if IOFORM = 1)"+"\n"+\
"\n"+\
"       Type of ALL Surface Station files in this run"+"\n"+\
"       (JDAT)            No Default        ! JDAT = 8 !"+"\n"+\
"             1 = CD144"+"\n"+\
"             2 = NCDC SAMSON"+"\n"+\
"             3 = NCDC HUSWO"+"\n"+\
"             5 = ISHWO"+"\n"+\
"             6 = TD3505"+"\n"+\
"             7 = TD9956 (full DATSAV3)"+"\n"+\
"             8 = GENERIC (.CSV format - see 'sample_generic.csv')"+"\n"+\
"\n"+\
"     Format of input HUSWO file"+"\n"+\
"     (Used only if JDAT = 3)"+"\n"+\
"     (IHUSWO)                   Default: 1     ! IHUSWO = 1 !"+"\n"+\
"        1 = All data are in English units"+"\n"+\
"        2 = All data are in Metric units"+"\n"+\
"\n"+\
"     Calculate missing station pressure from altimeter or sea level"+"\n"+\
"     pressure?"+"\n"+\
"     (applies to JDAT = 1-3,8; always T for JDAT = 5-7)"+"\n"+\
"     (LPCALC)                   Default: F     ! LPCALC = F !"+"\n"+\
"\n"+\
"\n"+\
"!END!"+"\n"+\
"\n"+\
"-----------------------------------------------------------------------------"+"\n"+\
"INPUT GROUP: 2 -- Stations used from previous SURF.DAT file"+"\n"+\
"---------------"+"\n"+\
"\n"+\
"   Data for the following NBSTN stations in the previous SURF.DAT"+"\n"+\
"   file identified as PREV.DAT are transferred to the new SURF.DAT"+"\n"+\
"   file created in this run.  Enter NBSTN lines identifying the"+"\n"+\
"   station number (IBSTN) for each, followed by a group terminator."+"\n"+\
"   This Input Group is used only if LPREV=T and NBSTN>0.  All stations"+"\n"+\
"   from a previous SURF.DAT file are transferred to the new SURF.DAT"+"\n"+\
"   file if NBSTA=0."+"\n"+\
"\n"+\
"\n"+\
"\n"+\
"\n"+\
"   -----------------------"+"\n"+\
"   Each line is treated as a separate input subgroup and therefore"+"\n"+\
"   must end with an input group terminator."


def make_smerge_text(template_txt, num_stations, stations_text, start_date, end_date, tz):
    smerge_text = template_txt
    smerge_text = smerge_text.replace("NUMFILES TO CHANGE", str(num_stations))
    smerge_text = smerge_text.replace("PUT STATION DETAILS IN HERE", stations_text)
    smerge_text = smerge_text.replace("IBYR = YYYY", "IBYR = "+str(start_date.year))
    smerge_text = smerge_text.replace("IBMO = MM", "IBMO = " + str(start_date.month))
    smerge_text = smerge_text.replace("IBDY = DD", "IBDY = " + str(start_date.day))
    smerge_text = smerge_text.replace("IBHR = HH", "IBHR = " + str(start_date.hour))
    smerge_text = smerge_text.replace("IEYR = YYYY", "IEYR = "+str(end_date.year))
    smerge_text = smerge_text.replace("IEMO = MM", "IEMO = " + str(end_date.month))
    smerge_text = smerge_text.replace("IEDY = DD", "IEDY = " + str(end_date.day))
    smerge_text = smerge_text.replace("IEHR = HH", "IEHR = " + str(end_date.hour))
    smerge_text = smerge_text.replace("ABTZ = UTC--TIME", "ABTZ = UTC" + tz)
    return smerge_text


def import_csv(file, lines_to_skip):
    #import csv into pandas dataframe
    df = pd.read_csv(file, skiprows=lines_to_skip, header=None)
    df.iloc[:,-1] = pd.to_datetime(df.iloc[:,-1])
    return df


def slice_data_by_dates(df, start_date, end_date):
    mask = (df.iloc[:,-1] > start_date) & (df.iloc[:,-1] < end_date)
    sliced_df = df.loc[mask]
    return sliced_df


# this function pulls data from an AECOM BoM DB style csv and formats it into SMERGE unput format
def format_sliced_df(df, header_lines, fill_blanks):
    new_df = pd.DataFrame()
    new_df['A'] = pd.DatetimeIndex(df.iloc[:,-1]).month
    new_df['B'] = pd.DatetimeIndex(df.iloc[:,-1]).day
    new_df['C'] = pd.DatetimeIndex(df.iloc[:,-1]).year
    new_df['C'] = new_df['C'].apply(lambda x: str(x)[-2:])
    new_df['D'] = pd.DatetimeIndex(df.iloc[:,-1]).hour
    new_df['D'] = new_df['D'].apply(lambda x: str(x) if x==0 else str(x)+"00")
    new_df['E'] = df.iloc[:,2].tolist()
    new_df['E'] = new_df['E'].apply(lambda x: 9999 if np.isnan(x) else round(x,1))
    new_df['F'] = df.iloc[:,1].tolist()
    new_df['F'] = new_df['F'].apply(lambda x: 0 if np.isnan(x) else x)
    new_df['G'] = df.iloc[:,27].tolist()
    new_df['G'] = new_df['G'].apply(lambda x: 9999 if np.isnan(x) else round(x, 1))
    new_df['H'] = df.iloc[:,5].tolist()
    new_df['H'] = new_df['H'].apply(lambda x: 9999 if np.isnan(x) else round(x, 1))
    new_df['I'] = df.iloc[:,10].tolist()
    new_df['I'] = new_df['I'].apply(lambda x: 9999 if np.isnan(x) else round(x, 1))
    new_df['J'] = df.iloc[:,8].tolist()
    new_df['J'] = new_df['J'].apply(lambda x: 9999 if np.isnan(x) else round(x/3.6, 1))
    new_df['K'] = df.iloc[:,25].tolist()
    new_df['K'] = new_df['K'].apply(lambda x: 9999 if np.isnan(x) else x)
    new_df['L'] = df.iloc[:,20].tolist()
    new_df['L'] = new_df['L'].apply(lambda x: 9999 if np.isnan(x) or x==0 else round(x*3.28/100,0))
    if fill_blanks == True:
        new_df.E = new_df.E.apply(lambda x: round(new_df.E.mean(),1) if x==9999 else round(x, 1))
        new_df.G = new_df.G.apply(lambda x: round(new_df.G.mean(),1) if x==9999 else round(x, 1))
        new_df.H = new_df.H.apply(lambda x: round(new_df.H.mean(), 1) if x==9999 else round(x, 1))
        print("\nTemp, RH, and pressure data replaced with average values")
    new_df.loc[-3] = header_lines[0]
    new_df.loc[-2] = header_lines[1]
    new_df.loc[-1] = header_lines[2]
    new_df.sort_index(inplace=True)
    return new_df


def smerge_stations_text(filenames, station_ids, tz):
    station_text = "    ! SFCMET = FILENAME !" +"\n" + \
               "    ! IFSTN = 999999 !" + "\n" + \
               "    ! ASTZ = UTC+1000 ! !END!"
    x = 0
    output_text = ""
    for file in filenames:
        station_text = station_text.replace("FILENAME", str(file))
        if len(station_ids[x]) < 5:
            station_id = "00" + station_ids[x]
        elif len(station_ids[x]) < 6:
            station_id = "0" + station_ids[x]
        else:
            station_id = station_ids[x]
        station_text = station_text.replace("999999", station_id)
        station_text = station_text.replace("+1000", tz)
        x+=1
        output_text += station_text + "\n"
        station_text = "    ! SFCMET = FILENAME !" + "\n" + \
                       "    ! IFSTN = 999999 !" + "\n" + \
                       "    ! ASTZ = UTC+1000 ! !END!"
    return output_text


def write_file(file, text):
    with open(file, 'w') as filehandle:
        filehandle.write(text)
    return None


def replace_missing_data(df, max_consecutive_values, cols_to_fill, station_name):
    new_df = df
    column_loc = [4,6,7,8,9]
    column_dict = {8:"wind direction", 9:"wind speed", 7:"RH", 6:"pressure", 4:"temperature"}
    print(f"\n********** Auto-fill results for {station_name} **********\n")
    for column in column_loc:
        data_df = pd.DataFrame()
        data_df['data'] = df.iloc[:,column]
        data_df = data_df.iloc[3:]
        criteria = data_df.data == 9999
        missing_data_df = data_df[criteria]
        missing_data_values = missing_data_df.index.tolist()
        #print(f"Index list of missing hours for {column_dict.get(column)} is {missing_data_values}")
        num_missing = len(missing_data_values)
        count = 0
        longest_run_missing_data = 0
        num_missing_changed = 0
        num_missing_not_changed = 0

        for x in range(data_df.shape[0]):
            if new_df.iloc[x,column] == 9999:
                count += 1
                if new_df.iloc[x+1,column] != 9999:
                    #print(f"Number of consecutive missing values is {count}")
                    if longest_run_missing_data < count:
                        longest_run_missing_data = count
                    if count <= max_consecutive_values:
                        num_missing_changed += count
                        if x > 2 * max_consecutive_values + 2:
                            for y in range(count):
                                if column in cols_to_fill:
                                    new_df.iloc[x-y,column] = new_df.iloc[(x-(count*2-1)+y),column]
                        else:
                            for y in range(count):
                                if column in cols_to_fill:
                                    new_df.iloc[x+3,column] = new_df.iloc[x+count+y,column]
                    else:
                        num_missing_not_changed += count
            else:
                count = 0
        print(f"TOTAL missing {column_dict.get(column)} hours:                               {num_missing}")
        print(f"The longest run of missing hours for {column_dict.get(column)}:     {longest_run_missing_data}")
        if column in cols_to_fill:
            print(f"Number of {column_dict.get(column)} hours auto-filled:                   {num_missing_changed}")
            if num_missing_not_changed == 0:
                print(f"Number of {column_dict.get(column)} hours retained as '9999':       {num_missing_not_changed}\n")
            else:
                print(f"Number of {column_dict.get(column)} hours retained as '9999':       {num_missing_not_changed}     ****WARNING - increase 'max_consecutive values' or manually edit SMERGE csv to account for long runs of missing data****\n")
        else:
            print('Auto-fill not selected for this parameter\n')
        # x = 1
        # count = 1
        # consecutive = 1
        # while x < num_missing:
        #     if (missing_data_values[x] - missing_data_values[x-1]) == 1:
        #         count += 1
        #         if count > consecutive:
        #             consecutive += 1
        #     else:
        #         count = 1
        #     x += 1
        # if num_missing == 0:
        #     num_consec = 0
        # else:
        #     num_consec = consecutive
        # print(f"\nMax consecutive missing hours for {column_dict.get(column)} is {num_consec}")
        # if consecutive < max_consecutive_values+1:
        #     print(f"Auto-replaced any missing {column_dict.get(column)} hours")
        #     for index in missing_data_values:
        #         if index > 4:
        #             new_df.iloc[index+3,column] = new_df.iloc[index+3-consecutive,column]
        #         else:
        #             new_df.iloc[index+3,column] = new_df.iloc[index+3+consecutive,column]
        # else:
        #     print(f"There are more than {max_consecutive_values} consecutive hours of missing {column_dict.get(column)} data - suggest manual edit")
        #     print(f"Missing hours in {column_dict.get(column)} retained as '9999' values")
    return new_df


BoM_style_df_cols = ['Station Number','Precipitation since last (AWS) observation in mm',
                     'Air Temperature in degrees Celsius','Wet bulb temperature in degrees Celsius',
                     'Dew point temperature in degrees Celsius','Relative humidity in percentage %',
                     'Vapour pressure in hPa','Saturated vapour pressure in hPa',
                     'Wind (1 minute) speed in km/h','Standard deviation of wind (1 minute)',
                     'Vector Average Wind Direction (in degrees)','Vector Average of Wind Speed and Direction',
                     'Vector Average of Wind Speed','Maximum wind gust (over 1 minute) in km/h',
                     'Height of cloud (ceilometer - instantaneous sample 1) in meters',
                     'Height of cloud (ceilometer - instantaneous sample 2) in meters',
                     'Height of cloud (ceilometer - instantaneous sample 3) in meters',
                     'Height of cloud (ceilometer - instantaneous sample 4) in meters',
                     'Height of cloud (ceilometer - instantaneous sample 5) in meters',
                     'Cloud amount for layer 1 (30 minute ceilometer mean) in eighths',
                     'Cloud height for layer 1 (30 minute ceilometer mean) in meters',
                     'Cloud amount for layer 2 (30 minute ceilometer mean) in eighths',
                     'Cloud height for layer 2 (30 minute ceilometer mean) in meters',
                     'Cloud amount for layer 3 (30 minute ceilometer mean) in eighths',
                     'Cloud height for layer 3 (30 minute ceilometer mean) in meters',
                     '* Total amount of cloud in eighths',
                     'Mean sea level pressure in hPa',
                     'Station level pressure in hPa',
                     'QNH pressure in hPa', 'Timestamp']


nsw_epa_met_columns = {'date_time':0,'Wind Dir (deg)':1,'Wind Speed (m/s)':2,'Temp (deg C)':3,'RH (%)':4,
                       'Solar Rad (W/m2)':5,'Sigma Theta (deg)':6,'Rainfall (mm)':7}

list_of_nsw_epa_sites = ['cook_and_phillip','randwick','rozelle','lindfield','chullora',
         'earlwood','macquarie_park',
         'parramatta_north','richmond','st_marys','vineyard','prospect',
         'rouse_hill',
         'bargo','bringelly','camden','campbelltown_west','liverpool',
         'macarthur','oakdale',
         'wollongong','kembla_grange','albion_park_sth',
         'wallsend','newcastle','beresfield',
         'carrington','mayfield','stockton',
         'wyong',
         'bathurst','orange',
         'coffs_harbour','port_macquarie',
         'armidale',
         'gunnedah','narrabri','tamworth',
         'goulburn',
         'albury','wagga_wagga','wagga_wagga_nth',
         'bradfield_highway',
         'muswellbrook','singleton','maison_dieu','bulga','camberwell',
         'mount_thorley','singleton_nw','muswellbrook_nw','wybong',
         'aberdeen','singleton_south','jerrys_plains','warkworth',
         'merriwa','liverpool_swaqs','katoomba','port_kembla_steelworks']


header_row_dict = {'nsw_epa':1}


def convert_to_bom_style(file, station, data_dict, wind_units):
    bom_style_df = pd.DataFrame(columns=BoM_style_df_cols)
    # if station in list_of_nsw_epa_sites:  # this will need to be included if a different type of data is necessary
    header_rows = header_row_dict.get('nsw_epa')
    data_set = data_dict
    if wind_units == 'm/s':
        ws_conversion = 3.6
    else:
        ws_conversion = 1
    met_input_df = pd.read_csv(file, skiprows=header_rows-1)
    bom_style_df['Vector Average Wind Direction (in degrees)'] = met_input_df.iloc[:,data_set.get('WD')].to_list()
    bom_style_df['Wind (1 minute) speed in km/h'] = met_input_df.iloc[:,data_set.get('WS')].to_list()
    bom_style_df['Wind (1 minute) speed in km/h'] = \
        bom_style_df['Wind (1 minute) speed in km/h'].apply(lambda x: x*ws_conversion)
    try:
        bom_style_df['Air Temperature in degrees Celsius'] = met_input_df.iloc[:,data_set.get('Temp')].to_list()
    except:
        print(f"No temperature data in {station} file")
    try:
        bom_style_df['Relative humidity in percentage %'] = met_input_df.iloc[:,data_set.get('RH')].to_list()
    except:
        print(f"No RH data in {station} file")
    try:
        bom_style_df['Precipitation since last (AWS) observation in mm'] = met_input_df.iloc[:,data_set.get('Rainfall')].to_list()
    except:
        print(f"No rain data in {station} file")
    try:
        bom_style_df['Station level pressure in hPa'] = met_input_df.iloc[:,data_set.get('Pressure')].to_list()
    except:
        print(f"No pressure data in {station} file")
    try:
        bom_style_df['* Total amount of cloud in eighths'] = met_input_df.iloc[:, data_set.get('Cloud')].to_list()
    except:
        print(f"No cloud data in {station} file")
    bom_style_df['Timestamp'] = pd.to_datetime(met_input_df.iloc[:,data_set.get('Date_time')], dayfirst=True)
    return bom_style_df


def create_ids_dict(ids_list):
    station_dict = {}
    non_bom_count = 1
    for id in ids_list:
        if id in [" "]: #all_bom_files:
            station_dict[id] = id
        else:
            station_dict[id] = str(non_bom_count) * 4
            non_bom_count += 1
    return station_dict


# @Gooey(menu=[{'name': 'Help', 'items':[{'type':'MessageDialog', 'menuTitle': 'Help Message', 'caption': 'Help',
#                            'message': 'This tool will generate SMERGE input csv files for each selected met station,'
#                            ' generate a smerge.bat file, and auto-run the SMERGE executable. It will attempt to '
#                            'auto-fill data based on parameters provided. The auto-fill algorithm will '
#                            'replace missing hours with a block of preceeding hours up to the maximum '
#                            'number of hours selected in "max_consecutive_values". If a block of hours longer '
#                            'than the selected value is encountered it will not be replaced. Care should be '
#                            'taken when auto-filling and the generated SMERGE csv files should be checked '
#                            'before use to ensure the data is representative. \n\n'
#                            'See modelling drive for list of BoM stations available\n'
#                            '\\auntl1fp001/Groups/!ENV/Team_AQ/Modelling/+Support_Data/+BOM Data\n\n'
#                            'See modelling drive for OEH stations available\n'
#                            '\\auntl1fp001/Groups/!ENV/Team_AQ/Modelling/+Support_Data/+OEH Data\n'
#                            'Note that OEH met data is currently only available from 2010 and '
#                            'some sites may not have data available until more recently. '
#                            'The tool currently only checks that if OEH dta is used the dates '
#                            'are 2010 or later, '
#                            'it does not check if the selected year and station has data or not.'
#                            'An empty data year will be written to a SMERGE file as "9999" missing\n\n'
#                            'Currently only a single custom csv file can be input. \n'
#                            'An option for multiple custom files may be developed at a later stage.\n\n'
#                            'Auto-fill and custom csv settings are optional. These can be '
#                            'left blank if no auto-fill or custom csv is required.'}]}],
#        optional_cols=4, program_name="SMERGE Automation", default_size=(750,1080),
#        hide_progress_msg=False, progress_regex=r"(\d+)%")
# def parse_args():
#     # create GUI with input widgets
#     prog_descrip = "Generate a SMERGE input file and CSV's from BoM and other met files and run SMERGE"
#     parser = GooeyParser(description=prog_descrip)
#
#     required_group = parser.add_argument_group("Required Arguments")
#
#     required_group.add_argument('folder_path', help='Specify output folder', type=str, widget="DirChooser")
#     required_group.add_argument('start_date', help='Enter start date e.g. "1/1/2019"', type=str)
#     required_group.add_argument('end_date', help='Enter end date e.g. "31/12/2019"', type=str)
#     required_group.add_argument('timezone', help='Enter timezone e.g. "+1000"', type=str, default="+1000")
#
#     met_group = parser.add_argument_group("Input Stations")
#     met_group.add_argument('--station_ids', help='Enter station IDs (BoM or OEH) separated by a comma - e.g. "12345, 34567, '
#                                     'Rozelle, Macquarie_Park" (multi-name OEH stations must be joined with '
#                                     'an underscore. Leave blank if no BoM or OEH stations used)', type=str)
#     met_group.add_argument('--optional_csv_met', help='Select a non-BoM/OEH file for custom input', widget='FileChooser')
#
#     missing_group = parser.add_argument_group("Auto-Fill", "Select data auto filling options")
#     # parser.add_argument('--fill_missing_data', default=False, action="store_true",
#     # help='Tick to replace missing temp, press, and RH data with period-average values.')
#     missing_group.add_argument('--auto_fill_wind', default=False, action="store_true")
#     missing_group.add_argument('--auto_fill_temp', default=False, action="store_true")
#     missing_group.add_argument('--auto_fill_rh', default=False, action="store_true")
#     missing_group.add_argument('--auto_fill_pressure', default=False, action="store_true")
#     missing_group.add_argument('--max_consecutive_values',
#                                help='Maximum number of consecutive missing values to auto-fill', type=int)
#     missing_group.add_argument('--stations_to_auto_fill', help='list stations to auto-fill separated by a comma '
#                     ' - leave blank to select all (auto-fill will only run if at least one parameter above is ticked',
#                                type=str)
#
#     opt_csv_group = parser.add_argument_group("Custom CSV Settings")
#     opt_csv_group.add_argument('--station_name', help="Station name for optional csv file", type=str)
#     opt_csv_group.add_argument('--date_col', help="Date-time column - e.g. A - leave blank if N/A", type=str)
#     opt_csv_group.add_argument('--ws_col', help="Wind speed (m/s) column - e.g. B - leave blank if N/A", type=str)
#     opt_csv_group.add_argument('--wd_col', help="Wind dir column - e.g. C - leave blank if N/A", type=str)
#     opt_csv_group.add_argument('--temp_col', help="Temperature (deg C) column - e.g. D - leave blank if N/A", type=str)
#     opt_csv_group.add_argument('--pressure_col', help="Pressure column - e.g. E - leave blank if N/A", type=str)
#     opt_csv_group.add_argument('--rh_col', help="RH column- e.g. F - leave blank if N/A", type=str)
#     opt_csv_group.add_argument('--rain_col', help="Rainfall column - e.g. G - leave blank if N/A", type=str)
#
#     args = parser.parse_args()
#     return args


def smerge(
        stations: str,
        output: str,
        timezone: str,
        **kwargs):


    # Get dates to parse
    start_date = kwargs.get("start", None)
    if start_date == None:
        start_date = "2010-01-01"
    end_date = kwargs.get("end", None)
    if end_date == None:
        end_date = date.today()

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) + datetime.timedelta(hours=23)

    # get data
    from Functions.read_data import get_met_data_for_smerge
    get_met_data_for_smerge(stations, start_date, end_date)


    # dir = conf.folder_path
    # os.chdir(dir)
    # if conf.station_ids:
    #     stations = conf.station_ids
    #     stations = stations.replace(" ","")
    # else:
    #     stations = ''
    # s_date = conf.start_date
    # e_date = conf.end_date
    # tz = conf.timezone
    # if conf.max_consecutive_values:
    #     max_consec_val = conf.max_consecutive_values
    # else:
    #     max_consec_val = 0
    # bom_network_loc = r'\\auntl1fp001/Groups/!ENV/Team_AQ/Modelling/+Support_Data/+BOM Data/'
    # oeh_network_loc = r'\\auntl1fp001/Groups/!ENV/Team_AQ/Modelling/+Support_Data/+NSW OEH Data/'
    # all_bom_files = glob.glob(bom_network_loc + '\*.csv')
    # all_bom_files = [x[len(bom_network_loc):-10] for x in all_bom_files]
    #
    # # get list of BoM and OEH files to find
    # files = []
    # if stations == '':
    #     files = []
    #     station_ids = []
    # else:
    #     station_ids = stations.split(",")
    #     station_ids = [x.lower() for x in station_ids]
    #     for station in station_ids:
    #         if station in list_of_nsw_epa_sites:
    #             files.append(oeh_network_loc + station + "_met.csv")
    #         else:
    #             files.append(bom_network_loc + station + "_60min.csv")
    #
    # #Check optional station name does not clash with OEH station name
    # if conf.station_name in list_of_nsw_epa_sites:
    #     print("\n*****ERROR***** Optional csv station name clashes with OEH station name\n")
    #     raise ValueError
    #
    # #Check if entered IDs are valid:
    # bom_files_entered = False
    # oeh_files_entered = False
    # for station in station_ids:
    #     if station in all_bom_files:
    #         bom_files_entered = True
    #     elif station in list_of_nsw_epa_sites:
    #         oeh_files_entered = True
    #
    # files_not_found = False
    # if files != []:
    #     for file in files:
    #         if os.path.isfile(file) == False:
    #             print(f"\n*****ERROR***** The file {file} could not be found - check BoM or OEH station is valid\n")
    #             files_not_found = True
    #     if files_not_found == True:
    #         raise FileNotFoundError
    #
    # # check network connection is ok
    # if bom_files_entered == True:
    #     if os.path.isdir(bom_network_loc) == False:
    #         print("\n*****ERROR***** The Newcastle modelling drive BoM folder is not available - check network connection\n")
    #         raise FileNotFoundError
    # elif oeh_files_entered == True:
    #     if os.path.isdir(oeh_network_loc) == False:
    #         print("\n*****ERROR***** The Newcastle modelling drive OEH folder is not available - check network connection\n")
    #         raise FileNotFoundError
    #
    # # check timezone
    # if tz[0] != '+':
    #     print("\n*****ERROR***** Check timezone format is valid - e.g. '+1000'")
    #     raise ValueError
    #
    # # Check dates
    # try:
    #     start_date = pd.to_datetime(s_date, format='%d/%m/%Y')
    #     start_date_for_df = pd.to_datetime(s_date, format='%d/%m/%Y') - datetime.timedelta(hours=1)
    #     end_date = pd.to_datetime(e_date, format='%d/%m/%Y') + datetime.timedelta(hours=23)
    #     end_date_for_df = pd.to_datetime(e_date, format='%d/%m/%Y') + datetime.timedelta(hours=24)
    # except:
    #     print("\n*****ERROR***** Check dates are in the correct format\n")
    #     raise SyntaxError
    # if end_date < start_date:
    #     print("\n*****ERROR***** End date is before start date - check date inputs\n")
    #     raise ValueError
    # if oeh_files_entered == True and start_date < pd.to_datetime("1/1/2010", dayfirst=True):
    #     print("\n*****ERROR***** Start date is before 2010 - currently no OEH met data is available before 2010\n")
    #     raise ValueError
    #
    # column_alpha = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    # columns_numeric = np.arange(0, 25)
    # col_alph_num_dict = dict(zip(column_alpha, columns_numeric))
    #
    # # parse optional csv input data
    #
    # if conf.optional_csv_met:
    #     files.append(conf.optional_csv_met)
    #     station_ids.append(conf.station_name)
    #     optional_csv_loc_in_list = len(files)
    #     optional_col_list = {'Date_time':col_alph_num_dict.get(conf.date_col.upper()),
    #                          'WS':col_alph_num_dict.get(conf.ws_col.upper()),
    #                          'WD':col_alph_num_dict.get(conf.wd_col.upper())}
    #     if conf.temp_col:
    #         optional_col_list['Temp'] = col_alph_num_dict.get(conf.temp_col.upper())
    #     if conf.pressure_col:
    #         optional_col_list['Pressure'] = col_alph_num_dict.get(conf.pressure_col.upper())
    #     if conf.rh_col:
    #         optional_col_list['RH'] = col_alph_num_dict.get(conf.rh_col.upper())
    #     if conf.rain_col:
    #         optional_col_list['Rainfall'] = col_alph_num_dict.get(conf.rain_col.upper())
    #     if None in optional_col_list.values():
    #         print("\n*****ERROR***** One or more entered optional column IDs not valid - must be alphabetic - only supported up to column Z")
    #         raise ValueError
    #
    # # Build list of columns selected for auto-filling
    # cols_to_fill_missing = []
    # if conf.auto_fill_wind:
    #     cols_to_fill_missing.append(8)
    #     cols_to_fill_missing.append(9)
    # if conf.auto_fill_temp:
    #     cols_to_fill_missing.append(4)
    # if conf.auto_fill_rh:
    #     cols_to_fill_missing.append(7)
    # if conf.auto_fill_pressure:
    #     cols_to_fill_missing.append(6)
    #
    # # Parse stations to auto-fill and check list
    # if conf.stations_to_auto_fill:
    #     a_f_stations = conf.stations_to_auto_fill
    #     a_f_stations = a_f_stations.replace(" ", "")
    #     a_f_stations_list = a_f_stations.split(',')
    # else:
    #     a_f_stations_list = station_ids
    # for station in a_f_stations_list:
    #     if station not in station_ids:
    #         print("*****ERROR***** Station in auto-fill list not in input stations")
    #         raise ValueError
    #
    #
    # columns = list('ABCDEFGHIJKL')
    # header_1 = ["GENERIC","Version","'2.0'","Manually generated","Time as ending hour","","","","","","",""]
    # header_2 = ["Station","ID","='","CHANGE_THIS","Temp","Precip","Pressure","RH","Wdir10m","Wspeed10m","Ccover","Cheight"]
    # header_3 = ["Month","Day","Year","Hour","DegC","mm","mb","%","deg","ms-1","tenths","hundreds_of_feet"]
    # x = 0
    # smerge_csvs = []
    # fill_missing = False
    # # cols_to_fill_missing = [4,6,7,8,9]
    # # if conf.fill_missing_data:
    # #     fill_missing = True
    # #     cols_to_fill_missing = [8,9]
    #
    # print("\nProcessing data...\n")
    # for file in gooey_tqdm(files):
    #     ids_dict = create_ids_dict(station_ids)
    #     header_2[3] = ids_dict.get(station_ids[x])
    #     header_lines = [header_1, header_2, header_3]
    #     if station_ids[x] in list_of_nsw_epa_sites:
    #         print(f"\nGetting OEH data for {station_ids[x]}:")
    #         oeh_met_columns = {'Date_time':0,'WD':1,'Temp':3,'WS':2,'RH':4,'Rainfall':7}
    #         met_df = convert_to_bom_style(file, station_ids[x], oeh_met_columns, wind_units='m/s')
    #     elif station_ids[x] in all_bom_files:
    #         print(f"\nGetting BoM data for station # {station_ids[x]}:")
    #         met_df = import_csv(file, 3)
    #     else:
    #         print(f"\nGetting optional csv data for {station_ids[x]}:")
    #         met_df = convert_to_bom_style(file, station_ids[x], optional_col_list, wind_units='m/s')
    #         if start_date < met_df.iloc[0,29] or end_date > met_df.iloc[-1,29]:
    #             print("\n*****ERROR***** Optional csv dates do not cover entered data period\n")
    #             raise ValueError
    #
    #     sliced_df = slice_data_by_dates(met_df, start_date_for_df, end_date_for_df)
    #     smerge_df = format_sliced_df(sliced_df, header_lines, fill_blanks=fill_missing)
    #
    #     if station_ids[x] in a_f_stations_list:
    #         smerge_df = replace_missing_data(smerge_df, max_consec_val, cols_to_fill_missing, station_ids[x])
    #     else:
    #         print(f"\n********** Auto-fill not selected for {station_ids[x]} **********")
    #
    #     csv_name = "SMERGE_" + station_ids[x] + ".csv"
    #     smerge_csvs.append(csv_name)
    #     smerge_df.to_csv(csv_name, header=False, index=False)
    #     x+=1
    #     print(f"\nCreated {csv_name} \n")
    #
    # smerge_station_ids = [ids_dict.get(x) for x in station_ids]
    # smerge_stations_txt = smerge_stations_text(smerge_csvs, smerge_station_ids, tz)
    # new_smerge_text = make_smerge_text(smerge_as_string, len(smerge_csvs), smerge_stations_txt, start_date,
    #                                    end_date, tz)
    # output_file = 'SMERGE.inp'
    # write_file(output_file, new_smerge_text)
    #
    # # write batch file, import smerge.exe and run
    # batch_text = "SMERGE.EXE SMERGE.INP"
    # batch_name = "SMERGE.bat"
    # write_file(batch_name, batch_text)
    # bat = dir + "/" + "SMERGE.bat"
    # print("\nCreated SMERGE.inp and SMERGE.bat\n")
    # smerge_exe = r'\\auntl1fp001/Groups/!ENV/Team_AQ/Modelling/+Support_Data/+Models & Software/Lakes/CALPUFF View/smerge.exe'
    # copy_smerge = dir + "/" + "smerge.exe"
    # copyfile(smerge_exe, copy_smerge)
    # import subprocess
    # print("Running SMERGE executable...\n")
    # subprocess.call("SMERGE.bat")
