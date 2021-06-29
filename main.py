from Functions import gui_scaffold
from Functions.file_utilities import get_files


if __name__ == "__main__":
    # Load GUI
    user_inputs = gui_scaffold.gui_inputs()

    ####################################################################################

    if user_inputs.command == "missing_data":
        from Functions.heat_map import heat_map

        heat_map(
            user_inputs.stations,
            user_inputs.output,
            start=user_inputs.start_date,
            end=user_inputs.end_date,
            no2=user_inputs.NO2,
            so2=user_inputs.SO2,
            pm25=user_inputs.PM25,
            pm10=user_inputs.PM10,
            tsp=user_inputs.TSP,
            co=user_inputs.CO,
            benzene=user_inputs.benzene,
            toluene=user_inputs.toluene,
            xylene=user_inputs.xylene,
            form=user_inputs.formaldehyde,
            met_params=user_inputs.met_params,
            all_poll=user_inputs.all_pollutants,
            custom_file_location=user_inputs.custom_file_location
        )

    ####################################################################################

    if user_inputs.command == "background_data_stats":
        from Functions.background_data_stats import background_data_stats

        background_data_stats(
            user_inputs.stations,
            user_inputs.output,
            start=user_inputs.start_date,
            end=user_inputs.end_date,
            no2=user_inputs.NO2,
            so2=user_inputs.SO2,
            pm25=user_inputs.PM25,
            pm10=user_inputs.PM10,
            tsp=user_inputs.TSP,
            co=user_inputs.CO,
            benzene=user_inputs.benzene,
            toluene=user_inputs.toluene,
            xylene=user_inputs.xylene,
            form=user_inputs.formaldehyde,
            all_poll=user_inputs.all_pollutants,
            no2_nox_ratio=user_inputs.NO2_NOx,
            all_capture_rates=user_inputs.all_capture_rates,
            no_nepm=user_inputs.no_NEPM_validation,
            percentiles=user_inputs.percentiles,
            custom_file_location=user_inputs.custom_file_location,
            custom_state=user_inputs.custom_state
        )

    ####################################################################################

    if user_inputs.command == "background_data_charts":
        from Functions.background_data_charts import background_data_charts

        background_data_charts(
            user_inputs.stations,
            user_inputs.output,
            start=user_inputs.start_date,
            end=user_inputs.end_date,
            # display_stations=user_inputs.display_stations,
            no2=user_inputs.all_no2,
            so2=user_inputs.all_so2,
            so2_24=user_inputs.so2_24,
            pm25_24=user_inputs.pm25_24,
            pm10_24=user_inputs.pm10_24,
            co=user_inputs.all_co,
            co_8=user_inputs.co_8,
            benzene=user_inputs.all_benzene,
            toluene=user_inputs.all_toluene,
            xylene=user_inputs.all_xylene,
            form=user_inputs.all_formaldehyde,
            use_cust_poll=user_inputs.use_cust_poll,
            custom_pollutant=user_inputs.custom_pollutant,
            custom_avg_prd=user_inputs.custom_avg_period,
            custom_poll_label=user_inputs.custom_label,
            ann_no2=user_inputs.ann_no2,
            ann_so2=user_inputs.ann_so2,
            ann_pm10=user_inputs.ann_pm10,
            ann_pm25=user_inputs.ann_pm25,
            show_criteria=user_inputs.include_criteria,
            custom_criteria=user_inputs.custom_criteria,
            show_average=user_inputs.include_average,
            no_nepm=user_inputs.no_NEPM_validation,
            font_size=user_inputs.font_size,
            y_limit=user_inputs.y_limit,
            prefix=user_inputs.prefix,
            criteria_label=user_inputs.objective_name,
            custom_file_location=user_inputs.custom_file_location,
            custom_state=user_inputs.custom_state,
            x_format=user_inputs.x_format,
            comp_file=user_inputs.comp_csv,
            comp_label=user_inputs.comp_label,
            comp_type=user_inputs.chart_type,
            custom_colours=user_inputs.cust_cols
        )

    ####################################################################################

    if user_inputs.command == 'temperature_rainfall_charts':

        from Functions.temp_and_rain_charts import temp_and_rain_charts

        temp_and_rain_charts(
            user_inputs.stations,
            user_inputs.output,
            optional_temp_axis=user_inputs.temp_y_axis,
            optional_rain_axis=user_inputs.rain_y_axis,
            start=user_inputs.start_d,
            end=user_inputs.end_d
        )

    ####################################################################################

    if user_inputs.command == 'SOI_chart':

        from Functions.soi import soi_chart
        import os

        os.chdir(user_inputs.output_location)

        soi_chart(
            user_inputs.soi_file,
            user_inputs.start_year,
            user_inputs.end_year
        )
