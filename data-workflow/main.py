from typing import List

import logging
import os

from googleapiclient import discovery
from googleapiclient.errors import HttpError
import pandas as pd

logger = logging.getLogger()

def get_raw_data(sheet_id: str, sheet_name: str = "__RAW") -> pd.DataFrame:
    """Get raw data from the spreadsheet and load to pandas for processing.
    Manually specify the column names based on knowledge of the backblast format."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    column_names = ["date", "q", "ao", "n_pax", "pax", "pax_id", "n_fngs", "fng_id", "pax_no_slack", "n_visiting_pax", "submitter", "submitter_id", "id", "store_date"]
    df = pd.read_csv(url, names=column_names, parse_dates=["date", "store_date"])
    return df

def get_reference_ao_data(sheet_id, sheet_name: str = "__REFERENCE_AO_INFO") -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    column_names = ["ao", "ao_normalized_name", "ao_type", "ao_region", "ao_day_of_week_int", "ao_lat", "ao_lon"]
    df = pd.read_csv(url, names=column_names, header=0)
    df["ao_day_of_week_int"] = df["ao_day_of_week_int"].astype(float)
    return df

def infer_ao_info(df: pd.DataFrame, reference_ao_df: pd.DataFrame) -> pd.DataFrame:
    """Add AO Info, and break ties when there is incorrect date information in a record.

    If any downstream processing uses the normalized AO name, then the reference ao data must be
    upated to ensure that all channel names are included in the list of normalied ao names.
    """
    new = df.copy()
    new["ao"] = new["ao"].fillna("1stf")
    new = new.merge(reference_ao_df, on="ao", how="left")
    new["ao_normalized_name"] = new["ao_normalized_name"].fillna(new["ao"])
    new["raw_ao"] = new["ao"]
    new["ao"] = new["ao_normalized_name"]
    return new

def add_day_of_week(df: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """Add a convenience column with the day of the week."""

    # In Looker Studio's WEEKDAY function, the value of Sunday is 0, therefore the value of Saturday is 6.
    new = df.copy()
    # In pandas dayofweek function, the value of Sunday is 6, and the value of Monday is 0
    # We want to match the Looker Studio behavior, so we add 1 to the pandas dayofweek function
    new["day_of_week_int"] = new[f"{date_column}"].dt.dayofweek
    new["day_of_week_int"] = (new["day_of_week_int"] + 1) % 7

    date_diff = new["day_of_week_int"] - new["ao_day_of_week_int"]  # 0 if the day of week is correct
    date_diff = date_diff.fillna(0)

    # Correct the date in favor of the ao_day_of_week
    new["date_raw"] = new[f"{date_column}"]
    new[f"{date_column}"] = new[f"{date_column}"] - pd.to_timedelta(date_diff, unit="d")

    new["day_of_week"] = new[f"{date_column}"].dt.day_name()
    return new

def update_pax_names(df: pd.DataFrame) -> pd.DataFrame:
    """Slack ID is persistent, but names can change. Update the names in the dataframe
    based on the last-used name of the PAX in the dataset."""
    # use most recent name for each pax
    pax = df[["pax", "pax_id"]].drop_duplicates(subset=["pax_id"], keep="last")
    updated = df.merge(pax, on="pax_id", how="left", suffixes=("_then_name", ""))
    return updated

def get_last_message_for_ao_q_day(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate backblast messages by date, q, and ao. If multiple
    messages were submitted for a single date/q/ao, keep the last one."""
    deduped = df[["date", "q", "ao", "id"]].drop_duplicates(subset=["date", "q", "ao"], keep="last")
    new = df.merge(deduped["id"], on=["id"], how="right")
    return new

def filter_by_ao_type(df: pd.DataFrame, ao_type: str = "1stf") -> pd.DataFrame:
    """Filter the dataframe to only include AOs of the specified type."""
    new = df.loc[df["ao_type"] == ao_type]
    return new

def get_df_as_list(df: pd.DataFrame, do_ao_rollup: bool = False) -> List[List[str]]:
    """Convert to a list of values to submit back to google sheets."""
    new = df.fillna("_")
    # reorder and drop columns (drop the old name, 'pax_then_name')
    new = new.drop(columns=["pax_then_name"])
    new = new[["date", "q", "ao", "n_pax", "pax", "day_of_week", "day_of_week_int", "pax_id", "n_fngs", "fng_id", "pax_no_slack", "n_visiting_pax", "ao_lat", "ao_lon", "submitter", "submitter_id", "id", "store_date"]]
    new["date"] = new["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
    new["store_date"] = new["store_date"].apply(lambda x: x.strftime("%Y-%m-%dT%H:%M:%S.%f"))
    if do_ao_rollup:
        # rollup by AO
        ao_level = new.drop(columns=["pax", "pax_id", "fng_id"])
        ao_level = ao_level.drop_duplicates(subset=["date", "q", "ao"], keep="last")
        values = ao_level.values.tolist()
        values = [
            ["Date", "Q", "AO", "PAX (count)", "Day of Week", "Day of Week - Int", "FNGs (count)", "PAX Not in Slack", "Visitng PAX (count)", "ao_lat", "ao_lon", "Submitter", "Submitter ID", "Backblast ID", "Backblast Timestamp"],
            *values
        ]
    else:
        values = new.values.tolist()
        values = [
            ["Date", "Q", "AO", "PAX (count)", "PAX Name", "Day of Week", "Day of Week - Int", "PAX Slack ID", "FNGs (count)", "FNG ID", "PAX Not in Slack", "Visitng PAX (count)", "ao_lat", "ao_lon", "Submitter", "Submitter ID", "Backblast ID", "Backblast Timestamp"],
            *values
        ]
    return values

def save_processed_values(sheet_id: str, sheet_suffix: str, values: List[List[str]]) -> None:
    """Save the processed values back to google sheets."""
    done = False
    try_count = 0


    spreadsheet_request_body = {
        "values": values
    }
    service = discovery.build('sheets', 'v4', cache_discovery=False)

    while not done and try_count < 3:
        try_count += 1
        try:
            result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"__PROCESSED_{sheet_suffix}",
                body=spreadsheet_request_body,
                valueInputOption="RAW"
            ).execute()
            logger.info(f"{result.get('updatedCells')} cells updated.")
            done = True
        except (ConnectionError, HttpError) as e:
            logger.error(f"Error: {e}")
            service = discovery.build('sheets', 'v4', cache_discovery=False)


def do_pipeline(sheet_id: str):
    # add day of week
    # update pax names to use the most recent one in all records
    # Remove duplicate records -- last one wins for each AO
    # Only show records that are from "1stf" AOs
    df = get_raw_data(sheet_id=sheet_id)
    reference_ao_df = get_reference_ao_data(sheet_id=sheet_id)
    df = infer_ao_info(df, reference_ao_df)
    df = add_day_of_week(df)
    df = update_pax_names(df)
    df = get_last_message_for_ao_q_day(df)
    df = filter_by_ao_type(df, ao_type="1stf")
    pax_level_values = get_df_as_list(df, do_ao_rollup=False)
    ao_level_values = get_df_as_list(df, do_ao_rollup=True)
    save_processed_values(sheet_id=sheet_id, sheet_suffix="PAX", values=pax_level_values)
    save_processed_values(sheet_id=sheet_id, sheet_suffix="AO", values=ao_level_values)


if __name__ == "__main__":
    print("Starting data workflow.")
    sheet_id = os.environ.get("SPREADSHEET_ID", "1c1vvx07AXdnu6NSa4is4a0oyUiu8q3cgOecFbTNWlAY")
    do_pipeline(sheet_id=sheet_id)
    print("Completed data workflow.")