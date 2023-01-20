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
def fetch_asset_data(limit=5):
    url = f"https://api.coincap.io/v2/assets?limit={limit}"
    r = requests.request("GET", url, headers=HEADERS, data=PAYLOAD)
    raw_assets_data = r.json()["data"]
    return raw_assets_data


def get_unix_time(date):
    return int(time.mktime(date.timetuple()) * 1000)


    return {asset["id"]: asset["symbol"] for asset in data}


def get_asset_id_by_symbol(assets, symbol):
    for key, value in assets.items():
        if symbol == value: return key 




@st.cache
def fetch_history_data(
    symbol, start_date_unix=START_DATE_UNIX, end_date_unix=END_DATE_UNIX
):
    url = f"https://api.coincap.io/v2/assets/{symbol}/history?interval=d1&start={start_date_unix}&end={end_date_unix}"
    r = requests.request("GET", url, headers=HEADERS, data=PAYLOAD)
    raw_history_by_id = r.json()["data"]
    if not raw_history_by_id:
        raise Exception("Error in getting data")
    return raw_history_by_id


def create_historical_fig(data, start_date, end_date):
    df = pd.DataFrame.from_records(data)
    df["date"] = pd.to_datetime(df["time"], unit="ms").dt.date
    df = df[(df["date"] > start_date) & (df["date"] < end_date)]
    fig = px.bar(
        df, x="date", y="priceUsd", labels={"date": "TIME", "priceUsd": "PRICE"}
    )
    return fig


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
            max_value=END_DATE_DEFAULT,
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
