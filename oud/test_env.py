import os


# Alpaca API credentials
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')  # Use paper trading URL by default
RISK_PERCENT = os.getenv('RISK_PERCENT', 0.01 )
MAX_BUDGET_PER_TICKER_POSITION = os.getenv('MAX_BUDGET_PER_TICKER_POSITION', 500 )


print(API_KEY)
print(API_SECRET)
print(BASE_URL)
print(RISK_PERCENT)
print(MAX_BUDGET_PER_TICKER_POSITION)
