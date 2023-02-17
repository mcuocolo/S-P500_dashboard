import yfinance as yf
import streamlit as st
import datetime
import pandas as pd
import cufflinks as cf
from plotly.offline import iplot

cf.go_offline()

# A function to dload list of components in S&P 500
@st.cache_data
def get_sp500_components():
    df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df = df[0]
    tickers = df["Symbol"].to_list()
    tickers_companies_dict = dict(
        zip(df["Symbol"], df["Security"])
    )
    return tickers, tickers_companies_dict

# get data from YF
@st.cache_data
def load_data(symbol, start, end):
    return yf.download(symbol, start, end)

# save as csv
@st.cache_data
def convert_to_csv(df):
    return df.to_csv().encode("utf-8")

# st layout

st.sidebar.header("Stock Parameters")

available_tickers, tickers_companies_dict = get_sp500_components()
ticker = st.sidebar.selectbox("Ticker", available_tickers, format_func=tickers_companies_dict.get)

start_date = st.sidebar.date_input("Start date", datetime.date(2019, 1, 1))
end_date = st.sidebar.date_input("End date", datetime.date.today())

if start_date > end_date:
    st.sidebar.error("The end date must fall after the start date!")

st.sidebar.header("Technical Analysis Indicator")

volume_flag = st.sidebar.checkbox(label="Show volume")

### SMA ##########################################
exp_sma = st.sidebar.expander("SMA")
sma_flag = exp_sma.checkbox(label="Add SMA")
sma_periods = exp_sma.number_input(label="SMA Periods", min_value=1, max_value=50, value=20, step=1)

### BBands ##########################################
exp_bb = st.sidebar.expander("Bolling Bands")
bb_flag = exp_bb.checkbox(label="Add BBands")
bb_periods = exp_bb.number_input(label="BB Periods", min_value=1, max_value=50, value=20, step=1)
bb_std = exp_bb.number_input(label="BB std deviation", min_value=1, max_value=4, value=2, step=1)

### RSI ##########################################
exp_rsi = st.sidebar.expander("RSI")
rsi_flag = exp_rsi.checkbox(label="Add RSI")
rsi_periods = exp_rsi.number_input(label="RSI Periods", min_value=1, max_value=50, value=20, step=1)
rsi_upper = exp_rsi.number_input(label="RSI Upper", min_value=60, max_value=90, value=70, step=5)
rsi_lower = exp_rsi.number_input(label="RSI Lower", min_value=10, max_value=40, value=30, step=5)

st.title("A cool web app for technical analysis of S&P 500 stocks")
st.write("Select company to show stock data and desired TA")

df = load_data(ticker, start_date, end_date)

# expander with data preview
data_exp = st.expander("Preview data")
available_cols = df.columns.tolist()
columns_to_show = data_exp.multiselect("Columns", available_cols, default=available_cols)
data_exp.dataframe(df[columns_to_show])

csv_file = convert_to_csv(df[columns_to_show])
data_exp.download_button(label="Download selected as CSV", data=csv_file,
                         file_name=f"{ticker}_stock_prices.csv", mime="text/csv")

# add candlesticks
title_str = f"{tickers_companies_dict[ticker]}'s stock price"

qf = cf.QuantFig(df, title=title_str)
if volume_flag:
    qf.add_volume()
if sma_flag:
    qf.add_sma(periods=sma_periods)
if bb_flag:
    qf.add_bollinger_bands(periods=bb_periods, boll_std=bb_std)
if rsi_flag:
    qf.add_rsi(periods=rsi_periods, rsi_upper=rsi_upper, rsi_lower=rsi_lower, showbands=True)

fig = qf.iplot(asFigure=True)
st.plotly_chart(fig)
