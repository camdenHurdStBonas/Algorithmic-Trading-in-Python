from typing import Any
import uuid
import logging
from robinhood_api_trading import CryptoAPITrading
import ccxt
import pandas as pd
import json
import datetime 

# Store the last signal in a file to avoid duplicate trades
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define a threshold for stopping trades
ACCOUNT_VALUE_THRESHOLD = 12500  # Set your desired threshold here

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

def read_last_signal(filename="BTC_last_signal.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return file.read().strip()
    return "hold"  # Default if file doesn't exist

def save_last_signal(signal, filename="BTC_last_signal.txt"):
    with open(filename, "w") as file:
        file.write(signal)

def fetch_historical_data(symbol: str = "BTC/USD",start_date: str = '2022-01-01T00:00:00Z', timeframe: str = '1d', limit: int = 365) -> pd.Series:
    """
    Fetches historical Bitcoin data from a crypto exchange using ccxt.
    
    :param symbol: The trading pair symbol
    :param timeframe: The data interval (e.g., '1m', '5m', '1h', '1d').
    :param limit: The number of data points to retrieve (default is 365).
    :return: A pandas Series with the closing prices of Bitcoin.
    """
    exchange = ccxt.coinbase()  # Correct exchange name for Coinbase in ccxt
    since = exchange.parse8601(start_date)  # Set the starting point for fetching data

    # Fetch OHLCV data (Open, High, Low, Close, Volume)
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit, since=since)
    
    # Convert OHLCV to a DataFrame
    price_data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Convert timestamp to a readable datetime format
    price_data['timestamp'] = pd.to_datetime(price_data['timestamp'], unit='ms')

    # Return the closing prices
    return price_data.set_index('timestamp')

def calculate_macd(prices: pd.Series, short_window: int = 60, long_window: int = 69, signal_window: int = 8) -> pd.DataFrame:
    """
    Calculates MACD values for a given price series.
    
    :param prices: Series of price data.
    :param short_window: Short EMA window for MACD.
    :param long_window: Long EMA window for MACD.
    :param signal_window: Window for MACD signal line.
    :return: DataFrame with MACD line, signal line, and histogram.
    """
    short_ema = prices.ewm(span=short_window, adjust=False).mean()
    long_ema = prices.ewm(span=long_window, adjust=False).mean()
    
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()

    macd_df = pd.DataFrame({
        'MACD': macd_line,
        'Signal Line': signal_line,
    })

    """
    Generates buy or sell signal based on MACD strategy.
    
    :param macd_df: DataFrame with MACD, Signal line, and Histogram.
    :return: 'buy' or 'sell' signal.
    """
    # Check if the MACD line crosses above the signal line (buy signal)
    if macd_df.iloc[-1]['MACD'] > macd_df.iloc[-1]['Signal Line'] and macd_df.iloc[-2]['MACD'] <= macd_df.iloc[-2]['Signal Line']:
        return 'buy'
    
    # Check if the MACD line crosses below the signal line (sell signal)
    elif macd_df.iloc[-1]['MACD'] < macd_df.iloc[-1]['Signal Line'] and macd_df.iloc[-2]['MACD'] >= macd_df.iloc[-2]['Signal Line']:
        return 'sell'
    
    # If no crossover, return 'hold'
    return 'hold'

def calculate_mvcd(prices: pd.Series, short_window: int = 60, long_window: int = 69, signal_window: int = 8) -> pd.DataFrame:
    """
    Calculates MACD values for a given price series.
    
    :param prices: Series of price data.
    :param short_window: Short EMA window for MACD.
    :param long_window: Long EMA window for MACD.
    :param signal_window: Window for MACD signal line.
    :return: DataFrame with MACD line, signal line, and histogram.
    """
    # Calculate daily returns
    returns = prices.pct_change().dropna()
    
    short_ema = prices.ewm(span=short_window, adjust=False).std()
    long_ema = prices.ewm(span=long_window, adjust=False).std()
    
    mvcd_line = short_ema - long_ema
    signal_line = mvcd_line.ewm(span=signal_window, adjust=False).std()

    macd_df = pd.DataFrame({
        'MVCD': mvcd_line,
        'Signal Line': signal_line,
    })

    """
    Generates buy or sell signal based on MACD strategy.
    
    :param macd_df: DataFrame with MACD, Signal line, and Histogram.
    :return: 'buy' or 'sell' signal.
    """
    # Check if the MACD line crosses above the signal line (buy signal)
    if macd_df.iloc[-1]['MVCD'] > macd_df.iloc[-1]['Signal Line'] and macd_df.iloc[-2]['MVCD'] <= macd_df.iloc[-2]['Signal Line']:
        return 'buy'
    
    # Check if the MACD line crosses below the signal line (sell signal)
    elif macd_df.iloc[-1]['MVCD'] < macd_df.iloc[-1]['Signal Line'] and macd_df.iloc[-2]['MVCD'] >= macd_df.iloc[-2]['Signal Line']:
        return 'sell'
    
    # If no crossover, return 'hold'
    return 'hold'

def calculate_vwap(prices: pd.DataFrame, vwap_window: int = 20) -> str:
    """
    Calculates rolling VWAP and returns a signal.
    
    :param prices: DataFrame containing 'close', 'volume', 'high', 'low'.
    :param vwap_window: Rolling window period for VWAP calculation.
    :return: 'buy', 'sell', or 'hold'.
    """
    # Calculate the typical price
    typical_price = (prices['high'] + prices['low'] + prices['close']) / 3

    # Calculate rolling VWAP over the specified window
    typical_price_volume = typical_price * prices['volume']
    rolling_cumulative_price_volume = typical_price_volume.rolling(window=vwap_window).sum()
    rolling_cumulative_volume = prices['volume'].rolling(window=vwap_window).sum()

    vwap = rolling_cumulative_price_volume / rolling_cumulative_volume

    # Signal based on current price relative to VWAP
    if prices['close'].iloc[-1] > vwap.iloc[-1] and prices['close'].iloc[-2] <= vwap.iloc[-2]:  # Price above VWAP
        return 'buy'
    elif prices['close'].iloc[-1] < vwap.iloc[-1] and prices['close'].iloc[-2] >= vwap.iloc[-2]:  # Price below VWAP
        return 'sell'
    else:
        return 'hold'

def calculate_tema(prices: pd.Series, window: int = 20) -> str:
    """
    Calculates TEMA and returns a signal.
    
    :param prices: Series of price data.
    :param window: Window period for TEMA.
    :return: 'buy', 'sell', or 'hold'.
    """
    # Calculate the three EMAs needed for TEMA
    ema1 = prices.ewm(span=window, adjust=False).mean()  # First EMA
    ema2 = ema1.ewm(span=window, adjust=False).mean()    # Second EMA of the first EMA
    ema3 = ema2.ewm(span=window, adjust=False).mean()    # Third EMA of the second EMA

    # Calculate TEMA
    tema = 3 * (ema1 - ema2) + ema3

    # Signal based on price crossing above or below TEMA
    if prices.iloc[-1] > tema.iloc[-1] and prices.iloc[-2] <= tema.iloc[-2]:  # Price above TEMA
        return 'buy'
    elif prices.iloc[-1] < tema.iloc[-1] and prices.iloc[-2] >= tema.iloc[-2]:  # Price below TEMA
        return 'sell'
    else:
        return 'hold'
      
def aggregate_signals(signals: dict, weights: dict) -> str:
    """
    Aggregate signals from multiple indicators using a weighted average.
    
    :param signals: Dictionary of indicator signals. e.g., {'MACD': 'buy', 'RSI': 'sell'}
    :param weights: Dictionary of weights for each indicator. e.g., {'MACD': 0.6, 'RSI': 0.4}
    :return: Aggregated signal ('buy', 'sell', 'hold').
    """
    weighted_sum = 0
    total_weight = sum(weights.values())
    
    for indicator, signal in signals.items():
        if signal == 'buy':
            weighted_sum += weights.get(indicator, 0) * 1
        elif signal == 'sell':
            weighted_sum += weights.get(indicator, 0) * -1
        # 'hold' contributes 0 to the weighted sum
    
    # Normalize to -1 to +1 scale
    normalized_score = weighted_sum / total_weight
    
    logging.info(f"Weighted Aggregated Score: {normalized_score}")

    # Decision based on thresholds
    if normalized_score > 0.5:
        return 'buy'
    elif normalized_score < -0.5:
        return 'sell'
    else:
        return 'hold'
      
def save_trade_data(symbol: str, entry_price: float, trade_size: float, stop_loss: float, take_profit: float, status: str = "active", filename="BTC_trade_data.json"):
    trade_data = {
        "symbol": symbol,
        "entry_price": entry_price,
        "trade size": trade_size,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "status": status  # Track if the trade is "active" or "closed"
    }
    with open(filename, "w") as file:
        json.dump(trade_data, file)

def load_trade_data(filename="BTC_trade_data.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return None  # No active trade
 
def execute_trade(api_trading_client: CryptoAPITrading, signal: str, symbol: str, account_value: float, risk_per_trade: float, stop_loss_percent: float, take_profit_percent: float, confidence: float):
    """
    Execute a trade with risk management, including stop-loss and take-profit.
    Ensure buy signals only execute if no active trade is open, and sell signals close active trades.
    """
    try:
        # Check for active trade
        trade_data = load_trade_data()
        if signal == 'sell':
            if trade_data and trade_data["status"] == "active":
                logging.info(f"Sell signal received. Closing active trade for {trade_data['symbol']}.")
                # Place sell order to close active trade
                client_order_id = str(uuid.uuid4())
                order_config = {"amount": str(trade_data["trade_size"])}  # Sell the amount from active trade
                #api_trading_client.place_order(client_order_id, side='ask', order_type='market', symbol=symbol, order_config=order_config)
                save_trade_data(trade_data["symbol"], 0, 0, 0, status="closed")
                logging.info(f"Active trade for {trade_data['symbol']} closed.")
            else:
                logging.info("Sell signal received but no active trade to close.")
            return  # Exit after processing sell signal

        if signal == 'buy':
            if trade_data and trade_data["status"] == "active":
                logging.info("Buy signal received but an active trade is already open. No additional buy order placed.")
                return  # Don't open a new trade if there's already one active

            client_order_id = str(uuid.uuid4())
            risk_amount = account_value * risk_per_trade * confidence

            # Fetch buying power from the account
            account_info = api_trading_client.get_account()
            buying_power = float(account_info.get('buying_power', 0))

            # Check if risk_amount exceeds buying power
            if risk_amount > buying_power:
                logging.warning(f"Insufficient buying power (${buying_power:.2f}) for risk amount (${risk_amount:.2f}). Trade aborted.")
                return

            # Fetch the current price
            price_info = api_trading_client.get_best_bid_ask(symbol)
            current_price = float(price_info['results'][0]['bid_inclusive_of_sell_spread'])
            trade_size = risk_amount / current_price

            # Place buy order
            order_config = {"amount": str(trade_size)}
            #api_trading_client.place_order(client_order_id, side='bid', order_type='market', symbol=symbol, order_config=order_config)
            
            stop_loss_price = current_price * (1 - stop_loss_percent)
            take_profit_price = current_price * (1 + take_profit_percent)
            logging.info(f"Buy order placed for {trade_size:.6f} {symbol} at ${current_price:.2f}. Risk: ${risk_amount:.2f}/{trade_size} coins, SL: {stop_loss_price}, TP: {take_profit_price}.")
            
            # Save trade data for monitoring
            save_trade_data(symbol, current_price, trade_sze, stop_loss_price, take_profit_price)

        else:
            logging.info("No trade executed. Holding position.")

    except Exception as e:
        logging.error(f"Error executing trade for {symbol}: {e}")

def monitor_risk(api_trading_client: CryptoAPITrading, filename="trade_data.json"):
    """
    Monitors open trades for stop-loss and take-profit conditions.
    """
    try:
        trade_data = load_trade_data(filename)
        if not trade_data:
            logging.info("No active trades to monitor.")
            return
        
        symbol = trade_data["symbol"]
        entry_price = trade_data["entry_price"]
        stop_loss = trade_data["stop_loss"]
        take_profit = trade_data["take_profit"]

        # Fetch the current price
        price_info = api_trading_client.get_best_bid_ask(symbol)
        current_price = float(price_info['results'][0]['bid_inclusive_of_sell_spread'])
        
        account_value = get_account_value(api_trading_client)
        
        # Check conditions
        if account_value <= ACCOUNT_VALUE_THRESHOLD:
            logging.info(f"Risk condition met for {symbol} at ${current_price:.2f}. Executing trade to close position.")
            execute_trade(api_trading_client, 'sell', symbol, 0, 0, 0, 0, 0)  # Close the position by executing a sell trade
        
        # Check conditions
        if current_price <= stop_loss or current_price >= take_profit:
            logging.info(f"Risk condition met for {symbol} at ${current_price:.2f}. Executing trade to close position.")
            execute_trade(api_trading_client, 'sell', symbol, 0, 0, 0, 0, 0)  # Close the position by executing a sell trade

    except Exception as e:
        logging.error(f"Error monitoring risk: {e}")

def BTC_trading_strategy(api_trading_client: CryptoAPITrading):
    """
    Bitcoin trading strategy with active trade management.
    """
    logging.info("Starting BTC trading strategy...")

    # Check for active trade first
    trade_data = load_trade_data()
    if trade_data and trade_data["status"] == "active":
        logging.info(f"Active trade detected for {trade_data['symbol']} at entry price ${trade_data['entry_price']:.2f}")
        if trade_data["stop_loss"] or trade_data["take_profit"]:
            monitor_risk(api_trading_client)  # Monitor the risk for stop-loss/take-profit triggers
    
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).isoformat() + 'Z'
    
    macd_short_window = 20
    macd_long_window = 30
    macd_signal_window = 10
    
    mvcd_short_window =20
    mvcd_long_window = 30
    mvcd_signal_window = 10
    
    vwap_window = 20
    
    tema_window = 20
    
    # Define weights for each indicator
    weights = {
        'MACD': 0.01,
        'MVCD': 0.01,
        'VWAP': 0.01,
        'TEMA': 0.01,
    }
    
    # Execute trade based on the signal
    account_value = get_account_value(api_trading_client)  # Example account value
    risk_per_trade = 0.01  # 1% risk
    stop_loss_percent = 0.02  # 2% stop loss
    take_profit_percent = 0.05  # 5% take profit
    confidence = 0.3 # 30% confidence
    
    # Fetch historical data
    prices_series = fetch_historical_data(start_date= start_date)['close']
    prices_df = fetch_historical_data(start_date= start_date)  # For indicators requiring OHLCV

    # Calculate signals from different indicators
    macd_signal_value = calculate_macd(prices_series,macd_short_window,macd_long_window,macd_signal_window)
    macd_signal_value = calculate_mvcd(prices_series,mvcd_short_window,mvcd_long_window,mvcd_signal_window)
    vwap_signal_value = calculate_vwap(prices_df,vwap_window)
    ema_signal_value = calculate_tema(prices_series,tema_window)

    # Combine signals into a dictionary
    signals = {
        'MACD': macd_signal_value,
        'MVCD': macd_signal_value,
        'VWAP': vwap_signal_value,
        'TEMA': ema_signal_value,
    }

    # Aggregate signals
    final_signal = aggregate_signals(signals, weights)
    logging.info(f"Signals: {signals}")
    logging.info(f"Aggregated Signal: {final_signal}")

    execute_trade(
        api_trading_client=api_trading_client,
        signal=final_signal,
        symbol="BTC-USD",
        account_value=account_value,
        risk_per_trade=risk_per_trade,
        stop_loss_percent=stop_loss_percent,
        take_profit_percent=take_profit_percent,
        confidence=confidence
    )
