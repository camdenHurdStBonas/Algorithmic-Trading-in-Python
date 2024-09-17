# main.py
from scheduler import start_scheduler
from robinhood_api_trading import CryptoAPITrading
from trading_strategy import trading_strategy

def main():
    api_trading_client = CryptoAPITrading()
    
    # Fetch and print account details
    print("Account details:")
    print(api_trading_client.get_account())

    # Start the scheduler with the trading strategy function and desired interval
    start_scheduler(trading_strategy, 1)  # Run trading strategy every 10 seconds
    
    # Fetch and print account details
    print("Account details:")
    print(api_trading_client.get_account())
    
    print("Done!")

if __name__ == "__main__":
    main()
