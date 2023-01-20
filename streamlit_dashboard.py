import logging
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from dateutil.relativedelta import relativedelta

PAYLOAD, HEADERS = {}, {}

END_DATE_DEFAULT = datetime.now() - relativedelta(days=1)
START_DATE_DEFAULT = END_DATE_DEFAULT - relativedelta(years=1)
MIN_DATE = datetime.now() - relativedelta(years=11)

st.title("Saber Interactive test assignment")


@st.cache
def fetch_asset_data(limit: int = 5) -> list:
    url = f"https://api.coincap.io/v2/assets?limit={limit}"
    r = requests.request("GET", url, headers=HEADERS, data=PAYLOAD)
    raw_assets_data = r.json()["data"]
    return raw_assets_data


def get_unix_time(date: datetime) -> int:
    return int(time.mktime(date.timetuple()) * 1000)


def get_asset_identifiers(data: list) -> dict:
    return {asset["id"]: asset["symbol"] for asset in data}


def get_asset_id_by_symbol(assets: dict, symbol: str) -> str:
    for key, value in assets.items():
        if symbol == value: return key 


def calculate_interval(start_date: datetime, end_date: datetime) -> str:
    days_difference = (end_date - start_date).days
    if days_difference > 14: return "d1"
    elif days_difference <= 14 and days_difference >= 7: return "m30"
    return "m15"


@st.cache
def fetch_history_data(
    symbol: str,
    start_date: datetime = START_DATE_DEFAULT,
    end_date: datetime = END_DATE_DEFAULT,
) -> list:
    interval = calculate_interval(start_date, end_date)
    start_date_unix, end_date_unix = get_unix_time(start_date), get_unix_time(end_date)

    url = f"https://api.coincap.io/v2/assets/{symbol}/history?interval={interval}&start={start_date_unix}&end={end_date_unix}"
    r = requests.request("GET", url, headers=HEADERS, data=PAYLOAD)
    raw_history_by_id = r.json()["data"]
    if not raw_history_by_id:
        raise Exception("Error in getting data")
    return raw_history_by_id


def create_historical_fig(
    df: pd.DataFrame, start_date: datetime, end_date: datetime
) -> go.Figure:
    )
    return fig


def generate_summary(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> str:
    first_el, last_el = float(df["priceUsd"].iloc[0]), float(df["priceUsd"].iloc[-1])
    changes = round(last_el - first_el, 3)
    percent_changes = round(abs(last_el - first_el) * 100 / last_el, 2)
    arrow = ":arrow_upper_right:" if changes >= 0 else ":arrow_lower_right:"
    sign = "+" if changes > 0 else ""
    return (
        f"{sign}{changes} ({percent_changes}%) {arrow} from {start_date} to {end_date}"
    )


def get_historical_df(data: list) -> pd.DataFrame:
    df = pd.DataFrame.from_records(data)
    df["priceUsd"] = df["priceUsd"].apply(lambda x: float(x))
    df["date"] = pd.to_datetime(df["date"])
    return df


def main():

    data = fetch_asset_data()
    assets = get_asset_identifiers(data)

    with st.sidebar:
        choice = st.selectbox("Select an asset", assets.values())

    # https://github.com/streamlit/streamlit/issues/5234 - about date_input format
    sidebar_layout = st.sidebar.columns(2)
    with sidebar_layout[0]:
        start_date_input = st.date_input(
            "Date from",
            value=START_DATE_DEFAULT,
            min_value=MIN_DATE,
            max_value=END_DATE_DEFAULT
            - relativedelta(days=1),
        )
    with sidebar_layout[-1]:
        end_date_input = st.date_input(
            "Date to",
            value=END_DATE_DEFAULT,
            min_value=MIN_DATE,
            max_value=END_DATE_DEFAULT,
        )

    asset_id = get_asset_id_by_symbol(assets, symbol=choice)
    historical_raw_data = fetch_history_data(
        asset_id, get_unix_time(start_date_input), get_unix_time(end_date_input)
    )
    hist_plot = create_historical_fig(
        historical_raw_data, start_date_input, end_date_input
    )

    st.plotly_chart(hist_plot)


if __name__ == "__main__":
    main()
