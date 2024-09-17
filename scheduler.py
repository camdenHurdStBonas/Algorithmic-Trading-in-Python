import schedule
import time
import logging
import threading
from typing import Callable
from robinhood_api_trading import CryptoAPITrading

# Configure logging
logging.basicConfig(filename='trading_scheduler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def job(trading_strategy: Callable[[CryptoAPITrading], None]):
    try:
        api_trading_client = CryptoAPITrading()
        trading_strategy(api_trading_client)
        logging.info("Trading strategy executed successfully.")
    except Exception as e:
        logging.error(f"Error executing trading strategy: {e}")

def run_scheduler(trading_strategy: Callable[[CryptoAPITrading], None], interval_seconds: int):
    # Schedule the job to run every `interval_seconds`
    schedule.every(interval_seconds).seconds.do(job, trading_strategy)
    print(f"Scheduler started. Trading strategy will run every {interval_seconds} seconds.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep to avoid high CPU usage

def start_scheduler(trading_strategy: Callable[[CryptoAPITrading], None], interval_seconds: int):
    scheduler_thread = threading.Thread(target=run_scheduler, args=(trading_strategy, interval_seconds), daemon=True)
    scheduler_thread.start()
    
    try:
        while True:
            command = input("Type 'q' to quit the scheduler: ").strip().lower()
            if command == 'q':
                print("Stopping scheduler...")
                break
    except KeyboardInterrupt:
        print("Scheduler stopped by user.")
