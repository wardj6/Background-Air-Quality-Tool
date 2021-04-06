from gooey import Gooey, GooeyParser

from Functions.__version__ import version
from Functions.__pollutant_and_met_parameters__ import states_included_in_database

@Gooey(
    program_name="Background AQ Toolkit",
    default_size=(1150,550),
    tabbed_groups=True,
    menu=[
        {
            "name": "About",
            "items": [
                {
                    "type": "AboutDialog",
                    "menuTitle": "About",
                    "name": "Background AQ Toolkit",
                    "description": "Miscellaneous tools for pollutant data",
                    "version": version,
                    "developer": "Julian Ward - AECOM 2021",
                },
            ],
        }
    ],
    hide_progress_msg=False,
    progress_regex=r"(\d+)%"
)
def gui_inputs():
    program_description = "Tools for background AQ data"
    parser = GooeyParser(description=program_description)

    subs = parser.add_subparsers(help="commands", dest="command")

    #########################################################

    missing_data = subs.add_parser("missing_data")

    heat_map_grp = missing_data.add_argument_group("Stations/ Period", gooey_options={"show_border": True})
    heat_map_grp.add_argument('stations', metavar="Station/s",type=str)
    heat_map_grp.add_argument('output', metavar='Output Folder', help="A heat map of the data availability will output to this folder",
                              widget="DirChooser")

    # heat_date_grp = missing_data.add_argument_group("Data Period",
    #                                                 gooey_options={"show_border": True})
    heat_map_grp.add_argument("--start_date", metavar="Start Date", widget="DateChooser", default='2010-01-01')
    heat_map_grp.add_argument("--end_date", metavar="End Date", widget="DateChooser", default='2019-12-31')

    pollutant_grp = missing_data.add_argument_group("Pollutants",
                                     gooey_options={"show_border": True, "columns": 11})
    pollutant_grp.add_argument('--NO2', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--SO2', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--PM25', metavar="PM2.5", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--PM10', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--TSP', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--CO', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--benzene', metavar="Benzene", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--toluene', metavar="Toluene", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--xylene', metavar="Xylene", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--formaldehyde', metavar="Form.", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--met_params',metavar='Met Params', widget='CheckBox', action='store_true')
    pollutant_grp.add_argument('--all_pollutants', metavar="Select All", widget="CheckBox", action="store_true")

    missing_options_grp = missing_data.add_argument_group("Options", gooey_options={"show_border": True, "columns": 2})
    missing_options_grp.add_argument("--custom_file_location", metavar="Custom directory", help="Location of database if not on network",
                                   widget="DirChooser")

    #########################################################

    background_stats = subs.add_parser("background_data_stats")

    stations_grp = background_stats.add_argument_group("Stations/ Period", gooey_options={"show_border": True})
    stations_grp.add_argument('stations', metavar="Station/s",
                              help="Type the station/s of interest, separated by a comma - must be in the same state for criteria purposes",
                              type=str)
    stations_grp.add_argument('output', metavar='Output Folder', help="The stats csv will be output to this folder",
                              widget="DirChooser")

    # date_grp = background_stats.add_argument_group("Data Period", gooey_options={"show_border": True})
    stations_grp.add_argument("--start_date", metavar="Start Date", widget="DateChooser", default='2010-01-01')
    stations_grp.add_argument("--end_date", metavar="End Date", widget="DateChooser", default='2019-12-31')

    pollutant_grp = background_stats.add_argument_group("Pollutants", "Select the pollutants to be included in the outputs stats csv - "
                                    "note that unless selected below, all data is averaged according to NEPM data capture requirements",
                                     gooey_options={"show_border": True, "columns": 5})
    pollutant_grp.add_argument('--NO2', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--SO2', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--PM25', metavar="PM2.5", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--PM10', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--TSP', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--CO', widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--benzene', metavar="Benzene", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--toluene', metavar="Toluene", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--xylene', metavar="Xylene", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--formaldehyde', metavar="Formaldehyde", widget="CheckBox", action="store_true")
    pollutant_grp.add_argument('--all_pollutants', metavar="Select All", widget="CheckBox", action="store_true")

    stats_options_grp = background_stats.add_argument_group("Stats Options", gooey_options={"show_border": True, "columns": 3})
    stats_options_grp.add_argument("--NO2_NOx", metavar="NO2 to NOx ratio", help="Generate annual average ratios - SELECT NO2 OPTION ABOVE",
                                   widget="CheckBox", action="store_true")
    stats_options_grp.add_argument("--all_capture_rates", metavar="Capture Rates",
                                   help="Generate a list of all data capture rates",
                                 widget="CheckBox", action="store_true")
    stats_options_grp.add_argument("--no_NEPM_validation", metavar="Ignore NEPM DCR",
                                   help="Days with low data capture rates (<75%) included", widget="CheckBox", action="store_true")
    stats_options_grp.add_argument("--percentiles", metavar="Percentiles to include",
                                   help="List percentiles to be included in output stats e.g. 70, 90", type=str)
    stats_options_grp.add_argument("--custom_file_location", metavar="Custom directory", help="Location of database if not on network",
                                   widget="DirChooser")
    stats_options_grp.add_argument("--custom_state", metavar="Custom State Criteria", choices=states_included_in_database,
                                     help="MANDATORY if using custom directory", widget='Dropdown')

    #########################################################

    background_charts = subs.add_parser("background_data_charts")

    charts_stations_grp = background_charts.add_argument_group("Stations/ Period", gooey_options={"show_border": True, "columns": 2})
    charts_stations_grp.add_argument('stations', metavar="Station/s",
                                     help="Type the station/s of interest, separated by a comma - must be in the same state for criteria purposes",
                                     type=str)
    charts_stations_grp.add_argument('output', metavar='Output Folder', help="Charts will be output to this folder",
                              widget="DirChooser")

    # charts_date_grp = background_charts.add_argument_group("Data Period", gooey_options={"show_border": True})
    charts_stations_grp.add_argument("--start_date", metavar="Start Date", widget="DateChooser", default='2010-01-01')
    charts_stations_grp.add_argument("--end_date", metavar="End Date", widget="DateChooser", default='2019-12-31')

    charts_grp = background_charts.add_argument_group("Short Term Average Line Charts",
                                           gooey_options={"show_border": True, "columns": 11})
    charts_grp.add_argument("--all_no2", metavar="1hr NO2", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--all_so2", metavar="1hr SO2", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--so2_24", metavar="24hr SO2", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--pm10_24", metavar="24hr PM10", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--pm25_24", metavar="24hr PM2.5", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--all_co", metavar="1hr CO", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--co_8", metavar="8hr CO", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--all_benzene", metavar="1hr Benz.", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--all_toluene", metavar="24hr Toluene", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--all_xylene", metavar="24hr Xylene", widget="CheckBox", action="store_true")
    charts_grp.add_argument("--all_formaldehyde", metavar="24hr Form.", widget="CheckBox", action="store_true")

    charts_grp.add_argument("--use_cust_poll", metavar="Process Custom Pollutant",
                            help="Enter a custom criteria value in the 'Chart Options' tab", action="store_true")
    charts_grp.add_argument("--custom_pollutant", metavar="Custom Pollutant", type=str, help='This should match the CSV column name',
                            default="NH3 (ug/m^3)")
    charts_grp.add_argument("--custom_avg_period", metavar='Custom Averaging Period (in hours)', type=int, default=1)
    charts_grp.add_argument("--custom_label", metavar='Y Label', help='Custom label for chart Y-axis', type=str, default="NH3")

    ann_group = background_charts.add_argument_group("Annual Average Bar Charts",
                                           gooey_options={"show_border": True, "columns": 11})
    ann_group.add_argument("--ann_no2", metavar="NO2", widget="CheckBox", action="store_true")
    ann_group.add_argument("--ann_so2", metavar="SO2", widget="CheckBox", action="store_true")
    ann_group.add_argument("--ann_pm10", metavar="PM10", widget="CheckBox", action="store_true")
    ann_group.add_argument("--ann_pm25", metavar="PM2.5", widget="CheckBox", action="store_true")

    chart_options_grp = background_charts.add_argument_group("Chart Options", gooey_options={"show_border": True, "columns": 4})

    chart_options_grp.add_argument("--include_criteria", metavar="Chart criteria line", widget="CheckBox", action="store_true")
    chart_options_grp.add_argument("--custom_criteria", metavar="Custom criteria value", type=float)
    chart_options_grp.add_argument("--include_average", metavar="Chart average line", widget="CheckBox", action="store_true")
    chart_options_grp.add_argument("--no_NEPM_validation", metavar="Ignore NEPM DCR",
                                   help="Days with low data capture rates (<75%) included", widget="CheckBox", action="store_true")
    chart_options_grp.add_argument("--font_size", metavar="Custom chart font size", choices=['Large', 'Medium','Small'], widget="Dropdown")
    chart_options_grp.add_argument("--x_format", metavar="Custom x-axis format",
                                   choices=['Dec', '01-12-2019', '01-12-19', '01-Dec-2019', '01-Dec'], widget="Dropdown",
                                   default='Dec')

    # extra_options_grp = background_charts.add_argument_group("Chart Options", gooey_options={"show_border": True, "columns": 5})
    chart_options_grp.add_argument("--y_limit", metavar="Chart Maximum y-axis value", type=int)
    chart_options_grp.add_argument("--prefix", metavar="File output prefix", type=str)
    chart_options_grp.add_argument("--objective_name", metavar="Term for criteria",
                                   help="Text to replace the word 'objective' in charts", type=str)
    chart_options_grp.add_argument("--custom_file_location", metavar="Custom directory", help="Location of database if not on network",
                                   widget="DirChooser")
    chart_options_grp.add_argument("--custom_state", metavar="Custom state criteria", choices=states_included_in_database,
                                     help="MANDATORY if using custom directory", widget='Dropdown')

    comparison_options_grp = background_charts.add_argument_group("Add Comparison Data", gooey_options={"show_border": True, "columns": 5})
    comparison_options_grp.add_argument("--comp_csv", metavar="Comparison CSV file", help="A set of data with 2 columns - Date and Pollutant Values",
                                        widget="FileChooser")
    comparison_options_grp.add_argument("--comp_label", metavar="Label for chart", type=str)
    comparison_options_grp.add_argument("--chart_type", metavar="Chart type", choices=['bar', 'line'],
                                        widget='Dropdown', default='bar')

    #########################################################
    # SMERGE is not currently implemented here
    # smerge = subs.add_parser('SMERGE')
    #
    # met_group = smerge.add_argument_group(gooey_options={"show_border": True, "columns": 3})
    # met_group.add_argument('stations', metavar='Stations/s', help='Enter station IDs (BoM, OEH, or DES) separated by a comma - e.g. "12345, 34567".'
    #                                                                   ' Leave blank if no BoM or OEH stations used)', type=str)
    # # met_group.add_argument('--optional_csv_met', help='Select a csv for custom input', widget='FileChooser')
    # met_group.add_argument('output', help='Specify output folder', type=str, widget="DirChooser")
    # met_group.add_argument('timezone', help='Enter timezone e.g. "+1000"', type=str, default="+1000")
    #
    # required_group = smerge.add_argument_group("Data Period", gooey_options={"show_border": True})
    # required_group.add_argument('--start_date', widget="DateChooser", default='2018-01-01')
    # required_group.add_argument('--end_date', widget="DateChooser", default='2018-12-31')
    #
    # missing_group = smerge.add_argument_group("Auto-Fill Options", gooey_options={"show_border": True, "columns": 3})
    # # parser.add_argument('--fill_missing_data', default=False, action="store_true",
    # # help='Tick to replace missing temp, press, and RH data with period-average values.')
    # missing_group.add_argument('--auto_fill_wind', default=False, action="store_true")
    # missing_group.add_argument('--auto_fill_temp', default=False, action="store_true")
    # missing_group.add_argument('--auto_fill_rh', default=False, action="store_true")
    # missing_group.add_argument('--auto_fill_pressure', default=False, action="store_true")
    # missing_group.add_argument('--max_consecutive_values',
    #                            help='Maximum number of consecutive missing values to auto-fill', type=int)
    # missing_group.add_argument('--stations_to_auto_fill', help='list stations to auto-fill separated by a comma '
    #                 ' - leave blank to select all (auto-fill will only run if at least one parameter above is ticked',
    #                            type=str)

    # opt_csv_group = parser.add_argument_group("Custom CSV Settings")
    # opt_csv_group.add_argument('--station_name', help="Station name for optional csv file", type=str)
    # opt_csv_group.add_argument('--date_col', help="Date-time column - e.g. A - leave blank if N/A", type=str)
    # opt_csv_group.add_argument('--ws_col', help="Wind speed (m/s) column - e.g. B - leave blank if N/A", type=str)
    # opt_csv_group.add_argument('--wd_col', help="Wind dir column - e.g. C - leave blank if N/A", type=str)
    # opt_csv_group.add_argument('--temp_col', help="Temperature (deg C) column - e.g. D - leave blank if N/A", type=str)
    # opt_csv_group.add_argument('--pressure_col', help="Pressure column - e.g. E - leave blank if N/A", type=str)
    # opt_csv_group.add_argument('--rh_col', help="RH column- e.g. F - leave blank if N/A", type=str)
    # opt_csv_group.add_argument('--rain_col', help="Rainfall column - e.g. G - leave blank if N/A", type=str)

    #########################################################

    args = parser.parse_args()
    return args
