import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import numpy as np


import mpl_styles
plt.style.use('AECOM-standard')
# axes.prop_cycle: cycler('color', ['008768', 'aecc53', '00353e', 'e52713', '009a9b', 'ffce00', 'c70c6f'])


def get_year_colours(annual_avg_soi_list):
    cols = []
    for i in annual_avg_soi_list:
        if i >=0:
            cols.append('#008768')
        else:
            cols.append('#aecc53')
    return cols


def soi_plot(soi_df, year_start, year_end):
    avg_soi_df = soi_df.resample('Y').mean()
    avg_soi_df.index = np.arange(year_start, year_end + 1)
    years = str(year_start) + "-" + str(year_end)

    soi_interpolated = soi_df.copy()
    soi_interpolated = soi_interpolated.resample('1H').sum()
    soi_interpolated.loc[soi_interpolated['SOI'] == 0] = np.nan
    soi_interpolated['SOI'] = soi_interpolated['SOI'].interpolate(method='polynomial', order=2)
    soi_above_zero = soi_interpolated.loc[soi_interpolated['SOI'] >= 0]
    soi_below_zero = soi_interpolated.loc[soi_interpolated['SOI'] < 0]

    fig, axs = plt.subplots(2,1, figsize=(10,6))
    axs[0].scatter(soi_above_zero.index, soi_above_zero['SOI'], s=0.3)
    axs[0].scatter(soi_below_zero.index, soi_below_zero['SOI'], s=0.3)

    # axs[0].plot(soi_df.index, soi_df['SOI'])
    y_max = math.ceil(soi_interpolated['SOI'].max()) + 1
    y_min = math.floor(soi_interpolated['SOI'].min()) - 1
    axs[0].set_ylim([y_min, y_max])

    axs[0].set_title("Monthly Average SOI")
    axs[0].set_ylabel("SOI Index")
    axs[0].set_xlabel("Year")
    axs[0].axhline(0, c='#008768', alpha=0.3, zorder=0)

    colours = get_year_colours(list(avg_soi_df['SOI']))
    axs[1].bar(avg_soi_df.index, avg_soi_df['SOI'], color=colours, zorder=3)

    y_max = math.ceil(avg_soi_df['SOI'].max()) + 1
    y_min = math.floor(avg_soi_df['SOI'].min()) - 1
    axs[1].set_ylim([y_min, y_max])

    axs[1].set_title("Yearly Average SOI")
    axs[1].set_ylabel("SOI Index")
    axs[1].set_xlabel("Year")
    axs[1].axhline(0, c='#008768', alpha=0.3, zorder=0)
    axs[1].set_xticks(np.arange(year_start, year_end + 1, 1))
    fig.tight_layout(pad=1.0)
    # plt.show()
    fig_title = "SOI_Chart_" + years + ".png"
    fig.savefig(fig_title)


def soi_chart(file, year_start, year_end):
    start_date = datetime(year=year_start, month=1, day=1, hour=0)
    end_date = datetime(year=year_end, month=12, day=31, hour=23)

    monthly_soi_df = pd.read_csv(file, parse_dates=['Date'], dayfirst=True)
    monthly_soi_df.set_index("Date", inplace=True, drop=True)
    monthly_soi_df = monthly_soi_df.loc[start_date:end_date]

    soi_plot(monthly_soi_df, year_start, year_end)