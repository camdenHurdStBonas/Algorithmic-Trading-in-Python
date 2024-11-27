import schedule
import time
import logging
import threading
from typing import Callable, List, Tuple
import functools
from robinhood_api_trading import CryptoAPITrading

# Configure logging
logging.basicConfig(filename='trading_scheduler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_account_value(api_trading_client: CryptoAPITrading) -> float:
    """
    Calculate the total value of the account, including cash and holdings.
    
    :param api_trading_client: An instance of the CryptoAPITrading client.
    :return: The total account value as a float.
    """
    try:
        # Fetch account buying power (cash balance)
        account_info = api_trading_client.get_account()
        buying_power = float(account_info.get('buying_power', 0))

        # Fetch all holdings
        holdings = api_trading_client.get_holdings()
        total_crypto_value = 0

        # Calculate the value of each holding
        for holding in holdings.get('results', []):
            asset_code = holding.get('asset_code')
            quantity = float(holding.get('total_quantity', 0))
            
            # Get the current price of the asset
            price_info = api_trading_client.get_best_bid_ask(f"{asset_code}-USD")
            current_price = float(price_info['results'][0]['bid_inclusive_of_sell_spread'])
            
            # Calculate and add the value of the holding
            total_crypto_value += quantity * current_price

        # Return total account value (cash + crypto holdings)
        total_value = buying_power + total_crypto_value
        return total_value

    except Exception as e:
        logging.error(f"Error calculating account value: {e}")
        return 0  # Default to 0 if there's an error

def job(trading_strategy: Callable[[CryptoAPITrading], None], api_trading_client: CryptoAPITrading):
    try:
        logging.info(f"trading...")
        account_value = get_account_value(api_trading_client)
        logging.info(f"Current account value: {account_value:.2f}")

        # Execute trading strategy if account value is above the threshold
        trading_strategy(api_trading_client)
        logging.info(f"Trading strategy executed successfully for {trading_strategy.__name__}.")

    except Exception as e:
        logging.error(f"Error executing trading strategy: {e}")

def run_scheduler(trading_strategies: List[Tuple[Callable[[CryptoAPITrading], None], int]]):
    """
    Accepts a list of trading strategies with their respective intervals and schedules each strategy.
    
    :param trading_strategies: A list of tuples containing the trading strategy and its interval in seconds.
    """
    api_trading_client = CryptoAPITrading()  # Instantiate once for the scheduler
    logging.info(api_trading_client.get_account())

    for trading_strategy, interval_seconds in trading_strategies:
        # Use functools.partial to pass the strategy and the client properly
        schedule.every(interval_seconds).seconds.do(functools.partial(job, trading_strategy, api_trading_client))
        print(f"Scheduler started for {trading_strategy.__name__}, will run every {interval_seconds} seconds.")

    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep to avoid high CPU usage

def start_scheduler(trading_strategies: List[Tuple[Callable[[CryptoAPITrading], None], int]]):
    """
    Starts the scheduler for multiple trading strategies in a separate thread.
    
    :param trading_strategies: A list of tuples containing trading strategies and their respective intervals.
    """
    logging.info("Starting scheduler...")
    scheduler_thread = threading.Thread(target=run_scheduler, args=(trading_strategies,), daemon=True)
    scheduler_thread.start()

    try:
        while True:
            command = input("Type 'q' to quit the scheduler:\n").strip().lower()
            if command == 'q':
                print("\nStopping scheduler...")
                logging.info("Scheduler Stopped.")
                logging.info("end.")
                break
    except KeyboardInterrupt:
        print("Scheduler stopped by user.")
