from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

# Replace with your Alpaca API key and secret
API_KEY = 'PKOKUFYMORFRCMH1HCOF'
SECRET_KEY = 'P8Op0Vl2INOF8jXwdkieqe7EzergH7XvYos4NEyw'

# Initialize the Market Data Client directly with the API key and secret key
data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

def getLatestTickerPrice(ticker):
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

# Example usage
ticker = 'NVDA'
current_price = getLatestTickerPrice(ticker)
print(f"Current price for {ticker}: {current_price}")