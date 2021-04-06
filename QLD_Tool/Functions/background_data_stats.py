from Functions.read_data import get_pollutant_dataframes, data_dict_empty, get_state
from Functions.__pollutant_and_met_parameters__ import match_pollutant_to_column, nepm_data_threshold
from Functions.__pollutant_and_met_parameters__ import states_included_in_database, qld_criteria, \
    nsw_criteria, vic_ers_criteria
import pandas as pd
import numpy as np
import datetime as dt
from datetime import date
import math


def get_exceedances(df: pd.DataFrame,
                    avg_prd: str,
                    criteria: float,
                    pollutant: str,
                    key: str,
                    no_nepm: bool) -> (pd.DataFrame, pd.DataFrame):

    # resample data according to the provided averaging period
    group_df = df.resample(avg_prd).mean()

    # create a map of values to remove due to low data capture rates
    cols = group_df.columns.tolist()
    data_capture_df = pd.DataFrame()
    for col in cols:
        data_capture_df[col] = df[col].resample(avg_prd).count() / df[col].resample(avg_prd).size()

    # Remove low data capture rates by default - of no nepm is selected in GUI, this will be skipped and low data capture rates retained
    if not no_nepm:
        above_nepm = data_capture_df < nepm_data_threshold
        group_df[above_nepm] = np.nan

    # Get number of exceedances per year
    group_df['year'] = group_df.index.year
    return_df = group_df[group_df > criteria].groupby(['year']).count()
    year_list = return_df.index.tolist()
    year_list = [str(x) + "-" + avg_prd + "-num_exceedances" for x in year_list]
    return_df.index = year_list
    columns_list = return_df.columns
    columns_list = [x + "_" + key for x in columns_list]
    return_df.columns = columns_list

    # Get dates of exceedance
    if pollutant in ["PM10", "PM2.5"]:
        above_criteria = group_df > criteria
        exceedances_df = group_df[above_criteria]
        exceedances_df.dropna(thresh=2, inplace=True)
        exceedances_df.drop('year', axis=1, inplace=True)
        ex_columns_list = exceedances_df.columns
        ex_columns_list = [x + "_24hr_" + key for x in ex_columns_list]
        exceedances_df.columns = ex_columns_list
    else:
        exceedances_df = pd.DataFrame(None)

    return return_df, exceedances_df


def get_stats(pollutant_dict: dict,
              avg_prd: str,
              no_nepm: bool) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):

    # Get stats and data capture rates for dictionary of pollutants and stations

    # Loop through each pollutant and get the averaged data for the specified averaging period
    resampled_df = pd.DataFrame()
    count = 1
    capture_df = pd.DataFrame()
    for pollutant, data in pollutant_dict.items():
        cols = data.columns.tolist()
        # print(pollutant, data)
        group_df = pd.DataFrame()
        data_capture = pd.DataFrame()
        for col in cols:
            group_df[col] = data[col].apply(pd.to_numeric).resample(avg_prd).mean()

            # For each column - remove periods with low data capture rates
            if avg_prd != "H":
                if not no_nepm:
                    if avg_prd == "24H":
                        poll_data_capture = col + "_24Hr_data_capture"
                    elif avg_prd == "8H":
                        poll_data_capture = col + "_8Hr_data_capture"
                    else:
                        poll_data_capture = col + "_annual_data_capture"

                    group_df[poll_data_capture] = data[col].resample(avg_prd).count() / data[col].resample(avg_prd).size()
                    group_df.loc[group_df[poll_data_capture] < nepm_data_threshold, col] = np.nan
                    data_capture[poll_data_capture] = group_df[poll_data_capture]
                    data_capture.index = group_df.index
                    group_df.drop(poll_data_capture, axis=1, inplace=True)

                else:
                    if avg_prd == "24H":
                        poll_data_capture = col + "_24Hr_data_capture"
                    elif avg_prd == "8H":
                        poll_data_capture = col + "_8Hr_data_capture"
                    else:
                        poll_data_capture = col + "_annual_data_capture"

                    data_capture[poll_data_capture] = data[col].resample(avg_prd).count() / data[col].resample(avg_prd).size()

        # Add a column denoting the pollutant and then re-index just as years if annual averages
        if avg_prd == "Y":
            pollutant_col_name = 'Pollutant' + "_annual"
        else:
            pollutant_col_name = 'Pollutant' + "_" + avg_prd
        data_capture[pollutant_col_name] = pollutant
        if avg_prd == "Y":
            data_capture.index = data_capture.index.year.tolist()

        # Convert datetime index to just dates - for cleaner output in Excel
        if avg_prd == "24H":
            def convert_to_date(elem):
                return dt.date(year=elem.year, month=elem.month, day=elem.day)
            data_capture.index = [convert_to_date(x) for x in data_capture.index.tolist()]

        # Save data capture rates specific to this pollutant to capture_df
        capture_df = pd.concat([capture_df, data_capture])

        group_df['year'] = group_df.index.year
        temp_df = group_df.groupby(['year']).max()
        # print(f"The temp df for {pollutant} and {avg_prd} is {temp_df}")

        column_list = []
        for column in data.columns.tolist():
            column_list.append(str(column) + "_" + str(pollutant))
        temp_df.columns = column_list
        if count == 1:
            resampled_df = temp_df
        else:
            resampled_df = resampled_df.join(temp_df)
        count += 1

    capture_df.index.name = "Date"
    removed_data_periods_df = capture_df.copy()

    def low_data_capture(elem):
        if elem >= nepm_data_threshold:
            return np.nan
        elif elem == 0:
            return np.nan
        else:
            return elem

    # Generate a dataframe of all periods that had data capture rates below the nepm threshold
    removed_data_periods_df = removed_data_periods_df.iloc[:,0:-1].applymap(low_data_capture)
    removed_data_periods_df[pollutant_col_name] = capture_df[pollutant_col_name].tolist()
    removed_data_periods_df.dropna(thresh=2, inplace=True)
    if avg_prd == "H":
        removed_data_periods_df.drop(pollutant_col_name, axis=1, inplace=True)

    # Drop all removed data period containing pollutants without 24 hour criteria - these are not important
    from Functions.__pollutant_and_met_parameters__ import pol_with_24hr_criteria
    if avg_prd == "24H":
        removed_data_periods_df = removed_data_periods_df[removed_data_periods_df[pollutant_col_name].isin(pol_with_24hr_criteria)]
        capture_df = capture_df[capture_df[pollutant_col_name].isin(pol_with_24hr_criteria)]

    stats_dict = {'H': 'max-1hr', '24H': 'max-24hr', 'Y': 'annual-avg', '8H': 'max-8hr'}
    year_list = resampled_df.index.tolist()
    stats_list = [str(x) + "-" + stats_dict.get(avg_prd) for x in year_list]
    resampled_df.index = stats_list

    return resampled_df, capture_df, removed_data_periods_df


def get_percentiles(pollutant_dict: dict,
                    avg_prd: str,
                    no_nepm: bool,
                    percentiles: list) -> pd.DataFrame:
    percentile_df = pd.DataFrame()
    for pollutant, data in pollutant_dict.items():
        data_capture_df = pd.DataFrame()
        group_df = data.resample(avg_prd).mean()
        cols = data.columns
        for col in cols:
            data_capture_df[col] = data[col].resample(avg_prd).count() / data[col].resample(avg_prd).size()

        # Remove low data capture rates by default - of no nepm is selected in GUI, this will be skipped and low data capture rates retained
        if not no_nepm:
            above_nepm = data_capture_df < nepm_data_threshold
            group_df[above_nepm] = np.nan

        # get percentiles
        pollutant_df = pd.DataFrame()
        for pcntl in percentiles:
            pcntl_df = group_df.copy()
            pcntl_df['year'] = pcntl_df.index.year
            pcntl_df = pcntl_df.groupby(['year']).quantile(q=pcntl)
            pcntl_df.columns = [x + "_" + pollutant for x in pcntl_df.columns]
            pcntl_df.index = [str(x) for x in pcntl_df.index]
            avg_prd_index = {'H': "1hr", "24H": "24hr", "8H": "8hr"}
            pcntl_df.index = [x + "-" + str(math.floor(pcntl * 100)) + "th-percentile-" + avg_prd_index.get(avg_prd) for x in pcntl_df.index]
            pollutant_df = pd.concat([pollutant_df, pcntl_df])

        percentile_df = pd.concat([percentile_df, pollutant_df], axis=1)
    return percentile_df


def get_no2_nox_ratios(pollutant_dict: dict) -> pd.DataFrame:
    ratio_df = pd.DataFrame()

    no2_df = pollutant_dict.get('NO2 (ug/m^3)')
    no_df = pollutant_dict.get('NO (ug/m^3)')

    nox_station_list = no2_df.columns
    for station in nox_station_list:
        if no2_df[station].isnull().sum() == no2_df.shape[0] or no_df[station].isnull().sum() == no_df.shape[0]:
            print(f"********** RUN INFO ********** NO2 or NO data not available for {station} for the selected period - "
                  f"NO2 to NOx ratios not included for this station")
        else:
            nox_col = station + "_NO2-NOx_ratio"
            ratio_df[nox_col] = no2_df[station] / (no2_df[station] + no_df[station])
    if ratio_df.shape[0] != 0:
        ratio_df['year'] = ratio_df.index.year
        average_ratio_df = ratio_df.groupby('year').mean()
        return average_ratio_df
    else:
        return pd.DataFrame(None)


def background_data_stats(
        stations: str,
        output: str,
        **kwargs):

    # print a warning if dates selected are less than a year
    start_date = kwargs.get("start", None)
    if start_date == None:
        start_date = "2010-01-01"
        print(f"********** RUN INFO ********** No start date has been selected - defaulting to January 1st 2010 (start of database)")
    end_date = kwargs.get("end", None)
    if end_date == None:
        end_date = date.today()
        print(f"********** RUN INFO ********** No end date has been selected - defaulting to today's date")

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) + dt.timedelta(hours=23)
    if start.year < 2010:
        print(f"\n********** ERROR ********** The selected start year {start.year} is prior to data in the database - "
              f"please selected a more recent year - starting from 2010\n")
        raise ValueError
    if end > date.today():
        print(f"\n********** ERROR ********** YOU HAVE SELECTED A FUTURE DATE YOU NUMPTY - TRY AGAIN\n")

        raise ValueError
    if start.month != 1:
        print(f"********** WARNING ********** The selected start date is not January 1st - stats for {start.year} "
              f"will not constitute a valid annual average")
    elif start.day != 1:
        print(f"********** WARNING ********** The selected start date is not January 1st - stats for {start.year} "
              f"will not constitute a valid annual average")
    if end.month != 12:
        print(f"********** WARNING ********** The selected end date is not December 31st - stats for {end.year} "
              f"will not constitute a valid annual average")
    elif end.day != 31:
        print(f"********** WARNING ********** The selected end date is not December 31st - stats for {end.year} "
              f"will not constitute a valid annual average")

    # get pollutant kwargs
    kwarg_dict = match_pollutant_to_column

    # Get a list of all pollutants selected to parse in DES column name form
    from Functions.__pollutant_and_met_parameters__ import num_pollutants_included_in_stats
    number_of_pollutants = num_pollutants_included_in_stats
    pollutant_list = []
    count = 0
    for key, value in kwargs.items():
        if count < number_of_pollutants + 3:  # Must be plus 3 to allow for the kwargs prior to the pollutants
            if key == 'all_poll':
                if value:
                    pollutant_list = list(kwarg_dict.values())[:-1]
            elif value:
                pollutant_list.append(kwarg_dict.get(key))
        count += 1
    pollutant_list = [x for x in pollutant_list if x]

    # get all kwargs
    no2_nox_ratio = kwargs.get("no2_nox_ratio", False)
    all_capture_rates = kwargs.get("all_capture_rates", False)
    no_nepm = kwargs.get("no_nepm", False)
    percentiles = kwargs.get("percentiles", None)

    # Read in the selected data to a dictionary of dataframes
    cust_loc = kwargs.get("custom_file_location", None)
    if cust_loc is None:
        data_dict, station_file_info = get_pollutant_dataframes(stations, pollutant_list, start, end)
    else:
        data_dict, station_file_info = get_pollutant_dataframes(stations, pollutant_list, start, end, custom_network_dir=cust_loc)


    # Check if no data has been grabbed at all - then print a warning and do nothing else. Otherwise proceed with stats generation
    if data_dict_empty(data_dict):
        print(f"********** RUN INFO ********** No data is available for the selected stations/ pollutants "
              f"and period combination - no stats generated")
    else:
        averaging_periods = ['Y', '24H', 'H']
        if "CO (ug/m^3)" in pollutant_list:
            averaging_periods.append("8H")

        # ####################################### Generate stats ########################################
        stats_results_df = pd.DataFrame()
        all_data_capture = pd.DataFrame()
        all_removed_periods = pd.DataFrame()
        for prd in averaging_periods:
            prd_df, data_capture, removed_periods = get_stats(data_dict, prd, no_nepm)
            stats_results_df = stats_results_df.append(prd_df)
            all_data_capture = all_data_capture.append(data_capture)
            all_removed_periods = all_removed_periods.append(removed_periods)

        # ####################################### Generate exceedances ########################################
        exceedances_df = pd.DataFrame()
        exceedance_dates_df = pd.DataFrame()
        count = 1
        exceedances_pollutants = pollutant_list.copy()
        not_included_in_exceedances = ["Benzene (ug/m^3)", "Toluene (ug/m^3)", "Xylenes (total) (ug/m^3)", "Formaldehyde (ug/m^3)",
                                       "CO (ug/m^3)"]
        for poll in pollutant_list:
            if poll in not_included_in_exceedances:
                exceedances_pollutants.remove(poll)

        # get state for data criteria to use
        possible_states = states_included_in_database
        custom_state = kwargs.get("custom_state", None)
        if custom_state is None and cust_loc is not None:
            print(f"\n********** ERROR ********** A custom state criteria must be selected if using a custom directory\n")
            raise ValueError
        state = get_state(station_file_info, custom_state)

        # Get relevant criteria
        criteria = {}
        if state == 'qld':
            criteria = qld_criteria
        if state == 'nsw':
            criteria = nsw_criteria
        if state == 'vic':
            criteria = vic_ers_criteria

        for poll in exceedances_pollutants:
            if "PM10" in poll:
                ex_df, ex_dates = get_exceedances(data_dict.get(poll), '24H', criteria.get(poll + "_24H"), "PM10", poll, no_nepm)
            elif "PM2.5" in poll:
                ex_df, ex_dates = get_exceedances(data_dict.get(poll), '24H', criteria.get(poll + "_24H"), "PM2.5", poll, no_nepm)
            elif "NO2" in poll:
                ex_df, ex_dates = get_exceedances(data_dict.get(poll), '1H', criteria.get(poll + "_1H"), "NO2", poll, no_nepm)
            elif "SO2" in poll:
                one_hr_df, ex_dates = get_exceedances(data_dict.get(poll), '1H', criteria.get(poll + "_1H"), "SO2", poll, no_nepm)
                day_df, ex_dates = get_exceedances(data_dict.get(poll), '24H', criteria.get(poll + "_24H"), "SO2", poll, no_nepm)
                ex_df = pd.concat([one_hr_df, day_df])
            # These pollutants not included in exceedances at the moment - there is little chance of exccedances anyway
            # elif "CO" in poll:
            #     ex_df = get_exceedances(data_dict.get(poll), '8H', 11000, "CO", poll)
            # elif "Toluene" in poll:
            #     ex_df = get_exceedances(data_dict.get(poll), '24H', 4100, "Toluene", poll)
            # elif "Xylene" in poll:
            #     ex_df = get_exceedances(data_dict.get(poll), '24H', 1200, "Xylene", poll)
            # elif "Form" in poll:
            #     ex_df = get_exceedances(data_dict.get(poll), '24H', 54, "Formaldehyde", poll)
            if count == 1:
                exceedances_df = ex_df
                exceedance_dates_df = ex_dates
            else:
                exceedances_df = pd.concat([exceedances_df, ex_df], axis=1, sort=False)
                exceedance_dates_df = pd.concat([exceedance_dates_df, ex_dates], axis=1, sort=False)
            count += 1

        # ####################################### Generate percentiles ########################################
        if percentiles == None:
            print("********** RUN INFO ********** No percentiles entered - percentiles not calculated")
        else:
            percentiles_list = [int(x.strip())/100 for x in percentiles.split(',')]
            percentile_avg_prds = ['H', '24H']
            if "CO (ug/m^3)" in pollutant_list:
                percentile_avg_prds.append("8H")
            for prd in percentile_avg_prds:
                percentile_df = get_percentiles(data_dict, prd, no_nepm, percentiles_list)
                stats_results_df = pd.concat([stats_results_df, percentile_df])

        # ####################################### Get NO2 to NOx ratios ########################################
        no2_nox_ratio_df = pd.DataFrame()
        if no2_nox_ratio:
            print(f"\nGetting NO and NO2 data for ratio calculations:\n")
            nox_polls = ['NO (ug/m^3)', 'NO2 (ug/m^3)']
            if cust_loc is None:
                nox_data, nox_station_file_info = get_pollutant_dataframes(stations, nox_polls, start, end)
            else:
                nox_data, nox_station_file_info = get_pollutant_dataframes(stations, nox_polls, start, end, custom_network_dir=cust_loc)
            no2_nox_ratio_df = get_no2_nox_ratios(nox_data)

        # ####################################### Output to Excel ########################################
        import openpyxl
        output = output + "\\" + "_" + stations + "_stats.xlsx"
        with pd.ExcelWriter(output, date_format='DD-MM-YYYY') as writer:
            stats_results_df.to_excel(writer, sheet_name="Stats")
            if all_capture_rates:
                all_data_capture.to_excel(writer, sheet_name="Data capture rates")
            if not no_nepm:
                all_removed_periods.to_excel(writer, sheet_name="Periods removed")
            exceedances_df.to_excel(writer, sheet_name="Num Exceedances")
            if exceedance_dates_df.shape[0] != 0:
                exceedance_dates_df.to_excel(writer, sheet_name="24H PM Exceedance Dates")
            if no2_nox_ratio_df.shape[0] != 0:
                no2_nox_ratio_df.to_excel(writer, sheet_name="Annual NO2-NOx Ratio")
        print(f"\n********** OUTPUT ********** Stats output to ----- {output}\n")







