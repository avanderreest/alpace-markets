from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os
import sys

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Alpaca API credentials
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')  # Use paper trading URL by default
print(f"Alpaca API Key: {ALPACA_API_KEY}")
print(f"Alpaca Secret Key: {ALPACA_SECRET_KEY}")
print(f"Alpaca Base URL: {APCA_API_BASE_URL}")

# Initialize Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, APCA_API_BASE_URL, api_version='v2')

# Define a route to handle webhook messages from TradingView
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return "Invalid data", 400

    # Extract the message type and other relevant information
    ticker = data.get('ticker')
    alert_message = data.get('side')
    time = data.get('time_in_force')
    trailing_price = round(float(data.get('trail_price')), 2) # This is the trailing price that will be used for the trailing stop order and is converted to a float and rounded to 2 decimal places
    
    print(f"ticker: {ticker}, alert_message: {alert_message}, time: {time}, trailing_price: {trailing_price}")


    if not all([ticker, alert_message, time]):
        return "Incomplete data", 400

    # Handle buy and sell messages
    if "Buy" in alert_message:
        handle_buy_signal(ticker, time, trailing_price)
    elif "Sell" in alert_message:
        handle_sell_signal(ticker, time)
    else:
        return "Unknown alert type", 400

    print("Message received:", data)
    return "Message received", 200

def getLatestTickerPrice(ticker):
    """
    Fetch the latest price for the given ticker using Alpaca API.
    
    Args:
        ticker (str): The ticker symbol to fetch the price for.
    
    Returns:
        float: The latest price of the ticker.
    """
    try:
        bars = api.get_bars(ticker, '1Min', limit=1).df
        latest_bar = bars.iloc[-1]  # Get the most recent bar
        return latest_bar['close']
    except Exception as e:
        print(f"Error fetching the latest price for {ticker}: {e}")
        return None

def tickerHasPosition(ticker):
    """
    Check if the given ticker has an open position in the Alpaca account.
    
    Args:
        ticker (str): The ticker symbol to check.
    
    Returns:
        bool: True if the ticker has an open position, False otherwise.
    """
    try:
        positions = api.list_positions()
        for position in positions:
            if position.symbol == ticker:
                return True
        return False
    except Exception as e:
        print(f"Error checking position for {ticker}: {e}")
        return False

def get_position(ticker):
    """
    Get the open position for the given ticker.
    
    Args:
        ticker (str): The ticker symbol to check.
    
    Returns:
        Position: The position object for the ticker, or None if no position exists.
    """
    try:
        positions = api.list_positions()
        for position in positions:
            if position.symbol == ticker:
                return position
        return None
    except Exception as e:
        print(f"Error retrieving position for {ticker}: {e}")
        return None

def handle_buy_signal(ticker, time, trailing_price):
    print(f"Buy signal received for {ticker} at {time}")
    try:
        if not tickerHasPosition(ticker):
            price = getLatestTickerPrice(ticker)
            if price is None:
                print(f"Unable to retrieve price for {ticker}. Buy signal aborted.")
                return

            # Check available cash
            account = api.get_account()
            available_cash = float(account.cash)

            # Calculate max quantity to buy with 10% limit of available cash
            max_budget = available_cash * 0.10
            
            if max_budget > 1000: # Limit to $1000 max budget
                max_budget = 1000  
                
            max_qty = max_budget // price

            if max_qty > 0:
                api.submit_order(
                symbol=ticker,
                qty=int(max_qty),
                side='buy',
                type='trailing_stop',
                time_in_force='gtc',
                trail_price=trailing_price  # This sets a trailing stop of $0.10 below the current market price. Price is calculated Tradingview and past byt the API webhook
            )
                print(f"Market order placed for {ticker}: {max_qty} shares")
            else:
                print(f"Not enough available cash to buy {ticker} at {price}")
        else:
            print(f"{ticker} already has an open position")
    except Exception as e:
        print(f"Error placing buy order: {e}")

def handle_sell_signal(ticker, time):
    print(f"Sell signal received for {ticker} at {time}")
    try:
        position = get_position(ticker)
        if position:
            # Close the position
            api.close_position(ticker) # This will close the entire position for the given ticker
            
            # api.submit_order(
            #     symbol=ticker,
            #     qty=position.qty,
            #     side='sell',
            #     type='market',
            #     time_in_force='gtc'
            # )
            print(f"Sell order placed for {ticker}")
        else:
            print(f"No open position for {ticker}")
    except Exception as e:
        print(f"Error placing sell order: {e}")

if __name__ == '__main__':
    app.run(port=5010)