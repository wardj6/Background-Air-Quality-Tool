import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date
import datetime as dt
import matplotlib.dates as mdates
from PIL import Image
from Functions.read_data import get_pollutant_dataframes
from Functions.__pollutant_and_met_parameters__ import match_pollutant_to_column, all_pollutants_for_stats_charts, all_met_params_missing_data, bom_met_param_dict


def concat_images(image_list) -> Image:
    cols_dict = {1: 1, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 3, 10: 5, 11: 4, 12: 4}
    rows_dict = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 3, 10: 2, 11: 3, 12: 3}
    n_cols = cols_dict.get(len(image_list))
    n_rows = rows_dict.get(len(image_list))
    total_width = n_cols * image_list[0].width
    total_height = n_rows * image_list[0].height
    dst = Image.new('RGB', (total_width, total_height), color='white')
    y = 0
    image_num = 0
    for row_num in range(0, n_rows):
        x = 0
        for col_num in range(0, n_cols):
            try:
                dst.paste(image_list[image_num], (x, y))
            except IndexError:
                print("")
            x += image_list[0].width
            image_num += 1
        y += image_list[0].height
    return dst


def heat_map(
        stations: str,
        output: str,
        **kwargs):

    # Get dates to parse
    start_date = kwargs.get("start", None)
    if start_date == None:
        start_date = "2010-01-01"
    end_date = kwargs.get("end", None)
    if end_date == None:
        end_date = date.today()

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) + dt.timedelta(hours=23)

    # get list of years to plot
    years = list(range(start.year, end.year+1))

    kwarg_dict = match_pollutant_to_column
    pollutants = []
    if kwargs.get("all_poll", False):
        pollutants = all_pollutants_for_stats_charts
        pollutants.extend(all_met_params_missing_data)
    else:
        for kwarg, pollutant in kwarg_dict.items():
            poll = kwargs.get(kwarg, False)
            if kwarg == "all_poll":
                pass
            elif poll:
                pollutants.append(pollutant)

    met_params = kwargs.get('met_params', None)
    if met_params:
        pollutants.extend(all_met_params_missing_data)

    # get data
    cust_loc = kwargs.get("custom_file_location", None)
    if cust_loc is None:
        data_dict, station_file_info = get_pollutant_dataframes(stations, pollutants, start, end)
    else:
        data_dict, station_file_info = get_pollutant_dataframes(stations, pollutants, start, end, custom_network_dir=cust_loc)

    # get list of stations from GUI inputs
    station_list = station_file_info['Station Name'].tolist()

    # rework data into station by station dataframes and generate heatmap
    for station in station_list:
        station_df = pd.DataFrame()
        station_title = station_file_info[station_file_info['Station Name'] == station].loc[:,'Chart Name'].values[0]

        for pollutant, data in data_dict.items():
            station_df[pollutant] = data[station]

        pollutant_cols = station_df.columns
        files_to_concatenate = []
        for poll_col in pollutant_cols:
            from Functions.__pollutant_and_met_parameters__ import missing_data_heat_map_display_pollutants
            pollutant_title = missing_data_heat_map_display_pollutants.get(poll_col)
            df = station_df[poll_col]
            if df.isnull().sum() == df.shape[0]:
                print(f"********** RUN INFO ********** No {poll_col} available for {station} - no missing data chart generated")
            else:
                x = 0
                y = 1
                fig = plt.figure(figsize=(8, 5))
                for year in years:
                    ax = fig.add_subplot(len(years), 1, x + y)
                    year_df = df.loc[df.index.year == year]
                    chart_df = year_df.notnull().astype(int)
                    ax.fill_between(chart_df.index, 0, chart_df)
                    ax.set_ylim(0,1)
                    ax.set_xlim(chart_df.index[0], chart_df.index[-1])
                    ax.tick_params(labelsize=12)
                    ax.axes.yaxis.set_ticks([])
                    if x < len(years) - 1:
                        ax.axes.xaxis.set_ticks([])
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                    x += 1
                    ax.set_ylabel(str(year) + "       ", rotation=0, fontsize=10)
                fig.suptitle(station_title + " " + pollutant_title)
                y += 1
                # plt.show()
                output_file = output + "\\" + "_" + station + "_" + "_".join(poll_col.split(" ")[:-1]) + ".png"
                files_to_concatenate.append(output_file)
                plt.savefig(output_file, bbox_inches="tight", pad_inches=0.1)

        # Find all generated png files and stitch together
        os.chdir(output)
        concat_image = output + "\\_" + station + "_missing_data.png"
        x = 1
        images = []
        if len(files_to_concatenate) != 0:
            for image in files_to_concatenate:
                images.append(Image.open(image))
            concat_images(images).save(concat_image)
            print(f"\n********** OUTPUT ********** Missing data heat map/s generated for {station} and added to {output}\n")
        else:
            print(f"********** RUN INFO ********** No data available for {station} for any of the selected pollutants - missing data figures not generated")





