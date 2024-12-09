API_KEY = 'PKOKUFYMORFRCMH1HCOF'
SECRET_KEY = 'P8Op0Vl2INOF8jXwdkieqe7EzergH7XvYos4NEyw'

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, AssetExchange

# Initialize the TradingClient
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

# Get all assets
assets = trading_client.get_all_assets()

# Filter for active, tradeable stocks on the NASDAQ exchange
nasdaq_stocks = [
    asset for asset in assets 
    if asset.tradable  # Check if the asset is tradable
    and asset.asset_class == AssetClass.US_EQUITY  # Ensure the asset is a US equity (stock)
    and asset.exchange == AssetExchange.NASDAQ  # Ensure the asset is listed on NASDAQ
]

## from nasdaq_stocks, get the symbols of the stocks and create a list of symbols


# Extract the symbols from the nasdaq_stocks list
nasdaq_symbols = [asset.symbol for asset in nasdaq_stocks]

# Print the list of NASDAQ symbols
print(nasdaq_symbols)