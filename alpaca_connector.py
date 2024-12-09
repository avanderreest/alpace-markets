from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, TrailingStopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus

from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
# load_dotenv()

# Alpaca API credentials
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')  # Use paper trading URL by default

# Get trader settings
max_budget_per_ticker_position = float(os.getenv('MAX_BUDGET_PER_TICKER_POSITION', 10000))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Initialize the Alpaca TradingClient
trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

# Initialize the Market Data Client directly with the API key and secret key
data_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# sys.exit("Exiting the script.")

# Define a route to handle webhook messages from TradingView
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return "Invalid data", 400
    
    # Extract the message type and other relevant information
    ticker = data.get('ticker').upper()
    alert_message = data.get('side')
    time = data.get('time_in_force')
    trailing_price = round(float(data.get('trail_price')), 2) # This is the trailing price that will be used for the trailing stop order and is converted to a float and rounded to 2 decimal places. NOT USED IN THIS VERSION. Tradeview manages the trailing stop order.
    
    print(f"ticker: {ticker}, alert_message: {alert_message}, time: {time}, trailing_price: {trailing_price}")


    if not all([ticker, alert_message, time]):
        return "Incomplete data", 400

    # Handle buy and sell messages
    if "Buy" in alert_message:
        
        if not tickerHasPosition(ticker, trading_client):
            current_price = getLatestTickerPrice(ticker, data_client)
            if current_price is None:
                return "Failed to get the current price", 400
                        
            qty_buy = calculateSharesToBuy(current_price, max_budget_per_ticker_position,trading_client)
            
            if qty_buy == 0: # If the number of shares to buy is 0, do not place the order
                return "No cash to buy shares for {ticker}", 200
            elif qty_buy > 0:
                handle_buy_signal(ticker, qty_buy, trailing_price,trading_client)
                
    elif "Sell" in alert_message:
        handle_sell_signal(ticker, trading_client)
    else:
        return "Unknown alert type", 400

    return "Message received", 200

def calculateSharesToBuy(current_price, max_budget_per_ticker_position, trading_client):
    # The no of shares to buy is based on the max budget per ticker position. 
    # If the account size is greater than the max budget per ticker position, calculate the number of shares to buy based on the max budget per ticker position
    
    account = trading_client.get_account() # Get the account information
    account_size = float(account.cash) # Get available cash in the account

    # Check if the account size is greater than the max budget per ticker position
    if account_size >= max_budget_per_ticker_position: # If so, calculate the number of shares to buy based on the max budget per ticker position
        shares_to_buy = max_budget_per_ticker_position / current_price
    else:
        shares_to_buy = 0 # If the account size is less than the max budget per ticker position, do not place the order
    
    return int(shares_to_buy)   

def getLatestTickerPrice(ticker, data_client):
    try:
        # Create a request for the latest trade
        request_params = StockLatestTradeRequest(symbol_or_symbols=ticker)
        
        # Get the latest trade
        latest_trade = data_client.get_stock_latest_trade(request_params)
        
        # Extract the price from the latest trade
        current_price = latest_trade[ticker].price
        
        return current_price
    except Exception as e:
        print(f"Error fetching the current price for {ticker}: {e}")
        return None
    
def tickerHasPosition(ticker, trading_client):
    try:
        positions = trading_client.get_all_positions()
        for position in positions:
            if position.symbol == ticker:
                return True
        return False
    except Exception as e:
        print(f"Error checking position for {ticker}: {e}")
        return False

def get_position(ticker, trading_client):
    try:
        positions = trading_client.get_all_positions()
        for position in positions:
            if position.symbol == ticker:
                return position
        return None
    except Exception as e:
        print(f"Error retrieving position for {ticker}: {e}")
        return None

def handle_buy_signal(ticker,qty_buy, trailing_price, trading_client):
    try:
        # Step 1: Place a Market Buy Order for 1 share of NVDA
        market_order_data = MarketOrderRequest(
            symbol=ticker,
            qty=qty_buy,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC
        )
        print(f"Placing market order for {qty_buy} shares of {ticker}")
        # sys.exit("Exiting the script.") 
        market_order = trading_client.submit_order(order_data=market_order_data)
        print(f"Market order placed: {market_order.id}")

    except Exception as e:
        print(f"Failed to place market order: {e}")
    
def handle_sell_signal(ticker, trading_client):
    try:
        close_order = trading_client.close_position(ticker)
        print(f"Position closed: {close_order}")
    except Exception as e:
        print(f"Failed to close NVDA position: {e}")

if __name__ == '__main__':
 
    app.run(host="0.0.0.0", port=5010)
    
    # •	127.0.0.1 (localhost): When the application listens on 127.0.0.1, it only accepts connections from within the container itself.
	# •	0.0.0.0: This tells the application to listen on all available network interfaces, including the container’s external interface, which is mapped to the host port 5010 through Docker.
 