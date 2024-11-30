# main.py
from trading_scheduler import start_scheduler
from robinhood_api_trading import CryptoAPITrading
from btc_trading_strategy import BTC_trading_strategy

def main():
    api_trading_client = CryptoAPITrading()
    
    # Fetch and print account details
    print("Account details:")
    print(api_trading_client.get_account())

    # Start the scheduler with the trading strategy function and desired interval
    start_scheduler(BTC_trading_strategy, 10)  # Run trading strategy every 10 seconds
    
    # Fetch and print account details
    print("Account details:")
    print(api_trading_client.get_account())
    
    print("Done!")

if __name__ == "__main__":
    main()
