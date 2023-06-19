import os
from typing import List, Optional, Union

import logging

from googleapiclient import discovery
from googleapiclient.errors import HttpError
import pandas as pd
from sqlalchemy import create_engine, select, table, column

logger = logging.getLogger()

def get_raw_data_db(include_team_ids: List[Union[str, None]]) -> pd.DataFrame:
    """Get raw data from the database and load to pandas for processing."""
    column_names = ["date", "q", "ao", "ao_id", "n_pax", "pax", "pax_ids", "n_fngs", "fngs", "fng_ids", "pax_no_slack", "n_visiting_pax", "submitter", "submitter_id", "id", "store_date", "q_id", "team_id"]
    column_select = [column(name) for name in column_names]
    query = select(*column_select).select_from(table("backblast"))
    exclude_null = True
    if None in include_team_ids:
        exclude_null = False
    include_team_ids = [team_id for team_id in include_team_ids if team_id is not None]
    if include_team_ids:
        query = query.where(column("team_id").in_(include_team_ids))
    if exclude_null:
        query = query.where(column("team_id").isnot(None))

    engine = create_engine(os.environ['COCKROACH_CONNECTION_STRING'])

    df = pd.read_sql(query, con=engine, parse_dates=["date", "store_date"])

    # Explode the list columns (largely a legacy of the google sheets implementation)
    new = df.explode(['pax', 'pax_ids'])
    new = new.explode(['fngs', 'fng_ids'])
    new.rename(columns={"pax_ids": "pax_id", "fngs": "fng", "fng_ids": "fng_id"}, inplace=True)

    return new

def get_raw_data(sheet_id: str, sheet_name: str = "__RAW") -> pd.DataFrame:
    """Get raw data from the spreadsheet and load to pandas for processing.
    Manually specify the column names based on knowledge of the backblast format."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    column_names = ["date", "q", "ao", "n_pax", "pax", "pax_id", "n_fngs", "fng_id", "pax_no_slack", "n_visiting_pax", "submitter", "submitter_id", "id", "store_date", "q_id", "team_id"]
    df = pd.read_csv(url, names=column_names, parse_dates=["date", "store_date"], dtype={
        "date": str,
        "q": str,
        "ao": str,
        "n_pax": float,
        "pax": str,
        "pax_id": str,
        "n_fngs": float,
        "fng_id": str,
        "pax_no_slack": str,
        "n_visiting_pax": float,
        "submitter": str,
        "submitter_id": str,
        "id": str,
        "store_date": str,
        "q_id": str,
        "team_id": str
    })
    return df

def get_reference_ao_data(sheet_id, sheet_name: str = "__REFERENCE_AO_INFO") -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    column_names = ["ao", "ao_normalized_name", "ao_type", "ao_region", "ao_day_of_week_int", "ao_lat", "ao_lon", "ao_day_of_week"]
    df = pd.read_csv(url, names=column_names, header=0, dtype={
        "ao": pd.StringDtype(),
        "ao_normalized_name": pd.StringDtype(),
        "ao_type": pd.StringDtype(),
        "ao_region": pd.StringDtype(),
        "ao_day_of_week_int": pd.Float64Dtype(),
        "ao_lat": pd.Float64Dtype(),
        "ao_lon": pd.Float64Dtype(),
        "ao_day_of_week": pd.StringDtype()
    })
    return df

def get_reference_ao_data_db(team_name: str) -> pd.DataFrame:
    engine = create_engine(os.environ['COCKROACH_CONNECTION_STRING'])
    df = pd.read_sql_table(f"ao_info_{team_name}", con=engine)
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
    new["day_of_week_int_original"] = new["day_of_week_int"]
    new["ao_day_of_week_int"] = new["ao_day_of_week_int"].fillna(new["day_of_week_int"])
    new["day_of_week_int"] = new["ao_day_of_week_int"]

    return new

def update_pax_names(df: pd.DataFrame) -> pd.DataFrame:
    """Slack ID is persistent, but names can change. Update the names in the dataframe
    based on the last-used name of the PAX in the dataset."""
    # use most recent name for each pax
    pax = df[["pax", "pax_id"]].drop_duplicates(subset=["pax_id"], keep="last")
    updated = df.merge(pax, on="pax_id", how="left", suffixes=("_then_name", ""))
    qs = updated[["q", "q_id"]].drop_duplicates(subset=["q_id"], keep="last")
    qs = qs[qs["q_id"].notnull()]
    updated = updated.merge(qs, on="q_id", how="left", suffixes=("_then_name", ""))
    updated["q"] = updated["q"].fillna(updated["q_then_name"])
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

def get_final_df(df: pd.DataFrame, do_ao_rollup: bool = False) -> pd.DataFrame:
    # reorder and drop columns (drop the old name, 'pax_then_name')
    new = df.drop(columns=["pax_then_name"])
    new = new[["date", "q", "ao", "n_pax", "pax", "day_of_week", "day_of_week_int", "pax_id", "n_fngs", "fng_id", "pax_no_slack", "n_visiting_pax", "ao_lat", "ao_lon", "submitter", "submitter_id", "id", "store_date", "ao_region", "q_id"]]
    if do_ao_rollup:
        # rollup by AO
        ao_level = new.drop(columns=["pax", "pax_id", "fng_id"])
        ao_level = ao_level.drop_duplicates(subset=["date", "q", "ao"], keep="last")
        return ao_level
    return new

def get_df_as_list(df: pd.DataFrame) -> List[List[str]]:
    """Convert to a list of values to submit back to google sheets."""
    new = df.fillna("_")
    # reorder and drop columns (drop the old name, 'pax_then_name')
    new["date"] = new["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
    new["store_date"] = new["store_date"].apply(lambda x: x.strftime("%Y-%m-%dT%H:%M:%S.%f"))
    # TODO: this is brittle both in how it detects columns and the column name/order
    if "pax" not in new.columns:
        values = new.values.tolist()
        values = [
            ["Date", "Q", "AO", "PAX (count)", "Day of Week", "Day of Week - Int", "FNGs (count)", "PAX Not in Slack", "Visitng PAX (count)", "ao_lat", "ao_lon", "Submitter", "Submitter ID", "Backblast ID", "Backblast Timestamp", "Region ID", "Q Slack ID"],
            *values
        ]
    else:
        values = new.values.tolist()
        values = [
            ["Date", "Q", "AO", "PAX (count)", "PAX Name", "Day of Week", "Day of Week - Int", "PAX Slack ID", "FNGs (count)", "FNG ID", "PAX Not in Slack", "Visitng PAX (count)", "ao_lat", "ao_lon", "Submitter", "Submitter ID", "Backblast ID", "Backblast Timestamp", "Region ID", "Q Slack ID"],
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
    pax_level_values = get_final_df(df, do_ao_rollup=False)
    ao_level_values = get_final_df(df, do_ao_rollup=True)
    pax_level_values = get_df_as_list(pax_level_values)
    ao_level_values = get_df_as_list(ao_level_values)
    save_processed_values(sheet_id=sheet_id, sheet_suffix="PAX", values=pax_level_values)
    save_processed_values(sheet_id=sheet_id, sheet_suffix="AO", values=ao_level_values)

def do_pipeline_db(team_name: str, team_ids: List[Union[str, None]]) -> None:
    df = get_raw_data_db(include_team_ids=team_ids)
    reference_ao_df = get_reference_ao_data_db(team_name=team_name)
    df = infer_ao_info(df, reference_ao_df)
    df = add_day_of_week(df)
    df = update_pax_names(df)
    df = get_last_message_for_ao_q_day(df)
    df = filter_by_ao_type(df, ao_type="1stf")
    pax_level_values = get_final_df(df, do_ao_rollup=False)
    ao_level_values = get_final_df(df, do_ao_rollup=True)

    engine = create_engine(os.environ['COCKROACH_CONNECTION_STRING'])

    ao_level_values.to_sql(f"ao_level_values_{team_name}", con=engine, if_exists="replace", index=False)
    pax_level_values.to_sql(f"pax_level_values_{team_name}", con=engine, if_exists="replace", index=False)

if __name__ == "__main__":
    do_sheets_workflow = os.environ.get("DO_SHEETS_WORKFLOW", "false").lower() == "true"
    if do_sheets_workflow:
        print("Starting sheets-based data workflow for Carpex/Peak City/Green Level:")
        do_pipeline(sheet_id="1c1vvx07AXdnu6NSa4is4a0oyUiu8q3cgOecFbTNWlAY")
        print("Completed data workflow.")
    else:
        print("Skipping sheets-based data workflow.")

    # Updating AO info is taking a REALLY long time -- using the sheets API in general is really slow today
    do_update_ao_info = os.environ.get("DO_UPDATE_AO_INFO", "false").lower() == "true"
    if do_update_ao_info:
        # Update reference AO data in the database
        print("Updating reference AO data in the database.")
        engine = create_engine(os.environ['COCKROACH_CONNECTION_STRING'])
        try:
            ao_data = get_reference_ao_data(sheet_id="1c1vvx07AXdnu6NSa4is4a0oyUiu8q3cgOecFbTNWlAY")
            for team_name in ["carpex_super_region", "carpex", "greenlevel", "peakcity"]:
                ao_data.to_sql(f"ao_info_{team_name}", con=engine, if_exists="replace", index=False)
        except TimeoutError:
            print("Timeout error updating reference AO data in the database. Continuing.")

        try:
            ao_data = get_reference_ao_data(sheet_id="1W5ULRiVCjrnBZ1jiLFpwy3E1osQ-doRsdASGMKtZI7Y")
            team_name = "churham"
            ao_data.to_sql(f"ao_info_{team_name}", con=engine, if_exists="replace", index=False)
        except TimeoutError:
            print("Timeout error updating reference AO data in the database. Continuing.")
    else:
        print("Skipping update of reference AO data in the database.")

    # Update the processed data in the database
    print("starting database-based workflow for Churham")
    do_pipeline_db("churham", ["T4GNGR79U"])
    print("starting database-based workflow for Carpex Super Region")
    do_pipeline_db("carpex_super_region", [None, "T86PHS6VB", "T04GS2ZJBHD", "T046M8F12U8"])
    print("starting database-based workflow for Carpex")
    do_pipeline_db("carpex", ["T86PHS6VB"])
    print("starting database-based workflow for Green Level")
    do_pipeline_db("greenlevel", ["T04GS2ZJBHD"])
    print("starting database-based workflow for Peak City")
    do_pipeline_db("peakcity", ["T046M8F12U8"])
    print("Completed database-based workflow.")
