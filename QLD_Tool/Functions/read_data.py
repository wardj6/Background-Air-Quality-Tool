import pandas as pd
import os
import math
import numpy as np
from datetime import date
from pathlib import Path
from Functions.__pollutant_and_met_parameters__ import des_data_network_dir, bom_data_network_dir, \
    oeh_data_network_dir, epav_data_network_dir, bom_met_param_dict


def get_stations_and_files(dir: str) -> pd.DataFrame:
    sites_file = dir + "\\__station_list_complete.csv"
    return pd.read_csv(sites_file)


def get_stations(stations: str) -> list:
    station_list = stations.split(',')
    station_list = [x.lower().strip() for x in station_list]
    return station_list


def get_state(station_info_df: pd.DataFrame,
              custom_state: str) -> str:
    # from the stations entered, find the state for criteria
    station_dir = Path(station_info_df.loc[:, 'File Name'].values[0]).parent
    if station_dir == Path(des_data_network_dir):
        print(f"********** RUN INFO ********** QLD criteria used for calculations/ charting")
        return 'qld'
    elif station_dir == Path(oeh_data_network_dir):
        print(f"********** RUN INFO ********** NSW criteria used for calculations/ charting")
        return 'nsw'
    elif station_dir == Path(epav_data_network_dir):
        print(f"********** RUN INFO ********** VIC criteria used for calculations/ charting")
        return 'vic'
    else:
        print(f"********** RUN INFO ********** {custom_state.upper()} criteria used for calculations/ charting")
        return custom_state


def get_station_info(dirs: list,
                     stations: list) -> pd.DataFrame:

    station_file_chart_details = pd.DataFrame()
    mixed_state_flag = 0
    stations_found = []
    all_possible_stations = []

    for dir in dirs:
        station_in_dir_list = []
        station_info_df = pd.DataFrame()
        try:
            station_info_df = get_stations_and_files(dir)
            station_info_df['Station Name'] = station_info_df['Station Name'].astype(str)
            station_info_df['File Name'] = dir + "\\" + station_info_df['File Name']
            all_possible_stations.append(station_info_df['Station Name'].tolist())

            for station in stations:
                if station in station_info_df['Station Name'].tolist():
                    station_in_dir_list.append(station)
                    stations_found.append(station)
            if len(station_in_dir_list) != 0:
                mixed_state_flag += 1
            if mixed_state_flag == 2:
                print(f"\n********** ERROR ********** The selected stations are in multiple states - please select stations in a single state\n")
                raise ValueError
            station_file_chart_details = pd.concat([station_file_chart_details,
                                                    station_info_df.loc[station_info_df['Station Name'].isin(station_in_dir_list)]])
        except FileNotFoundError:
            # do nothing, keep look in next dir
            print("")

    # check for invalid stations and throw an error if found
    for station in stations:
        if station not in stations_found:
            # return a warning that it has not been found and give a list of valid stations
            print(f"\n********** ERROR ********** {station} has not been found - please select from the following stations:"
                  f"\n\n {all_possible_stations}\n\n")
            raise ValueError

    return station_file_chart_details


def get_data(r_df: pd.DataFrame,
             start: date,
             end: date,
             my_pollutants: list,
             missing_pollutants: list) -> pd.DataFrame:

    output_df = pd.DataFrame()
    output_df = r_df[my_pollutants]
    output_df.index = pd.to_datetime(output_df.index)
    output_df = output_df.loc[start:end]
    for pol in missing_pollutants:
        output_df[pol] = np.nan
    output_df = output_df.apply(pd.to_numeric, errors='coerce')
    return output_df


def get_pollutant_dataframes(stations: str,
                             plts_to_parse: list,
                             start_date: date,
                             end_date: date,
                             **kwargs) -> (dict, pd.DataFrame):

    # Get location of files - either modelling drives or custom location
    network_files_dirs = []
    custom_dir = kwargs.get("custom_network_dir", None)
    if custom_dir is None:
        network_files_dirs.append(oeh_data_network_dir)
        network_files_dirs.append(des_data_network_dir)
        network_files_dirs.append(epav_data_network_dir)
        network_files_dirs.append(bom_data_network_dir)
    else:
        network_files_dirs.append(custom_dir)

    # get list of stations from GUI inputs
    station_list = get_stations(stations)

    # Get station and file details
    station_file_info = get_station_info(network_files_dirs, station_list)

    # get list of files to grab data from for each station
    file_list = []
    for station in station_list:
        file_list.append(station_file_info[station_file_info['Station Name'] == station]['File Name'].values[0])

    for file in file_list:
        if os.path.isfile(file) == False:
            print(f'********** ERROR ********** {file} not reachable - check network connection or presence of file in folder')
            raise ConnectionError

    # read in data for each file and create a dictionary of dataframes - consisting of 1 dataframe per station
    data_collection = {}
    for file, station in zip(file_list, station_list):
        try:
            # Get data from OES, DES or EPAV style csv
            raw_df = pd.read_csv(file, index_col='Date')
        except ValueError:
            # Get data from BoM style csv
            raw_df = pd.read_csv(file, index_col='Timestamp')
        raw_df.index = pd.to_datetime(raw_df.index.tolist(), dayfirst=True)

        # Convert BoM columns to standard OEH/ EPAV and DES naming scheme
        raw_df.rename(columns=bom_met_param_dict, inplace=True)
        from Functions.__pollutant_and_met_parameters__ import all_possible_col_names

        # Find missing pollutant columns in the raw data
        present_pollutants = plts_to_parse.copy()
        missing_pollutants = []
        for pollutant in plts_to_parse:
            if pollutant not in raw_df.columns.tolist():
                print(f"********** RUN INFO ********** No {pollutant} data is available for {station}")
                missing_pollutants.append(pollutant)
                present_pollutants.remove(pollutant)

        parsed_df = pd.DataFrame(None)
        parsed_df = get_data(raw_df, start_date, end_date, present_pollutants, missing_pollutants)

        # Deal with data before the start of the dataframe
        # Warn the user that data is not available for that station for the full period and append null values
        nox_data = "Data"
        missing_txt = " - missing data replaced with null values"
        if plts_to_parse == ['NO (ug/m^3)', 'NO2 (ug/m^3)']:
            nox_data = "NOx Data"
            missing_txt = ""
        if parsed_df.shape[0] != 0:
            if parsed_df.index[0] > start_date:
                print(f"********** RUN INFO ********** {nox_data} is not available for {station} prior to {parsed_df.index[0].year}"
                      f"{missing_txt}")
                append_dates_df = pd.DataFrame(columns=parsed_df.columns)
                diff = pd.to_timedelta(parsed_df.index[0] - start_date) / pd.Timedelta('1 hour')
                append_dates_df['temp'] = [1] * math.floor(diff)
                append_dates_df.index = pd.date_range(start_date, periods=diff, freq='H')
                append_dates_df.drop('temp', axis=1, inplace=True)
                parsed_df = pd.concat([append_dates_df, parsed_df])

            # Deal with missing data after the end of the dataframe
            # Warn the user that data is not available for that station for the full period and append null values
            if parsed_df.index[-1] < end_date:
                print(f"********** RUN INFO ********** {nox_data} is not available for {station} after {parsed_df.index[-1].year}"
                      f"{missing_txt}")
                append_dates_after_df = pd.DataFrame(columns=parsed_df.columns)
                diff = pd.to_timedelta(end_date - parsed_df.index[-1]) / pd.Timedelta('1 hour')
                append_dates_after_df['temp'] = [1] * math.floor(diff)
                append_dates_after_df.index = pd.date_range(parsed_df.index[-1] + pd.to_timedelta('1 hour'), periods=diff, freq='H')
                append_dates_after_df.drop('temp', axis=1, inplace=True)
                parsed_df = pd.concat([parsed_df, append_dates_after_df])

        data_collection[station] = parsed_df

    # get data into pollutant-specific dataframes and return
    data_by_pollutants = {}

    for pollutant in plts_to_parse:
        new_df = pd.DataFrame(None)
        for key, value in data_collection.items():
            new_df[key] = value[pollutant]
        data_by_pollutants[pollutant] = new_df
    return data_by_pollutants, station_file_info


def data_dict_empty(data_dict: dict) -> bool:
    null_data_count = 0
    for poll, data in data_dict.items():
        if data.empty:
            null_data_count += 1
    if null_data_count == len(data_dict):
        return True
    else:
        return False


def get_met_data_for_smerge(stations: str,
                            start_date: date,
                            end_date: date,
                            **kwargs) -> (dict, pd.DataFrame):

    # Get location of files - either modelling drives or custom location
    network_files_dirs = []
    custom_dir = kwargs.get("custom_network_dir", None)
    if custom_dir is None:
        network_files_dirs.append(oeh_data_network_dir)
        network_files_dirs.append(des_data_network_dir)
        network_files_dirs.append(epav_data_network_dir)
    else:
        network_files_dirs.append(custom_dir)

    # get list of stations from GUI inputs
    station_list = get_stations(stations)

    # Get station and file details
    station_file_info = get_station_info(network_files_dirs, station_list)

    # get list of files to grab data from for each station
    file_list = []
    for station in station_list:
        file_list.append(station_file_info[station_file_info['Station Name'] == station]['File Name'].values[0])

    for file in file_list:
        if os.path.isfile(file) == False:
            print(f'********** ERROR ********** {file} not reachable - check network connection or presence of file in folder')
            raise ConnectionError

    # get all station data and load to dictionary of dataframes
    met_data_dict = {}
    for file, station in zip(file_list, station_list):
        df = pd.read_csv(file)
        from Functions.__pollutant_and_met_parameters__ import smerge_met_cols_dict
        df.rename(columns=smerge_met_cols_dict, inplace=True)
        met_params = list(smerge_met_cols_dict.values())
        met_df = pd.DataFrame()
        for param in met_params:
            try:
                met_df[param] = df[param]
            except KeyError:
                met_df[param] = np.nan
        met_data_dict[station] = met_df
    print(met_data_dict)
