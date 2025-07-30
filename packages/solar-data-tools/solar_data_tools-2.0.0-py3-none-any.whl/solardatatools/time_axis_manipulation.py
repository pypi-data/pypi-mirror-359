# -*- coding: utf-8 -*-
"""Data Transforms Module

This module contains functions for transforming PV power data, including time-axis standardization and
2D-array generation

"""

from datetime import timedelta
import numpy as np
import pandas as pd
from collections import Counter
from typing import Optional

TZ_LOOKUP = {
    "America/Anchorage": 9,
    "America/Chicago": 6,
    "America/Denver": 7,
    "America/Los_Angeles": 8,
    "America/New_York": 5,
    "America/Phoenix": 7,
    "Pacific/Honolulu": 10,
    "Canada/Central": 6,
}


def make_time_series(
    df,
    return_keys=True,
    localize_time=-8,
    timestamp_key="ts",
    value_key="meas_val_f",
    name_key="meas_name",
    groupby_keys=["site", "sensor"],
    filter_length=200,
):
    """
    Accepts a Pandas data frame extracted from a relational or Cassandra database.
    These queries often result in data with repeated timestamps, as you might
    have multiple columns stacked into rows in the database. Defaults are
    intended to work with GISMo's VADER Cassandra database implementation.

    Returns a data frame with a single timestamp
    index and the data from different systems split into columns.

    :param df: A Pandas data from generated from a query the VADER Cassandra database
    :param return_keys: If true, return the mapping from data column names to site and system ID
    :param localize_time: If non-zero, localize the time stamps. Default is PST or UTC-8
    :param filter_length: The number of non-null data values a single system must have to be included in the output
    :return: A time-series data frame
    """
    # Check to see if there is a reasonable amount of data
    if np.sum(df[value_key].values >= 0) < 24:
        raise ValueError(
            "Insufficient data to run pipeline. Please check your data frame."
        )
    # Make sure that the timestamps are monotonically increasing. There may be
    # missing or repeated time stamps
    df.sort_values(timestamp_key, inplace=True)
    time_index = pd.to_datetime(df[timestamp_key].sort_values())
    time_index = time_index[~time_index.duplicated(keep="first")]
    output = pd.DataFrame(index=time_index)
    site_keys = []
    site_keys_a = site_keys.append
    grouped = df.groupby(groupby_keys)
    keys = grouped.groups.keys()
    counter = 1
    for key in keys:
        df_view = df.loc[grouped.groups[key]]
        ############## data cleaning ####################################
        # df_view = df_view[pd.notnull(df_view[value_key])]               # Drop records with nulls
        df_view.set_index(
            timestamp_key, inplace=True
        )  # Make the timestamp column the index
        df_view.index = pd.to_datetime(df_view.index)
        df_view.sort_index(inplace=True)  # Sort on time
        df_view = df_view[
            ~df_view.index.duplicated(keep="first")
        ]  # Drop duplicate times
        df_view = df_view.reindex(
            index=time_index, method=None
        )  # Match the master index, interp missing
        #################################################################
        meas_name = str(df_view[name_key].iloc[0])
        col_name = meas_name + "_{:02}".format(counter)
        output[col_name] = df_view[value_key]
        if (
            output[col_name].count() > filter_length
        ):  # final filter on low data count relative to time index
            site_keys_a((key, col_name))
            counter += 1
        else:
            del output[col_name]
    if localize_time:
        output.index = output.index + pd.Timedelta(hours=localize_time)  # Localize time

    if return_keys:
        return output, site_keys
    else:
        return output


def standardize_time_axis(
    df, timeindex=True, power_col=None, datetimekey=None, correct_tz=True, verbose=True
):
    """
    This function takes in a pandas data frame containing tabular time series
    data, likely generated with a call to pandas.read_csv(). It is assumed that
    each row of the data frame corresponds to a unique date-time, though not
    necessarily on standard intervals. This function will attempt to convert a
    user-specified column containing time stamps to python datetime objects,
    assign this column to the index of the data frame, and then standardize the
    index over time. By standardize, we mean reconstruct the index to be at
    regular intervals, starting at midnight of the first day of the data set.
    This solves a couple common data errors when working with raw data.
    (1) Missing data points from skipped scans in the data acquisition system.
    (2) Time stamps that are at irregular exact times, including fractional
    seconds.

    :param df: A pandas data frame containing the tabular time series data
    :param datetimekey: An optional key corresponding to the name of the column that contains the time stamps
    :return: A new data frame with a standardized time axis
    """
    # convert index to timeseries
    df = df.copy()
    if not timeindex:
        try:
            df[datetimekey] = pd.to_datetime(df[datetimekey])
            df.set_index(datetimekey, inplace=True)
        except KeyError:
            time_cols = [
                col for col in df.columns if np.logical_or("Time" in col, "time" in col)
            ]
            key = time_cols[0]
            df[datetimekey] = pd.to_datetime(df[key])
            df.set_index(datetimekey, inplace=True)
    # make sure it's a datetime index
    df.index = pd.to_datetime(df.index)
    # Check for "large" time zone issues (> 4 hrs off). This is to avoid power
    # generation at midnight, which "wraps around" when forming a matrix
    if power_col is not None:
        thresh = 0.01
        # calculate average day
        s = df[power_col]
        avg_day = s.groupby(s.index.time).mean()
        # normalize to [0, 1]
        avg_day -= np.min(avg_day)
        avg_day /= np.max(avg_day)
        # find sunrise and sunset times
        idxs = np.arange(len(avg_day))
        if avg_day.iloc[0] >= thresh:
            sr_loc = [idxs[0]]
        else:
            sr_loc = idxs[
                np.r_[[False], np.diff((avg_day.values >= thresh).astype(float)) == 1]
            ]
        if avg_day.iloc[-1] >= thresh:
            ss_loc = [idxs[-1]]
        else:
            ss_loc = idxs[
                np.r_[np.diff((avg_day.values >= thresh).astype(float)) == -1, [False]]
            ]
        sunrise = avg_day.index.values[sr_loc]
        sunrise = sunrise[0].hour + sunrise[0].minute / 60  # first index
        sunset = avg_day.index.values[ss_loc]
        sunset = sunset[-1].hour + sunset[-1].minute / 60  # last index
        # calculate solar noon of average day
        if sunrise < sunset:
            sn = np.average([sunrise, sunset])
        else:
            sn = np.average([sunrise, sunset + 24])
            if sn > 24:
                sn -= 24
        avg_solar_noon = sn
        sn_deviation = int(np.round(12 - avg_solar_noon))
    else:
        sn_deviation = 0
    # if estimated average solar noon is more than 4 hours from clock noon,
    # then apply a correction
    if correct_tz and power_col is not None:
        if np.abs(sn_deviation) > 4:
            df.index = df.index.shift(sn_deviation, freq="H")
        else:
            sn_deviation = 0
    else:
        if np.abs(sn_deviation) > 4:
            m1 = "CAUTION: Time zone offset error detected, "
            m1 += "but TZ correction flag turned off!\n"
            m1 += "Recommend checking timezone localization in data or "
            m1 += "turning on TZ correction flag."
            print(m1)
        sn_deviation = 0
    # determine most common sampling frequency
    try:
        diff = (df.index[1:] - df.index[:-1]).seconds
        # print('case 1')
    except AttributeError:
        diff = df.index[1:] - df.index[:-1]
        diff /= np.timedelta64(1, "s")
        # print('case 2')
    diff = (np.round(diff / 10) * 10).astype(
        np.int64
    )  # Round to the nearest 10 seconds
    # Find *all* common sampling frequencies
    freq_counts = Counter(diff)
    freq = freq_counts.most_common()[0][0]
    deltas = [c[0] for c in freq_counts.most_common() if int(c[1] > 0.05 * len(df))]
    if len(deltas) > 1:
        if verbose:
            print("CAUTION: Multiple scan rates detected!")
            print("Scan rates (in seconds):", deltas)
            df["deltas"] = np.r_[diff, [0]]
            daily_scanrate = df["deltas"].groupby(df.index.date).median()
            slct = np.zeros(len(daily_scanrate))
            for d in deltas:
                slct = np.logical_or(daily_scanrate == d, slct)
            leading = daily_scanrate[slct].index[
                np.r_[np.diff(daily_scanrate[slct]) != 0, [False]]
            ]
            trailing = daily_scanrate[slct].index[
                np.r_[[False], np.diff(daily_scanrate[slct]) != 0]
            ]
            if len(leading) == 1:
                print("\n1 transition detected.\n")
            else:
                print("{} transitions detected.".format(len(leading)))
            print("Suggest splitting data set between:")
            for s, t in zip(leading, trailing):
                print("    ", s, "and", t)
            print("\n")
            del df["deltas"]

    start = df.index[0]
    end = df.index[-1]
    # Create the standardized index to cover the data
    time_index = pd.date_range(
        start=start.date(), end=end.date() + timedelta(days=1), freq="{}s".format(freq)
    )[:-1]
    # This forces the existing data into the closest new timestamp to the
    # old timestamp.
    try:
        df = df.loc[df.index.notnull()]
        df = df.loc[~df.index.duplicated()]
        df = df.loc[df.index.notnull()].reindex(
            index=time_index, method="nearest", limit=1
        )
    except TypeError:
        df.index = df.index.tz_localize(None)
        df = df.loc[df.index.notnull()].reindex(
            index=time_index, method="nearest", limit=1
        )
    return df, sn_deviation


def fix_daylight_savings_with_known_tz(df, tz="America/Los_Angeles", inplace=False):
    index = (
        df.index.tz_localize(tz, nonexistent="NaT", ambiguous="NaT")
        .tz_convert("Etc/GMT+{}".format(TZ_LOOKUP[tz]))
        .tz_localize(None)
    )
    if inplace:
        df.index = index
        return
    else:
        df_out = df.copy()
        df_out.index = index
        return df_out


def remove_index_timezone(df):
    """
    Removes the timezone information from the index of a pandas DataFrame, if
    it is timezone aware. This function was written with ChatGPT and checked by
    Bennet Meyers

    Parameters:
    df (pandas.DataFrame): The DataFrame to modify.

    Returns:
    pandas.DataFrame: The modified DataFrame.
    """
    if isinstance(df.index, pd.DatetimeIndex) and df.index.tzinfo is not None:
        new_index = df.index.tz_localize(None)
        return df.set_index(new_index)
    else:
        return df


def get_index_timezone(df: pd.DataFrame) -> Optional[str]:
    """
    Returns the timezone name or offset amount (in hours) of the index of a
    pandas DataFrame. This function was written with ChatGPT and checked by
    Bennet Meyers

    Parameters:
    df (pandas.DataFrame): The DataFrame to check.

    Returns:
    str or None: The timezone name or offset amount (in hours) of the index,
    or None if the index is not timezone aware.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        tzinfo = df.index.tzinfo
        if tzinfo is not None:
            tzname = tzinfo.tzname(None)
            if tzname is not None:
                return tzname
            else:
                tzoffset = tzinfo.utcoffset(None).total_seconds() // 3600
                return f"{tzoffset:+}"
    return None
