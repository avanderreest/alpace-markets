from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the environment variables
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')  # Default value if not in .env

print(f"Alpaca API Key: {ALPACA_API_KEY}")
print(f"Alpaca Secret Key: {ALPACA_SECRET_KEY}")
print(f"Alpaca Base URL: {APCA_API_BASE_URL}")