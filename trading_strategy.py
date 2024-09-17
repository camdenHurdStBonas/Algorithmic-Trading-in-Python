from typing import Any
import uuid
import logging
from robinhood_api_trading import CryptoAPITrading

# Configure logging
logging.basicConfig(level=logging.INFO)

def trading_strategy(api_trading_client: Any):
  
    # Get Best Bid/Ask Prices
    print("\nFetching Best Bid/Ask for BTC-USD...")
    best_bid_ask = api_trading_client.get_best_bid_ask("BTC-USD")
    print("Best Bid/Ask response:")
    print(best_bid_ask)
    
