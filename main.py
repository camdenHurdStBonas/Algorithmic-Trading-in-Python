import uuid
from trading_strategy import trading_strategy  # Import the function
from robinhood_api_trading import CryptoAPITrading  # Assuming you have this class defined in CryptoAPITrading.py

def main():
    api_trading_client = CryptoAPITrading()
    
    # Fetch and print account details
    print("Account details:")
    print(api_trading_client.get_account())

    # Run the trading strategy
    trading_strategy(api_trading_client)

if __name__ == "__main__":
    main()
