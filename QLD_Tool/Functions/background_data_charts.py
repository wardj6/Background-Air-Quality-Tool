import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import date
import datetime as dt
from Functions.read_data import get_pollutant_dataframes, data_dict_empty, get_state
from Functions.__pollutant_and_met_parameters__ import match_pollutant_to_column_charts, all_pollutants_for_stats_charts
from Functions.__pollutant_and_met_parameters__ import qld_criteria, qld_chart_criteria, \
    nsw_criteria, nsw_chart_criteria, vic_ers_criteria, vic_ers_chart_criteria, chart_averaging_periods_dict


def make_chart(df_dict: dict,
               pollutant: str,
               avg_time: str,
               start: date,
               end: date,
               output_figure_name: str,
               show_criteria: bool,
               y_axis_limit: int,
               show_average: bool,
               no_nepm: bool,
               criteria_label: str,
               custom_criteria,
               state: str,
               station_file_info: pd.DataFrame,
               font: int,
               x_frmt: str,
               comp_csv: pd.DataFrame,
               comp_lab: str,
               comp_chart_type: str,
               cust_y_label: str):

    chart_font = 'Arial'

    # Get relevant criteria
    criteria = {}
    if state == 'qld':
        criteria = qld_criteria
        chart_criteria = qld_chart_criteria
    elif state == 'nsw':
        criteria = nsw_criteria
        chart_criteria = nsw_chart_criteria
    elif state == 'vic':
        criteria = vic_ers_criteria
        chart_criteria = vic_ers_chart_criteria

    pollutant_avg_time = pollutant + "_" + avg_time
    pollutant_criteria = criteria.get(pollutant_avg_time)

    # read in data from df dictionary - check and remove final column if "year" (this will be added again later)
    if avg_time == "1H":
        chart_data = df_dict.get(pollutant).copy()
        chart_data = chart_data[start:end]
        if chart_data.columns.tolist()[-1] == "year":
            chart_data.drop(["year"], axis=1, inplace=True)
        linewidth = 0.4
    elif avg_time == '8H':
        chart_data = df_dict.get(pollutant).copy()
        chart_data = chart_data[start:end].rolling(8, min_periods=6).mean()
        if chart_data.columns.tolist()[-1] == "year":
            chart_data.drop(["year"], axis=1, inplace=True)
        linewidth = 0.6
    else:
        chart_data = df_dict.get(pollutant).copy()
        data_capture_df = pd.DataFrame()
        cols = chart_data.columns
        for col in cols:
            data_capture_df[col + '_data_capture'] = chart_data[col].resample(avg_time).count() / chart_data[col].resample(avg_time).size()
        chart_data = chart_data[start:end].resample("24H").mean()

        # # Remove 24 hour means that have less than 75% data capture rate - as per NEPM Data Collection and Handling
        # # Remove low data capture rates by default - of 'no nepm' option is selected in GUI, this will be skipped and low data capture rates retained
        from Functions.__pollutant_and_met_parameters__ import nepm_data_threshold
        if not no_nepm:
            chart_data = pd.concat([chart_data, data_capture_df], axis=1)
            for col in cols:
                chart_data.loc[chart_data[col + "_data_capture"] < nepm_data_threshold, col] = np.nan
                chart_data.drop(columns=col + "_data_capture", inplace=True)

        if chart_data.columns.tolist()[-1] == "year":
            chart_data.drop(["year"], axis=1, inplace=True)
        linewidth = 0.8


    # Check data exists and exit if not
    if chart_data.isnull().sum().sum() == chart_data.shape[0] * chart_data.shape[1]:
        # dataframe is empty, get out of here
        print(f"********** RUN INFO ********** There is no data for {pollutant} in the selected period and stations - no chart generated")
    else:
        # get the highest concentration in all the data
        max_conc = chart_data.max().max()

        # set the y limits based on max conc/ criteria
        if y_axis_limit > 0:
            y_max = y_axis_limit
        else:
            if show_criteria:
                if max_conc < chart_criteria.get(pollutant_criteria):
                    y_max = chart_criteria.get(pollutant_criteria)
                else:
                    if pollutant_criteria > 100:
                        y_max = (max_conc // 100 + 1) * 100
                    else:
                        y_max = (max_conc // 10 + 1) * 10
            else:
                y_max = (max_conc // 10 + 1) * 10

        sites = chart_data.columns.tolist()
        chart_data['year'] = chart_data.index.year.tolist()
        years = chart_data.year.unique()

        # Create y-axis pollutant labels
        from Functions.__pollutant_and_met_parameters__ import chart_display_pollutants
        plt.rcParams.update({'mathtext.default': 'regular'})
        pollutant_lab = chart_display_pollutants.get(pollutant_avg_time)
        if pollutant_lab is None:
            pollutant_lab = cust_y_label + " (" + r"$\mu$" + "g/m" + "$^3$" + ")"

        # monthsfmt = mdates.DateFormatter('%d-%b-%y')
        if x_frmt == 'Dec':
            xfmt = mdates.DateFormatter('%b')
        elif x_frmt == '01-12-2019':
            xfmt = mdates.DateFormatter('%d-%m-%Y')
        elif x_frmt == '01-12-19':
            xfmt = mdates.DateFormatter('%d-%m-%y')
        elif x_frmt == '01-Dec-2019':
            xfmt = mdates.DateFormatter('%d-%b-%Y')
        elif x_frmt == '01-Dec':
            xfmt = mdates.DateFormatter('%d-%b')

        colours = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#d62728']

        if avg_time != 'Y':
            fig = plt.figure(figsize=(10, len(years) * 2 + 1))
            for x in range(len(years)):
                year_data = chart_data.loc[chart_data['year'] == years[x]]
                if custom_criteria is not None:
                    pollutant_criteria = custom_criteria
                criteria_on_chart = [pollutant_criteria] * year_data.shape[0]
                x_min = year_data.index[0]
                x_max = year_data.index[-1]
                ax = fig.add_subplot(len(years), 1, x+1)
                i = 0
                for site in sites:
                    label = station_file_info[station_file_info['Station Name'] == site]['Chart Name'].values[0]
                    ax.plot(mdates.date2num(list(year_data.index)), year_data.iloc[:,i], label=label, c=colours[i], linewidth=linewidth)
                    if show_average:
                        year_average = [year_data.iloc[:,i].mean()] * year_data.shape[0]
                        ax.plot(mdates.date2num(list(year_data.index)), year_average, label=label + "_avg", linewidth=linewidth, c=colours[i], linestyle="dashed")
                    i += 1
                if show_criteria:
                    ax.plot(year_data.index, criteria_on_chart, label=criteria_label, c="red", linewidth=1.2, linestyle="dotted")
                    # ax.axhline(pollutant_criteria, c='red', alpha=0.5, linestyle="dotted")

                # Add comparison data as a bar or line chart
                if comp_csv.shape[0] != 0:
                    comp_csv_sliced = comp_csv.loc[pd.DatetimeIndex(comp_csv["Date"]).year == years[x]]
                    comp_csv_sliced = comp_csv_sliced.sort_values(by="Date", ignore_index=True)
                    bar_ax = ax.twinx()
                    if comp_chart_type == 'bar':
                        bar_ax.bar(comp_csv_sliced.iloc[:,0], comp_csv_sliced.iloc[:,1], width=0.8, facecolor='indianred', label=comp_lab)

                    elif comp_chart_type == 'line':
                        ax.plot(comp_csv_sliced.iloc[:, 0], comp_csv_sliced.iloc[:, 1], c='indianred', linewidth=linewidth,
                                    linestyle='dashed', label=comp_lab)
                    if comp_csv_sliced.shape[0] != 0:
                        leg2 = bar_ax.legend(fontsize=font - ((font - 8) / 2), loc="upper right")

                ax.set_ylim(0,y_max)
                ax.set_xlim(x_min, x_max)
                ax.set_title(years[x], fontname=chart_font)
                if show_average:
                    leg = ax.legend(ncol=chart_data.shape[1]*2+1, fontsize=font - ((font-8) / 2), loc="upper left")
                else:
                    leg = ax.legend(ncol=chart_data.shape[1] + 1, fontsize=font - ((font-8) / 2), loc="upper left")
                    # if comp_csv.shape[0] != 0:
                    #     leg2 = bar_ax.legend(fontsize=font - ((font-8) / 2), loc="upper right")
                ax.set_ylabel(pollutant_lab, fontname=chart_font, fontsize=font)

                ax.xaxis.set_major_formatter(xfmt)
                ax.tick_params(axis='both', labelsize=font)

                for line in leg.get_lines():
                    line.set_linewidth(2)

            fig.tight_layout(pad=1)

            plt.savefig(output_figure_name)
            print(f"********** OUTPUT ********** Generated chart for {pollutant} and saved as {output_figure_name}")
            # plt.show()

        # Annual bar plots
        if avg_time == 'Y':
            poll_df = df_dict.get(pollutant)
            ann_df = poll_df.resample('Y').mean()
            label_cols = []
            for col in ann_df.columns:
                label_cols.append(station_file_info.loc[station_file_info['Station Name'] == col]['Chart Name'].tolist()[0])
            ann_df.columns = label_cols

            # remove years with less than 75% DCR
            if not no_nepm:
                dcr_df = poll_df.resample('Y').count()
                hours_in_year = poll_df.resample('Y').size()
                for i in range(dcr_df.shape[1]):
                    dcr_df.iloc[:,i] = dcr_df.iloc[:,i] / hours_in_year
                less_than_nepm = dcr_df < 0.90
                for i in range(dcr_df.shape[1]):
                    col_bool = dcr_df.iloc[:,i] < 0.75
                    ann_df.iloc[:,i][col_bool] = np.nan

            ax = ann_df.plot.bar(color=colours)
            plt.ylabel(pollutant_lab, fontsize=font + 1, fontname=chart_font)
            plt.title("Annual Average " + pollutant_lab.split(" ")[0], fontsize=font)
            xlabels = ann_df.index.strftime("%Y")
            ax.set_xticklabels(xlabels, rotation=0, fontsize=font)

            # set the y limits based on max conc/ criteria
            ann_y_max = 0
            max_conc = ann_df.max().max()
            if y_axis_limit > 0:
                ann_y_max = y_axis_limit
            else:
                if show_criteria:
                    if max_conc < chart_criteria.get(pollutant_criteria):
                        ann_y_max = chart_criteria.get(pollutant_criteria)
                    else:
                        if pollutant_criteria > 100:
                            ann_y_max = (max_conc // 100 + 1) * 100
                        elif pollutant_criteria > 10:
                            ann_y_max = (max_conc // 10 + 1) * 10
                        else:
                            ann_y_max = (max_conc // 1) + 2
                else:
                    ann_y_max = (max_conc // 10 + 1) * 10

            ax.set_ylim((0, ann_y_max))
            if show_criteria:
                criteria_line = ax.axhline(pollutant_criteria, c='red', alpha=1.5, linestyle="dotted")
                criteria_line.set_label(criteria_label)
            leg_col_dict = {2:2, 3:3, 4:4, 5:3, 6:3, 7:4, 8:4, 9:3, 10:4, 11:4}
            leg_cols = leg_col_dict.get(ann_df.shape[1] + 1)

            leg = ax.legend(fontsize=font - ((font-8) / 2), loc='upper left', ncol=leg_cols)
            for line in leg.get_lines():
                line.set_linewidth(2)
            ax.tick_params(axis='both', labelsize=font)
            plt.savefig(output_figure_name)
            print(f"********** OUTPUT ********** Generated chart for {pollutant} and saved as {output_figure_name}")
            # plt.show()


def background_data_charts(stations: str,
                           output: str,
                           **kwargs):
    # Get dates to parse
    start_date = kwargs.get("start", None)
    if start_date is None:
        start_date = "2010-01-01"
    end_date = kwargs.get("end", None)
    if end_date is None:
        end_date = date.today()

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) + dt.timedelta(hours=23)

    kwarg_dict = match_pollutant_to_column_charts
    pollutants = []
    if kwargs.get("all_poll", False):
        pollutants = all_pollutants_for_stats_charts
    else:
        for kwarg, pollutant in kwarg_dict.items():
            poll = kwargs.get(kwarg, False)
            if kwarg == "all_poll":
                pass
            elif poll:
                pollutants.append(pollutant)

    # Get custom pollutant if selected to process plus get custom label for Y-axis
    use_custom_pollutant = kwargs.get("use_cust_poll", False)
    cust_poll_label = ""
    if use_custom_pollutant:
        "Using Custom Pollutant"
        cust_poll = kwargs.get("custom_pollutant", None)
        if cust_poll is not None:
            pollutants.append(cust_poll)
        cust_poll_label = kwargs.get("custom_poll_label", None)

    # get data
    cust_loc = kwargs.get("custom_file_location", None)
    if cust_loc is None:
        data_dict, station_file_info = get_pollutant_dataframes(stations, list(set(pollutants)), start, end)
    else:
        data_dict, station_file_info = get_pollutant_dataframes(stations, list(set(pollutants)), start, end, custom_network_dir=cust_loc)

    # Raise an error if there are more than 10 stations selected
    if station_file_info.shape[0] > 10:
        print("\n********** ERROR ********** Currently the charts are limited to 10 stations - please select less stations\n")
        raise ValueError

    # Check if no data has been grabbed at all - then print a warning and do nothing else. Otherwise proceed with stats generation
    if data_dict_empty(data_dict):
        print(f"********** WARNING ********** No data is available for the selected stations/ pollutants "
              f"and period combination - no charts generated")
    else:
        # get chart options
        show_criteria = kwargs.get("show_criteria", False)
        y_limit = kwargs.get("y_limit", None)
        if y_limit is None:
            y_limit = 0
        show_average = kwargs.get("show_average", False)
        criteria_label = kwargs.get("criteria_label", None)
        if criteria_label is None:
            criteria_label = "Objective"

        # Get a list of the averaging periods for each chart
        averaging_periods_dict = chart_averaging_periods_dict

        avg_prd_list = []
        for plt, avg in averaging_periods_dict.items():
            included = kwargs.get(plt, False)
            if included:
                avg_prd_list.append(avg)

        # Get custom averaging period and add to list if selected to process
        use_custom_pollutant = kwargs.get("use_cust_poll", False)
        if use_custom_pollutant:
            "Using Custom Pollutant"
            cust_avg_prd = kwargs.get("custom_avg_prd", None)
            cust_avg_prd = str(cust_avg_prd) + 'H'
            averaging_periods_dict[cust_poll] = cust_avg_prd
            avg_prd_list.append(cust_avg_prd)

        # get NEPM flag
        no_nepm = kwargs.get("no_nepm", False)

        # get file output prefix
        file_prefix = kwargs.get("prefix", None)
        if file_prefix is None:
            file_prefix = ""

        # get list of stations from GUI inputs
        station_list = station_file_info['Station Name'].tolist()

        # get state for data criteria to use
        from Functions.__pollutant_and_met_parameters__ import states_included_in_database
        possible_states = states_included_in_database
        custom_state = kwargs.get("custom_state", None)
        if custom_state is None and cust_loc is not None:
            print(f"\n********** ERROR ********** A custom state criteria must be selected if using a custom directory\n")
            raise ValueError
        state = get_state(station_file_info, custom_state)

        # get font size option if selected - default is 10
        font = 10
        if kwargs.get("font_size", None) == 'Large':
            font = 12
        if kwargs.get("font_size", None) == 'Medium':
            font = 10
        if kwargs.get("font_size", None) == 'Small':
            font = 8

        # Get custom criteria if selected
        custom_criteria = kwargs.get("custom_criteria", None)

        # Get x axis format - month name is default
        x_form = kwargs.get("x_format", None)
        if x_form is None:
            x_form = 'Dec'

        # Get optional comparison csv for adding data to chart
        comp_csv = kwargs.get("comp_file", None)
        if comp_csv is not None:
            comp_data = pd.read_csv(comp_csv)
            comp_data.columns = ['Date', 'Pollutant']
            comp_data['Date'] = pd.to_datetime(comp_data['Date'], dayfirst=True)
        else:
            comp_data = pd.DataFrame(None)

        # Get chart label and type
        comp_label = kwargs.get("comp_label", None)
        if comp_label is None:
            comp_label = ""
        comp_type = kwargs.get("comp_type", None)


        # Make the charts for each station and pollutant/ averaging period selected
        stations_combined = "_".join(station_list)
        for plt, avg in zip(pollutants, avg_prd_list):
            chart_name = output + "\\_" + file_prefix + "_" + stations_combined + "_" + plt.split(" ")[0] + "_" + avg + ".png"
            # Drop criteria if CO 1H selected for state QLD (no criteria)
            if plt == 'CO (ug/m^3)' and avg == '1H' and state == 'qld':
                print("********** WARNING ********** No criteria for 1 hour CO in QLD - no criteria displayed on this chart")
                make_chart(data_dict, plt, avg, start, end, chart_name, False,
                           y_limit, show_average, no_nepm, criteria_label, custom_criteria, state,
                           station_file_info, font, x_form, comp_data, comp_label, comp_type, cust_poll_label)
            elif plt == 'Benzene (ug/m^3)' and avg == '1H' and state == 'qld':
                print("********** WARNING ********** No criteria for 1 hour benzene in QLD - no criteria displayed on this chart")
                make_chart(data_dict, plt, avg, start, end, chart_name, False,
                           y_limit, show_average, no_nepm, criteria_label, custom_criteria, state,
                           station_file_info, font, x_form, comp_data, comp_label, comp_type, cust_poll_label)
            else:
                make_chart(data_dict, plt, avg, start, end, chart_name, show_criteria,
                       y_limit, show_average, no_nepm, criteria_label, custom_criteria, state,
                           station_file_info, font, x_form, comp_data, comp_label, comp_type, cust_poll_label)




