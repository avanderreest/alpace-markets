import os
import streamlit as st
import pandas as pd
import numpy as np
import ta
import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Alpaca API credentials
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')  # Use paper trading URL by default

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Function to download historical data
def get_historical_data(symbol, timeframe='4Hour', min_data_points=50):
    end_date = pd.Timestamp.now(tz='America/New_York')
    start_date = end_date - timedelta(days=30)  # Fetch data for the last 30 days
    bars = api.get_bars(symbol, timeframe, start=start_date.isoformat(), end=end_date.isoformat()).df
    return bars

# Function to compute MACD
def compute_macd(df, fast_length, slow_length, signal_smoothing):
    macd = ta.trend.MACD(df['close'], window_slow=slow_length, window_fast=fast_length, window_sign=signal_smoothing)
    df['macd'] = macd.macd()
    df['signal'] = macd.macd_signal()
    df['hist'] = macd.macd_diff()
    return df

# Function to compute ATR
def compute_atr(df, atr_period, atr_multiplier):
    atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=atr_period)
    df['atr'] = atr.average_true_range()
    df['trail_price'] = np.nan
    return df

# Streamlit interface
st.title('MACD Trailing Stop Strategy')

symbol = st.text_input("Symbol", value="AAPL")
timeframe = st.selectbox("Timeframe", ["1Min", "5Min", "15Min", "1H", "4H", "1D"], index=4)
fast_length = st.slider("MACD Fast Length", 1, 50, 3)
slow_length = st.slider("MACD Slow Length", 1, 50, 10)
signal_smoothing = st.slider("MACD Signal Smoothing", 1, 50, 16)
atr_period = st.slider("ATR Period", 1, 50, 14)
atr_multiplier = st.slider("ATR Multiplier", 0.1, 5.0, 1.0)

min_data_points = max(slow_length, atr_period)

if st.button('Run Strategy'):
    df = get_historical_data(symbol, timeframe, min_data_points)
    
    if len(df) < min_data_points:
        st.error(f"Not enough data to compute MACD and ATR. Minimum required data points: {min_data_points}")
    else:
        df = compute_macd(df, fast_length, slow_length, signal_smoothing)
        df = compute_atr(df, atr_period, atr_multiplier)

        buy_signals = []
        sell_signals = []

        position_size = 0
        for i in range(1, len(df)):
            if df['macd'][i] > df['signal'][i] and df['macd'][i-1] <= df['signal'][i-1]:
                buy_signals.append(i)
                position_size = 1
            elif df['macd'][i] < df['signal'][i] and df['macd'][i-1] >= df['signal'][i-1]:
                sell_signals.append(i)
                position_size = 0

            if position_size > 0:
                trail_price = df['close'][i] - (df['atr'][i] * atr_multiplier)
                df.at[i, 'trail_price'] = trail_price

        st.write(df.tail())

        fig, ax = plt.subplots()
        ax.plot(df.index, df['close'], label='Close Price')
        ax.plot(df.index, df['macd'], label='MACD', color='blue')
        ax.plot(df.index, df['signal'], label='Signal', color='red')
        ax.scatter(df.iloc[buy_signals].index, df.iloc[buy_signals]['close'], marker='^', color='green', label='Buy Signal')
        ax.scatter(df.iloc[sell_signals].index, df.iloc[sell_signals]['close'], marker='v', color='red', label='Sell Signal')
        ax.scatter(df.index, df['trail_price'], marker='x', color='orange', label='Trailing Stop')

        ax.legend()
        st.pyplot(fig)

        # Generate JSON message for the trailing stop order
        last_trail_price = df['trail_price'].dropna().iloc[-1] if not df['trail_price'].dropna().empty else 0
        order_json = {
            "symbol": symbol,
            "qty": "all",
            "side": "sell",
            "type": "trailing_stop",
            "trail_price": f"{last_trail_price:.2f}",
            "time_in_force": "gtc",
            "order_class": "simple"
        }
        st.json(order_json)