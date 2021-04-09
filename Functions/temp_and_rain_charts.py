import pandas as pd
import datetime as dt
from datetime import date
from Functions.read_data import get_pollutant_dataframes
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def get_axis_range(axis_min, axis_max):
    """
    A function to adjust the limits for y axis, depending on the range of data
    :param axis_min: min axis range
    :param axis_max: max axis range
    :return:
    """
    if axis_max - axis_min >= 30:
        min_graph = axis_min // 5 * 5
    else:
        min_graph = axis_min // 5 * 5 - 5
    max_graph = min_graph + 40
    axis_range = [min_graph, max_graph]
    return axis_range


def resample_data(df):

    """
    Resample the data into monthly average min/max temperatures and rainfall
    :param df: The data to be resampled
    :return: A resampled dataframe containing 12 rows, one for each month
    """

    df1 = df.copy()
    # first, convert all NaN values to np.nan
    df1 = df1.fillna(np.nan)

    daily_df = pd.DataFrame()
    daily_df['maxtemp'] = df1['Temp (deg C)'].resample('d').apply(np.max)
    daily_df['mintemp'] = df1['Temp (deg C)'].resample('d').apply(np.min)
    daily_df['rainfall'] = df1['Rainfall (mm)'].resample('d').agg(pd.Series.sum, min_count=18)

    # series.resample('2T').apply(lambda x: np.sum(x.values))
    daily_df['month'] = pd.DatetimeIndex(daily_df.index).month
    monthly_rain = pd.DataFrame()
    monthly_rain['rainfall'] = daily_df['rainfall'].resample('m').agg(pd.Series.sum, min_count=22)
    monthly_rain['month'] = pd.DatetimeIndex(monthly_rain.index).month

    # Build the chart ready df
    chart_df = daily_df.groupby('month').mean()
    chart_df['rainfall'] = monthly_rain.groupby('month').apply(np.mean)

    # Remove any columns that are empty
    columns = chart_df.columns
    for column in columns:
        if chart_df[column].isnull().sum() == len(chart_df):
            chart_df.drop(columns=[column], inplace=True)

    return chart_df


def temp_rain_chart(station: str,
                    df: pd.DataFrame,
                    custom_temp_axis_range: list,
                    custom_rain_axis_range: list):

    """
    Generates the chart
    :param custom_rain_axis_range: A 2-element list containing the min and max values for the rainfall axis - empty list if no custom axis entered
    :param custom_temp_axis_range: A 2-element list containing the min and max values for the temperature axis - empty list if no custom axis entered
    :param station: Station name as string
    :param df: Pandas dataframe containing three columns - one each for temp, rainfall and RH
    :return: Nothing
    """

    # create temp and rainfall chart
    print(f"\nCreating temperature and rain graph for {station}")

    # Resample the data for the chart
    chart_df = resample_data(df)

    # get the years of data
    temp_df = df['Temp (deg C)'].dropna()
    temp_period = str(pd.DatetimeIndex(temp_df.index).year.min()) + "-" + str(pd.DatetimeIndex(temp_df.index).year.max())
    rain_df = df['Rainfall (mm)'].dropna()
    rain_period = str(pd.DatetimeIndex(rain_df.index).year.min()) + "-" + str(pd.DatetimeIndex(rain_df.index).year.max())

    if 'maxtemp' in chart_df.columns and 'mintemp' in chart_df.columns:
        # create and set up the matplotlib figure and embedded axis object
        tempfig, ax1 = plt.subplots(figsize=(9, 5))
        ax1.plot(chart_df.index, chart_df.maxtemp, color='tab:red')
        ax1.plot(chart_df.mintemp, color='tab:green')
        ax1.set(xlabel="Month", ylabel="Temperature (deg C)")
        # get temp axis range
        temp_min = chart_df.mintemp.min()
        temp_max = chart_df.maxtemp.max()
        temp_axis_range = get_axis_range(temp_min, temp_max)
        # additional chart formatting
        if custom_temp_axis_range == []:
            ax1.set(ylim=(temp_axis_range[0], temp_axis_range[1]))
        else:
            ax1.set(ylim=(int(custom_temp_axis_range[0]), int(custom_temp_axis_range[1])))
        legendmaxtmp = "Max temp" + " (" + temp_period + ")"
        ax1.legend([legendmaxtmp, 'Min temp'], loc='upper right')

        if 'rainfall' in chart_df.columns:
            # add rainfall data to the chart if available
            ax1.set(title="Average Monthly Temperature and Rainfall")
            ax2 = ax1.twinx()
            ax2.set_ylabel("Rainfall (mm)")
            ax2.bar(chart_df.index, chart_df.rainfall, width=0.5, color='tab:blue')
            if custom_rain_axis_range == []:
                ax2.set(ylim=(0, 400))
            else:
                ax2.set(ylim=(int(custom_rain_axis_range[0]), int(custom_rain_axis_range[1])))
            # ax2.xaxis.set_major_locator(months)
            # ax2.xaxis.set_major_formatter(monthsfmt)
            legendrain = "Rainfall" + " (" + rain_period + ")"
            ax2.legend([legendrain], loc='upper left')
        else:
            print(f"Rainfall data missing from {station}, no rainfall displayed on graph")
            ax1.set(title="Average Monthly Temperature")
        ax1.grid(linewidth=0.5, axis='y')

        import datetime
        ticklabels = [datetime.date(1900, item, 1).strftime('%b') for item in chart_df.index]
        ax1.set_xticks(np.arange(1, 13))
        ax1.set_xticklabels(ticklabels)

        fig_save_title = station + "_temp_rain.png"
        tempfig.savefig(fig_save_title)

    else:
        print(f"Temp data missing from {station}, no graph produced")


def concat_df(data_dict: dict):

    """
    Reorganises the data into station specific temp, rain and RH dataframes and returns them via a dictionary
    :param data_dict: Dictionary - key = met param, value = a dataframe with a column for each station
    :return: dict
    """

    stations = list(data_dict.get('Rainfall (mm)').columns)

    out_dict = {}

    for station in stations:
        concat_df = pd.DataFrame()
        columns = []
        for i, (key, data) in enumerate(data_dict.items()):
            columns.append(key)
            if i == 0:
                concat_df = data[station]
            else:
                concat_df = pd.concat([concat_df,data[station]], axis=1)
        concat_df.columns = columns

        out_dict[station] = concat_df

    return out_dict


def temp_and_rain_charts(
        stations: str,
        output_dir: str,
        **kwargs):

    """
    Main function in this module to generate temp and rainfall charts
    :param stations: Stations as input via the GUI
    :param output_file:
    :param kwargs: optional start and end dates
    :return: Nothing
    """

    import os
    os.chdir(output_dir)

    # Get dates to parse
    start_date = kwargs.get("start", None)
    if start_date == None:
        start_date = "2010-01-01"
    end_date = kwargs.get("end", None)
    if end_date == None:
        end_date = date.today()

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) + dt.timedelta(hours=23)

    # Set parameters to get
    met_params = ['Temp (deg C)', 'RH (%)', 'Rainfall (mm)']

    # get data
    cust_loc = kwargs.get("custom_file_location", None)
    if cust_loc is None:
        data_dict, station_file_info = get_pollutant_dataframes(stations, met_params, start, end)
    else:
        data_dict, station_file_info = get_pollutant_dataframes(stations, met_params, start, end, custom_network_dir=cust_loc)

    # get list of stations from GUI inputs
    station_list = station_file_info['Station Name'].tolist()

    # Reform dataframes
    temp_rain_dict = concat_df(data_dict)

    def get_range(str):
        if str is None:
            return []
        else:
            return str.split("-")

    # Get axis ranges
    temp_axis_range = get_range(kwargs.get("optional_temp_axis", None))
    rain_axis_range = get_range(kwargs.get("optional_rain_axis", None))


    for station, data in temp_rain_dict.items():
        temp_rain_chart(station, data, temp_axis_range, rain_axis_range)



